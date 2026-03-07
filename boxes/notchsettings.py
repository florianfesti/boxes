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

"""NotchSettings – reusable argparse group for outer-notch (gear-rim) options.

Usage in any generator::

    from boxes.notchsettings import NotchSettings

    class MyGenerator(Boxes):
        def __init__(self) -> None:
            Boxes.__init__(self)
            self.addSettingsArgs(NotchSettings)

        def render(self) -> None:
            if self.Notch_enabled:
                self._draw_outer_notches(cx, cy, ro, ctx)
"""

from __future__ import annotations

import argparse

from boxes import BoolArg
from boxes.edges import Settings


class NotchSettings(Settings):
    """Notch Settings

    Controls the gear-like notches cut on the outer rim.

     * enabled    : False  : Add notches on the outer rim
     * depth      : 2.0   : Depth of each notch [mm]
     * shape      : symmetric : Notch wall shape: symmetric (straight walls) or radial (walls converge at centre)
     * rounded    : False  : Round the notch corners
     * radius     : 0.5   : Corner radius for rounded notches [mm]
    """

    absolute_params: dict = {
        "enabled": False,
        "depth":   2.0,
        "shape":   "symmetric",
        "rounded": False,
        "radius":  0.5,
    }
    relative_params: dict = {}

    @classmethod
    def parserArguments(cls, parser: argparse.ArgumentParser,
                        prefix: str | None = None, **defaults: object) -> None:
        """Register arguments in a dedicated *Notch Settings* group."""
        prefix = prefix or "Notch"

        group = parser.add_argument_group("Notch Settings")
        group.prefix = prefix  # type: ignore[attr-defined]

        default_enabled = bool(defaults.get("enabled", cls.absolute_params["enabled"]))
        group.add_argument(
            f"--{prefix}_enabled",
            action="store", type=BoolArg(),
            default=default_enabled,
            help="Add gear-like notches on the outer rim (one notch per score value)")

        default_depth = float(defaults.get("depth", cls.absolute_params["depth"]))  # type: ignore[arg-type]
        group.add_argument(
            f"--{prefix}_depth",
            action="store", type=float,
            default=default_depth,
            help="Depth of each outer notch [mm]")

        default_shape = str(defaults.get("shape", cls.absolute_params["shape"]))
        group.add_argument(
            f"--{prefix}_shape",
            action="store", type=str,
            default=default_shape,
            choices=["symmetric", "radial"],
            help="Notch wall shape: symmetric = straight walls perpendicular to the rim; "
                 "radial = walls converge toward the centre")

        default_rounded = bool(defaults.get("rounded", cls.absolute_params["rounded"]))
        group.add_argument(
            f"--{prefix}_rounded",
            action="store", type=BoolArg(),
            default=default_rounded,
            help="Round the notch corners instead of sharp right angles")

        default_radius = float(defaults.get("radius", cls.absolute_params["radius"]))  # type: ignore[arg-type]
        group.add_argument(
            f"--{prefix}_radius",
            action="store", type=float,
            default=default_radius,
            help="Corner radius for rounded notches [mm]")

    def __init__(self, thickness: float, relative: bool = True, **kw: object) -> None:
        # NotchSettings has no relative params and needs no thickness scaling.
        self.values: dict = {}
        self.thickness = thickness
