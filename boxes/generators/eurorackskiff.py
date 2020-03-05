#!/usr/bin/env python3
# Copyright (C) 2013-2017 Florian Festi
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


class EuroRackSkiff(Boxes):
    """3U Height case with adjustable width and height and included rails"""

    ui_group = "Box"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser("h")
        self.argparser.add_argument(
            "--hp", action="store", type=int, default=84,
            help="Width of the case in HP")
        

    def wallxCB(self, x):
        t = self.thickness
        
    def wallyCB(self, y):
        t = self.thickness
        self.fingerHolesAt(6, self.h-1.5*t, y, 0)

    def railHoles(self):
        for i in range(0, self.hp):
            self.hole(i*5.08 + 2.54, 3, d=3.0)
        
    def render(self):

        t = self.thickness
        h = self.h
        y = self.hp * 5.08
        x = 128.5
        
        
        self.rectangularWall(y, 6, "feee", callback=[self.railHoles] , move="up")
        self.rectangularWall(y, 6, "feee", callback=[self.railHoles] , move="up")
        self.rectangularWall(x, h, "fFeF", callback=[self.wallxCB(x)],
                             move="right")
        self.rectangularWall(y, h, "ffef", callback=[self.wallyCB(y)], move="up")
        self.rectangularWall(y, h, "ffef", callback=[self.wallyCB(y)])
        self.rectangularWall(x, h, "fFeF", callback=[self.wallxCB(x)],
                             move="left up")
        self.rectangularWall(x, y, "FFFF", callback=[], move="right")
        



