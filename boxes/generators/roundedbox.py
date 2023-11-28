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
            "--top",  action="store", type=str, default="none",
            choices=["closed", "hole", "lid",],
            help="style of the top and lid")

    def hole(self):
        t = self.thickness
        x, y, r = self.x, self.y, self.radius

        dr = 2*t
        if self.edge_style == "h":
            dr = t

        if r > dr:
            r -= dr
        else:
            x += dr - 2*r
            y += dr - 2*r
            self.moveTo(dr-r, 0)
            r = 0

        lx = x - 2*r - 2*dr
        ly = y - 2*r - 2*dr

        self.moveTo(0, dr)
        for l in (lx, ly, lx, ly):
            self.edge(l)
            self.corner(90, r)

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
            self.roundedPlate(x, y, r, es, wallpieces=self.wallpieces,
                              extend_corners=ec, move="right")
            for dh in self.sh[:-1]:
                self.roundedPlate(x, y, r, "f", wallpieces=self.wallpieces,
                                  extend_corners=False, move="right")
            self.roundedPlate(x, y, r, es, wallpieces=self.wallpieces,
                              extend_corners=ec, move="right",
                              callback=[self.hole] if self.top != "closed" else None)
            if self.top == "lid":
                r_extra = self.edges[self.edge_style].spacing()
                self.roundedPlate(x+2*r_extra,
                                  y+2*r_extra,
                                  r+r_extra,
                                  "e", wallpieces=self.wallpieces,
                                  extend_corners=False, move="right")

        self.roundedPlate(x, y, r, es, wallpieces=self.wallpieces, move="up only")

        self.surroundingWall(x, y, r, h, pe, pe, pieces=self.wallpieces,
                             callback=self.cb)


