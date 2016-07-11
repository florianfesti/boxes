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

class SVGFile(object):

    pathre = re.compile(r"[MCL]? *((-?\d+(\.\d+)?) (-?\d+(\.\d+)?) *)+")
    transformre = re.compile(r"matrix\(" + ",".join([r"(-?\d+(\.\d+)?)"] * 6) + "\)")

    def __init__(self, filename):
        self.filename = filename
        self.minx = self.maxx = self.miny = self.maxy = None

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
                tx = matrix[0]*x+matrix[2]*y+matrix[4]
                ty = matrix[1]*x+matrix[3]*y+matrix[5]

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
        f = open(self.filename, "r+")
        s = f.read(1024)

        m = re.search(r"""<svg[^>]*(width="(\d+pt)" height="(\d+pt)" viewBox="0 (0 (\d+) (\d+))") version="1.1">""", s)

        #minx = 10*int(self.minx//10)-10
        # as we don't rewrite the left border keep it as 0
        if 0 <= self.minx <= 50:
            minx = 0
        else:
            raise ValueError("Left end of drawing at wrong place: %imm (0-50mm expected)" % self.minx)
        maxx = 10*int(self.maxx//10)+10
        miny = 10*int(self.miny//10)-10
        maxy = 10*int(self.maxy//10)+10

        if m:
            f.seek(m.start(1))
            s = ('width="%imm" height="%imm" viewBox="0 %i %i %i"' %
                 (maxx-minx, maxy-miny, miny, maxx, maxy-miny))
            if len(s) > len(m.group(1)):
                raise ValueError("Not enough space for size")
            f.write(s + " " * (len(m.group(1))- len(s)))
        else:
            raiseValueError("Could not understand SVG file")
        

if __name__ == "__main__":
    svg = SVGFile("examples/box.svg")
    svg.getEnvelope()
    svg.rewriteViewPort()
