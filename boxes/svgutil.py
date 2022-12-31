#!/usr/bin/env python3
# Copyright (C) 2016 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re

from xml.etree import ElementTree
ElementTree.register_namespace("","http://www.w3.org/2000/svg")
ElementTree.register_namespace("xlink", "http://www.w3.org/1999/xlink")

unit2mm = {"mm" : 1.0,
           "cm" : 10.0,
           "in" : 25.4,
           "px" : 90.0/25.4,
           "pt" : 90.0/25.4/1.25,
           "pc" : 90.0/25.4/15,
}

def getSizeInMM(tree):
    root = tree.getroot()
    m = re.match(r"(-?\d+\.?\d*)(\D+)", root.get("height"))
    height, units = m.groups()
    height = float(height) * unit2mm.get(units, 1.0)

    m = re.match(r"(-?\d+\.?\d*)(\D+)", root.get("width"))
    width, units = m.groups()
    width = float(width) * unit2mm.get(units, 1.0)

    return width, height

def getViewBox(tree):
    root = tree.getroot()
    m = re.match(r"\s*(-?\d+\.?\d*)\s+"
                     "(-?\d+\.?\d*)\s+"
                     "(-?\d+\.?\d*)\s+"
                     "(-?\d+\.?\d)\s*", root.get("viewBox"))

    return [float(m) for m in m.groups()]

def ticksPerMM(tree):
    width, height = getSizeInMM(tree)
    x1, y1, x2, y2 = getViewBox(tree)

    return x2/width, y2/height

def svgMerge(box, inkscape, output):

    src_tree = ElementTree.parse(box)
    dest_tree = ElementTree.parse(inkscape)
    dest_root = dest_tree.getroot()

    src_width, src_height = getSizeInMM(src_tree)
    dest_width, dest_height = getSizeInMM(dest_tree)

    src_scale_x, src_scale_y = ticksPerMM(src_tree)
    dest_scale_x, dest_scale_y = ticksPerMM(dest_tree)

    scale_x = dest_scale_x / src_scale_x
    scale_y = dest_scale_y / src_scale_y

    src_view = getViewBox(src_tree)

    off_x = src_view[0] * -scale_x
    off_y = (src_view[1]+src_view[3]) * -scale_y + dest_height * scale_y

    for el in src_tree.getroot():
        dest_root.append(el)
        if el.tag.endswith("g"):
            el.set("transform", "matrix(%f,0,0,%f, %f, %f)" % (
                scale_x, scale_y, off_x, off_y))

    # write the xml file
    ElementTree.ElementTree(dest_root).write(output, encoding='utf-8', xml_declaration=True)
