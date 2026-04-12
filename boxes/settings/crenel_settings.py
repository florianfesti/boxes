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

"""CrenelSettings – reusable argparse group for outer-crenel (gear-rim) options.

Usage in any generator::

    from boxes.crenelsettings import CrenelSettings

    class MyGenerator(Boxes):
        def __init__(self) -> None:
            Boxes.__init__(self)
            self.addSettingsArgs(CrenelSettings)

        def render(self) -> None:
            if self.crenel_enabled:
                self._draw_outer_crenels(cx, cy, ro, ctx)
"""

from __future__ import annotations

import argparse

from boxes import boolarg
from boxes.args import FloatStepper
from boxes.edges import Settings


class CrenelSettings(Settings):
    """Crenel Settings

    Controls the gear-like crenels cut on the outer rim.

     * enabled    : False  : Add crenels on the outer rim
     * depth      : 2.0   : Depth of each crenel [mm]
     * shape      : symmetric : Crenel wall shape: symmetric (straight walls) or radial (walls converge at center)
     * rounded    : False  : Round the crenel corners
     * radius     : 0.5   : Corner radius for rounded crenels [mm]
    """

    absolute_params: dict = {
        "enabled": True,
        "depth":   2.0,
        "shape":   "symmetric",
        "rounded": True,
        "radius":  0.5,
    }
    relative_params: dict = {}

    @classmethod
    def parserArguments(cls, parser: argparse.ArgumentParser,
                        prefix: str | None = None, **defaults: object) -> None:
        """Register arguments in a dedicated *Crenel Settings* group."""
        prefix = prefix or "crenel"

        group = parser.add_argument_group("Crenel Settings")
        group.prefix = prefix  # type: ignore[attr-defined]

        default_enabled = bool(defaults.get("enabled", cls.absolute_params["enabled"]))
        group.add_argument(
            f"--{prefix}_enabled",
            action="store", type=boolarg,
            default=default_enabled,
            help="Add gear-like crenels on the outer rim (one crenel per score value)")

        default_depth = float(defaults.get("depth", cls.absolute_params["depth"]))  # type: ignore[arg-type]
        group.add_argument(
            f"--{prefix}_depth",
            action="store", type=FloatStepper(0.5),
            default=default_depth,
            help="Depth of each outer crenel [mm]")

        default_shape = str(defaults.get("shape", cls.absolute_params["shape"]))
        group.add_argument(
            f"--{prefix}_shape",
            action="store", type=str,
            default=default_shape,
            choices=["symmetric", "radial"],
            help="Crenel wall shape: symmetric = straight walls perpendicular to the rim; "
                 "radial = walls converge toward the center")

        default_rounded = bool(defaults.get("rounded", cls.absolute_params["rounded"]))
        group.add_argument(
            f"--{prefix}_rounded",
            action="store", type=boolarg,
            default=default_rounded,
            help="Round the crenel corners instead of sharp right angles")

        default_radius = float(defaults.get("radius", cls.absolute_params["radius"]))  # type: ignore[arg-type]
        group.add_argument(
            f"--{prefix}_radius",
            action="store", type=FloatStepper(0.5),
            default=default_radius,
            help="Corner radius for rounded crenels [mm]")

    def __init__(self, thickness: float, relative: bool = True, **kw: object) -> None:
        # CrenelSettings has no relative params and needs no thickness scaling.
        self.values: dict = {}
        self.thickness = thickness
