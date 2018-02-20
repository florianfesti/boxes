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
        "height" : 150,
        "radius" : 30,
        "r_hole" : 0,
        }

class RoundedTriangleEdge(edges.Edge):
    """Makes an 'edge' with a rounded triangular bumpout and
       optional hole"""
    char = "q"
    def __call__(self, length, **kw):
        angle = math.degrees(math.atan(2*self.settings.height/length))
        r = self.settings.radius
        if r >  length / 2:
            r = 0
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


class Caddy(Boxes):
    """An open box with two special 'house shaped' sides to generate parts for a 
       6-pack or other carrying caddy. A dowel through the sides makes a handle"""
    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings, finger=2.0, space=2.0)

        self.argparser.add_argument(
            "--handle_height",  action="store", type=float, default=150,
            dest="handle_height", help="distance handle extends past the edge")

        self.argparser.add_argument(
            "--handle_radius",  action="store", type=float, default=6,
            dest="handle_radius", help="radius of the holes for the handle dowel")

        self.buildArgParser("x", "y", "h", "outside")

        #Nice size for a 6-pack of 355ml (12oz) bottles, try making inserts with
        #> ./trayinsert.py --sx 200/3 --sy 135/2 --h 90 --thickness 5
        self.argparser.set_defaults(
            x=210, y=140, h=100)


    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness
        hh= self.handle_height
        hr= self.handle_radius

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            h = self.adjustSize(h)
            hh= self.adjustSize(hn)

        self.open()

        s = RoundedTriangleEdgeSettings(
            self.thickness,
            height=hh,
            r_hole=hr)
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
        # Todo: Parameterize foot option (change s -> F for no feet
        # or allow e for flat bottom, with s for feet or h for straight
        # with holes for fingers)  edges = 'BRTL'
    
        self.rectangularWall(h, y, "FsFq", move="right")    #handle end
        self.rectangularWall(x, y, "ffff", move="right")    #bottom
        self.rectangularWall(h, y, "FqFs", move="up")       #handle end
        self.rectangularWall(x, h, "sfef", move="up left")  #side
        self.rectangularWall(x, h, "efsf")                  #side
        
        #Todo: Add a slotted Insert

        self.close()


def main():
    b = Caddy()
    b.parseArgs()
    b.render()


if __name__ == '__main__':
    main()
