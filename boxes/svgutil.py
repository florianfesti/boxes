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

import re, datetime

from xml.etree import cElementTree as ElementTree

class Extend:

    def __init__(self):
        self.minx = None
        self.maxx = None
        self.miny = None
        self.maxy = None

    def __add__(self, v):
        x, y = v
        res = Extend()
        res.minx = self.minx + x
        res.maxx = self.maxx + x
        res.miny = self.miny + y
        res.maxy = self.maxy + y
        return res

    def addPoint(self, x, y):
        if self.minx is None or self.minx > x:
            self.minx = x
        if self.maxx is None or self.maxx < x:
            self.maxx = x
        if self.miny is None or self.miny > y:
            self.miny = y
        if self.maxy is None or self.maxy < y:
            self.maxy = y

    def addExtend(self, extend, x, y):
        extend = extend + (x, y)
        self.addPoint(extend.minx, extend.miny)
        self.addPoint(extend.maxx, extend.maxy)

class SVGFile(object):
    pathre = re.compile(r"[MCL]? *((-?\d+(\.\d+)?) (-?\d+(\.\d+)?) *)+")
    transformre = re.compile(r"matrix\(" + ",".join([r"(-?\d+(\.\d+)?)"] * 6) + "\)")

    def __init__(self, filename):
        self.filename = filename
        self.minx = self.maxx = self.miny = self.maxy = None
        self.tree = ElementTree.parse(filename)
        self.symbol_extends = {}

    def fix(self, metadata=None):
        self.getEnvelope()
        self.moveOrigin()
        self.addMetadata(metadata)
        self.rewriteViewPort()

    def getExtend(self, element, extend):
        if element.tag.endswith("}path"):
            minx = maxx = miny = maxy = None
            m = self.transformre.match(element.attrib.get("transform", ""))

            if m:
                matrix = [float(m.group(i)) for i in range(1, 12, 2)]
            else:
                matrix = [1, 0,
                          0, 1,
                          0, 0]

            for m in self.pathre.findall(element.attrib.get("d", "")):
                x = float(m[1])
                y = float(m[3])
                tx = matrix[0] * x + matrix[2] * y + matrix[4]
                ty = matrix[1] * x + matrix[3] * y + matrix[5]

                extend.addPoint(tx, ty)
        elif element.tag.endswith("}use"):
            x, y = float(element.attrib["x"]), float(element.attrib["y"])
            s = self.symbol_extends[element.attrib["{http://www.w3.org/1999/xlink}href"][1:]]
            extend.addExtend(s, x, y)

        for e in element:
            if e.tag.endswith("}symbol"):
                self.symbol_extends[e.attrib["id"]] = self.getExtend(e, Extend())
            else:
                self.getExtend(e, extend)
        return extend

    def getEnvelope(self):
        self.tags = []
        root = self.tree.getroot()
        self.extend = self.getExtend(root, Extend())


    def _moveElement(self, e, dx, dy):
        if e.tag.endswith("}symbol"):
            return
        if e.tag.endswith("}path"):
            minx = maxx = miny = maxy = None
            m = self.transformre.match(e.attrib.get("transform", ""))

            if m:
                matrix = [float(m.group(i)) for i in range(1, 12, 2)]
            else:
                matrix = [1, 0,
                          0, 1,
                          0, 0]
            matrix[4] += dx
            matrix[5] += dy
            e.attrib["transform"] = "matrix(%s)" % (",".join(("%.4f" % m for m in matrix)))
        if e.tag.endswith("}use"):
            e.attrib["x"] = "%.4f" % (float(e.attrib["x"])+dx)
            e.attrib["y"] = "%.4f" % (float(e.attrib["y"])+dy)

        for child in e:
            self._moveElement(child, dx, dy)

    def moveOrigin(self):
        self._moveElement(self.tree.getroot(),
                          -self.extend.minx+10, -self.extend.miny+10)
        self.extend.maxx -= self.extend.minx-20
        self.extend.maxy -= self.extend.miny-20
        self.extend.minx = self.extend.miny = 0.0

    def rewriteViewPort(self):
        """
        Modify SVG file to have the correct width, height and viewPort attributes.
        """

        self.extend.minx = self.extend.minx or 0
        self.extend.miny = self.extend.miny or 0
        self.extend.maxx = self.extend.maxx or (self.extend.minx + 10)
        self.extend.maxy = self.extend.maxy or (self.extend.miny + 10)

        if 0 <= self.extend.minx <= 50:
            minx = 0
        else:
            minx = 10 * int(self.extend.minx // 10) - 10

        maxx = 10 * int(self.extend.maxx // 10) + 10
        miny = 10 * int(self.extend.miny // 10) - 10
        maxy = 10 * int(self.extend.maxy // 10) + 10

        root = self.tree.getroot()
        root.set('width', "%imm" % (maxx-minx))
        root.set('height', "%imm" % (maxy-miny))
        root.set('viewBox', "%i %i %i %i" % (minx, miny, maxx - minx, maxy - miny))

        self.tree.write(self.filename)

    def addMetadata(self, md):
        txt = """
{name} - {description}
Created with Boxes.py (http://festi.info/boxes.py)
Creation date: {date}
""".format(date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") , **md)

        txt += "Command line (remove spaces beteen dashes): %s\n" % md["cli"].replace("--", "- -")

        if md["url"]:
            txt+= "Url: %s\n" % md["url"]
            txt+= "SettingsUrl: %s\n" % re.sub(r"&render=[01]", "", md["url"])
        m = ElementTree.Comment(txt)
        self.tree.getroot().insert(0, m)

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

    parser = ElementTree.XMLParser(remove_blank_text=True)

    src_tree = ElementTree.parse(box, parser)
    dest_tree = ElementTree.parse(inkscape, parser)
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
    ElementTree.ElementTree(dest_root).write(output, pretty_print=True, encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    svg = SVGFile("examples/box.svg")
    svg.getEnvelope()
    svg.rewriteViewPort()
