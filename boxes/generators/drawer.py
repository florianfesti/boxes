#!/usr/bin/python3
# Copyright (C) 2013-2016 Bob Marchese
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
#
#   Using libraries from Florian Fest
#   https://github.com/florianfesti/boxes

from boxes import *


class Drawer(Boxes):
    """A Two peice project that forms a small drawer for a
        Streichholzschaechtelchen (little matchbox). That can be enclosed
        in a nested box
        drawer.py --x 100 --y 100 --h 150 --thickness 5 --output drawer_inner.svg 
        box2.py   --x 110 --y 110 --h 150 --thickness 5 --output drawer_outer.svg 
    """
    def __init__(self):
        Boxes.__init__(self)
        # remove cli params you do not need
        self.buildArgParser("x", "y", "h", "hi", "outside")

        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--overhang",  action="store", type=float, default=1,
            dest="overhang", help="Make overhanging edges on bottom")        

        # Set default you might want
        self.argparser.set_defaults(
            fingerjointfinger=2, fingerjointspace=2)

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
        # form an overhang or flange on the given edge
        s = edges.FingerJointSettings(self.thickness, relative=True)

        ts = edges.StackableSettings(self.thickness, relative=True,
                angle = 45, height = 0, holedistance = self.overhang)

        tp = edges.StackableEdge(self, ts, s)
        tp.char = "t"
        self.addPart(tp)

        ##
        ## Draw the Drawer parts
        ##
        #Jog things over to make room for the flanges
        self.moveTo(40, 0)

        # Now render the parts. These 5 calls to rectangularWall()
        # defines a simple box that is open at the top and a special
        # front. 
        # To keep things simple the parts are arranged from left to right 
        # on the canvas using the and without bedBolts.

        # First make the Front face. It will use special type 't' edge with
        # holes all around to receive finger joints. The t joint leaves
        # an overhang of a multiple of the material thickness. The 'E'
        # forms a smooth edge that is outset by 1 thickness to make it
        # flush with an enclosure
        # The third argument specifies the edge type in order 'BRTL'
        print(x, y, h)
        self.rectangularWall(x, y, "ttEt", bedBolts=None, move="right")

        # Makes the left side, back and right side of the drawer
        self.rectangularWall(h, y, "ffef", bedBolts=None, move="right")
        self.rectangularWall(x, y, "FFeF", bedBolts=None, move="right")
        self.rectangularWall(h, y, "ffef", bedBolts=None, move="right")

        # Makes the floor
        self.rectangularWall(h, x, "FfFf", bedBolts=None)


        ##
        ## Draw the enclosure, a simple box open at the front 2 thickness
        ## larger in X & Y and an extra thinckness in h (the drawer depth)
        ##
        x_outer = x + 2*self.thickness
        y_outer = y + 2*self.thickness
        h_outer = h   #No change so drawer sticks out one thickness
        self.moveTo(-1*(2*h+2*x+13.5*self.thickness), 3*self.thickness + x)
        self.rectangularWall(h_outer, y_outer, "FFFE", bedBolts=None, move="right")
        self.rectangularWall(x_outer, y_outer, "ffff", bedBolts=None, move="right")
        self.rectangularWall(h_outer, y_outer, "FEFF", bedBolts=None, move="right")

        self.rectangularWall(h_outer, x_outer, "fFfE", bedBolts=None, move="right")
        self.rectangularWall(h_outer, x_outer, "fEfF", bedBolts=None, move="right")

        self.close()

def main():
    b = Drawer()
    b.parseArgs()
    b.render()

if __name__ == '__main__':
    main()
