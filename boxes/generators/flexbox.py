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

import boxes
import math

class FlexBox(boxes.Boxes):
    """Box with living hinge and round corners"""
    def __init__(self):
        boxes.Boxes.__init__(self)
        self.buildArgParser("x", "y", "h")
        self.argparser.add_argument(
            "--radius",  action="store", type=float, default=15,
            help="Radius of the latch in mm")
        
    @boxes.restore
    def flexBoxSide(self, x, y, r, callback=None):
        self.moveTo(r, 0)
        for i, l in zip(range(2), (x, y)):
            self.cc(callback, i)
            self.edges["f"](l-2*r)
            self.corner(90, r)
        self.cc(callback, 2)
        self.edge(x-2*r)
        self.corner(90, r)
        self.cc(callback, 3)
        self.latch(self.latchsize)
        self.cc(callback, 4)
        self.edges["f"](y-2*r-self.latchsize)
        self.corner(90, r)

    def surroundingWall(self):
        x, y, h, r = self.x, self.y, self.h, self.radius
        
        c4 = math.pi * r * 0.5

        self.edges["F"](y-2*r-self.latchsize, False)
        self.edges["X"](c4, h+2*self.thickness)
        self.edges["F"](x-2*r, False)
        self.edges["X"](c4, h+2*self.thickness)
        self.edges["F"](y-2*r, False)
        self.edges["X"](c4, h+2*self.thickness)
        self.edge(x-2*r)
        self.edges["X"](c4, h+2*self.thickness)
        self.latch(self.latchsize, False)
        self.edge(h+2*self.thickness)
        self.latch(self.latchsize, False, True)
        self.edge(c4)
        self.edge(x-2*r)
        self.edge(c4)
        self.edges["F"](y-2*r, False)
        self.edge(c4)
        self.edges["F"](x-2*r, False)
        self.edge(c4)
        self.edges["F"](y-2*r-self.latchsize, False)
        self.corner(90)
        self.edge(h+2*self.thickness)
        self.corner(90)

    def render(self):
        x, y, h = self.x, self.y, self.h
        r = self.radius or min(x, y)/2.0
        self.latchsize = 8 * self.thickness
        c4 = math.pi * r * 0.5

        width = 2*x + 2*y - 8*r + 4*c4 + 4*self.thickness
        height = y + h + 8*self.thickness

        self.open(width, height)

        self.moveTo(self.thickness, self.thickness)
        self.surroundingWall()
        self.moveTo(self.thickness, self.h+5*self.thickness)
        self.flexBoxSide(self.x, self.y, self.radius)
        self.moveTo(2*self.x+3*self.thickness, 0)
        self.ctx.scale(-1, 1)
        self.flexBoxSide(self.x, self.y, self.radius)

        self.close()

def main():
    b = FlexBox()
    b.parseArgs()
    b.render()

if __name__=="__main__":
    main()
