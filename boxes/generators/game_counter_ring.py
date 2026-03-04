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


class GameCounterRing(Boxes):
    """Ring-dial game point counter – three concentric pieces cut together"""

    ui_group = "GameAccessory"

    description = """
A three-piece circular point counter for board games.

All three pieces are laid out **concentrically** in the SVG so they can be
cut in a single laser pass with minimal material waste.

* **Piece A – Outer ring**: the moving frame. Score numbers are engraved
  around the *inner* face. The player spins this disc to select the score.
* **Piece B – Inner disc**: the fix center, a pointer triangle is
  engraved at the top.
* **Piece C – Base disc**: a plain disc the same size as the Outer ring external.
  Piece B is glued to Piece C before assembly. No magnets are used.

**Assembly**
1. Glue Piece B (arrow) on top of Piece C (base) – an optional small hole can be added to the centre of Piece C and B to help with alignment.
2. Drop the Piece A (ring) on top of glued B+C .
3. The ring freely.
4. Spin Piece A to count up / down; Piece B stays fixed.
"""

    # Dummy declarations for mypy – overwritten by argparse at runtime.
    outer_radius: float = 50.0
    inner_radius: float = 32.0
    score_min: int = 0
    score_max: int = 20
    font_size: float = 4.0
    pointer_size: float = 4.0
    play: float = 0.3
    burn: float = 0.1

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.argparser.add_argument(
            "--outer_radius", action="store", type=float, default=50.0,
            help="Outer radius of the ring frame [mm]")
        self.argparser.add_argument(
            "--inner_radius", action="store", type=float, default=32.0,
            help="Inner radius of the ring / radius of the dial disc [mm]")
        self.argparser.add_argument(
            "--score_min", action="store", type=int, default=0,
            help="Minimum score value shown on the ring")
        self.argparser.add_argument(
            "--score_max", action="store", type=int, default=20,
            help="Maximum score value shown on the ring")
        self.argparser.add_argument(
            "--font_size", action="store", type=float, default=4.0,
            help="Font size for score numbers [mm]")
        self.argparser.add_argument(
            "--pointer_size", action="store", type=float, default=4.0,
            help="Height of the pointer triangle engraved on the dial [mm]")
        self.argparser.add_argument(
            "--play", action="store", type=float, default=0.3,
            help="Radial clearance between ring inner edge and dial [mm]")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _draw_score_numbers(self, cx: float, cy: float,
                             label_r: float, ctx: Context) -> None:
        """Engrave score numbers evenly around a circle of radius label_r."""
        n = self.score_max - self.score_min + 1
        if n < 1:
            return
        angle_step = 360.0 / n
        self.set_source_color(Color.ETCHING)
        for i, score in enumerate(range(self.score_min, self.score_max + 1)):
            angle_deg = i * angle_step
            angle_rad = math.radians(angle_deg)
            tx = cx + label_r * math.sin(angle_rad)
            ty = cy + label_r * math.cos(angle_rad)
            self.text(str(score), x=tx, y=ty, angle=-angle_deg,
                      align="middle center",
                      fontsize=self.font_size, color=Color.ETCHING)
        ctx.stroke()

    def _draw_pointer(self, cx: float, cy: float,
                       disc_r: float, ctx: Context) -> None:
        """Engrave a filled pointer triangle near the top edge of the dial."""
        ps = self.pointer_size
        tip_x, tip_y = cx, cy + disc_r - ps * 0.3
        bl_x, bl_y = cx - ps * 0.5, cy + disc_r - ps * 1.3
        br_x, br_y = cx + ps * 0.5, cy + disc_r - ps * 1.3
        self.set_source_color(Color.SOLID_FILL)
        for x0, y0, x1, y1 in [
            (tip_x, tip_y, br_x, br_y),
            (br_x, br_y, bl_x, bl_y),
            (bl_x, bl_y, tip_x, tip_y),
        ]:
            self.moveTo(x0, y0)
            dx, dy = x1 - x0, y1 - y0
            length = math.hypot(dx, dy)
            angle = math.degrees(math.atan2(dy, dx))
            self.moveTo(0, 0, angle)
            self.edge(length)
        ctx.stroke()

    # ------------------------------------------------------------------
    # Pieces
    # ------------------------------------------------------------------

    def _piece_a_ring(self, cx: float, cy: float, ctx: Context) -> None:
        """Piece A – outer ring: outer perimeter + inner hole + score numbers."""
        ro = self.outer_radius
        ri = self.inner_radius - self.play

        # Outer perimeter
        self.set_source_color(Color.OUTER_CUT)
        self.circle(cx, cy, ro)

        # Inner hole cut – red
        self.set_source_color(Color.INNER_CUT)
        self.hole(cx, cy, r=ri)

        # Score numbers – black (non-filled engraving)
        label_r = (ro + ri) / 2.0
        self._draw_score_numbers(cx, cy, label_r, ctx)

    def _piece_b_arow(self, cx: float, cy: float, ctx: Context) -> None:
        """Piece B – outer cut + filled pointer triangle."""
        ri = self.inner_radius - self.play - self.burn

        # Outer perimeter cut
        self.set_source_color(Color.OUTER_CUT)
        self.circle(cx, cy, ri)

        # Filled pointer
        self._draw_pointer(cx, cy, ri, ctx)

    def _piece_c_base(self, cx: float, cy: float) -> None:
        """Piece C – base disc cut."""
        self.set_source_color(Color.OUTER_CUT)
        self.circle(cx, cy, self.outer_radius)

    # ------------------------------------------------------------------
    # Main render
    # ------------------------------------------------------------------

    def render(self) -> None:
        ro = self.outer_radius
        disc_r = self.inner_radius - self.play
        disc_d = disc_r * 2

        # Piece A+B share the same ro*2 square (drawn concentric).
        # Piece C is a separate ro*2 square placed to the right.
        total_w = ro * 2 + self.spacing + ro * 2
        total_h = ro * 2

        if self.move(total_w, total_h, "right", before=True):
            return

        ctx = cast(Context, self.ctx)

        # Piece A (ring) + Piece B (arrow disc) – both centred at (ro, ro)
        self._piece_a_ring(ro, ro, ctx)
        self._piece_b_arow(ro, ro, ctx)

        # Piece C – base disc (same size as ring), to the right
        c_cx = ro * 2 + self.spacing + ro
        self._piece_c_base(c_cx, ro)

        self.move(total_w, total_h, "right")
