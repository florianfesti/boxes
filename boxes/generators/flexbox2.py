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
import math

class FlexBox(Boxes):
    """Box with living hinge and top corners rounded"""
    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("x", "y", "h")
        self.argparser.add_argument(
            "--radius",  action="store", type=float, default=15,
            help="Radius of the corners in mm")
        
    @restore
    def flexBoxSide(self, x, y, r, callback=None):
        self.cc(callback, 0)
        self.fingerJointEdge(x)
        self.corner(90, 0)
        self.cc(callback, 1)
        self.fingerJointEdge(y-r)
        self.corner(90, r)
        self.cc(callback, 2)
        self.edge(x-2*r)
        self.corner(90, r)
        self.cc(callback, 3)
        self.latch(self.latchsize)
        self.cc(callback, 4)
        self.fingerJointEdge(y-r-self.latchsize)
        self.corner(90)

    def surroundingWall(self):
        x, y, h, r = self.x, self.y, self.h, self.radius
        
        self.edges["F"](y-r, False)
        if (x-2*r < 0.1):
            self.flexEdge(2*self.c4, h+2*self.thickness)
        else:
            self.flexEdge(self.c4, h+2*self.thickness)
            self.edge(x-2*r)
            self.flexEdge(self.c4, h+2*self.thickness)
        self.latch(self.latchsize, False)
        self.edge(h+2*self.thickness)
        self.latch(self.latchsize, False, True)
        self.edge(self.c4)
        self.edge(x-2*r)
        self.edge(self.c4)
        self.edges["F"](y-r)
        self.corner(90)
        self.edge(self.thickness)
        self.edges["f"](h)
        self.edge(self.thickness)
        self.corner(90)

    def render(self):
        self.radius = self.radius or min(x, y)/2.0
        self.c4 = c4 = math.pi * self.radius * 0.5
        self.latchsize = 8*self.thickness

        width = 2*self.x + self.y - 3*self.radius + 2*c4 + 7*self.thickness + self.latchsize # lock
        height = self.y + self.h + 8*self.thickness

        self.open(width, height)

        self.fingerJointSettings = (4, 4)

        self.moveTo(2*self.thickness, self.thickness)
        self.ctx.save()
        self.surroundingWall()
        self.moveTo(self.x+self.y-3*self.radius+2*self.c4+self.latchsize+1*self.thickness, 0)
        self.rectangularWall(self.x, self.h, edges="FFFF")
        self.ctx.restore()
        self.moveTo(0, self.h+4*self.thickness)
        self.flexBoxSide(self.x, self.y, self.radius)
        self.moveTo(2*self.x+3*self.thickness, 0)
        self.ctx.scale(-1, 1)
        self.flexBoxSide(self.x, self.y, self.radius)
        self.ctx.scale(-1, 1)
        self.moveTo(2*self.thickness, 0)
        self.rectangularWall(self.h, self.y-self.radius-self.latchsize, edges="fFeF")
        self.close()

def main():
    b = FlexBox()
    b.parseArgs()
    b.render()

if __name__=="__main__":
    main()
