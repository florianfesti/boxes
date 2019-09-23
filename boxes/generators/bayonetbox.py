#!/usr/bin/env python3
# Copyright (C) 2013-2019 Florian Festi
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

class BayonetBox(Boxes):
    """Round box made from layers with twist on top"""

    description = """Glue together. All outside rings to the bottom, all inside rings to the top."""
    ui_group = "Box"

    def __init__(self):
        Boxes.__init__(self)
        
        self.argparser.add_argument(
            "--diameter",  action="store", type=float, default=50.,
            help="Diameter of the box in mm")
        self.argparser.add_argument(
            "--lugs",  action="store", type=int, default=10,
            help="number of locking lugs")
        self.buildArgParser("outside")

    def lowerCB(self):
        d = self.diameter
        r = d / 2
        t = self.thickness
        p = 0.05*t
        l = self.lugs

        a = 180 / l
        
        self.hole(0, 0, r=d/2 - 2.5*t)
        self.moveTo(d/2 - 1.5*t, 0, -90)

        for i in range(l):
            self.polyline(0, (-4/3*a, r-1.5*t), 0, 90, 0.5*t, -90, 0, (-2/3*a, r-t), 0, -90, 0.5*t, 90)

        self.moveTo(0, p)
            
        for i in range(l):
            self.polyline(0, (-2/3*a, r-1.5*t+p), 0, 90, 0.5*t, -90, 0, (-4/3*a, r-t+p), 0, -90, 0.5*t, 90)
        

    def upperCB(self):
        d = self.diameter
        r = d / 2
        t = self.thickness
        p = 0.05*t
        l = self.lugs

        a = 180 / l
        
        self.hole(0, 0, r=d/2 - 2.5*t)
        self.hole(0, 0, r=d/2 - 1.5*t)
        self.moveTo(d/2 - 1.5*t, 0, -90)

        for i in range(l):
            self.polyline(0, (-1.3*a, r-1.5*t+p), 0, 90, 0.5*t, -90, 0, (-0.7*a, r-t+p), 0, -90, 0.5*t, 90)        


    def render(self):
        d = self.diameter
        t = self.thickness
        p = 0.05*t

        if not self.outside:
            self.diameter = d = d - 3*t
        
        
        self.parts.disc(d, move="right")
        self.parts.disc(d, callback=lambda: self.hole(0, 0, d/2-1.5*t), move="right")
        self.parts.disc(d, callback=self.lowerCB, move="right")
        self.parts.disc(d, callback=self.upperCB, move="right")
        self.parts.disc(d, move="right")
