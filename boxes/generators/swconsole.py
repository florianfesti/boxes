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

class SlatwallConsole(Boxes):
    """Outset and angled plate to mount stuff to"""

    ui_group = "SlatWall"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.SlatWallSettings)

        self.buildArgParser(sx=100, h=100, outside=True)

        self.argparser.add_argument(
            "--top_depth",  action="store", type=float, default=50,
            help="depth at the top")
        self.argparser.add_argument(
            "--bottom_depth",  action="store", type=float, default=35,
            help="depth at the bottom")

    def backHoles(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            self.slatWallHolesAt(posx, 0, self.h, 90)

    def frontHoles(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            self.fingerHolesAt(posx, 0, self.front, 90)

    def render(self):
        # Add slat wall edges
        s = edges.SlatWallSettings(self.thickness, True,
                                   **self.edgesettings.get("SlatWall", {}))
        s.edgeObjects(self)
        self.slatWallHolesAt = edges.SlatWallHoles(self, s)


        if self.outside:
            self.sx = self.adjustSize(self.sx)
            self.h = self.adjustSize(self.h)

        x = sum(self.sx) + self.thickness * (len(self.sx) - 1)
        h = self.h
        td = self.top_depth
        bd = self.bottom_depth

        self.front = (h**2 + (td-bd)**2)**0.5
            
        self.rectangularWall(x, h, "eCec", callback=[self.backHoles],
                             move="up")
        self.rectangularWall(x, self.front, "eFeF",
                             callback=[self.frontHoles], move="up")

        for i in range(len(self.sx)+1):
            self.trapezoidWall(h, td, bd, "befe", move="up")
