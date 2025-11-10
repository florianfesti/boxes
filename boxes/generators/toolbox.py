
# Copyright (C) 2013-2025 Florian Festi
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

import math

from boxes import *


class CustomCabinetHingeEdge(edges.BaseEdge):
    """Edge with cabinet hinges and customizable spacing segments."""

    char = "u"
    description = "Edge with cabinet hinges"

    def __init__(self, boxes, settings=None, top: bool = False, angled: bool = False) -> None:
        super().__init__(boxes, settings)
        self.top = top
        self.angled = angled
        self.char = "uUvV"[bool(top) + 2 * bool(angled)]

    def startwidth(self) -> float:
        return self.settings.thickness if self.top and self.angled else 0.0

    def _hinge_spacing_segment(self, length: float, index: int, total: int, total_length: float) -> None:
        """Draw the straight segment that spaces hinge modules.

        ``index`` can be ``-1`` for the leading segment and ``total`` for the trailing one.
        """
        if length <= 0:
            return

        if self.char != "u":
            self.edge(length, tabs=2)
            return

        finger_edge = self.boxes.edges.get('F')
        handle_width = getattr(self.boxes, "handle_width", None)
        handle_thickness = getattr(self.boxes, "handle_thickness", None)

        if finger_edge is None or handle_width is None or handle_thickness is None:
            self.edge(length, tabs=2)
            return

        inner_span = max(0.0, handle_width - handle_thickness)
        required = 2 * handle_thickness + inner_span
        if length < required:
            # Not enough room for the custom profile, fall back to simple spacing
            self.edge(length, tabs=2)
            return

        edges_spacing = max(0.0, (length - required - 0.5) / 2.0)

        self.edge(edges_spacing)
        finger_edge(handle_thickness)
        self.edge(inner_span + 0.5)
        finger_edge(handle_thickness)
        self.edge(edges_spacing)

    def _should_use_custom_spacing(self, length: float) -> bool:
        handle_width = getattr(self.boxes, "handle_width", None)
        if handle_width is None:
            return True
        return length > handle_width

    def __poly(self):
        n = self.settings.eyes_per_hinge
        p = self.settings.play
        e = self.settings.eye
        t = self.settings.thickness
        spacing = self.settings.spacing

        if self.settings.style == "outside" and self.angled:
            e = t
        elif self.angled and not self.top:
            # move hinge up to leave space for lid
            e -= t

        if self.top:
            # start with space
            poly = [spacing, 90, e + p]
        else:
            # start with hinge eye
            poly = [spacing + p, 90, e + p, 0]
        for i in range(n):
            if (i % 2) ^ self.top:
                # space
                if i == 0:
                    poly += [-90, t + 2 * p, 90]
                else:
                    poly += [90, t + 2 * p, 90]
            else:
                # hinge eye
                poly += [t - p, -90, t, -90, t - p]

        if (n % 2) ^ self.top:
            # stopped with hinge eye
            poly += [0, e + p, 90, p + spacing]
        else:
            # stopped with space
            poly[-1:] = [-90, e + p, 90, spacing]

        width = (t + p) * n + p + 2 * spacing

        return poly, width

    def __call__(self, l, **kw):
        n = self.settings.eyes_per_hinge
        p = self.settings.play
        e = self.settings.eye
        t = self.settings.thickness
        hn = self.settings.hinges

        poly, width = self.__poly()

        if self.settings.style == "outside" and self.angled:
            e = t
        elif self.angled and not self.top:
            # move hinge up to leave space for lid
            e -= t

        hn = min(hn, int(l // width))

        if hn == 1:
            lead = (l - width) / 2
            if self._should_use_custom_spacing(lead):
                self._hinge_spacing_segment(lead, -1, hn, l)
            else:
                self.edge(lead, tabs=2)

        for j in range(hn):
            for i in range(n):
                if not (i % 2) ^ self.top:
                    self.rectangularHole(self.settings.spacing + 0.5 * t + p + i * (t + p), e + 2.5 * t, t, t)
            self.polyline(*poly)
            if j < (hn - 1):
                segment = (l - hn * width) / (hn - 1)
                if self._should_use_custom_spacing(segment):
                    self._hinge_spacing_segment(segment, j, hn, l)
                else:
                    self.edge(segment, tabs=2)

        if hn == 1:
            tail = (l - width) / 2
            if self._should_use_custom_spacing(tail):
                self._hinge_spacing_segment(tail, hn, hn, l)
            else:
                self.edge(tail, tabs=2)

    def parts(self, move=None) -> None:
        e, b = self.settings.eye, self.settings.bore
        t = self.settings.thickness

        n = self.settings.eyes_per_hinge * self.settings.hinges
        pairs = n // 2 + 2 * (n % 2)

        if self.settings.style == "outside":
            th = 2 * e + 4 * t
            tw = n * (max(3 * t, 2 * e) + self.boxes.spacing)
        else:
            th = 4 * e + 3 * t + self.boxes.spacing
            tw = max(e, 2 * t) * pairs

        if self.move(tw, th, move, True, label="hinges"):
            return

        if self.settings.style == "outside":
            ax = max(t / 2, e - t)
            self.moveTo(t + ax)
            for i in range(n):
                if self.angled:
                    if i > n // 2:
                        l = 4 * t + ax
                    else:
                        l = 5 * t + ax
                else:
                    l = 3 * t + e
                self.hole(0, e, b / 2.0)
                da = math.asin((t - ax) / e)
                dad = math.degrees(da)
                dy = e * (1 - math.cos(da))
                self.polyline(0, (180 - dad, e), 0, (-90 + dad), dy + l - e, (90, t))
                self.polyline(0, 90, t, -90, t, 90, t, 90, t, -90, t, -90, t,
                              90, t, 90, (ax + t) - e, -90, l - 3 * t, (90, e))
                self.moveTo(2 * max(e, 1.5 * t) + self.boxes.spacing)

            self.move(tw, th, move, label="hinges")
            return

        if e <= 2 * t:
            if self.angled:
                corner = [2 * e - t, (90, 2 * t - e), 0, -90, t, (90, e)]
            else:
                corner = [2 * e, (90, 2 * t)]
        else:
            a = math.asin(2 * t / e)
            ang = math.degrees(a)
            corner = [e * (1 - math.cos(a)) + 2 * t, -90 + ang, 0, (180 - ang, e)]
        self.moveTo(max(e, 2 * t))
        for i in range(n):
            self.hole(0, e, b / 2.0)
            
            self.corner(180,4.5)
            self.moveTo(0,0,-90)
            self.polyline(*[ t-self.burn, 90, t, -90, t, -90, t, 90, t, 90, t, (90, t)] + corner + [self.burn])
            self.moveTo(self.boxes.spacing, 4 * e + 3 * t + self.boxes.spacing, 180)
            if i % 2:
                self.moveTo(2 * max(e, 2 * t) + 2 * self.boxes.spacing)

        self.move(th, tw, move, label="hinges")


class Handle:
    """Custom handle profile."""

    def __init__(self, boxes: Boxes, width: float, height: float, thickness: float, gap: float) -> None:
        self.boxes = boxes
        self.width = width
        self.height = height
        self.thickness = thickness
        self.gap = gap

    def render(self, move: str = "", label: str = "Handle") -> None:
        h = self.height
        w = self.width
        t = self.thickness
        g = self.gap
        cr = 0.5
        

        if self.width <= 0 or self.height <= 0:
            return

        b = self.boxes
        if b.move(self.width, self.height, move, before=True, label=label):
            return

        finger_edge = b.edges.get('f')
        b.moveTo(0, 0)
        b.polyline(w+cr,[90, t / 2],h-t/2,[90,0])
        finger_edge(t)
        b.corner(90,0)
        b.polyline(g-cr,[-90,cr],w-cr-t,[-90,cr],g-cr,90)
        finger_edge(t)
        b.corner(90,0)
        b.polyline(h-t/2,[90,t/2])
        b.ctx.stroke()

        b.move(self.width, self.height, move, label=label)


class Latche:

    def __init__(self, boxes, settings=None, width: float = 50, height: float = 50) -> None:
        super().__init__(boxes, settings)
        self.width = width
        self.height = height

    def render(self, move: str = "", label: str = "Handle"):
        b = self.boxes
        w = self.width
        h = self.height
        mt = self.settings.thickness




        b.move(self.width, self.height, move, label=label)
    


class ToolBox(Boxes):
    """Finger jointed toolbox with four walls and a bottom panel."""

    ui_group = "Box"

    description = """A straightforward rectangular toolbox that generates four
walls and a bottom panel using finger joints. Dimensions can be provided either
as internal or external measurements."""

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.CabinetHingeSettings)

        self.buildArgParser("x", "y", "h", "outside")
        self.argparser.add_argument(
            "--custom_spacing",
            action="store",
            type=float,
            default=None,
            help="override spacing between parts (in mm)")
        self.argparser.add_argument(
            "--handle",
            action="store",
            type=bool,
            default=True,
            help="gera a peca de alca (True/False)")
        self.argparser.add_argument(
            "--handle-height",
            action="store",
            type=float,
            default=70,
            help="altura total da alca em mm")
        self.argparser.add_argument(
            "--handle_width",
            action="store",
            type=float,
            default=100,
            help="largura total da alca em mm")
        self.argparser.add_argument(
            "--handle_thickness",
            action="store",
            type=float,
            default=30,
            help="espessura (largura do perfil) da alca em mm")
        self.argparser.add_argument(
            "--handle_gap",
            action="store",
            type=float,
            default=30,
            help="abertura central da alca (gap) em mm")

    def open(self) -> None:
        super().open()
        self._override_cabinet_hinge_edges()
    
    def _override_cabinet_hinge_edges(self) -> None:
        base_edge = self.edges.get('u')
        if base_edge is None:
            return
        settings = base_edge.settings
        for top, angled in ((False, False), (True, False), (False, True), (True, True)):
            edge = CustomCabinetHingeEdge(self, settings, top=top, angled=angled)
            self.addPart(edge)

    def render(self) -> None:

        x, y, h = self.x, self.y, self.h

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            h = self.adjustSize(h)

        material_thickness = self.thickness
        spacing = self.custom_spacing if self.custom_spacing is not None else self.spacing
        if self.custom_spacing is not None:
            self.spacing = spacing
        half_height = h / 2
        move_spacing = (2 * material_thickness) + spacing
        handle_width = self.handle_width
        handle_height = self.handle_height
        handle_thickness = self.handle_thickness
        handle_gap = self.handle_gap

        self.rectangularWall(x, half_height, "FFuF", move="right", label="Lower Wall 1")
        self.rectangularWall(y, half_height, "Ffef", move="up", label="Lower Wall 2")
        self.rectangularWall(x, half_height, "FFeF", move="left right", label="Lower Wall 3")
        self.rectangularWall(y, half_height, "Ffef", move="up", label="Lower Wall 4")

        self.moveTo(-(x + move_spacing), 0)

        self.rectangularWall(x, y, "ffff", move="right", label="Bottom")
        self.rectangularWall(x, y, "ffff", move="up", label="Top")

        self.moveTo(-(x + move_spacing), 0)

        self.rectangularWall(x, half_height, "UFFF", move="right", label="Upper Wall 1")
        self.rectangularWall(y, half_height, "efFf", move="up", label="Upper Wall 2")
        self.rectangularWall(x, half_height, "eFFF", move="left right", label="Upper Wall 3")
        self.rectangularWall(y, half_height, "efFf", move="up", label="Upper Wall 4")

        self.moveTo(-(x + move_spacing), 0)
        self.edges['u'].parts(move="right right right ")

        handle_piece = Handle(self, handle_width, handle_height, handle_thickness, handle_gap)
        handle_piece.render(move="right", label="Handle")
