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

"""ScoreSettings – reusable argparse group for score-ring configuration.

Usage in any generator::

    from boxes.scoresettings import ScoreSettings

    class MyGenerator(Boxes):
        def __init__(self) -> None:
            Boxes.__init__(self)
            self.addSettingsArgs(ScoreSettings)

        def render(self) -> None:
            n = self.Score_max - self.Score_min + 1
"""

from __future__ import annotations

import argparse
from typing import cast

from boxes.args import IntStepper, FloatStepper
from boxes.edges import Settings


class ScoreSettings(Settings):
    """Score Settings

    Controls the score range and label placement on the ring.

     * min    : 0     : Minimum score value shown on the ring
     * max    : 20    : Maximum score value shown on the ring
     * radius : 0.0   : Radius for score labels [mm] (0 = auto)
     * angle  : 0.0   : Extra rotation applied to every label [degrees]. 0 = face outward, 180 = face inward
    """

    absolute_params: dict = {
        "min":    0,
        "max":    9,
        "radius": 0.0,
        "angle":  0.0,
    }
    relative_params: dict = {}

    @classmethod
    def parserArguments(cls, parser: argparse.ArgumentParser,
                        prefix: str | None = None, **defaults: object) -> None:
        """Register arguments in a dedicated *Score Settings* group."""
        prefix = prefix or "Score"

        group = parser.add_argument_group("Score Settings")
        group.prefix = prefix  # type: ignore[attr-defined]

        default_min = cast(int, defaults.get("min", cls.absolute_params["min"]))
        group.add_argument(
            f"--{prefix}_min",
            action="store", type=IntStepper(1),
            default=default_min,
            help="Minimum score value shown on the ring")

        default_max = cast(int, defaults.get("max", cls.absolute_params["max"]))
        group.add_argument(
            f"--{prefix}_max",
            action="store", type=IntStepper(1),
            default=default_max,
            help="Maximum score value shown on the ring")

        default_radius = float(defaults.get("radius", cls.absolute_params["radius"]))  # type: ignore[arg-type]
        group.add_argument(
            f"--{prefix}_radius",
            action="store", type=FloatStepper(0.5),
            default=default_radius,
            help="Radius at which score numbers are placed [mm]. 0 = auto (midpoint between inner and outer radii)")

        default_angle = float(defaults.get("angle", cls.absolute_params["angle"]))  # type: ignore[arg-type]
        group.add_argument(
            f"--{prefix}_angle",
            action="store", type=FloatStepper(1.0),
            default=default_angle,
            help="Extra rotation applied to every label [degrees]. 0 = face outward, 180 = face inward")

    def __init__(self, thickness: float, relative: bool = True, **kw: object) -> None:
        self.values: dict = {}
        self.thickness = thickness
