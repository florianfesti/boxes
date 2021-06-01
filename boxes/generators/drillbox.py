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

from boxes import Boxes, edges, Color


class DrillBox(Boxes):
    """A parametrized box for drills"""

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser(sx="25*3", sy="60*4", h=60)
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

    def holesx(self):
        x = sum(self.sx)
        self.fingerHolesAt(0, 5, x, angle=0)
        self.fingerHolesAt(0, 25, x, angle=0)

    def holesy(self):
        y = sum(self.sy)
        self.fingerHolesAt(0, 5, y, angle=0)
        self.fingerHolesAt(0, 25, y, angle=0)

    def drillholes(self, description=False):
        y = 0
        d = self.firsthole
        for dy in self.sy:
            x = 0
            for dx in self.sx:
                iy = dy / self.holes
                for k in range(self.holes):
                    self.hole(x + dx / 2, y + (k + 0.5) * iy, d + 0.05)
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
        h = self.h

        self.edges["f"].settings.setValues(self.thickness, space=3, finger=3, surroundingspaces=1)

        self.rectangularWall(x, h, "FfeF", callback=[self.holesx], move="right")
        self.rectangularWall(y, h, "FfeF", callback=[self.holesy], move="up")
        self.rectangularWall(y, h, "FfeF", callback=[self.holesy])
        self.rectangularWall(x, h, "FfeF", callback=[self.holesx], move="left up")

        self.rectangularWall(x, y, "ffff", move="right")
        self.rectangularWall(x, y, "ffff", callback=[self.drillholes], move="right")
        self.rectangularWall(x, y, "ffff", callback=[lambda: self.drillholes(description=True)], move="right")
