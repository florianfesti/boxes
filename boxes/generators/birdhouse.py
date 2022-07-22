#!/usr/bin/env python3
# Copyright (C) 2013-2022 Florian Festi
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

class BirdHouse(Boxes):
    """Simple Bird House"""

    ui_group = "Unstable" # "Misc"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, finger=10.0,space=10.0)

        # remove cli params you do not need
        self.buildArgParser(x=200, y=200, h=200)

    def side(self, x, h, edges="hfeffef", callback=None, move=None):
        angles = (90, 0, 45, 90, 45, 0, 90)
        roof = 2**0.5 * x / 2
        t = self.thickness
        lengths = (x, h, t, roof, roof, t, h)

        edges = [self.edges.get(e, e) for e in edges]
        edges.append(edges[0]) # wrap arround

        tw = x + edges[1].spacing() + edges[-2].spacing()
        th = h + x/2 + t + edges[0].spacing() + max(edges[3].spacing(), edges[4].spacing())

        if self.move(tw, th, move, True):
            return

        self.moveTo(edges[-2].spacing())
        for i in range(7):
            self.cc(callback, i, y=self.burn+edges[i].startwidth())
            edges[i](lengths[i])
            self.edgeCorner(edges[i], edges[i+1], angles[i])            
        
        self.move(tw, th, move)

    def side_hole(self, width):
        self.rectangularHole(width/2, self.h/2,
                             0.75*width, 0.75*self.h,
                             r=self.thickness)

    def render(self):
        x, y, h = self.x, self.y, self.h

        roof = 2**0.5 * x / 2

        cbx = [lambda: self.side_hole(x)]
        cby = [lambda: self.side_hole(y)]
        
        self.side(x, h, callback=cbx, move="right")
        self.side(x, h, callback=cbx, move="right")
        self.rectangularWall(y, h, "hFeF", callback=cby, move="right")
        self.rectangularWall(y, h, "hFeF", callback=cby, move="right")
        self.rectangularWall(x, y, "ffff", move="right")
        self.edges["h"].settings.setValues(self.thickness, relative=False, edge_width=0.1*roof)
        self.flangedWall(y, roof, "ehfh", r=0.2*roof, flanges=[0.2*roof], move="right")
        self.flangedWall(y, roof, "ehFh", r=0.2*roof, flanges=[0.2*roof], move="right")
