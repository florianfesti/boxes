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
import math

class AngledBox(Boxes):
    """Box with both ends cornered"""

    ui_group = "Box"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser("x", "y", "h", "outside")
        self.argparser.add_argument(
            "--n",  action="store", type=int, default=5,
            help="number of walls at one side (1+)")
        self.argparser.add_argument(
            "--top",  action="store", type=str, default="none",
            choices=["none", "angled hole", "angled lid", "angled lid2"],
            help="style of the top and lid")

    def floor(self, x, y, n, edge='e', hole=None, move=None, callback=None):
        r, h, side  = self.regularPolygon(2*n+2, h=y/2.0)
        t = self.thickness
        
        if n % 2:
            lx = x - 2 * h + side
        else:
            lx = x - 2 * r + side
        
        edge = self.edges.get(edge, edge)

        tx = x + 2 * edge.spacing()
        ty = y + 2 * edge.spacing()
        
        if self.move(tx, ty, move, before=True):
            return

        self.moveTo((tx-lx)/2., 0)

        if hole:
            self.ctx.save()
            hr, hh, hside  = self.regularPolygon(2*n+2, h=y/2.0-t)
            dx = side - hside
            hlx = lx - dx
            
            self.moveTo(dx/2.0, t+edge.spacing())
            for i, l in enumerate(([hlx] + ([hside] * n))* 2):
                self.edge(l)
                self.corner(360.0/(2*n + 2))
            self.ctx.restore()

        for i, l in enumerate(([lx] + ([side] * n))* 2):
            self.cc(callback, i, 0, edge.startwidth() + self.burn)
            edge(l)
            self.edgeCorner(edge, edge, 360.0/(2*n + 2))

        self.move(tx, ty, move)

    def render(self):
        self.open()

        x, y, h, n = self.x, self.y, self.h, self.n

        if n < 1:
            n = self.n = 1

        if x < y:
            x, y = y, x

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            if self.top == "none":
                h = self.adjustSize(h, False)
            elif "lid" in self.top and self.top != "angled lid":
                h = self.adjustSize(h) - self.thickness
            else:
                h = self.adjustSize(h)

        t = self.thickness

        r, hp, side  = self.regularPolygon(2*n+2, h=y/2.0)
        
        if n % 2:
            lx = x - 2 * hp + side
        else:
            lx = x - 2 * r + side
        
        edges.FingerJointSettings(self.thickness, True, angle=360./(2 * (n+1))).edgeObjects(self, chars="gGH")


        self.ctx.save()
        self.floor(x, y , n, edge='F', move="right")
        if self.top == "angled lid":
            self.floor(x, y, n, edge='e', move="right")
            self.floor(x, y, n, edge='E', move="right")
        elif self.top in ("angled hole", "angled lid2"):
            self.floor(x, y, n, edge='F', move="right", hole=True)
            if self.top == "angled lid2":
                self.floor(x, y, n, edge='E', move="right")
        self.ctx.restore()
        self.floor(x, y , n, edge='F', move="up only")

        fingers = self.top in ("angled lid2", "angled hole")

        self.rectangularWall(lx, h, move="right",
                             edges="fGfG" if fingers else "fGeG")

        for i in range(2):
            for i in range(n):
                if i % 2:
                    self.rectangularWall(side, h, move="right",
                                         edges="fGfG" if fingers else "fGeG")
                else:
                    self.rectangularWall(side, h, move="right",
                                         edges="fgfg" if fingers else "fgeg")

        if i % 2:
            self.rectangularWall(lx, h, move="right",
                                 edges="fgfg" if fingers else "fGeG")
        else:
            self.rectangularWall(lx, h, move="right",
                                 edges="fGfG" if fingers else "fGeG")

        self.close()


