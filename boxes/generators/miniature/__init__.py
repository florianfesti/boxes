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

from boxes import Boxes, Color, FloatStepper
from boxes.settings.resource_settings import (
    NONE_CHOICE,
    DrawShape,
    ResourceSettings,
    draw_enabled_shapes,
    resource_path,
)

from .svgimport import draw_piece, load_svg_piece

THEME_DIR = pathlib.Path(__file__).parent / "fantasy"
CHARACTER_DIR = THEME_DIR / "character"
PET_DIR = THEME_DIR / "pet"
BASE_DIR = THEME_DIR / "base"


def _pet_selected(boxes_obj) -> bool:
    """True once either pet picker has an actual resource chosen."""
    return (getattr(boxes_obj, "Pet_resource", NONE_CHOICE) != NONE_CHOICE
            or getattr(boxes_obj, "Pet2_resource", NONE_CHOICE) != NONE_CHOICE)


def _miniature_hole_cy_fraction(boxes_obj) -> float:
    """Centered by default; moved up to the upper third once a pet is in
    play, to leave the lower third clear for the pet peg hole(s)."""
    return 2 / 3 if _pet_selected(boxes_obj) else 0.5


def _hole_drawer(cx_fraction, cy_fraction, hole_length: float):
    """Return a DrawShape.draw callback for a horizontal thickness-tall peg
    hole centered at (*cx_fraction*, *cy_fraction*) of the base piece's
    (width, height). Either fraction may be a plain float or a
    ``callable(boxes_obj) -> float`` for a position that depends on other
    settings (e.g. whether a pet is selected).

    Shrunk by ``2 * burn`` on both dimensions, same kerf compensation as
    :meth:`Boxes.hole`/:meth:`Boxes.rectangularHole` -- the laser removes
    roughly ``burn`` of material on each side of a cut line, so drawing the
    hole smaller by that much keeps the peg a tight fit instead of loose."""

    def draw(boxes_obj, piece) -> None:
        length = max(hole_length - 2 * boxes_obj.burn, 0.0)
        height = max(boxes_obj.thickness - 2 * boxes_obj.burn, 0.0)
        cx_frac = cx_fraction(boxes_obj) if callable(cx_fraction) else cx_fraction
        cy_frac = cy_fraction(boxes_obj) if callable(cy_fraction) else cy_fraction
        cx = piece.width * cx_frac
        cy = piece.height * cy_frac
        with boxes_obj.saved_context():
            boxes_obj.set_source_color(Color.OUTER_CUT)
            boxes_obj.ctx.rectangle(cx - length / 2, cy - height / 2, length, height)
            boxes_obj.ctx.stroke()

    return draw


# Optional peg holes overlaid on the Base artwork -- thickness-wide slots a
# character/pet peg is glued into. Position is expressed as a fraction of the
# base piece's own (width, height) so it still lands correctly however big
# the chosen base artwork is or however --Base_height scales it.
BASE_DRAW_SHAPES = [
    DrawShape("miniature_hole", _hole_drawer(0.5, _miniature_hole_cy_fraction, 15.0), default=True,
              label="miniature peg hole"),
    DrawShape("left_pet_hole", _hole_drawer(1 / 4, 1 / 3, 12.0), default=False,
              label="left pet peg hole"),
    DrawShape("right_pet_hole", _hole_drawer(3 / 4, 1 / 3, 12.0), default=True,
              label="right pet peg hole"),
]


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
                                  draw=BASE_DRAW_SHAPES, default="random")
            self.argparser.add_argument(
                "--gap", action="store", type=FloatStepper(0.5), default=1.0,
                help="Space between pieces on the board [mm]")

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

    def render(self) -> None:
        base = self._load(BASE_DIR, self.Base_resource, self.Base_height)
        character = self._load(CHARACTER_DIR, self.Character_resource)
        pets = [p for p in (self._load(PET_DIR, self.Pet_resource),
                             self._load(PET_DIR, self.Pet2_resource)) if p is not None]

        if base is None and character is None and not pets:
            raise ValueError("No character, pet or base resource available -- add svg files under the fantasy folder")

        x_cursor = 0.0


        if len(pets) == 1:
            # A single pet gets its own column, printed before the main
            # character so it lands on the same baseline (aligned with the
            # miniature), not stacked under the base.
            piece, scale = pets[0]
            self._draw_at(piece, scale, x_cursor, 0.0)
            x_cursor += piece.width * scale + self.gap

        if base is not None:
            piece, scale = base
            self._draw_at(piece, scale, x_cursor)
            # Peg holes stay full material thickness wide even when
            # --Base_height scales the artwork, so they are drawn outside
            # the scaled context, at the piece's scaled size.
            scaled_piece = SimpleNamespace(width=piece.width * scale, height=piece.height * scale)
            with self.saved_context():
                self.ctx.translate(x_cursor, 0)
                draw_enabled_shapes(self, "Base", BASE_DRAW_SHAPES, scaled_piece)
            x_cursor += piece.width * scale + self.gap

        if character is not None:
            piece, scale = character
            self._draw_at(piece, scale, x_cursor)
            x_cursor += piece.width * scale + self.gap

        if len(pets) == 2:
            # Both pets get their own column, stacked one above the other.
            (piece1, scale1), (piece2, scale2) = pets
            self._draw_at(piece1, scale1, x_cursor, 0.0)
            self._draw_at(piece2, scale2, x_cursor, piece1.height * scale1 + self.gap)
