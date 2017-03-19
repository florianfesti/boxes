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

class HingeBox(Boxes):
    """Box with lid attached by cabinet hinges"""

    ui_group = "Box"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.CabinetHingeSettings)
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

        self.rectangularWall(x, h, "FFeF", move="right")
        self.rectangularWall(y, h, "Ffef", move="up")
        self.rectangularWall(y, h, "Ffef")
        self.rectangularWall(x, h, "FFuF", move="left up")
        
        self.rectangularWall(x, hl, "UFFF", move="right")
        self.rectangularWall(y, hl, "efFf", move="up")
        self.rectangularWall(y, hl, "efFf")
        self.rectangularWall(x, hl, "eFFF", move="left up")

        self.rectangularWall(x, y, "ffff", move="right")
        self.rectangularWall(x, y, "ffff")
        self.rectangularWall(x, y, "ffff", move="left up only")
        self.edges['u'].parts()

        self.close()


