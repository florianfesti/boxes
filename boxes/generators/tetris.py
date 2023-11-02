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


class Tetris(Boxes):
    """3D Tetris shapes"""

    ui_group = "Misc"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)

        self.argparser.add_argument(
            "--blocksize", action="store", type=float, default=40.,
            help="size of a square")
        self.argparser.add_argument(
            "--shape", action="store", type=str, default="L",
            choices=['I', 'L', 'O', 'S', 'T'],
            help="shape of the piece")

    def cb(self, nr):
        t = self.thickness
        s = self.blocksize
        self.ctx.stroke()
        self.set_source_color(Color.ETCHING)
        
        if nr == 0:
            if self.shape in "LT":
                for i in range(1, 3):
                    with self.saved_context():
                        self.moveTo(s*i - t, 0, 90)
                        self.edge(s - 2*t)
                if self.shape == "L":
                    self.moveTo(s*2, s - t, 0)
                else: # "T"
                    self.moveTo(s, s - t, 0)
                self.edge(s - 2*t)
            if self.shape == "I":
                for i in range(1, 4):
                    with self.saved_context():
                        self.moveTo(s*i - t, 0, 90)
                        self.edge(s - 2*t)
        if self.shape == "S" and nr in (0, 1, 4, 5):
            self.moveTo(s - t, 0, 90)
            self.edge(s - 2*t)
        if self.shape == "O":
            self.moveTo(s - t, 0, 90)
            self.edge(s - t)


        self.ctx.stroke()
                        
    def render(self):
        # adjust to the variables you want in the local scope
        t = self.thickness
        s = self.blocksize
        
        if self.shape == "L":
            borders = [3*s - 2*t, 90, 2*s - 2*t, 90, s - 2*t, 90,
                       s, -90, 2*s, 90, s - 2*t, 90] 
        elif self.shape == "I":
            borders = [4*s - 2*t, 90, s - 2*t, 90 ] * 2
        elif self.shape == "S":
            borders = [2 * s - 2 * t, 90, s, -90, s, 90, s - 2 * t, 90] *2
        elif self.shape == "O":
            borders = [2*s - 2*t, 90] * 4
        elif self.shape == "T":
            borders = [90, s - 2*t, 90, s, -90, s, 90]
            borders = [3*s - 2*t] + borders + [s - 2*t] + list(reversed(borders))
        self.polygonWall(borders=borders, callback=self.cb, move="right")
        self.polygonWall(borders=borders, callback=self.cb,
                         move="mirror right")

        self.polygonWalls(borders=borders, h=s - 2 * t)
