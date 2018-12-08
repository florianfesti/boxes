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

from boxes import Boxes, edges, boolarg

class PaintStorage(Boxes):
    """Stackable paint storage"""

    webinterface = True
    ui_group = "Shelf" # see ./__init__.py for names

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.StackableSettings)

        self.buildArgParser(x=100, y=300)

        self.argparser.add_argument(
            "--canheight", action="store", type=int, default=50,
            help="Height of the paintcans")
        self.argparser.add_argument(
            "--candiameter", action="store", type=int, default=30,
            help="Diameter of the paintcans")
        self.argparser.add_argument(
            "--minspace", action="store", type=int, default=10,
            help="Minimum space between the paintcans")
        self.argparser.add_argument(
            "--hexpattern", action="store", type=boolarg, default=False,
            help="Use hexagonal arrangement for the holes instead of orthogonal")

    def paintholes(self):
        "Place holes for the paintcans evenly"

        if self.hexpattern:
            self.moveTo(self.minspace/2, self.minspace/2)
            self.hexHolesRectangle(self.y - 1*self.minspace,
                                   self.x - 1*self.minspace,
                (self.candiameter/2, self.minspace, 'circle'))
            return
        n_x = int(self.x / (self.candiameter+self.minspace))
        n_y = int(self.y / (self.candiameter+self.minspace))
        spacing_x = (self.x - n_x*self.candiameter)/n_x
        spacing_y = (self.y - n_y*self.candiameter)/n_y
        for i in range(n_y):
            for j in range(n_x):
                self.hole(i * (self.candiameter+spacing_y) + (self.candiameter+spacing_y)/2,
                          j * (self.candiameter+spacing_x) + (self.candiameter+spacing_x)/2,
                          self.candiameter/2)


    def render(self):
        # adjust to the variables you want in the local scope
        x, y = self.x, self.y
        t = self.thickness
        
        # Initialize canvas
        self.open()

        stack = self.edges['s'].settings
        h = self.canheight - stack.height - stack.holedistance + t

        # render your parts here
        self.rectangularWall(h, x, "eseS", callback=[
            lambda: self.rectangularHole(h/3, x/2., h/4., 3./4.*x, r=2*t),
            lambda: self.fingerHolesAt(0, self.canheight/3, x, 0)],
                             move="right")
        self.rectangularWall(y, x, "efef",
                             move="right")

        self.rectangularWall(0.8*stack.height+stack.holedistance, x, "eeee",
                             move="up")
        self.rectangularWall(0.8*stack.height+stack.holedistance, x, "eeee",
                             move="")
        self.rectangularWall(y, x, "efef", callback=[self.paintholes],
                             move="left")
        self.rectangularWall(h, x, "eseS", callback=[
            lambda: self.rectangularHole(h/3, x/2., h/4., 3./4.*x, r=2*t),
            lambda: self.fingerHolesAt(0, self.canheight/3, x, 0)],
                             move="left")
        self.close()
