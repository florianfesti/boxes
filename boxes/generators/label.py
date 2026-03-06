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

from __future__ import annotations

from typing import cast

from boxes import *
from boxes.drawing import Context
from boxes.fontsettings import FontSettings


class Label(Boxes):
    """Rectangular label with rounded corners, optional inner border line and engraved text."""

    ui_group = "Deco"

    description = """
A flat laser-cut label plate.

* **Outer cut** (black / OUTER_CUT): the perimeter of the label with
  configurable rounded corners – this is the cut-through line.
* **Inner border** (blue / INNER_CUT, optional): a decorative inset line
  parallel to the outer edge – engraved, not cut through.
* **Text** (green / ETCHING): one line of text engraved inside the label,
  with configurable font, size and alignment.


Assembly: none required – this is a single flat piece.
"""

    # Dummy declarations so mypy knows the types set by argparse at runtime.
    longueur: float = 110.0
    hauteur: float = 40.0
    radius: float = 5.0
    inner_border: bool = True
    border_margin: float = 3.0
    label_text: str = "Label"
    text_align: str = "middle center"
    # Font settings – set by FontSettings group (prefix "Font")
    Font_font: str = "sans-serif"
    Font_size: float = 10.0
    Font_bold: bool = False
    Font_italic: bool = False

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(FontSettings, size=self.Font_size)

        self.argparser.add_argument(
            "--longueur", action="store", type=float, default=self.longueur,
            help="Total width of the label [mm]")
        self.argparser.add_argument(
            "--hauteur", action="store", type=float, default=self.hauteur,
            help="Total height of the label [mm]")
        self.argparser.add_argument(
            "--radius", action="store", type=float, default=self.radius,
            help="Corner radius [mm] (0 = sharp corners)")
        self.argparser.add_argument(
            "--inner_border", action="store", type=boolarg, default=self.inner_border,
            help="Add an inner border line parallel to the outer edge")
        self.argparser.add_argument(
            "--border_margin", action="store", type=float, default=self.border_margin,
            help="Distance between the outer cut and the inner border line [mm]")
        self.argparser.add_argument(
            "--label_text", action="store", type=str, default=self.label_text,
            help="Text to engrave on the label (leave blank to omit)")
        self.argparser.add_argument(
            "--text_align", action="store", type=str, default=self.text_align,
            choices=[
                "middle center", "middle left", "middle right",
                "top center", "top left", "top right",
                "bottom center", "bottom left", "bottom right",
            ],
            help="Alignment of the engraved text inside the label")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _rounded_rect(self, w: float, h: float, r: float) -> None:
        """Draw a rounded rectangle starting from the bottom-left corner."""
        r = max(0.0, min(r, w / 2.0, h / 2.0))
        self.moveTo(r, 0)
        self.polyline(
            w - 2 * r, (90, r),
            h - 2 * r, (90, r),
            w - 2 * r, (90, r),
            h - 2 * r, (90, r),
        )

    # ------------------------------------------------------------------
    # Main render
    # ------------------------------------------------------------------

    def render(self) -> None:
        w = self.longueur
        h = self.hauteur
        r = self.radius
        margin = self.border_margin

        if self.move(w, h, "right", before=True):
            return

        ctx = cast(Context, self.ctx)

        # ── 2. Outer perimeter cut (OUTER_CUT = black) ──────────────────
        self.set_source_color(Color.OUTER_CUT)
        with self.saved_context():
            self._rounded_rect(w, h, r)
            ctx.stroke()

        # ── 3. Inner border line (INNER_CUT = blue, optional) ────────────
        if self.inner_border and margin > 0:
            iw = w - 2 * margin
            ih = h - 2 * margin
            if iw > 0 and ih > 0:
                ir = max(0.0, r - margin)
                self.set_source_color(Color.INNER_CUT)
                with self.saved_context():
                    self.moveTo(margin, margin)
                    self._rounded_rect(iw, ih, ir)
                    ctx.stroke()

        # ── 4. Engraved text (ETCHING = green) ───────────────────────────
        if self.label_text and self.Font_size > 0:
            align = self.text_align
            tokens = align.split()
            valign_token = tokens[0] if tokens else "middle"
            halign_token = tokens[1] if len(tokens) >= 2 else "center"

            x_positions = {"left": margin + self.Font_size * 0.3,
                           "center": w / 2.0,
                           "right": w - margin - self.Font_size * 0.3}
            y_positions = {"top": h - margin - self.Font_size * 0.1,
                           "middle": h / 2.0,
                           "bottom": margin + self.Font_size * 0.1}

            tx = x_positions.get(halign_token, w / 2.0)
            ty = y_positions.get(valign_token, h / 2.0)

            ctx.set_font(self.Font_font, bold=self.Font_bold, italic=self.Font_italic)
            self.text(
                self.label_text,
                x=tx, y=ty, angle=0,
                align=align,
                fontsize=self.Font_size,
                color=Color.ETCHING,
            )

        # ── 5. Finalise move ─────────────────────────────────────────────
        self.move(w, h, "right")
