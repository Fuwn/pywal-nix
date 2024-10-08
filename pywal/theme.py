# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

"""
Theme file handling.
"""

import logging
import os
import random
import sys

from .settings import CACHE_DIR, CONF_DIR, MODULE_DIR
from . import util


def list_themes(dark=True):
    """List all installed theme files."""
    dark = "dark" if dark else "light"
    themes = os.scandir(os.path.join(MODULE_DIR, "colorschemes", dark))
    return [t for t in themes if os.path.isfile(t.path)]


def list_themes_user():
    """List user theme files."""
    themes = [
        *os.scandir(os.path.join(CONF_DIR, "colorschemes/dark/")),
        *os.scandir(os.path.join(CONF_DIR, "colorschemes/light/")),
    ]
    return [t for t in themes if os.path.isfile(t.path)]


def terminal_sexy_to_wal(data):
    """Convert terminal.sexy json schema to wal."""
    data["colors"] = {}
    data["special"] = {
        "foreground": data["foreground"],
        "background": data["background"],
        "cursor": data["color"][9],
    }

    for i, color in enumerate(data["color"]):
        data["colors"]["color%s" % i] = color

    return data


def parse(theme_file):
    """Parse the theme file."""
    data = util.read_file_json(theme_file)

    if "wallpaper" not in data:
        data["wallpaper"] = "None"

    if "alpha" not in data:
        data["alpha"] = util.Color.alpha_num

    # Terminal.sexy format.
    if "color" in data:
        data = terminal_sexy_to_wal(data)

    return data


def get_random_theme(dark=True):
    """Get a random theme file."""
    themes = [theme.path for theme in list_themes(dark)]
    random.shuffle(themes)
    return themes[0]


def get_random_theme_user():
    """Get a random theme file from user theme directories."""
    themes = [theme.path for theme in list_themes_user()]
    random.shuffle(themes)
    return themes[0]


def file(input_file, light=False):
    """Import colorscheme from json file."""
    util.create_dir(os.path.join(CONF_DIR, "colorschemes/light/"))
    util.create_dir(os.path.join(CONF_DIR, "colorschemes/dark/"))

    theme_name = ".".join((input_file, "json"))
    bri = "light" if light else "dark"

    user_theme_file = os.path.join(CONF_DIR, "colorschemes", bri, theme_name)
    theme_file = os.path.join(MODULE_DIR, "colorschemes", bri, theme_name)

    # Find the theme file.
    if input_file in ("random", "random_dark"):
        theme_file = get_random_theme()

    elif input_file == "random_light":
        theme_file = get_random_theme(light)

    elif input_file == "random_user":
        theme_file = get_random_theme_user()

    elif os.path.isfile(user_theme_file):
        theme_file = user_theme_file

    elif os.path.isfile(input_file):
        theme_file = input_file

    # Parse the theme file.
    if os.path.isfile(theme_file):
        logging.info("Set theme to \033[1;37m%s\033[0m.", os.path.basename(theme_file))
        util.save_file(
            os.path.basename(theme_file), os.path.join(CACHE_DIR, "last_used_theme")
        )
        return parse(theme_file)

    logging.error("No %s colorscheme file found.", bri)
    logging.error("Try adding   '-l' to set light themes.")
    logging.error("Try removing '-l' to set dark themes.")
    sys.exit(1)
