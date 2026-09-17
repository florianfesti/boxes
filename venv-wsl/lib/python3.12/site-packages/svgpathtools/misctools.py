"""This submodule contains miscellaneous tools that are used internally, but
aren't specific to SVGs or related mathematical objects."""

# External dependencies:
from __future__ import division, absolute_import, print_function
import os
import sys
import webbrowser


# stackoverflow.com/questions/214359/converting-hex-color-to-rgb-and-vice-versa
def hex2rgb(value):
    """Converts a hexadeximal color string to an RGB 3-tuple

    EXAMPLE
    -------
    >>> hex2rgb('#0000FF')
    (0, 0, 255)
    """
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+lv//3], 16) for i in range(0, lv, lv//3))


# stackoverflow.com/questions/214359/converting-hex-color-to-rgb-and-vice-versa
def rgb2hex(rgb):
    """Converts an RGB 3-tuple to a hexadeximal color string.

    EXAMPLE
    -------
    >>> rgb2hex((0,0,255))
    '#0000FF'
    """
    return ('#%02x%02x%02x' % tuple(rgb)).upper()


def isclose(a, b, rtol=1e-5, atol=1e-8):
    """This is essentially np.isclose, but slightly faster."""
    return abs(a - b) < (atol + rtol * abs(b))


def open_in_browser(file_location):
    """Attempt to open file located at file_location in the default web
    browser."""

    # If just the name of the file was given, check if it's in the Current
    # Working Directory.
    if not os.path.isfile(file_location):
        file_location = os.path.join(os.getcwd(), file_location)
    if not os.path.isfile(file_location):
        raise IOError("\n\nFile not found.")

    #  For some reason OSX requires this adjustment (tested on 10.10.4)
    if sys.platform == "darwin":
        file_location = "file:///"+file_location

    new = 2  # open in a new tab, if possible
    webbrowser.get().open(file_location, new=new)


BugException = Exception("This code should never be reached.  You've found a "
                         "bug.  Please submit an issue to \n"
                         "https://github.com/mathandy/svgpathtools/issues"
                         "\nwith an easily reproducible example.")
