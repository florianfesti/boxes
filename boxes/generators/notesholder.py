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
from boxes.edges import Edge, CompoundEdge

class USlotEdge(Edge):

    def __call__(self, length, bedBolts=None, bedBoltSettings=None, **kw):
        l = length
        o = self.settings
        d = length * (1-o/100) / 2
        r = min(3*self.thickness, (l-2*d)/2)
        self.edges["f"](d)
        self.polyline(0, 90, 0, (-90, r), l-2*d-2*r, (-90, r), 0, 90)
        self.edges["f"](d)

    def margin(self) -> float:
        return self.edges["f"].margin()

class HalfStackableEdge(edges.StackableEdge):

    char = 'H'

    def __call__(self, length, **kw):
        s = self.settings
        r = s.height / 2.0 / (1 - math.cos(math.radians(s.angle)))
        l = r * math.sin(math.radians(s.angle))
        p = 1 if self.bottom else -1

        if self.bottom:
            self.boxes.fingerHolesAt(0, s.height + self.settings.holedistance + 0.5 * self.boxes.thickness,
                                     length, 0)

        self.boxes.edge(s.width, tabs=1)
        self.boxes.corner(p * s.angle, r)
        self.boxes.corner(-p * s.angle, r)
        self.boxes.edge(length - 1 * s.width - 2 * l)

    def endwidth(self) -> float:
        return self.settings.holedistance + self.settings.thickness

class NotesHolder(Boxes):
    """Box for holding a stack of paper, coasters etc"""

    ui_group = "Box"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=1)
        self.addSettingsArgs(edges.StackableSettings)
        self.buildArgParser(sx="78", y=78, h=35, bottom_edge="s")
        self.argparser.add_argument(
            "--opening",  action="store", type=float, default=40,
            help="percent of front that's open")

    def fingerHoleCB(self, lengths, height, posy=0.0):
        def CB():
            t = self.thickness
            px = -0.5 * t
            for x in lengths[:-1]:
                px += x + t
                self.fingerHolesAt(px, posy, height, 90)
        return CB

    def render(self):
        sx, y, h = self.sx, self.y, self.h
        t = self.thickness

        x = sum(sx) + (len(sx) - 1) * t

        o = max(0, min(self.opening, 100))
        sides = x * (1-o/100) / 2

        b = self.edges.get(self.bottom_edge, self.edges["F"])
        if self.bottom_edge == "s":
            b2 = HalfStackableEdge(self, self.edges["s"].settings,
                                   self.edges["f"].settings)
            b3 = self.edges["h"]
        else:
            b2 = b
            b3 = b

        b4 = Edge(self, None)
        b4.startwidth = lambda: b3.startwidth()

        with self.saved_context():
            self.rectangularWall(y, h, [b, "F", "e", "F"],
                                 ignore_widths=[1, 6], move="right")
            # front walls
            if self.opening == 0.0:
                self.rectangularWall(x, h, [b, "f", "e", "f"],
                                     ignore_widths=[1, 6], move="right")
            else:
                self.rectangularWall(sx[0] * (1-o/100) / 2, h,
                                     [b2, "e", "e", "f"],
                                     ignore_widths=[1, 6], move="right")
                for ix in range(len(sx)-1):
                    left = sx[ix] * (1-o/100) / 2
                    right = sx[ix+1] * (1-o/100) / 2
                    h_e = t
                    bottom_edge = CompoundEdge(
                        self, [b3, b4, b3], [left, t, right])
                    self.rectangularWall(
                        left+right+t, h,
                        [bottom_edge, "e", "e", "e"],
                        callback=[lambda: self.fingerHolesAt(left+t/2, 0, h, 90)],
                        move="right")

                self.rectangularWall(sx[-1] * (1-o/100) / 2, h,
                                     [b2, "e", "e", "f"],
                                     ignore_widths=[1, 6], move="right mirror")

        self.rectangularWall(x, h, [b, "F", "e", "F"],
                             ignore_widths=[1, 6], move="up only")

        with self.saved_context():
            self.rectangularWall(y, h, [b, "F", "e", "F"], ignore_widths=[1, 6], move="right")
            self.rectangularWall(x, h, [b, "f", "e", "f"],
                                 callback=[self.fingerHoleCB(sx, h)],
                                 ignore_widths=[1, 6], move="right")
        self.rectangularWall(y, h, [b, "F", "e", "F"], move="up only")

        if self.bottom_edge != "e":
            if self.opening == 0.0:
                self.rectangularWall(x, y, ["f", "f", "f", "f"], move="up")
            else:
                u_edge = USlotEdge(self, o)
                print([l for x in sx for l in (x, t)])
                front = CompoundEdge(
                    self,
                    ([u_edge, "e"]*len(sx))[:-1],
                    ([l for x in sx for l in (x, t)])[:-1])
                self.rectangularWall(x, y, [front, "f", "f", "f"],
                                     callback=[self.fingerHoleCB(sx, y)],
                                     move="up")
        # innner walls
        for i in range(len(sx)-1):
            self.rectangularWall(
                y, h, ("e" if self.bottom_edge=="e" else "f") + "fef",
                move="right")
