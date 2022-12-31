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

import math

import boxes


class DoubleFlexDoorBox(boxes.Boxes):
    """Box with two part lid with living hinges and round corners"""

    ui_group = "FlexBox"

    def __init__(self):
        boxes.Boxes.__init__(self)
        self.addSettingsArgs(boxes.edges.FingerJointSettings)
        self.addSettingsArgs(boxes.edges.FlexSettings)
        self.buildArgParser("x", "y", "h", "outside")
        self.argparser.add_argument(
            "--radius", action="store", type=float, default=15,
            help="Radius of the latch in mm")
        self.argparser.add_argument(
            "--latchsize", action="store", type=float, default=8,
            help="size of latch in multiples of thickness")

    def flexBoxSide(self, x, y, r, callback=None, move=None):
        t = self.thickness
        ll = (x - 2*r) / 2 - self.latchsize

        if self.move(x+2*t, y+2*t, move, True):
            return

        self.moveTo(t+r, t)

        for i, l in zip(range(2), (x, y)):
            self.cc(callback, i)
            self.edges["f"](l - 2 * r)
            self.corner(90, r)

        self.cc(callback, 2)
        self.edge(ll)
        self.latch(self.latchsize)
        self.latch(self.latchsize, reverse=True)
        self.edge(ll)
        
        self.corner(90, r)
        self.cc(callback, 3)
        self.edges["f"](y - 2 * r)
        self.corner(90, r)

        self.move(x+2*t, y+2*t, move)

    def surroundingWall(self, x, y, h, r, move=None):
        t = self.thickness
        c4 = math.pi * r * 0.5

        tw = 2*x + 2*y - 8*r + 4*c4
        th = h + 2.5*t

        if self.move(tw, th, move, True):
            return

        self.moveTo(0, 0.25*t, -90)

        self.latch(self.latchsize, False, True)
        self.edge((x-2*r)/2 - self.latchsize, False)
        if y - 2 * r < t:
            self.edges["X"](2 * c4 + y - 2 * r, h + 2 * t)
        else:
            self.edges["X"](c4, h + 2 * t)
            self.edges["F"](y - 2 * r, False)
            self.edges["X"](c4, h + 2 * t)
        self.edges["F"](x - 2 * r, False)
        if y - 2 * r < t:
            self.edges["X"](2 * c4 + y - 2 * r, h + 2 * t)
        else:
            self.edges["X"](c4, h + 2 * t)
            self.edges["F"](y - 2 * r)
            self.edges["X"](c4, h + 2 * t)
        self.edge((x-2*r)/2 - self.latchsize, False)
        self.latch(self.latchsize, False)
        self.edge(h + 2 * t)
        self.latch(self.latchsize, False, True)
        self.edge((x-2*r)/2 - self.latchsize, False)
        self.edge(c4)
        self.edges["F"](y - 2 * r)
        self.edge(c4)
        self.edges["F"](x - 2 * r, False)
        self.edge(c4)
        self.edges["F"](y - 2 * r, False)
        self.edge(c4)
        self.edge((x-2*r)/2 - self.latchsize)
        self.latch(self.latchsize, False, False)
        self.edge(h + 2 * t)

        self.move(tw, th, move)

    def render(self):

        if self.outside:
            self.x = self.adjustSize(self.x)
            self.y = self.adjustSize(self.y)
            self.h = self.adjustSize(self.h)

        t = self.thickness
        self.latchsize *= t
        x, y, h = self.x, self.y, self.h
        r = self.radius or min(x - 2*self.latchsize, y) / 2.0
        r = min(r, y / 2.0)
        self.radius = r = min(r, max(0, (x - 2*self.latchsize) / 2.0))


        # swap y and h for more consistent axis names
        self.surroundingWall(x, h, y, r, move="up")
        self.flexBoxSide(x, h, r, move="right")
        self.flexBoxSide(x, h, r, move="mirror")
