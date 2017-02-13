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


class RegularBox(Boxes):
    """Regular box"""

    ui_group = "Box"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser("h", "outside")
        self.argparser.add_argument(
            "--radius",  action="store", type=float, default=50.0,
            help="inner radius if the box (at the corners)")
        self.argparser.add_argument(
            "--n",  action="store", type=int, default=5,
            help="number of sides")
        self.argparser.add_argument(
            "--top",  action="store", type=str, default="none",
            choices=["none", "hole", "angled hole", "angled lid", "angled lid2", "round lid"],
            help="style of the top and lid")

    def render(self):
        self.open()

        r, h, n = self.radius, self.h, self.n

        if self.outside:
            r = r = r - self.thickness / math.cos(math.radians(360/(2*n)))
            if self.top == "none":
                h = self.adjustSize(h, False)
            elif "lid" in self.top and self.top != "angled lid":
                h = self.adjustSize(h) - self.thickness
            else:
                h = self.adjustSize(h)

        t = self.thickness

        edges.FingerJointSettings(self.thickness, True, angle=360./n).edgeObjects(self, chars="gGH")

        r, sh, side  = self.regularPolygon(n, radius=r)

        self.ctx.save()
        self.regularPolygonWall(corners=n, r=r, edges='F', move="right")
        if self.top == "angled lid":
            self.regularPolygonWall(corners=n, r=r, edges='e', move="right")
            self.regularPolygonWall(corners=n, r=r, edges='E', move="right")
        elif self.top in ("angled hole", "angled lid2"):
            self.regularPolygonWall(corners=n, r=r, edges='F', move="right",
                                    callback=[lambda:self.regularPolygonAt(
                                        0, 0, n, h=sh-t)])
            if self.top == "angled lid2":
                self.regularPolygonWall(corners=n, r=r, edges='E', move="right")
        elif self.top in ("hole", "round lid"):
            self.regularPolygonWall(corners=n, r=r, edges='F', move="right",
                          hole=(sh-t)*2)
        if self.top == "round lid":
            self.parts.disc(sh*2, move="right")

        self.ctx.restore()
        self.regularPolygonWall(corners=n, r=r, edges='F', move="up only")

        side = 2 * math.sin(math.radians(180.0/n)) * r
        fingers = self.top in ("hole", "round lid", "angled lid2")
        
        if n % 2:
            for i in range(n):
                self.rectangularWall(side, h, move="right",
                                     edges="fgfG" if fingers else "fgeG")
        else:
            for i in range(n//2):
                self.rectangularWall(side, h, move="right",
                                     edges="fGfG" if fingers else "fGeG")
                self.rectangularWall(side, h, move="right",
                                     edges="fgfg" if fingers else "fgeg")


        self.close()


def main():
    b = RegularBox()
    b.parseArgs()
    b.render()


if __name__ == '__main__':
    main()
