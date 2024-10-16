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


def create_custom_array(values, inbetween_value, ends_value=None):
    array = [elem for pair in zip(values, [inbetween_value] * (len(values) - 1)) for elem in pair] + [values[-1]]
    if not ends_value:
        return array
    return [ends_value] + array + [ends_value]


class HobbyCaseLayout(Boxes):
    """Generate a typetray from a layout file."""

    # This class reads in the layout either from a file (with --input) or
    # as string (with --layout) and turns it into a drawing for a box.

    ui_group = "Tray"

    description = """This is a two step process. This is step 2.
Edit the layout text graphics to adjust your tray.
Put in the sizes for each column and row. You can replace the hyphens and
vertical bars representing the walls with a space character to remove the walls.
You can replace the space characters representing the floor by a "X" to remove the floor for this compartment.
"""

    def __init__(self) -> None:
        super().__init__()
        self.add_rails = True
        self.add_cover = True
        self.addSettingsArgs(boxes.edges.FingerJointSettings)
        self.argparser.add_argument("--unitD", action="store", type=float, default=128)
        self.argparser.add_argument("--unitH", action="store", type=float, default=50)
        self.argparser.add_argument("--unitW", action="store", type=str, default="215 215 215")
        self.argparser.add_argument("--cols", action="store", type=int, default=3)
        self.argparser.add_argument("--rows", action="store", type=int, default=6)
        self.argparser.add_argument("--shelvesNs", action="store", type=str, default="2 3 2")
        self.argparser.add_argument("--add_rails", action="store", type=boolarg, default=True)
        self.argparser.add_argument("--add_cover", action="store", type=boolarg, default=True)
        self.addSettingsArgs(boxes.edges.StackableSettings, angle=90, width=0.0, height=2.0)

    @restore
    def edgeAt(self, edge, x, y, length, angle=0):
        self.moveTo(x, y, angle)
        edge = self.edges.get(edge, edge)
        edge(length)

    def prepare(self):
        self.unitW = [float(w) for w in self.unitW.split()]
        self.sumW = sum(self.unitW)
        self.totalW = self.sumW + 2 * (self.cols - 1) * self.thickness

        self.shelvesNs = [int(w) for w in self.shelvesNs.split()]
        self.railsets = [self.rows-1-shelve for shelve in self.shelvesNs]

        self.externalDepth = self.unitD + 2 * self.thickness
        self.internalDepth = self.unitD

        s = self.edgesettings.get("FingerJoint", {})
        s["width"] = 2.0
        doubleFingerJointSettings = s = edges.FingerJointSettings(self.thickness, True,
                                                                **self.edgesettings.get("FingerJoint", {}))
        self.addPart(edges.FingerHoles(self, doubleFingerJointSettings), name="doubleFingerHolesAt")

    def topAndBottomCB(self):
        for col in range(1, self.cols):
            posx = sum(self.unitW[:col]) + (col * 2 - 1) * self.thickness
            self.doubleFingerHolesAt(posx, 0, self.internalDepth, angle=90)

    def topAndBottom(self):
        for name in ["bottom", "top"]:
            self.rectangularWall(
                self.totalW, self.externalDepth,
                [self.segmented_edge(self.unitW, "f", 2*self.thickness, "e"), "F", "e", "F"],
                callback=[self.topAndBottomCB],
                move="up",
                label="%s (%ix%i)" % (name, self.totalW, self.externalDepth))

    def shelveCB(self):
        for row in range(1, self.rows):
            posy = row * self.unitH + (row + 0.5) * self.thickness
            self.fingerHolesAt(0, posy, self.internalDepth, angle=0)

    def verticalWall(self, x, y, edges=None, move=None, label=None):
        self.rectangularWall(x, y, edges, callback=[self.shelveCB], move=move, label=label)

    def verticalWalls(self):
        self.ctx.save()
        x_inner = self.internalDepth
        x_outer = self.externalDepth
        y = self.rows * self.unitH + (self.rows + 1) * self.thickness

        self.rectangularWall(x_outer, y,
                             edges=["f",
                                    "e",
                                    "f",
                                    self.segmented_edge([self.unitH] * self.rows, "f", self.thickness, "e",
                                                        self.thickness * 1, "e")],
                             callback=[self.shelveCB],
                             move="right",
                             label="left\n(%ix%i)" % (x_outer, y))

        for i in range(2 * (self.cols - 1)):
            self.verticalWall(x_inner, y, "feff", move="right", label="vertical wall\n(%ix%i)" % (x_inner, y))

        self.rectangularWall(x_outer, y,
                             edges=["f",
                                    "e",
                                    "f",
                                    self.segmented_edge([self.unitH] * self.rows, "f", self.thickness, "e",
                                                        self.thickness * 1, "e")],
                             callback=[self.shelveCB],
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

        horizontalLengths = self.unitW
        horizontalInbetween = 2 * self.thickness
        verticalLengths = [self.unitH] * self.rows
        verticalInbetween = self.thickness

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
                             [
                                 self.segmented_edge(horizontalLengths, "F", horizontalInbetween, "E"),
                                 self.segmented_edge(verticalLengths, "F", verticalInbetween, "E", F, "E"),
                                 self.segmented_edge(list(reversed(horizontalLengths)), "F", horizontalInbetween, "E"),
                                 self.segmented_edge(list(reversed(verticalLengths)), "F", verticalInbetween, "E", F,"E"),
                             ], label="base plate\n(%ix%i)" % (tx, ty), move="up")

    def segmented_edge(self, segments_lengths, segment_edge, inbetween_length, inbetween_edge, ends_length=None,
                       ends_edge=None):
        lengths = create_custom_array(segments_lengths, inbetween_length, ends_length)
        _edges = create_custom_array([segment_edge] * len(segments_lengths), inbetween_edge, ends_edge)
        return boxes.edges.CompoundEdge(self, _edges, lengths)

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
