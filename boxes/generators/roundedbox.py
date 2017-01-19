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


class RoundedBox(Boxes):
    """Box with rounded corners"""

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings, finger=3.0, space=3.0)
        self.buildArgParser("x", "y", "h", "outside")
        self.argparser.add_argument(
            "--radius", action="store", type=float, default=15,
            help="Radius of the corners in mm")

    def render(self):
        self.open()

        x, y, h, r = self.x, self.y, self.h, self.radius

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            h = self.adjustSize(h)

        t = self.thickness

        self.ctx.save()
        self.roundedPlate(x, y, r, move="right")
        self.roundedPlate(x, y, r, move="right")
        self.ctx.restore()
        self.roundedPlate(x, y, r, move="up only")

        self.surroundingWall(x, y, r, h, "F", "F")

        self.close()


def main():
    b = RoundedBox()
    b.parseArgs()
    b.render()


if __name__ == '__main__':
    main()
