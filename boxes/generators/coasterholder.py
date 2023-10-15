#!/usr/bin/env python3
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
from boxes.lids import LidSettings


class CoasterHolder(Boxes):
    """A coaste holder"""

    description = "This is a coaster holder"

    ui_group = "Box"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.buildArgParser(x=102, y=102, h=35)
        self.argparser.add_argument(
            "--opening", action="store", type=float, default=40,
            help="percent of front that's open")
        self.argparser.add_argument(
            "--bottom_radius", action="store", type=float, default=5,
            help="radius of the bottom corners")
        self.argparser.add_argument(
            "--short_wall_radius", action="store", type=float, default=10,
            help="radius of the short wall corner")
        self.argparser.add_argument(
            "--flange_out", action="store", type=float, default=5,
            help="size of the over flange")

    def bottomWall(self, x, y, o, flange=5.0, r=10.0, callback=None, move=None, label=""):
        rl = min(r, flange)

        if self.move(x+2*flange+2*self.thickness, y+2*flange+2*self.thickness, move, before=True):
            return

        # bottom desk
        with self.saved_context():
            self.moveTo(rl, 0)
            self.edge(x + (flange-rl)*2 + self.thickness*2)
            self.corner(90, rl)
            self.edge(y + (flange-rl)*2 + self.thickness*2)
            self.corner(90, rl)
            self.edge(x + (flange - rl) * 2 + self.thickness*2)
            self.corner(90, rl)
            self.edge(y + (flange - rl) * 2 + self.thickness*2)
            self.corner(90, rl)

        self.moveTo(self.thickness*0.5+flange, self.thickness*0.5+flange)
        d = x * (1 - o / 100) / 2
        # bottom short holes
        self.fingerHolesAt(self.thickness*0.5, 0, d, 0)
        self.fingerHolesAt(x - d + self.thickness*0.5, 0, d, 0)
        # right holes
        self.fingerHolesAt(x+self.thickness, self.thickness*0.5, y, 90)
        # left holes
        self.fingerHolesAt(0, y+0.5*self.thickness, y, 270)
        # top short holes
        self.fingerHolesAt(x+self.thickness*0.5, y+self.thickness, d, 180)
        self.fingerHolesAt(d+self.thickness*0.5, y+self.thickness, d, 180)

        self.move(x+2*flange+2*self.thickness, y+2*flange+2*self.thickness, move, label=label)



    def shorterWall(self, x, h, o, r=2.0, callback=None, move=None, label=""):
        sl = x * (1 - o / 100) / 2
        rl = min(r, max(sl, h))

        if self.move(sl+self.thickness, h+self.thickness, move, before=True):
            return
        self.moveTo(self.thickness,self.thickness)
        self.edges["f"](sl)
        self.corner(90)
        self.edges["e"](h-rl-self.burn)
        self.corner(90, rl)
        self.edges["e"](sl-rl-self.burn)
        self.corner(90)
        self.edges["f"](h)

        self.move(sl + self.thickness, h + self.thickness, move, label=label)

    def render(self):
        x, y, h = self.x, self.y, self.h
        r_out = self.bottom_radius
        r_wall = self.short_wall_radius
        flange_out = self.flange_out
        o = self.opening

        self.bottomWall(x, y, o, flange_out, r_out)
        self.bottomWall(x, y, o, flange_out, r_out, move="right only")

        self.rectangularWall(y, h, ["f", "F", "e", "F"],
                             ignore_widths=[1, 6], move="up")
        self.rectangularWall(y, h, ["f", "F", "e", "F"], ignore_widths=[1, 6], move="up")

        self.shorterWall(x, h, o, r_wall, move="right")
        self.shorterWall(x, h, o, r_wall, move="right mirror")

        self.shorterWall(x, h, o, r_wall, move="right")
        self.shorterWall(x, h, o, r_wall, move="right mirror")
