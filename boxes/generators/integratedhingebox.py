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


class IntegratedHingeBox(Boxes):
    """Box with lid and integraded hinge"""

    ui_group = "Box"

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

        hx = self.edges["O"].startwidth()

        e1 = edges.CompoundEdge(self, "Fe", (h-hx, hx))
        e2 = edges.CompoundEdge(self, "eF", (hx, h-hx))
        e_back = ("F", e1, "e", e2)

        self.rectangularWall(x, h-hx, "FfOf", ignore_widths=[2], move="up")
        self.rectangularWall(x, hl-hx, "pfFf", ignore_widths=[1], move="up")
        self.rectangularWall(x, h-hx, "Ffof", ignore_widths=[5], move="up")
        self.rectangularWall(x, hl-hx, "PfFf", ignore_widths=[6], move="up")
        self.rectangularWall(y, h, "FFeF", move="up")
        self.rectangularWall(y, h, e_back, move="up")
        self.rectangularWall(y, hl, "FFeF", move="up")
        self.rectangularWall(y, hl-hx, "FFqF", move="up")

        self.rectangularWall(x, y, "ffff", move="up")
        self.rectangularWall(x, y, "ffff")

        self.close()


def main():
    b = IntegratedHingeBox()
    b.parseArgs()
    b.render()


if __name__ == '__main__':
    main()
