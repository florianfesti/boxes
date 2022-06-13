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
    """DESCRIPTION"""

    ui_group = "Unstable" # see ./__init__.py for names

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(fillHolesSettings, hole_max_radius=4, hole_min_radius=1, space_between_holes=3, space_to_border=2, maximum=1000)

        self.buildArgParser(x=100, y=100, h=100, hi=0)


    def xHoles(self):
        border = [(0, 0), (245, 0), (225, 150), (235, 150), (255, 0), (300, 0), (270, 200), (45, 200), (45, 50), (35, 50), (35, 200), (0, 200)]
        
        self.showBorderPoly(border)

        start_time = time.time()
        self.fillHoles(
            pattern=self.fillHoles_fill_pattern, 
            border=border, 
            max_radius=self.fillHoles_hole_max_radius, 
            hspace=self.fillHoles_space_between_holes, 
            bspace=self.fillHoles_space_to_border, 
            min_radius=self.fillHoles_hole_min_radius, 
            style=self.fillHoles_hole_style,
            maximum=self.fillHoles_maximum)
        end_time = time.time()

        print('fillHoles - Execution time:', (end_time-start_time)*1000, 'ms ', self.fillHoles_fill_pattern)        

    def render(self):
        self.rectangularWall(300,200,"eeee",callback=[self.xHoles, None, None, None],)


