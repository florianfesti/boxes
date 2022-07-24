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
from boxes.walledges import _WallMountedBox

class PinEdge(edges.BaseEdge):
    def __call__(self, length, **kw):
        w2 = self.settings.pinwidth/2
        l = self.settings.pinlength
        s = self.settings.pinspacing
        inc = self.settings.pinspacing_increment
        t = self.settings.thickness
        
        pin = [0, -90, l+t-w2, (180, w2), l+t-w2, -90]

        self.edge(s/2-w2)
        s += inc/2
        for i in range(self.pins-1):
            self.polyline(*pin, s-2*w2)
            s+=inc
        self.polyline(*pin, s/2-w2-inc/4)

    def margin(self):
        return self.settings.thickness+self.settings.pinlength

class WallPinRow(_WallMountedBox):
    """Outset and angled plate to mount stuff to"""

    def __init__(self):
        super().__init__()

        self.argparser.add_argument(
            "--pins",  action="store", type=int, default=8,
            help="number of pins")
        self.argparser.add_argument(
            "--pinlength",  action="store", type=float, default=35,
            help="length of pins (in mm)")
        self.argparser.add_argument(
            "--pinwidth",  action="store", type=float, default=10,
            help="width of pins (in mm)")
        self.argparser.add_argument(
            "--pinspacing",  action="store", type=float, default=35,
            help="space from middle to middle of pins (in mm)")
        self.argparser.add_argument(
            "--pinspacing_increment",  action="store", type=float, default=0.0,
            help="increase spacing from left to right (in mm)")
        self.argparser.add_argument(
            "--angle",  action="store", type=float, default=20.0,
            help="angle of the pins pointing up (in degrees)")

        self.argparser.add_argument(
            "--hooks",  action="store", type=int, default=3,
            help="number of hooks into the wall")
        self.argparser.add_argument(
            "--h",  action="store", type=float, default=50.0,
            help="height of the front plate (in mm) - needs to be at least 7 time the thickness")
        
    def frontCB(self):
        s = self.pinspacing
        inc = self.pinspacing_increment
        t = self.thickness

        pos = s/2
        s += 0.5*inc
        for i in range(self.pins):
            self.rectangularHole(pos, 2*t, self.pinwidth, t)
            pos += s
            s+=inc

        for i in range(1, self.hooks-1):
            self.fingerHolesAt(i*self.x/(self.hooks-1), self.h/2, self.h/2)

            
    def backCB(self):
        t = self.thickness
        self.fingerHolesAt(0, 2*t, self.x, 0)
        if self.angle < 0.001:
            return
        for i in range(1, self.hooks-1):
            self.fingerHolesAt(i*self.x/(self.hooks-1), 3*t, self.h/2-3*t)

    def sideWall(self, move=None):
        a = self.angle
        ar = math.radians(a)
        h = self.h
        t = self.thickness

        sh = math.sin(ar)*6*t + math.cos(ar)*h
        
        tw = self.edges["a"].margin() + math.sin(ar)*h + math.cos(ar)*6*t
        th = sh + 6
        if self.move(tw, th, move, True):
            return

        self.moveTo(self.edges["a"].margin())
        
        self.polyline(math.sin(ar)*h, a, 4*t)
        self.fingerHolesAt(-3.5*t, 0, h/2, 90)
        self.edgeCorner("e", "h")
        self.edges["h"](h)
        self.polyline(0, 90-a, math.cos(ar)*6*t, 90)
        self.edges["a"](sh)
        self.corner(90)
        
        self.move(tw, th, move)

        
    def supportWall(self, move=None):
        a = self.angle
        ar = math.radians(a)
        h = self.h
        t = self.thickness

        sh = math.sin(ar)*6*t + math.cos(ar)*h
        
        tw = self.edges["a"].margin() + max(
            math.sin(ar)*h/2 + math.cos(ar)*5*t,
            math.sin(ar)*h)
        th = sh + 6
        if self.move(tw, th, move, True):
            return

        self.moveTo(self.edges["a"].margin())

        if a > 0.001:
            self.polyline(math.sin(ar)*h, a+90, 3*t)
            self.edges["f"](h/2-3*t)
            self.polyline(0, -90)
        self.polyline(4*t, 90)
        self.edges["f"](h/2)
        self.polyline(math.sin(ar)*2*t, 90-a,
                      math.cos(ar)*4*t - math.sin(ar)**2*2*t, 90)
        if a > 0.001:
            self.edges["a"](sh)
        else:
            self.edges["a"](h/2)
        self.corner(90)
        
        self.move(tw, th, move)
        
            
    def render(self):
        self.generateWallEdges()

        p = PinEdge(self, self)
        n = self.pins
        t = self.thickness

        if self.h < 7*t:
            self.h = 7*t

        self.x = x = n*self.pinspacing + (n)*(n-1)/2 *self.pinspacing_increment


        self.rectangularWall(x, 3*t, [p, "e", "f", "e"], move="up")
        self.rectangularWall(x, self.h, "efef", callback=[self.frontCB],
                             move="up")
        self.rectangularWall(x, self.h/2, "efef", callback=[self.backCB],
                             move="up")
        self.sideWall(move="right")
        for i in range(self.hooks-2):
            self.supportWall(move="right")
        self.sideWall(move="right")
