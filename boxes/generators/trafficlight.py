#!/usr/bin/env python3
# Copyright (C) 2013-2016 Florian Festi
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

class ShadyEdge(edges.BaseEdge):
    char = "s"

    def __call__(self, lenght, **kw):
        s = self.shades
        h = self.h
        a = math.atan(s/h)
        angle = math.degrees(a)
        for i in range(3):
            self.polyline(0, -angle, h / math.cos(a), angle+90)
            self.edges["f"](s)
            self.corner(-90)
            if i < 2:
                self.edge(self.thickness)

    def margin(self):
        return self.shades

class TrafficLight(Boxes): # change class name here and below
    """Traffic light with 3 lights"""
    
    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)

        # remove cli params you do not need
        self.buildArgParser("h")
        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--depth",  action="store", type=float, default=100,
            help="inner depth not including the shades")
        self.argparser.add_argument(
            "--shades",  action="store", type=float, default=50,
            help="depth of the shaders")

    def backCB(self):
        t = self.thickness
        for i in range(1,3):
            self.fingerHolesAt(i*(self.h+t)-0.5*t, 0, self.h)

    def sideCB(self):
        t = self.thickness
        for i in range(1,3):
            self.fingerHolesAt(i*(self.h+t)-0.5*t, 0, self.depth)
        for i in range(3):
            self.fingerHolesAt(i*(self.h+t),
                               self.depth-2*t, self.h, 0)

    def frontCB(self):
        self.hole(self.h/2, self.h/2, self.h/2-self.thickness)
    
    def render(self):
        # adjust to the variables you want in the local scope
        d, h = self.depth, self.h
        s = self.shades
        t = self.thickness

        th = 3 * h + 2*t
        
        # Initialize canvas
        self.open()

        self.addPart(ShadyEdge(self, None))

        self.rectangularWall(th, h, "FFFF", callback=[self.backCB], move="up")
        self.rectangularWall(th, d, "fFsF", callback=[self.sideCB], move="up")
        self.rectangularWall(th, d, "fFsF", callback=[self.sideCB], move="up")
        
        e = edges.CompoundEdge(self, "fF", (d, s))
        e2 = edges.CompoundEdge(self, "Ff", (s, d))
        for i in range(3):
            self.rectangularWall(h, d+s, ['f', e, 'e', e2],
                                 move="right" if i<2 else "right up")
        for i in range(3):
            self.rectangularWall(h, h, "ffff", callback=[self.frontCB],
                                 move="left" if i<2 else "left up")
        self.rectangularWall(h, d, "ffef")
        
        self.close()

def main():
    b = TrafficLight() # change to class name
    b.parseArgs()
    b.render()

if __name__ == '__main__':
    main()
