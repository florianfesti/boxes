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


class BasedBox(Boxes):
    """Fully closed box on a base"""

    ui_group = "Box"

    description = """This box is more of a building block than a finished item.
Use a vector graphics program (like Inkscape) to add holes or adjust the base
plate. The width of the "brim" can also be adjusted with the **edge_width**
 parameter in the **Finger Joints Settings**.

See ClosedBox for variant without a base.
"""

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.CabinetHingeSettings)
        self.buildArgParser(top_edge="feFhcCESŠvtyY", x=100.0, y=100.0, h=100.0, outside=True)


    def render(self):

        top_edge = self.top_edge
        x, y, h = self.x, self.y, self.h

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            h = self.adjustSize(h)

        t = self.thickness

        top_edge1 = top_edge
        top_edge2 = top_edge
        top_edge3 = top_edge
        top_edge4 = top_edge
        bottom_edge = "h"
        
        match top_edge:
            case "f":
                top_edges = "F" * 4
            case "e":
                top_edges = "" # do not generate top
            case "F" | "h" | "Š":
                top_edges = "f" * 4
            case "c":
                top_edges = "C" * 4
            case "C":
                top_edges = "c" * 4
            case "E":
                top_edges = "E" * 4
                top_edge1 = "e"
                top_edge2 = "e"
                top_edge3 = "e"
                top_edge4 = "e"
            case "S":
                top_edges = ""
            case 'v':
                top_edges = 'Eeve'
                top_edge1 = "V"
                top_edge2 = "E"
                top_edge3 = "e"
                top_edge4 = "E"
            case 't':
                top_edges = "" # do not generate top
                top_edge1 = "E"
                top_edge3 = "E"
            case 'y':
                top_edges = "" # do not generate top
                top_edge1 = "E"
                top_edge3 = "E"
            case 'Y':
                top_edges = "f" * 4
                top_edge1 = "F"
                top_edge3 = "F"
            case _:
                top_edges = ""
            
        self.rectangularWall(y, h, "ff" + top_edge2 + "f", move="right", label="Wall 2")
        self.rectangularWall(y, h, "ff" + top_edge4 + "f", move="up", label="Wall 4")
        self.rectangularWall(x, h, "fF" + top_edge3 + "F", label="Wall 3")
        self.rectangularWall(x, h, "fF" + top_edge1 + "F", move="left up", label="Wall 1")

        if top_edges != "":
            self.rectangularWall(x, y, top_edges, move="right", label="Top")

        self.rectangularWall(x, y, "hh" + bottom_edge + "h", move="up", label="Base")

        if top_edge == "v":
            # Ensure hinge edge is initialized with settings
            if "v" not in self.edges:
                s = edges.CabinetHingeSettings(self.thickness)
                s.edgeObjects(self, "vV", add=True)
            self.edges["v"].parts(move="up")
