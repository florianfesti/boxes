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

import time

from boxes import *


class FillTest(Boxes): # Change class name!
    """Piece for testing different settings for hole filling"""

    ui_group = "Part"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(fillHolesSettings, fill_pattern="hex")

        self.buildArgParser(x=320, y=220)


    def xHoles(self):
#        border = [(5, 10), (245, 10), (225, 150), (235, 150), (255, 10), (290, 10), (270, 190), (45, 190), (45, 50), (35, 50), (35, 190), (5, 190)]

        x, y = self.x, self.y

        border = [
            (  5/320*x,  10/220*y),
            (245/320*x,  10/220*y),
            (225/320*x, 150/220*y),
            (235/320*x, 150/220*y),
            (255/320*x,  10/220*y),
            (290/320*x,  10/220*y),
            (270/320*x, 190/220*y),
            ( 45/320*x, 190/220*y),
            ( 45/320*x,  50/220*y),
            ( 35/320*x,  50/220*y),
            ( 35/320*x, 190/220*y),
            (  5/320*x, 190/220*y),
            ]


        self.showBorderPoly(border)
        self.text("Area to be filled", x/2, 190/220*y, align="bottom center", color=Color.ANNOTATIONS)

        start_time = time.time()
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
        end_time = time.time()

#        print('fillHoles - Execution time:', (end_time-start_time)*1000, 'ms ', self.fillHoles_fill_pattern)

    def render(self):
        self.rectangularWall(self.x, self.y, "eeee", callback=[self.xHoles, None, None, None],)


