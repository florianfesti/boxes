#!/usr/bin/python3
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

class Box(Boxes):
    def __init__(self, x, y, h, h2, thickness=4.0):
        self.x, self.y, self.h, self.h2 = x, y, h, h2
        Boxes.__init__(self, width=x+y+8*thickness, height=x+h+h2+4*thickness,
                       thickness=thickness)

    def side(self, w, h, h2):
        r = min(h-h2, w) / 2.0
        if (h-h2) > w:
            r = w / 2.0
            lx = 0
            ly = (h-h2) - w
        else:
            r = (h - h2) / 2.0
            lx = (w - 2*r) / 2.0
            ly = 0

        e_w = self.edges["F"].width()
        self.moveTo(3, 3)
        self.edge(e_w)
        self.edges["F"](w)
        self.edge(e_w)
        self.corner(90)
        self.edge(e_w)
        self.edges["F"](h2)
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
        x, y, h, h2 = self.x, self.y, self.h, self.h2
        t = self.thickness

        self.ctx.save()
        self.rectangularWall(x, h, "Ffef", move="up")
        self.rectangularWall(x, h2, "Ffef", move="up")

        self.rectangularWall(y, x, "ffff")
        self.ctx.restore()

        self.rectangularWall(x, h, "Ffef", move="right only")
        self.side(y, h, h2)
        self.moveTo(y+15, h+h2+15, 180)
        self.side(y, h, h2)

        self.close()

b = Box(80, 235, 300, 150)
b.edges["f"].settings.setValues(b.thickness, space=2, finger=2)
b.render()
