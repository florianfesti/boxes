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

    def side_ogee(self, w, h, hi):
        '''Draws a magazine file side with a classic Ogee curve
        consisting of two opposing 60deg arcs along the line from
        the front hi to h. Details from Chris Schwarz: 
        https://goo.gl/cyIT5V'''
        r = min(h - hi, w) / 2.0

        if (h - hi) > w:
            r = w / 2.0
            lx = 0
            ly = (h - hi) - w
        else:
            r = (h - hi) / 2.0
            lx = (w - 2 * r) / 2.0
            ly = 0

        theta = math.degrees(math.atan(w / (h-hi)))
        slant = math.hypot(w, h-hi)
        
        e_w = self.edges["F"].startwidth()
        self.moveTo(3, 3)
        self.edge(e_w)
        self.edges["F"](w)
        self.edge(e_w)
        self.corner(90)
        self.edge(e_w)
        self.edges["F"](hi)

        # The courner at the top of 'hi' and 
        # draw one thickness horizontally
        self.corner(90)
        self.edge(e_w)
        
        # 1) Turn to the calculated heading minus 60deg, 
        # 2) Draw a 60deg arc for half the length
        # 3) Draw another 60deg arc the opposite way
        # 4) Turn the turtle so he faces horizontally
        # 5) Draw one thickness to the back
        self.corner(theta-60)
        self.corner(-60, slant/2)
        self.corner(60, slant/2)
        self.corner(60-theta)
        self.edge(e_w)

        self.corner(90)
        self.edges["F"](h)
        self.edge(e_w)
        self.corner(90)

 
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
        self.rectangularWall(x, h, "Ffef", move="up")
        self.rectangularWall(x, hi, "Ffef", move="up")

        self.rectangularWall(y, x, "ffff")
        self.ctx.restore()

        self.rectangularWall(x, h, "Ffef", move="right only")
        self.side_ogee(y, h, hi)
        self.moveTo(y + 15, h + hi + 15, 180)
        self.side_ogee(y, h, hi)

        self.close()


def main():
    b = MagazinFile()
    b.parseArgs()
    b.render()


if __name__ == '__main__':
    main()
