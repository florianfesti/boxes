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
    """Box with just 3 walls"""
    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("x", "y", "h")

    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        self.open(width=x+y+10*t, height=y+h+10*t)

        self.edges["f"].settings.setValues(self.thickness, space=3, finger=3,
                                           surroundingspaces=1)

        d2 = [edges.Bolts(2)]
        d3 = [edges.Bolts(3)]

        d2 = d3 = None

        self.moveTo(t, t)
        self.rectangularWall(x, h, "FFeF", bedBolts=d2, move="right")
        self.rectangularWall(y, h, "Feef", bedBolts=d3, move="up")
        self.rectangularWall(y, h, "Feef", bedBolts=d3)
        #self.rectangularWall(x, h, "FFeF", bedBolts=d2, move="left up")
        
        self.rectangularWall(x, y, "efff", bedBolts=[d2, d3, d2, d3], move="left")
        #self.rectangularWall(x, y, "ffff", bedBolts=[d2, d3, d2, d3])

        self.close()

def main():
    b = Box()
    b.parseArgs()
    b.render()

if __name__ == '__main__':
    main()
