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

    def __init__(self) -> None:
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
            "--min_diameter", action="store", type=float, default=24,
            help="inner diameter of bottle neck hole")
        self.argparser.add_argument(
            "--max_diameter", action="store", type=float, default=50,
            help="outer diameter of bottle neck hole")
        self.argparser.add_argument(
            "--radius", action="store", type=float, default=15,
            help="corner radius of bottom tag")
        self.argparser.add_argument(
            "--segment_width", action="store", type=int, default=3,
            help="inner segment width")

    def render(self):
        # adjust to the variables you want in the local scope
        width = self.width
        height = self.height
        r_min = self.min_diameter / 2
        r_max = self.max_diameter / 2
        r = self.radius
        segment_width = self.segment_width

        # tag outline
        self.moveTo(r)
        self.edge(width - r - r)
        self.corner(90, r)
        self.edge(height - width / 2.0 - r)
        self.corner(180, width / 2)
        self.edge(height - width / 2.0 - r)
        self.corner(90, r)

        # move to centre of hole and cut the inner circle
        self.moveTo(width / 2 - r, height - width / 2)
        with self.saved_context():
            self.moveTo(0, -r_min)
            self.corner(360, r_min)

        # draw the radial lines approx 2mm apart on r_min
        seg_angle = math.degrees(segment_width / r_min)
        # for neatness, we want an integral number of cuts
        num = math.floor(360 / seg_angle)
        for i in range(num):
            with self.saved_context():
                self.moveTo(0, 0, i * 360.0 / num)
                self.moveTo(r_min)
                self.edge(r_max - r_min)
                # Add some right angle components to reduce tearing
                with self.saved_context():
                    self.moveTo(0, 0, 90)
                    self.edge(0.5)
                with self.saved_context():
                    self.moveTo(0, 0, -90)
                    self.edge(0.5)

