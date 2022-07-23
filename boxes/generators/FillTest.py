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
from shapely.geometry import *
import random
import time

class FillTest(Boxes): # Change class name!
    """Piece for testing different settings for hole filling"""

    ui_group = "Part"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(fillHolesSettings, fill_pattern="hex")

        self.buildArgParser()


    def xHoles(self):
        border = [(5, 10), (245, 10), (225, 150), (235, 150), (255, 10), (290, 10), (270, 190), (45, 190), (45, 50), (35, 50), (35, 190), (5, 190)]
               
        self.showBorderPoly(border)
        self.text("Area to be filled", 150, 190, align="bottom center", color=Color.ANNOTATIONS)

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
        self.rectangularWall(320,220,"eeee",callback=[self.xHoles, None, None, None],)


