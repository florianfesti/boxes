#!/usr/bin/python3
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


class FlexTest2(Boxes):
    "Piece for testing 2D flex settings"

    ui_group = "Part"

    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("x", "y")
        self.argparser.add_argument(
            "--fw", action="store", type=float, default=1,
            help="distance of flex cuts in multiples of thickness")

    def render(self):
        x, y = self.x, self.y

        self.rectangularWall(x, y, callback=[lambda: self.flex2D(x, y, self.fw)])


