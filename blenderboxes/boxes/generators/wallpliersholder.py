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

from boxes import *
from boxes.walledges import _WallMountedBox

class WallPliersHolder(_WallMountedBox):
    """Bar to hang pliers on"""

    def __init__(self) -> None:
        super().__init__()

        self.buildArgParser(sx="100*3", y=50, h=50, outside=True)

        self.argparser.add_argument(
            "--angle",  action="store", type=float, default=45,
            help="bracing angle - less for more bracing")

    def brace(self, h, d, a, outside=False, move=None):
        t = self.thickness
        
        tw = d + self.edges["b"].spacing() + self.edges["f"].spacing()
        th = self.h_t

        if self.move(tw, th, move, True):
            return

        self.moveTo(self.edges["b"].spacing())

        r = d / 4
        l = (d + t - r) / math.sin(math.radians(a))

        if outside:
            self.polyline(t, (90-a, r), l, (a, r))
            self.edges["h"](h)
            self.polyline(0, 90, d + 2*t, 90)
        else:
            self.polyline(0, (90-a, r), l, (a, r), 0, 90, t, -90)
            self.edges["f"](h)
            self.polyline(0, 90, d, 90)
        self.edges["b"](h + (d+t-r) * math.tan(math.radians(90-a)) + r)
        self.polyline(0, 90)

        self.move(tw, th, move)

    def frontCB(self):
        t = self.thickness
        posx = -t
        for dx in self.sx[:-1]:
            posx += dx + t
            self.fingerHolesAt(posx, 0, self.h, 90)

    def backCB(self):
        t = self.thickness
        posx = -t
        for dx in self.sx[:-1]:
            posx += dx + t
            self.wallHolesAt(posx, 0, self.h_t, 90)

    def render(self):
        self.generateWallEdges()

        if self.outside:
            self.sx = self.adjustSize(self.sx)
        
        sx, y, h = self.sx, self.y, self.h
        t = self.thickness

        r = y / 4
        self.h_t = h + (y+t-r) * math.tan(math.radians(90-self.angle)) + r
        
        self.rectangularWall(sum(sx) + (len(sx)-1) * t, h, "efef", callback=[self.frontCB],  move="up")
        self.rectangularWall(sum(sx) + (len(sx)-1) * t, self.h_t, "eCec", callback=[self.backCB],  move="up")
        for i in range(len(sx)+1):
            self.brace(h, y, self.angle, i<2, move="right")
            
