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

class LaserHoldfast(Boxes):
    """A holdfast for honey comb tables of laser cutters"""

    ui_group = "Part"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.buildArgParser(x=25, h=40)
        self.argparser.add_argument(
            "--hookheight",  action="store", type=float, default=5.0,
            help="height of the top hook")
        self.argparser.add_argument(
            "--shaftwidth",  action="store", type=float, default=5.0,
            help="width of the shaft")

    def render(self):
        # adjust to the variables you want in the local scope
        x, hh, h, sw = self.x, self.hookheight, self.h, self.shaftwidth 
        t = self.thickness

        a = 30
        r = x/math.radians(a)

        self.polyline(hh+h, (180, sw/2), h, -90+a/2, 0, (-a, r), 0, (180, hh/2), 0, (a, r+hh), 0 , -a/2, sw-math.sin(math.radians(a/2))*hh , 90)
