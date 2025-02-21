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
import math

from boxes import *
from boxes import lids


class GridfinityBase(Boxes):
    """A parameterized Gridfinity base"""

    description = """This is a configurable gridfinity base.  This
    design is based on
    <a href="https://www.youtube.com/watch?app=desktop&v=ra_9zU-mnl8">Zach Freedman's Gridfinity system</a>"""

    ui_group = "Tray"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings, space=4, finger=4)
        self.addSettingsArgs(lids.LidSettings)
        self.argparser.add_argument("--sx", type=int, default=0, help="size of base in X direction (0=auto)")
        self.argparser.add_argument("--sy", type=int, default=0, help="size of base in Y direction (0=auto)")
        self.argparser.add_argument("--x", type=int, default=3, help="number of grids in X direction (0=auto)")
        self.argparser.add_argument("--y", type=int, default=2, help="number of grids in Y direction (0=auto)")
        self.argparser.add_argument("--h", type=float, default=7*3, help="height of sidewalls of the tray (mm)")
        self.argparser.add_argument("--m", type=float, default=0.5, help="Extra margin around the gridfinity base to allow it to drop into the carrier (mm)")
        self.argparser.add_argument(
            "--bottom_edge", action="store",
            type=ArgparseEdgeType("Fhse"), choices=list("Fhse"),
            default='F',
            help="edge type for bottom edge")
        self.argparser.add_argument("--pitch", type=int, default=42, help="The Gridfinity pitch, in mm.  Should always be 42.")
        self.argparser.add_argument("--opening", type=int, default=38, help="The cutout for each grid opening.  Typical is 38.")
        self.argparser.add_argument("--radius", type=float, default=1.6, help="The corner radius for each grid opening.  Typical is 1.6.")
        self.argparser.add_argument("--cut_pads", type=boolarg, default=False, help="cut pads to be used for gridinity boxes from the grid openings")
        self.argparser.add_argument("--pad-radius", type=float, default=0.8, help="The corner radius for each grid opening.  Typical is 0.8,")
        

    def generate_grid(self):
        radius, pad_radius = self.radius, self.pad_radius
        pitch = self.pitch
        opening = self.opening
        padx = self.sx - (self.x * pitch)
        pady = self.sy - (self.y * pitch)

        for col in range(self.x):
            for row in range(self.y):
                lx = col*pitch+pitch/2+int(padx/2)
                ly = row*pitch+pitch/2+math.ceil(pady/2)
                self.rectangularHole(lx, ly, opening, opening, r=radius)
                if self.cut_pads:
                    self.rectangularHole(lx, ly, opening - 2, opening - 2, r=pad_radius)

    def render(self):
        if self.x == 0 and self.sx == 0:
            raise ValueError('either --sx or --x must be provided')
        if self.y == 0 and self.sy == 0:
            raise ValueError('either --sy or --y must be provided')

        if self.sx == 0:
            # if we are producting a minimally sized base sx will be zero
            self.sx = self.x*self.pitch
        else:
            if self.x == 0:
                # if we are producing an automatically determined maximum
                # number of grid cols self.x will be zero
                self.x = int(self.sx / self.pitch)
            # if both sx and x were provided, x takes precedence
            self.sx = max(self.sx, self.x*self.pitch)

        if self.sy == 0:
            # if we are producting a minimally sized base sy will be zero
            self.sy = self.y*self.pitch
        else:
            if self.y == 0:
                # if we are producing an automatically determined maximum
                # number of grid rows self.y will be zero
                self.y = int(self.sy / self.pitch)
            # if both sy and y were provided, y takes precedence
            self.sy = max(self.sy, self.y*self.pitch)

        pitch = self.pitch
        x, y = self.sx, self.sy
        nx, ny = self.x, self.y
        opening = self.opening
        margin = self.m

        h = self.h
        t = self.thickness
        x += 2*margin
        y += 2*margin
        t1, t2, t3, t4 = "eeee"
        b = self.edges.get(self.bottom_edge, self.edges["F"])
        sideedge = "F" # if self.vertical_edges == "finger joints" else "h"

        self.rectangularWall(x, y, move="up", callback=[self.generate_grid])

        if h > 0:
            self.rectangularWall(x, h, [b, sideedge, t1, sideedge],
                                ignore_widths=[1, 6], move="right")
            self.rectangularWall(y, h, [b, "f", t2, "f"],
                                ignore_widths=[1, 6], move="up")
            self.rectangularWall(y, h, [b, "f", t4, "f"],
                                ignore_widths=[1, 6], move="")
            self.rectangularWall(x, h, [b, sideedge, t3, sideedge],
                                ignore_widths=[1, 6], move="left up")

            if self.bottom_edge != "e":
                self.rectangularWall(x, y, "ffff", move="up")

        self.lid(x, y)
