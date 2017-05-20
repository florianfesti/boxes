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

class BOX(Boxes): # Change class name!
    """DESCRIPTION"""
    
    webinterface = False # Change to make visible in web interface

    ui_group = "Unstable" # see ./__init__.py for names

    def __init__(self):
        Boxes.__init__(self)

        # Uncomment the settings for the edge types you use
        # self.addSettingsArgs(edges.FingerJointSettings)
        # self.addSettingsArgs(edges.StackableSettings)
        # self.addSettingsArgs(edges.HingeSettings)
        # self.addSettingsArgs(edges.LidSettings)
        # self.addSettingsArgs(edges.ClickSettings)
        # self.addSettingsArgs(edges.FlexSettings)

        # remove cli params you do not need
        self.buildArgParser("x", "sx", "y", "sy", "h", "hi")
        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--XX",  action="store", type=float, default=0.5,
            help="DESCRIPTION")
        

    def render(self):
        # adjust to the variables you want in the local scope
        x, y, h = self.x, self.y, self.h
        t = self.thickness
        # Initialize canvas
        self.open()

        # Change settings of default edges if needed. E.g.:
        self.edges["f"].settings.setValues(self.thickness, space=3, finger=3,
                                        surroundingspaces=1)
        # Create new Edges here if needed E.g.:
        s = edges.FingerJointSettings(self.thickness, relative=False,
                                      space = 10, finger=10, height=10,
                                      width=self.thickness)
        p = edges.FingerJointEdge(self, s)
        p.char = "p"
        self.addPart(p)

        
        # render your parts here


        self.close()

