# Copyright (C) 2023 fidoriel
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
from collections import OrderedDict
from typing import Tuple

from boxes import *


class BrickSorter(Boxes):
    """Stackable nestable sorting sieve for bricks"""

    description = """## Stackable nestable sorting sieve for bricks
A stackable sorting sieve for bricks, nestable for storage.
You will need to export all 5 levels, to get a full sieve.
If you feel you do not need the upper levels, just do not export them.
x,y,h are the dimensions for the largest sieve,
they will be the outer dimensions of the box,
the smaller sieves will be nested inside, therefore smaller.
Of course 256mm or 384mm (base plate size) are recommended values for x and y,
but you can use any value you like.

Full set of all 5 levels:
![Full Set](static/samples/BrickSorter-2.jpg)

![Full Set](static/samples/BrickSorter-3.jpg)

Stacked for Usage:
![Stacked](static/samples/BrickSorter-4.jpg)

Nested for Storage:
![Full Set](static/samples/BrickSorter-5.jpg)

In Use:
![Full Set](static/samples/BrickSorter-6.jpg)
"""

    ui_group = "Box"

    # level name, size of the holes in mm, and the thickness of the grid
    sieve_sizes = OrderedDict(
        (
            ("large_sieve", (30, 5)),
            ("medium_sieve", (20, 5)),
            ("small_sieve", (15, 4)),
            ("tiny_sieve", (10, 3)),
        )
    )

    bottom_edge: str = "h"
    level: str
    radius: int
    wiggle: float
    edge_width: int = 3

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings, edge_width=self.edge_width)
        self.buildArgParser(x=256, y=256, h=120)
        self.level_desc = list(self.sieve_sizes.keys()) + ["bottom"]
        self.argparser.add_argument(
            "--level",
            action="store",
            type=str,
            default="large_sieve",
            choices=self.level_desc,
            help="Level of the nestable sieve",
        )

        self.argparser.add_argument(
            "--radius",
            action="store",
            type=int,
            default=3,
            help="Radius of the corners of the sieve pattern in mm. Enter 30 for circular holes.",
        )

        self.argparser.add_argument(
            "--wiggle",
            action="store",
            type=float,
            default=4,
            help="Wiggle room, that the layers can slide in each other."
        )
        for action in self.argparser._actions:
            if action.dest in ["x", "y"]:
                action.help = "outer width of the most outer layer"

    @property
    def _sieve_grid_thickness(self) -> int:
        return self.sieve_sizes[self.level][1]

    @property
    def _sieve_level_index(self) -> int:
        """Return the index of the current sieve level, where 0 is the most outer sieve"""
        return self.level_desc.index(self.level)

    @property
    def _outer_height_after_nesting(self) -> float:
        return self.h - (((self.edge_width + 1) * self.thickness) * self._sieve_level_index) - (self._sieve_level_index * 2)

    def _xy_after_nesting(self, a: float) -> float:
        return a - ((2 * self.thickness + self.wiggle) * self._sieve_level_index)

    @property
    def _outer_x_after_nesting(self) -> float:
        return self._xy_after_nesting(self.x)

    @property
    def _outer_y_after_nesting(self) -> float:
        return self._xy_after_nesting(self.y)

    @property
    def _level_hole_size(self) -> float:
        return self.sieve_sizes[self.level][0]

    def _calc_hole_count(self, inner_mm_after_nesting: float) -> int:
        return int(
            (inner_mm_after_nesting - self._sieve_grid_thickness)
            / (self._level_hole_size + self._sieve_grid_thickness)
        )

    def _calc_grid_size_width_offset(
        self, inner_mm_after_nesting: float
    ) -> Tuple[int, float]:
        """Return the size of the grid and the offset from the outer top right corner"""
        hole_count = self._calc_hole_count(inner_mm_after_nesting)
        grid_size = (
            self._level_hole_size + self._sieve_grid_thickness
        ) * hole_count + self._sieve_grid_thickness
        offset = (inner_mm_after_nesting - grid_size) / 2
        return hole_count, offset

    def _draw_sieve(self, x: float, y: float) -> None:
        if self.level == "bottom":
            raise Exception("Cannot draw sieve pattern on bottom level")

        x_count, x_offset = self._calc_grid_size_width_offset(x)
        y_count, y_offset = self._calc_grid_size_width_offset(y)
        size = self._level_hole_size

        for relx in range(x_count):
            for rely in range(y_count):
                x_pos = (
                    x
                    - x_offset
                    - size
                    - relx * (size + self._sieve_grid_thickness)
                    - self._sieve_grid_thickness
                )
                y_pos = (
                    y
                    - y_offset
                    - size
                    - rely * (size + self._sieve_grid_thickness)
                    - self._sieve_grid_thickness
                )
                self.rectangularHole(
                    x=x_pos,
                    y=y_pos,
                    dx=size,
                    dy=size,
                    r=self.radius,
                    center_x=False,
                    center_y=False,
                )

    def render(self):
        # this is directly adapted from ABox.render
        x, y, h = (
            self._outer_x_after_nesting,
            self._outer_y_after_nesting,
            self._outer_height_after_nesting,
        )

        t1, t2, t3, t4 = "eeee"
        b = self.edges.get(self.bottom_edge, self.edges["F"])
        sideedge = "F"

        self.x = x = self.adjustSize(x, sideedge, sideedge)
        self.y = y = self.adjustSize(y)
        self.h = h = self.adjustSize(h, b, t1)

        with self.saved_context():
            self.rectangularWall(
                x, h, [b, sideedge, t1, sideedge], ignore_widths=[1, 6], move="up"
            )
            self.rectangularWall(
                x, h, [b, sideedge, t3, sideedge], ignore_widths=[1, 6], move="up"
            )

            if self.level == "bottom":
                callback = None
            else:
                callback = [lambda: self._draw_sieve(x, y)]
            self.rectangularWall(x, y, "ffff", move="up", callback=callback)

        self.rectangularWall(
            x, h, [b, sideedge, t3, sideedge], ignore_widths=[1, 6], move="right only"
        )
        self.rectangularWall(y, h, [b, "f", t2, "f"], ignore_widths=[1, 6], move="up")
        self.rectangularWall(y, h, [b, "f", t4, "f"], ignore_widths=[1, 6], move="up")
