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


class DiceTower(Boxes):
    """Tool for fairly rolling dice"""

    ui_group = "Misc"

    description = """Feel free to add a shallow ABox as a container for catching the dice so they don't scatter across the table.

You can also configure the DiceTower and change the number and angle of the ramps.
"""

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.argparser.add_argument(
            "--width",  action="store", type=float, default=80.0, help="width of the tower (side where the dice fall out)")
        self.argparser.add_argument(
            "--depth",  action="store", type=float, default=80.0, help="depth of the tower")
        self.argparser.add_argument(
            "--height",  action="store", type=float, default=170.0, help="height of the tower")
        self.buildArgParser("outside")
        self.argparser.add_argument(
            "--ramps",  action="store", type=int, default=3, help="number of ramps in the tower")
        self.argparser.add_argument(
            "--angle",  action="store", type=float, default=30.0, help="angle of the ramps in the tower")

    def side(self):
        a = math.radians(self.angle)

        # Bottom ramp (full length)
        pos_x = self.left_ramp_cutoff
        pos_y = (self.depth - self.left_ramp_cutoff) * math.tan(a)
        self.fingerHolesAt(pos_x, pos_y, self.ramp_len, -self.angle)

        # Other ramps
        top_gap = 4 * self.thickness
        section_height = (self.height - pos_y - top_gap) / (self.ramps - 1)

        for i in range(self.ramps -1):
            pos_y_i = pos_y + (section_height * (i+1))
            self.ramp(pos_x, pos_y_i, i % 2 == 0)


    def ramp(self, pos_x, pos_y, mirror):
        # Fingerholes for a single ramp
        if mirror:
            # Starts on left side (front)
            self.fingerHolesAt(self.depth - pos_x, pos_y, 0.5*self.ramp_len, 180+self.angle)
        else:
            # Starts on right side (back)
            self.fingerHolesAt(pos_x, pos_y, 0.5*self.ramp_len, -self.angle)


    def render(self):
        if self.outside:
            self.width = self.adjustSize(self.width)
            self.depth = self.adjustSize(self.depth)
            self.height = self.adjustSize(self.height)

        # Calculate length of the bottom ramp
        a = math.radians(self.angle)
        # Start ramps a bit to the side, so we don't have overlap
        self.left_ramp_cutoff = (0.5*self.thickness)*math.sin(a)
        # Bottom ramp also needs to end a bit earlier
        self.right_ramp_cutoff = (0.5*self.thickness) / math.tan(a) * math.cos(a)
        self.ramp_len = (self.depth - self.left_ramp_cutoff - self.right_ramp_cutoff) / math.cos(a)

        # Leave room for dice to fall through on the bottom
        front_gap = self.depth * math.tan(a)
        front_edge = edges.CompoundEdge(self, "Ef", (front_gap, self.height - front_gap))

        # Outer walls
        self.rectangularWall(self.depth, self.height, ("F", front_edge, "e", "f"), callback=[self.side], move="mirror right", label="side")
        self.rectangularWall(self.width, self.height, "FFeF", move="right", label="back")
        self.rectangularWall(self.depth, self.height, ("F", front_edge, "e", "f"), callback=[self.side], move="right", label="side")
        self.rectangularWall(self.width, self.height - front_gap, "eFeF", move="right", label="front")

        # Bottom
        self.rectangularWall(self.width, self.depth, "Efff", move="right", label="bottom")

        # ramps
        self.rectangularWall(self.width, self.ramp_len, "efef", move="up", label="ramp")
        for _ in range(self.ramps - 1):
            self.rectangularWall(self.width, 0.5*self.ramp_len, "efef", move="up", label="ramp")
