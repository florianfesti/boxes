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
    """Fully closed box"""
    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("x", "y", "h", "outside")
        self.argparser.set_defaults(
            fingerjointfinger=3.0,
            fingerjointspace=3.0
            )

    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            h = self.adjustSize(h)

        self.open()

        d2 = [edges.Bolts(2)]
        d3 = [edges.Bolts(3)]

        d2 = d3 = None

        self.moveTo(t, t)
        self.rectangularWall(h, y, "FfFe")
        self.moveTo(h+2*t, 0)
        self.rectangularWall(x, y, "FFFF")
        self.moveTo(x+3*t, 0)
        self.rectangularWall(h, y, "FeFf")
        self.moveTo(-(x+3*t), y+3*t)
        self.rectangularWall(x, h, "ffef")
        #self.moveTo(0, -(h+y+5*t))
        self.moveTo(0, (h+3*t))
        self.rectangularWall(x, h, "efff")
        
        #self.moveTo(t, t)
        #self.rectangularWall(x, h, "FFeF", bedBolts=d2)
        #self.moveTo(x+3*t, 0)
        #self.rectangularWall(y, h, "Feef", bedBolts=d3)
        #self.moveTo(0, h+3*t)
        #self.rectangularWall(y, h, "Feef", bedBolts=d3)
        #self.moveTo(-x-3*t, 0)
        #self.rectangularWall(x, y, "efff", bedBolts=[d2, d3, d2, d3])

        self.close()

def main():
    b = Box()
    b.parseArgs()
    b.render()

if __name__ == '__main__':
    main()
