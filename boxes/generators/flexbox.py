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
        self.buildArgParser(sx="100", y=100.0, h=100.0, outside=True)
        self.argparser.add_argument(
            "--radius", action="store", type=float, default=15,
            help="Radius of the latch in mm")
        self.argparser.add_argument(
            "--latchsize", action="store", type=float, default=8,
            help="size of latch in multiples of thickness")

    def flexBoxSide(self, y, h, r, middle=False, callback=None, move=None):
        t = self.thickness

        if self.move(y+2*t, h+t, move, True):
            return

        self.moveTo(t+r, t)

        for i, l in zip(range(2), (y, h)):
            self.cc(callback, i)
            self.edges["f"](l - 2 * r)
            self.corner(90, r)

        self.cc(callback, 2)
        self.edge(y - 2 * r)
        self.corner(90, r)
        self.cc(callback, 3)
        if middle:
            self.edge(self.latchsize)
        else:
            self.latch(self.latchsize)
        self.cc(callback, 4)
        self.edges["f"](h - 2 * r - self.latchsize)
        self.corner(90, r)

        self.move(y+2*t, h+t, move)

    def _fingerHoles(self, l):
        t = self.thickness
        pos = -0.5*t
        for x in self.sx[:-1]:
            pos += x + t
            self.fingerHolesAt(0, pos, l, 0)

    def surroundingWall(self, move=None):
        x, y, h, r = self.x, self.y, self.h, self.radius
        t = self.thickness
        c4 = math.pi * r * 0.5

        tw = 2*y + 2*h - 8*r + 4*c4
        th = x + 2.5*t

        if self.move(tw, th, move, True):
            return

        self.moveTo(0, 0.25*t)

        self._fingerHoles(h - 2 * r - self.latchsize)
        self.edges["F"](h - 2 * r - self.latchsize, False)
        if y - 2 * r < t:
            self.edges["X"](2 * c4 + y - 2 * r, x + 2 * t)
        else:
            self.edges["X"](c4, x + 2 * t)
            self._fingerHoles(y - 2 * r)
            self.edges["F"](y - 2 * r, False)
            self.edges["X"](c4, x + 2 * t)
        self._fingerHoles(h - 2 * r)
        self.edges["F"](h - 2 * r, False)
        if y - 2 * r < t:
            self.edges["X"](2 * c4 + y - 2 * r, x + 2 * t)
        else:
            self.edges["X"](c4, x + 2 * t)
            self.edge(y - 2 * r)
            self.edges["X"](c4, x + 2 * t)
        self.latch(self.latchsize, False)
        self.edge(x + 2 * t)
        self.latch(self.latchsize, False, True)
        self.edge(c4)
        self.edge(y - 2 * r)
        self.edge(c4)
        self.edges["F"](h - 2 * r, False)
        self.edge(c4)
        self.edges["F"](y - 2 * r, False)
        self.edge(c4)
        self.edges["F"](h - 2 * r - self.latchsize, False)
        self.corner(90)
        self.edge(x + 2 * t)
        self.corner(90)

        self.move(tw, th, move)

    def render(self):

        if self.outside:
            self.sx = self.adjustSize(self.sx)
            self.y = self.adjustSize(self.y)
            self.h = self.adjustSize(self.h)

        sx, y, h = self.sx, self.y, self.h
        x = self.x = sum(sx) + (len(sx)-1) * self.thickness

        self.latchsize *= self.thickness
        r = self.radius or min(y, h - self.latchsize) / 2.0
        r = min(r, y / 2.0)
        self.radius = r = min(r, max(0, (h - self.latchsize) / 2.0))


        self.surroundingWall(move="up")
        for i in range(len(sx)):
            self.flexBoxSide(self.y, self.h, self.radius, middle=i>0, move="right")
        self.flexBoxSide(self.y, self.h, self.radius, move="mirror")
