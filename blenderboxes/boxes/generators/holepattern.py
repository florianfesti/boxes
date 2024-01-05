# Copyright (C) 2013-2022 Florian Festi
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


class HolePattern(Boxes):
    """Generate hole patterns in different simple shapes"""

    ui_group = "Holes"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(fillHolesSettings, fill_pattern="hex")

        self.buildArgParser("x", "y")
        self.argparser.add_argument(
            "--shape",  action="store", type=str, default="rectangle",
            choices=["rectangle", "ellipse", "oval", "hexagon", "octagon"],
            help="Shape of the hole pattern")

    def render(self):
        x, y = self.x, self.y

        if self.shape == "ellipse":
            border = [(x * (.5+math.sin(math.radians(a))/2),
                       y * (.5+math.cos(math.radians(a))/2))
                      for a in range(0, 360, 18)]
        elif self.shape == "oval":
            r = min(x, y) / 2
            dx = max(x-y, 0)
            dy = max(y-x, 0)
            border = [(r * (.5+math.cos(math.radians(a))/2) +
                       (dx if q in [0, 3] else 0),
                       r * (.5+math.sin(math.radians(a))/2) +
                       (dy if q in [1, 2] else 0))
                      for q in range(4)
                      for a in range(90*q, 90*q+91, 18)]
        elif self.shape == "hexagon":
            dx = min(y / (3**.5) / 2, x / 2)
            border = [(dx, 0), (x-dx, 0), (x, .5*y),
                      (x-dx, y), (dx, y), (0, .5*y)]
        elif self.shape == "octagon":
            d = (2**.5/(2+2*2**.5))
            d2 = 1 -d
            border = [(d*x, 0), (d2*x, 0), (x, d*y), (x, d2*y),
                      (d2*x, y), (d*x, y), (0, d2*y), (0, d*y)]
        else: # "rectangle"
            border = [(0, 0), (x, 0), (x, y), (0, y)]
    
        self.fillHoles(
            pattern=self.fillHoles_fill_pattern,
            border=border,
            max_radius=self.fillHoles_hole_max_radius,
            hspace=self.fillHoles_space_between_holes,
            bspace=self.fillHoles_space_to_border,
            min_radius=self.fillHoles_hole_min_radius,
            style=self.fillHoles_hole_style,
            bar_length=self.fillHoles_bar_length,
            max_random=self.fillHoles_max_random
            )
