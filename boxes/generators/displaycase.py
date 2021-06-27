#!/usr/bin/env python3
# Copyright (C) 2013-2014 Florian Festi
# Copyright (C) 2018 Alexander Bulimov
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


class DisplayCase(Boxes):
    """Fully closed box intended to be cut from transparent acrylics and to serve as a display case."""

    ui_group = "Box"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser("x", "y", "h", "outside")
        self.argparser.add_argument(
            "--overhang",
            action="store",
            type=float,
            default=2,
            help="overhang for joints in mm",
        )

    def render(self):

        x, y, h = self.x, self.y, self.h

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            h = self.adjustSize(h)

        t = self.thickness

        d2 = edges.Bolts(2)
        d3 = edges.Bolts(3)

        d2 = d3 = None

        self.rectangularWall(x, h, "ffff", bedBolts=[d2] * 4, move="right", label="Wall 1")
        self.rectangularWall(y, h, "fFfF", bedBolts=[d3, d2, d3, d2], move="up", label="Wall 2")
        self.rectangularWall(y, h, "fFfF", bedBolts=[d3, d2, d3, d2], label="Wall 4")
        self.rectangularWall(x, h, "ffff", bedBolts=[d2] * 4, move="left up", label="Wall 3")

        self.flangedWall(x, y, "FFFF", flanges=[self.overhang] * 4, move="right", label="Top")
        self.flangedWall(x, y, "FFFF", flanges=[self.overhang] * 4, label="Bottom")

