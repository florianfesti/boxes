# Copyright (C) 2013-2023 Florian Festi
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

from functools import partial

from boxes import *


class WallRack(Boxes):
    """Wall mountable rack for spices or other items"""

    ui_group = "WallMounted"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=1.0)
        self.addSettingsArgs(edges.MountingSettings)
        self.addSettingsArgs(edges.HandleEdgeSettings)

        self.buildArgParser(x=200, y=50, sh="100*3", outside=False)
        self.argparser.add_argument(
            "--top_edge", action="store",
            type=ArgparseEdgeType("eEGy"), choices=list("eEGy"),
            default="G", help="edge type for top edge")
        self.argparser.add_argument("--full_height_top", type=boolarg, default=True, help="Add full height of topmost rack to the back panel")
        self.argparser.add_argument(
            "--wall_height",  action="store", type=float, default=20.0,
            help="height of walls")
        self.argparser.add_argument(
            "--back_height",  action="store", type=float, default=1.5,
            help="height of the back as fraction of the front height")
        self.argparser.add_argument(
            "--side_edges", action="store",
            type=ArgparseEdgeType("Fh"), choices=list("Fh"),
            default="h", help="edge type holding the shelves together")
        self.argparser.add_argument(
            "--flat_bottom", type=boolarg, default=False, help="Make bottom Flat, so that the rack can also stand")

    def generate_shelves(self, x, y, front_height, back_height):
        se = self.side_edges
        for i in range(len(self.sh)):
            self.rectangularWall(x, y, "ffff", move="up", label=f"shelf {i+1}")
            self.rectangularWall(x, front_height, se + "fef", move="up", label=f"front lip {i+1}")
            self.trapezoidWall(y, front_height, back_height, se + "fe" + se, move="right", label=f"right lip {i+1}")
            self.trapezoidWall(y, front_height, back_height, se + "fe" + se, move="up", label=f"left lip {i+1}")
            self.move(y + self.thickness*2, back_height, "left", before=True)

    #Generate finger holes for back part
    def generate_finger_holes(self, x, back_height):
        t = self.thickness
        pos_y = 0
        for h in self.sh:
            self.fingerHolesAt(t*0.5, pos_y + 0.5*t, x, 0)
            self.fingerHolesAt(0, pos_y + t, back_height, 90)
            self.fingerHolesAt(x+t, pos_y + t, back_height, 90)
            pos_y += h

    def render(self):
        x, y, front_height = self.x, self.y, self.wall_height
        back_height = front_height * self.back_height
        t = self.thickness
        if self.outside:
            x = self.adjustSize(x, "h", "f")
            y = self.adjustSize(y)
            front_height = self.adjustSize(front_height)
            back_height = self.adjustSize(back_height)

        if self.full_height_top:
            total_height = sum(self.sh)
        else:
            total_height = sum(self.sh[:-1]) + back_height

        for h in self.sh if self.full_height_top else self.sh[:-1]:
            if h < back_height:
                raise ValueError(f"Sections in sh must be at least wall_height * back_height = {back_height} tall. {h} found.")

        be = "e" if self.flat_bottom and self.side_edges == "F" else "E"
        if be == "E" and self.full_height_top:
            total_height -= t

        self.rectangularWall(x+self.thickness, total_height, be + "E" + self.top_edge + "E",
                             callback=[partial(self.generate_finger_holes, x, back_height)], label="back wall", move="right")
        self.generate_shelves(x, y, front_height, back_height)
