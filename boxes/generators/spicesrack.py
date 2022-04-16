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

class FrontEdge(edges.Edge):

    def __call__(self, length, **kw):
        with self.saved_context():
            a = 90
            r = (self.diameter +self.space) / 2
            self.ctx.scale(1, self.edge_width/r)
            for i in range(self.numx):
                self.corner(-a)
                self.corner(180, r)
                self.corner(-a)
        self.moveTo(length)

    def margin(self):
        return self.edge_width
                
class SpicesRack(Boxes):
    """Rack for cans of spices"""

    ui_group = "Shelf"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=1.0)

        self.argparser.add_argument(
            "--diameter",  action="store", type=float, default=55.,
            help="diameter of spice cans")
        
        self.argparser.add_argument(
            "--height",  action="store", type=float, default=60.,
            help="height of the cans that needs to be supported")
        self.argparser.add_argument(
            "--space",  action="store", type=float, default=10.,
            help="space between cans")
        self.argparser.add_argument(
            "--numx",  action="store", type=int, default=5,
            help="number of cans in a row")
        self.argparser.add_argument(
            "--numy",  action="store", type=int, default=6,
            help="number of cans in a column")
        self.argparser.add_argument(
            "--in_place_supports",  action="store", type=boolarg, default=False,
            help="place supports pieces in holes (check for fit yourself)")
        self.argparser.add_argument(
            "--feet",  action="store", type=boolarg, default=False,
            help="add feet so the rack can stand on the ground")


    def support(self, width, height, move=None):
        t = self.thickness
        tw = width + t
        th = height

        r = min(width - 2*t, height - 2*t)

        if self.move(tw, th, move, True):
            return

        self.polyline(width-r, 90, 0, (-90, r), 0, 90, height-r, 90, width, 90)
        self.edges["f"](height)

        self.move(tw, th, move)

    def foot(self, width, height, move=None):
        t = self.thickness
        tw, th = height, width + t

        if self.move(tw, th, move, True):
            return

        self.moveTo(0, t)
        self.edges["f"](height)
        self.polyline(0, 90, width, 90, 0, (90, height), width-height, 90)

        self.move(tw, th, move)

    def holes(self):
        w = 2* self.base_r
        r = self.diameter / 2
        a = self.base_angle
        l = self.hole_length
        self.moveTo(0, self.hole_distance)
        
        with self.saved_context():
            self.ctx.scale(1, l/self.base_h)
            self.moveTo(self.space/2, 0, 90)
            for i in range(self.numx):
                self.polyline(0, -a, 0, (-180+2*a, r), 0, -90-a, w, -90)
                self.moveTo(0, -(self.diameter+self.space))
        self.ctx.stroke()
        if self.feet and not self.feet_done:
            self.feet_done = True
            return

        if not self.in_place_supports:
            return
        inner_width = self.hole_distance + self.hole_length/3
        t = self.thickness
        for i in range(self.numx-1):
            with self.saved_context():
                self.moveTo((self.diameter+self.space)*(i+0.5)- (inner_width+t)/2, self.spacing)
                self.support(inner_width, (self.h-t)/2)

    def backCB(self):
        t = self.thickness
        dy = self.h/2 - t/2
        for i in range(self.numy):
            self.fingerHolesAt(0, (i+1)*self.h-0.5*self.thickness-dy, self.x, 0)
            for j in range(1, self.numx):
                self.fingerHolesAt(
                    j*(self.diameter+self.space),
                    (i+1)*self.h-t-dy, (self.h-t)/2, -90)

    def render(self):
        self.feet_done = False
        t = self.thickness
        self.x = x = self.numx * (self.diameter+self.space)
        d = self.diameter

        self.base_angle = 10
        self.base_r = self.diameter/2 * math.cos(math.radians(self.base_angle))
        self.base_h = self.diameter/2 * (1-math.sin(math.radians(self.base_angle)))
        self.angle = math.degrees(math.atan(self.base_r/self.height))
        self.hole_length = (self.base_h**2+self.height**2)**0.5
        self.hole_distance = (self.diameter-self.base_r) * math.sin(math.radians(self.angle))

        self.h = (self.space + d) / math.cos(math.radians(self.angle))
        h = self.numy * self.h - self.h / 2 + 6*t

        width = self.hole_distance + self.hole_length + self.space/2
        inner_width = self.hole_distance + self.hole_length/3
        
        self.edge_width = width - inner_width
        
        for i in range(self.numy):
            self.rectangularWall(x, inner_width,[
                "f", "e", FrontEdge(self, self), "e"],
                                 callback=[self.holes], move="up")

        self.rectangularWall(x, h,
                             callback=[self.backCB,
                                       None,
                                       lambda:self.hole(3*t, 3*t, 1.5),
                                       lambda:self.hole(3*t, 3*t, 1.5),
                             ], move="up")


        if not self.in_place_supports:
            self.partsMatrix((self.numx-1)*self.numy, self.numx-1, "up",
                             self.support, inner_width, (self.h-t)/2)
        if self.feet:
            self.partsMatrix(self.numx-1, self.numx-1, "up",
                             self.foot, width, (self.h-t)/2)
            
