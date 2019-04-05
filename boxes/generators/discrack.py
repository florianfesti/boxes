#!/usr/bin/env python3
# Copyright (C) 2019 chrysn <chrysn@fsfe.org>
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
from math import sqrt

class DiscRack(Boxes):
    """A rack for storing disk-shaped objects vertically next to each other"""

    ui_group = "Shelf"

    def __init__(self):
        super().__init__()
        self.buildArgParser("sx")
        self.argparser.add_argument(
            "--disc-diameter", action="store", type=float, default=150.0,
            help="Disc diameter in mm")
        self.argparser.add_argument(
            "--disc-thickness", action="store", type=float, default=5.0,
            help="Thickness of the discs in mm")

        self.argparser.add_argument(
            "--lower-factor", action="store", type=float, default=0.75,
            help="Position of the lower rack grids along the radius")
        self.argparser.add_argument(
            "--rear-factor", action="store", type=float, default=0.75,
            help="Position of the rear rack grids along the radius")

        self.argparser.add_argument(
            "--disc-outset", action="store", type=float, default=3.0,
            help="Additional space kept between the disks and the outbox of the rack")
        self.argparser.add_argument(
            "--lower-outset", action="store", type=float, default=12.0,
            help="Space in front of the disk slits")
        self.argparser.add_argument(
            "--rear-outset", action="store", type=float, default=12.0,
            help="Space above the disk slits")

        self.argparser.add_argument(
            "--angle", action="store", type=float, default=18,
            help="Backwards slant of the rack")
        self.addSettingsArgs(edges.FingerJointSettings)

    def calculate(self):
        self.outer = self.disc_diameter + 2 * self.disc_outset

        r = self.disc_diameter / 2

        # front outset, space to radius, space to rear part, plus nothing as fingers extend out
        self.lower_size = self.lower_outset + \
                r * sqrt(1 - self.lower_factor**2) + \
                r * self.rear_factor

        self.rear_size = r * self.lower_factor + \
                r * sqrt(1 - self.rear_factor**2) + \
                self.rear_outset

        # still to be checked:
        # * is the inner junction outside the disks?
        # * is the outermost junction point (including the type-h outset) still inside the walls?
        # * does any of the outsets exceed the walls?

    def sidewall_holes(self):
        r = self.disc_diameter / 2

        self.moveTo(self.outer/2, self.outer/2, -self.angle)
        # can now move down to paint horizontal lower part, or right to paint
        # vertical rear part
        with self.saved_context():
            self.moveTo(
                    r * self.rear_factor,
                    -r * self.lower_factor - self.thickness/2,
                    90)
            self.fingerHolesAt(0, 0, self.lower_size)
        with self.saved_context():
            self.moveTo(
                    r * self.rear_factor + self.thickness/2,
                    -r * self.lower_factor,
                    0)
            self.fingerHolesAt(0, 0, self.rear_size)

        if self.debug:
            self.circle(0, 0, self.disc_diameter / 2)

    def _draw_slits(self, inset, halfslit):
        total_x = 0

        for x in self.sx:
            center_x = total_x + x / 2

            total_x += x
            self.rectangularHole(inset, center_x, 2 * halfslit, self.disc_thickness)
            if self.debug:
                self.ctx.rectangle(inset - halfslit, center_x - x/2, 2 * halfslit, x)

    def lower_holes(self):
        r = self.disc_diameter / 2
        halfslit = r * sqrt(1 - self.lower_factor**2)
        inset = self.lower_outset + halfslit

        self._draw_slits(inset, halfslit)

    def rear_holes(self):
        r = self.disc_diameter / 2
        halfslit = r * sqrt(1 - self.rear_factor**2)
        inset = r * self.lower_factor

        self._draw_slits(inset, halfslit)

    def render(self):
        self.calculate()

        o = self.outer

        self.rectangularWall(o, o, "eeee", move="right", callback=[self.sidewall_holes])
        self.rectangularWall(o, o, "eeee", move="right mirror", callback=[self.sidewall_holes])

        self.rectangularWall(self.lower_size, sum(self.sx), "fffe", move="right", callback=[self.lower_holes])
        self.rectangularWall(self.rear_size, sum(self.sx), "fefh", move="right", callback=[self.rear_holes])
