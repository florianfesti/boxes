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
from boxes.generators.bayonetbox import BayonetBox

class FilamentSpool(BayonetBox):
    """A two part spool for 3D printing filament"""

    description = """
Use small nails to properly align the pieces of the bayonet latch. Glue the parts of the bayonet latch before assembling the "axle". The inner parts go at the side and the outer parts at the inside of the axle.
![opened spool](static/samples/FilamentSpool-2.jpg)"""

    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)

        self.buildArgParser(h=48)
        self.argparser.add_argument(
            "--outer_diameter",  action="store", type=float, default=200.0,
            help="diameter of the flanges")
        self.argparser.add_argument(
            "--inner_diameter",  action="store", type=float, default=100.0,
            help="diameter of the center part")
        self.argparser.add_argument(
            "--axle_diameter",  action="store", type=float, default=50.0,
            help="diameter of the axle hole")
        self.argparser.add_argument(
            "--sides",  action="store", type=int, default=8,
            help="number of pieces for the center part")
        self.argparser.add_argument(
            "--alignment_pins",  action="store", type=float, default=1.0,
            help="diameter of the alignment pins")


    def leftsideCB(self):
        self.hole(0, 0, d=self.axle_diameter)
        r, h, side = self.regularPolygon(self.sides, radius=self.inner_diameter/2)
        for i in range(self.sides):
            self.fingerHolesAt(-side/2, h+0.5*self.thickness, side, 0)
            self.moveTo(0, 0, 360/self.sides)
        self.outerHolesCB()

    def outerHolesCB(self):
        t = self.thickness
        for i in range(6):
            for j in range(2):
                self.rectangularHole(
                    0, self.outer_diameter / 2 - 7.0,
                    self.outer_diameter * math.pi / 360 * 8, 5, r=2.5)
                self.moveTo(0, 0, 10)
            self.moveTo(0, 0, 360 / 6 - 20)
        self.rectangularHole(
            (self.outer_diameter + self.inner_diameter) / 4, 0,
            (self.outer_diameter - self.inner_diameter) / 2 - 4*t, t, r=t/2)
            
            
    def render(self):
        t = self.thickness

        self.inner_diameter -= 2 * t
        r, h, side = self.regularPolygon(self.sides, radius=self.inner_diameter/2)
        self.diameter = 2*h
        self.lugs = self.sides

        self.parts.disc(
            self.outer_diameter, callback=self.leftsideCB, move="right")
        self.parts.disc(
            self.outer_diameter, hole=self.axle_diameter,
            callback=lambda:(self.alignmentHoles(True),
                             self.outerHolesCB()),
            move="right")
        self.regularPolygonWall(
            self.sides, r=self.inner_diameter/2, edges="f",
            callback=[self.upperCB], move="right")
        self.parts.disc(self.diameter, callback=self.lowerCB, move="right")

        for i in range(self.sides):
            self.rectangularWall(
                side, self.h - t, "feFe",
                callback=[lambda:self.hole(side/2, self.h-2*t, r=t)],
                move="right")
