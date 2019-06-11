#!/usr/bin/env python3
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

class SlatwallEdges(Boxes):
    """Shows the different edge types for slat walls"""

    ui_group = "SlatWall" # see ./__init__.py for names

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.SlatWallSettings)
        self.buildArgParser(h=120)

    def render(self):

        s = edges.SlatWallSettings(self.thickness, True,
                                   **self.edgesettings.get("SlatWall", {}))
        s.edgeObjects(self)
        self.slatWallHolesAt = edges.SlatWallHoles(self, s)

        h = self.h

        for i, c in enumerate("aAbBcC"):
            self.text(c, x=i*30+15, y=5)
        self.text("slatWallHolesAt", 115, 15)
        self.moveTo(0, 25)
        self.rectangularWall(40, h, "eAea", move="right")
        self.rectangularWall(40, h, "eBeb", move="right")
        self.rectangularWall(40, h, "eCec", callback=[
            lambda: self.slatWallHolesAt(20, 0, h, 90)], move="right")
