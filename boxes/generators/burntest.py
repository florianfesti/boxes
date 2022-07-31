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

class BurnTest(Boxes):
    """Test different burn values"""
    description = """This generator will make shapes that you can use to select
optimal value for burn parameter for other generators. After burning try to
attach sides with the same value and use best fitting one on real projects.
In this generator set burn in the Default Settings to the lowest value
to be tested. To get an idea cut a rectangle with known nominal size and
measure the shrinkage due to the width of the laser cut. Now you can
measure the burn value that you should use in other generators. It is half
the difference of the overall size as shrinkage is occurring on both
sides. You can use the reference rectangle as it is rendered without burn
correction.

See also LBeam that can serve as compact BurnTest and FlexTest for testing flex settings.
"""

    ui_group = "Part"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser(x=100)
        self.argparser.add_argument(
            "--step",  action="store", type=float, default=0.01,
            help="increases in burn value between the sides")
        self.argparser.add_argument(
            "--pairs",  action="store", type=int, default=2,
            help="number of pairs (each testing four burn values)")


    def render(self):
        x, s = self.x, self.step
        t = self.thickness
        
        fsize = 12.5 * self.x / 100 if self.x < 81 else 10

        self.moveTo(t, t)

        for cnt in range(self.pairs):
            
            for i in range(4):
                self.text("%.3fmm" % self.burn, x/2, t, fontsize = fsize, align="center", color=Color.ETCHING)
                self.edges["f"](x)
                self.corner(90)
                self.burn += s
                
            self.burn -= 4*s

            self.moveTo(x+2*t+self.spacing, -t)
            for i in range(4):
                self.text("%.3fmm" % self.burn, x/2, t, fontsize = fsize, align="center", color=Color.ETCHING)
                self.edges["F"](x)
                self.polyline(t, 90, t)
                self.burn += s
            self.moveTo(x+2*t+self.spacing, t)
