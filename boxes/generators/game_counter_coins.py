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
    coin_radius: float = 30.0
    magnet_diameter: float = 4.0
    score_min: int = 0
    score_max: int = 9
    font_size: float = 4.0
    notch_width: float = 3.0
    play: float = 0.2

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.argparser.add_argument(
            "--coin_radius", action="store", type=float, default=30.0,
            help="Outer radius of both discs [mm]")
        self.argparser.add_argument(
            "--magnet_diameter", action="store", type=float, default=4.0,
            help="Diameter of the central cylindrical magnet [mm]")
        self.argparser.add_argument(
            "--score_min", action="store", type=int, default=0,
            help="Minimum score value displayed on Piece A")
        self.argparser.add_argument(
            "--score_max", action="store", type=int, default=9,
            help="Maximum score value displayed on Piece A")
        self.argparser.add_argument(
            "--font_size", action="store", type=float, default=4.0,
            help="Font size for score numbers engraved on Piece A [mm]")
        self.argparser.add_argument(
            "--notch_width", action="store", type=float, default=3.0,
            help="Width of the reading notch on Piece B [mm]")
        self.argparser.add_argument(
            "--play", action="store", type=float, default=0.2,
            help="Radial play between the two discs [mm]")

    # ------------------------------------------------------------------
    # Piece A – bottom coin with score scale
    # ------------------------------------------------------------------
    def bottomCoin(self, move: str = "") -> None:
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
        label_r = r - self.font_size * 1.2

        self.set_source_color(Color.ETCHING)
        for i, score in enumerate(range(self.score_min, self.score_max + 1)):
            angle_deg = i * angle_step
            angle_rad = math.radians(angle_deg)
            tx = r + label_r * math.sin(angle_rad)
            ty = r + label_r * math.cos(angle_rad)
            with self.saved_context():
                self.text(str(score), x=tx, y=ty, angle=-angle_deg,
                          align="middle center",
                          fontsize=self.font_size, color=Color.ETCHING)

        self.move(r * 2, r * 2, move)

    # ------------------------------------------------------------------
    # Piece B – top disc with reading notch
    # ------------------------------------------------------------------
    def topDisc(self, move: str = "") -> None:
        """Top disc: single closed outline with smooth semicircular notch at the top + central magnet hole."""
        r = self.coin_radius - self.play
        md = self.magnet_diameter
        # Notch is a semicircle of radius nw/2 centred on the rim at 12 o'clock.
        notch_r = min(self.notch_width / 2.0, r * 0.35)

        if self.move(r * 2, r * 2, move, before=True):
            return

        ctx = cast(Context, self.ctx)

        # --- Single closed OUTER_CUT path: disc with smooth semicircular notch ---
        # All coordinates are in local space; disc centre = (cx, cy) = (r, r).
        #
        # IMPORTANT – Y-axis inversion:
        # SVGSurface applies invert_y=True, which mirrors every arc vertically.
        # As a result ctx.arc (mathematically CCW) renders CW on screen, and
        # ctx.arc_negative (math CW) renders CCW on screen.
        #
        # In screen space (Y down) "top of disc" = cy - disc_r, angle = +π/2 in
        # screen convention.  We work in math angles throughout:
        #   top  = angle +π/2  (cos=0, sin=+1 → point (cx, cy+disc_r) before Y-flip,
        #                        which maps to (cx, cy-disc_r) after Y-flip ✓)
        #
        # Notch endpoints (math angles, Y-flip applied by surface):
        #   a_right = +π/2 - α   (left  side in screen space after flip)
        #   a_left  = +π/2 + α   (right side in screen space after flip)
        # where α = asin(notch_r / disc_r).
        #
        # Big arc:  arc_negative (math CW = screen CCW) from a_right → a_left
        #           going the long way (≈360°-2α) around the disc.
        # Notch arc: arc (math CCW = screen CW) semicircle going inward.
        #           Centre at (cx, cy + disc_r·cos α) [before flip → screen top].
        #           From angle 0 (right notch point) → π (left notch point)
        #           via the top of the semicircle (= inward toward disc centre).

        cx: float = r
        cy: float = r
        burn: float = self.burn
        disc_r: float = r + burn  # outer cut perimeter includes burn compensation

        alpha: float = math.asin(notch_r / disc_r)
        a_right: float = math.pi / 2.0 - alpha   # right endpoint angle (math)
        a_left: float  = math.pi / 2.0 + alpha   # left  endpoint angle (math)

        # Notch semicircle centre: on the disc rim at the very top.
        # In math coords (before Y-flip) this is (cx, cy + disc_r·cos α).
        notch_cx: float = cx
        notch_cy: float = cy + disc_r * math.cos(alpha)

        self.set_source_color(Color.OUTER_CUT)

        # Move pen to the right notch endpoint on the disc rim.
        ctx.move_to(
            cx + disc_r * math.cos(a_right),
            cy + disc_r * math.sin(a_right),
        )

        # Big arc: arc_negative (math CW) from a_right → a_left the long way round.
        # Math CW with decreasing angle: a_right → 0 → -π/2 → -π → … → a_left
        # (≈ 360° - 2α).  After Y-flip this traces the disc CCW on screen.
        n_segments: int = 10
        span: float = 2.0 * math.pi - 2.0 * alpha   # angular span of the big arc
        da: float = span / n_segments
        a: float = a_right
        for _ in range(n_segments):
            ctx.arc_negative(cx, cy, disc_r, a, a - da)
            a -= da

        # Notch arc: arc (math CCW) from angle 0 → π.
        # Math CCW goes 0 → π/2 (topmost = deepest inward point) → π.
        # After Y-flip this curves inward (toward disc centre) on screen. ✓
        # Split into two 90° segments to avoid zero-division at exactly 180°.
        ctx.arc(notch_cx, notch_cy, notch_r, 0.0, math.pi / 2.0)
        ctx.arc(notch_cx, notch_cy, notch_r, math.pi / 2.0, math.pi)

        ctx.stroke()

        # Central magnet hole
        self.hole(r, r, d=md)

        self.move(r * 2, r * 2, move)

    # ------------------------------------------------------------------
    # Main render
    # ------------------------------------------------------------------
    def render(self) -> None:
        self.bottomCoin(move="right")
        self.topDisc(move="right")
