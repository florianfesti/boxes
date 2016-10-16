#!/usr/bin/env python3
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


class MagazinFile(Boxes):
    """Open magazine file"""

    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("x", "y", "h", "hi", "outside")
        self.argparser.set_defaults(
            fingerjointfinger=2.0,
            fingerjointspace=2.0
        )

        self.argparser.add_argument(
            "--arc",  action="store", type=float, default=60,
            dest="arc", help="Curvature of the sides in degree")

    def side_ogee(self, w, h, hi, arc):
        '''Draws a magazine file side with a classic Ogee curve
        consisting of two opposing 60deg arcs along the line from
        the front hi to h. Details from Chris Schwarz: 
        https://goo.gl/cyIT5V'''

        # Calculate the angle and distance between top of h and hi
        theta = math.degrees(math.atan(w / (h-hi)))
        slant = math.hypot(w, h-hi)

        # length of the secant of the given arc
        secant = (slant/2) / (2*math.sin(math.radians(arc/2)))

        e_w = self.edges["F"].startwidth()
        self.moveTo(3, 3)
        self.edge(e_w)
        self.edges["F"](w)
        self.edge(e_w)
        self.corner(90)
        self.edge(e_w)
        self.edges["F"](hi)

        # The corner at the top of 'hi' and
        # draw one thickness horizontally
        self.corner(90)
        self.edge(e_w)

        # starts pointing west, turn north,
        # then angle to the desired average slope
        # the pre-turn for half the given arc
        self.corner(-90)
        self.corner(theta)
        self.corner(arc/2)
        
        # Draw the curves. First one way, then the other
        self.corner(-arc, secant)
        self.corner(arc, secant)

        # Reverse the initial turns so it points west again
        self.corner(-arc/2)
        self.corner(-theta)
        self.corner(90)
        
        # Draw one thickness to the back edge
        self.edge(e_w)

        self.corner(90)
        self.edges["F"](h)
        self.edge(e_w)
        self.corner(90)

        # Closes the group ?
        self.ctx.stroke()


    def fingerHole(self):
        if self.hi/2 > 12.5 + 10:
            if self.x/2 > 12.5 + 10:
                self.hole(self.x/2, self.hi/2, 12.5)
            else:
                print("Warning: box too narrow to allow room for finger hole")
        else:
            print("Warning: inner wall to short to allow room for finger hole")


    def render(self):

        if self.outside:
            self.x = self.adjustSize(self.x)
            self.y = self.adjustSize(self.y)
            self.h = self.adjustSize(self.h, e2=False)

        x, y, h, = self.x, self.y, self.h
        self.hi = hi = self.hi or (h / 2.0)
        t = self.thickness

        self.open()

        self.ctx.save()
        self.rectangularWall(x, h, "Ffef", move="up", callback=[self.fingerHole])
        self.rectangularWall(x, hi, "Ffef", move="up", callback=[self.fingerHole])

        self.moveTo(0, 3) # jog the bottom wall up a bit
        self.rectangularWall(y, x, "ffff")

        self.ctx.restore()

        self.rectangularWall(x, h, "Ffef", move="right only")

        self.side_ogee(y, h, hi, self.arc)
        self.moveTo(y + 15, h + hi + 15, 180)
        self.side_ogee(y, h, hi, self.arc)

        self.close()


def main():
    b = MagazinFile()
    b.parseArgs()
    b.render()


if __name__ == '__main__':
    main()
