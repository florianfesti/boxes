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

class FanHole(Boxes):
    """Hole pattern for mounting a fan"""

    ui_group = "Holes"

    def __init__(self):
        Boxes.__init__(self)

        self.argparser.add_argument(
            "--diameter",  action="store", type=float, default=80,
            help="diameter of the fan hole")
        self.argparser.add_argument(
            "--mounting_holes",  action="store", type=float, default=3,
            help="diameter of the fan mounting holes")
        self.argparser.add_argument(
            "--mounting_holes_inset",  action="store", type=float, default=5,
            help="distance of the fan mounting holes from the outside")
        self.argparser.add_argument(
            "--arms",  action="store", type=int, default=10,
            help="number of arms")
        self.argparser.add_argument(
            "--inner_disc",  action="store", type=float, default=.2,
            help="relative size of the inner disc")
        self.argparser.add_argument(
            "--style",  action="store", type=str, default="CW Swirl",
            choices=["CW Swirl", "CCW Swirl", "Hole"],
            help="Style of the fan hole")
        

    def arc(self, d, a):
        r = abs(1/math.cos(math.radians(90-a/2))*d/2)
        self.corner(-a/2)
        self.corner(a, r)
        self.corner(-a/2)

    def swirl(self, r, ri_rel=.1, n=20):

        d = 2*r
        #r = d/2
        ri = ri_rel * r

        ai = 90
        ao = 360/n * 0.8
        # angle going in
        a1 = math.degrees(math.atan( 
            ri*math.sin(math.radians(ai)) /
            (r - ri*math.cos(math.radians(ai)))))
        d1= (ri*math.sin(math.radians(ai))**2 +
             (r - ri*math.cos(math.radians(ai)))**2)**.5
        d2= (ri*math.sin(math.radians(ai-ao))**2 +
             (r - ri*math.cos(math.radians(ai-ao)))**2)**.5

        # angle coming out
        a_i2 = math.degrees(math.atan(
            (r*math.sin(math.radians(ao)) - ri*math.sin(math.radians(ai))) /
            (r*math.cos(math.radians(ao)) - ri*math.cos(math.radians(ai)))))
        a3 = a1 + a_i2
        a2 = 90 + a_i2 - ao

        self.moveTo(0, -r, 180)

        for i in range(n):
            with self.saved_context():
                self.corner(-ao, r)
                self.corner(-a2)
                self.arc(d2, -90)
                self.corner(-180+a3)
                self.arc(d1, 85)
                self.corner(-90-a1)
            
            self.moveArc(-360./n, r)        

    def render(self):
        r_h = self.mounting_holes / 2
        d = self.diameter
        inset = self.mounting_holes_inset

        for px in (inset, d-inset):
            for py in (inset, d-inset):
                self.hole(px, py, r_h)
        self.moveTo(d/2, d/2)
        print(self.style)
        if self.style == "CW Swirl":
            self.ctx.scale(-1, 1)
            self.swirl(d/2, self.inner_disc, self.arms)
        elif self.style == "CCW Swirl":
            self.swirl(d/2, self.inner_disc, self.arms)
        else: #Hole
            self.hole(0, 0, d=d)
