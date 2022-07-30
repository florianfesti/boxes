#!/usr/bin/env python3
# Copyright (C) 2013-2021 Florian Festi
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


class CardHolder(Boxes):
    """Shelf for holding (multiple) piles of playing cards / notes"""

    ui_group = "Shelf"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.GroovedSettings)
        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=1.0)

        self.buildArgParser(sx="68*3", y=100, h=40, outside=False)
        self.argparser.add_argument(
            "--angle", action="store", type=float, default=7.5,
            help="backward angle of floor")
        self.argparser.add_argument(
            "--stackable", action="store", type=boolarg, default=True,
            help="make holders stackable")

    def side(self):
        t = self.thickness
        a = math.radians(self.angle)

        pos_y = self.y - abs(0.5 * t * math.sin(a))
        pos_h = t - math.cos(a) * 0.5 * t
        self.fingerHolesAt(pos_y, pos_h, self.y, 180-self.angle)

    def fingerHoleCB(self, length, posy=0.0):
        def CB():
            t = self.thickness
            px = -0.5 * t
            for x in self.sx[:-1]:
                px += x + t
                self.fingerHolesAt(px, posy, length, 90)
        return CB

    def middleWall(self, move=None):
        y, h = self.y , self.h
        a = self.angle
        t = self.thickness
        tw = y + t
        th = h

        if self.move(tw, th, move, True):
            return

        self.moveTo(t, t, a)

        self.edges["f"](y)
        self.polyline(0, 90-a, h-t-y*math.sin(math.radians(a)), 90,
                      y*math.cos(math.radians(a)), 90)
        self.edges["f"](h-t)

        self.move(tw, th, move)

    def render(self):
        sx, y = self.sx, self.y
        t = self.thickness

        bottom = "š" if self.stackable else "e"
        top = "S" if self.stackable else "e"

        if self.outside:
            self.sx = sx = self.adjustSize(sx)
            h = self.h = self.adjustSize(self.h, bottom, top)
        else:
            h = self.h = self.h + t + y * math.sin(math.radians(self.angle))
        self.x = x = sum(sx) + t * (len(sx) - 1)

        self.rectangularWall(y, h, [bottom, "F", top, "e"],
                             ignore_widths=[1, 6],
                             callback=[self.side], move="up")
        self.rectangularWall(y, h, [bottom, "F", top, "e"],
                             ignore_widths=[1, 6],
                             callback=[self.side], move="up mirror")

        nx = len(sx)
        f_lengths = []
        for val in self.sx:
            f_lengths.append(val)
            f_lengths.append(t)
        f_lengths = f_lengths[:-1]

        frontedge = edges.CompoundEdge(
            self, "e".join("z" * nx), f_lengths)

        self.rectangularWall(x, y, [frontedge, "f", "e", "f"],
                             callback=[self.fingerHoleCB(y)], move="up")
        self.rectangularWall(x, h, bottom + "f"  + top + "f",
                             ignore_widths=[1, 6],
                             callback=[self.fingerHoleCB(h-t, t)], move="up")
        for i in range(nx-1):
            self.middleWall(move="right")
