#!/usr/bin/python
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

class TrayInsert(Boxes):
    def __init__(self, x, y, h, **kw):
        self.x, self.y, self.h = x, y, h
        t = kw.get("thickness", 4.0)
        Boxes.__init__(self, width=max(sum(x)+len(x)*t, sum(y)+len(y)*t)+2*t,
                       height=(len(x)+len(y)-2)*(h+t)+2*t, **kw)

    def render(self):
        x = sum(self.x) + self.thickness * (len(self.x)-1)
        y = sum(self.y) + self.thickness * (len(self.y)-1)
        h = self.h
        t = self.thickness

        self.moveTo(t, t)

        # Inner walls
        for i in range(len(self.x)-1):
            e = [SlottedEdge(self, self.y, slots=0.5*h), "e", "e", "e"]
            self.rectangularWall(y, h, e,
                                 move="up")
        for i in range(len(self.y)-1):
            e = ["e", "e",
                 SlottedEdge(self, self.x[::-1], "e", slots=0.5*h), "e"]
            self.rectangularWall(x, h, e,
                                 move="up")
        self.close()


# Calculate equidistant section
x = 260 # width
nx = 3
y = 300 # depth
ny = 4
thickness=4.0
dx = (x+thickness)/nx-thickness
dy = (y+thickness)/ny-thickness

sx = [dx] * nx
sy = [dy] * ny

# Or give sections by hand 
#sx = [80, 100, 80]
#sy = [80, 120, 200]

b = TrayInsert(sx, sy, 80, thickness=thickness, burn=0.1)
b.render()
