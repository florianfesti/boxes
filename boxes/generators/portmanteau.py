#!/usr/bin/python3
# Copyright (C) 2013-2014 Florian Festi
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

from boxes import *


class TriangleEdgeSettings(edges.Settings):
    absolute_params = {
        "height" : 100,
        }

class TriangleEdge(edges.Edge):
    """Extends one corner of the previous edge by 'height' and draws
       a triangular edge back to the endpoint."""
    char = "q"
    def __call__(self, length, **kw):
        t = self.boxes.thickness
        h = self.settings.height
        angle = math.degrees(math.atan(self.settings.height/(length-t)))
        sh = math.hypot(length-t, h)
        r = 0 #Todo round the corners

        # Todo: Triangle starts at top or bottom for stacking
        # parts on page and so material has good side out.
        self.corner(-90, r)
        self.fingerHolesAt(t/2, 0, length-t)
        self.edge(t)
        self.corner(90-angle, r)
        self.edge(sh)
        self.corner(angle, r)
        self.edge(t)
        self.corner(90, r)
        self.edges["F"](h)
        self.edge(t)
        self.corner(-90)

    def margin(self):
        return self.boxes.spacing + self.boxes.thickness + self.settings.height


class Portmanteau(Boxes):
    """Portmanteau - as in a piece of luggage that open into two equal parts. 
       Generates parts for one half of a case with a handle at the top"""
    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("x", "y", "h", "outside")
        self.addSettingsArgs(edges.FingerJointSettings, finger=3.0, space=3.0)

        self.argparser.add_argument(
            "--handle_height",  action="store", type=float, default=100,
            dest="handle_height", help="distance handle extends past the edge")
        self.argparser.add_argument(
            "--grip_width",  action="store", type=float, default=80,
            dest="gw", help="width of the handle hole")
        self.argparser.add_argument(
            "--grip_height",  action="store", type=float, default=20,
            dest="gh", help="height of the handle hole")

    def gripHole(self):
        if not self.gw:
            return

        # Todo: param to orient vertically or horizontally
        x = self.y
        r = min(self.gw, self.gh) / 2.0
        self.rectangularHole(self.handle_height-(2.5*r), x/2.0, self.gh, self.gw, r)


    def render(self):
        x, y, h = self.x, self.y, self.h
        hh = self.handle_height
        t = self.thickness

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            h = self.adjustSize(h)

        self.open()

        s = TriangleEdgeSettings(
            self.thickness,
            height = hh,
            )
        self.addPart(TriangleEdge(self, s))

        # edges = 'BRTL'

        # Todo: Stack parts for minimum size
        self.moveTo(t, t)
        self.rectangularWall(h, y, "FfFe", move="right")
        self.rectangularWall(x, y, "FFFF", move="right")
        self.rectangularWall(h-t, y, "fFff", move="right")
        self.rectangularWall(hh,y, "feff", callback=[self.gripHole]) 
        self.moveTo(-(x+h+5*t), 0)
        self.moveTo(0, y+3*t)
        self.rectangularWall(x, h, "fqef")
        self.moveTo(0, (h+3*t))
        self.rectangularWall(x, h, "fqef") #flip this on horizontal axis
        
        self.close()

def main():
    b = Portmanteau()
    b.parseArgs()
    b.render()

if __name__ == '__main__':
    main()
