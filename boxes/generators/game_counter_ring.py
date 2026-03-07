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


class GameCounterRing(Boxes):
    """Ring-dial game point counter – three concentric pieces cut together"""

    ui_group = "GameAccessory"

    description = """
A three-piece circular point counter for board games.

All three pieces are laid out **concentrically** in the SVG so they can be
cut in a single laser pass with minimal material waste.

* **Piece A – Outer ring**: the moving frame. Score numbers are engraved
  around the *inner* face. The player spins this disc to select the score.
* **Piece B – Inner disc**: the fixed centre. A pointer is engraved near
  the top edge to indicate the current score on the ring.
* **Piece C – Base disc**: a plain disc the same size as the outer ring.
  Piece B is glued to Piece C before assembly. No magnets are used.

**Assembly**
1. Glue Piece B (pointer disc) on top of Piece C (base disc) – an optional
   small hole at the centre of both pieces helps with alignment.
2. Drop Piece A (ring) on top of the glued B+C stack.
3. The ring spins freely.
4. Spin Piece A to count up / down; Piece B stays fixed.

**Pointer styles**

* ``triangle`` – outlined equilateral-ish triangle pointing toward the ring.
* ``circle``   – small engraved circle at the top of the disc.
* ``rectangle`` – outlined rectangle near the top of the disc.
* ``line``     – single radial line from the disc centre to near the edge.
"""

    # Dummy declarations for mypy – overwritten by argparse at runtime.
    outer_radius: float = 50.0
    inner_radius: float = 32.0
    score_min: int = 0
    score_max: int = 20
    Font_size: float = 4.0
    Font_font: str = "sans-serif"
    Font_bold: bool = False
    Font_italic: bool = False
    label_radius: float = 0.0
    label_invert: bool = False
    pointer_size: float = 4.0
    pointer_style: str = "triangle"
    notch_outer: bool = False
    notch_depth: float = 2.0
    play: float = 0.3
    burn: float = 0.1

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(FontSettings, size=self.Font_size)

        self.argparser.add_argument(
            "--outer_radius", action="store", type=float, default=self.outer_radius,
            help="Outer radius of the ring frame [mm]")
        self.argparser.add_argument(
            "--inner_radius", action="store", type=float, default=self.inner_radius,
            help="Inner radius of the ring / radius of the dial disc [mm]")
        self.argparser.add_argument(
            "--score_min", action="store", type=int, default=self.score_min,
            help="Minimum score value shown on the ring")
        self.argparser.add_argument(
            "--score_max", action="store", type=int, default=self.score_max,
            help="Maximum score value shown on the ring")
        self.argparser.add_argument(
            "--label_radius", action="store", type=float, default=self.label_radius,
            help="Radius at which score numbers are placed on Piece A [mm]. "
                 "0 = auto (midpoint between inner and outer radii)")
        self.argparser.add_argument(
            "--label_invert", action="store", type=boolarg, default=self.label_invert,
            help="Invert the orientation of score number labels")
        self.argparser.add_argument(
            "--pointer_size", action="store", type=float, default=self.pointer_size,
            help="Size of the pointer shape engraved on the dial [mm]")
        self.argparser.add_argument(
            "--pointer_style", action="store", type=str, default=self.pointer_style,
            choices=["triangle", "circle", "rectangle", "line"],
            help="Shape of the pointer engraved on Piece B")
        self.argparser.add_argument(
            "--notch_outer", action="store", type=boolarg, default=self.notch_outer,
            help="Add gear-like notches on the outer rim of Piece A (one notch per score value)")
        self.argparser.add_argument(
            "--notch_depth", action="store", type=float, default=self.notch_depth,
            help="Depth of each outer notch [mm]")
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
        orientation = 180 if self.label_invert else 0

        ctx.set_font(self.Font_font, bold=self.Font_bold, italic=self.Font_italic)
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
                          fontsize=self.Font_size, color=Color.ETCHING)
        ctx.stroke()

    # --- pointer style helpers ----------------------------------------
    # All helpers draw at disc centre (cx, cy) with disc radius disc_r.
    # pointer_size (ps) is the characteristic size in mm.

    def _pointer_triangle(self, cx: float, cy: float,
                           disc_r: float, ps: float, ctx: Context) -> None:
        """Outlined isoceles triangle pointing toward the rim (upward on screen)."""
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
        # Centre of the circle sits ps*0.8 inward from the rim.
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
        """Radial line from disc centre toward the rim."""
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

    def _draw_outer_notches(self, cx: float, cy: float,
                             ro: float, ctx: Context) -> None:
        """Draw the outer perimeter of Piece A with gear-like rectangular notches.

        One notch (tooth gap) is cut per score value, evenly distributed
        around the full 360°.  The tooth width equals the gap width so the
        duty cycle is 50 %.  The notch depth is ``self.notch_depth``.
        """
        n = self.score_max - self.score_min + 1
        if n < 1:
            return

        depth = self.notch_depth
        ri_notch = ro - depth          # bottom of the notch (inner radius)

        angle_step = 2.0 * math.pi / n   # full sector per score value (tooth + gap)
        half = angle_step / 2.0           # half sector = tooth half-angle
        quarter = half / 2.0              # quarter = boundary between tooth and gap

        self.set_source_color(Color.OUTER_CUT)

        # Start angle: centre of the first tooth, offset so a tooth sits at
        # the top (π/2 in math coords = pointing up on screen after Y-flip).
        start_angle = math.pi / 2.0

        # Build the path: for each of the n sectors draw  tooth → gap.
        # A sector spans [start_angle + i*angle_step - half,
        #                 start_angle + i*angle_step + half]
        # The tooth occupies the outer half of the sector (±quarter around centre).
        # The gap  occupies the remaining ±(half - quarter) on each side, at ri_notch.

        def pt_outer(a: float) -> tuple[float, float]:
            return (cx + ro * math.cos(a), cy + ro * math.sin(a))

        def pt_inner(a: float) -> tuple[float, float]:
            return (cx + ri_notch * math.cos(a), cy + ri_notch * math.sin(a))

        # First point: start of first gap (left edge of sector 0)
        first_a = start_angle - half
        x0, y0 = pt_inner(first_a)
        ctx.move_to(x0, y0)

        for i in range(n):
            centre_a = start_angle + i * angle_step
            gap_start  = centre_a - half        # left edge of sector  (inner)
            tooth_start = centre_a - quarter    # left edge of tooth   (outer)
            tooth_end   = centre_a + quarter    # right edge of tooth  (outer)
            gap_end     = centre_a + half       # right edge of sector (inner)

            # --- gap arc at ri_notch from gap_start → tooth_start ---
            # Use a single arc at the inner radius.
            ctx.arc(cx, cy, ri_notch, gap_start, tooth_start)

            # --- step up to outer radius ---
            ctx.line_to(*pt_outer(tooth_start))

            # --- tooth arc at ro from tooth_start → tooth_end ---
            ctx.arc(cx, cy, ro, tooth_start, tooth_end)

            # --- step back down to inner radius ---
            ctx.line_to(*pt_inner(tooth_end))

        # Close path back to the starting inner point
        ctx.line_to(x0, y0)
        ctx.stroke()

    # ------------------------------------------------------------------
    # Pieces
    # ------------------------------------------------------------------

    def _piece_a_ring(self, cx: float, cy: float, ctx: Context) -> None:
        """Piece A – outer ring: outer perimeter + inner hole + score numbers."""
        ro = self.outer_radius
        ri = self.inner_radius - self.play

        # Outer perimeter cut – plain circle or notched gear rim
        if self.notch_outer:
            self._draw_outer_notches(cx, cy, ro, ctx)
        else:
            self.set_source_color(Color.OUTER_CUT)
            self.circle(cx, cy, ro)

        # Inner hole cut
        self.set_source_color(Color.INNER_CUT)
        self.hole(cx, cy, r=ri)

        # Score numbers – auto or explicit label radius
        if self.label_radius > 0.0:
            label_r = self.label_radius
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
