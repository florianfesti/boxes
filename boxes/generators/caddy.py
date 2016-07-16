#!/usr/bin/python3
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


class RoundedTriangleEdgeSettings(edges.Settings):
    absolute_params = {
        "height" : 100,
        "radius" : 20,
        "r_hole" : None,
        }

class RoundedTriangleEdge(edges.Edge):
    """Makes an 'edge' with a rounded triangular bumpout and
       optional hole"""
    char = "q"
    def __call__(self, length, **kw):
        angle = math.degrees(math.atan(2*self.settings.height/length))
        r = self.settings.radius
        l = 0.5 * (length-2*r) / math.cos(math.radians(angle))

        self.corner(-90)
        if self.settings.r_hole:
            x = self.settings.height - 2*self.settings.radius
            y = 0.5 * (length)
            self.hole(x, y, self.settings.r_hole)
        self.corner(90-angle, r)
        self.edge(l)
        self.corner(2*angle, r)
        self.edge(l)
        self.corner(90-angle, r)
        self.corner(-90)

    def margin(self):
        return self.boxes.spacing + self.boxes.thickness + self.settings.height


class Box(Boxes):
    """An open box with two special 'house shaped' sides to make 6-pack 
       style caddy. A dowel through the sides makes a handle"""
    def __init__(self):
        Boxes.__init__(self)
        #TODO: Get hole, rounding radius and angle from command line
        self.buildArgParser("x", "y", "h", "outside")
        self.argparser.set_defaults(
            fingerjointfinger=3.0,
            fingerjointspace=3.0
            )

    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            h = self.adjustSize(h)

        self.open()

        s = RoundedTriangleEdgeSettings(self.thickness, height=100, r_hole=6)
        self.addPart(RoundedTriangleEdge(self, s))

        # Notes on rectangularWall parameters, all reference a 2D part
        #   screen width, or X-dimension
        #   screen height, Y-dimension
        #   edge defines the style of the 4 sides of athe 2D part 
        #       (bottom, right, top, left) of 2D part. In general,
        #        match F with f on mating edges of the box
        #   move= turtle graphic commands that move origin drawing
        #
        # Arguments x, y, h are 3D parameters of the box we're making.
        #
        self.rectangularWall(h, y, "FfFq", move="right")    #handle end
        self.rectangularWall(x, y, "FFFF", move="right")    #bottom
        self.rectangularWall(h, y, "FqFf", move="up")       #handle end
        self.rectangularWall(x, h, "ffef", move="up left")  #side
        self.rectangularWall(x, h, "efff")                  #side
        
        #TODO: Add a slotted Insert

        self.close()

def main():
    b = Box()
    b.parseArgs()
    b.render()

if __name__ == '__main__':
    main()
