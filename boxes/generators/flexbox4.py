#!/usr/bin/env python3
# Copyright (C) 2013-2018 Florian Festi
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


class FlexBox4(Boxes):
    """Box with living hinge and left corners rounded"""

    ui_group = "FlexBox"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.FlexSettings)
        self.buildArgParser("x", "y", "h", "outside")
        self.argparser.add_argument(
            "--radius", action="store", type=float, default=15,
            help="Radius of the corners in mm")
        self.argparser.add_argument(
            "--latchsize", action="store", type=float, default=8,
            help="size of latch in multiples of thickness")

    def flexBoxSide(self, x, y, r, callback=None, move=None):
        t = self.thickness

        if self.move(x+2*t, y+t, move, True):
            return

        self.moveTo(t, t)

        self.cc(callback, 0)
        self.edges["f"](x)
        self.corner(90, 0)
        self.cc(callback, 1)
        self.edges["f"](y - r)
        self.corner(90, r)
        self.cc(callback, 2)
        self.edge(x - 2 * r)
        self.corner(90, r)
        self.cc(callback, 3)
        self.edges["e"](y - r - self.latchsize)
        self.cc(callback, 4)
        self.latch(self.latchsize)
        self.corner(90)

        self.move(x+2*t, y+t, move)

    def surroundingWall(self, move=None):
        x, y, h, r = self.x, self.y, self.h, self.radius
        c4 = self.c4

        t = self.thickness

        tw, th = 2*c4 + 2*y + x - 4*r + 2*t, h + 2.5*t

        if self.move(tw, th, move, True):
            return

        self.moveTo(t, 0.25*t)

        self.edges["F"](y - r, False)
        if (x - 2 * r < self.thickness):
            self.edges["X"](2 * c4 + x - 2 * r, h + 2 * self.thickness)
        else:
            self.edges["X"](c4, h + 2 * self.thickness)
            self.edge(x - 2 * r)
            self.edges["X"](c4, h + 2 * self.thickness)

        self.edge(y - r - self.latchsize)
        self.latch(self.latchsize+t, False)
        self.edge(h + 2 * self.thickness)
        self.latch(self.latchsize+t, False, True)
        self.edge(y - r - self.latchsize)
        self.edge(c4)
        self.edge(x - 2 * r)
        self.edge(c4)
        self.edges["F"](y - r)
        self.corner(90)
        self.edge(self.thickness)
        self.edges["f"](h)
        self.edge(self.thickness)
        self.corner(90)

        self.move(tw, th, move)

    def render(self):
        if self.outside:
            self.x = self.adjustSize(self.x)
            self.y = self.adjustSize(self.y)
            self.h = self.adjustSize(self.h)

        self.latchsize *= self.thickness
        self.radius = self.radius or min(self.x / 2.0, self.y - self.latchsize)
        self.radius = min(self.radius, self.x / 2.0)
        self.radius = min(self.radius, max(0, self.y - self.latchsize))
        self.c4 = c4 = math.pi * self.radius * 0.5


        self.surroundingWall(move="up")
        self.flexBoxSide(self.x, self.y, self.radius, move="right")
        self.flexBoxSide(self.x, self.y, self.radius, move="mirror right")
        self.rectangularWall(self.x, self.h, edges="FeFF")



