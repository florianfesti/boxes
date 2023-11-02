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


class FlexBox5(boxes.Boxes):
    """Box with living hinge and round corners"""

    ui_group = "FlexBox"

    def __init__(self) -> None:
        boxes.Boxes.__init__(self)
        self.addSettingsArgs(boxes.edges.FingerJointSettings)
        self.addSettingsArgs(boxes.edges.FlexSettings)
        self.buildArgParser("x", "h", "outside")
        self.argparser.add_argument(
            "--top_diameter", action="store", type=float, default=60,
            help="diameter at the top")
        self.argparser.add_argument(
            "--bottom_diameter", action="store", type=float, default=60,
            help="diameter at the bottom")
        self.argparser.add_argument(
            "--latchsize", action="store", type=float, default=8,
            help="size of latch in multiples of thickness")

    def flexBoxSide(self, callback=None, move=None):
        t = self.thickness

        r1, r2 = self.top_diameter/2., self.bottom_diameter/2
        a = self.a
        l = self.l

        tw , th = l+r1+r2, 2*max(r1, r2)+2*t
        
        if self.move(tw, th, move, True):
            return

        self.moveTo(r2, t)

        self.cc(callback, 0)
        self.edges["f"](l)
        self.corner(180+2*a, r1)
        self.cc(callback, 1)
        self.latch(self.latchsize)
        self.cc(callback, 2)
        self.edges["f"](l - self.latchsize)
        self.corner(180-2*a, r2)

        self.move(tw, th, move)

    def surroundingWall(self, move=None):
        t = self.thickness

        r1, r2 = self.top_diameter/2., self.bottom_diameter/2
        h = self.h
        a = self.a
        l = self.l


        c1 = math.radians(180+2*a) * r1
        c2 = math.radians(180-2*a) * r2

        tw = 2*l + c1 + c2
        th = h + 2.5*t

        if self.move(tw, th, move, True):
            return

        self.moveTo(0, 0.25*t)

        self.edges["F"](l - self.latchsize, False)
        self.edges["X"](c2, h + 2 * t)
        self.edges["F"](l, False)
        self.edges["X"](c1, h + 2 * t)
        self.latch(self.latchsize, False)
        self.edge(h + 2 * t)
        self.latch(self.latchsize, False, True)
        self.edge(c1)
        self.edges["F"](l, False)
        self.edge(c2)
        self.edges["F"](l - self.latchsize, False)
        self.corner(90)
        self.edge(h + 2 * t)
        self.corner(90)

        self.move(tw, th, move)

    def render(self):

        if self.outside:
            self.x = self.adjustSize(self.x)
            self.h = self.adjustSize(self.h)
            self.top_diameter = self.adjustSize(self.top_diameter)
            self.bottom_diameter = self.adjustSize(self.bottom_diameter)
            
        t = self.thickness
        self.latchsize *= self.thickness
        d_t, d_b = self.top_diameter, self.bottom_diameter
        self.x = max(self.x, self.latchsize + 2*t + (d_t + d_b)/2)

        d_c = self.x - d_t/2. - d_b/2.
        self.a = math.degrees(math.asin((d_t-d_b)/2 / d_c))
        self.l = d_c * math.cos(math.radians(self.a))

        self.surroundingWall(move="up")
        self.flexBoxSide(move="right")
        self.flexBoxSide(move="mirror")
