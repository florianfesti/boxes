#!/usr/bin/env python3
# Copyright (C) 2020  Luca Schmid
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
from math import sqrt

class MarbleSlide(Boxes):
    """Generate a simple slide for marbles"""

    ui_group = "Unstable"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=1.0, finger=2.0, space=2.0)

        self.buildArgParser(x=200, y=28, h=15, outside=True)
        self.argparser.add_argument('--grid', type=float, default=15.0, help="grid spacing")


    def calcNotchDimensions(self):
        dh = sqrt(self.thickness**2/2)
        h = (self.h if self.outside else self.h+self.thickness*2) / 5 * 3
        return dh, h


    def rectangularWallWithNotch(self, x, y, edges="eeee", move=None):
        """
        Rectangular wall with notch

        :param x: width
        :param y: height
        :param edges:  (Default value = "eeee") bottom, right, top, left
        :param move:  (Default value = None)

        """
        if len(edges) != 4:
            raise ValueError("four edges required")
        edges = [self.edges.get(e, e) for e in edges]

        overallwidth = x + edges[-1].spacing() + edges[1].spacing()
        overallheight = y + edges[0].spacing() + edges[2].spacing()
        dh, h = self.calcNotchDimensions()

        if self.move(overallwidth, overallheight, move, before=True):
            return

        self.moveTo(edges[-1].spacing())
        self.moveTo(0, edges[0].margin())
        for i, l in enumerate((x, y, x, y)):
            e1, e2 = edges[i], edges[(i+1)%4]

            if i == 0:
                self.edge(self.thickness+dh)
                self.corner(90)
                self.edge(h-2*dh)
                self.corner(45)
                self.edge(self.thickness)
                self.corner(-90)
                self.edge(self.thickness)
                self.corner(-45)
                self.edge(self.thickness)
                self.corner(-90)
                self.edge(self.thickness)
                self.corner(45)
                self.edge(sqrt((h-self.thickness)**2*2))
                self.corner(45)
                edges[i](l-(self.thickness+dh+h))
            elif i == 3:
                edges[i](l+self.thickness*2)
            else:
                edges[i](l)
            self.edgeCorner(e1, self.edges['e'] if i == 3 else e2, 90)

        self.move(overallwidth, overallheight, move)


    def render(self):
        x, y, h, grid = self.x, self.y, self.h, self.grid
        ho = h + self.thickness*2

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            ho = h
            h = self.adjustSize(h)

        dh, nh = self.calcNotchDimensions()

        self.rectangularWall(x-(self.thickness+dh+nh), y, 'fefe', move='down')
        self.rectangularWall(y, ho, 'efef', move='down')
        self.rectangularWallWithNotch(x, h, 'heeh', move='down')
        self.rectangularWallWithNotch(x, h, 'heeh', move='down mirror')


