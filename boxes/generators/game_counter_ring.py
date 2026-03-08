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
from boxes.settings.crenel_settings import CrenelSettings
from boxes.settings.score_settings import ScoreSettings


class GameCounterRing(Boxes):
    """Ring-dial game point counter – three concentric pieces cut together"""

    ui_group = "GameAccessory"

    description = """
A three-piece circular point counter for board games.

All three pieces are laid out **concentrically** in the SVG so they can be
cut in a single laser pass with minimal material waste.

* **Piece A – Outer ring**: the moving frame. Score numbers are engraved
  around the *inner* face. The player spins this disc to select the score.
* **Piece B – Inner disc**: the fixed center. A pointer is engraved near
  the top edge to indicate the current score on the ring.
* **Piece C – Base disc**: a plain disc the same size as the outer ring.
  Piece B is glued to Piece C before assembly. No magnets are used.

**Assembly**
1. Glue Piece B (pointer disc) on top of Piece C (base disc) – an optional
   small hole at the center of both pieces helps with alignment.
2. Drop Piece A (ring) on top of the glued B+C stack.
3. The ring spins freely.
4. Spin Piece A to count up / down; Piece B stays fixed.

**Pointer styles**

* ``triangle`` – outlined equilateral-ish triangle pointing toward the ring.
* ``circle``   – small engraved circle at the top of the disc.
* ``rectangle`` – outlined rectangle near the top of the disc.
* ``line``     – single radial line from the disc center to near the edge.
"""

    # Dummy declarations for mypy – overwritten by argparse at runtime.
    outer_radius: float = 50.0
    inner_radius: float = 32.0
    score_min: int = 0
    score_max: int = 9
    score_radius: float = 0.0
    score_inv: bool = False
    font_size: float = 8
    font_font: str = "sans-serif"
    font_bold: bool = False
    font_italic: bool = False
    pointer_size: float = 6
    pointer_style: str = "triangle"
    crenel_enabled: bool = False
    crenel_depth: float = 2.0
    crenel_shape: str = "symmetric"
    crenel_rounded: bool = True
    crenel_radius: float = 1
    play: float = 0.3
    burn: float = 0.1

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(ScoreSettings, prefix="score")
        self.addSettingsArgs(FontSettings, prefix="font", size=self.font_size)
        self.addSettingsArgs(CrenelSettings, prefix="crenel")

        self.argparser.add_argument(
            "--outer_radius", action="store", type=float, default=self.outer_radius,
            help="Outer radius of the ring frame [mm]")
        self.argparser.add_argument(
            "--inner_radius", action="store", type=float, default=self.inner_radius,
            help="Inner radius of the ring / radius of the dial disc [mm]")
        self.argparser.add_argument(
            "--pointer_size", action="store", type=float, default=self.pointer_size,
            help="Size of the pointer shape engraved on the dial [mm]")
        self.argparser.add_argument(
            "--pointer_style", action="store", type=str, default=self.pointer_style,
            choices=["triangle", "circle", "rectangle", "line"],
            help="Shape of the pointer engraved on Piece B")
        self.argparser.add_argument(
            "--play", action="store", type=float, default=self.play,
            help="Radial clearance between ring inner edge and dial [mm]")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _draw_score_numbers(self, cx: float, cy: float,
                             label_r: float, ctx: Context) -> None:
        """Engrave score numbers evenly around a circle of radius *label_r*."""
        n = self.score_max - self.score_min + 1
        if n < 1:
            return
        angle_step = 360.0 / n
        orientation = 180 if self.score_inv else 0

        ctx.set_font(self.font_font, bold=self.font_bold, italic=self.font_italic)
        self.set_source_color(Color.ETCHING)
        for i, score in enumerate(range(self.score_min, self.score_max + 1)):
            angle_deg = i * angle_step
            angle_rad = math.radians(angle_deg)
            tx = cx + label_r * math.sin(angle_rad)
            ty = cy + label_r * math.cos(angle_rad)
            with self.saved_context():
                self.text(str(score), x=tx, y=ty,
                          angle=-angle_deg + orientation,
                          align="middle center",
                          fontsize=self.font_size, color=Color.ETCHING)
        ctx.stroke()

    # --- pointer style helpers ----------------------------------------
    # All helpers draw at disc center (cx, cy) with disc radius disc_r.
    # pointer_size (ps) is the characteristic size in mm.

    def _pointer_triangle(self, cx: float, cy: float,
                           disc_r: float, ps: float, ctx: Context) -> None:
        """Outlined isosceles triangle pointing toward the rim (upward on screen)."""
        # Tip: ps*0.3 inward from the rim; base: ps below the tip.
        tip_x  = cx
        tip_y  = cy + disc_r - ps * 0.3
        bl_x   = cx - ps * 0.5
        bl_y   = cy + disc_r - ps * 1.3
        br_x   = cx + ps * 0.5
        br_y   = cy + disc_r - ps * 1.3

        self.set_source_color(Color.ETCHING)
        ctx.move_to(tip_x, tip_y)
        ctx.line_to(br_x,  br_y)
        ctx.line_to(bl_x,  bl_y)
        ctx.line_to(tip_x, tip_y)
        ctx.stroke()

    def _pointer_circle(self, cx: float, cy: float,
                         disc_r: float, ps: float, ctx: Context) -> None:
        """Small engraved circle near the top of the disc."""
        # Center of the circle sits ps*0.8 inward from the rim.
        circle_cx = cx
        circle_cy = cy + disc_r - ps * 0.8
        circle_r  = ps * 0.4

        self.set_source_color(Color.ETCHING)
        # self.circle() handles the full 360° arc correctly
        self.circle(circle_cx, circle_cy, circle_r)
        ctx.stroke()

    def _pointer_rectangle(self, cx: float, cy: float,
                             disc_r: float, ps: float, ctx: Context) -> None:
        """Outlined rectangle near the top of the disc."""
        hw = ps * 0.5          # half-width
        h  = ps * 0.8          # height of the rectangle
        top_y    = cy + disc_r - ps * 0.3
        bottom_y = top_y - h

        self.set_source_color(Color.ETCHING)
        ctx.move_to(cx - hw, bottom_y)
        ctx.line_to(cx + hw, bottom_y)
        ctx.line_to(cx + hw, top_y)
        ctx.line_to(cx - hw, top_y)
        ctx.line_to(cx - hw, bottom_y)
        ctx.stroke()

    def _pointer_line(self, cx: float, cy: float,
                       disc_r: float, ps: float, ctx: Context) -> None:
        """Radial line from disc center toward the rim."""
        # Line starts ps inward from rim and ends ps*0.1 from rim.
        start_y = cy + ps
        end_y   = cy + disc_r - ps * 0.1

        self.set_source_color(Color.ETCHING)
        ctx.move_to(cx, start_y)
        ctx.line_to(cx, end_y)
        ctx.stroke()

    def _draw_pointer(self, cx: float, cy: float,
                       disc_r: float, ctx: Context) -> None:
        """Dispatch to the selected pointer style."""
        ps    = self.pointer_size
        style = self.pointer_style if self.pointer_style in (
            "triangle", "circle", "rectangle", "line") else "triangle"
        fn = getattr(self, f"_pointer_{style}")
        fn(cx, cy, disc_r, ps, ctx)

    def _draw_outer_crenels(self, cx: float, cy: float,
                            ro: float, ctx: Context) -> None:
        """Draw the outer perimeter of Piece A with gear-like crenels.

        One notch (gap) per score value, evenly distributed around 360°.
        Tooth and gap each occupy half a sector (50 % duty cycle).

        ``crenel_shape``:
          * ``symmetric`` – straight walls perpendicular to the sector bisector
            (true rectangular slots, geometrically symmetric).
          * ``radial``    – walls are radial lines converging toward the center.

        ``crenel_rounded`` adds fillets of radius ``crenel_radius`` at the four
        inner corners of each notch.
        """
        n = self.score_max - self.score_min + 1
        if n < 1:
            return

        depth   = self.crenel_depth
        radial  = (self.crenel_shape == "radial")
        rounded = self.crenel_rounded
        r_corn  = self.crenel_radius if rounded else 0.0
        ri      = ro - depth

        angle_step = 2.0 * math.pi / n
        half       = angle_step / 2.0
        quarter    = half / 2.0

        self.set_source_color(Color.OUTER_CUT)
        start_angle = math.pi / 2.0

        def pt_on(r: float, a: float) -> tuple[float, float]:
            return cx + r * math.cos(a), cy + r * math.sin(a)

        def sym_inner_corners(center_a_in: float) -> tuple[
                tuple[float, float], tuple[float, float]]:
            """Left and right inner corners of a rectangular notch."""
            bx_in = math.cos(center_a_in)
            by_in = math.sin(center_a_in)
            ox_l, oy_l = pt_on(ro, center_a_in - quarter)
            ox_r, oy_r = pt_on(ro, center_a_in + quarter)
            return (ox_l - depth * bx_in, oy_l - depth * by_in), \
                   (ox_r - depth * bx_in, oy_r - depth * by_in)

        # Start on the outer rim at the very beginning of sector 0's gap.
        ctx.move_to(*pt_on(ro, start_angle - half))

        for i in range(n):
            center_a = start_angle + i * angle_step
            tooth_l  = center_a - quarter   # left  outer edge of tooth
            tooth_r  = center_a + quarter   # right outer edge of tooth
            gap_end  = center_a + half      # end of the following gap

            if radial:
                if r_corn <= 0.0 or ri <= 0.0:
                    # Gap arc → left wall down → floor arc → right wall up
                    ctx.arc(cx, cy, ro,  center_a - half, tooth_l)
                    ctx.line_to(*pt_on(ri, tooth_l))
                    ctx.arc(cx, cy, ri,  tooth_l,         tooth_r)
                    ctx.line_to(*pt_on(ro, tooth_r))
                else:
                    da_o = min(r_corn / ro, quarter * 0.45)
                    da_i = min(r_corn / ri, quarter * 0.45)
                    ctx.arc(cx, cy, ro, center_a - half, tooth_l - da_o)
                    ctx.curve_to(*pt_on(ri, tooth_l - da_i),
                                 *pt_on(ri, tooth_l - da_i),
                                 *pt_on(ri, tooth_l + da_i))
                    ctx.arc(cx, cy, ri, tooth_l + da_i,  tooth_r - da_i)
                    ctx.curve_to(*pt_on(ro, tooth_r + da_o),
                                 *pt_on(ro, tooth_r + da_o),
                                 *pt_on(ro, tooth_r + da_o))
            else:
                il, ir = sym_inner_corners(center_a)
                bx = math.cos(center_a)
                by = math.sin(center_a)
                if r_corn <= 0.0:
                    ctx.arc(cx, cy, ro, center_a - half, tooth_l)
                    ctx.line_to(*il)
                    ctx.line_to(*ir)
                    ctx.line_to(*pt_on(ro, tooth_r))
                else:
                    da_o = min(r_corn / ro, quarter * 0.4)
                    rc   = min(r_corn, ro * quarter * 0.4)
                    ctx.arc(cx, cy, ro, center_a - half, tooth_l - da_o)
                    fl_ctrl = (cx + ro * math.cos(tooth_l) - rc * bx,
                               cy + ro * math.sin(tooth_l) - rc * by)
                    ctx.curve_to(*fl_ctrl, *fl_ctrl, *il)
                    ctx.line_to(*ir)
                    fr_ctrl = (cx + ro * math.cos(tooth_r) - rc * bx,
                               cy + ro * math.sin(tooth_r) - rc * by)
                    ctx.curve_to(*fr_ctrl, *fr_ctrl, *pt_on(ro, tooth_r + da_o))

        # Close the path: arc back to the starting point and close.
        ctx.arc(cx, cy, ro,
                start_angle + n * angle_step - half,
                start_angle - half + 2.0 * math.pi)
        ctx.stroke()

    # ------------------------------------------------------------------
    # Pieces
    # ------------------------------------------------------------------

    def _piece_a_ring(self, cx: float, cy: float, ctx: Context) -> None:
        """Piece A – outer ring: outer perimeter + inner hole + score numbers."""
        ro = self.outer_radius
        ri = self.inner_radius - self.play

        # Outer perimeter cut – plain circle or notched gear rim
        if self.crenel_enabled:
            self._draw_outer_crenels(cx, cy, ro, ctx)
        else:
            self.set_source_color(Color.OUTER_CUT)
            self.circle(cx, cy, ro)

        # Inner hole cut
        self.set_source_color(Color.INNER_CUT)
        self.hole(cx, cy, r=ri)

        # Score numbers – auto or explicit label radius
        if self.score_radius > 0.0:
            label_r = self.score_radius
        else:
            label_r = (ro + ri) / 2.0
        self._draw_score_numbers(cx, cy, label_r, ctx)

    def _piece_b_disc(self, cx: float, cy: float, ctx: Context) -> None:
        """Piece B – inner disc: outer cut + engraved pointer."""
        ri = self.inner_radius - self.play - self.burn

        # Outer perimeter cut
        self.set_source_color(Color.OUTER_CUT)
        self.circle(cx, cy, ri)

        # Pointer engraving
        self._draw_pointer(cx, cy, ri, ctx)

    def _piece_c_base(self, cx: float, cy: float) -> None:
        """Piece C – base disc cut (same outer radius as Piece A)."""
        self.set_source_color(Color.OUTER_CUT)
        self.circle(cx, cy, self.outer_radius)

    # ------------------------------------------------------------------
    # Main render
    # ------------------------------------------------------------------

    def render(self) -> None:
        ro = self.outer_radius

        # Piece A+B share the same ro*2 bounding square (drawn concentric).
        # Piece C is a separate ro*2 square placed to the right.
        total_w = ro * 2 + self.spacing + ro * 2
        total_h = ro * 2

        if self.move(total_w, total_h, "right", before=True):
            return

        ctx = cast(Context, self.ctx)

        # Piece A (ring) + Piece B (pointer disc) – both centred at (ro, ro)
        self._piece_a_ring(ro, ro, ctx)
        self._piece_b_disc(ro, ro, ctx)

        # Piece C – base disc (same size as ring), placed to the right
        c_cx = ro * 2 + self.spacing + ro
        self._piece_c_base(c_cx, ro)

        self.move(total_w, total_h, "right")
