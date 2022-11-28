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

class DisplayShelf(Boxes): # change class name here and below
    """Shelf with slanted floors"""

    ui_group = "Shelf"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)

        #self.buildArgParser(x=400, y=100, h=300, outside=True)
        self.buildArgParser(x=140, y=215, h=215, outside=False)
        self.argparser.add_argument(
            "--num",  action="store", type=int, default=1,
            help="number of shelves")
        self.argparser.add_argument(
            "--frontWallHeight",  action="store", type=float, default=50.0,
            help="height of front walls")
        self.argparser.add_argument(
            "--angle",  action="store", type=float, default=45.0,
            help="angle of floors (negative values for slanting backwards)")
        self.argparser.add_argument(
            "--include_back", action="store", type=boolarg, default=False,
            help="Include panel on the back of the shelf")
        self.argparser.add_argument(
            "--slope_top", action="store", type=boolarg, default=True,
            help="Slope the sides a the top by front wall height")

    def side(self):

        t = self.thickness
        a = math.radians(self.angle)

        hs = (self.sl+t) * math.sin(a) + math.cos(a) * t

        for i in range(self.num):
            pos_x = abs(0.5*t*math.sin(a))
            pos_y = hs - math.cos(a)*0.5*t + i * (self.h-hs) / (self.num - 0.5)
            self.fingerHolesAt(pos_x, pos_y, self.sl, -self.angle)
            pos_x += math.cos(-a) * (self.sl+0.5*t) + math.sin(a)*0.5*t
            pos_y += math.sin(-a) * (self.sl+0.5*t) + math.cos(a)*0.5*t
            self.fingerHolesAt(pos_x, pos_y, self.frontWallHeight, 90-self.angle)

    def generate_sides(self, width, height):

        if self.slope_top:
            a = math.radians(self.angle)
            lip_height = self.frontWallHeight * math.cos(a)
            hypotenuse = (height - lip_height) / math.sin(a)
            top_width = width - math.sqrt((hypotenuse ** 2) - ((height - lip_height) * 2))

            borders = [width, 90, lip_height, self.angle, hypotenuse, -135, top_width, -90, height, 90]

            self.polygonWall(borders, edge='e', callback=[self.side], move="up")
            self.polygonWall(borders, edge='e', callback=[self.side], move="up")
        else:
            edges = "eeee"
            if self.include_back:
                edges = "eeeF"
            self.rectangularWall(width, height, edges, callback=[self.side], move="up", label="left side")
            self.rectangularWall(width, height, edges, callback=[self.side], move="up", label="right side")

    def generate_shelves(self):
        if self.frontWallHeight:
            for i in range(self.num):
                self.rectangularWall(self.x, self.sl, "ffef", move="up", label="shelf")
                self.rectangularWall(self.x, self.frontWallHeight, "Ffef", move="up", label="front lip")
        else:
            for i in range(self.num):
                self.rectangularWall(self.x, self.sl, "Efef", move="up", label="shelf")

    def render(self):
        # adjust to the variables you want in the local scope
        x, y, h = self.x, self.y, self.h
        front = self.frontWallHeight
        thickness = self.thickness

        if self.outside:
            x = self.adjustSize(x)

        a = math.radians(self.angle)

        self.sl = (y - (thickness * (math.cos(a) + abs(math.sin(a)))) - max(0, math.sin(a) * front)) / math.cos(a)

        # render your parts here
        self.generate_sides(y, h)
        self.generate_shelves()

        if self.include_back:
            self.rectangularWall(x, h, "efef", label="back wall", move="up")
