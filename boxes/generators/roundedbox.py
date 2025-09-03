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

import boxes
from math import sqrt


class RoundedBox(boxes.Boxes):
    """Box with vertical edges rounded"""

    description = """
Default: edge_style = f Finger Joint:
![Finger Joint](static/samples/RoundedBox-2.jpg)

Alternative: edge_style = h Edge (parallel Finger Joint Holes):
![Finger Joint Holes](static/samples/RoundedBox-3.jpg)

With lid:
"""

    ui_group = "FlexBox"

    def __init__(self) -> None:
        boxes.Boxes.__init__(self)
        self.addSettingsArgs(boxes.edges.FingerJointSettings)
        self.addSettingsArgs(boxes.edges.DoveTailSettings)
        self.addSettingsArgs(boxes.edges.FlexSettings)
        self.buildArgParser("x", "y", "outside", sh="100.0")
        self.argparser.add_argument(
            "--radius", action="store", type=float, default=15,
            help="Radius of the corners in mm")
        self.argparser.add_argument(
            "--wallpieces", action="store", type=int, default=1,
            choices=[1, 2, 3, 4], help="number of pieces for outer wall")
        self.argparser.add_argument(
            "--edge_style", action="store",
            type=boxes.ArgparseEdgeType("fFh"), choices=list("fFh"),
            default="f",
            help="edge type for top and bottom edges")
        self.argparser.add_argument(
            "--top",  action="store", type=str, default="hole",
            choices=["hole", "lid", "closed", "lid_with_latches"],
            help="style of the top and lid")

    @property
    def hole_dr(self):
        dr = 2*self.thickness
        if self.edge_style == "h":
            dr = self.thickness
        return dr

    def top_hole(self):
        t = self.thickness
        x, y, r = self.x, self.y, self.radius

        dr = self.hole_dr

        if r > dr:
            r -= dr
        else:
            self.moveTo(dr-r, 0)
            r = 0

        lx = x - 2*r - 2*dr
        ly = y - 2*r - 2*dr

        self.moveTo(0, dr)
        for l in (lx, ly, lx, ly):
            self.edge(l)
            self.corner(90, r)

        if self.top == "lid_with_latches":
            # We end up where we started, so move up further to the
            # centre of the radiused corner
            self.moveTo(0, r)  # Note r=self.radius-dr
            self.screw_slots(lx, ly, 3.3/2)

    @boxes.holeCol
    def screw_slots(self, lx, ly, r):
        """Make four slots with rounded ends, at the four corners.

        These slots allow screws to slide along them, to move the latches
        in and out.
        """
        for l in (lx, ly, lx, ly):
            self.moveTo(0, 0, 45)
            self.moveTo(0, -r)
            self.corner(180, r)
            self.edge(2*self.thickness)
            self.corner(180, r)
            self.edge(2*self.thickness)
            self.moveTo(0, r, -45)
            self.moveTo(l, 0, 90)

    def screw_clearance_slots(self):
        t = self.thickness
        x, y, r = self.x, self.y, self.radius

        self.moveTo(0, r + t)
        self.screw_slots(x - 2*r, y - 2*r, 5)

    def latches(self):
        """Screw holes for tapping on latches"""
        t = self.thickness
        x, y, r = self.x - 4*t, self.y - 4*t, self.radius - 2*t

        # we end up at(r, 0), where the curve joins the edge
        for l in [y-2*r, x-2*r, y-2*r, x-2*r]:
            self.hole(0, r, d=2.5)
            # This will cut a finger out of the corner
            self.moveTo(0, 0, 45)
            self.edge(40)
            self.corner(180, r/sqrt(2))
            self.edge(40)
            self.moveTo(0, 0, -135)
            self.moveTo(l, 0, 180)

    def latch_screw_slots(self):
        """Slots for the screws to slide in"""
        t = self.thickness
        # This will be on the "top" plate with the hole, so it's
        # actually bigger than nominal by t in all directions.
        x, y, r = self.x + 2*t, self.y + 2*t, self.radius + t
        screw_r = 3.3/2

        # we end up at(r, 0), where the curve joins the edge
        for l in [y-2*r, x-2*r, y-2*r, x-2*r]:
            # This will cut a slot, and move from one end of the
            # curve to the other
            self.moveTo(0, r, 45)
            self.moveTo(-2*t, -screw_r)
            self.edge(2*t)
            self.corner(180, screw_r)
            self.edge(2*t)
            self.corner(180, screw_r)
            self.moveTo(0, 0, -45)
            self.moveTo(l, 0, 90)

    def cb(self, nr):
        h = 0.5 * self.thickness

        left, l, right = self.surroundingWallPiece(nr, self.x, self.y, self.radius, self.wallpieces)
        for dh in self.sh[:-1]:
            h += dh
            self.fingerHolesAt(0, h, l, 0)

    def render(self):

        x, y, sh, r = self.x, self.y, self.sh, self.radius

        if self.outside:
            self.x = x = self.adjustSize(x)
            self.y = y = self.adjustSize(y)
            self.sh = sh = self.adjustSize(sh)

        r = self.radius = min(r, y / 2.0)

        t = self.thickness

        h = sum(sh) + t * (len(sh) - 1)
        es = self.edge_style

        corner_holes = True
        if self.edge_style == "f":
            pe = "F"
            ec = False
        elif self.edge_style == "F":
            pe = "f"
            ec = False
        else: # "h"
            pe = "f"
            corner_holes = True
            ec = True

        with self.saved_context():
            # This plate is the base of the box
            self.roundedPlate(x, y, r, es, wallpieces=self.wallpieces,
                              extend_corners=ec, move="right")
            # These are the inner shelves
            for dh in self.sh[:-1]:
                self.roundedPlate(x, y, r, "f", wallpieces=self.wallpieces,
                                  extend_corners=False, move="right")
            # This is the top plate (which has a hole in it, if requested)
            self.roundedPlate(x, y, r, es, wallpieces=self.wallpieces,
                              extend_corners=ec, move="right",
                              callback=[self.top_hole] if self.top != "closed" else None)
            # An additional plate for the lid, if requested
            if self.top in ["lid", "lid_with_latches"]:
                r_extra = self.edges[self.edge_style].spacing()
                self.roundedPlate(x+2*r_extra,
                                  y+2*r_extra,
                                  r+r_extra,
                                  "e", wallpieces=self.wallpieces,
                                  extend_corners=False, move="right",
                                  callback=[self.screw_clearance_slots] if self.top == "lid_with_latches" else None)

            # A plate with the latches.
            if self.top == "lid_with_latches":
                dr = self.hole_dr
                if r < dr:
                    raise ValueError("Latches only work with radius > %f." % dr)
                self.roundedPlate(x - 2*dr, y - 2*dr, r - dr, "e", wallpieces=self.wallpieces,
                                  extend_corners=False, move="right",
                                  callback=[self.latches])

        # I don't know what this plate is for!
        self.roundedPlate(x, y, r, es, wallpieces=self.wallpieces, move="up only")

        # This is the wall (i.e. the vertical part)
        self.surroundingWall(x, y, r, h, pe, pe, pieces=self.wallpieces,
                             callback=self.cb)
