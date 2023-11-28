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
        self.argparser.add_argument("--x", type=int, default=3, help="number of grids in X direction")
        self.argparser.add_argument("--y", type=int, default=2, help="number of grids in Y direction")
        self.argparser.add_argument("--h", type=float, default=7*3, help="height of sidewalls of the tray (mm)")
        self.argparser.add_argument("--m", type=float, default=0.5, help="Extra margin around the gridfinity base to allow it to drop into the carrier (mm)")
        self.argparser.add_argument(
            "--bottom_edge", action="store",
            type=ArgparseEdgeType("Fhse"), choices=list("Fhse"),
            default='F',
            help="edge type for bottom edge")
        self.argparser.add_argument("--pitch", type=int, default=42, help="The Gridfinity pitch, in mm.  Should always be 42.")
        self.argparser.add_argument("--opening", type=int, default=38, help="The cutout for each grid opening.  Typical is 38.")

    def generate_grid(self):
        pitch = self.pitch
        nx, ny = self.x, self.y
        opening = self.opening
        for col in range(nx):
            for row in range(ny):
                lx = col*pitch+pitch/2
                ly = row*pitch+pitch/2
                self.rectangularHole(lx, ly, opening, opening)
        
    def create_base_plate(self):
        pitch = self.pitch
        nx, ny = self.x, self.y
        opening = self.opening
        self.rectangularWall(nx*pitch, ny*pitch, move="up", callback=[self.generate_grid])
        return

    def create_tray(self):
        pitch = self.pitch
        nx, ny = self.x, self.y
        margin = self.m
        x, y, h = nx*pitch, ny*pitch, self.h
        t = self.thickness
        x += 2*margin
        y += 2*margin
        t1, t2, t3, t4 = "eeee"
        b = self.edges.get(self.bottom_edge, self.edges["F"])
        sideedge = "F" # if self.vertical_edges == "finger joints" else "h"

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

        return

    def render(self):
        self.create_base_plate()
        self.create_tray()
        self.lid(self.x*self.pitch + 2*self.m,
                 self.y*self.pitch + 2*self.m)
