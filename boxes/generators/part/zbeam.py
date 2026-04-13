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


class ZBeam(Boxes):
    """Z-Beam (or U-Beam): three pieces joined at right angles"""
    description = """
With the "flanged_ubeam" option, there is a fourth piece the length of "y".
![U-Beam with flange](static/samples/ZBeam-flanged-ubeam.jpg)
"""

    ui_group = "Part"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.argparser.add_argument(
            "--top_edge", action="store", type=ArgparseEdgeType("Ffe"),
            choices=list("Ffe"), default="e", help="edge type for top edge")
        self.argparser.add_argument(
            "--bottom_edge", action="store", type=ArgparseEdgeType("Ffe"),
            choices=list("Ffe"), default="e", help="edge type for bottom edge")
        self.buildArgParser("x", "y")
        self.argparser.add_argument(
            "--z", action="store", type=float, default=100.0,
            help="inner depth in mm")
        self.argparser.add_argument(
            "--flanged_ubeam", action="store", type=boolarg, default=False,
            help="Add a fourth piece to make a U-Beam with a flange")
        self.buildArgParser("h", "outside")
        self.addSettingsArgs(edges.FingerJointSettings)

    def render(self):
        x, y, z, h = self.x, self.y, self.z, self.h
        t = self.thickness

        if self.outside:
            x = self.adjustSize(x, False)
            y = self.adjustSize(y, False)
            z = self.adjustSize(z, False)

        self.rectangularWall(
            x, h, self.bottom_edge + "F" + self.top_edge + "e", move="right")
        self.rectangularWall(
            y, h, self.bottom_edge + "f" + self.top_edge + "f", move="right")
        if self.flanged_ubeam:
            self.rectangularWall(
                z, h, self.bottom_edge + "F" + self.top_edge + "F", move="right")
            self.rectangularWall(
                y + self.thickness, h, self.bottom_edge + "e" + self.top_edge + "f")
        else:
            self.rectangularWall(z, h, self.bottom_edge + "e" + self.top_edge + "F")
