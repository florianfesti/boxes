#!/usr/bin/python3
# Copyright (C) 2013-2018 Florian Festi
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


class TwoPiece(Boxes):
    """A two piece box where top slips over the bottom half to form 
       the enclosure.
    """

    ui_group = "Box"

    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("x", "y", "h", "outside")
        self.addSettingsArgs(edges.FingerJointSettings, finger=2.0, space=2.0)

        self.argparser.add_argument(
            "--play",  action="store", type=float, default=0.05,
            help="play between the two parts as multipleof the wall thickness")

    def render(self):
        # adjust to the variables you want in the local scope
        x, y, h = self.x, self.y, self.h
        t = self.thickness
        p = self.play * t

        if self.outside:
            x -= 4*t + 2*p
            y -= 4*t + 2*p
            h -= 2 * t


        # Adjust h edge with play
        self.edges["f"].settings.setValues(t, False, edge_width=self.edges["f"].settings.edge_width + p)

        for i in range(2):
            d = i * 2 * (t+p)
            with self.saved_context():
                self.rectangularWall(x+d, h, "fFeF", bedBolts=None, move="right")
                self.rectangularWall(y+d, h, "ffef", bedBolts=None, move="right")
                self.rectangularWall(x+d, h, "fFeF", bedBolts=None, move="right")
                self.rectangularWall(y+d, h, "ffef", bedBolts=None, move="right")
            self.rectangularWall(y, h, "ffef", bedBolts=None, move="up only")

        self.rectangularWall(x, y, "hhhh", bedBolts=None, move="right")
        self.rectangularWall(x+d, y+d, "FFFF", bedBolts=None, move="right")
        
