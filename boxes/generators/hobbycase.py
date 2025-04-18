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
    """A case that can be used in any hobby involving small pieces in need of organizing."""

    ui_group = "Tray"

    description = """
The hobby case is defined by units, "cells" of the case.
You define depth, height and widths of the cells.
By combining dimensions with number of columns and rows slots for shelves are generated.
Slots can be populated by:

* shelves (horizontal piece of plywood that covers full width and depth of the column. You can put anything on them, but they also provide some structural integrity. It is recommended to have a least one shelve every 2-4 slots (depending on the unit height)
* rails (3 horizontal pieces that stick out of the side and back walls of the column. They can be used to allow taller things placed on shelves below, but also some sliding drawers can be put in them.
"""

    def __init__(self) -> None:
        super().__init__()
        self.debug = None
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
        self.argparser.add_argument("--inset_shelves", action="store", type=boolarg, default=True, help="Should the inner dividers and shelves be inset from the front edge?")
        self.addSettingsArgs(boxes.edges.StackableSettings, angle=90, width=0.0, height=2.0)


    def prepare(self):
        self.cols = len(self.unit_w)

        self.sum_w = sum(self.unit_w)
        self.inside_w = self.sum_w + 2 * (self.cols - 1) * self.thickness
        self.outside_w = self.inside_w + 2 * self.thickness

        self.sum_h = self.rows * self.unit_h
        self.inside_h = self.sum_h + (self.rows - 1) * self.thickness
        self.outside_h = self.inside_h + 2 * self.thickness

        self.shelves_n = [int(w) for w in self.shelves_n]
        self.railsets = [self.rows - 1 - shelve for shelve in self.shelves_n]

        self.inside_depth = self.unit_d
        self.outside_depth = self.unit_d if not self.inset_shelves else self.unit_d + 2 * self.thickness

        s = self.edgesettings.get("FingerJoint", {})
        s["width"] = 2.0
        doubleFingerJointSettings = edges.FingerJointSettings(self.thickness, True, **self.edgesettings.get("FingerJoint", {}))
        self.addPart(edges.FingerHoles(self, doubleFingerJointSettings), name="doubleFingerHolesAt")

    # Top / Bottom walls
    def top_and_bottom(self, move="up"):
        for name in ["bottom", "top"]:
            self.rectangularWall(self.inside_w, self.outside_depth, "fFeF",
                                 callback=[self.topAndBottomHolesCallback],
                                 move=move,
                                 label=f"{name} ({self.inside_w}x{self.outside_depth})")

    def topAndBottomHolesCallback(self):
        self.cut_double_wall_holes(self.inside_depth)

    # Vertical walls
    def vertical_walls(self, move="up"):
        self.ctx.save()

        self.verticalWall(self.outside_depth, self.inside_h, label="left")

        for i in range(2 * (self.cols - 1)):
            self.verticalWall(self.inside_depth, self.inside_h, label="vertical wall")

        self.verticalWall(self.outside_depth, self.inside_h, move="up", label="right")

        self.move(self.outside_depth, self.inside_h + 2 * self.thickness, move)

    def verticalWall(self, x, y, edges="feff", move="right", label=None):
        label = f"{label}\n({x}x{y})"
        self.rectangularWall(x, y, edges, callback=[self.slotsHolesCallback], move=move, label=label)

    def slotsHolesCallback(self):
        self.cut_shelve_holes_in_single_column(self.inside_depth, 0)

    # Cover
    def cover(self, move="up"):
        x = self.outside_w
        y = self.outside_h - self.thickness

        _edges = ["e", "z", "e", "z", "e"]
        hole_edge_length = self.unit_w[0]/2
        straight_edge_length = (x - 2 * hole_edge_length) / 3
        lengths = [straight_edge_length, hole_edge_length, straight_edge_length, hole_edge_length, straight_edge_length]
        edge_with_cutouts = boxes.edges.CompoundEdge(self, _edges, lengths)

        self.rectangularWall(x, y, ["e", "e", edge_with_cutouts, "e"], move=move, label=f"cover plate\n({x}x{y})")

    # Shelves
    def shelves(self, move="up"):
        for columnIndex, unit_width in enumerate(self.unit_w):
            x = unit_width
            y = self.inside_depth
            self.partsMatrix(self.shelves_n[columnIndex], 0, move,
                             self.rectangularWall,
                             x, y, "efff", label=f"shelf (column {columnIndex})\n({x}x{y})")

    # Rails
    def rails(self, move="up"):
        for col_idx, unit_width in enumerate(self.unit_w):
            for n in range(self.railsets[col_idx]):
                self.railSet(self.inside_depth, unit_width, move)

    def railSet(self, sideLength, backLength, move=None):
        self.ctx.save()
        self.rectangularWall( sideLength,0, "feSe", move="right")
        self.rectangularWall( backLength - 8*self.thickness,0, "feSe", move="right")
        self.rectangularWall( sideLength,0, "feSe", move="right")
        self.move(2*sideLength+backLength, 3 * self.thickness, move)

    # Base plate
    def base_plate(self, move="up"):
        self.rectangularWall(self.inside_w, self.inside_h, "FFFF",
                             callback=[self.baseplate_callback],
                             label=f"base plate\n({self.inside_w}x{self.inside_h})", move=move)

    def baseplate_callback(self):
        for col in range(self.cols):
            posx = sum(self.unit_w[:col]) + col * 2 * self.thickness
            self.cut_shelve_holes_in_single_column(self.unit_w[col], posx)
        self.cut_double_wall_holes(self.inside_h)

    # Render
    def render(self) -> None:
        self.prepare()
        self.base_plate()
        self.shelves()
        if self.add_cover:
            self.cover()
        self.top_and_bottom()
        self.vertical_walls()
        if self.add_rails:
            self.rails()

    # Helper functions
    def cut_double_wall_holes(self, length):
        for col in range(1, self.cols):
            posx = self.thickness + sum(self.unit_w[:col]) + (col-1) * 2 * self.thickness
            self.doubleFingerHolesAt(posx, 0, length, angle=90)

    def cut_shelve_holes_in_single_column(self, length, posx = 0):
        for row in range(1, self.rows):
            posy = 0.5 * self.thickness + row * self.unit_h + (row-1) * self.thickness
            self.fingerHolesAt(posx, posy, length, angle=0)
