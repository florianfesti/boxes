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


class Box4(Boxes):
    """Box with lid and integraded hinge"""

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.ChestHingeSettings)
        self.buildArgParser("x", "y", "h", "outside")
        self.argparser.add_argument(
            "--lidheight",  action="store", type=float, default=20.0,
            help="height of lid in mm")
        

    def render(self):
        self.open()

        x, y, h, hl = self.x, self.y, self.h, self.lidheight

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            h = self.adjustSize(h)

        t = self.thickness

        self.rectangularWall(x, h, "FfOf", move="up")
        self.rectangularWall(x, hl, "pfFf", move="up")
        self.rectangularWall(x, h, "Ffof", move="up")
        self.rectangularWall(x, hl, "PfFf", move="up")
        self.rectangularWall(y, h, "FFQF", move="up")
        self.rectangularWall(y, h, "FFQF", move="up")
        self.rectangularWall(y, hl, "FFQF", move="up")
        self.rectangularWall(y, hl, "FFqF", move="up")

        self.rectangularWall(x, y, "ffff", move="up")
        self.rectangularWall(x, y, "ffff")

        self.close()


def main():
    b = Box4()
    b.parseArgs()
    b.render()


if __name__ == '__main__':
    main()
