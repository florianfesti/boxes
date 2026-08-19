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

from boxes import Boxes
from boxes.settings.resource_settings import ResourceSettings, resource_path

from .svgimport import draw_piece, load_svg_piece

THEME_DIR = pathlib.Path(__file__).parent / "fantasy"
CHARACTER_DIR = THEME_DIR / "character"
PET_DIR = THEME_DIR / "pet"
BASE_DIR = THEME_DIR / "base"


class MiniatureWorkshop(Boxes):
    """Pick a main character, an optional pet and a base -- get one board with all
    three laid out ready to laser in a single job."""

    description = (
        "Combines pre-drawn miniature artwork (main character, optional pet, "
        "base) into a single laser-ready board. Each piece keeps the colors "
        "it was authored with; run boxes.generators.miniature.svgscan over an "
        "asset folder to check those colors against this app's cut/etch "
        "palette before trusting a new file."
    )

    ui_group = "Game"

    def __init__(self) -> None:
        Boxes.__init__(self)
        with self.settingsGroup("Miniature configuration"):
            self.addSettingsArgs(ResourceSettings, prefix="Character",
                                  folder=CHARACTER_DIR, label="Main character")
            self.addSettingsArgs(ResourceSettings, prefix="Pet",
                                  folder=PET_DIR, label="Pet", optional=True)
            self.addSettingsArgs(ResourceSettings, prefix="Base",
                                  folder=BASE_DIR, label="Base")
        self.argparser.add_argument(
            "--gap", action="store", type=float, default=5.0,
            help="Space between pieces on the board [mm]")

    def render(self) -> None:
        pieces = []
        for folder, name in (
            (BASE_DIR, self.Base_resource),
            (CHARACTER_DIR, self.Character_resource),
            (PET_DIR, self.Pet_resource),
        ):
            path = resource_path(folder, name)
            if path is not None:
                pieces.append(load_svg_piece(path))

        if not pieces:
            raise ValueError("No character, pet or base resource available -- add svg files under the fantasy folder")

        x_cursor = 0.0
        for piece in pieces:
            with self.saved_context():
                self.ctx.translate(x_cursor, 0)
                draw_piece(self, piece)
            x_cursor += piece.width + self.gap
