#!/usr/bin/env python3
# Copyright (C) 2013-2016 Florian Festi
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

class AirPurifier(Boxes):
    """Housing for the Nukit Open Air Purifier"""

    ui_group = "Unstable" # see ./__init__.py for names

    description = """Still untested"""

    fan_holes = {
        40: 32.5,
        60: 50,
        80: 71.5,
        92: 82.5,
        120: 105,
        140: 125,
        }
    
    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        
        self.buildArgParser(x=498., y=496.)

        self.argparser.add_argument(
            "--filter_height",  action="store", type=float, default=46.77,
            help="height of the filter along the flow direction (in mm)")
        self.argparser.add_argument(
            "--rim",  action="store", type=float, default=30.,
            help="rim around the filter holing it in place (in mm)")
        self.argparser.add_argument(
            "--fan_diameter",  action="store", type=float, default=140.,
            choices=list(self.fan_holes.keys()),
            help="diameter of the fans (in mm)")
        self.argparser.add_argument(
            "--filters",  action="store", type=int, default=2,
            choices=(1, 2),
            help="")
        self.argparser.add_argument(
            "--fans_left",  action="store", type=int, default=-1,
            help="number of fans on the left side (-1 for maximal number)")
        self.argparser.add_argument(
            "--fans_right",  action="store", type=int, default=-1,
            help="number of fans on the right side (-1 for maximal number)")
        self.argparser.add_argument(
            "--fans_top",  action="store", type=int, default=0,
            help="number of fans on the top side (-1 for maximal number)")
        self.argparser.add_argument(
            "--fans_bottom",  action="store", type=int, default=0,
            help="number of fans on the bottom side (-1 for maximal number)")
        self.argparser.add_argument(
            "--screw_holes",  action="store", type=float, default=5.,
            help="diameter of the holes for screwing in the fans (in mm)")

    def fanCB(self, n, h, l, fingerHoles=True):
        fh = self.filter_height
        t = self.thickness

        def cb():
            if fingerHoles:
                self.fingerHolesAt(0, fh + t/2, l, 0)
                if self.filters > 1:
                    self.fingerHolesAt(0, h- fh - t/2, l, 0)

            max_n = int((l-20) // (self.fan_diameter + 10))
            if n == -1:
                n_ = max_n
            else:
                n_ = min(max_n, n)

            if n_ == 0:
                return
            w = (l-20) / n_
            x = 10 + w / 2
            delta = self.fan_holes[self.fan_diameter] / 2
            if self.filters==2:
                posy = h / 2
            else:
                posy = (h + t + fh)  / 2

            for i in range(n_):
                posx = x+i*w
                self.hole(posx, posy, d=self.fan_diameter-4)
                for dx in [-delta, delta]:
                    for dy in [-delta, delta]:
                        self.hole(posx + dx, posy + dy, d=self.screw_holes)

        return cb

    def render(self):
        x, y, d = self.x, self.y, self.fan_diameter
        t = self.thickness

        fh = self.filter_height
        h = d + 2 + self.filters * (fh + t)

        if self.filters==2:
            edge = edges.CompoundEdge(self, "eFe", (fh + t, d+2, fh + t))
        else:
            edge = edges.CompoundEdge(self, "Fe", (d+2, fh + t))
        
        self.rectangularWall(x, d, "ffff", callback=[
            self.fanCB(self.fans_top, d, x, False)], label="top", move="up")
        self.rectangularWall(x, h, "ffff", callback=[
            self.fanCB(self.fans_bottom, h, x)], label="bottom", move="up")

        for fans in (self.fans_left, self.fans_right):
            self.rectangularWall(y, h, ["f", "h", "f", edge],
                                 callback=[self.fanCB(fans, h, y)], move="up")

        r = self.rim
        self.rectangularWall(x, y, "ehhh", callback=[
            lambda:self.rectangularHole(x/2, y/2, x - r, y - r, r=10)], move="up")
        self.rectangularWall(x, y, "Ffff", callback=[
            lambda:self.rectangularHole(x/2, y/2, x - r, y - r, r=10)], move="up")
        if self.filters==2:
            self.rectangularWall(x, y, "Ffff", callback=[
                lambda:self.rectangularHole(x/2, y/2, x - r, y - r, r=10)], move="up")
            self.rectangularWall(x, y, "ehhh", callback=[
                lambda:self.rectangularHole(x/2, y/2, x - r, y - r, r=10)], move="up")
        else:
            self.rectangularWall(x, y, "ehhh", move="up")
