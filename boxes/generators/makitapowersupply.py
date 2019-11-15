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

class MakitaPowerSupply(Boxes):
    """Bench power supply powered with Maktia 18V battery or laptop power supply"""

    description = """
Vitamins: DSP5005 (or similar) power supply, two banana sockets, two 4.8mm flat terminals with flat soldering tag

To allow powering by laptop power supply: flip switch, Lenovo round socket (or adjust right  hole for different socket)
"""

    ui_group = "Misc"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)


    def side(self, l, h=14, move=None):
        t = self.thickness
        tw, th = h+t, l

        if self.move(tw, th, move, True):
            return

        self.moveTo(t, 0)
        self.polyline(h, 90, l-h/3**0.5, 60, h*2/3**0.5, 120)
        self.edges["f"](l)

        self.move(tw, th, move)

    def side2(self, l, h=14, move=None):
        t = self.thickness
        tw, th = h, l-10

        if self.move(tw, th, move, True):
            return

        if h > 14:
            self.polyline(h, 90, l-12, 90, h-14, 90, 50-12, -90, 8, -90)
        else:
            self.polyline(h, 90, l-50, 90, h-6, -90)
        self.polyline(11, 90, 1, -90, 27, (90, 1),
                      3, (90, 1), l-12, 90)

        self.move(tw, th, move)


    def bottom(self):
        t = self.thickness
        m = self.x / 2
        self.moveTo(0, 10)

        self.fingerHolesAt(m-30.5-0.5*t, 0, self.l)
        self.fingerHolesAt(m+30.5+0.5*t, 0, self.l)

        #self.rectangularHole(m-19, 23, 0.8, 6.25)
        #self.rectangularHole(m+19, 23, 0.8, 6.25)
        self.rectangularHole(m-19, 34, 0.8, 6.25)
        self.rectangularHole(m+19, 34, 0.8, 6.25)

        self.rectangularHole(m, -2.5, 35, 5)

    def front(self):
        self.hole(10, self.h/2, r=2.0)
        self.hole(30, self.h/2, r=2.0)
        self.hole(50, self.h/2, d=5.9)

        self.rectangularHole(76, 6.4, 12.4, 12.4)

    def back(self):
        for i in range(3):
            self.rectangularHole(self.x/2, i*8+5, self.x-20, 5, r=2.5)

    def regulatorCB(self):
        self.rectangularHole(21, 9.5, 35, 5)
        self.rectangularHole(5, 33+12, 10, 10)
        self.rectangularHole(42-5, 33+12, 10, 10)

        for x in [3.5, 38.5]:
            for y in [3.5, 65]:
                self.hole(x, y, 1.0)

    def render(self):
        # adjust to the variables you want in the local scope
        t = self.thickness

        l = self.l = 64
        hm = 15.5
        #w = self.w = 72

        self.x, self.y, self.h = x, y, h = 85, 75, 35

        self.rectangularWall(x, h, "FFFF", callback=[self.front], move="right")
        self.rectangularWall(y, h, "FfFf", move="up")
        self.rectangularWall(y, h, "FfFf")
        self.rectangularWall(x, h, "FFFF", callback=[self.back], move="left up")

        self.rectangularWall(x, y, "ffff", callback=[self.bottom], move="right")
        self.rectangularWall(x, y, "ffff", callback=[
            lambda: self.rectangularHole(x/2, y-20-5, 76, 40)], move="")
        self.rectangularWall(x, y, "ffff", move="left up only")

        #self.rectangularWall(72, l, callback=[self.bottom], move="right")
        self.side(l, hm, move="right")
        self.side(l, hm, move="right mirror")
        self.side2(l, hm, move="right")
        self.side2(l, hm, move="right mirror")

        #self.rectangularWall(42, l+12-t, "efff", callback=[self.regulatorCB], move="right")
        #self.rectangularWall(16, l+12-t, "eFFe", move="right")
        #self.rectangularWall(16, l+12-t, "eFFe", move="right")
        #self.rectangularWall(16, 42, "fFfe", move="right")
