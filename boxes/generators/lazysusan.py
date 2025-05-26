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


    def drawfloor(self, angle=None, inside_radius=None, outside_radius=None):
        with self.saved_context():
            self.moveTo(inside_radius, 0)
            self.moveArc(90)
            self.polyline(0, (angle, inside_radius))
        
        with self.saved_context():
            self.moveTo(outside_radius, 0)
            self.moveArc(90)
            self.polyline(0, (angle, outside_radius))
            self.polyline(0, 90)
            self.edges["f"](outside_radius-inside_radius)

        with self.saved_context():
            self.moveTo(inside_radius, 0)
            self.edges["f"](outside_radius-inside_radius)
            
    def render(self):
        angle,inside_radius,outside_radius, h = self.angle, self.inside_radius, self.outside_radius, self.h
        t = self.thickness

        # angle = 30

        self.moveTo(-inside_radius, 5)
        self.drawfloor(angle, inside_radius, outside_radius)
        self.moveTo(outside_radius+5, 0)
        # 
        outside_wall = angle * (math.pi / 180) * outside_radius
        self.rectangularWall(outside_wall, h, "eFeF", move="right")

        inside_wall = angle * (math.pi / 180) * inside_radius
        self.rectangularWall(inside_wall, h, "eFeF", move="right")
        self.flangedWall(outside_radius-inside_radius,h, "FfFf", move="up" )
        self.flangedWall(outside_radius-inside_radius,h, "FfFf", move="right")
