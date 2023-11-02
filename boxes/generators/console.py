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

    description = """

Console Arcade Stick

![Front](static/samples/ConsoleArcadeStickFront.jpg)
![Back](static/samples/ConsoleArcadeStickBack.jpg)
![Inside](static/samples/ConsoleArcadeStickInside.jpg)

Keyboard enclosure:
"""

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=.5)
        self.addSettingsArgs(edges.StackableSettings)

        self.buildArgParser(x=100, y=100, h=100, outside=False)
        self.argparser.add_argument(
            "--front_height",  action="store", type=float, default=30,
            help="height of the front below the panel (in mm)")
        self.argparser.add_argument(
            "--angle",  action="store", type=float, default=50,
            help="angle of the front panel (90°=upright)")

    def render(self):
        x, y, h, hf = self.x, self.y, self.h, self.front_height
        t = self.thickness

        if self.outside:
            self.x = x = self.adjustSize(x)
            self.y = y = self.adjustSize(y)
            self.h = h = self.adjustSize(h)

        panel = min((h-hf)/math.cos(math.radians(90-self.angle)),
                    y/math.cos(math.radians(self.angle)))
        top = y - panel * math.cos(math.radians(self.angle))
        h = hf + panel * math.sin(math.radians(self.angle))

        if top>0.1*t:
            borders = [y, 90, hf, 90-self.angle, panel, self.angle, top,
                       90, h, 90]
        else:
            borders = [y, 90, hf, 90-self.angle, panel, self.angle+90, h, 90]

        if hf < 0.01*t:
            borders[1:4] = [180-self.angle]

        self.polygonWall(borders, move="right")
        self.polygonWall(borders, move="right")
        self.polygonWalls(borders, x)
