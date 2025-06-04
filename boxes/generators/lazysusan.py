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


class LazySusan(Boxes):
    """Box for storing tipable things on a lazy susan"""

    ui_group = "FlexBox"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, finger=1.0,space=1.0)
        self.addSettingsArgs(edges.FlexSettings)
        
        self.buildArgParser(h=50)
        self.argparser.add_argument(
            "--inside_radius", action="store", type=float, default=40,
            help="inside radius of the lazy susan")
        self.argparser.add_argument(
            "--outside_radius", action="store", type=float, default=90,
            help="outside radius of the lazy susan")
        self.argparser.add_argument(
            "--angle", action="store", type=float, default=90,
            help="angle of the lazy susan")
        self.argparser.add_argument(
            "--top",  action="store", type=str, default="hole",
            choices=["hole", "lid", "closed",],
            help="style of the top and lid")

    def holeCB(self):
        angle, inside_radius, outside_radius, h = self.angle, self.inside_radius, self.outside_radius, self.h
        t = self.thickness
        s = 0.2 * inside_radius
        d = t
        poly = [s-d, (angle, outside_radius-s-d), s-d, 90,
                outside_radius-inside_radius-2*d, 90,
                s-d, (-angle, inside_radius-s+d), s-d, 90,
                outside_radius-inside_radius-2*d, 90]
        self.moveTo(d, d)
        self.polyline(*poly)

            
    def render(self):
        angle, inside_radius, outside_radius, h = self.angle, self.inside_radius, self.outside_radius, self.h
        t = self.thickness

        # angle = 30

        s = 0.2 * inside_radius
        
        poly=[s, (angle, outside_radius-s), s, 90,
              outside_radius-inside_radius, 90,
              s, (-angle, inside_radius-s), s, 90,
              outside_radius-inside_radius, 90]
        with self.saved_context():
            self.polygonWall(poly, move="right")
            if self.top == "closed":
                self.polygonWall(poly, move="right")
            else:
                self.polygonWall(poly, callback=[self.holeCB], move="right")
            if self.top == "lid":
                self.polygonWall(poly, edge="E", move="right")

        self.polygonWall(poly, move="up only")
        self.moveTo(0, t)
        self.polygonWalls(poly, self.h)
