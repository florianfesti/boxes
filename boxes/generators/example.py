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


class Box(Boxes):
    """An example of creating a custom box definition using the Boxes API"""
    def __init__(self):
        Boxes.__init__(self)
        # remove cli params you do not need
        self.buildArgParser("x", "y", "h", "hi", "outside")

        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--special_finger",  action="store", type=float, default=10,
            dest="special_finger", help="Custom finger joint size")        

        # Set default you might want
        self.argparser.set_defaults(
            fingerjointfinger=2, fingerjointspace=2
            )

    def render(self):
        # adjust to the variables you want in the local scope
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y, False)
            h = self.adjustSize(h, False)

        # Initialize canvas
        self.open()

        # Create new type of edges here. This example uses a newwe
        # finger joint with sizes set with the 'special_finger' 
        # parameter added to the class above
        s = edges.FingerJointSettings(self.thickness, relative=False,
                                      space = self.special_finger, 
                                      finger = self.special_finger,
                                      height = self.special_finger,
                                      width=self.thickness)

        # The new joint type will be indicated with an 'n' and a 'N'
        # for its mate.
        p = edges.FingerJointEdge(self, s)
        p.char = "n"
        self.addPart(p)
        p = edges.FingerJointEdgeCounterPart(self, s)
        p.char = "N"
        self.addPart(p)
        
        # Move away from the lower left courner by the thickness of the
        # in X and Y in the x and y
        self.moveTo(t, t)

        # Now render the parts. These 5 calls to rectangularWall()
        # defines a simple box that is open at the top. To keep things
        # simple the parts are arranged from left to right on the
        # canvas using the move="right" argument and without bedBolts.

        # First make the bottom. It will use type 'f' finger joints all
        # Around. First two arguments are the horizontal and vertical
        # sizes using the local variables x and y. 3rd argument are 4 
        # characters that specifies the edges in order (bottom, right, 
        # top, left) relative to the part on the canvas. For this part
        # they are all type 'f' finger joints.
        self.rectangularWall(x, y, "ffff", bedBolts=None, move="right")

        # Add the first two sides. with joints as follows
        #   Bottom is type 'F' to mate with lower case f used above
        #   Right is type 'F' for a mating finger joint for the right side
        #   Top is type 'e' to make it flat
        #   Left is another 'F' to mate with the next part
        self.rectangularWall(x, h, "FFeF", bedBolts=None, move="right")

        # These edge parameters are similar: 'F' at bottom, but with 'f' 
        # at Right and Left (2nd and 4th). Top (3rd) is always and 'e'.
        self.rectangularWall(x, h, "Ffef", bedBolts=None, move="right")
        
        # Add the next two side. the "FNeF' amd 'Ffen' have the same
        # Top and bottom definitions as all the others but with 'N' and
        # 'n' to use the pair of special joints
        self.rectangularWall(x, h, "FNeF", bedBolts=None, move="right")
        self.rectangularWall(x, h, "Ffen", bedBolts=None, move="right")

        self.close()

def main():
    b = Box()
    b.parseArgs()
    b.render()

if __name__ == '__main__':
    main()
