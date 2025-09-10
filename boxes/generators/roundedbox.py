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
            "--top",  action="store", type=str, default="hole",
            choices=["hole", "lid", "lid_with_latches", "closed"],
            help="style of the top and lid")
        self.argparser.add_argument(
            "--bottom",  action="store", type=str, default="closed",
            choices=["closed", "hole", "lid", "lid_with_latches"],
            help="style of the top and lid")

    def latch(self, move=None):
        t = self.thickness
        p = .05 * t
        l = 10*t
        if self.move(l, 3*t, move, True):
            return

        r = t / 2**0.5
        self.polyline(l, 90, 1.5*t, 45, 0, (90, r), 0, 45,
                      t, -90, 4*t, 180, 4*t, 90,
                      t-p, 90, 3*t, -90, 2*t+p, 90,
                      3*t, 90, t, 90, t, -90, t+p, -90,
                      3.75*t, 45, t/4*2**0.5, 45, 1.25*t-p, 90)

        self.move(l, 3*t, move)

    def latch_positions(self, x, y, r, callback):
        d = (1-0.5*2**0.5) * r
        for l in (x, y, x, y):
            with self.saved_context():
                self.moveTo(+d, d, -45)
                callback()
            self.moveTo(l+2*r, 0, 90)

    @property
    def hole_dr(self):
        dr = 2*self.thickness
        if self.edge_style == "h":
            dr = self.thickness
        return dr

    def top_hole(self, style):

        if style == "closed":
            return

        t = self.thickness
        p = 0.05*t
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

        if style == "lid_with_latches":
            # We end up where we started
            # go to "corner" of the hole
            self.moveTo(-r)
            self.latch_positions(
                lx, ly, r,
                lambda: (
                    self.rectangularHole(0, 2.5*t, 1.1*t, 4*t, center_y=False),
                    self.rectangularHole(0, 8*t, 1.1*t, 0.7*t),
                    self.rectangularHole(0, 10*t, 1.1*t, 0.7*t)))

    def latches(self):
        t = self.thickness
        x, y, r = self.x, self.y, self.radius
        r_extra = self.edges[self.edge_style].spacing()
        dr = self.hole_dr
        self.moveTo(dr-r, dr+r_extra)

        if r > dr:
            r -= dr
        else:
            r = 0

        lx = x - 2*r - 2*dr
        ly = y - 2*r - 2*dr

        self.latch_positions(
            lx, ly, r,
            lambda: (
                self.rectangularHole(0, 1.5*t, t, 3*t, center_y=False),
                self.rectangularHole(0, 0.5*t,
                                     7*t, 13*t, r=7*t, center_y=False),
                self.hole(0, 9.5*t, d=5*t),
                self.rectangularHole(0, 0.5*t,
                                     7*t, 15*t, r=7*t, center_y=False)))

    def cb(self, nr):
        h = 0.5 * self.thickness

        left, l, right = self.surroundingWallPiece(nr, self.x, self.y, self.radius, self.wallpieces)
        for dh in self.sh[:-1]:
            h += dh
            self.fingerHolesAt(0, h, l, 0)

    def render(self):

        _ = self.translations.gettext
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
            # These are the inner shelves
            for dh in self.sh[:-1]:
                self.roundedPlate(x, y, r, "f", wallpieces=self.wallpieces,
                                  label=_("inner shelf"),
                                  extend_corners=False, move="right")

            for name, style in ((_("bottom"), self.bottom),
                                (_("top"), self.top)):
                # This is the top/bottom plate (which has a hole in it, if requested)
                self.roundedPlate(
                    x, y, r, es, wallpieces=self.wallpieces,
                    extend_corners=ec, move="right",
                    label=name,
                    callback=[lambda: self.top_hole(style)])
                # An additional plate for the lid, if requested
                if style in ["lid", "lid_with_latches"]:
                    r_extra = self.edges[self.edge_style].spacing()
                    self.roundedPlate(
                        x+2*r_extra, y+2*r_extra, r+r_extra,
                        "e", wallpieces=self.wallpieces,
                        label=_("%s lid") % name,
                        extend_corners=False, move="right",
                        callback=[self.latches] if style == "lid_with_latches" else None)

        # Move up one row
        self.roundedPlate(x, y, r, es, wallpieces=self.wallpieces, move="up only")

        # This is the wall (i.e. the vertical part)
        self.surroundingWall(x, y, r, h, pe, pe, pieces=self.wallpieces,
                             callback=self.cb, move="up")
        for style in (self.top, self.bottom):
            if style == "lid_with_latches":
                for i in range(4):
                    self.latch(move="right")
