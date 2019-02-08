#!/usr/bin/env python3
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


class RoundedBox(Boxes):
    """Box with vertical edges rounded"""

    ui_group = "FlexBox"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser("x", "y", "h", "outside")
        self.argparser.add_argument(
            "--radius", action="store", type=float, default=15,
            help="Radius of the corners in mm")
        self.argparser.add_argument(
            "--wallpieces", action="store", type=int, default=1,
            choices=[1, 2, 3, 4], help="# pieces of outer wall")
        self.argparser.add_argument(
            "--top",  action="store", type=str, default="none",
            choices=["closed", "hole", "lid",],
            help="style of the top and lid")

    def hole(self):
        t = self.thickness
        x, y, r = self.x, self.y, self.radius

        if r > 2*t:
            r -= 2*t
        else:
            x += 2*t - 2*r
            y += 2*t - 2*r
            self.moveTo(2*t-r, 0)
            r = 0

        lx = x - 2*r - 4*t
        ly = y - 2*r - 4*t

        self.moveTo(0, 2*t)
        for l in (lx, ly, lx, ly):
            self.edge(l);
            self.corner(90, r)

    def render(self):
        self.open()

        x, y, h, r = self.x, self.y, self.h, self.radius

        if self.outside:
            self.x = x = self.adjustSize(x)
            self.y = y = self.adjustSize(y)
            self.h = h = self.adjustSize(h)

        r = self.radius = min(r, y / 2.0)

        t = self.thickness

        with self.saved_context():
            self.roundedPlate(x, y, r, wallpieces=self.wallpieces, move="right")
            self.roundedPlate(x, y, r, wallpieces=self.wallpieces, move="right",
                              callback=[self.hole] if self.top != "closed" else None)
            if self.top == "lid":
                self.roundedPlate(x, y, r, "E", wallpieces=self.wallpieces, move="right")

        self.roundedPlate(x, y, r, wallpieces=self.wallpieces, move="up only")

        self.surroundingWall(x, y, r, h, "F", "F", pieces=self.wallpieces)


