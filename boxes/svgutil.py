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

import xml.parsers.expat
import re

from xml.etree import cElementTree as ElementTree

class SVGFile(object):
    pathre = re.compile(r"[MCL]? *((-?\d+(\.\d+)?) (-?\d+(\.\d+)?) *)+")
    transformre = re.compile(r"matrix\(" + ",".join([r"(-?\d+(\.\d+)?)"] * 6) + "\)")

    def __init__(self, filename):
        self.filename = filename
        self.minx = self.maxx = self.miny = self.maxy = None
        self.tree = ElementTree.parse(filename)

    def handleStartElement(self, name, attrs):
        self.tags.append(name)
        if name == "path" and "symbol" not in self.tags:
            minx = maxx = miny = maxy = None
            m = self.transformre.match(attrs.get("transform", ""))

            if m:
                matrix = [float(m.group(i)) for i in range(1, 12, 2)]
            else:
                matrix = [1, 0,
                          0, 1,
                          0, 0]

            for m in self.pathre.findall(attrs.get("d", "")):
                x = float(m[1])
                y = float(m[3])
                tx = matrix[0] * x + matrix[2] * y + matrix[4]
                ty = matrix[1] * x + matrix[3] * y + matrix[5]

                if self.minx is None or self.minx > tx:
                    self.minx = tx

                if self.maxx is None or self.maxx < tx:
                    self.maxx = tx

                if self.miny is None or self.miny > ty:
                    self.miny = ty

                if self.maxy is None or self.maxy < ty:
                    self.maxy = ty

    def handleEndElement(self, name):
        last = self.tags.pop()

        if last != name:
            raise ValueError("Got </%s> expected </%s>" % (name, last))

    def getEnvelope(self):
        self.tags = []
        p = xml.parsers.expat.ParserCreate()
        p.StartElementHandler = self.handleStartElement
        p.EndElementHandler = self.handleEndElement
        p.ParseFile(open(self.filename, "rb"))

    def rewriteViewPort(self):
        """
        Modify SVG file to have the correct width, height and viewPort attributes.
        """

        self.minx = self.minx or 0
        self.miny = self.miny or 0
        self.maxx = self.maxx or (self.minx + 10)
        self.maxy = self.maxy or (self.miny + 10)

        if 0 <= self.minx <= 50:
            minx = 0
        else:
            minx = 10 * int(self.minx // 10) - 10

        maxx = 10 * int(self.maxx // 10) + 10
        miny = 10 * int(self.miny // 10) - 10
        maxy = 10 * int(self.maxy // 10) + 10

        root = self.tree.getroot()
        root.set('width', "%imm" % (maxx-minx))
        root.set('height', "%imm" % (maxy-miny))
        root.set('viewBox', "%i %i %i %i" % (minx, miny, maxx - minx, maxy - miny))

        self.tree.write(self.filename)

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
    from lxml import etree as et

    parser = et.XMLParser(remove_blank_text=True)

    src_tree = et.parse(box, parser)
    dest_tree = et.parse(inkscape, parser)
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
        import sys
        dest_root.append(el)
        if el.tag.endswith("g"):
            el.set("transform", "matrix(%f,0,0,%f, %f, %f)" % (
                scale_x, scale_y, off_x, off_y))

    # write the xml file
    et.ElementTree(dest_root).write(output, pretty_print=True, encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    svg = SVGFile("examples/box.svg")
    svg.getEnvelope()
    svg.rewriteViewPort()
