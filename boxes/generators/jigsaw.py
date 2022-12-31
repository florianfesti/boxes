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


class JigsawPuzzle(Boxes):  # change class name here and below
    """Fractal jigsaw puzzle. Still aplha"""

    webinterface = False  # Change to make visible in web interface

    def __init__(self):
        Boxes.__init__(self)
        self.count = 0
        self.argparser.add_argument(
            "--size", action="store", type=float, default=100,
            help="size of the puzzle in mm")
        self.argparser.add_argument(
            "--depth", action="store", type=int, default=5,
            help="depth of the recursion/level of detail")

    def peano(self, level):
        if level == 0:
            self.edge(self.size / self.depth)
            return

        self.peano(self, level - 1)
        self.corner()

    def edge(self, l):
        self.count += 1
        Boxes.edge(self, l)
        # if (self.count % 2**5) == 0: #level == 3 and parity>0:
        #    self.corner(-360, 0.25*self.size/2**self.depth)

    def hilbert(self, level, parity=1):
        if level == 0:
            return
        # rotate and draw first subcurve with opposite parity to big curve
        self.corner(parity * 90)
        self.hilbert(level - 1, -parity)

        # interface to and draw second subcurve with same parity as big curve
        self.edge(self.size / 2 ** self.depth)
        self.corner(parity * -90)
        self.hilbert(level - 1, parity)

        # third subcurve
        self.edge(self.size / 2 ** self.depth)
        self.hilbert(level - 1, parity)

        # if level == 3: self.corner(-360, 0.4*self.size/2**self.depth)
        # fourth subcurve
        self.corner(parity * -90)
        self.edge(self.size / 2 ** self.depth)
        self.hilbert(level - 1, -parity)
        # a final turn is needed to make the turtle
        # end up facing outward from the large square
        self.corner(parity * 90)
        # if level == 3 and parity>0: # and random.random() < 100*0.5**(self.depth-2):
        #  self.corner(-360, 0.4*self.size/2**self.depth)
        # with self.savedcontext():
        #     self.corner(parity*-90)
        #     self.edge(self.size/2**self.depth)

    def render(self):
        size = self.size
        t = self.thickness
        self.burn = 0.0
        self.moveTo(10, 10)
        self.hilbert(self.depth)


