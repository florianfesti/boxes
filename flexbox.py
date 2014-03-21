#!/usr/bin/python
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
    def __init__(self, x, y, z, r=None, thickness=3.0):
        c4 = math.pi * r * 0.5
        self.x = x
        self.y = y
        self.z = z
        self.r = r or min(x, y)/2.0
        self.latchsize = 8*thickness

        width = 2*x + 2*y - 8*r + 4*c4 + 4*thickness
        height = y + z + 4*thickness
        boxes.Boxes.__init__(self, width, height, thickness=thickness)
        
    @boxes.restore
    def flexBoxSide(self, x, y, r, callback=None):
        self.moveTo(r, 0)
        for i, l in zip(range(2), (x, y)):
            self.cc(callback, i)
            self.fingerJointEdge(l-2*r)
            self.corner(90, r)
        self.cc(callback, 2)
        self.edge(x-2*r)
        self.corner(90, r)
        self.cc(callback, 3)
        self.latch(self.latchsize)
        self.cc(callback, 4)
        self.fingerJointEdge(y-2*r-self.latchsize)
        self.corner(90, r)

    def surroundingWall(self):
        x, y, z, r = self.x, self.y, self.z, self.r
        
        c4 = math.pi * r * 0.5

        self.edges["F"](y-2*r-self.latchsize, False)
        self.flexEdge(c4, z+2*self.thickness)
        self.edges["F"](x-2*r, False)
        self.flexEdge(c4, z+2*self.thickness)
        self.edges["F"](y-2*r, False)
        self.flexEdge(c4, z+2*self.thickness)
        self.edge(x-2*r)
        self.flexEdge(c4, z+2*self.thickness)
        self.latch(self.latchsize, False)
        self.edge(z+2*self.thickness)
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
        self.edge(z+2*self.thickness)
        self.corner(90)

    def render(self):
        self.moveTo(self.thickness, self.thickness)
        self.surroundingWall()
        self.moveTo(self.thickness, self.z+4*self.thickness)
        self.flexBoxSide(self.x, self.y, self.r)
        self.moveTo(2*self.x+3*self.thickness, 0)
        self.ctx.scale(-1, 1)
        self.flexBoxSide(self.x, self.y, self.r)

        self.close()

if __name__=="__main__":
    b = FlexBox(50, 70, 50, r=15)
    b.render()
