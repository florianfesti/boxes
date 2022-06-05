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

    description = """
Set *hi* larger than *h* to leave gap between the inner and outer shell. This can be used to make opening the box easier. Set *hi* smaller to only have a small inner ridge that will allow the content to be momre visible after opening.

![Bottom view](static/samples/TwoPiece2.jpg)
"""

    ui_group = "Box"

    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("x", "y", "h", "hi", "outside")
        self.addSettingsArgs(edges.FingerJointSettings, finger=2.0, space=2.0)

        self.argparser.add_argument(
            "--play",  action="store", type=float, default=0.15,
            help="play between the two parts as multipleof the wall thickness")

    def render(self):
        # adjust to the variables you want in the local scope
        x, y, h = self.x, self.y, self.h
        hi = self.hi or self.h
        t = self.thickness
        p = self.play * t

        if self.outside:
            x -= 4*t + 2*p
            y -= 4*t + 2*p
            h -= 2 * t
            hi -= 2 * t

        # Adjust h edge with play
        self.edges["f"].settings.setValues(t, False, edge_width=self.edges["f"].settings.edge_width + p)

        for i in range(2):
            d = i * 2 * (t+p)
            height = [hi, h][i]
            with self.saved_context():
                self.rectangularWall(x+d, height, "fFeF", move="right")
                self.rectangularWall(y+d, height, "ffef", move="right")
                self.rectangularWall(x+d, height, "fFeF", move="right")
                self.rectangularWall(y+d, height, "ffef", move="right")
            self.rectangularWall(y, height, "ffef", move="up only")

        self.rectangularWall(x, y, "hhhh", bedBolts=None, move="right")
        self.rectangularWall(x+d, y+d, "FFFF", bedBolts=None, move="right")
        
