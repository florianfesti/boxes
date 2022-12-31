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


class Display(Boxes):
    """Diplay for flyers or leaflets"""

    ui_group = "Misc"

    def __init__(self):
        Boxes.__init__(self)

        self.buildArgParser(x=150., h=200.0)
        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--radius",  action="store", type=float, default=5.,
            help="radius of the corners in mm")
        self.argparser.add_argument(
            "--angle",  action="store", type=float, default=0.,
            help="greater zero for top wider as bottom")


    def render(self):
        # adjust to the variables you want in the local scope
        x, h, r = self.x, self.h, self.radius
        a = self.angle
        t = self.thickness

        self.roundedPlate(0.7*x, x, r, "e", extend_corners=False, move="up")

        oh = 1.2*h-2*r
        if a > 0:
            self.moveTo(math.sin(math.radians(a))*oh)
        self.rectangularHole(x/2, h*0.2, 0.7*x+0.1*t, 1.3*t)
        self.moveTo(r)
        self.polyline(x-2*r, (90-a, r), oh, (90+a, r),
                      x-2*r+2*math.sin(math.radians(a))*oh,
                      (90+a, r), oh, (90-a, r))

