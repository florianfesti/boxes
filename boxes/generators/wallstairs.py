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

class WallStairs(_WallMountedBox):
    """Platforms in different heights e.g. for screw drivers"""

    description = """You are supposed to add holes or slots to the stair tops yourself using Inkscape or another vector drawing or CAD program.

sh gives height of the stairs from front to back. Note that the overall width and height is bigger than the nominal values as walls and the protrusions are not included in the measurements.
"""
    def __init__(self):
        super().__init__()

        self.buildArgParser(sx="250/3", sy="40*3", sh="30:100:180")
        self.argparser.add_argument(
            "--braceheight",  action="store", type=float, default=30,
            help="height of the brace at the bottom back (in mm). Zero for none")
        
    def yWall(self, move=None):
        t = self.thickness
        x, sx, y, sy, sh = self.x, self.sx, self.y, self.sy, self.sh        

        tw, th = sum(sy), max(sh) + t

        if self.move(tw, th, move, True):
            return

        self.polyline(y-t, 90)
        self.edges["f"](self.braceheight)
        self.step(t)
        self.edges["A"](sh[-1] - self.braceheight)
        self.corner(90)
        for i in range(len(sy)-1, 0, -1):
            self.edges["f"](sy[i])
            self.step(sh[i-1]-sh[i])
        self.edges["f"](sy[0])
        self.polyline(0, 90, sh[0], 90)
        
        self.move(tw, th, move)

    def yCB(self, width):
        t = self.thickness
        posx = -0.5 * t
        for dx in self.sx[:-1]:
            posx += dx + t
            self.fingerHolesAt(posx, 0, width, 90)
            

    def render(self):
        self.generateWallEdges()

        self.extra_height = 20
        t = self.thickness
        sx, sy, sh = self.sx, self.sy, self.sh
        self.x = x = sum(sx) + len(sx)*t - t
        self.y = y = sum(sy)

        for w in sy:
            self.rectangularWall(
                x, w, "eheh", callback=[lambda:self.yCB(w)], move="up")
        if self.braceheight:
            self.rectangularWall(
                x, self.braceheight, "eheh",
                callback=[lambda:self.yCB(self.braceheight)], move="up")
            
        for i in range(len(sx) + 1):
            self.yWall(move="right")
