#!/usr/bin/env python3
# Copyright (C) 2013-2016 Florian Festi
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

class Arcade(Boxes): # change class name here and below
    """Desktop Arcade Maschine"""
    
    def __init__(self):
        Boxes.__init__(self)
        # remove cli params you do not need
        #self.buildArgParser("x", "y","h")

    def side(self, move=None):
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        if self.move(x, y, move, True):
            return
        
        self.moveTo(50, 0)
        self.fingerHolesAt(20, 10, self.bottom, 0)
        self.polyline(y-20, (90, 10))
        self.fingerHolesAt(0.5*t, 10, self.back, 0)
        self.fingerHolesAt(h-40-40, 10, self.back, 0)
        
        self.polyline(h-10, (45, 10))
        self.fingerHolesAt(0, 10, self.topback, 0)
        self.fingerHolesAt(200, 10+0.5*t, self.top, 90)
        self.fingerHolesAt(200-0.5*t, 110, self.speaker, -180)
        self.polyline(200, (90, 10), 100, (90, 10), 100, (-90, 10),  350, (-30, 10))
        self.fingerHolesAt(0, 10, self.keyb, 0)
        self.fingerHolesAt(-0.5*t, 10+0.5*t, self.keyback, 90)
        self.fingerHolesAt(150+0.5*t, 10+0.5*t, self.front, 90)
        self.polyline(150, (90, 10), 72.7, (75, 10), 5)

        self.move(x, y, move)
        
    def keyboard(self):
        pass

    def speakers(self):
        self.hole(self.x/4., 50, 40)
        self.hole(self.x*3/4., 50, 40)
        
    def render(self):
        # adjust to the variables you want in the local scope
        x, y, h = self.x, self.y, self.h = 450, 540, 400
        t = self.thickness

        self.bottom = y-40-0.5*t
        self.back = 40
        self.backwall = h-40
        self.front = 70
        self.keyb = 150
        self.keyback = 40
        self.speaker = 150
        self.top = 100-t
        self.topback = 200-0.5*t

        # Initialize canvas
        self.open()
        # floor
        self.rectangularWall(x, self.bottom, "efff", move="up")
        # Back
        self.rectangularWall(x, self.back, "Ffef", move="up")
        self.rectangularWall(x, self.backwall, move="up")
        self.rectangularWall(x, self.back, "efef", move="up")

        # front bottom 
        self.rectangularWall(x, self.front, "efff", move="up")
        self.rectangularWall(x, self.keyb, "FfFf", callback=[self.keyboard], move="up")
        self.rectangularWall(x, self.keyback, "ffef", move="up")
        #top
        self.rectangularWall(x, self.speaker, "efff", callback=[None, None, self.speakers], move="up")
        self.rectangularWall(x, self.top, "FfFf", move="up")
        self.rectangularWall(x, self.topback, "ffef", move="up")

        self.side(move="up")

        self.close()

def main():
    b = Arcade() # change to class name
    b.parseArgs()
    b.render()

if __name__ == '__main__':
    main()
