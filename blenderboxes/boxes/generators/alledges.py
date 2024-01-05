# Copyright (C) 2013-2018 Florian Festi
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

class AllEdges(Boxes):
    """Showing all edge types"""

    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.StackableSettings)
        self.addSettingsArgs(edges.HingeSettings)
        self.addSettingsArgs(edges.SlideOnLidSettings)
        self.addSettingsArgs(edges.ClickSettings)
        self.addSettingsArgs(edges.FlexSettings)
        self.addSettingsArgs(edges.HandleEdgeSettings)

        self.buildArgParser(x=100)

    def render(self):
        x = self.x
        t = self.thickness

        chars = list(self.edges.keys())
        chars.sort(key=lambda c: c.lower() + (c if c.isupper() else ''))
        chars.reverse()

        self.moveTo(0, 10*t)
        
        for c in chars:
            with self.saved_context():
                self.move(0, 0, "", True)
                self.moveTo(x, 0, 90)
                self.edge(t+self.edges[c].startwidth())
                self.corner(90)
                self.edges[c](x, h=4*t)
                self.corner(90)
                self.edge(t+self.edges[c].endwidth())
                self.move(0, 0, "")

            self.moveTo(0, 3*t + self.edges[c].spacing())
            self.text(f"{c} - {self.edges[c].description}")
            self.moveTo(0, 12*t)

