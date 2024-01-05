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

class PizzaShovel(Boxes):
    """Pizza shovel with conveyor belt action"""

    description = """
You need (permanent) baking paper to create the conveyor. With that you can pick up and put down the pizza by moving the handle attached to the belt.
    """
    
    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.HandleEdgeSettings, outset=0.0, height=40, hole_width="30:30:30")
        self.buildArgParser(x=382, y=400)
        self.argparser.add_argument(
            "--grip_length",  action="store", type=float, default=250.0,
            help="Length of the grip. Zero for holes for a screw-in handle")
        self.argparser.add_argument(
            "--grip_height",  action="store", type=float, default=30.0,
            help="Height of the grip. Distance between the cross beams.")
        self.argparser.add_argument(
            "--top_holes",  action="store", type=float, default=3.0,
            help="Diameter of the screw holes in the bottom of the pusher - where the screws pass through")
        self.argparser.add_argument(
            "--bottom_holes",  action="store", type=float, default=2.0,
            help="Diameter of the screw holes in the bottom of the pusher - where the screws hold")
        self.argparser.add_argument(
            "--grip_holes",  action="store", type=float, default=3.0,
            help="Diameter of the screw holes for zero griplength")

    def holesCB(self, d):
        def cb():
            for i in range(5):
                self.hole((self.x-3)/5 * (i+0.5), 20, d=d)
        return cb

    def gripCB(self, top):

        def cb():
            t = self.thickness
            if self.grip_length:
                for d in (-t, +t):
                    self.fingerHolesAt(self.x/2 + d, 0, 40, 90)
            else:
                for y in ((10, 30) if top else (15, 35, 60)):
                    self.hole(self.x/2, y, d=self.grip_holes)
        return cb

    def render(self):
        x, y, h = self.x, self.y, self.grip_height
        grip = self.grip_length
        t = self.thickness

        ce = edges.CompoundEdge(self, "fe", [y/2, y/2])
        ec = edges.CompoundEdge(self, "ef", [y/2, y/2])
        
        self.rectangularWall(x, y, ["e", ce, "e", ec], move="up")
        self.rectangularWall(x, 40, "efef", callback=[self.gripCB(top=True)], move="up")
        self.rectangularWall(x, 80, "efef", callback=[self.gripCB(top=False)], move="up")
        for i in range(2):
            a = math.atan((h+2*t) / (y/2 - 30))
            l = (y/2 - 30) / math.cos(a)
            a = math.degrees(a)
            self.polygonWall((y/2+40, (90, t), h+2*t, (90, t), 70, a, l, -a, 0, (180, t)), "e",
                             callback=[lambda: (self.fingerHolesAt(0, 1.5*t, y/2, 0),
                                                self.fingerHolesAt(y/2+t, 1.5*t, 40, 0)),
                                       None,
                                       lambda: self.fingerHolesAt(-t, 1.5*t, 80, 0)],
                             move="up")

        self.rectangularWall(x-3, 40, "eeee", callback=[self.holesCB(self.bottom_holes)], move="up")
        self.rectangularWall(x-3, 40, "yeee", callback=[self.holesCB(self.top_holes)], move="up")

        if grip:
            ce1 = edges.CompoundEdge(self, "fe", (40, grip-h/2))
            ce2 = edges.CompoundEdge(self, "ef", (grip-h/2, 40))
            self.flangedWall(40+grip-h/2, h, [ce1, "e", ce2,  "e"], flanges=[0, h/2], r=h/2, move="up")
            self.flangedWall(40+grip-h/2, h, "eeee", flanges=[0, h/2], r=h/2, move="up")
            self.flangedWall(40+grip-h/2, h, [ce1, "e", ce2,  "e"], flanges=[0, h/2], r=h/2, move="up")
            self.flangedWall(30+grip-h/2, h-2*t, "eeee", flanges=[0, h/2-t], r=h/2-t, move="up")
            self.flangedWall(30+grip-h/2, h-2*t, "eeee", flanges=[0, h/2-t], r=h/2-t, move="up")
