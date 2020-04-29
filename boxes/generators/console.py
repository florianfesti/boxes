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

class Console(Boxes):
    """Console with slanted panel"""

    ui_group = "Box"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=.5)
        self.addSettingsArgs(edges.StackableSettings)

        self.buildArgParser(x=100, y=100, h=100, hi=30)
        self.argparser.add_argument(
            "--angle",  action="store", type=float, default=50,
            help="angle of the front panel (90°=upright)")

    def render(self):
        x, y, h, hi = self.x, self.y, self.h, self.hi
        t = self.thickness

        panel = min((h-hi)/math.cos(math.radians(90-self.angle)),
                    y/math.cos(math.radians(self.angle)))
        top = y - panel * math.cos(math.radians(self.angle))
        h = hi + panel * math.sin(math.radians(self.angle))

        if top>0.1*t:
            borders = [y, 90, hi, 90-self.angle, panel, self.angle, top,
                       90, h, 90]
        else:
            borders = [y, 90, hi, 90-self.angle, panel, self.angle+90, h, 90]

        self.polygonWall(borders, move="right")
        self.polygonWall(borders, move="right")
        self.polygonWalls(borders, x)
