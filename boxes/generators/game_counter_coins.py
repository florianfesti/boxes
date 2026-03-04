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
        """Top disc: outer circle cut + rectangular notch + central magnet hole."""
        r = self.coin_radius - self.play
        md = self.magnet_diameter
        nw = self.notch_width
        notch_depth = min(nw, r * 0.4)

        if self.move(r * 2, r * 2, move, before=True):
            return

        ctx = cast(Context, self.ctx)

        # Outer perimeter circle
        self.set_source_color(Color.OUTER_CUT)
        self.circle(r, r, r)
        ctx.stroke()

        # Notch
        self.set_source_color(Color.INNER_CUT)
        self.rectangularHole(r, r + r - notch_depth / 2.0,
                              nw, notch_depth)

        # Central magnet hole – blue (filled pocket)
        self.hole(r, r, d=md)

        self.move(r * 2, r * 2, move)

    # ------------------------------------------------------------------
    # Main render
    # ------------------------------------------------------------------
    def render(self) -> None:
        self.bottomCoin(move="right")
        self.topDisc(move="right")
