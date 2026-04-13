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

import math
from dataclasses import dataclass
from typing import cast

from boxes import *
from boxes.args import FloatStepper
from boxes.drawing import Context
from boxes.settings.crenel_settings import CrenelSettings
from boxes.settings.font_settings import FontSettings
from boxes.settings.score_settings import ScoreSettings


@dataclass
class _WheelParams:
    """All per-wheel parameters, resolved from self attributes."""

    outer_diameter: float
    score_min: int
    score_max: int
    score_radius: float
    score_angle: float
    crenel_enabled: bool
    crenel_depth: float
    crenel_width: float
    crenel_shape: str
    crenel_rounded: bool
    crenel_radius: float


class GameCounterDual(Boxes):
    """Dual-wheel board game score counter – one board, two independent spinning rings"""

    ui_group = "GameAccessory"

    description = """
A board game score counter with **two independent spinning score wheels** on a
single base board.

Each wheel works exactly like the ring counter (``GameCounterRing``):
a spinning outer ring shows the score; a fixed inner disc carries the pointer.
Both wheels share a common font but have fully independent score ranges,
diameters, and optional gear-tooth (crenel) rims.

**Cut pieces**

* **Board** – rectangular base with two magnet pockets (one per wheel).
* **Ring 1 / Ring 2** – the spinning outer ring of each wheel.

**Assembly**

1. Press a magnet into each pocket on the board.
2. Drop each ring over its magnet pocket; the magnet holds it in place while
   still allowing it to spin freely.
3. Spin the rings to track scores independently.
"""

    # ------------------------------------------------------------------ #
    # mypy stubs – all overwritten by argparse at runtime                  #
    # ------------------------------------------------------------------ #
    wheel1_outer_diameter: float = 90.0
    wheel2_outer_diameter: float = 70.0
    board_margin: float = 8.0
    magnet_diameter: float = 5.0
    # font (shared)
    font_size: float = 10.0
    font_font: str = "sans-serif"
    font_bold: bool = False
    font_italic: bool = False
    # score – wheel 1
    score1_min: int = 0
    score1_max: int = 3
    score1_radius: float = 0.0
    score1_angle: float = 0.0
    # score – wheel 2
    score2_min: int = 0
    score2_max: int = 9
    score2_radius: float = 0.0
    score2_angle: float = 0.0
    # crenel – wheel 1
    crenel1_enabled: bool = False
    crenel1_depth: float = 4.0
    crenel1_width: float = 0.5
    crenel1_shape: str = "radial"
    crenel1_rounded: bool = True
    crenel1_radius: float = 2.0
    # crenel – wheel 2
    crenel2_enabled: bool = False
    crenel2_depth: float = 4.0
    crenel2_width: float = 0.5
    crenel2_shape: str = "radial"
    crenel2_rounded: bool = True
    crenel2_radius: float = 2.0

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(ScoreSettings, prefix="score1", title="Score Wheel 1 Settings",
                             min=self.score1_min, max=self.score1_max,
                             radius=self.score1_radius, angle=self.score1_angle)
        self.addSettingsArgs(ScoreSettings, prefix="score2", title="Score Wheel 2 Settings",
                             min=self.score2_min, max=self.score2_max,
                             radius=self.score2_radius, angle=self.score2_angle)
        self.addSettingsArgs(FontSettings, prefix="font", size=self.font_size, font=self.font_font,
                             bold=self.font_bold, italic=self.font_italic)
        self.addSettingsArgs(CrenelSettings, prefix="crenel1", title="Crenel Wheel 1 Settings",
                             enabled=self.crenel1_enabled, depth=self.crenel1_depth,
                             width=self.crenel1_width, shape=self.crenel1_shape,
                             rounded=self.crenel1_rounded, radius=self.crenel1_radius)
        self.addSettingsArgs(CrenelSettings, prefix="crenel2", title="Crenel Wheel 2 Settings",
                             enabled=self.crenel2_enabled, depth=self.crenel2_depth,
                             width=self.crenel2_width, shape=self.crenel2_shape,
                             rounded=self.crenel2_rounded, radius=self.crenel2_radius)

        self.argparser.add_argument("--wheel1_outer_diameter", action="store", type=FloatStepper(1.0),
                                    default=self.wheel1_outer_diameter,
                                    help="Outer diameter of wheel 1 ring [mm]")
        self.argparser.add_argument("--wheel2_outer_diameter", action="store", type=FloatStepper(1.0),
                                    default=self.wheel2_outer_diameter,
                                    help="Outer diameter of wheel 2 ring [mm]")
        self.argparser.add_argument("--board_margin", action="store", type=FloatStepper(1.0),
                                    default=self.board_margin,
                                    help="Margin between each wheel centre and the board edge [mm]")
        self.argparser.add_argument("--magnet_diameter", action="store", type=FloatStepper(0.1),
                                    default=self.magnet_diameter,
                                    help="Diameter of the central magnet hole on each wheel (0 = no hole) [mm]")

    # ------------------------------------------------------------------ #
    # Parameter helpers                                                    #
    # ------------------------------------------------------------------ #

    def _wheel_params(self, n: int) -> _WheelParams:
        """Build _WheelParams from self attributes for wheel n (1 or 2)."""
        s = str(n)
        return _WheelParams(
            outer_diameter=getattr(self, f"wheel{s}_outer_diameter"),
            score_min=getattr(self, f"score{s}_min"),
            score_max=getattr(self, f"score{s}_max"),
            score_radius=getattr(self, f"score{s}_radius"),
            score_angle=getattr(self, f"score{s}_angle"),
            crenel_enabled=getattr(self, f"crenel{s}_enabled"),
            crenel_depth=getattr(self, f"crenel{s}_depth"),
            crenel_width=getattr(self, f"crenel{s}_width"),
            crenel_shape=getattr(self, f"crenel{s}_shape"),
            crenel_rounded=getattr(self, f"crenel{s}_rounded"),
            crenel_radius=getattr(self, f"crenel{s}_radius"),
        )

    # ------------------------------------------------------------------ #
    # Score number engraving                                               #
    # ------------------------------------------------------------------ #

    def _draw_score_numbers(self, cx: float, cy: float, label_r: float,
                            ctx: Context, wp: _WheelParams) -> None:
        """Engrave score numbers evenly around a circle of radius *label_r*."""
        n = wp.score_max - wp.score_min + 1
        if n < 1:
            return
        angle_step = 360.0 / n

        ctx.set_font(self.font_font, bold=self.font_bold, italic=self.font_italic)
        self.set_source_color(Color.ETCHING)
        for i, score in enumerate(range(wp.score_min, wp.score_max + 1)):
            angle_deg = i * angle_step + 90.0
            angle_rad = math.radians(angle_deg)
            tx = cx + label_r * math.sin(angle_rad)
            ty = cy + label_r * math.cos(angle_rad)
            with self.saved_context():
                self.text(str(score), x=tx, y=ty,
                          angle=-angle_deg + wp.score_angle,
                          align="middle center",
                          fontsize=self.font_size, color=Color.ETCHING)
        ctx.stroke()

    # ------------------------------------------------------------------ #
    # Outer crenels                                                        #
    # ------------------------------------------------------------------ #

    def _draw_outer_crenels(self, cx: float, cy: float, ro: float,
                            ctx: Context, wp: _WheelParams) -> None:
        """Draw gear-tooth outer perimeter for a ring wheel."""
        n = wp.score_max - wp.score_min + 1
        if n < 1:
            return

        depth = wp.crenel_depth
        radial = (wp.crenel_shape == "radial")
        r_corn = wp.crenel_radius if wp.crenel_rounded else 0.0
        ri = ro - depth

        angle_step = 2.0 * math.pi / n
        half = angle_step / 2.0
        # tooth_half: half-angle of the tooth = sector × (1 − gap_fraction) / 2
        tooth_half = angle_step * (1.0 - max(0.05, min(0.95, wp.crenel_width))) / 2.0

        self.set_source_color(Color.OUTER_CUT)
        start_angle = math.pi / 2.0

        def pt_on(r: float, a: float) -> tuple[float, float]:
            return cx + r * math.cos(a), cy + r * math.sin(a)

        def sym_inner_corners(
                center_a_in: float,
        ) -> tuple[tuple[float, float], tuple[float, float]]:
            bx_in = math.cos(center_a_in)
            by_in = math.sin(center_a_in)
            ox_l, oy_l = pt_on(ro, center_a_in - tooth_half)
            ox_r, oy_r = pt_on(ro, center_a_in + tooth_half)
            return (ox_l - depth * bx_in, oy_l - depth * by_in), \
                (ox_r - depth * bx_in, oy_r - depth * by_in)

        ctx.move_to(*pt_on(ro, start_angle - half))
        last_tooth_r: float = start_angle - half

        for i in range(n):
            center_a = start_angle + i * angle_step
            tooth_l = center_a - tooth_half
            tooth_r = center_a + tooth_half

            if radial:
                if r_corn <= 0.0 or ri <= 0.0:
                    ctx.arc(cx, cy, ro, center_a - half, tooth_l)
                    ctx.line_to(*pt_on(ri, tooth_l))
                    ctx.arc(cx, cy, ri, tooth_l, tooth_r)
                    ctx.line_to(*pt_on(ro, tooth_r))
                    last_tooth_r = tooth_r
                else:
                    da_o = min(r_corn / ro, tooth_half * 0.45)
                    da_i = min(r_corn / ri, tooth_half * 0.45)
                    ctx.arc(cx, cy, ro, center_a - half, tooth_l - da_o)
                    ctx.curve_to(*pt_on(ri, tooth_l - da_i),
                                 *pt_on(ri, tooth_l - da_i),
                                 *pt_on(ri, tooth_l + da_i))
                    ctx.arc(cx, cy, ri, tooth_l + da_i, tooth_r - da_i)
                    ctx.curve_to(*pt_on(ro, tooth_r + da_o),
                                 *pt_on(ro, tooth_r + da_o),
                                 *pt_on(ro, tooth_r + da_o))
                    last_tooth_r = tooth_r + da_o
            else:
                il, ir = sym_inner_corners(center_a)
                bx = math.cos(center_a)
                by = math.sin(center_a)
                if r_corn <= 0.0:
                    ctx.arc(cx, cy, ro, center_a - half, tooth_l)
                    ctx.line_to(*il)
                    ctx.line_to(*ir)
                    ctx.line_to(*pt_on(ro, tooth_r))
                    last_tooth_r = tooth_r
                else:
                    da_o = min(r_corn / ro, tooth_half * 0.4)
                    rc = min(r_corn, ro * tooth_half * 0.4)
                    ctx.arc(cx, cy, ro, center_a - half, tooth_l - da_o)
                    fl_ctrl = (cx + ro * math.cos(tooth_l) - rc * bx,
                               cy + ro * math.sin(tooth_l) - rc * by)
                    ctx.curve_to(*fl_ctrl, *fl_ctrl, *il)
                    ctx.line_to(*ir)
                    fr_ctrl = (cx + ro * math.cos(tooth_r) - rc * bx,
                               cy + ro * math.sin(tooth_r) - rc * by)
                    ctx.curve_to(*fr_ctrl, *fr_ctrl, *pt_on(ro, tooth_r + da_o))
                    last_tooth_r = tooth_r + da_o

        ctx.arc(cx, cy, ro, last_tooth_r, start_angle - half + 2.0 * math.pi)
        ctx.stroke()

    # ------------------------------------------------------------------ #
    # Piece drawing                                                        #
    # ------------------------------------------------------------------ #

    def _draw_ring(self, cx: float, cy: float,
                   ctx: Context, wp: _WheelParams) -> None:
        """Spinning disc for one wheel."""
        ro = wp.outer_diameter / 2

        if wp.crenel_enabled:
            self._draw_outer_crenels(cx, cy, ro, ctx, wp)
        else:
            self.set_source_color(Color.OUTER_CUT)
            self.circle(cx, cy, ro)

        if self.magnet_diameter > 0.0:
            self.hole(cx, cy, d=self.magnet_diameter)

        label_r = wp.score_radius if wp.score_radius > 0.0 else ro - self.font_size / 2.0 - 1.0
        self._draw_score_numbers(cx, cy, label_r, ctx, wp)

    def _draw_board(self, move: str = "") -> None:
        """Base board: rectangle sized to hold both wheels, with magnet pockets."""
        ro1 = self.wheel1_outer_diameter / 2
        ro2 = self.wheel2_outer_diameter / 2
        m = self.board_margin

        board_w = 2 * ro1 + self.spacing + 2 * ro2 + 2 * m
        board_h = 2 * max(ro1, ro2) + 2 * m

        if self.move(board_w, board_h, move, before=True):
            return

        ctx = cast(Context, self.ctx)

        self.set_source_color(Color.OUTER_CUT)
        ctx.rectangle(0, 0, board_w, board_h)

        if self.magnet_diameter > 0.0:
            cy = board_h / 2
            self.hole(m + ro1, cy, d=self.magnet_diameter)
            self.hole(m + 2 * ro1 + self.spacing + ro2, cy, d=self.magnet_diameter)

        self.move(board_w, board_h, move)

    def _draw_wheels_row(self, wp1: _WheelParams, wp2: _WheelParams,
                         ctx: Context, move: str = "") -> None:
        """Both wheels side-by-side in one bounding box, vertically centred."""
        ro1 = wp1.outer_diameter / 2
        ro2 = wp2.outer_diameter / 2
        max_r = max(ro1, ro2)

        row_w = ro1 * 2 + self.spacing + ro2 * 2
        row_h = max_r * 2

        if self.move(row_w, row_h, move, before=True):
            return

        # Both centres sit at the vertical midpoint of the shared bounding box.
        cy = max_r
        self._draw_ring(ro1,                              cy, ctx, wp1)
        self._draw_ring(ro1 * 2 + self.spacing + ro2,    cy, ctx, wp2)

        self.move(row_w, row_h, move)

    # ------------------------------------------------------------------ #
    # Main render                                                          #
    # ------------------------------------------------------------------ #

    def render(self) -> None:
        ctx = cast(Context, self.ctx)
        wp1 = self._wheel_params(1)
        wp2 = self._wheel_params(2)

        # Board at bottom, both wheels above it – centre-aligned horizontally.
        self._draw_board(move="up")
        self._draw_wheels_row(wp1, wp2, ctx, move="up")
