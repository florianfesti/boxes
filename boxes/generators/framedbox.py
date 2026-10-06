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
import math


class FramedBox(Boxes):
    """A box in which every face is a frame"""

    ui_group = "Box"

    description = """This box is more of a building block than a finished item.
Use a vector graphics program (like Inkscape) to add any features."""

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.DoveTailSettings, size=3, depth=.9, radius=.05, angle=40)
        self.buildArgParser("x", "y", "h", "outside")
        self.argparser.add_argument("--frame_thickness", type=float, default=15, help="Thickness of the frame pieces")

    def render(self):
        x, y, h = self.x, self.y, self.h

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            h = self.adjustSize(h)

        self.splitRectangularWall(x, h, "FFFF", move="right", label="Wall 1")
        self.splitRectangularWall(y, h, "FfFf", move="up", label="Wall 2")
        self.splitRectangularWall(y, h, "FfFf", label="Wall 4")
        self.splitRectangularWall(x, h, "FFFF", move="left up", label="Wall 3")
        self.splitRectangularWall(x, y, "ffff", move="right", label="Top")
        self.splitRectangularWall(x, y, "ffff", label="Bottom")

    def splitRectangularWall(self, w, h, edges, move=None, label=None):
        overallWidth = max(w,h) + self.thickness * 2
        overallHeight = (self.frame_thickness + self.thickness + self.spacing/2) * 4
        if self.move(overallWidth, overallHeight, move,before=True): return
        edges = [self.edges.get(e, e) for e in edges]
        edges += edges  # append for wrapping around
        DOVE_TAIL_CHARS='dD'
        which = ['bottom', 'right', 'top', 'left']
        for i, l in enumerate((w, h, w, h)):
            self.pieceOfFrame(edges,i,l,self.frame_thickness,DOVE_TAIL_CHARS[i % 2],f"{label}\n{which[i]}")
        self.move(overallWidth, overallHeight, move)


    def pieceOfFrame(self,edges,i,l,thickness,dove_tail_char,label):
        edge = edges[i]
        sw = edges[i-1].endWidth()
        ew = edges[i+1].startWidth()
        pieceWidth = l + sw + ew  
        pieceHeight = thickness
        if edge.char == 'f': self.moveTo(0,self.thickness)
        if self.move(pieceWidth, pieceHeight, 'up', before=True):
            return
        diagonal = math.sqrt(2) * thickness
        self.edge(sw)
        edge(l)
        self.edge(ew)
        self.corner(90+45)
        self.edges[dove_tail_char](diagonal)
        self.corner(90-45)
        self.edges['e'](pieceWidth - 2 * thickness)
        self.corner(90-45)
        self.edges[dove_tail_char](diagonal)
        self.corner(90+45)
        self.move(pieceWidth, pieceHeight, 'up',label=label)
