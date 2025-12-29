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


class Crate(Boxes):
    """Crate with handles. Can be made stackable. Can produce additional mask to put patterns onto crate walls"""

    description = """Pattern mask can be used in your editor to cut out from some pattern section that will be added to walls."""
    ui_group = "Box"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, bottom_lip=1.0)
        self.addSettingsArgs(edges.StackableSettings, bottom_stabilizers=2.0)
        self.buildArgParser(x=150, y=200, h=100)

        self.argparser.add_argument("--HandleOffset", action="store", type=float, default=10.0, help="offset of the handle hole from top edge")
        self.argparser.add_argument("--HandleWidth", action="store", type=float, default=100.0, help="width of the handle hole")
        self.argparser.add_argument("--HandleHeight", action="store", type=float, default=25.0, help="height of the handle hole")
        self.argparser.add_argument("--HandleRadius", action="store", type=float, default=12.5, help="handle hole radius")
        self.argparser.add_argument("--MakeStackable", action="store", type=boolarg, default=True, help="make crates stackable")
        self.argparser.add_argument("--AddPatternMask", action="store", type=boolarg, default=False, help="add pattern mask")

    def handleHole(self, width):
        stackEdge = self.edges['s'].settings
        offsetForStacking = stackEdge.height if self.MakeStackable else 0
        hoffset = self.HandleOffset
        hw = self.HandleWidth
        hh = self.HandleHeight
        hr = self.HandleRadius
        handley = hh/2 + hoffset - offsetForStacking
        self.rectangularHole(width/2, handley, hw, hh, hr)
        if self.AddPatternMask:
            self.rectangularHole(width/2, handley, hw + hoffset * 2, hh + hoffset * 2, hr + hoffset, color = Color.ANNOTATIONS)
            patternHeight = self.h - hoffset * 2
            patterny = handley + patternHeight/2 if self.MakeStackable else hoffset + patternHeight/2
            self.rectangularHole(width/2, patterny, width - hoffset * 2, patternHeight, 0, color = Color.ANNOTATIONS)


    def frontHandleHole(self):
        self.handleHole(self.x)

    def sideHandleHole(self):
        self.handleHole(self.y)

    def render(self):
        x, y, h = self.x, self.y, self.h

        self.rectangularWall(y, x, "ffff", move="up", label="Bottom")

        if self.MakeStackable:
            frontEdges = "sfSf"
            sideEdges = "sFSF"
        else:
            frontEdges = "hfef"
            sideEdges = "hFeF"

        self.rectangularWall(y, h, sideEdges, callback=[None, None, self.sideHandleHole, None], ignore_widths=[1, 6], move="up", label="side1")
        self.rectangularWall(y, h, sideEdges, callback=[None, None, self.sideHandleHole, None], ignore_widths=[1, 6], move="up", label="side2")

        self.rectangularWall(x, h, frontEdges, callback=[None, None, self.frontHandleHole, None], ignore_widths=[1, 6], move="right", label="front")
        self.rectangularWall(x, h, frontEdges, callback=[None, None, self.frontHandleHole, None], ignore_widths=[1, 6], label="back")
