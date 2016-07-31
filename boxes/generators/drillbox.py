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

class DrillBox(Boxes):
    """Not yet parametrized box for drills from 1 to 12.5mm
in 0.5mm steps, 3 holes each size"""
    def __init__(self):
        Boxes.__init__(self)
        self.x, self.y, self.h = 120, 240, 60

    def holesx(self):
        self.fingerHolesAt(0, 5, self.x, angle=0)
        self.fingerHolesAt(0, 25, self.x, angle=0)

    def holesy(self):
        self.fingerHolesAt(0, 5, self.y, angle=0)
        self.fingerHolesAt(0, 25, self.y, angle=0)


    def drillholes(self):
        for i in range(6):
            for j in range(4):
                for k in range(3):
                    r = (12.5-2*i-0.5*j) * 0.5
                    self.hole(i*20+10, j*60+k*20+10, r+0.05)

    def description(self):
        self.ctx.set_font_size(6)
        for i in range(4):
            for j in range(6):
                self.rectangularHole(i*60+30, 20*j+10, 58, 14+1*j)
                d = 2.5-0.5*i+2*j
                self.text("%.1f" % d, i*60+20, 19*j+6,
                          align="center")


    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        self.open()
        self.edges["f"].settings.setValues(self.thickness, space=3, finger=3,
                                surroundingspaces=1)

        self.moveTo(t, t)
        self.rectangularWall(x, h, "FfeF", callback=[self.holesx],move="right")
        self.rectangularWall(y, h, "FfeF", callback=[self.holesy], move="up")
        self.rectangularWall(y, h, "FfeF", callback=[self.holesy])
        self.rectangularWall(x, h, "FfeF", callback=[self.holesx],
                             move="left up")
        
        self.rectangularWall(x, y, "ffff", move="up")
        self.rectangularWall(x, y, "ffff", callback=[self.drillholes],
                             move="up")
        self.rectangularWall(x, y, "ffff", callback=[self.drillholes,
                                                     self.description],
                             move="up")

        self.close()

def main():
    b = DrillBox()
    b.parseArgs()
    b.render()

if __name__ == '__main__':
    main()
