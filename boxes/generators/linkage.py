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


class Linkage(Boxes):
    """Model for trying out linkages"""

    ui_group = "Part"

    description = """Needs pins of length 2 and 3 times thickness as vitamins.
Plain pins of length 2, Pins of length 3 with a disc on the first and middle third.
Linkages more complicated than a four bar linkage might need even more pins variants.
"""

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.buildArgParser(x=100, y=100)

        self.argparser.add_argument(
            "--diameter",  action="store", type=float, default=3.3,
            help="Diameter of the holes")
        self.argparser.add_argument(
            "--length",  action="store", type=float, default=200.0,
            help="Hole to hole length of longest linkage")
        self.argparser.add_argument(
            "--width",  action="store", type=float, default=15.0,
            help="Width of linkages")
        self.argparser.add_argument(
            "--dist",  action="store", type=float, default=5.0,
            help="Distance of holes")

    def link(self, l, holes=True, move=None):
        dist = self.dist
        w = self.width
        d = self.diameter

        l_ = (l // dist) * dist
        if l_ < l:
            l_ += dist

        def holesCB():
            for i in range(int(l_ // dist)):
                self.hole(i * dist, w/2, d=d)
            self.hole(l_, (w+dist)/2, d=d)
            self.hole(l_, (w-dist)/2, d=d)

        def slotCB():
            self.rectangularHole(l_/2, w/2, l_+d-2*dist, 1.05*d, r=d/2)
            self.hole(0, w/2, d=d)
            self.hole(l_, w/2, d=d)

        self.polygonWall((l_, (180, w/2), l_, (180, w/2)), "e",
                         callback=[holesCB if holes else slotCB], move=move)

    def plateCB(self):
        x, y, dist = self.x, self.y, self.dist
        n = int(x//dist) - 1

        for pos_y in (2*dist, y/2, y-2*dist):
            for i in range(n):
                self.hole(i*dist + (x-n*dist) / 2, pos_y, d=self.diameter)

    def render(self):
        w = self.width
        l = self.length

        self.partsMatrix(10, 10, "up", self.parts.disc, w, 0.95*self.diameter)

        for holes in (True, False):
            self.link(l, holes, "up")
            self.link(l*3/4, holes, "up")
            self.link(l/2, holes, "up")
            self.link(l/3, holes, "up")
            self.link(l/4, holes, "up")

        self.roundedPlate(self.x, self.y, self.thickness, "e", extend_corners=False,
                          callback=[self.plateCB], move="up")
