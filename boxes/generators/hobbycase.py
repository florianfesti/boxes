# Copyright (C) 2024 Jan Grzybowski
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
from __future__ import annotations

import boxes
from boxes import *


class HobbyCase(Boxes):
    """A case that can be used in any hobby."""

    ui_group = "Tray"

    description = """
    The hobby case is defined by units, "cells" of the case. 
    You define depth, height and widths of the cells. 
    By combining dimensions with number of columns and rows slots for shelves are generated.
    Slots can be populated by:
     - shelves (horizontal piece of plywood that covers full width and depth of the column. You can put anything on them, but they also provide some structural integrity. It is recommended to have a least one shelve every 2-4 slots (depending on the unit height)
     - rails (3 horizontal pieces that stick out of the side and back walls of the column. They can be used to allow taller things placed on shelves below, but also some sliding drawers can be put in them.
"""

    def __init__(self) -> None:
        super().__init__()
        self.add_rails = True
        self.add_cover = True
        self.addSettingsArgs(boxes.edges.FingerJointSettings)
        self.argparser.add_argument("--unitD", action="store", type=float, default=128, help="Depth of single unit")
        self.argparser.add_argument("--unitH", action="store", type=float, default=50, help="Height of single unit")
        self.argparser.add_argument("--unitW", action="store", type=argparseSections, default="215*3", help="Widths of unit columns, eg. 215*3 or 150:215:150")
        self.argparser.add_argument("--rows", action="store", type=int, default=6, help="Number of rows in each of the columns")
        self.argparser.add_argument("--shelvesNs", action="store", type=argparseSections, default="2:3:2", help="How many shelves should each column have eg. 2:3:2. Use integers only!")
        self.argparser.add_argument("--add_rails", action="store", type=boolarg, default=True, help="Should rails be generated for slots unpopulated by shelves?")
        self.argparser.add_argument("--add_cover", action="store", type=boolarg, default=True, help="Should cover for the case be generated?")
        self.addSettingsArgs(boxes.edges.StackableSettings, angle=90, width=0.0, height=2.0, help="")

    @restore
    def edgeAt(self, edge, x, y, length, angle=0):
        self.moveTo(x, y, angle)
        edge = self.edges.get(edge, edge)
        edge(length)

    def prepare(self):
        self.cols = len(self.unitW)

        self.sumW = sum(self.unitW)
        self.totalW = self.sumW + 2 * (self.cols - 1) * self.thickness

        self.shelvesNs = [int(w) for w in self.shelvesNs]
        self.railsets = [self.rows-1-shelve for shelve in self.shelvesNs]

        self.externalDepth = self.unitD + 2 * self.thickness
        self.internalDepth = self.unitD

        s = self.edgesettings.get("FingerJoint", {})
        s["width"] = 2.0
        doubleFingerJointSettings = s = edges.FingerJointSettings(self.thickness, True,
                                                                **self.edgesettings.get("FingerJoint", {}))
        self.addPart(edges.FingerHoles(self, doubleFingerJointSettings), name="doubleFingerHolesAt")

    def topAndBottomHolesCallback(self):
        for col in range(1, self.cols):
            posx = sum(self.unitW[:col]) + (col * 2 - 1) * self.thickness
            self.doubleFingerHolesAt(posx, 0, self.internalDepth, angle=90)

    def topAndBottom(self):
        for name in ["bottom", "top"]:
            self.rectangularWall(
                self.totalW, self.externalDepth,"fFeF",
                callback=[self.topAndBottomHolesCallback],
                move="up",
                label="%s (%ix%i)" % (name, self.totalW, self.externalDepth))

    def shelvesHolesCallback(self):
        for row in range(1, self.rows):
            posy = row * self.unitH + (row + 0.5) * self.thickness
            self.fingerHolesAt(0, posy, self.internalDepth, angle=0)

    def verticalWall(self, x, y, edges=None, move=None, label=None):
        self.rectangularWall(x, y, edges, callback=[self.shelvesHolesCallback], move=move, label=label)

    def verticalWalls(self):
        self.ctx.save()
        x_inner = self.internalDepth
        x_outer = self.externalDepth
        y = self.rows * self.unitH + (self.rows + 1) * self.thickness

        self.rectangularWall(x_outer, y,
                             edges="feff",
                             callback=[self.shelvesHolesCallback],
                             move="right",
                             label="left\n(%ix%i)" % (x_outer, y))

        for i in range(2 * (self.cols - 1)):
            self.verticalWall(x_inner, y, "feff", move="right", label="vertical wall\n(%ix%i)" % (x_inner, y))

        self.rectangularWall(x_outer, y,
                             edges="feff",
                             callback=[self.shelvesHolesCallback],
                             move="up",
                             label="right\n(%ix%i)" % (x_outer, y))

        self.move(x_outer, y + 2 * self.thickness, "up")

    def cover(self, move=None):
        x = self.sumW + 2 * (self.cols-1) * self.thickness
        y = self.rows * self.unitH + (self.rows + 1) * self.thickness

        _edges = ["e", "z", "e", "z", "e"]
        hole_edge_length = self.unitW[0]/2
        straight_edge_length = (x - 2 * hole_edge_length) / 3
        lengths = [straight_edge_length, hole_edge_length, straight_edge_length, hole_edge_length, straight_edge_length]

        self.rectangularWall(x, y, ["e", "e", boxes.edges.CompoundEdge(self, _edges, lengths), "e"],
                             move="up", label="cover plate\n(%ix%i)" % (x, y))

    def shelves(self, move=None):
        for columnIndex, unitWidth in enumerate(self.unitW):
            x = unitWidth
            y = self.internalDepth
            self.partsMatrix(self.shelvesNs[columnIndex], 0, "up",
                             self.rectangularWall,
                             x, y, "efff", label="shelf (column %i)\n(%ix%i)" % (columnIndex, x, y))

    def railSet(self, sideLength, backLength, move=None):
        self.ctx.save()
        self.rectangularWall( sideLength,0, "feSe", move="right")
        self.rectangularWall( backLength,0, "feSe", move="right")
        self.rectangularWall( sideLength,0, "feSe", move="right")
        self.move(2*sideLength+backLength, 3*self.thickness, move)

    def rails(self):
        for col_idx, unitWidth in enumerate(self.unitW):
            for n in range(self.railsets[col_idx]):
                self.railSet(self.internalDepth, unitWidth,"up")

    def new_base_plate(self, move=None):
        F = self.edges["F"].startwidth()
        tx = sum(self.unitW) + 2 * (self.cols - 1) * self.thickness
        ty = self.rows * self.unitH + (self.rows - 1) * self.thickness + 2 * F

        for col in range(self.cols):
            for row in range(1, self.rows):
                posx = 1.25 * self.thickness + sum(self.unitW[:col]) + col * 2 * self.thickness
                posy = F + row * self.unitH + row * self.thickness + 0.75 * self.thickness
                self.fingerHolesAt(posx, posy, self.unitW[col], angle=0)

        for col in range(1, self.cols):
            posx = 0.25 * self.thickness + sum(self.unitW[:col]) + col * 2 * self.thickness
            posy = F + 0.5 * self.thickness
            self.doubleFingerHolesAt(posx, posy, ty, angle=90)

        self.rectangularWall(tx, ty,
                             ["F","F","F","F"],
                             label="base plate\n(%ix%i)" % (tx, ty), move="up")

    def render(self) -> None:
        self.prepare()
        self.new_base_plate()
        if self.add_cover:
            self.cover()
        self.topAndBottom()
        self.verticalWalls()
        self.shelves()
        if self.add_rails:
            self.rails()
