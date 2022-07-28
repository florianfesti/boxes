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

from boxes import Boxes, edges, Color, ArgparseEdgeType
from boxes.lids import _TopEdge

class DrillBox(_TopEdge):
    """A parametrized box for drills"""

    ui_group = "Tray"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings,
                             space=3, finger=3, surroundingspaces=1)
        self.addSettingsArgs(edges.RoundedTriangleEdgeSettings, outset=1)
        self.addSettingsArgs(edges.StackableSettings)
        self.addSettingsArgs(edges.MountingSettings)
        self.argparser.add_argument(
            "--top_edge", action="store",
            type=ArgparseEdgeType("eStG"), choices=list("eStG"),
            default="e", help="edge type for top edge")
        self.buildArgParser(sx="25*3", sy="60*4", sh="5:25:10",
                            bottom_edge="h")
        self.argparser.add_argument(
            "--holes",
            action="store",
            type=int,
            default=3,
            help="Number of holes for each size",
        )
        self.argparser.add_argument(
            "--firsthole",
            action="store",
            type=float,
            default=1.0,
            help="Smallest hole",
        )
        self.argparser.add_argument(
            "--holeincrement",
            action="store",
            type=float,
            default=.5,
            help="increment between holes",
        )

    def sideholes(self, l):
        t = self.thickness
        h = -0.5 * t
        for d in self.sh[:-1]:
            h += d + t
            self.fingerHolesAt(0, h, l, angle=0)


    def drillholes(self, description=False):
        y = 0
        d = self.firsthole
        for dy in self.sy:
            x = 0
            for dx in self.sx:
                iy = dy / self.holes
                for k in range(self.holes):
                    self.hole(x + dx / 2, y + (k + 0.5) * iy, d=d + 0.05)
                if description:
                    self.rectangularHole(x + dx / 2, y + dy / 2, dx - 2, dy - 2, color=Color.ETCHING)
                    self.text(
                        "%.1f" % d,
                        x + 2,
                        y + 2,
                        270,
                        align="right",
                        fontsize=6,
                        color=Color.ETCHING,
                    )
                    # TODO: make the fontsize dynamic to make the text fit in all cases
                d += self.holeincrement
                x += dx
            y += dy

    def render(self):
        x = sum(self.sx)
        y = sum(self.sy)

        h = sum(self.sh) + self.thickness * (len(self.sh)-1)
        b = self.bottom_edge
        t1, t2, t3, t4 = self.topEdges(self.top_edge)

        self.rectangularWall(
            x, h, [b, "f", t1, "F"],
            ignore_widths=[1, 6],
            callback=[lambda: self.sideholes(x)], move="right")
        self.rectangularWall(
            y, h, [b, "f", t2, "F"], callback=[lambda: self.sideholes(y)],
            ignore_widths=[1, 6],
            move="up")
        self.rectangularWall(
            y, h, [b, "f", t3, "F"], callback=[lambda: self.sideholes(y)],
            ignore_widths=[1, 6])
        self.rectangularWall(
            x, h, [b, "f", t4, "F"],
            ignore_widths=[1, 6],
            callback=[lambda: self.sideholes(x)], move="left up")
        if b != "e":
            self.rectangularWall(x, y, "ffff", move="right")
        for d in self.sh[:-2]:
            self.rectangularWall(
                x, y, "ffff", callback=[self.drillholes], move="right")
        self.rectangularWall(
            x, y, "ffff",
            callback=[lambda: self.drillholes(description=True)],
            move="right")
