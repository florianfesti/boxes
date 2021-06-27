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


class ClosedBox(Boxes):
    """Fully closed box"""

    ui_group = "Box"

    description = """This box is more of a building block than a finished item.
Use a vector graphics program (like Inkscape) to add holes or adjust the base
plate.

See BasedBox for variant with a base."""

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser("x", "y", "h", "outside")

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

        self.rectangularWall(x, h, "FFFF", bedBolts=[d2] * 4, move="right", label="Wall 1")
        self.rectangularWall(y, h, "FfFf", bedBolts=[d3, d2, d3, d2], move="up", label="Wall 2")
        self.rectangularWall(y, h, "FfFf", bedBolts=[d3, d2, d3, d2], label="Wall 4")
        self.rectangularWall(x, h, "FFFF", bedBolts=[d2] *4, move="left up", label="Wall 3")

        self.rectangularWall(x, y, "ffff", bedBolts=[d2, d3, d2, d3], move="right", label="Top")
        self.rectangularWall(x, y, "ffff", bedBolts=[d2, d3, d2, d3], label="Bottom")



