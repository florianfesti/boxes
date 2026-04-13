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
        nx = (int(x//dist) // 2) * 2 - 1
        ny = (int(y//dist) // 2) * 2 - 1

        self.moveTo(-self.thickness)
        for pos_y in (y/2-dist*((ny-1)/2), y/2, y/2+dist*((ny-1)/2)):
            for i in range(nx):
                self.hole(i*dist + (x - (nx-1)*dist)/2, pos_y, d=self.diameter)
        for pos_x in (x/2-dist*(nx-1)/2, x/2, x/2+dist*(nx-1)/2):
            for i in range(ny):
                if i in (0, (ny-1)/2, ny-1): continue
                self.hole(pos_x, i*dist + (y-(ny-1)*dist) / 2, d=self.diameter)

    def render(self):
        w = self.width
        l = self.length
        d = self.diameter

        with self.saved_context():
            self.partsMatrix(8, 8, "right", self.parts.disc, w, 0.95*d)
            self.partsMatrix(2, 2, "", self.parts.disc, w, callback=lambda: (self.hole(-self.dist/2, 0, d=0.95*d), self.hole(+self.dist/2, 0, d=0.95*d)))
        self.partsMatrix(8, 8, "up only", self.parts.disc, w)

        for lengths in ((l, ), (l,), (l*3/4, l/4), (l*3/4, l/4), (l/2, l/2), (l/3, l/3)):
            with self.saved_context():
                for length in lengths:
                    self.link(length, True, "right")
            self.link(l, False, "up only")
        for lengths in ((l, ), (l*3/4, l/4), (l/2, l/2), (l/3, l/3)):
            with self.saved_context():
                for length in lengths:
                    self.link(length, False, "right")
            self.link(l, False, "up only")

        self.roundedPlate(self.x, self.y, self.thickness, "e", extend_corners=False,
                          callback=[self.plateCB], move="up")
