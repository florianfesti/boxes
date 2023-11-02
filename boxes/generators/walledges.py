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

from boxes.walledges import _WallMountedBox

class WallEdges(_WallMountedBox):
    """Shows the different edge types for wall systems"""

    def __init__(self) -> None:
        super().__init__()
        self.buildArgParser(h=120)

    def render(self):
        self.generateWallEdges()

        h = self.h

        self.moveTo(0, 25)
        self.rectangularWall(
            40, h, "eAea", move="right",
            callback=[lambda : (self.text("a", 0, -20),
                                self.text("A", 30, -20))])
        self.rectangularWall(
            40, h, "eBeb", move="right",
            callback=[lambda : (self.text("b", 0, -20),
                                self.text("B", 30, -20))])
        self.rectangularWall(40, h, "eCec",
            callback=[lambda : (self.text("c", 0, -20),
                                self.text("C", 30, -20),
                                self.text("wallHolesAt", -5, -30),
                                self.wallHolesAt(20, 0, h, 90))], move="right")
        self.moveTo(10)
        self.rectangularWall(
            40, h, "eDed", move="right",
            callback=[lambda : (self.text("d", 0, -20),
                                self.text("D", 30, -20))])
