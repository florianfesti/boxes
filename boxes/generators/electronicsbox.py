#!/usr/bin/env python3
# Copyright (C) 2013-2017 Florian Festi
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


class ElectronicsBox(Boxes):
    """Closed box with screw on top and mounting holes"""

    ui_group = "Box"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser("x", "y", "h", "outside")
        self.argparser.add_argument(
            "--triangle", action="store", type=float, default=25.,
            help="Sides of the triangles holding the lid in mm")
        self.argparser.add_argument(
            "--d1", action="store", type=float, default=2.,
            help="Diameter of the inner lid screw holes in mm")
        self.argparser.add_argument(
            "--d2", action="store", type=float, default=3.,
            help="Diameter of the lid screw holes in mm")
        self.argparser.add_argument(
            "--d3", action="store", type=float, default=3.,
            help="Diameter of the mounting screw holes in mm")
        self.argparser.add_argument(
            "--outsidemounts", action="store", type=boolarg, default=True,
            help="Add external mounting points")
        self.argparser.add_argument(
            "--holedist", action="store", type=float, default=7.,
            help="Distance of the screw holes from the wall in mm")

    def wallxCB(self):
        t = self.thickness
        self.fingerHolesAt(0, self.h-1.5*t, self.triangle, 0)
        self.fingerHolesAt(self.x, self.h-1.5*t, self.triangle, 180)
        
    def wallyCB(self):
        t = self.thickness
        self.fingerHolesAt(0, self.h-1.5*t, self.triangle, 0)
        self.fingerHolesAt(self.y, self.h-1.5*t, self.triangle, 180)

    def bottom(self, move=None):
        x, y = self.x, self.y
        hd = self.holedist
        t = self.thickness

        if self.move(x+2*t+4*hd, y+2*t, move, True):
            return

        self.moveTo(hd, 0)
        self.hole(0, hd, d=self.d3)
        self.edge(hd+t)
        self.fingerHolesAt(-0.5*t, t, y, 90)
        self.edges['F'](x)
        self.fingerHolesAt(0.5*t, t, y, 90)
        self.hole(hd+t, hd, d=self.d3)
        self.polyline(hd+t, (90, hd), y+2*t-2*hd, (90, hd), hd+t)
        self.hole(-hd-t, hd, d=self.d3)
        self.edges['F'](x)
        self.hole(hd+t, hd, d=self.d3)
        self.polyline(hd+t, (90, hd), y+2*t-2*hd, (90, hd))
        
        self.move(x+2*t+4*hd, y+2*t, move)
        
    def render(self):
        self.open()

        x, y, h = self.x, self.y, self.h
        d1, d2, d3 =self.d1, self.d2, self.d3
        hd = self.holedist
        t = self.thickness
        
        if self.outside:
            self.x = x = self.adjustSize(x)
            self.y = y = self.adjustSize(y)
            h = self.adjustSize(h)
            self.h = h = h + 2*t

        self.rectangularWall(x, h, "fFFF", callback=[self.wallxCB],
                             move="right")
        self.rectangularWall(y, h, "ffFf", callback=[self.wallyCB], move="up")
        self.rectangularWall(y, h, "ffFf", callback=[self.wallyCB])
        self.rectangularWall(x, h, "fFFF", callback=[self.wallxCB],
                             move="left up")

        if not self.outsidemounts:
            self.rectangularWall(x, y, "FFFF", callback=[
            lambda:self.hole(hd, hd, d=d3),
            lambda:self.hole(hd, hd, d=d3),
            lambda:self.hole(hd, hd, d=d3),
            lambda:self.hole(hd, hd, d=d3)], move="right")
        else:
            self.bottom(move='up')
        self.rectangularWall(x, y, callback=[
            lambda:self.hole(hd, hd, d=d2),
            lambda:self.hole(hd, hd, d=d2),
            lambda:self.hole(hd, hd, d=d2),
            lambda:self.hole(hd, hd, d=d2)], move='up')

        self.rectangularTriangle(self.triangle, self.triangle, "ffe", num=4,
            callback=[None, lambda: self.hole(hd, hd, d=d1)])

        self.close()


