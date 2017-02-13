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


class TypeTray(Boxes):
    """Type tray - allows only continuous walls"""

    ui_group = "Tray"

    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("sx", "sy", "h", "hi", "outside")
        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=0.5)
        self.argparser.add_argument(
            "--gripheight", action="store", type=float, default=30,
            dest="gh", help="height of the grip hole in mm")
        self.argparser.add_argument(
            "--gripwidth", action="store", type=float, default=70,
            dest="gw", help="width of th grip hole in mm (zero for no hole)")

    def xSlots(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            posy = 0
            for y in self.sy:
                self.fingerHolesAt(posx, posy, y)
                posy += y + self.thickness

    def ySlots(self):
        posy = -0.5 * self.thickness
        for y in self.sy[:-1]:
            posy += y + self.thickness
            posx = 0
            for x in self.sx:
                self.fingerHolesAt(posy, posx, x)
                posx += x + self.thickness

    def xHoles(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            self.fingerHolesAt(posx, 0, self.hi)

    def yHoles(self):
        posy = -0.5 * self.thickness
        for y in self.sy[:-1]:
            posy += y + self.thickness
            self.fingerHolesAt(posy, 0, self.hi)

    def gripHole(self):
        if not self.gw:
            return

        x = sum(self.sx) + self.thickness * (len(self.sx) - 1)
        r = min(self.gw, self.gh) / 2.0
        self.rectangularHole(x / 2.0, self.gh * 1.5, self.gw, self.gh, r)

    def render(self):
        if self.outside:
            self.sx = self.adjustSize(self.sx)
            self.sy = self.adjustSize(self.sy)
            self.h = self.adjustSize(self.h, e2=False)
            if self.hi:
                self.hi = self.adjustSize(self.hi, e2=False)

        x = sum(self.sx) + self.thickness * (len(self.sx) - 1)
        y = sum(self.sy) + self.thickness * (len(self.sy) - 1)
        h = self.h
        hi = self.hi = self.hi or h
        t = self.thickness

        self.open()

        # outer walls
        self.rectangularWall(x, h, "Ffef", callback=[self.xHoles, None, self.gripHole],  move="right")
        self.rectangularWall(y, h, "FFeF", callback=[self.yHoles, ], move="up")
        self.rectangularWall(y, h, "FFeF", callback=[self.yHoles, ])
        self.rectangularWall(x, h, "Ffef", callback=[self.xHoles, ], move="left up")

        # floor
        self.rectangularWall(x, y, "ffff", callback=[self.xSlots, self.ySlots],move="right")
        # Inner walls
        for i in range(len(self.sx) - 1):
            e = [edges.SlottedEdge(self, self.sy, "f", slots=0.5 * hi), "f", "e", "f"]
            self.rectangularWall(y, hi, e, move="up")

        for i in range(len(self.sy) - 1):
            e = [edges.SlottedEdge(self, self.sx, "f"), "f",
                 edges.SlottedEdge(self, self.sx[::-1], "e", slots=0.5 * hi), "f"]
            self.rectangularWall(x, hi, e, move="up")

        self.close()


def main():
    b = TypeTray()
    b.parseArgs()
    b.render()


if __name__ == '__main__':
    main()
