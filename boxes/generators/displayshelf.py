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

class DisplayShelf(Boxes): # change class name here and below
    """Shelf with forward slanted floors"""
    
    ui_group = "Shelf"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)

        self.buildArgParser(x=400, y=100, h=300, outside=True)
        self.argparser.add_argument(
            "--num",  action="store", type=int, default=3,
            help="number of shelves")
        self.argparser.add_argument(
            "--front",  action="store", type=float, default=20.0,
            help="height of front walls")
        self.argparser.add_argument(
            "--angle",  action="store", type=float, default=30.0,
            help="angle of floors")

    def side(self):

        t = self.thickness
        a = math.radians(self.angle)
                
        hs = (self.sl+t) * math.sin(a) + math.cos(a) * t

        for i in range(self.num):
            pos_x = 0.5*t*math.sin(a)
            pos_y = hs - math.cos(a)*0.5*t + i * (self.h-hs) / (self.num - 0.5)
            self.fingerHolesAt(pos_x, pos_y, self.sl, -self.angle)
            pos_x += math.cos(-a) * (self.sl+0.5*t) + math.sin(a)*0.5*t
            pos_y += math.sin(-a) * (self.sl+0.5*t) + math.cos(a)*0.5*t
            self.fingerHolesAt(pos_x, pos_y, self.front, 90-self.angle)

    def render(self):
        # adjust to the variables you want in the local scope
        x, y, h = self.x, self.y, self.h
        f = self.front
        t = self.thickness

        if self.outside:
            x = self.adjustSize(x)
        
        # Initialize canvas
        self.open()

        a = math.radians(self.angle)

        self.sl = sl = (y - t * (math.cos(a) + math.sin(a)) - math.sin(a) * f) / math.cos(a)
        
        # render your parts here
        self.rectangularWall(y, h, callback=[self.side], move="up")
        self.rectangularWall(y, h, callback=[self.side], move="up")

        for i in range(self.num):
            self.rectangularWall(x, sl, "ffef", move="up")
            self.rectangularWall(x, f, "Ffef", move="up")

        self.close()

