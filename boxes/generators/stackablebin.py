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


class StackableBinEdge(edges.BaseEdge):
    char = "B"

    def __call__(self, length, **kw):
        f = self.settings.front
        a1 = math.degrees(math.atan(f/(1-f)))
        a2 = 45 + a1
        self.corner(-a1)

        self.edges["e"](self.settings.h* (f**2+(1-f)**2)**0.5)
        self.corner(a2)
        self.edges["f"](self.settings.h*f*2**0.5)

        self.corner(-45)

    def margin(self) -> float:
        return self.settings.h * self.settings.front

class StackableBinSideEdge(StackableBinEdge):
    char = 'b'

class StackableBin(Boxes):
    """Stackable bin base on bintray"""

    ui_group = "Shelf"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.StackableSettings, bottom_stabilizers=2.4)
        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=0.5)
        self.buildArgParser("outside")
        self.buildArgParser(sx="70", h=50)
        self.argparser.add_argument(
            "--d", action="store", type=float, default=100,
            help="bin (d)epth")
        self.argparser.add_argument(
            "--front", action="store", type=float, default=0.4,
            help="fraction of bin height covered with slope")

    def wallCB(self, sx, l):
        def CB():
            t = self.thickness
            posx = -0.5*t
            for x in sx[:-1]:
                posx += x + t
                self.fingerHolesAt(posx, 0, l, 90)
        return CB

    def render(self):

        self.front = min(self.front, 0.999)

        self.addPart(StackableBinEdge(self, self))
        self.addPart(StackableBinSideEdge(self, self))

        angledsettings = copy.deepcopy(self.edges["f"].settings)
        angledsettings.setValues(self.thickness, True, angle=45)
        angledsettings.edgeObjects(self, chars="gGH")

        if self.outside:
            self.sx = self.adjustSize(self.sx)
            self.h = self.adjustSize(self.h, "s", "S")
            self.d = self.adjustSize(self.d, "h", "b")

        x = sum(self.sx) + self.thickness * (len(self.sx) - 1)

        with self.saved_context():
            self.rectangularWall(x, self.d, "ffGf",
                                 callback=[self.wallCB(self.sx, self.d)],
                                 label="bottom", move="up")
            self.rectangularWall(x, self.h, "hfef",
                                 callback=[self.wallCB(self.sx, self.h)],
                                 label="back", move="up ")
            self.rectangularWall(x, self.h*self.front*2**0.5, "gFeF",
                                 callback=[self.wallCB(self.sx, self.h*self.front*2**0.5)],
                                 label="retainer", move="up")
            self.rectangularWall(x, 3, "EEEE", label="for label (optional)")

        self.rectangularWall(x, 3, "EEEE", label="movement", move="right only")

        self.rectangularWall(self.d, self.h, "shSb", label="left", move="up")
        self.rectangularWall(self.d, self.h, "shSb", label="right", move="mirror up")
        for i in range(len(self.sx)-1):
            self.rectangularWall(self.d, self.h, "ffSb", label="left", move="up")
