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
    """Makes an 'edge' with a rounded triangular bumpout and
       optional hole"""
    char = "q"
    def __call__(self, length, **kw):
        t = self.boxes.thickness
        l = length
        h = self.settings.height
        angle = math.degrees(math.atan(self.settings.height/(length-t)))
        sh = math.hypot(l-t, h)
        r = 0 #TODO round the corners

        # TODO: Add holes for finger joints along original edge
        self.corner(-90, r)
        self.edge(t)
        self.corner(90-angle, r)
        self.edge(sh)
        self.corner(angle, r)
        self.edge(t)
        self.corner(90, r)
        self.edge(h+t)
        self.corner(-90)

    def margin(self):
        return self.boxes.spacing + self.boxes.thickness + self.settings.height


class Portmanteau(Boxes):
    """Portmanteau - as in a piece of luggage that open into two equal parts. 
       Generates parts for one half of a case with a handle at the top"""
    def __init__(self):
        Boxes.__init__(self)

        self.argparser.add_argument(
            "--handle_height",  action="store", type=float, default=100,
            dest="handle_height", help="distance handle extends past the edge")
        self.argparser.add_argument(
            "--grip_width",  action="store", type=float, default=80,
            dest="gw", help="width of the handle hole")
        self.argparser.add_argument(
            "--grip_height",  action="store", type=float, default=20,
            dest="gh", help="height of the handle hole")

        self.buildArgParser("x", "y", "h", "outside")
        self.argparser.set_defaults(
            fingerjointfinger=3.0,
            fingerjointspace=3.0
            )


    def gripHole(self):
        if not self.gw:
            return

        # TODO: param to orient vertically or horizontally
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

        self.moveTo(t, t)
        self.rectangularWall(h, y, "FfFe", move="right")
        self.rectangularWall(x, y, "FFFF", move="right")
        self.rectangularWall(h, y, "efef", move="right") #TODO: fingers on top and bottom
        self.rectangularWall(hh,y, "eeeF", callback=[self.gripHole]) 
        self.moveTo(-(x+h+6*t), 0)
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
