# Copyright (C) 2021 Guillaume Collic
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

from boxes import Boxes, boolarg


class CoffeeCapsuleHolder(Boxes):
    """
    Coffee capsule holder
    """

    ui_group = "Misc"

    description = """
    You can store your coffee capsule near your espresso machine with this. It works both vertically, or upside down under a shelf.
"""

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.argparser.add_argument(
            "--columns",
            type=int,
            default=4,
            help="Number of columns of capsules.",
        )
        self.argparser.add_argument(
            "--rows",
            type=int,
            default=5,
            help="Number of capsules by columns.",
        )
        self.argparser.add_argument(
            "--backplate",
            type=boolarg,
            default=True,
            help="True if a backplate should be generated.",
        )

    def render(self):
        self.lid_size = 37
        self.lid_size_with_margin = 39
        self.body_size = 30
        self.column_spacing = 5
        self.corner_radius = 3
        self.screw_margin = 6
        self.outer_margin = 7
        # Add space for the opening. A full row is not necessary for it.
        self.rows = self.rows + 0.6

        self.render_plate(screw_hole=7, hole_renderer=self.render_front_hole)
        self.render_plate(hole_renderer=self.render_middle_hole)
        if self.backplate:
            self.render_plate()

    def render_plate(self, screw_hole=3.5, hole_renderer=None, move="right"):
        width = (
            self.columns * (self.lid_size_with_margin + self.column_spacing)
            - self.column_spacing
            + 2 * self.outer_margin
        )
        height = self.rows * self.lid_size + 2 * self.outer_margin

        if self.move(width, height, move, True):
            return

        with self.saved_context():
            self.moveTo(self.corner_radius)
            self.polyline(
                width - 2 * self.corner_radius,
                (90, self.corner_radius),
                height - 2 * self.corner_radius,
                (90, self.corner_radius),
                width - 2 * self.corner_radius,
                (90, self.corner_radius),
                height - 2 * self.corner_radius,
                (90, self.corner_radius),
            )

        if hole_renderer:
            for col in range(self.columns):
                with self.saved_context():
                    self.moveTo(
                        self.outer_margin + col * (self.lid_size_with_margin + self.column_spacing) - self.burn,
                        self.outer_margin + (self.rows - 0.5) * self.lid_size + self.burn,
                        -90,
                    )
                    hole_renderer()

        if screw_hole:
            for x in [self.screw_margin, width - self.screw_margin]:
                for y in [self.screw_margin, height - self.screw_margin]:
                    self.hole(x, y + self.burn, d=screw_hole)

        self.move(width, height, move)

    def render_front_hole(self):
        radians = math.acos(self.body_size / self.lid_size_with_margin)
        height_difference = (self.lid_size / 2) * math.sin(radians)
        degrees = math.degrees(radians)
        half = [
            0,
            (degrees, self.lid_size_with_margin / 2),
            0,
            -degrees,
            (self.rows - 1) * self.lid_size - height_difference,
        ]
        path = (
            half
            + [(180, self.body_size / 2)]
            + list(reversed(half))
            + [(180, self.lid_size_with_margin / 2)]
        )
        self.polyline(*path)

    def render_middle_hole(self):
        half = [(self.rows - 1) * self.lid_size, (180, self.lid_size_with_margin / 2)]
        path = half * 2
        self.polyline(*path)
