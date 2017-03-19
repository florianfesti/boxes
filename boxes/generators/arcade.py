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

class Arcade(Boxes):
    """Desktop Arcade Maschine"""
    
    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.argparser.add_argument(
            "--width",  action="store", type=float, default=450.0,
            help="inner width of the console")

    def side(self, move=None):
        # TODO: Add callbacks

        y, h = self.y, self.h
        t = self.thickness

        if self.move(y+35, h+155, move, True):
            return
        
        self.moveTo(45, 0)
        self.fingerHolesAt(10, 10, self.bottom, 0)
        self.polyline(y-30, (90, 10))
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
        self.polyline(150, (90, 10), 124.45, (75, 10), 5)

        self.move(y+35, h+155, move)
        
    def keyboard(self):
        # Add holes for the joystick and buttons here
        pass

    def speakers(self):
        self.hole(self.width/4., 50, 40)
        self.hole(self.width*3/4., 50, 40)
        
    def render(self):
        y, h = self.y, self.h = 540, 450
        width = self.width
        t = self.thickness

        self.bottom = y-40-0.5*t
        self.back = 40
        self.backwall = h-40
        self.front = 120
        self.keyb = 150
        self.keyback = 50
        self.speaker = 150
        self.top = 100-t
        self.topback = 200-0.5*t

        # Initialize canvas
        self.open()
        # Floor
        self.rectangularWall(width, self.bottom, "efff", move="up")
        # Back
        self.rectangularWall(width, self.back, "Ffef", move="up")
        self.rectangularWall(width, self.backwall, move="up")
        self.rectangularWall(width, self.back, "efef", move="up")

        # Front bottom
        self.rectangularWall(width, self.front, "efff", move="up")
        self.rectangularWall(width, self.keyb, "FfFf", callback=[self.keyboard], move="up")
        self.rectangularWall(width, self.keyback, "ffef", move="up")
        # Top
        self.rectangularWall(width, self.speaker, "efff", callback=[None, None, self.speakers], move="up")
        self.rectangularWall(width, self.top, "FfFf", move="up")
        self.rectangularWall(width, self.topback, "ffef", move="up")
        # Sides
        self.side(move="up")
        self.side(move="up")

        self.close()

