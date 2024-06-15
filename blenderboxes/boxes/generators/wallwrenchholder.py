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

class SlottedEdge(edges.Edge):

    def __call__(self, length, **kw):

        n = self.number
        t = self.thickness
        
        self.polyline(t, 45)

        l = t
        
        for i in range(n):
            w = self.min_width * ((n-i)/n) + self.max_width * (i / n)
            s = self.min_strength * ((n-i)/n) + self.max_strength * (i / n)
            if i == n-1:
                self.polyline(w-s/2+2*s, (-180, s/2), w - 0.5*s,
                              (180, s/2))
                l += s *2 * 2**0.5
            else:
                self.polyline(w-s/2+2*s, (-180, s/2), w - 0.5*s,
                              (135, s/2), self.extra_distance, (45, s/2))
                l += s *2 * 2**0.5 + self.extra_distance
        self.polyline(0, -45)
        self.edge(length-l)

class WallWrenchHolder(_WallMountedBox):
    """Hold a set of wrenches at a wall"""


    def __init__(self) -> None:
        super().__init__()

        # remove cli params you do not need
        self.buildArgParser(x=100)
        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--depth",  action="store", type=float, default=30.0,
            help="depth of the sides (in mm)")
        self.argparser.add_argument(
            "--number",  action="store", type=int, default=11,
            help="number of wrenches (in mm)")
        self.argparser.add_argument(
            "--min_width",  action="store", type=float, default=8.0,
            help="width of smallest wrench (in mm)")
        self.argparser.add_argument(
            "--max_width",  action="store", type=float, default=25.0,
            help="width of largest wrench (in mm)")
        self.argparser.add_argument(
            "--min_strength",  action="store", type=float, default=3.0,
            help="strength of smallest wrench (in mm)")
        self.argparser.add_argument(
            "--max_strength",  action="store", type=float, default=5.0,
            help="strength of largest wrench (in mm)")
        self.argparser.add_argument(
            "--extra_distance",  action="store", type=float, default=0.0,
            help="additional distance between wrenches (in mm)")


    def render(self):
        self.generateWallEdges()

        h = ((self.min_strength + self.max_strength) * self.number * 2**0.5
             +  self.extra_distance * (self.number - 1)
             + self.max_width)
        t = self.thickness
        x = self.x-2*t
        
        self.rectangularWall(self.depth, h,
                             ["e", "B", "e", SlottedEdge(self, None)],
                             move="right")
        self.rectangularWall(self.depth, h,
                             ["e", "B", "e", SlottedEdge(self, None)],
                             move="right")
        self.rectangularWall(x, h, "eDed",
            # callback=[lambda:self.fingerHolesAt(x/2, 0, h, 90)],
            move="right")
