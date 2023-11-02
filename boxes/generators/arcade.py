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
    """Desktop Arcade Machine"""
    
    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.argparser.add_argument(
            "--width",  action="store", type=float, default=450.0,
            help="inner width of the console")
        self.argparser.add_argument(
            "--monitor_height",  action="store", type=float, default=350.0,
            help="inner width of the console")
        self.argparser.add_argument(
            "--keyboard_depth",  action="store", type=float, default=150.0,
            help="inner width of the console")

    def side(self, move=None):
        # TODO: Add callbacks

        y, h = self.y, self.h
        t = self.thickness
        r = 10
        d_30 = 2* r * math.tan(math.radians(15))

        tw, th = y+2*r+(self.front+t) * math.sin(math.radians(15)), h+2*r+(self.topback+t)/2**0.5
        if self.move(tw, th, move, True):
            return
        
        self.moveTo(r+(self.front+t) * math.sin(math.radians(15)), 0)

        with self.saved_context():
            self.moveTo(0, r)
            self.polyline(y, 90, h, 45, self.topback+t, 90, self.top+2*t, 90, 100, -90, self.monitor_height, -30, self.keyboard_depth+2*t, 90, self.front+t, 75)
        
        self.fingerHolesAt(10, r+t/2, self.bottom, 0)
        self.polyline(y, (90, r))
        self.fingerHolesAt(0.5*t, r+t/2, self.back, 0)
        self.fingerHolesAt(h-40-40, r+t/2, self.back, 0)
        
        self.polyline(h, (45, r))
        self.fingerHolesAt(0, r+t/2, self.topback, 0)
        self.fingerHolesAt(self.topback+t/2, r+t, self.top, 90)
        self.fingerHolesAt(self.topback, self.top+r+1.5*t, self.speaker, -180)
        self.polyline(self.topback+t, (90, r), self.top+2*t, (90, r), 100-2*r, (-90, r),  self.monitor_height-2*r-d_30, (-30, r))
        self.fingerHolesAt(-d_30+t, r+.5*t, self.keyboard_depth, 0)
        self.fingerHolesAt(-d_30+0.5*t, r+t, self.keyback, 90)
        self.fingerHolesAt(self.keyboard_depth-d_30+1.5*t, r+t, self.front, 90)
        self.polyline(self.keyboard_depth-d_30+2*t, (90, r), self.front+t, (75, r))

        self.move(tw, th, move)
        
    def keyboard(self):
        # Add holes for the joystick and buttons here
        pass

    def speakers(self):
        self.hole(self.width/4., 50, 40)
        self.hole(self.width*3/4., 50, 40)
        
    def render(self):
        width = self.width
        t = self.thickness

        self.back = 40
        self.front = 120
        self.keyback = 50
        self.speaker = 150
        self.top = 100
        self.topback = 200
        y, h = self.y, self.h = 540, 450
        y = self.y = ((self.topback+self.top+3*t-100+self.monitor_height) / 2**0.5
                      + (self.keyboard_depth+2*t)*math.cos(math.radians(15))
                      - (self.front+t) * math.sin(math.radians(15)))
        h = self.h = ((self.monitor_height-self.topback+self.top+1*t+100) / 2**0.5 +
                      + (self.keyboard_depth+2*t)*math.sin(math.radians(15))
                      + (self.front+t) * math.cos(math.radians(15)))
                      
        self.bottom = y-40-0.5*t
        self.backwall = h-40

        # Floor
        self.rectangularWall(width, self.bottom, "efff", move="up")
        # Back
        self.rectangularWall(width, self.back, "Ffef", move="up")
        self.rectangularWall(width, self.backwall, move="up")
        self.rectangularWall(width, self.back, "efef", move="up")

        # Front bottom
        self.rectangularWall(width, self.front, "efff", move="up")
        self.rectangularWall(width, self.keyboard_depth, "FfFf", callback=[self.keyboard], move="up")
        self.rectangularWall(width, self.keyback, "ffef", move="up")
        # Top
        self.rectangularWall(width, self.speaker, "efff", callback=[None, None, self.speakers], move="up")
        self.rectangularWall(width, self.top, "FfFf", move="up")
        self.rectangularWall(width, self.topback, "ffef", move="up")
        # Sides
        self.side(move="up")
        self.side(move="up")


