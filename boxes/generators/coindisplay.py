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

class CoinHolderSideEdge(edges.BaseEdge):
    char = "B"
    def __call__(self, length, **kw):
        a_l = self.coin_plate
        a_l2 = self.settings.coin_plate * math.sin(self.settings.angle)
        a = math.degrees(self.settings.angle)

        print(a, a_l, a_l2)
        self.corner(-a)
        # Draw the angled edge, but set the thickness to two temporarily
        #   as two pieces will go on top of another
        self.edges["F"].settings.thickness = self.thickness * 2
        self.edges["F"](a_l)
        self.edges["F"].settings.thickness = self.thickness

        self.polyline(0, 90+a, a_l2, -90)

    def margin(self) -> float:
        return self.settings.coin_plate_x

class CoinDisplay(Boxes):
    """A showcase for a single coin"""

    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser("x", "y", "h", "outside")
        self.argparser.add_argument(
            "--coin_d",  action="store", type=float, default=20.0,
            help="The diameter of the coin in mm")
        self.argparser.add_argument(
            "--coin_plate",  action="store", type=float, default=50.0,
            help="The size of the coin plate")
        self.argparser.add_argument(
            "--coin_showcase_h",  action="store", type=float, default=50.0,
            help="The height of the coin showcase piece")
        self.argparser.add_argument(
            "--angle",  action="store", type=float, default=30,
            help="The angle that the coin will tilt as")

    def bottomHoles(self):
        """
        Function that puts two finger holes at the bottom cube plate for the coin holder
        """
        self.fingerHolesAt(self.x/2 - self.thickness - self.thickness/2 - (self.coin_plate/2), self.y/2+self.coin_plate_x/2-self.thickness, self.coin_plate_x, -90)
        self.fingerHolesAt(self.x/2 - self.thickness + self.thickness/2 + (self.coin_plate/2), self.y/2+self.coin_plate_x/2-self.thickness, self.coin_plate_x, -90)

        self.fingerHolesAt(self.x/2-self.coin_plate/2-self.thickness, self.y/2-self.coin_plate_x/2-self.thickness*1.5, self.coin_plate, 0)

    def coinCutout(self):
        """
        Function that puts a circular hole in the coin holder piece
        """
        self.hole(self.coin_plate/2, self.coin_plate/2, self.coin_d/2)

    def render(self):

        x, y, h = self.x, self.y, self.h

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            h = self.adjustSize(h)

        t = self.thickness

        d2 = edges.Bolts(2)
        d3 = edges.Bolts(3)

        d2 = d3 = None

        self.addPart(CoinHolderSideEdge(self, self))

        self.angle = math.radians(self.angle)
        self.coin_plate_x = self.coin_plate * math.cos(self.angle)

        self.rectangularWall(x, h, "FFFF", bedBolts=[d2] * 4, move="right", label="Wall 1")
        self.rectangularWall(y, h, "FfFf", bedBolts=[d3, d2, d3, d2], move="up", label="Wall 2")
        self.rectangularWall(y, h, "FfFf", bedBolts=[d3, d2, d3, d2], label="Wall 4")
        self.rectangularWall(x, h, "FFFF", bedBolts=[d2] *4, move="left up", label="Wall 3")

        self.rectangularWall(x, y, "ffff", bedBolts=[d2, d3, d2, d3], move="right", label="Top")
        self.rectangularWall(x, y, "ffff", bedBolts=[d2, d3, d2, d3], move="right", label="Bottom", callback=[self.bottomHoles])

        # Draw the coin holder side holsers
        e = ["f", "f", "B", "e"]
        self.rectangularWall(self.coin_plate_x, self.coin_showcase_h, e, move="right", label="CoinSide1")
        self.rectangularWall(self.coin_plate_x, self.coin_showcase_h, e, move="right", label="CoinSide2")

        self.rectangularWall(self.coin_plate, self.coin_plate, "efef", move="left down", label="Coin Plate Base")
        self.rectangularWall(self.coin_plate, self.coin_plate, "efef", move="down", label="Coin Plate", callback=[self.coinCutout])

        self.rectangularWall(self.coin_plate, self.coin_showcase_h, "fFeF", move="down", label="CoinSide3")

