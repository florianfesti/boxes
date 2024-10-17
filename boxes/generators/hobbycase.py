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
        self.argparser.add_argument("--unit_d", action="store", type=float, default=128, help="Depth of single unit")
        self.argparser.add_argument("--unit_h", action="store", type=float, default=50, help="Height of single unit")
        self.argparser.add_argument("--unit_w", action="store", type=argparseSections, default="215*3", help="Widths of unit columns, eg. 215*3 or 150:215:150")
        self.argparser.add_argument("--rows", action="store", type=int, default=6, help="Number of rows in each of the columns")
        self.argparser.add_argument("--shelves_n", action="store", type=argparseSections, default="2:3:2", help="How many shelves should each column have eg. 2:3:2. Use integers only!")
        self.argparser.add_argument("--add_rails", action="store", type=boolarg, default=True, help="Should rails be generated for slots unpopulated by shelves?")
        self.argparser.add_argument("--add_cover", action="store", type=boolarg, default=True, help="Should cover for the case be generated?")
        self.addSettingsArgs(boxes.edges.StackableSettings, angle=90, width=0.0, height=2.0, help="")

    @restore
    def edgeAt(self, edge, x, y, length, angle=0):
        self.moveTo(x, y, angle)
        edge = self.edges.get(edge, edge)
        edge(length)

    def prepare(self):
        self.cols = len(self.unit_w)

        self.sum_w = sum(self.unit_w)
        self.total_w = self.sum_w + 2 * (self.cols - 1) * self.thickness

        self.shelves_n = [int(w) for w in self.shelves_n]
        self.railsets = [self.rows - 1 - shelve for shelve in self.shelves_n]

        self.external_depth = self.unit_d + 2 * self.thickness
        self.internal_depth = self.unit_d

        s = self.edgesettings.get("FingerJoint", {})
        s["width"] = 2.0
        doubleFingerJointSettings = edges.FingerJointSettings(self.thickness, True,
                                                                **self.edgesettings.get("FingerJoint", {}))
        self.addPart(edges.FingerHoles(self, doubleFingerJointSettings), name="doubleFingerHolesAt")

    def topAndBottomHolesCallback(self):
        for col in range(1, self.cols):
            posx = sum(self.unit_w[:col]) + (col * 2 - 1) * self.thickness
            self.doubleFingerHolesAt(posx, 0, self.internal_depth, angle=90)

    def topAndBottom(self, move="up"):
        for name in ["bottom", "top"]:
            self.rectangularWall(
                self.total_w, self.external_depth, "fFeF",
                callback=[self.topAndBottomHolesCallback],
                move=move,
                label="%s (%ix%i)" % (name, self.total_w, self.external_depth))

    def slotsHolesCallback(self):
        for row in range(1, self.rows):
            posy = row * self.unit_h + (row + 0.5) * self.thickness
            self.fingerHolesAt(0, posy, self.internal_depth, angle=0)

    def verticalWall(self, x, y, edges=None, move=None, label=None):
        self.rectangularWall(x, y, edges, callback=[self.slotsHolesCallback], move=move, label=label)

    def verticalWalls(self, move="up"):
        self.ctx.save()
        x_inner = self.internal_depth
        x_outer = self.external_depth
        y = self.rows * self.unit_h + (self.rows + 1) * self.thickness

        self.rectangularWall(x_outer, y,
                             edges="feff",
                             callback=[self.slotsHolesCallback],
                             move="right",
                             label="left\n(%ix%i)" % (x_outer, y))

        for i in range(2 * (self.cols - 1)):
            self.verticalWall(x_inner, y, "feff", move="right", label="vertical wall\n(%ix%i)" % (x_inner, y))

        self.rectangularWall(x_outer, y,
                             edges="feff",
                             callback=[self.slotsHolesCallback],
                             move="up",
                             label="right\n(%ix%i)" % (x_outer, y))

        self.move(x_outer, y + 2 * self.thickness, move)

    def cover(self, move="up"):
        x = self.total_w + 2 * self.thickness
        y = self.rows * self.unit_h + (self.rows + 1) * self.thickness

        _edges = ["e", "z", "e", "z", "e"]
        hole_edge_length = self.unit_w[0]/2
        straight_edge_length = (x - 2 * hole_edge_length) / 3
        lengths = [straight_edge_length, hole_edge_length, straight_edge_length, hole_edge_length, straight_edge_length]

        self.rectangularWall(x, y, ["E", "E", boxes.edges.CompoundEdge(self, _edges, lengths), "E"],
                             move=move, label="cover plate\n(%ix%i)" % (x, y))

    def shelves(self, move="up"):
        for columnIndex, unit_width in enumerate(self.unit_w):
            x = unit_width
            y = self.internal_depth
            self.partsMatrix(self.shelves_n[columnIndex], 0, move,
                             self.rectangularWall,
                             x, y, "efff", label="shelf (column %i)\n(%ix%i)" % (columnIndex, x, y))

    def railSet(self, sideLength, backLength, move=None):
        self.ctx.save()
        self.rectangularWall( sideLength,0, "feSe", move="right")
        self.rectangularWall( backLength,0, "feSe", move="right")
        self.rectangularWall( sideLength,0, "feSe", move="right")
        self.move(2*sideLength+backLength, 3*self.thickness, move)

    def rails(self, move="up"):
        for col_idx, unit_width in enumerate(self.unit_w):
            for n in range(self.railsets[col_idx]):
                self.railSet(self.internal_depth, unit_width, move)

    def base_plate(self, move="up"):
        F = self.edges["F"].startwidth()
        tx = sum(self.unit_w) + 2 * (self.cols - 1) * self.thickness
        ty = self.rows * self.unit_h + (self.rows - 1) * self.thickness + 2 * F

        for col in range(self.cols):
            for row in range(1, self.rows):
                posx = 1.25 * self.thickness + sum(self.unit_w[:col]) + col * 2 * self.thickness
                posy = F + row * self.unit_h + row * self.thickness + 0.75 * self.thickness
                self.fingerHolesAt(posx, posy, self.unit_w[col], angle=0)

        for col in range(1, self.cols):
            posx = 0.25 * self.thickness + sum(self.unit_w[:col]) + col * 2 * self.thickness
            posy = F + 0.5 * self.thickness
            self.doubleFingerHolesAt(posx, posy, ty, angle=90)

        self.rectangularWall(tx, ty,
                             ["F","F","F","F"],
                             label="base plate\n(%ix%i)" % (tx, ty), move=move)

    def render(self) -> None:
        self.prepare()
        self.base_plate()
        if self.add_cover:
            self.cover()
        self.topAndBottom()
        self.verticalWalls()
        self.shelves()
        if self.add_rails:
            self.rails()
