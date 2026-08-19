# Copyright (C) 2026 boxes-acatoire contributors
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

"""Import a pre-drawn svg artwork file (one flat piece) and replay it through
a Boxes generator's drawing context.

The svg files this loads (xTool Creative Space exports) hold every shape as
one top-level ``<path>`` with its own ``transform="matrix(...)"`` and a flat
``fill``/``stroke`` color -- no nested group transforms. Each path is parsed
with svgpathtools and replayed as move_to/line_to/curve_to calls so the
artwork ends up as real cut/etch geometry, going through the same drawing
context as everything else Boxes.py draws. That is what makes it work for
every output format (svg, dxf, lbrn2, ...): the format-specific serialising
happens after this, in the normal Boxes.py pipeline, not here.

Colors are preserved exactly as authored in the source file -- see
:mod:`boxes.generators.miniature.svgscan` for auditing whether those colors
actually match this app's laser-role palette before trusting a new asset.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

from svgpathtools import Arc, CubicBezier, Line, QuadraticBezier, parse_path

from boxes.Color import Color

SVG_NS = "{http://www.w3.org/2000/svg}"
_MATRIX_RE = re.compile(r"matrix\(([^)]+)\)")
_ARC_STEPS = 16


@dataclass
class SvgPiece:
    """One flat piece parsed out of a source svg file, geometry already in mm."""
    width: float
    height: float
    # list of (color, ops); ops are ("M", x, y) / ("L", x, y) / ("C", x1, y1, x2, y2, x3, y3)
    shapes: list = field(default_factory=list)


def _parse_matrix(transform: str | None) -> tuple[float, float, float, float, float, float]:
    if not transform:
        return (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    m = _MATRIX_RE.search(transform)
    if not m:
        return (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    a, b, c, d, e, f = (float(v) for v in re.split(r"[,\s]+", m.group(1).strip()))
    return (a, b, c, d, e, f)


def _mm(value: str) -> float:
    return float(value.replace("mm", "").strip())


def load_svg_piece(path) -> SvgPiece:
    """Parse an svg file into millimeter-space shapes, keeping each path's own color."""
    root = ET.parse(path).getroot()

    width = _mm(root.get("width", "0"))
    height = _mm(root.get("height", "0"))
    view_box = [float(v) for v in root.get("viewBox", f"0 0 {width} {height}").split()]
    vb_x, vb_y, vb_w, vb_h = view_box
    scale_x = width / vb_w if vb_w else 1.0
    scale_y = height / vb_h if vb_h else 1.0

    shapes: list[tuple[str, list[tuple]]] = []
    for elem in root.iter(f"{SVG_NS}path"):
        d = elem.get("d")
        if not d:
            continue
        fill = elem.get("fill", "")
        stroke = elem.get("stroke", "")
        color = fill if fill and fill != "none" else stroke
        if not color or color == "none":
            continue

        a, b, c, dd, e, f = _parse_matrix(elem.get("transform"))

        def to_mm(pt: complex, a=a, b=b, c=c, dd=dd, e=e, f=f) -> tuple[float, float]:
            x, y = pt.real, pt.imag
            mx = a * x + c * y + e
            my = b * x + dd * y + f
            # Source svg coordinates are y-down (like every svg), 0..height with
            # 0 at the top. Boxes.py's own drawing context is y-up -- every other
            # generator draws its content starting at y=0 (the cursor / "ground")
            # and extending up to +height, then SVGSurface flips that once to
            # y-down at output time. Mapping to (height - y) both undoes the extra
            # flip (upright again) and keeps the piece in the same [0, height]
            # band everything else uses, so it lands next to the cursor instead
            # of behind/under whatever was already drawn there (e.g. the
            # reference rectangle).
            return ((mx - vb_x) * scale_x, height - (my - vb_y) * scale_y)

        ops: list[tuple] = []
        last_end = None
        for seg in parse_path(d):
            if last_end is None or abs(seg.start - last_end) > 1e-6:
                ops.append(("M", *to_mm(seg.start)))
            if isinstance(seg, Line):
                ops.append(("L", *to_mm(seg.end)))
            elif isinstance(seg, CubicBezier):
                ops.append(("C", *to_mm(seg.control1), *to_mm(seg.control2), *to_mm(seg.end)))
            elif isinstance(seg, QuadraticBezier):
                c1 = seg.start + 2 / 3 * (seg.control - seg.start)
                c2 = seg.end + 2 / 3 * (seg.control - seg.end)
                ops.append(("C", *to_mm(c1), *to_mm(c2), *to_mm(seg.end)))
            elif isinstance(seg, Arc):
                for i in range(1, _ARC_STEPS + 1):
                    ops.append(("L", *to_mm(seg.point(i / _ARC_STEPS))))
            last_end = seg.end

        if ops:
            shapes.append((color, ops))

    return SvgPiece(width=width, height=height, shapes=shapes)


def draw_piece(boxes, piece: SvgPiece) -> None:
    """Replay a parsed SvgPiece onto boxes.ctx at the current origin, mm for mm."""
    ctx = boxes.ctx
    for color, ops in piece.shapes:
        try:
            rgb = Color.from_hex(color) if color.startswith("#") else None
        except ValueError:
            rgb = None
        if rgb is None:
            continue
        ctx.set_source_rgb(*rgb)
        for op in ops:
            code = op[0]
            if code == "M":
                ctx.move_to(op[1], op[2])
            elif code == "L":
                ctx.line_to(op[1], op[2])
            elif code == "C":
                ctx.curve_to(*op[1:])
        ctx.stroke()
