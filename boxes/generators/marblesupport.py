#!/usr/bin/env python3
# Copyright (C) 2020  Luca Schmid
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
from math import atan, degrees, floor, fmod, sqrt

class MarbleSupport(Boxes):
    """Support piece for other Marble* parts"""

    ui_group = "Unstable"

    def __init__(self):
        Boxes.__init__(self)

        self.buildArgParser(x=28.0, y=15.0) # outer dimensions (x_o, y_o) are (x + depth + thickness, y_o = y + 2 * dia)
        self.argparser.add_argument("--grid", type=float, default=15.0, help="grid spacing")
        self.argparser.add_argument("--dia", type=float, default=4.8, help="grid hole diameter")
        self.argparser.add_argument("--depth", type=float, default=4.0, help="grid hole depth")


    def pin(self, dia, depth):
        a = depth / 2
        b = dia / 24
        c = sqrt(a**2+b**2)
        alpha = degrees(atan(b/a))

        self.edge(a)
        self.corner(alpha)
        self.edge(c)
        self.corner(90-alpha)
        self.edge(dia-b*2)
        self.corner(90-alpha)
        self.edge(c)
        self.corner(alpha)
        self.edge(a)
        self.corner(-90)


    def render(self):
        x, y, grid, dia, d = self.x, self.y, self.grid, self.dia, self.depth
        t = self.thickness

        w = x + t

        n = floor(y / grid)
        r = fmod(y, grid) / 2
        s = 3*w/4
        alpha = degrees(atan(y/s))

        self.moveTo(d, r)
        self.edge(w/4)
        self.corner(alpha)
        self.edge(sqrt(s**2+y**2))
        self.corner(90-alpha)
        self.edge(2*dia)
        self.corner(90)
        self.edge(t)
        self.corner(90)
        self.edge(dia)
        self.corner(-90)
        self.edge(x)

        if r > 0:
            self.corner(90)
            self.edge(r)
            self.corner(-90)

        for _ in range(n):
            self.pin(dia, d)
            self.edge(grid-dia)
            self.corner(-90)
        self.pin(dia, d)

        if r > 0:
            self.edge(r)
            self.corner(90)


