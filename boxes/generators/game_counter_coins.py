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
from boxes.args import IntStepper, FloatStepper
from boxes.drawing import Context
from boxes.settings.font_settings import FontSettings


class GameCounterCoins(Boxes):
    """Coin-stack game point counter – top disc notch reads score off bottom coin"""

    ui_group = "GameAccessory"

    description = """
A two-piece stacked coin counter for board games.

The **bottom coin** (Piece A) has the score scale engraved around its rim.
The **top disc** (Piece B) has a notch on its edge: rotate it to align the
notch with the current score on Piece A below it.
Both pieces are held together by a central magnet so they spin freely.

Assembly: insert magnet into both pieces → stack face-to-face → enjoy!

"""

    # Dummy declarations for mypy – overwritten by argparse at runtime.
    burn: float = 0.1
    coin_radius: float = 25.0
    magnet_diameter: float = 4.0
    score_min: int = 0
    score_max: int = 9
    label_radius: float = 0.0
    font_size: float = 8.0
    font_font: str = "sans-serif"
    font_bold: bool = False
    font_italic: bool = False
    label_invert: bool = False
    notch_width: float = 15.0
    notch_depth: float = 0.0
    notch_style: str = "oval"
    play: float = 0.2

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(FontSettings,
                             prefix="font",
                             size=self.font_size)

        self.argparser.add_argument(
            "--coin_radius", action="store", type=float, default=self.coin_radius,
            help="Outer radius of both discs [mm]")
        self.argparser.add_argument(
            "--magnet_diameter", action="store", type=float, default=self.magnet_diameter,
            help="Diameter of the central cylindrical magnet [mm]")
        self.argparser.add_argument(
            "--score_min", action="store", type=IntStepper(1), default=self.score_min,
            help="Minimum score value displayed on Piece A")
        self.argparser.add_argument(
            "--score_max", action="store", type=IntStepper(1), default=self.score_max,
            help="Maximum score value displayed on Piece A")
        self.argparser.add_argument(
            "--label_invert", action="store", type=boolarg, default=self.label_invert,
            help="Invert the font orientation")
        self.argparser.add_argument(
            "--label_radius", action="store", type=FloatStepper(0.5), default=self.label_radius,
            help="Radius at which score numbers are placed on Piece A [mm]. "
                 "0 = auto (coin_radius − font_size × 0.5)")
        self.argparser.add_argument(
            "--notch_width", action="store", type=FloatStepper(1.0), default=self.notch_width,
            help="Width of the reading notch on Piece B [mm]")
        self.argparser.add_argument(
            "--notch_depth", action="store", type=FloatStepper(1.0), default=self.notch_depth,
            help="Depth of the reading notch on Piece B [mm]. "
                 "0 = auto (notch_width / 2)")
        self.argparser.add_argument(
            "--notch_style", action="store", type=str, default=self.notch_style,
            choices=["circular", "triangular", "oval", "trapezoid"],
            help="Shape of the reading notch on Piece B")
        self.argparser.add_argument(
            "--play", action="store", type=float, default=self.play,
            help="Radial play between the two discs [mm]")

    # ------------------------------------------------------------------
    # Piece A – bottom coin with score scale
    # ------------------------------------------------------------------
    def bottom_coin(self, move: str = "") -> None:
        """Bottom disc: outer cut + central magnet hole + engraved score numbers."""
        r = self.coin_radius
        md = self.magnet_diameter

        if self.move(r * 2, r * 2, move, before=True):
            return

        ctx = cast(Context, self.ctx)

        # Outer perimeter cut
        self.set_source_color(Color.OUTER_CUT)
        self.circle(r, r, r)
        ctx.stroke()

        # Central magnet hole
        self.hole(r, r, d=md)

        # Score numbers
        n = self.score_max - self.score_min + 1
        angle_step = 360.0 / n

        if self.label_invert:
            orientation = 180
            offset_label_radius = self.font_size * 0.4
        else:
            orientation = 0
            offset_label_radius = self.font_size * 0.6

        label_r = self.label_radius if self.label_radius > 0.0 else r - offset_label_radius

        ctx.set_font(self.font_font, bold=self.font_bold, italic=self.font_italic)
        self.set_source_color(Color.ETCHING)
        for i, score in enumerate(range(self.score_min, self.score_max + 1)):
            angle_deg = i * angle_step
            angle_rad = math.radians(angle_deg)
            tx = r + label_r * math.sin(angle_rad)
            ty = r + label_r * math.cos(angle_rad)
            with self.saved_context():
                self.text(str(score), x=tx, y=ty, angle=-angle_deg + orientation,
                          align="middle center",
                          fontsize=self.font_size, color=Color.ETCHING)

        self.move(r * 2, r * 2, move)

    # ------------------------------------------------------------------
    # Piece B – top disc with reading notch
    # ------------------------------------------------------------------

    # All _notch_* helpers share the same calling convention:
    #   ctx       – the Cairo context (pen already at the LEFT rim endpoint)
    #   cx, cy    – disc center in math coordinates
    #   disc_r    – disc radius (with burn)
    #   a_left    – math angle of left  rim endpoint (= π/2 + α)
    #   a_right   – math angle of right rim endpoint (= π/2 − α)
    #   notch_r   – half-width (= "radius") of the notch
    #   depth     – how deep the notch cuts in from the rim
    #
    # Y-flip reminder: ctx.arc (math CCW) renders CW on screen.
    #                  ctx.arc_negative (math CW) renders CCW on screen.
    # "inward" on screen = decreasing y on screen = increasing y in math coordinates.

    def _notch_circular(
            self, ctx: Context,
            cx: float, cy: float, disc_r: float,
            a_left: float, a_right: float, notch_r: float, depth: float,
    ) -> None:
        """Circular-arc notch.  pen: left endpoint → right endpoint.

        The two rim endpoints are fixed by notch_r (half-width).
        depth controls the sagitta – how far the arc dips inward from the chord.
        When depth == notch_r the arc is a perfect semicircle.
        """
        # Rim endpoints in math coordinates.
        lx = cx + disc_r * math.cos(a_left)
        ly = cy + disc_r * math.sin(a_left)
        rx = cx + disc_r * math.cos(a_right)
        ry = cy + disc_r * math.sin(a_right)

        # Chord half-length (should equal notch_r, but recompute for safety).
        chord_half = math.hypot(rx - lx, ry - ly) / 2.0

        d = max(depth, 1e-6)
        # Arc radius from sagitta formula: R = (w² + d²) / (2·d)
        arc_r = (chord_half * chord_half + d * d) / (2.0 * d)

        # Chord midpoint.
        mid_chord_x = (lx + rx) / 2.0
        mid_chord_y = (ly + ry) / 2.0

        # Unit vector along the chord (left → right).
        chord_dx = rx - lx
        chord_dy = ry - ly
        chord_len = math.hypot(chord_dx, chord_dy)
        ux = chord_dx / chord_len
        uy = chord_dy / chord_len

        # Inward normal (rotated 90° CCW in math coordinates = toward disc center).
        # "Inward" means decreasing y on screen = decreasing y in math coordinates
        # (since the notch is at the top: disc_r·sin(π/2) = +disc_r direction).
        # The inward direction from the chord toward the disc center is -y in math.
        nx = uy  # normal pointing "inward" (toward disc center in math)
        ny = -ux

        # Arc center: move from chord midpoint inward by (arc_r - depth).
        arc_cx = mid_chord_x + nx * (arc_r - d)
        arc_cy = mid_chord_y + ny * (arc_r - d)

        # Angles from arc center to each rim endpoint.
        angle_left = math.atan2(ly - arc_cy, lx - arc_cx)
        angle_right = math.atan2(ry - arc_cy, rx - arc_cx)

        # We want arc (math CCW) going from angle_left → through the deepest
        # inward point → angle_right.  If angle_right < angle_left we add 2π.
        if angle_right < angle_left:
            angle_right += 2.0 * math.pi
        mid_angle = (angle_left + angle_right) / 2.0
        ctx.arc(arc_cx, arc_cy, arc_r, angle_left, mid_angle)
        ctx.arc(arc_cx, arc_cy, arc_r, mid_angle, angle_right)

    def _notch_triangular(
            self, ctx: Context,
            cx: float, cy: float, disc_r: float,
            a_left: float, a_right: float, notch_r: float, depth: float,
    ) -> None:
        """Triangular (V-shaped) notch.  pen: left endpoint → right endpoint."""
        # Apex: on the disc center-line, inward by 'depth' from the rim.
        apex_x = cx
        apex_y = cy + disc_r - depth  # math coordinates: higher y = toward top before flip
        right_x = cx + disc_r * math.cos(a_right)
        right_y = cy + disc_r * math.sin(a_right)
        ctx.line_to(apex_x, apex_y)
        ctx.line_to(right_x, right_y)

    def _notch_oval(
            self, ctx: Context,
            cx: float, cy: float, disc_r: float,
            a_left: float, a_right: float, notch_r: float, depth: float,
    ) -> None:
        """Oval (elliptical) notch using cubic Bézier approximation.
        pen: left endpoint → right endpoint."""
        # Endpoints on the rim.
        lx = cx + disc_r * math.cos(a_left)
        ly = cy + disc_r * math.sin(a_left)
        rx = cx + disc_r * math.cos(a_right)
        ry = cy + disc_r * math.sin(a_right)
        # Deepest point: center-line, inward by 'depth'.
        mid_x = cx
        mid_y = cy + disc_r - depth
        # Bézier control points: tangent at endpoints is horizontal (parallel to
        # the chord lx→rx); tangent at midpoint is vertical.
        # kappa ≈ 0.5523 gives the best circle approximation; for a half-ellipse
        # we scale the horizontal handles by the half-width and vertical by depth.
        kappa: float = 0.5523
        h_ctrl = notch_r * kappa  # horizontal offset of the ctrl point
        v_ctrl = depth * kappa  # vertical offset of the ctrl point
        # From left endpoint to mid (going CW on screen = math CCW upward):
        ctx.curve_to(
            lx + h_ctrl, ly,  # cp1: nudge right from left endpoint
            mid_x - h_ctrl, mid_y,  # cp2: nudge left from midpoint
            mid_x, mid_y,
        )
        # From mid to right endpoint:
        ctx.curve_to(
            mid_x + h_ctrl, mid_y,  # cp1: nudge right from midpoint
            rx - h_ctrl, ry,  # cp2: nudge left from right endpoint
            rx, ry,
        )

    def _notch_trapezoid(
            self, ctx: Context,
            cx: float, cy: float, disc_r: float,
            a_left: float, a_right: float, notch_r: float, depth: float,
    ) -> None:
        """Trapezoid notch: wide at the rim, flat narrower bottom.
        pen: left endpoint → right endpoint."""
        # Inner (flat) half-width = 60 % of outer half-width.
        inner_hw = notch_r * 0.6
        # Four corners (math coordinates):
        #   left_outer  = left rim endpoint
        #   left_inner  = inward by depth, x offset = −inner_hw
        #   right_inner = inward by depth, x offset = +inner_hw
        #   right_outer = right rim endpoint
        inner_y = cy + disc_r - depth
        right_x = cx + disc_r * math.cos(a_right)
        right_y = cy + disc_r * math.sin(a_right)
        ctx.line_to(cx - inner_hw, inner_y)
        ctx.line_to(cx + inner_hw, inner_y)
        ctx.line_to(right_x, right_y)

    def top_disc(self, move: str = "") -> None:
        """Top disc: closed outline with reading notch (style set by --notch_style) + central magnet hole."""
        r = self.coin_radius - self.play
        md = self.magnet_diameter

        notch_r = min(self.notch_width / 2.0, r * 0.35)

        if self.move(r * 2, r * 2, move, before=True):
            return

        ctx = cast(Context, self.ctx)

        # --- Common geometry ---
        # disc center = (cx, cy); Y-flip applied by SVGSurface.
        # "top of disc" on screen  = (cx, cy − disc_r)
        #                          = (cx, cy + disc_r) in math coordinates.
        cx: float = r
        cy: float = r
        burn: float = self.burn
        disc_r: float = r + burn

        alpha: float = math.asin(notch_r / disc_r)
        a_right: float = math.pi / 2.0 - alpha
        a_left: float = math.pi / 2.0 + alpha

        # Notch depth: explicit value or auto (= half-width, giving a semicircle).
        depth: float = self.notch_depth if self.notch_depth > 0.0 else notch_r

        self.set_source_color(Color.OUTER_CUT)

        # Start path at the RIGHT rim endpoint.
        ctx.move_to(
            cx + disc_r * math.cos(a_right),
            cy + disc_r * math.sin(a_right),
        )

        # Big arc: arc_negative (math CW) from a_right → a_left the long way round
        # (≈ 360° − 2α).  After Y-flip this traces the disc outline on screen.
        n_segments: int = 10
        span: float = 2.0 * math.pi - 2.0 * alpha
        da: float = span / n_segments
        a: float = a_right
        for _ in range(n_segments):
            ctx.arc_negative(cx, cy, disc_r, a, a - da)
            a -= da
        # Pen is now at the LEFT rim endpoint (a_left).

        # Dispatch to the chosen notch style.
        # Each helper draws from the left endpoint back to the right endpoint.
        style = self.notch_style if self.notch_style in ("circular", "triangular", "oval", "trapezoid") else "oval"
        notch_fn = getattr(self, f"_notch_{style}")
        notch_fn(ctx, cx, cy, disc_r, a_left, a_right, notch_r, depth)

        ctx.stroke()

        # Central magnet hole
        self.hole(r, r, d=md)

        self.move(r * 2, r * 2, move)

    # ------------------------------------------------------------------
    # Main render
    # ------------------------------------------------------------------
    def render(self) -> None:
        self.bottom_coin(move="right")
        self.top_disc(move="right")
