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

    ui_group = "Unstable" # see ./__init__.py for names

    def __init__(self) -> None:
        Boxes.__init__(self)

        # Uncomment the settings for the edge types you use
        # use keyword args to set default values
        # self.addSettingsArgs(edges.FingerJointSettings, finger=1.0,space=1.0)
        # self.addSettingsArgs(edges.StackableSettings)
        # self.addSettingsArgs(edges.HingeSettings)
        # self.addSettingsArgs(edges.SlideOnLidSettings)
        # self.addSettingsArgs(edges.ClickSettings)
        # self.addSettingsArgs(edges.FlexSettings)

        # remove cli params you do not need
        self.buildArgParser(x=100, sx="3*50", y=100, sy="3*50", h=100, hi=0)
        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--XX",  action="store", type=float, default=0.5,
            help="DESCRIPTION")


    def render(self):
        # adjust to the variables you want in the local scope
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        # Create new Edges here if needed E.g.:
        s = edges.FingerJointSettings(self.thickness, relative=False,
                                      space = 10, finger=10,
                                      width=self.thickness)
        p = edges.FingerJointEdge(self, s)
        p.char = "a" # 'a', 'A', 'b' and 'B' is reserved for being used within generators
        self.addPart(p)

        # render your parts here

