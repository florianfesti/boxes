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

from boxes import *


class FlexBox2(Boxes):
    """Box with living hinge and top corners rounded"""

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
        self.latch(self.latchsize)
        self.cc(callback, 4)
        self.edges["f"](h - r - self.latchsize)
        self.corner(90)

        self.move(y+2*t, h+t, move)

    def surroundingWall(self, move=None):
        y, h, x, r = self.y, self.h, self.x, self.radius
        t = self.thickness

        tw = y + h - 3*r + 2*self.c4 + self.latchsize + t
        th = x + 2.5*t

        if self.move(tw, th, move, True):
            return

        self.moveTo(t, .25*t)
        self.edges["F"](h - r, False)

        if (y - 2 * r < t):
            self.edges["X"](2 * self.c4 + y - 2 * r, x + 2 * t)
        else:
            self.edges["X"](self.c4, x + 2 * t)
            self.edge(y - 2 * r)
            self.edges["X"](self.c4, x + 2 * t)

        self.latch(self.latchsize, False)
        self.edge(x + 2 * t)
        self.latch(self.latchsize, False, True)
        self.edge(self.c4)
        self.edge(y - 2 * r)
        self.edge(self.c4)
        self.edges["F"](h - r)
        self.corner(90)
        self.edge(t)
        self.edges["f"](x)
        self.edge(t)
        self.corner(90)

        self.move(tw, th, move)

    def render(self):

        if self.outside:
            self.y = self.adjustSize(self.y)
            self.h = self.adjustSize(self.h)
            self.x = self.adjustSize(self.x)

        self.latchsize *= self.thickness
        self.radius = self.radius or min(self.y / 2.0, self.h - self.latchsize)
        self.radius = min(self.radius, self.y / 2.0)
        self.radius = min(self.radius, max(0, self.h - self.latchsize))
        self.c4 = c4 = math.pi * self.radius * 0.5


        self.moveTo(2 * self.thickness, self.thickness)

        with self.saved_context():
            self.surroundingWall(move="right")
            self.rectangularWall(self.y, self.x, edges="FFFF")

        self.surroundingWall(move="up only")

        self.flexBoxSide(self.y, self.h, self.radius, move="right")
        self.flexBoxSide(self.y, self.h, self.radius, move= "mirror right")
        self.rectangularWall(self.x, self.h - self.radius - self.latchsize, edges="fFeF")


