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


class BinFrontEdge(edges.BaseEdge):
    char = "B"
    def __call__(self, length, **kw):
        f = self.settings.front
        a1 = math.degrees(math.atan(f/(1-f)))
        a2 = 45 + a1
        self.corner(-a1)
        for i, l in enumerate(self.settings.sh):
            self.edges["e"](l* (f**2+(1-f)**2)**0.5)
            self.corner(a2)
            self.edges["f"](l*f*2**0.5)
            if i < len(self.settings.sh)-1:
                if self.char == "B":
                    self.polyline(0, 45, 0.5*self.settings.y,
                                  -90, self.thickness, -90, 0.5*self.settings.y, 90-a1)
                else:
                    self.polyline(0, -45, self.thickness, -a1)
            else:
                self.corner(-45)

    def margin(self) -> float:
        return max(self.settings.sh) * self.settings.front

class BinFrontSideEdge(BinFrontEdge):
    char = 'b'

class BinTray(Boxes):
    """A Type tray variant to be used up right with sloped walls in front"""

    ui_group = "Shelf"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.buildArgParser("sx", "y", "sh", "outside", "hole_dD")
        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=0.5)
        self.argparser.add_argument(
            "--front", action="store", type=float, default=0.4,
            help="fraction of bin height covered with slope")

    def xSlots(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            posh = 0
            for h in self.sh:
                self.fingerHolesAt(posx, posh, h)
                posh += h + self.thickness

    def hSlots(self):
        posh = -0.5 * self.thickness
        for h in self.sh[:-1]:
            posh += h + self.thickness
            posx = 0
            for x in reversed(self.sx):
                self.fingerHolesAt(posh, posx, x)
                posx += x + self.thickness

    def addMount(self):
        ds = self.hole_dD[0]

        if len(self.hole_dD) < 2: # if no head diameter is given
            dh = 0 # only a round hole is generated
            h = max (self.thickness * 1.25, self.thickness * 1.0 + ds) # and we assume that a typical screw head diameter is twice the shaft diameter
        else:
            dh = self.hole_dD[1] # use given head diameter
            h = max (self.thickness * 1.25, self.thickness * 1.0 + dh / 2) # and offset the hole to have enough space for the head

        dx = sum(self.sx) + self.thickness * (len(self.sx) - 1)
        x1 = dx * 0.125
        x2 = dx * 0.875

        self.mountingHole(x1, h, ds, dh, -90)
        self.mountingHole(x2, h, ds, dh, -90)

    def xHoles(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            self.fingerHolesAt(posx, 0, self.y)

    def frontHoles(self, i):
        def CB():
            posx = -0.5 * self.thickness
            for x in self.sx[:-1]:
                posx += x + self.thickness
                self.fingerHolesAt(posx, 0, self.sh[i]*self.front*2**0.5)
        return CB

    def hHoles(self):
        posh = -0.5 * self.thickness
        for h in reversed(self.sh[1:]):
            posh += h + self.thickness
            self.fingerHolesAt(posh, 0, self.y)

    def render(self):
        t = self.thickness
        if self.outside:
            self.sx = self.adjustSize(self.sx)
            self.sh = self.adjustSize(self.sh)
            self.y = self.adjustSize(self.y, e2=False)

        x = sum(self.sx) + t * (len(self.sx) - 1)
        h = sum(self.sh) + t * (len(self.sh) - 1)

        y = self.y
        self.front = min(self.front, 0.999)

        self.addPart(BinFrontEdge(self, self))
        self.addPart(BinFrontSideEdge(self, self))

        angledsettings = copy.deepcopy(self.edges["f"].settings)
        angledsettings.setValues(t, True, angle=45)
        angledsettings.edgeObjects(self, chars="gGH")

        # outer walls
        e = ["F", "f", edges.SlottedEdge(self, self.sx[::-1], "G"), "f"]

        self.rectangularWall(x, y, e, callback=[self.xHoles],  move="right", label="bottom")
        self.rectangularWall(h, y, "FFbF", callback=[self.hHoles, ], move="up", label="left")
        self.rectangularWall(h, y, "FFbF", callback=[self.hHoles, ], label="right")
        self.rectangularWall(x, y, "Ffef", callback=[self.xHoles, ], move="left", label="top")
        self.rectangularWall(h, y, "FFBF", move="up only")

        # floor
        self.rectangularWall(x, h, "ffff", callback=[self.xSlots, self.hSlots, self.addMount], move="right", label="back")
        # Inner walls
        for i in range(len(self.sx) - 1):
            e = [edges.SlottedEdge(self, self.sh, "f"), "f", "B", "f"]
            self.rectangularWall(h, y, e, move="up", label="inner vertical " + str(i+1))

        for i in range(len(self.sh) - 1):
            e = [edges.SlottedEdge(self, self.sx, "f", slots=0.5 * y), "f",
                 edges.SlottedEdge(self, self.sx[::-1], "G"), "f"]
            self.rectangularWall(x, y, e, move="up", label="inner horizontal " + str(i+1))

        # Front walls
        for i in range(len(self.sh)):
            e = [edges.SlottedEdge(self, self.sx, "g"), "F", "e", "F"]
            self.rectangularWall(x, self.sh[i]*self.front*2**0.5, e, callback=[self.frontHoles(i)], move="up", label="retainer " + str(i+1))
