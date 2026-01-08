# Copyright (C) 2013-2017 Florian Festi
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
from boxes.lids import LidSettings, _TopEdge


class UBox(_TopEdge):
    """Box various options for different stypes and lids"""

    ui_group = "FlexBox"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addTopEdgeSettings()
        self.addSettingsArgs(edges.FlexSettings)
        self.addSettingsArgs(LidSettings)
        self.buildArgParser("top_edge", "x", "y", "h")
        self.argparser.add_argument(
            "--radius",  action="store", type=float, default=30.0,
            help="radius of bottom corners")
        self.angle = 0

    def U(self, y, h, r, edge="e", move=None, label=""):

        e = self.edges.get(edge, edge)

        w = self.edges["f"].spacing()
        tw = y+2*w
        th = h+w+e.spacing()
        if self.move(tw, th, move, True, label=label):
            return

        self.moveTo(w+r, w)
        self.edges["f"](y-2*r)
        self.corner(90, r)
        self.edges["f"](h-r)
        self.edgeCorner("f", e)
        e(y)
        self.edgeCorner(e, "f")
        self.edges["f"](h-r)
        self.corner(90, r)

        self.move(tw, th, move, label=label)

    def Uwall(self, y, h, x, r, edges="ee", move=None, label=""):

        e = [self.edges.get(edge, edge) for edge in edges]

        w = self.edges["F"].spacing()
        cl = r*math.pi/2

        tw = 2*h + y - 4*(cl-r) + e[0].spacing() + e[1].spacing()
        th = x + 2*w
        if self.move(tw, th, move, True, label=label):
            return

        self.moveTo(e[0].spacing())

        for nr, flex in enumerate("XE"):
            self.edges["F"](h-r)
            if y-2*r > 0.1 * self.thickness:
                self.edges[flex](cl, h=th)
                self.edges["F"](y-2*r)
                self.edges[flex](cl, h=th)
            else:
                self.edges[flex](2*cl+y-2*r, h=th)
            self.edges["F"](h-r)
            if edges[0] in (self.edges["i"], self.edges["k"]):
                # hinged lids, mimic ignor_widths
                self.edgeCorner("e", e[nr])
                e[nr](x + self.edges["F"].startWidth() +
                      self.edges["F"].endWidth())
                self.edgeCorner(e[nr], "e")
            else:
                self.edgeCorner("F", e[nr])
                e[nr](x)
                self.edgeCorner(e[nr], "F")
        self.move(tw, th, move, label=label)

    def render(self):
        x, y, h, r = self.x, self.y, self.h, self.radius

        self.radius = r = min(r, y/2.0, h)

        self.edges["i"].settings.style = "flush_inset"

        _ = self.translations.gettext
        t1, t2, t3, t4 = self.topEdges(self.top_edge)

        self.U(y, h, r, t1, move="right", label=_("left"))
        self.U(y, h, r, t3, move="up", label=_("right"))
        self.U(y, h, r, t3, move="left only")
        self.Uwall(y, h, x, r, [t2, t4], move="up", label=_("wall"))

        self.drawLid(x, y, self.top_edge)
        self.lid(y, x, self.top_edge) # keep chest lid aligned with U
