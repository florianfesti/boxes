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

    def __init__(self) -> None:
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

    def flexBoxSide(self, y, h, r, callback=None, move=None):
        t = self.thickness

        if self.move(y+2*t, h+t, move, True):
            return

        self.moveTo(t, t)

        self.cc(callback, 0)
        self.edges["f"](y)
        self.corner(90, 0)
        self.cc(callback, 1)
        self.edges["f"](h - r)
        self.corner(90, r)
        self.cc(callback, 2)
        self.edge(y - 2 * r)
        self.corner(90, r)
        self.cc(callback, 3)
        self.edges["e"](h - r - self.latchsize)
        self.cc(callback, 4)
        self.latch(self.latchsize)
        self.corner(90)

        self.move(y+2*t, h+t, move)

    def surroundingWall(self, move=None):
        x, y, h, r = self.x, self.y, self.h, self.radius
        c4 = self.c4

        t = self.thickness

        tw, th = 2*c4 + 2*h + y - 4*r + 2*t, x + 2.5*t

        if self.move(tw, th, move, True):
            return

        self.moveTo(t, 0.25*t)

        self.edges["F"](h - r, False)
        if (y - 2 * r < self.thickness):
            self.edges["X"](2 * c4 + y - 2 * r, x + 2 * self.thickness)
        else:
            self.edges["X"](c4, x + 2 * self.thickness)
            self.edge(y - 2 * r)
            self.edges["X"](c4, x + 2 * self.thickness)

        self.edge(h - r - self.latchsize)
        self.latch(self.latchsize, False, extra_length=t)
        self.edge(x + 2 * self.thickness)
        self.latch(self.latchsize, False, True, extra_length=t)
        self.edge(h - r - self.latchsize)
        self.edge(c4)
        self.edge(y - 2 * r)
        self.edge(c4)
        self.edges["F"](h - r)
        self.corner(90)
        self.edge(self.thickness)
        self.edges["f"](x)
        self.edge(self.thickness)
        self.corner(90)

        self.move(tw, th, move)

    def render(self):
        if self.outside:
            self.x = self.adjustSize(self.x)
            self.y = self.adjustSize(self.y)
            self.h = self.adjustSize(self.h)

        self.latchsize *= self.thickness
        self.radius = self.radius or min(self.y / 2.0, self.h - self.latchsize)
        self.radius = min(self.radius, self.y / 2.0)
        self.radius = min(self.radius, max(0, self.h - self.latchsize))
        self.c4 = c4 = math.pi * self.radius * 0.5


        self.surroundingWall(move="up")
        self.flexBoxSide(self.y, self.h, self.radius, move="right")
        self.flexBoxSide(self.y, self.h, self.radius, move="mirror right")
        self.rectangularWall(self.y, self.x, edges="FeFF")
