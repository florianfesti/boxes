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


class FlexBox(boxes.Boxes):
    """Box with living hinge and round corners"""

    ui_group = "FlexBox"

    def __init__(self) -> None:
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

        if self.move(x+2*t, y+t, move, True):
            return

        self.moveTo(t+r, t)

        for i, l in zip(range(2), (x, y)):
            self.cc(callback, i)
            self.edges["f"](l - 2 * r)
            self.corner(90, r)

        self.cc(callback, 2)
        self.edge(x - 2 * r)
        self.corner(90, r)
        self.cc(callback, 3)
        self.latch(self.latchsize)
        self.cc(callback, 4)
        self.edges["f"](y - 2 * r - self.latchsize)
        self.corner(90, r)

        self.move(x+2*t, y+t, move)

    def surroundingWall(self, move=None):
        x, y, h, r = self.x, self.y, self.h, self.radius
        t = self.thickness
        c4 = math.pi * r * 0.5

        tw = 2*x + 2*y - 8*r + 4*c4
        th = h + 2.5*t

        if self.move(tw, th, move, True):
            return

        self.moveTo(0, 0.25*t)

        self.edges["F"](y - 2 * r - self.latchsize, False)
        if x - 2 * r < t:
            self.edges["X"](2 * c4 + x - 2 * r, h + 2 * t)
        else:
            self.edges["X"](c4, h + 2 * t)
            self.edges["F"](x - 2 * r, False)
            self.edges["X"](c4, h + 2 * t)
        self.edges["F"](y - 2 * r, False)
        if x - 2 * r < t:
            self.edges["X"](2 * c4 + x - 2 * r, h + 2 * t)
        else:
            self.edges["X"](c4, h + 2 * t)
            self.edge(x - 2 * r)
            self.edges["X"](c4, h + 2 * t)
        self.latch(self.latchsize, False)
        self.edge(h + 2 * t)
        self.latch(self.latchsize, False, True)
        self.edge(c4)
        self.edge(x - 2 * r)
        self.edge(c4)
        self.edges["F"](y - 2 * r, False)
        self.edge(c4)
        self.edges["F"](x - 2 * r, False)
        self.edge(c4)
        self.edges["F"](y - 2 * r - self.latchsize, False)
        self.corner(90)
        self.edge(h + 2 * t)
        self.corner(90)

        self.move(tw, th, move)

    def render(self):

        if self.outside:
            self.x = self.adjustSize(self.x)
            self.y = self.adjustSize(self.y)
            self.h = self.adjustSize(self.h)

        x, y, h = self.x, self.y, self.h
        self.latchsize *= self.thickness
        r = self.radius or min(x, y - self.latchsize) / 2.0
        r = min(r, x / 2.0)
        self.radius = r = min(r, max(0, (y - self.latchsize) / 2.0))


        self.surroundingWall(move="up")
        self.flexBoxSide(self.x, self.y, self.radius, move="right")
        self.flexBoxSide(self.x, self.y, self.radius, move="mirror")



