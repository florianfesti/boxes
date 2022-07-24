#!/usr/bin/env python3
# Copyright (C) 2013-2019 Florian Festi
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
from boxes.walledges import _WallMountedBox

class FrontEdge(edges.Edge):

    def __call__(self, length, **kw):
        td = self.tooldiameter
        rh = self.holediameter / 2.0
        r = self.radius
        sw = self.slot_width

        a = math.degrees(math.asin((r+sw/2)/(r+rh)))
        l = (td - sw - 2*r) / 2

        for i in range(self.number):
            self.polyline(l, (180-a, r), 0, (-360+2*a, rh), 0, (180-a, r), l)
            
        

class WallChiselHolder(_WallMountedBox):
    """Wall tool holder for chisels, files and similar tools"""

    def __init__(self):
        super().__init__()

        self.buildArgParser(h=120)

        self.argparser.add_argument(
            "--tooldiameter",  action="store", type=float, default=30.,
            help="diameter of the tool including space to grab")
        self.argparser.add_argument(
            "--holediameter",  action="store", type=float, default=30.,
            help="diameter of the hole for the tool (handle should not fit through)")
        self.argparser.add_argument(
            "--slot_width",  action="store", type=float, default=5.,
            help="width of slots")
        #self.argparser.add_argument(
        #    "--angle",  action="store", type=float, default=0.,
        #    help="angle of the top - positive for leaning backwards")
        self.argparser.add_argument(
            "--radius",  action="store", type=float, default=5.,
            help="radius at the slots")
        self.argparser.add_argument(
            "--number",  action="store", type=int, default=6,
            help="number of tools/slots")
        self.argparser.add_argument(
            "--hooks",  action="store", type=str, default="all",
            choices=("all", "odds", "everythird"),
            help="amount of hooks / braces")

    def brace(self, i):
        n = self.number
        if i in (0, n):
            return True
        # fold for symmetry
        #if i > n//2:
        #    i = n - i
        if self.hooks == "all":
            return True
        elif self.hooks == "odds":
            return not (i % 2)
        elif self.hooks == "everythird":
            return not (i % 3)

    def braces(self):
        return sum((self.brace(i) for i in range(self.number+1)))

    def backCB(self):
        n = self.number
        rt = self.holediameter
        wt = self.tooldiameter
        t = self.thickness
        
        d = min(2*t, (wt-rt)/4.)
        self.wallHolesAt(d, 0, self.h, 90)
        self.wallHolesAt(n*wt-d, 0, self.h, 90)
        
        for i in range(1, n):
            if self.brace(i):
                self.wallHolesAt(i*wt, 0, self.h, 90)

    def topCB(self):
        n = self.number
        rt = self.holediameter
        wt = self.tooldiameter
        t = self.thickness
        l = self.depth
        
        d = min(2*t, (wt-rt)/4.)
        self.fingerHolesAt(d, 0, l, 90)
        self.fingerHolesAt(n*wt-d, 0, l, 90)
        
        for i in range(1, n):
            if self.brace(i):
                self.fingerHolesAt(i*wt, 0, l, 90)

    def render(self):
        self.generateWallEdges()

        t = self.thickness
        wt = self.tooldiameter
        n = self.number

        self.depth = depth = wt + 4*t

        self.rectangularWall(n*wt, self.h, "eeee", callback=[self.backCB], move="up")
        self.rectangularWall(n*wt, depth, [FrontEdge(self, None), "e","e","e"], callback=[self.topCB], move="up")
        self.moveTo(0, t)
        self.rectangularTriangle(depth, self.h, "fbe", r=3*t, num=self.braces())
