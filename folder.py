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
import math

class Folder(Boxes):

    def __init__(self, x, y, h, r=0):
        Boxes.__init__(self, width=2*x+3*h+20, height=y+20)
        self.x = x
        self.y = y
        self.h = h
        self.r = r

    def render(self):
        x, y, r, h = self.x, self.y, self.r, self.h
        c2 = math.pi * h
        self.moveTo(r+self.thickness, self.thickness)
        self.edge(x-r)
        self.flexEdge(c2, y)
        self.edge(x-r)
        self.corner(90, r)
        self.edge(y-2*r)
        self.corner(90, r)
        self.edge(2*x-2*r+c2)
        self.corner(90, r)
        self.edge(y-2*r)
        self.corner(90, r)
        
        self.close()

f = Folder(240, 350, 20, 15)
f.render()
