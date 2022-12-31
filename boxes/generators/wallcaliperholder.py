#!/usr/bin/env python3
# Copyright (C) 2013-2019 Florian Festi
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

from boxes.walledges import _WallMountedBox

class WallCaliper(_WallMountedBox):
    """Holds a single caliper to a wall"""

    def __init__(self):
        super().__init__()

        # remove cli params you do not need
        self.buildArgParser(h=100)
        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--width",  action="store", type=float, default=18.0,
            help="width of the long end")
        self.argparser.add_argument(
            "--heigth",  action="store", type=float, default=6.0,
            help="heigth of the body")

    def side(self, move=None):
        t = self.thickness
        h = self.h
        hc = self.heigth

        tw = self.edges["b"].spacing() + hc + 8*t

        if self.move(tw, h, move, True):
            return
        
        self.moveTo(self.edges["b"].startwidth())
        self.polyline(5*t+hc, (90, 2*t), h/2-2*t, (180, 1.5*t), 0.25*h,
                      -90, hc, -90, 0.75*h-2*t, (90, 2*t), 2*t, 90)

        self.edges["b"](h)

        self.move(tw, h, move)

    def render(self):
        self.generateWallEdges()

        t = self.thickness
        h = self.h
        
        self.side(move="right")
        self.side(move="right")
        w = self.width
        self.flangedWall(w, h, flanges=[0, 2*t, 0, 2*t], edges="eeee",
                         r=2*t,
                         callback=[lambda:(self.wallHolesAt(1.5*t, 0, h, 90), self.wallHolesAt(w+2.5*t, 0, h, 90))])
