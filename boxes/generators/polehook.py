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

class PoleHook(Boxes): # change class name here and below
    """Hook for pole like things to be clamped to another pole"""
    
    def __init__(self):
        Boxes.__init__(self)

        # Uncomment the settings for the edge types you use
        self.addSettingsArgs(edges.FingerJointSettings)

        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--diameter",  action="store", type=float, default=50.,
            help="diameter of the thing to hook")
        self.argparser.add_argument(
            "--screw",  action="store", type=float, default=7.8,
            help="diameter of the screw in mm")
        self.argparser.add_argument(
            "--screwhead",  action="store", type=float, default=13.,
            help="with of the screw head in mm")
        self.argparser.add_argument(
            "--screwheadheight",  action="store", type=float, default=5.5,
            help="height of the screw head in mm")
        self.argparser.add_argument(
            "--pin",  action="store", type=float, default=4.,
            help="diameter of the pin in mm")

    def fork(self, d, w, edge="e", full=True, move=None):
        tw = d + 2 * w
        th = 2 * d

        if self.move(tw, th, move, True):
            return

        e = self.edges.get(edge, edge)

        
        self.moveTo(0, e.margin())

        if e is self.edges["e"]:
            self.bedBoltHole(tw)
        else:
            e(tw, bedBolts=edges.Bolts(1))
        if full:
            self.hole(-0.5*w, 2*d, self.pin/2)
            self.polyline(0, 90, 2*d, (180, w/2), d, (-180, d/2),
                          0.5*d, (180, w/2), 1.5 * d, 90)
        else:
            self.polyline(0, 90, d, 90, w, 90, 0, (-180, d/2),
                          0.5*d, (180, w/2), 1.5 * d, 90)
            
        self.move(tw, th, move)

    def lock(self, l1, l2, w, move=None):
        l1 += w/2
        l2 += w/2
        if self.move(l1, l2, move, True):
            return
        self.hole(w/2, w/2, self.pin/2)
        self.moveTo(w/2, 0)
        self.polyline(l2-w, (180, w/2), l2-2*w, (-90, w/2), l1-2*w, (180, w/2),
                      l1-w, (90, w/2))
        self.move(l1, l2, move)

    def backplate(self):
        tw = self.diameter + 2*self.ww
        t = self.thickness
        b = edges.Bolts(1)
        bs = (0.0, )
        self.fingerHolesAt(-tw/2, -2*t, tw, 0, bedBolts=b, bedBoltSettings=bs)
        self.fingerHolesAt(-tw/2, 0, tw, 0, bedBolts=b, bedBoltSettings=bs)
        self.fingerHolesAt(-tw/2, +2*t, tw, 0, bedBolts=b, bedBoltSettings=bs)

    def clamp(self):
        d = self.diameter + 2 * self.ww
        self.moveTo(10, -0.5*d, 90)
        self.edge(d)
        self.moveTo(0, -8, -180)
        self.edge(d)

    def render(self):
        # adjust to the variables you want in the local scope
        d = self.diameter
        t = self.thickness

        shh = self.screwheadheight
        self.bedBoltSettings = (self.screw, self.screwhead, shh, d/4+shh, d/4)  # d, d_nut, h_nut, l, l
        self.ww = ww = 4*t
        self.fork(d, ww, "f", move="right")
        self.fork(d, ww, "f", move="right")
        self.fork(d, ww, "f", full=False, move="right")
        self.fork(d, ww, full=False, move="right")
        self.fork(d, ww, full=False, move="right")

        self.parts.disc(d+2*ww, callback=self.backplate, hole=self.screw, move="right")
        self.parts.disc(d+2*ww, hole=self.screw, move="right")
        self.parts.disc(d+2*ww, callback=self.clamp, hole=self.screw+0.5*t, move="right")
        self.parts.disc(d+2*ww, hole=self.screw+0.5*t, move="right")
        self.parts.waivyKnob(50, callback=lambda:self.nutHole(self.screwhead),
                             move="right")
        self.parts.waivyKnob(50, callback=lambda:self.nutHole(self.screwhead),
                             move="right")
        self.parts.waivyKnob(50, hole=self.screw+0.5*t, move="right")

        ll = ((d**2 + (0.5*(d+ww))**2)**0.5) - 0.5 * d
        for i in range(3):
            self.lock(ll, ll, ww, move="right")

        for i in range(2):
            self.parts.disc(ww, move="up")
            

