# Copyright (C) 2024 Oliver Jensen
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


class FlexBook(Boxes):
    """Box with living hinge styled after a book."""

    ui_group = "FlexBox"

    description = """
If you have an enclosure, arrange the living hinge to be as close to your extractor fan as possible.

![Open](static/samples/FlexBook-2.jpg)"""

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.FlexSettings)
        self.buildArgParser(x=75.0, y=35.0, h=125.0)
        self.argparser.add_argument(
            "--latchsize", action="store", type=float, default=8,
            help="size of latch in multiples of thickness")
        self.argparser.add_argument(
            "--recess_wall", action="store", type=boolarg, default=False,
            help="Whether to recess the inner wall for easier object removal")


    def flexBookSide(self, h, x, r, callback=None, move=None):
        t = self.thickness

        tw, th = h+t, x+2*t+r
        if self.move(tw, th, move, True):
            return

        self.fingerHolesAt(0, x+1.5*t, h, 0)

        self.edges["F"](h)
        self.corner(90, 0)
        self.edges["e"](t)
        self.edges["f"](x + t)
        self.corner(180, r)
        self.edges["e"](x + 2*t)
        self.corner(90)

        self.move(tw, th, move)


    def flexBookRecessedWall(self, h, y, include_recess, callback=None, move=None):
        t = self.thickness

        tw, th = h, y+2*t

        if self.move(tw, th, move, True):
            return

        # TODO: figure out math for gentler angles
        cutout_radius = min(h/4, y/8)
        cutout_angle = 90
        cutout_predist = y * 0.2
        cutout_angle_dist = h/2 - 2 * cutout_radius
        cutout_base_dist = y - (y * .4) - 4 * cutout_radius

        self.moveTo(0, t)

        self.edges["f"](h)
        self.corner(90,)
        self.edges["e"](y)
        self.corner(90)
        self.edges["f"](h)
        self.corner(90)
        if include_recess:
            self.polyline(
                cutout_predist,
                (cutout_angle, cutout_radius),
                cutout_angle_dist,
                (-cutout_angle, cutout_radius),
                cutout_base_dist,
                (-cutout_angle, cutout_radius),
                cutout_angle_dist,
                (cutout_angle, cutout_radius),
                cutout_predist)
        else :
            self.edges["e"](y)
        self.corner(90)

        self.move(tw, th, move)


    def flexBookLatchWall(self, h, y, latchSize, callback=None, move=None):
        t = self.thickness

        if self.recess_wall:
            x_adjust = 0
        else:
            x_adjust = 3 * t

        tw, th = h+t+x_adjust, y+2*t

        if self.move(tw, th, move, True):
            return

        self.moveTo(x_adjust, t)

        self.edges["f"](h)
        self.corner(90)
        self.edges["f"](y)
        self.corner(90)
        self.edges["f"](h)
        self.corner(90)

        self.rectangularHole(y/2, -1.5*t, latchSize - 2*t, t)

        self.polyline(
            (y-latchSize) / 2,
            -90,
            2.5*t,
            (90, t/2),
            latchSize - t,
            (90, t/2),
            2.5*t,
            -90,
            (y-latchSize) / 2,
            90
        )

        self.move(tw, th, move)

    def flexBookCover(self, move=None):
        x, y = self.x, self.y
        latchSize = self.latchsize
        c4 = self.c4
        t = self.thickness

        tw = 2*x + 6*t + 2*c4 + t
        th = y + 4*t

        if self.move(tw, th, move, True):
            return

        self.moveTo(2*t, 0)

        self.edges["h"](x+t)
        self.edges["X"](2*c4 + t, y + 4*t) # extra thickness here to make it fit
        self.edges["e"](x+t)
        self.corner(90, 2*t)
        self.edges["e"](y/2)

        self.rectangularHole(0, 1.5*t, latchSize, t)
        self.rectangularHole((latchSize+7*t)/2, 3.5*t, t, t)
        self.rectangularHole(-(latchSize+7*t)/2, 3.5*t, t, t)

        self.edges["e"](y/2)
        self.corner(90, 2*t)
        self.edges["e"](x+t + 2*c4 + t) # corresponding extra thickness
        self.edges["h"](x+t)
        self.corner(90, 2*t)
        self.edges["h"](y)
        self.corner(90, 2*t)

        if False:
            # debug lines
            self.moveTo(0, 2*t)
            self.edges["e"](x+t + 2*c4 + x+t + t)
            self.corner(90)
            self.edges["e"](y)
            self.corner(90)
            self.edges["e"](x+t + 2*c4 + x+t + t)
            self.corner(90)
            self.edges["e"](y)
            self.corner(90)

            self.edges["e"](x)
            self.corner(90)
            self.edges["e"](y)
            self.corner(90)
            self.edges["e"](x)
            self.corner(90)
            self.edges["e"](y)
            self.corner(90)

        self.move(tw, th, move)

    def flexBookLatchBracket(self, isCover, move=None):
        t = self.thickness
        round = t/3

        tw, th = 5*t, 5.5*t
        if self.move(tw, th, move, True):
            return

        if isCover:
            self.edge(5*t)
        else:
            self.edge(t)
            self.corner(90)
            self.edge(2*t - round)
            self.corner(-90, round)
            self.edge(1.5*t - round)
            self.rectangularHole(0, 1.5 * t, t, t)
            self.edge(1.5*t - round)
            self.corner(-90, round)
            self.edge(2*t - round)
            self.corner(90)
            self.edge(t)

        self.corner(90)
        self.edge(3*t)
        self.corner(180, 2.5 * t)
        self.edge(3*t)

        if not isCover:
            # anchor pin
            self.moveTo(-1.5*t, 1.25*t)
            self.ctx.stroke()
            self.rectangularWall(t, 2*t)

        self.move(tw, th, move)

    def flexBookLatchPin(self, move=None):
        t = self.thickness
        l = self.latchsize

        tw, th = l + 4*t, 5*t

        if self.move(tw, th, move, True):
            return

        round = t/3

        self.moveTo(2*t, 0)

        self.polyline(
            l,
            90,
            2*t,
            -90,
            2*t - round,
            (90, round),
            2*t - 2*round,
            (90, round),
            3*t - round,
            -90,
            t - round,
            (90, round),
            l - 2*t - 2*round,
            (90, round),
            t - round,
            -90,
            3*t - round,
            (90, round),
            2*t - 2*round,
            (90, round),
            2*t - round,
            -90,
            2*t,
            90)
        self.move(tw, th, move)




    def render(self):

        # I found it easier to conceptualize swapping y and h
        y = self.h
        self.h = self.y
        self.y = y
        t = self.thickness

        self.radius = self.h / 2
        self.c4 = c4 = math.pi * self.radius * 0.5

        self.latchsize *= self.thickness

        self.flexBookCover(move="up")
        self.flexBookRecessedWall(self.h, self.y, self.recess_wall, move="mirror right")
        self.flexBookLatchWall(self.h, self.y, self.latchsize, move="right")

        with self.saved_context():
            self.flexBookSide(self.h, self.x, self.radius, move="right")
            self.flexBookSide(self.h, self.x, self.radius, move="mirror right")
        self.flexBookSide(self.h, self.x, self.radius, move="up only")

        with self.saved_context():
            self.flexBookLatchBracket(False, move="up")
            self.flexBookLatchBracket(False, move="up")
        self.flexBookLatchBracket(False, move="right only")

        with self.saved_context():
            self.flexBookLatchBracket(True, move="up")
            self.flexBookLatchBracket(True, move="up")
        self.flexBookLatchBracket(False, move="right only")

        l = self.latchsize
        self.rectangularWall(
            4*t, l,
            callback=[lambda: self.rectangularHole(2*t, l/2, 2.5*t, .8*l, r=2*t)],
            move="right")
        self.flexBookLatchPin(move="right")
