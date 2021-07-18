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

class OpenBox(Boxes):
    """Box with top and front open"""

    ui_group = "Box"

    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("x", "y", "h", "outside")
        self.argparser.add_argument(
            "--edgetype", action="store",
            type=ArgparseEdgeType("Fh"), choices=list("Fh"),
            default="F",
            help="edge type")
        self.addSettingsArgs(edges.FingerJointSettings)

    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y, False)
            h = self.adjustSize(h, False)

        e = self.edgetype
        self.rectangularWall(x, h, [e, e, "e", e], move="right")
        self.rectangularWall(y, h, [e, "e", "e", "f"], move="up")
        self.rectangularWall(y, h, [e, "e", "e", "f"])
        self.rectangularWall(x, y, "efff", move="left")
