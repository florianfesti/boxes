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
import math

class ShadyEdge(edges.BaseEdge):
    char = "s"

    def __call__(self, lenght, **kw):
        s = self.shades
        h = self.h
        a = math.atan(s/h)
        angle = math.degrees(a)
        for i in range(self.n):
            self.polyline(0, -angle, h / math.cos(a), angle+90)
            self.edges["f"](s)
            self.corner(-90)
            if i < self.n-1:
                self.edge(self.thickness)

    def margin(self):
        return self.shades

class TrafficLight(Boxes): # change class name here and below
    """Traffic light"""
    
    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)

        # remove cli params you do not need
        self.buildArgParser("h")
        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--depth",  action="store", type=float, default=100,
            help="inner depth not including the shades")
        self.argparser.add_argument(
            "--shades",  action="store", type=float, default=50,
            help="depth of the shaders")
        self.argparser.add_argument(
            "--n",  action="store", type=int, default=3,
            help="number of lights")
        self.argparser.add_argument(
            "--upright",  action="store", type=boolarg, default=True,
            help="stack lights upright (or side by side)")

    def backCB(self):
        t = self.thickness
        for i in range(1, self.n):
            self.fingerHolesAt(i*(self.h+t)-0.5*t, 0, self.h)

    def sideCB(self):
        t = self.thickness
        for i in range(1, self.n):
            self.fingerHolesAt(i*(self.h+t)-0.5*t, 0, self.depth)
        for i in range(self.n):
            self.fingerHolesAt(i*(self.h+t), self.depth-2*t, self.h, 0)

    def topCB(self):
        t = self.thickness
        for i in range(1, self.n):
            self.fingerHolesAt(i*(self.h+t)-0.5*t, 0, self.depth + self.shades)
        for i in range(self.n):
            self.fingerHolesAt(i*(self.h+t), self.depth-2*t, self.h, 0)

    def frontCB(self):
        self.hole(self.h/2, self.h/2, self.h/2-self.thickness)

    def wall(self, h1, h2, w, edges="ffef", callback=None, move=""):
        edges = [self.edges.get(e, e) for e in edges]
        edges += edges  # append for wrapping around
        overallwidth = w + edges[-1].spacing() + edges[1].spacing()
        overallheight = max(h1, h2) + edges[0].spacing() + edges[2].spacing()

        if self.move(overallwidth, overallheight, move, before=True):
            return

        a = math.atan((h2-h1)/float(w))
        angle = math.degrees(a)

        self.moveTo(edges[-1].spacing(), edges[0].margin())
        for i, l in [(0, w), (1, h2)]:
            self.cc(callback, i, y=edges[i].startwidth() + self.burn)
            edges[i](l)
            self.edgeCorner(edges[i], edges[i + 1], 90)

        self.corner(angle)
        self.cc(callback, i, y=edges[2].startwidth() + self.burn)
        edges[2](w / math.cos(a))
        self.corner(-angle)
        self.edgeCorner(edges[2], edges[2 + 1], 90)
        self.cc(callback, i, y=edges[3].startwidth() + self.burn)
        edges[3](h1)
        self.edgeCorner(edges[3], edges[3 + 1], 90)

        self.ctx.stroke()

        self.move(overallwidth, overallheight, move)
    
    def render(self):
        # adjust to the variables you want in the local scope
        d, h, n = self.depth, self.h, self.n
        s = self.shades
        t = self.thickness

        th = n * (h + t) - t
        
        # Initialize canvas
        self.open()

        self.addPart(ShadyEdge(self, None))

        # back
        self.rectangularWall(th, h, "FFFF", callback=[self.backCB], move="up")

        if self.upright:
            # sides
            self.rectangularWall(th, d, "fFsF", callback=[self.sideCB], move="up")
            self.rectangularWall(th, d, "fFsF", callback=[self.sideCB], move="up")

            # horizontal Walls / blinds tops
            e = edges.CompoundEdge(self, "fF", (d, s))
            e2 = edges.CompoundEdge(self, "Ff", (s, d))
            for i in range(n):
                self.rectangularWall(h, d+s, ['f', e, 'e', e2],
                                     move="right" if i<n-1 else "right up")
        else:
            # bottom
            self.rectangularWall(th, d, "fFeF", callback=[self.sideCB],
                                 move="up")
            # top
            self.rectangularWall(th, d+s, "fFeF", callback=[self.topCB],
                                 move="up")
            # vertical walls
            for i in range(n):
                self.wall(d, d+s, h, move="right" if i<n-1 else "right up")

        # fronts
        for i in range(n):
            self.rectangularWall(h, h, "efef", callback=[self.frontCB],
                                 move="left" if i<n-1 else "left up")

        if self.upright:
            # bottom wall
            self.rectangularWall(h, d, "ffef", move="up")
        else:
            # vertical wall
            self.wall(d, d+s, h, move="up")

        # Colored windows
        for i in range(n):
            self.parts.disc(h-2*t, move="right")
        
        self.close()

def main():
    b = TrafficLight() # change to class name
    b.parseArgs()
    b.render()

if __name__ == '__main__':
    main()
