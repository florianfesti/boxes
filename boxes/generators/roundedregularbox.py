# Copyright (C) 2013-2014 Florian Festi
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

import math

import boxes


class RoundedRegularBox(boxes.Boxes):
    """Regular polygone box with vertical edges rounded"""

    description = """"""

    ui_group = "FlexBox"

    def __init__(self) -> None:
        boxes.Boxes.__init__(self)
        self.addSettingsArgs(boxes.edges.FingerJointSettings)
        self.addSettingsArgs(boxes.edges.DoveTailSettings)
        self.addSettingsArgs(boxes.edges.FlexSettings)
        self.buildArgParser(h="100.0")
        self.argparser.add_argument(
            "--sides", action="store", type=int, default=5,
             help="number of sides")
        self.argparser.add_argument(
            "--inner_size", action="store", type=float, default=150,
            help="diameter of the inner circle in mm")
        self.argparser.add_argument(
            "--radius", action="store", type=float, default=15,
            help="Radius of the corners in mm")
        self.argparser.add_argument(
            "--wallpieces", action="store", type=int, default=0,
             help="number of pieces for outer wall (0 for one per side)")
        self.argparser.add_argument(
            "--top",  action="store", type=str, default="none",
            choices=["closed", "hole", "lid",],
            help="style of the top and lid")

    def holeCB(self):
        n = self.sides
        t = self.thickness

        poly = [self.side, (360 / n, self.radius-2*t)] * n

        self.moveTo(-self.side/2, 2*t)
        self.polygonWall(poly, edge="e", turtle=True)

    def render(self):

        n = self.sides
        t = self.thickness
        if self.wallpieces == 0:
            self.wallpieces = n

        _radius, height, side = self.regularPolygon(n, h=self.inner_size/2)

        self.side = side = side - 2 * self.radius * math.tan(math.radians(360/2/n))

        poly = [side/2, (360 / n, self.radius)]
        parts = 1
        for i in range(n-1):
            if self.wallpieces * (i+1) / n >= parts:
                poly.extend([side/2, 0, side/2, (360 / n, self.radius)])
                parts += 1
            else:
                poly.extend([side, (360 / n, self.radius)])
        poly.extend([side/2, 0])

        with self.saved_context():
            self.polygonWall(poly, move="right")
            if self.top == "closed":
                self.polygonWall(poly, move="right")
            else:
                self.polygonWall(poly, callback=[self.holeCB], move="right")
            if self.top == "lid":
                self.polygonWall([self.side, (360 / n, self.radius+t)] *n, edge="e", move="right")

        self.polygonWall(poly, move="up")
        self.moveTo(0, t)
        self.polygonWalls(poly, self.h)
