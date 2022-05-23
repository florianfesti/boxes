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


class MagazinFile(Boxes):
    """Open magazine file"""

    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("x", "y", "h", "hi", "outside")
        self.addSettingsArgs(edges.FingerJointSettings)

    def side(self, w, h, hi):
        r = min(h - hi, w) / 2.0

        if (h - hi) > w:
            r = w / 2.0
            lx = 0
            ly = (h - hi) - w
        else:
            r = (h - hi) / 2.0
            lx = (w - 2 * r) / 2.0
            ly = 0

        e_w = self.edges["F"].startwidth()
        self.moveTo(3, 3)
        self.edge(e_w)
        self.edges["F"](w)
        self.edge(e_w)
        self.corner(90)
        self.edge(e_w)
        self.edges["F"](hi)
        self.corner(90)
        self.edge(e_w)
        self.edge(lx)
        self.corner(-90, r)
        self.edge(ly)
        self.corner(90, r)
        self.edge(lx)
        self.edge(e_w)
        self.corner(90)
        self.edges["F"](h)
        self.edge(e_w)
        self.corner(90)

    def render(self):

        if self.outside:
            self.x = self.adjustSize(self.x)
            self.y = self.adjustSize(self.y)
            self.h = self.adjustSize(self.h, e2=False)

        x, y, h, = self.x, self.y, self.h
        self.hi = hi = self.hi or (h / 2.0)
        t = self.thickness


        with self.saved_context():
            self.rectangularWall(x, h, "Ffef", move="up")
            self.rectangularWall(x, hi, "Ffef", move="up")
            self.rectangularWall(x, y, "ffff")

        self.rectangularWall(x, h, "Ffef", move="right only")
        self.side(y, h, hi)
        self.moveTo(y + 15, h + hi + 15, 180)
        self.side(y, h, hi)



