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
from boxes.walledges import WallMountedBox

class WallEdges(WallMountedBox):
    """Shows the different edge types for wall systems"""

    def __init__(self):
        super().__init__()
        self.buildArgParser(h=120)

    def render(self):
        self.generateWallEdges()

        h = self.h

        for i, c in enumerate("aAbBcCdD"):
            self.text(c, x=i*30+15, y=5)
        self.text("wallHolesAt", 115, 15)
        self.moveTo(0, 25)
        self.rectangularWall(40, h, "eAea", move="right")
        self.rectangularWall(40, h, "eBeb", move="right")
        self.rectangularWall(40, h, "eCec", callback=[
            lambda: self.wallHolesAt(20, 0, h, 90)], move="right")
        self.moveTo(10)
        self.rectangularWall(40, h, "eDed", move="right")
