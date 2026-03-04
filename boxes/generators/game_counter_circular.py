# Copyright (C) 2024 boxes-acatoire contributors
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

from boxes import *

# ---------------------------------------------------------------------------
# DESIGN NOTES – game_counter_circular
# ---------------------------------------------------------------------------
#
# CONCEPT
# -------
# A physical, laser-cut point counter for board games.
# Two flat circular discs are stacked concentrically and held together by
# small neodymium magnets so they can rotate freely against each other.
#
#   Piece A  – OUTER RING (the "frame")
#     • A full disc with a circular cutout in the centre, forming a ring.
#     • The outer edge shows the current score: numbers / marks are
#       engraved (blue / ETCHING color) around the ring at regular angular
#       intervals on the VISIBLE FACE.
#     • Notches or arrow marker cut into the ring edge to indicate the
#       currently selected value (or a pointer is printed on Piece B).
#     • Magnet holes (circular pockets, INNER_CUT / blue) placed
#       symmetrically near the inner edge of the ring to attract Piece B.
#
#   Piece B  – INNER DISC (the "dial")
#     • A solid disc whose radius is slightly smaller than the cutout in
#       Piece A, giving a small rotation gap (kerf + play).
#     • An indicator arrow or triangle is etched (ETCHING) at one point on
#       the circumference so the player can read the score off Piece A.
#     • Matching magnet holes on the top face so the two pieces snap
#       together face-to-face and spin smoothly.
#     • Optional: a central finger-grip hole or thumb notch so the user
#       can spin Piece B without disturbing Piece A.
#
# ASSEMBLY
# ---------
#   1. Drop magnets (e.g. 4 × Ø6 × 2 mm cylinder) into the holes of Piece B.
#   2. Place Piece A on top, aligning the magnet holes.
#   3. The magnetic attraction keeps the stack together while still
#      allowing free rotation.
#   4. Rotate Piece B (inner disc) to count up / down; Piece A (ring)
#      stays fixed or is held by the other hand.
#
# LASER COLOR CONVENTION (boxes standard)
# ----------------------------------------
#   Color.OUTER_CUT  (black)  → outer perimeter cuts (profile of each piece)
#   Color.INNER_CUT  (blue)   → interior cuts: magnet holes, centre hole
#   Color.ETCHING    (green)  → score numbers, tick marks, arrow indicator
#   Color.ANNOTATIONS (red)   → alignment markers / debug guides only
#
# PARAMETERS (planned argparser arguments)
# -----------------------------------------
#   --outer_radius      float   Total outer radius of the counter [mm]  (default 60)
#   --inner_radius      float   Radius of the inner disc / cutout [mm]  (default 40)
#   --magnet_diameter   float   Diameter of cylindrical magnets [mm]    (default 6)
#   --magnet_height     float   Height / depth of magnet pocket [mm]    (default 2)
#   --magnet_count      int     Number of magnets (evenly spaced)        (default 4)
#   --score_min         int     Minimum score value displayed            (default 0)
#   --score_max         int     Maximum score value displayed            (default 20)
#   --play              float   Radial gap between ring and disc [mm]    (default 0.3)
#   --font_size         float   Font size for score numbers [mm]         (default 5)
#   --pointer_size      float   Height of the pointer triangle [mm]      (default 4)
#
# PIECES OUTPUT (first iteration – 2 pieces side by side)
# --------------------------------------------------------
#   render() will draw two pieces with move="right":
#     1. outerRing()  → Piece A
#     2. innerDisc()  → Piece B
#
# BOXES LIB TOOLS THAT WILL BE USED
# -----------------------------------
#   self.parts.disc(diameter, hole, move)
#       → base shape for Piece B (inner disc)
#       → used with hole=0 then manual inner cutout for Piece A
#
#   self.hole(x, y, r/d)           → magnet pocket holes (INNER_CUT)
#   self.circle(x, y, r)           → outer perimeter circle cuts
#   self.text(text, x, y, angle, align, fontsize, color, font)
#       → score numbers engraved along the ring
#
#   self.set_source_color(Color.X)  → switch laser color
#   self.saved_context()            → isolate transforms for each number/mark
#   self.moveTo(x, y, angle)        → polar positioning for numbers
#
#   math.cos / math.sin / math.radians  → polar → Cartesian for placements
#
# METHODS PLANNED
# ----------------
#   outerRing(move=None, label="")
#       - Draws the ring profile (outer circle cut + inner circle cut)
#       - Engraves score numbers around the ring
#       - Adds magnet holes near the inner edge
#
#   innerDisc(move=None, label="")
#       - Draws the solid disc (outer circle cut)
#       - Etches pointer/arrow at 0° position
#       - Adds matching magnet holes
#       - Optionally adds a thumb grip hole at the centre
#
#   render()
#       - Calls outerRing("right") then innerDisc("right")
#
# ---------------------------------------------------------------------------


class GameCounterCircular(Boxes):
    """Circular game point counter – two magnetic rotating discs"""

    ui_group = "Misc"

    description = """
A two-piece circular point counter for board games.

The **outer ring** (Piece A) displays the score scale around its inner face.
The **inner disc** (Piece B) carries a pointer and is rotated to select the
current score. The two pieces are held together by small neodymium magnets
inserted into matching pockets so they can spin freely without falling apart.

Assembly: insert magnets → stack pieces face-to-face → enjoy!

Color convention:
* **Red / OUTER_CUT** → perimeter cuts (the outline of each piece)
* **Blue / INNER_CUT** → magnet pockets, centre hole
* **Green / ETCHING**  → score numbers, tick marks, pointer arrow
"""

    def __init__(self) -> None:
        Boxes.__init__(self)

        # TODO: implement argparser arguments as described in DESIGN NOTES above
        pass

    # ------------------------------------------------------------------
    # Piece A – outer ring
    # ------------------------------------------------------------------
    def outerRing(self, move=None, label=""):
        """TODO: implement outer ring piece"""
        pass

    # ------------------------------------------------------------------
    # Piece B – inner disc
    # ------------------------------------------------------------------
    def innerDisc(self, move=None, label=""):
        """TODO: implement inner disc piece"""
        pass

    # ------------------------------------------------------------------
    # Main render
    # ------------------------------------------------------------------
    def render(self):
        """TODO: call outerRing and innerDisc side by side"""
        pass
