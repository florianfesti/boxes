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
        40.: 32.5,
        60.: 50,
        80.: 71.5,
        92.: 82.5,
        120.: 105,
        140.: 125,
        }
    
    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.DoveTailSettings, size=2.0, depth=1)
        
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
            help="Filters on both sides or only one")
        self.argparser.add_argument(
            "--split_frames",  action="store", type=BoolArg(), default=True,
            help="Split frame pieces into four thin rectangles to save material")
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
        r = self.rim

        def cb():
            if fingerHoles:
                heights = [fh + t/2]
                if self.filters > 1:
                    heights.append(h - fh - t/2)
                for h_ in heights:
                    if self.split_frames:
                        self.fingerHolesAt(0, h_, r, 0)
                        self.fingerHolesAt(r, h_, l-2*r, 0)
                        self.fingerHolesAt(l-r, h_, r, 0)
                    else:
                        self.fingerHolesAt(0, h_, l, 0)

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
        r = self.rim

        y = self.y = y - t # shorten by one thickness as we use the wall space

        fh = self.filter_height
        h = d + 2 + self.filters * (fh + t)

        
        self.rectangularWall(x, d, "ffff", callback=[
            self.fanCB(self.fans_top, d, x, False)], label="top", move="up")
        self.rectangularWall(x, h, "ffff", callback=[
            self.fanCB(self.fans_bottom, h, x)], label="bottom", move="up")

        be = te = edges.CompoundEdge(self, "fff", (r, y - 2*r, r)) \
            if self.split_frames else "f"

        if self.filters==2:
            le = edges.CompoundEdge(self, "EFE", (fh + t, d+2, fh + t))
        else:
            le = edges.CompoundEdge(self, "FE", (d+2, fh + t))
            te = "f"

        for fans in (self.fans_left, self.fans_right):
            self.rectangularWall(y, h, [be, "h", te, le],
                                 callback=[self.fanCB(fans, h, y)], move="up")


        if self.split_frames:
            e = edges.CompoundEdge(self, "DeD", (r, x - 2*r, r))
            for _ in range(self.filters):
                self.rectangularWall(x, r, ["E", "h", e, "h"], move="up")
                self.rectangularWall(y - 2*r, r, "hded", move="up")
                self.rectangularWall(y - 2*r, r, "hded", move="up")
                self.rectangularWall(x, r, [e, "h", "h", "h"], move="up")

                self.rectangularWall(x, r, ["F", "f", e, "f"], move="up")
                self.rectangularWall(y - 2*r, r, "fded", move="up")
                self.rectangularWall(y - 2*r, r, "fded", move="up")
                self.rectangularWall(x, r, [e, "f", "f", "f"], move="up")
        else:
            for _ in range(self.filters):
                self.rectangularWall(x, y, "Ffff", callback=[
                    lambda:self.rectangularHole(x/2, y/2, x - r, y - r, r=10)], move="up")
                self.rectangularWall(x, y, "Ehhh", callback=[
                    lambda:self.rectangularHole(x/2, y/2, x - r, y - r, r=10)], move="up")
        if self.filters==1:
            self.rectangularWall(x, y, "hhhh", move="up")
