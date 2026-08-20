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

import pathlib
from types import SimpleNamespace

from boxes import Boxes, Color, FloatStepper, boolarg
from boxes.settings.resource_settings import ResourceSettings, resource_path

from .svgimport import draw_piece, load_svg_piece

THEME_DIR = pathlib.Path(__file__).parent / "fantasy"
CHARACTER_DIR = THEME_DIR / "character"
PET_DIR = THEME_DIR / "pet"
BASE_DIR = THEME_DIR / "base"

# Fraction-of-piece-size layout for the peg holes overlaid on the Base
# artwork -- thickness-wide slots a character/pet peg is glued into.
_MINIATURE_HOLE_LENGTH = 15.0
_PET_HOLE_LENGTH = 12.0
_LEFT_HOLE_CX_FRACTION = 1 / 4
_RIGHT_HOLE_CX_FRACTION = 3 / 4
_PET_HOLE_CY_FRACTION = 1 / 3


def _draw_hole(boxes_obj, piece, cx_fraction: float, cy_fraction: float, hole_length: float) -> None:
    """Draw one horizontal, thickness-tall peg hole centered at
    (*cx_fraction*, *cy_fraction*) of *piece*'s (width, height) -- position
    is expressed as a fraction so it still lands correctly however big the
    chosen base artwork is or however --Base_height scales it.

    Shrunk by ``2 * burn`` on both dimensions, same kerf compensation as
    :meth:`Boxes.hole`/:meth:`Boxes.rectangularHole` -- the laser removes
    roughly ``burn`` of material on each side of a cut line, so drawing the
    hole smaller by that much keeps the peg a tight fit instead of loose."""
    length = max(hole_length - 2 * boxes_obj.burn, 0.0)
    height = max(boxes_obj.thickness - 2 * boxes_obj.burn, 0.0)
    cx = piece.width * cx_fraction
    cy = piece.height * cy_fraction
    with boxes_obj.saved_context():
        boxes_obj.set_source_color(Color.OUTER_CUT)
        boxes_obj.ctx.rectangle(cx - length / 2, cy - height / 2, length, height)
        boxes_obj.ctx.stroke()


def _draw_base_holes(boxes_obj, piece, pet_count: int) -> None:
    """Draw the miniature peg hole plus whichever pet peg hole(s) fit
    *pet_count* -- no user toggle, this is fully automatic:

     * 0 pets : miniature hole only, centered
     * 1 pet  : miniature hole moved up to the upper third (to leave the
                lower third clear), plus one pet hole -- right side by
                default, left if ``--Base_invert_pet_hole_side`` is set
     * 2 pets : miniature hole moved up, plus both pet holes
    """
    miniature_cy = 1 / 2 if pet_count == 0 else 2 / 3
    _draw_hole(boxes_obj, piece, 1 / 2, miniature_cy, _MINIATURE_HOLE_LENGTH)

    if pet_count == 2:
        _draw_hole(boxes_obj, piece, _LEFT_HOLE_CX_FRACTION, _PET_HOLE_CY_FRACTION, _PET_HOLE_LENGTH)
        _draw_hole(boxes_obj, piece, _RIGHT_HOLE_CX_FRACTION, _PET_HOLE_CY_FRACTION, _PET_HOLE_LENGTH)
    elif pet_count == 1:
        cx_fraction = _LEFT_HOLE_CX_FRACTION if boxes_obj.Base_invert_pet_hole_side else _RIGHT_HOLE_CX_FRACTION
        _draw_hole(boxes_obj, piece, cx_fraction, _PET_HOLE_CY_FRACTION, _PET_HOLE_LENGTH)


class MiniatureWorkshop(Boxes):
    """Pick a main character, up to two optional pets and a base -- get one
    board with all pieces laid out ready to laser in a single job."""

    description = (
        "Combines pre-drawn miniature artwork (main character, up to two "
        "optional pets, base) into a single laser-ready board. Each piece "
        "keeps the colors it was authored with; run "
        "boxes.generators.miniature.svgscan over an asset folder to check "
        "those colors against this app's cut/etch palette before trusting "
        "a new file."
    )

    ui_group = "Game"

    def __init__(self) -> None:
        Boxes.__init__(self)
        with self.settingsGroup("Miniature configuration"):
            self.addSettingsArgs(ResourceSettings, prefix="Character",
                                  folder=CHARACTER_DIR, label="Main character",
                                  default="random")
            self.addSettingsArgs(ResourceSettings, prefix="Pet",
                                  folder=PET_DIR, label="Pet", optional=True,
                                  default="random")
            self.addSettingsArgs(ResourceSettings, prefix="Pet2",
                                  folder=PET_DIR, label="Second pet", optional=True,
                                  default=None)
            self.addSettingsArgs(ResourceSettings, prefix="Base",
                                  folder=BASE_DIR, label="Base", height=40.0,
                                  optional=True, default="random")
            self.argparser.add_argument(
                "--gap", action="store", type=FloatStepper(0.5), default=1.0,
                help="Space between pieces on the board [mm]")
            self.argparser.add_argument(
                "--Base_invert_pet_hole_side", action="store", type=boolarg, default=False,
                help="With exactly one pet, put its peg hole on the left of the base instead of the right")

    def _load(self, folder, name, target_height=0.0):
        """Return (piece, scale) for the resource named *name* in *folder*,
        or None if unset. *scale* is >1 native size when *target_height*
        requests a different height."""
        path = resource_path(folder, name)
        if path is None:
            return None
        piece = load_svg_piece(path)
        scale = target_height / piece.height if target_height and piece.height else 1.0
        return piece, scale

    def _draw_at(self, piece, scale, x, y=0.0) -> None:
        with self.saved_context():
            self.ctx.translate(x, y)
            if scale != 1.0:
                self.ctx.scale(scale, scale)
            draw_piece(self, piece)

    # Margin between the outer cut border and every other piece [mm].
    OUTER_BORDER_MARGIN = 5.0

    def render(self) -> None:
        base = self._load(BASE_DIR, self.Base_resource, self.Base_height)
        character = self._load(CHARACTER_DIR, self.Character_resource)
        pets = [p for p in (self._load(PET_DIR, self.Pet_resource),
                             self._load(PET_DIR, self.Pet2_resource)) if p is not None]

        if base is None and character is None and not pets:
            raise ValueError("No character, pet or base resource available -- add svg files under the fantasy folder")

        x_cursor = 0.0
        bbox = None  # [min_x, min_y, max_x, max_y] over every piece actually drawn

        def draw_and_track(piece, scale, x, y=0.0) -> None:
            nonlocal bbox
            self._draw_at(piece, scale, x, y)
            x0, y0, x1, y1 = x, y, x + piece.width * scale, y + piece.height * scale
            if bbox is None:
                bbox = [x0, y0, x1, y1]
            else:
                bbox[0] = min(bbox[0], x0)
                bbox[1] = min(bbox[1], y0)
                bbox[2] = max(bbox[2], x1)
                bbox[3] = max(bbox[3], y1)

        if character is not None:
            piece, scale = character
            draw_and_track(piece, scale, x_cursor)
            x_cursor += piece.width * scale + self.gap

        if len(pets) == 2 and base is None:
            # Both pets get their own column, stacked one above the other.
            (piece1, scale1), (piece2, scale2) = pets
            draw_and_track(piece1, scale1, x_cursor, 0.0)
            draw_and_track(piece2, scale2, x_cursor, piece1.height * scale1 + self.gap)
            x_cursor += max(piece1.width * scale1, piece2.width * scale2) + self.gap

        if base is not None:
            piece, scale = base
            draw_and_track(piece, scale, x_cursor)
            # Peg holes stay full material thickness wide even when
            # --Base_height scales the artwork, so they are drawn outside
            # the scaled context, at the piece's scaled size.
            scaled_piece = SimpleNamespace(width=piece.width * scale, height=piece.height * scale)
            with self.saved_context():
                self.ctx.translate(x_cursor, 0)
                _draw_base_holes(self, scaled_piece, len(pets))

            if len(pets) == 1:
                # A single pet shares the base's column, stacked above it.
                pet_piece, pet_scale = pets[0]
                draw_and_track(pet_piece, pet_scale, x_cursor, piece.height * scale + self.gap)

            if len(pets) == 2:
                # With a base, both pets sit above it side by side instead
                # of stacked -- otherwise the stack would tower over the base.
                (pet1_piece, pet1_scale), (pet2_piece, pet2_scale) = pets
                pet_y = piece.height * scale + self.gap
                draw_and_track(pet1_piece, pet1_scale, x_cursor, pet_y)
                pet2_x = x_cursor + pet1_piece.width * pet1_scale + self.gap
                draw_and_track(pet2_piece, pet2_scale, pet2_x, pet_y)

            x_cursor += piece.width * scale + self.gap
        elif len(pets) == 1:
            # No base to stack on -- the single pet just gets its own column.
            piece, scale = pets[0]
            draw_and_track(piece, scale, x_cursor, 0.0)

        # Outer cut: a red rectangle self.OUTER_BORDER_MARGIN away from every
        # piece drawn above, on all four sides.
        min_x, min_y, max_x, max_y = bbox
        margin = self.OUTER_BORDER_MARGIN
        with self.saved_context():
            self.set_source_color(Color.OUTER_CUT)
            self.ctx.rectangle(min_x - margin, min_y - margin,
                                (max_x - min_x) + 2 * margin, (max_y - min_y) + 2 * margin)
            self.ctx.stroke()
