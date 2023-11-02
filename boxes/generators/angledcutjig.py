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

class AngledCutJig(Boxes): # Change class name!
    """Jig for making angled cuts in a laser cutter"""

    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=1.)

        # remove cli params you do not need
        self.buildArgParser(x=50, y=100)
        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--angle",  action="store", type=float, default=45.,
            help="Angle of the cut")

    def bottomCB(self):
        t = self.thickness
        self.fingerHolesAt(10-t, 4.5*t, 20, 0)
        self.fingerHolesAt(30+t, 4.5*t, self.x, 0)
        self.fingerHolesAt(10-t, self.y-4.5*t, 20, 0)
        self.fingerHolesAt(30+t, self.y-4.5*t, self.x, 0)

    def render(self):
        # adjust to the variables you want in the local scope
        x, y = self.x, self.y
        t = self.thickness

        th = x * math.tan(math.radians(90-self.angle))
        l = (x**2 + th**2)**0.5
        th2 = 20 * math.tan(math.radians(self.angle))
        l2 = (20**2 + th2**2)**0.5

        self.rectangularWall(30+x+2*t, y, callback=[self.bottomCB], move="right")
        self.rectangularWall(l, y, callback=[
            lambda:self.fingerHolesAt(0, 4.5*t, l, 0), None,
            lambda:self.fingerHolesAt(0, 4.5*t, l, 0), None],
                             move="right")
        self.rectangularWall(l2, y, callback=[
            lambda:self.fingerHolesAt(0, 4.5*t, l2, 0), None,
            lambda:self.fingerHolesAt(0, 4.5*t, l2, 0), None],
                             move="right")
        
        self.rectangularTriangle(x, th, "fef", num=2, move="up")
        self.rectangularTriangle(20, th2, "fef", num=2, move="up")
        
