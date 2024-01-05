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
from boxes import pulley


class Pulley(Boxes):
    """Timing belt pulleys for different profiles"""

    ui_group = "Part"

    def __init__(self) -> None:
        Boxes.__init__(self)
        # remove cli params you do not need
        self.buildArgParser(h=6.)
        self.argparser.add_argument(
            "--profile", action="store", type=str, default="GT2_2mm",
            choices=pulley.Pulley.getProfiles(),
            help="profile of the teeth/belt")
        self.argparser.add_argument(
            "--teeth", action="store", type=int, default=20,
            help="number of teeth")
        self.argparser.add_argument(
            "--axle", action="store", type=float, default=5,
            help="diameter of the axle")
        self.argparser.add_argument(
            "--insideout", action="store", type=BoolArg(), default=False,
            help="create a ring gear with the belt being pushed against from within")
        self.argparser.add_argument(
            "--top", action="store", type=float, default=0,
            help="overlap of top rim (zero for none)")

        # Add non default cli params if needed (see argparse std lib)
        # self.argparser.add_argument(
        #    "--XX",  action="store", type=float, default=0.5,
        #    help="DESCRIPTION")

    def disk(self, diameter, hole, callback=None, move=""):
        w = diameter + 2 * self.spacing

        if self.move(w, w, move, before=True):
            return

        self.moveTo(w / 2, w / 2)
        self.cc(callback, None, 0.0, 0.0)

        if hole:
            self.hole(0, 0, hole / 2.0)

        self.moveTo(diameter / 2 + self.burn, 0, 90)
        self.corner(360, diameter / 2)
        self.move(w, w, move)

    def render(self):
        # adjust to the variables you want in the local scope
        t = self.thickness

        if self.top:
            self.disk(
                self.pulley.diameter(self.teeth, self.profile) + 2 * self.top,
                self.axle, move="right")

        for i in range(int(math.ceil(self.h / self.thickness))):
            self.pulley(self.teeth, self.profile, insideout=self.insideout, r_axle=self.axle / 2.0, move="right")



