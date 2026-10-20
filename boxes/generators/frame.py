# Copyright (C) 2026 Daniel Garcia
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

import math

from boxes import Boxes, boolarg, edges


class Frame(Boxes):
    """Flat frame or trim made of up to four mitred bars"""

    description = """
A flat frame around an opening: a picture frame, a window or door trim, a bezel.
The frame is cut as separate bars that lie in one plane. Neighbouring bars meet in a mitre
and can be locked together with dove tails.

Each bar has its own width. Set the width of a bar to 0 to leave that side open:

* `bottom = 0` gives a 3-sided trim, e.g. a window casing above a sill
* `bottom = 0` and `right = 0` gives an L shape

Where both bars of a corner have the same width the mitre is 45°. With different widths
the mitre runs from the inner corner to the outer corner, so the joint still closes.
Next to an open side the bar ends square.

`x` and `y` are the size of the opening. With `outside` they are the overall size of the frame
instead, and the opening is reduced by the bar widths.

All bars are drawn with their front side up and their inner edge at the bottom.
The vertical bars are drawn lying down to save material.

Without dove tails the bars only touch each other. Glue them to a backing board or join them
with biscuits, dowels or corner brackets.
"""

    ui_group = "Misc"

    SIDES = ("top", "bottom", "left", "right")

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.DoveTailSettings, size=2.0, depth=1.0)
        self.argparser.add_argument(
            "--x", action="store", type=float, default=150.0,
            help="width of the opening in mm (unless outside selected)")
        self.argparser.add_argument(
            "--y", action="store", type=float, default=100.0,
            help="height of the opening in mm (unless outside selected)")
        self.argparser.add_argument(
            "--outside", action="store", type=boolarg, default=False,
            help="treat x and y as the overall size of the frame")
        for side in self.SIDES:
            self.argparser.add_argument(
                f"--{side}", action="store", type=float, default=30.0,
                help=f"width of the {side} bar in mm (0 for no {side} bar)")
        self.argparser.add_argument(
            "--joint", action="store", type=str, default="dovetail",
            choices=["dovetail", "none"],
            help="how neighbouring bars are joined at the mitres")

    def bar(self, inner: float, w: float, w_start: float, w_end: float,
            slant_edge: str, label: str = "", move: str | None = None) -> None:
        """Draw one bar of the frame.

        The bar is drawn in the orientation it has in the top bar position:
        the inner edge (the one facing the opening) at the bottom, going left
        to right, and the body of the bar above it.

        :param inner: length of the inner edge
        :param w: width of this bar
        :param w_start: width of the neighbouring bar at the start (left end) of the inner edge, 0 for none
        :param w_end: width of the neighbouring bar at the end (right end) of the inner edge, 0 for none
        :param slant_edge: edge type for the mitres
        :param label: label of the part
        :param move: where to move after drawing
        """
        # A mitre runs from the inner corner to the outer corner. Without a
        # neighbour (width 0) it degrades to a square end of length w.
        h_start = math.hypot(w_start, w)
        h_end = math.hypot(w_end, w)
        a_start = math.degrees(math.atan2(w, w_start))
        a_end = math.degrees(math.atan2(w, w_end))
        outer = inner + w_start + w_end

        borders = [inner, a_end, h_end, 180 - a_end,
                   outer, 180 - a_start, h_start, a_start]
        edge_types = ["e",
                      slant_edge if w_end else "e",
                      "e",
                      slant_edge if w_start else "e"]
        self.polygonWall(borders, edge_types, move=move, label=label)

    def render(self):
        x, y = self.x, self.y
        widths = [getattr(self, side) for side in self.SIDES]
        top, bottom, left, right = widths

        for side, w in zip(self.SIDES, widths):
            if w < 0:
                raise ValueError(f"The {side} bar width must not be negative")
        if not any(widths):
            raise ValueError("At least one bar needs a width greater than 0")

        if self.outside:
            x -= left + right
            y -= top + bottom
        if x <= 0 or y <= 0:
            raise ValueError(
                "The opening must be larger than 0. "
                "Make x and y larger or the bars narrower.")

        width = x + left + right
        height = y + top + bottom

        # Horizontal bars get the dove tails, vertical bars the counter part
        if self.joint == "dovetail":
            h_edge, v_edge = "d", "D"
        else:
            h_edge = v_edge = "e"

        # Each bar is drawn as if it were the top bar. Turning it into its
        # position decides which neighbour is at which end:
        # bottom: turned by 180°, the right bar is at the start
        # left:   turned by 90° counter clockwise, the bottom bar is at the start
        # right:  turned by 90° clockwise, the top bar is at the start
        if top:
            self.bar(x, top, left, right, h_edge,
                     label=f"top {width:.0f}x{top:.0f}", move="up")
        if bottom:
            self.bar(x, bottom, right, left, h_edge,
                     label=f"bottom {width:.0f}x{bottom:.0f}", move="up")
        if left:
            self.bar(y, left, bottom, top, v_edge,
                     label=f"left {left:.0f}x{height:.0f}", move="up")
        if right:
            self.bar(y, right, top, bottom, v_edge,
                     label=f"right {right:.0f}x{height:.0f}", move="up")
