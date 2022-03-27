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


class BottleTag(Boxes):
    """Paper slip over bottle tag"""

    ui_group = "Misc"  # see ./__init__.py for names

    def __init__(self):
        Boxes.__init__(self)

        self.buildArgParser()
        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--width", action="store", type=float, default=72,
            help="width of neck tag")
        self.argparser.add_argument(
            "--height", action="store", type=float, default=98,
            help="height of neck tag")
        self.argparser.add_argument(
            "--r1", action="store", type=float, default=12,
            help="inner radius of bottle neck hole")
        self.argparser.add_argument(
            "--r2", action="store", type=float, default=25,
            help="outer radius of bottle neck hole")
        self.argparser.add_argument(
            "--r3", action="store", type=float, default=15,
            help="corner radius of bottom tag")
        self.argparser.add_argument(
            "--segment_width", action="store", type=int, default=3,
            help="inner segment width")

    def render(self):
        # adjust to the variables you want in the local scope
        width = self.width
        height = self.height
        r1 = self.r1
        r2 = self.r2
        r3 = self.r3
        segment_width = self.segment_width

        # tag outline
        self.edge(width - r3 - r3)
        self.corner(90, r3)
        self.edge(height - width / 2.0 - r3)
        self.corner(180, width / 2)
        self.edge(height - width / 2.0 - r3)
        self.corner(90, r3)

        # move to centre of hole and cut the inner circle
        self.moveTo(width / 2 - r3, height - width / 2)
        with self.saved_context():
            self.moveTo(0, -r1)
            self.corner(360, r1)

        # draw the radial lines approx 2mm apart on r1
        seg_angle = math.degrees(segment_width / r1)
        # for neatness, we want an integral number of cuts
        num = math.floor(360 / seg_angle)
        for i in range(num):
            with self.saved_context():
                self.moveTo(0, 0, i * 360.0 / num)
                self.moveTo(r1)
                self.edge(r2 - r1)
                # Add some right angle components to reduce tearing
                with self.saved_context():
                    self.moveTo(0, 0, 90)
                    self.edge(0.5)
                with self.saved_context():
                    self.moveTo(0, 0, -90)
                    self.edge(0.5)

