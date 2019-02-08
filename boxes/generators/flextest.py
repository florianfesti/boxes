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

from boxes import *


class FlexTest(Boxes):
    "Piece for testing different flex settings"

    ui_group = "Part"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FlexSettings)
        self.buildArgParser("x", "y")

    def render(self):
        x, y = self.x, self.y

        self.moveTo(5, 5)
        self.edge(10)
        self.edges["X"](x, y)
        self.edge(10)
        self.corner(90)
        self.edge(y)
        self.corner(90)
        self.edge(x + 20)
        self.corner(90)
        self.edge(y)
        self.corner(90)



