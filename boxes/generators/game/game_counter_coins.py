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
from boxes.args import FloatStepper, IntStepper
from boxes.drawing import Context
from boxes.settings.font_settings import FontSettings
from boxes.settings.score_settings import ScoreSettings


class GameCounterCoins(Boxes):
    """Coin-stack game point counter – top disc notch reads score off bottom coin"""

    ui_group = "Game"
    tags = ["new"]

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
    coin_diameter: float = 50.0
    magnet_diameter: float = 4.0
    # Score Settings stubs
    Score_min: int = 0
    Score_max: int = 9
    Score_radius: float | None = None
    Score_angle: float = 0.0
    Score_values: str = ""
    # Font Settings stubs
    font_size: float = 8.0
    font_font: str = "sans-serif"
    font_bold: bool = False
    font_italic: bool = False
    notch_width: float = 15.0
    notch_depth: float | None = None
    notch_style: str = "oval"
    notch_count: int = 1
    play: float = 0.2

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(ScoreSettings,
                             min=self.Score_min,
                             max=self.Score_max)
        self.addSettingsArgs(FontSettings,
                             prefix="font",
                             size=self.font_size)

        self.argparser.add_argument(
            "--coin_diameter", action="store", type=FloatStepper(0.1), default=self.coin_diameter,
            help="Outer diameter of both discs [mm]")
        self.argparser.add_argument(
            "--magnet_diameter", action="store", type=FloatStepper(0.1), default=self.magnet_diameter,
            help="Diameter of the central cylindrical magnet [mm]")
        self.argparser.add_argument(
            "--notch_width", action="store", type=FloatStepper(0.1), default=self.notch_width,
            help="Width of the reading notch on Piece B [mm]")
        _auto_notch_d = round(self.notch_width / 2)
        self.argparser.add_argument(
            "--notch_depth", action="store",
            type=FloatStepper(1.0, auto_default=float(_auto_notch_d), auto=True),
            default=self.notch_depth,
            help=f"Depth of the reading notch on Piece B [mm]. "
                 f"auto = notch_width / 2 (≈{_auto_notch_d} mm)")
        self.argparser.add_argument(
            "--notch_style", action="store", type=str, default=self.notch_style,
            choices=["circular", "triangular", "oval", "trapezoid"],
            help="Shape of the reading notch on Piece B")
        self.argparser.add_argument(
            "--notch_count", action="store", type=IntStepper(1), default=self.notch_count,
            help="Number of reading notches equally spaced around Piece B (≥ 1)")
        self.argparser.add_argument(
            "--play", action="store", type=float, default=self.play,
            help="Radial play between the two discs [mm]")

    # ------------------------------------------------------------------
    # Score label helper
    # ------------------------------------------------------------------
    def _score_labels(self) -> list[tuple[str, float]]:
        """Return ``(text, extra_angle_deg)`` for each score position.

        Tokens prefixed with ``!`` are rotated an extra 180° so they face
        the opposite direction — useful when mixing orientations, e.g.
        ``0,1,2,!3,!4`` makes the last two labels face inward.
        """
        raw = (self.Score_values or "").strip()
        tokens: list[str] = (
            [v.strip() for v in raw.split(",") if v.strip()]
            if raw
            else [str(i) for i in range(self.Score_min, self.Score_max + 1)]
        )
        result: list[tuple[str, float]] = []
        for token in tokens:
            if token.startswith("!"):
                result.append((token[1:], 180.0))
            else:
                result.append((token, 0.0))
        return result

    # ------------------------------------------------------------------
    # Piece A – bottom coin with score scale
    # ------------------------------------------------------------------
    def bottom_coin(self, move: str = "") -> None:
        """Bottom disc: outer cut + central magnet hole + engraved score numbers."""
        r = self.coin_diameter / 2
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

        # Score labels
        labels = self._score_labels()
        n = len(labels)
        if n == 0:
            self.move(r * 2, r * 2, move)
            return

        angle_step = 360.0 / n
        orientation = self.Score_angle
        # When facing inward (≈180°) labels sit a bit closer to centre.
        inward = abs((orientation % 360) - 180) < 10
        offset_label_radius = self.font_size * (0.4 if inward else 0.6)
        label_r = (
            self.Score_radius if self.Score_radius is not None
            else r - offset_label_radius
        )

        ctx.set_font(self.font_font, bold=self.font_bold, italic=self.font_italic)
        self.set_source_color(Color.ETCHING)
        for i, (label, extra_angle) in enumerate(labels):
            angle_deg = i * angle_step
            angle_rad = math.radians(angle_deg)
            tx = r + label_r * math.sin(angle_rad)
            ty = r + label_r * math.cos(angle_rad)
            with self.saved_context():
                self.text(label, x=tx, y=ty,
                          angle=-angle_deg + orientation + extra_angle,
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
            center_angle: float = math.pi / 2,
    ) -> None:
        """Triangular (V-shaped) notch.  pen: left endpoint → right endpoint."""
        apex_x = cx + (disc_r - depth) * math.cos(center_angle)
        apex_y = cy + (disc_r - depth) * math.sin(center_angle)
        right_x = cx + disc_r * math.cos(a_right)
        right_y = cy + disc_r * math.sin(a_right)
        ctx.line_to(apex_x, apex_y)
        ctx.line_to(right_x, right_y)

    def _notch_oval(
            self, ctx: Context,
            cx: float, cy: float, disc_r: float,
            a_left: float, a_right: float, notch_r: float, depth: float,
            center_angle: float = math.pi / 2,
    ) -> None:
        """Oval (elliptical) notch using cubic Bézier approximation.
        pen: left endpoint → right endpoint."""
        lx = cx + disc_r * math.cos(a_left)
        ly = cy + disc_r * math.sin(a_left)
        rx = cx + disc_r * math.cos(a_right)
        ry = cy + disc_r * math.sin(a_right)
        # Deepest point at center_angle, inward by depth.
        mid_x = cx + (disc_r - depth) * math.cos(center_angle)
        mid_y = cy + (disc_r - depth) * math.sin(center_angle)
        # Tangent direction (CW) at center_angle: (sin φ, −cos φ)
        kappa: float = 0.5523
        h_ctrl = notch_r * kappa
        tx = math.sin(center_angle)
        ty = -math.cos(center_angle)
        ctx.curve_to(
            lx + h_ctrl * tx, ly + h_ctrl * ty,
            mid_x - h_ctrl * tx, mid_y - h_ctrl * ty,
            mid_x, mid_y,
        )
        ctx.curve_to(
            mid_x + h_ctrl * tx, mid_y + h_ctrl * ty,
            rx - h_ctrl * tx, ry - h_ctrl * ty,
            rx, ry,
        )

    def _notch_trapezoid(
            self, ctx: Context,
            cx: float, cy: float, disc_r: float,
            a_left: float, a_right: float, notch_r: float, depth: float,
            center_angle: float = math.pi / 2,
    ) -> None:
        """Trapezoid notch: wide at the rim, flat narrower bottom.
        pen: left endpoint → right endpoint."""
        inner_hw = notch_r * 0.6
        # Inner centre: inward by depth along the radial direction at center_angle.
        icx = cx + (disc_r - depth) * math.cos(center_angle)
        icy = cy + (disc_r - depth) * math.sin(center_angle)
        # Tangent (CW) at center_angle: (sin φ, −cos φ)
        tx = math.sin(center_angle)
        ty = -math.cos(center_angle)
        right_x = cx + disc_r * math.cos(a_right)
        right_y = cy + disc_r * math.sin(a_right)
        ctx.line_to(icx - inner_hw * tx, icy - inner_hw * ty)   # left inner
        ctx.line_to(icx + inner_hw * tx, icy + inner_hw * ty)   # right inner
        ctx.line_to(right_x, right_y)

    def top_disc(self, move: str = "") -> None:
        """Top disc: closed outline with reading notch(es) + central magnet hole."""
        r = self.coin_diameter / 2 - self.play
        md = self.magnet_diameter
        notch_count = max(1, self.notch_count)
        notch_r = min(self.notch_width / 2.0, r * 0.35)

        if self.move(r * 2, r * 2, move, before=True):
            return

        ctx = cast(Context, self.ctx)

        cx: float = r
        cy: float = r
        burn: float = self.burn
        disc_r: float = r + burn

        # Clamp alpha so arc_span stays positive even with many notches.
        alpha = math.asin(min(notch_r / disc_r, 0.99 / notch_count))
        depth: float = self.notch_depth if self.notch_depth is not None else notch_r

        style = self.notch_style if self.notch_style in ("circular", "triangular", "oval", "trapezoid") else "oval"
        notch_fn = getattr(self, f"_notch_{style}")

        # Arc span between consecutive notches (going CW).
        arc_span = 2.0 * math.pi / notch_count - 2.0 * alpha
        n_seg = max(1, round(10 * arc_span / (2.0 * math.pi)))
        da = arc_span / n_seg

        # Notch centre angles going CW from top (π/2).
        centers = [math.pi / 2.0 - i * (2.0 * math.pi / notch_count)
                   for i in range(notch_count)]

        self.set_source_color(Color.OUTER_CUT)

        # Start at right rim endpoint of notch 0.
        ctx.move_to(cx + disc_r * math.cos(centers[0] - alpha),
                    cy + disc_r * math.sin(centers[0] - alpha))

        for i in range(notch_count):
            # Arc CW from right of notch i to left of notch (i+1) % n.
            a = centers[i] - alpha
            for _ in range(n_seg):
                ctx.arc_negative(cx, cy, disc_r, a, a - da)
                a -= da
            # Draw notch (i+1) % n.
            ni = (i + 1) % notch_count
            a_left  = centers[ni] + alpha
            a_right = centers[ni] - alpha
            notch_fn(ctx, cx, cy, disc_r, a_left, a_right, notch_r, depth,
                     center_angle=centers[ni])

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
