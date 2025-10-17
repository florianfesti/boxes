
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

from boxes import *


class CustomCabinetHingeEdge(edges.CabinetHingeEdge):
    """Cabinet hinge edge with adjustable straight section between fingers."""

    

    def _space_segment(self, first: bool, t: float, p: float) -> list[float]:
        base_length = t + 2 * p 
        base_length = max(0.0, base_length)
        if first and not self.top:
            return [-90, base_length, 90]
        return [90, base_length, 90]

    # override the mangled helper used by the base class
    def _CabinetHingeEdge__poly(self):
        n = self.settings.eyes_per_hinge
        p = self.settings.play
        e = self.settings.eye
        t = self.settings.thickness
        spacing = self.settings.spacing

        if self.settings.style == "outside" and self.angled:
            e = t
        elif self.angled and not self.top:
            e -= t

        if self.top:
            poly = [spacing, 90, e + p]
        else:
            poly = [spacing + p, 90, e + p, 0]

        for i in range(n):
            if (i % 2) ^ self.top:
                poly += self._space_segment(i == 0, t, p)
            else:
                poly += [t - p, -90, t, -90, t - p]

        if (n % 2) ^ self.top:
            poly += [0, e + p, 90, p + spacing]
        else:
            poly[-1:] = [-90, e + p, 90, spacing]

        width = (t + p) * n + p + 2 * spacing
        return poly, width


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
        base_edge = self.edges.get('U')
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
