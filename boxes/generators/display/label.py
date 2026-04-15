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
from boxes.settings.font_settings import FontSettings
from boxes.settings.label_settings import LabelSettings
from boxes.settings.text_settings import TextSettings


class Label(Boxes):
    """Rectangular label with rounded corners, optional inner border line and engraved text."""

    ui_group = "Display"

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

    # mypy stubs – values set by argparse at runtime.
    Label_longueur:      float = 110.0
    Label_hauteur:       float = 40.0
    Label_radius:        float = 5.0
    Label_inner_border:  bool  = True
    Label_border_margin: float = 3.0
    Text_text:           str   = "Label"
    Text_x:              float = 0.0
    Text_y:              float = 0.0
    Text_step:           float = 1.0
    Text_outline:        float = 0.0
    Font_font:           str   = "sans-serif"
    Font_size:           float = 10.0
    Font_bold:           bool  = False
    Font_italic:         bool  = False

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(LabelSettings,
                             longueur=self.Label_longueur,
                             hauteur=self.Label_hauteur,
                             radius=self.Label_radius,
                             inner_border=self.Label_inner_border,
                             border_margin=self.Label_border_margin)
        self.addSettingsArgs(TextSettings, text=self.Text_text)
        self.addSettingsArgs(FontSettings, size=self.Font_size)

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
        w = self.Label_longueur
        h = self.Label_hauteur
        r = self.Label_radius
        margin = self.Label_border_margin

        if self.move(w, h, "right", before=True):
            return

        ctx = cast(Context, self.ctx)

        # ── Outer perimeter cut (OUTER_CUT = black) ──────────────────────
        self.set_source_color(Color.OUTER_CUT)
        with self.saved_context():
            self._rounded_rect(w, h, r)
            ctx.stroke()

        # ── Inner border line (INNER_CUT = blue, optional) ───────────────
        if self.Label_inner_border and margin > 0:
            iw = w - 2 * margin
            ih = h - 2 * margin
            if iw > 0 and ih > 0:
                ir = max(0.0, r - margin)
                self.set_source_color(Color.INNER_CUT)
                with self.saved_context():
                    self.moveTo(margin, margin)
                    self._rounded_rect(iw, ih, ir)
                    ctx.stroke()

        # ── Engraved text (ETCHING = green) ──────────────────────────────
        if self.Text_text and self.Font_size > 0:
            tx = w / 2.0 + self.Text_x
            ty = h / 2.0 + self.Text_y
            ctx.set_font(self.Font_font, bold=self.Font_bold, italic=self.Font_italic)
            self.text(
                self.Text_text,
                x=tx, y=ty, angle=0,
                align="middle center",
                fontsize=self.Font_size,
                color=Color.ETCHING,
                outline_lw=self.Text_outline,
            )

        # ── Finalise move ─────────────────────────────────────────────────
        self.move(w, h, "right")
