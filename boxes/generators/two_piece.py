#!/usr/bin/python3
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


class TwoPiece(Boxes):
    """A two piece box where top slips over the bottom half to form 
        the enclosure. For the inner part, generate a with an overhang
        of two thickness. For the outer part, use the same height but
        add 2x the thickness to X and Y withg an overhang of one less.
        two_piece.py --overhang 2 --x 100 --y 100 --h 50 --thickness 5 --output box_inner.svg 
        two_piece.py --overhang 1 --x 110 --y 110 --h 50 --thickness 5 --output box_outer.svg 

        This leaves a flange that is one thickness at the top and
        bottom that is visible when fully assembled.

        TODO: Generate both sets of pieces from a single command line
        TODO: Replace 'stackable' edge abuse with one based on 'outset' 
    """
    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("x", "y", "h", "outside")
        self.addSettingsArgs(edges.FingerJointSettings, finger=2.0, space=2.0)

        # Add CLI param to controll overhand
        self.argparser.add_argument(
            "--overhang",  action="store", type=float, default=1,
            dest="overhang", help="Make overhanging edges on bottom")        

    def render(self):
        # adjust to the variables you want in the local scope
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        if self.outside:
            x = self.adjustSize(x, False)
            y = self.adjustSize(y, False)
            h = self.adjustSize(h, False)

        # Initialize canvas
        self.open()

        # New edge type based on the stackable edge type, used here to
        # Make an overhang on the bottom of the box
        s = edges.FingerJointSettings(self.thickness, relative=True)

        ts = edges.StackableSettings(self.thickness, relative=True,
                angle = 45, height = 0, holedistance = self.overhang)

        tp = edges.StackableEdge(self, ts, s)
        tp.char = "t"
        self.addPart(tp)

        # Now render the parts. These 5 calls to rectangularWall()
        # defines a simple box that is open at the top. To keep things
        # simple the parts are arranged from left to right on the
        # canvas using the move="right" argument and without bedBolts.

        #Define the walls. The first two arguments are the horizontal and 
        # verticalsizes using the local variables x and y. The third 
        # argument specifies the edge type in order 'BRTL'

        # First make the bottom. It will use special type 't' edge with
        # holes all around to receive finger joints. The t joint leaves
        # an overhang of a multiple of the material thickness. Reverts 
        # to a normal F joint when the bottom is to be flush with sides
        if self.overhang > 0:
            self.rectangularWall(x, y, "tttt", bedBolts=None, move="right")
        else:
            self.rectangularWall(x, y, "FFFF", bedBolts=None, move="right")

        # Add the first two sides. with joints as follows
        #   Bottom is type 'F' to mate with lower case f used above
        #   Right is type 'F' for a mating finger joint for the right side
        #   Top is type 'e' to make it flat
        #   Left is another 'F' to mate with the next part
        self.rectangularWall(x, h, "fFeF", bedBolts=None, move="right")

        # These edge parameters are similar: 'F' at bottom, but with 'f' 
        # at Right and Left (2nd and 4th). Top (3rd) is always and 'e'.
        self.rectangularWall(x, h, "ffef", bedBolts=None, move="right")
        
        # Add the next two side. the "FNeF' amd 'Ffen' have the same
        # Top and bottom definitions as all the others but with 'N' and
        # 'n' to use the pair of special joints
        self.rectangularWall(x, h, "fFeF", bedBolts=None, move="right")
        self.rectangularWall(x, h, "ffef", bedBolts=None, move="right")

        self.close()

def main():
    b = TwoPiece()
    b.parseArgs()
    b.render()

if __name__ == '__main__':
    main()
