
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
    """Local variant of the cabinet hinge edge with additional finger joints."""

    CHAR_MAP = "wWxX"

    def __init__(self, boxes, settings=None, top: bool = False, angled: bool = False) -> None:
        super().__init__(boxes, settings)
        self.top = top
        self.angled = angled
        self.char = self.CHAR_MAP[bool(top) + 2 * bool(angled)]
        self.description = "Custom cabinet hinge variant"

    def startwidth(self) -> float:
        return self.settings.thickness if self.top and self.angled else 0.0

    def _poly(self) -> tuple[list[float], float]:
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
                if i == 0:
                    poly += [-90, t + 2 * p, 90]
                else:
                    poly += [90, t + 2 * p, 90]
            else:
                poly += [t - p, -90, t, -90, t - p]

        if (n % 2) ^ self.top:
            poly += [0, e + p, 90, p + spacing]
        else:
            poly[-1:] = [-90, e + p, 90, spacing]

        width = (t + p) * n + p + 2 * spacing
        prt = [n,p,e,t,spacing,poly]
        print(prt)
        return poly, width

    def __call__(self, l, **kw):
        n = self.settings.eyes_per_hinge
        p = self.settings.play
        e = self.settings.eye
        t = self.settings.thickness
        hn = self.settings.hinges

        poly, width = self._poly()

        if self.settings.style == "outside" and self.angled:
            e = t
        elif self.angled and not self.top:
            e -= t

        hn = min(hn, int(l // width))

        if hn == 1:
            self.edge((l - width) / 2, tabs=2)

        for j in range(hn):
            for i in range(n):
                if not (i % 2) ^ self.top:
                    self.rectangularHole(
                        self.settings.spacing + 0.5 * t + p + i * (t + p),
                        e + 2.5 * t,
                        t,
                        t,
                    )
            self.polyline(*poly)
            if j < (hn - 1):
                self.edge((l - hn * width) / (hn - 1), tabs=2)

        if hn == 1:
            self.edge((l - width) / 2, tabs=2)

        self._draw_handle_fingers(l)

    def _draw_handle_fingers(self, total_length: float) -> None:
        boxes = self.boxes
        handle_width = getattr(boxes, "handle_width_value", None)
        handle_thickness = getattr(boxes, "handle_thickness_value", None)
        if not handle_width or not handle_thickness:
            return
        finger_width = handle_thickness
        if finger_width <= 0 or handle_width <= 2 * finger_width:
            return
        start_offset = total_length / 2.0 - handle_width / 2.0 - finger_width
        print(f"[handle-debug] start_offset={total_length:.3f}")
        if start_offset < 0:
            start_offset = 0.0
        mid_gap = handle_width - 2.0 * finger_width
        finger_edge = boxes.edges.get('f')
        if finger_edge is None:
            return
        with boxes.saved_context():
            self.moveTo(start_offset, 0)
            finger_edge(finger_width)
            if mid_gap > 0:
                self.edge(mid_gap)
            finger_edge(finger_width)

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
                    l = 4 * t + ax if i > n // 2 else 5 * t + ax
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
            self.polyline(*([0, (180, e), 0, -90, t, 90, t, -90, t, -90, t, 90, t, 90, t, (90, t)] + corner))
            self.moveTo(self.boxes.spacing, 4 * e + 3 * t + self.boxes.spacing, 180)
            if i % 2:
                self.moveTo(2 * max(e, 2 * t) + 2 * self.boxes.spacing)

        self.move(th, tw, move, label="hinges")


class Handle:
    """Simple rectangular handle piece."""

    def __init__(self, boxes: Boxes, width: float, height: float, thickness: float) -> None:
        self.boxes = boxes
        self.width = width
        self.height = height
        self.thickness = thickness

    def render(self, move: str = "", label: str = "Handle") -> None:
        if self.width <= 0 or self.height <= 0:
            return

        boxes = self.boxes
        if boxes.move(self.width, self.height, move, before=True, label=label):
            return

        ctx = boxes.ctx
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.stroke()

        boxes.move(self.width, self.height, move, label=label)


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

    def open(self) -> None:
        """Ensure custom hinge edges are available after opening."""
        super().open()
        self._add_custom_hinge_edges()

    def _add_custom_hinge_edges(self) -> None:
        """Register local cabinet hinge variants with characters w/W/x/X."""
        base_edge = self.edges.get('u')
        if base_edge is None:
            return
        if 'w' in self.edges:
            return
        base_settings = base_edge.settings
        combinations = (
            (False, False),  # w
            (True, False),   # W
            (False, True),   # x
            (True, True),    # X
        )
        for top, angled in combinations:
            edge = CustomCabinetHingeEdge(self, base_settings, top=top, angled=angled)
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
        handle_width = 100
        handle_height = 50
        handle_thickness = material_thickness
        self.handle_width_value = handle_width
        self.handle_thickness_value = handle_thickness

        self.rectangularWall(x, half_height, "FFwF", move="right", label="Lower Wall 1")
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
        self.edges['u'].parts(move="right right right")

        handle_piece = Handle(self, handle_width, handle_height, material_thickness)
        handle_piece.render(move="right", label="Handle")
