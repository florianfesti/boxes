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


class RoundedTriangleSettings(edges.Settings):
    absolute_params = {
        "angle" : 60,
        "radius" : 30,
        "r_hole" : None,
        }

class RoundedTriangle(edges.Edge):
    char = "q"
    def __call__(self, length, **kw):
        self.corner(-90)
        angle = self.settings.angle
        r = self.settings.radius

        if self.settings.r_hole:
            x = 0.5*(length-2*r)*math.tan(math.radians(angle))
            y =  0.5*(length)
            self.hole(x, y, self.settings.r_hole)

        l = 0.5 * (length-2*r) / math.cos(math.radians(angle))
        self.corner(90-angle, r)
        self.edge(l)
        self.corner(2*angle, r)
        self.edge(l)
        self.corner(90-angle, r)
        self.corner(-90)


class Box(Boxes):
    """Fully closed box"""
    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("x", "y", "h", "outside")
        self.argparser.set_defaults(
            fingerjointfinger=3.0,
            fingerjointspace=3.0
            )

    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            h = self.adjustSize(h)

        self.open()

        s = RoundedTriangleSettings(self.thickness, angle=60, r_hole=5)
        self.addPart(RoundedTriangle(self, s))

        # (bottom, right, top, left)

        self.moveTo(t, t)
        #self.rectangularWall(h, y, "FfFe", move="right")
        #self.moveTo(h+2*t, 0)
        self.rectangularWall(x, y, "FFFF", move="right")
        #self.moveTo(x+3*t, 0)

        self.rectangularWall(h, y, "FqFf", move="right")
        self.moveTo(-(x+3*t), y+3*t)

        self.rectangularWall(h, y, "FfFq", move="right")
        self.moveTo(-(x+3*t), y+3*t)

        self.rectangularWall(x, h, "ffef", move="up")
        #self.moveTo(0, -(h+y+5*t))
        #self.moveTo(0, (h+3*t))
        self.rectangularWall(x, h, "efff")
        
        #self.moveTo(t, t)
        #self.rectangularWall(x, h, "FFeF", bedBolts=d2)
        #self.moveTo(x+3*t, 0)
        #self.rectangularWall(y, h, "Feef", bedBolts=d3)
        #self.moveTo(0, h+3*t)
        #self.rectangularWall(y, h, "Feef", bedBolts=d3)
        #self.moveTo(-x-3*t, 0)
        #self.rectangularWall(x, y, "efff", bedBolts=[d2, d3, d2, d3])

        self.close()

def main():
    b = Box()
    b.parseArgs()
    b.render()

if __name__ == '__main__':
    main()
