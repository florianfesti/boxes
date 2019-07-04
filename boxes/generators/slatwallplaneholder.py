#!/usr/bin/env python3
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

class SlatwallPlaneHolder(Boxes):
    """Hold a plane to a slatwall"""

    ui_group = "SlatWall"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.SlatWallSettings)

        self.argparser.add_argument(
            "--width",  action="store", type=float, default=80,
            help="width of the plane")
        self.argparser.add_argument(
            "--length",  action="store", type=float, default=250,
            help="legth of the plane")
        self.argparser.add_argument(
            "--hold_length",  action="store", type=float, default=30,
            help="legth of the part hiolding the plane over the front")
        self.argparser.add_argument(
            "--height",  action="store", type=float, default=80,
            help="height of the front of plane")

    def side(self):
        l, w, h = self.length, self.width, self.height
        hl = self.hold_length
        t = self.thickness
        self.fingerHolesAt(1.5*t, 2*t, 0.25*l, 90)
        self.fingerHolesAt(1.5*t, 2*t+0.75*l, 0.25*l, 90)
        self.fingerHolesAt(2.5*t+h, 2*t+l-hl, hl, 90)
        self.fingerHolesAt(2*t, 1.5*t, h+2*t, 0)

    def render(self):
        # Add slat wall edges
        s = edges.SlatWallSettings(self.thickness, True,
                                   **self.edgesettings.get("SlatWall", {}))
        s.edgeObjects(self)
        self.slatWallHolesAt = edges.SlatWallHoles(self, s)

        l, w, h = self.length, self.width, self.height
        t = self.thickness
        self.rectangularWall(h+4*t, l+2*t, "eeea", callback=[self.side],
                             move="right")
        self.rectangularWall(h+4*t, l+2*t, "eeea", callback=[self.side],
                             move="right")
        self.rectangularWall(w, h+2*t, "efFf", move="up")
        self.rectangularWall(w, 0.25*l, "ffef", move="up")
        self.rectangularWall(w, 0.25*l, "efef", move="up")
        self.rectangularWall(w, self.hold_length, "efef", move="up")
