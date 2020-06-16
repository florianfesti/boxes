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

class CornerEdge(edges.Edge):
    char = "C"
    
    def startwidth(self):
        return self.boxes.thickness * math.tan(math.radians(90-22.5))

    def __call__(self, length, bedBolts=None, bedBoltSettings=None, **kw):
        with self.saved_context():
            self.ctx.stroke()
            self.set_source_color(Color.RED)
            self.moveTo(0, self.startwidth())
            self.edge(length)
            self.ctx.stroke()
            self.set_source_color(Color.BLACK)
        super().__call__(length, bedBolts=None, bedBoltSettings=None, **kw)
    

class TriangleLamp(Boxes):
    """Triangle LED Lamp"""

    ui_group = "Misc"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, finger=3.0,space=3.0,
                             surroundingspaces=0.5)
        self.buildArgParser(x=250, h=40)
        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--cornersize",  action="store", type=float, default=30,
            help="short side of the corner triangles")
        self.argparser.add_argument(
            "--screenholesize",  action="store", type=float, default=4,
            help="diameter of the holes in the screen")
        self.argparser.add_argument(
            "--screwholesize",  action="store", type=float, default=2,
            help="diameter of the holes in the wood")
        self.argparser.add_argument(
            "--sharpcorners",  action="store", type=boolarg, default=False,
            help="extend walls for 45° corners. Requires grinding a 22.5° bevel.")

    def CB(self, l, size):

        def f():
            t = self.thickness
            self.fingerHolesAt(0, self.h-1.5*t, size, 0)
            self.fingerHolesAt(l, self.h-1.5*t, size, 180)

        return f

    def render(self):
        # adjust to the variables you want in the local scope
        x, h = self.x, self.h
        l = (x**2+x**2)**.5
        c = self.cornersize
        t = self.thickness

        r1 = self.screwholesize / 2
        r2 = self.screenholesize / 2

        self.addPart(CornerEdge(self, None))

        self.rectangularTriangle(x, x, num=2, move="up", callback=[
            lambda: self.hole(2/3.*c, 1/4.*c, r2),
            lambda: (self.hole(1/3.*c, 1/3.*c, r2),
                     self.hole(x-2/3.*c, 1/4.*c, r2)),
        ])
        self.rectangularTriangle(x, x, "fff", num=2, move="up")

        C = 'e'
        if self.sharpcorners:
            C = 'C'

        self.rectangularWall(x, h, "Ffe"+C, callback=[self.CB(x, c)],
                             move="up")
        self.rectangularWall(x, h, "Ffe"+C, callback=[self.CB(x, c)],
                             move="up")

        self.rectangularWall(x, h, "F"+C+"eF", callback=[self.CB(x, c)],
                             move="up")
        self.rectangularWall(x, h, "F"+C+"eF", callback=[self.CB(x, c)],
                             move="up")

        self.rectangularWall(l, h, "F"+C+"e" + C,
                             callback=[self.CB(l, c*2**.5)], move="up")
        self.rectangularWall(l, h, "F"+C+"e" + C,
                             callback=[self.CB(l, c*2**.5)], move="up")

        
        self.rectangularTriangle(c, c, "ffe", num=2, move="right", callback=[
            lambda:self.hole(2/3.*c,1/3.*c, r1)])
        self.rectangularTriangle(c, c, "fef", num=4, move="up", callback=[
            lambda: self.hole(2/3.*c, 1/4.*c, r1)])
