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

from boxes import ArgparseEdgeType, Boxes, edges
from boxes.generators.gridfinitytraylayout import GridfinityTrayLayout
from boxes.lids import LidSettings, _TopEdge


class GridfinityDrillBox(_TopEdge, GridfinityTrayLayout):
    """A Gridfinity box for drills or similar tools"""

    description = """You need to add a hole pattern to all horizontal layers except the very bottom"""

    ui_group = "Tray"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.pitch = 42.0 # gridfinity pitch is defined as 42.
        self.opening = 38
        self.opening_margin = 2

        self.addSettingsArgs(edges.FingerJointSettings,
                             space=3, finger=3, surroundingspaces=1)
        self.addSettingsArgs(edges.RoundedTriangleEdgeSettings, outset=1)
        self.addSettingsArgs(edges.StackableSettings)
        self.addSettingsArgs(edges.MountingSettings)
        self.addSettingsArgs(LidSettings)
        self.argparser.add_argument("--nx", type=int, default=3, help="number of gridfinity grids in X direction")
        self.argparser.add_argument("--ny", type=int, default=2, help="number of gridfinity grids in Y direction")
        self.argparser.add_argument("--margin", type=float, default=0.75, help="Leave this much total margin on the outside, in mm")
        self.argparser.add_argument(
            "--top_edge", action="store",
            type=ArgparseEdgeType("eStG"), choices=list("eStG"),
            default="e", help="edge type for top edge")
        self.buildArgParser(sh="5:25:10")

    def sideholes(self, l):
        t = self.thickness
        h = -0.5 * t
        for d in self.sh[:-1]:
            h += d + t
            self.fingerHolesAt(0, h, l, angle=0)


    def render(self):
        self.x = x = self.pitch * self.nx - self.margin - 2 * self.thickness
        self.y = y = self.pitch * self.ny - self.margin - 2 * self.thickness

        h = sum(self.sh) + self.thickness * (len(self.sh)-1)
        b = "F"
        t1, t2, t3, t4 = self.topEdges(self.top_edge)

        self.rectangularWall(
            x, h, [b, "f", t1, "f"],
            ignore_widths=[1, 6],
            callback=[lambda: self.sideholes(x)], move="right")
        self.rectangularWall(
            y, h, [b, "F", t2, "F"], callback=[lambda: self.sideholes(y)],
            ignore_widths=[1, 6],
            move="up")
        self.rectangularWall(
            y, h, [b, "F", t3, "F"], callback=[lambda: self.sideholes(y)],
            ignore_widths=[1, 6])
        self.rectangularWall(
            x, h, [b, "f", t4, "f"],
            ignore_widths=[1, 6],
            callback=[lambda: self.sideholes(x)], move="left up")
        if b != "e":
            self.rectangularWall(x, y, "ffff", callback=[self.baseplate_etching], move="right")
        for d in self.sh[:-1]:
            self.rectangularWall(
                x, y, "ffff", move="right")
        self.lid(x, y, self.top_edge)
        foot = self.opening - self.opening_margin
        for i in range(min(self.nx * self.ny, 4)):
            self.rectangularWall(foot, foot, move="right")
