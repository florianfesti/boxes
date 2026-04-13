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


class TriangularWall(Boxes):
    """Simple wall with options for different edges"""

    ui_group = "Part" # see ./__init__.py for names

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.CabinetHingeSettings)
        self.addSettingsArgs(edges.ClickSettings)
        self.addSettingsArgs(edges.DoveTailSettings)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.GearSettings)
        self.addSettingsArgs(edges.GripSettings)
        self.addSettingsArgs(edges.HingeSettings)
        self.addSettingsArgs(edges.ChestHingeSettings)
        self.addSettingsArgs(edges.SlideOnLidSettings)
        self.addSettingsArgs(edges.StackableSettings)

        self.buildArgParser(x=100, h=100)
        self.argparser.add_argument(
            "--radius", action="store", type=float,
            default=20, help="radius to strengthen the corners")

        self.argparser.add_argument(
            "--bottom_edge", action="store",
            type=ArgparseEdgeType("cCdDeEfFghiIjJkKlLmMnNoOpPqQRsSšŠuUvV"), choices=list("cCdDeEfFghiIjJkKlLmMnNoOpPqQRsSšŠuUvV"),
            default="e", help="edge type for bottom edge")
        self.argparser.add_argument(
            "--right_edge", action="store",
            type=ArgparseEdgeType("cCdDeEfFghiIjJkKlLmMnNoOpPqQRsSšŠuUvV"), choices=list("cCdDeEfFghiIjJkKlLmMnNoOpPqQRsSšŠuUvV"),
            default="e", help="edge type for right edge")
        self.argparser.add_argument(
            "--left_edge", action="store",
            type=ArgparseEdgeType("cCdDeEfFghiIjJkKlLmMnNoOpPqQRsSšŠuUvV"), choices=list("cCdDeEfFghiIjJkKlLmMnNoOpPqQRsSšŠuUvV"),
            default="e", help="edge type for left edge")


    def cb(self, nr):
        t = self.thickness
        x, h, r = self.x, self.h, self.radius
        r = min(r, x, h)
        l = [x, h, ((x-r)**2+(h-r)**2)**0.5][nr]
        if self.edgetypes[nr] == "f":
            self.fingerHolesAt(0, -2.5*t, l, 0)

    def render(self):
        # adjust to the variables you want in the local scope
        t = self.thickness

        self.edgetypes = [self.bottom_edge, self.right_edge, self.left_edge]

        self.moveTo(3*t, 3*t)
        self.rectangularTriangle(self.x, self.h, self.edgetypes, callback=self.cb, r=self.radius)
