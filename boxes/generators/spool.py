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

class Spool(Boxes):
    """A simple spool"""

    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)

        self.buildArgParser(h=100)
        self.argparser.add_argument(
            "--outer_diameter",  action="store", type=float, default=200.0,
            help="diameter of the flanges")
        self.argparser.add_argument(
            "--inner_diameter",  action="store", type=float, default=80.0,
            help="diameter of the center part")
        self.argparser.add_argument(
            "--axle_diameter",  action="store", type=float, default=40.0,
            help="diameter of the axle hole (axle not part of drawing)")
        self.argparser.add_argument(
            "--sides",  action="store", type=int, default=8,
            help="number of pieces for the center part")
        self.argparser.add_argument(
            "--reinforcements",  action="store", type=int, default=8,
            help="number of reinforcement ribs per side")
        self.argparser.add_argument(
            "--reinforcement_height",  action="store", type=float, default=0.0,
            help="height of reinforcement ribs on the flanges")

    def sideCB(self):
        self.hole(0, 0, d=self.axle_diameter)
        r, h, side = self.regularPolygon(self.sides, radius=self.inner_diameter/2)
        t = self.thickness
        for i in range(self.sides):
            self.fingerHolesAt(-side/2, h+0.5*self.thickness, side, 0)
            self.moveTo(0, 0, 360 / self.sides)

        if self.reinforcement_height:
            for i in range(self.reinforcements):
                self.fingerHolesAt(
                    self.axle_diameter / 2, 0, h-self.axle_diameter / 2, 0)
                self.fingerHolesAt(
                     r + t, 0, self.outer_diameter / 2 - r - t, 0)
                self.moveTo(0, 0, 360 / self.reinforcements)

    def reinforcementCB(self):
        for i in range(self.reinforcements):
            self.fingerHolesAt(
                self.axle_diameter / 2, 0,
                (self.inner_diameter - self.axle_diameter) / 2 + self.thickness, 0)
            self.moveTo(0, 0, 360 / self.reinforcements)
        
        
    def render(self):
        t = self.thickness
        r, h, side = self.regularPolygon(self.sides, radius=self.inner_diameter/2)
        for i in range(2):
            self.parts.disc(
                self.outer_diameter, callback=self.sideCB, move="right")
        for i in range(self.sides):
            self.rectangularWall(side, self.h, "fefe", move="right")
        if self.reinforcement_height:
            for i in range(self.reinforcements*2):
                edge = edges.CompoundEdge(
                    self, "fef",
                    [self.outer_diameter / 2 - r - t,
                     r - h + t,
                     h - self.axle_diameter / 2])
                self.trapezoidWall(
                    self.reinforcement_height - t,
                    (self.outer_diameter - self.axle_diameter) / 2,
                    (self.inner_diameter - self.axle_diameter) / 2 + t,
                    ["e", "f", "e", edge],
                    move="right")
            for i in range(2):
                self.parts.disc(
                    self.inner_diameter + 2*t,
                    hole=self.axle_diameter,
                    callback=self.reinforcementCB,
                    move="right")
