# Copyright (C) 2013-2019 Florian Festi
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
from boxes.walledges import _WallMountedBox

class WallXXX(_WallMountedBox): # Change class name!
    """DESCRIPTION"""

    def __init__(self) -> None:
        super().__init__()

        # remove cli params you do not need
        self.buildArgParser(x=100, sx="3*50", y=100, sy="3*50", h=100, hi=0)

        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--XX",  action="store", type=float, default=0.5,
            help="DESCRIPTION")

        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--XXX",  action="store", type=boolarg, default=False,
            help="DESCRIPTION")

    def render(self):
        self.generateWallEdges() # creates the aAbBcCdD| edges

        # render your parts here
