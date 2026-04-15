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

"""LabelSettings – reusable argparse group for flat laser-cut label plates.

Usage in any generator::

    from boxes.settings.label_settings import LabelSettings

    class MyGenerator(Boxes):
        # mypy stubs
        Label_longueur:      float = 110.0
        Label_hauteur:       float = 40.0
        Label_radius:        float = 5.0
        Label_inner_border:  bool  = False
        Label_border_margin: float = 3.0

        def __init__(self) -> None:
            Boxes.__init__(self)
            self.addSettingsArgs(LabelSettings)
"""

from __future__ import annotations

import argparse

from boxes import boolarg
from boxes.args import FloatStepper
from boxes.edges import Settings


class LabelSettings(Settings):
    """Label Settings

    Controls the shape of a flat laser-cut label plate.

     * longueur      : 110.0 : Width of the label [mm]
     * hauteur       : 40.0  : Height of the label [mm]
     * radius        : 5.0   : Corner radius [mm] (0 = sharp corners)
     * inner_border  : False : Add a decorative inner border line
     * border_margin : 3.0   : Gap between outer cut and inner border [mm]
    """

    absolute_params: dict = {
        "longueur":      110.0,
        "hauteur":       40.0,
        "radius":        5.0,
        "inner_border":  False,
        "border_margin": 3.0,
    }
    relative_params: dict = {}

    @classmethod
    def parserArguments(
        cls,
        parser: argparse.ArgumentParser,
        prefix: str | None = None,
        **defaults: object,
    ) -> None:
        """Register all label shape arguments in a dedicated *Label Settings* group."""
        prefix = prefix or "Label"

        group = parser.add_argument_group("Label Settings")
        group.prefix = prefix  # type: ignore[attr-defined]

        group.add_argument(
            f"--{prefix}_longueur",
            action="store", type=FloatStepper(1.0),
            default=float(defaults.get("longueur", cls.absolute_params["longueur"])),  # type: ignore[arg-type]
            help="Width of the label [mm]")

        group.add_argument(
            f"--{prefix}_hauteur",
            action="store", type=FloatStepper(1.0),
            default=float(defaults.get("hauteur", cls.absolute_params["hauteur"])),  # type: ignore[arg-type]
            help="Height of the label [mm]")

        group.add_argument(
            f"--{prefix}_radius",
            action="store", type=FloatStepper(0.5),
            default=float(defaults.get("radius", cls.absolute_params["radius"])),  # type: ignore[arg-type]
            help="Corner radius [mm] (0 = sharp corners)")

        group.add_argument(
            f"--{prefix}_inner_border",
            action="store", type=boolarg,
            default=bool(defaults.get("inner_border", cls.absolute_params["inner_border"])),
            help="Add a decorative inner border line parallel to the outer edge")

        group.add_argument(
            f"--{prefix}_border_margin",
            action="store", type=FloatStepper(0.5),
            default=float(defaults.get("border_margin", cls.absolute_params["border_margin"])),  # type: ignore[arg-type]
            help="Gap between the outer cut and the inner border line [mm]")


    def __init__(self, thickness: float, relative: bool = True, **kw: object) -> None:
        # No relative params; thickness stored for API compatibility only.
        self.values: dict = {}
        self.thickness = thickness
