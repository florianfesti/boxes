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

from boxes import *

class HingeBox(Boxes):
    """Box with lid attached by cabinet hinges"""

    description = """Needs (metal) pins as hinge axles. Pieces of nails will
do fine. They need to be cut to length as they are captured as soon as the
hinges are assembled.

Assemble the box and the lid separately. Then insert the axle into the hinges.
Then attach the hinges on the inside of the box and then connect them to lid.
"""
    ui_group = "Box"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.CabinetHingeSettings)
        self.buildArgParser("x", "y", "h", "outside")
        self.argparser.add_argument(
            "--lidheight",  action="store", type=float, default=20.0,
            help="height of lid in mm")
        self.argparser.add_argument(
            "--splitlid",  action="store", type=float, default=0.0,
            help="split the lid in y direction (mm)")

    def render(self):

        x, y, h, hl = self.x, self.y, self.h, self.lidheight
        s = self.splitlid
        
        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            h = self.adjustSize(h)
            s = self.adjustSize(s, None) # reduce by half of the walls

        if s > x or s < 0.0: s = 0.0
        t = self.thickness

        # bottom walls
        if s:
            self.rectangularWall(x, h, "FFuF", move="right")
        else:
            self.rectangularWall(x, h, "FFeF", move="right")
        self.rectangularWall(y, h, "Ffef", move="up")
        self.rectangularWall(y, h, "Ffef")
        self.rectangularWall(x, h, "FFuF", move="left up")

        # lid
        self.rectangularWall(x, hl, "UFFF", move="right")
        if s:
            self.rectangularWall(s, hl, "eeFf", move="right")
            self.rectangularWall(y-s, hl, "efFe", move="up")
            self.rectangularWall(y-s, hl, "eeFf")
            self.rectangularWall(s, hl, "efFe", move="left")
            self.rectangularWall(x, hl, "UFFF", move="left up")
        else:
            self.rectangularWall(y, hl, "efFf", move="up")
            self.rectangularWall(y, hl, "efFf")
            self.rectangularWall(x, hl, "eFFF", move="left up")

        self.rectangularWall(x, y, "ffff", move="right only")
        self.rectangularWall(x, y, "ffff")
        if s:
            self.rectangularWall(x, s, "ffef", move="left up")
            self.rectangularWall(x, y-s, "efff", move="up")
        else:
            self.rectangularWall(x, y, "ffff", move="left up")
        self.edges['u'].parts(move="up")
        if s:
            self.edges['u'].parts(move="up")



