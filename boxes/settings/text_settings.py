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

"""TextSettings – reusable argparse group for engraved text on laser-cut parts.

Usage in any generator::

    from boxes.settings.text_settings import TextSettings

    class MyGenerator(Boxes):
        # mypy stubs
        Text_text:    str   = "Label"
        Text_x:       float = 0.0   # X offset from centre [mm]
        Text_y:       float = 0.0   # Y offset from centre [mm]
        Text_step:    float = 1.0   # d-pad step (UI only)
        Text_outline: float = 0.0   # outside outline stroke width [mm]

        def __init__(self) -> None:
            Boxes.__init__(self)
            self.addSettingsArgs(TextSettings)

        def render(self) -> None:
            cx, cy = ..., ...
            self.text(self.Text_text,
                      x=cx + self.Text_x, y=cy + self.Text_y,
                      align="middle center",
                      fontsize=self.Font_size,
                      color=Color.ETCHING,
                      outline_lw=self.Text_outline)
"""

from __future__ import annotations

import argparse

from boxes.args import DPadMoverArg, FloatStepper
from boxes.edges import Settings


class TextSettings(Settings):
    """Text Settings

    Controls the text content and position for laser-engraved text.

     * text    : Label : Text to engrave (leave blank to omit)
     * x       : 0.0   : Text X offset from centre [mm]
     * y       : 0.0   : Text Y offset from centre [mm]
     * step    : 1.0   : D-pad movement step [mm]
     * outline : 0.0   : Outside stroke width around each glyph [mm] (0 = none)
    """

    absolute_params: dict = {
        "text":    "Label",
        "x":       0.0,
        "y":       0.0,
        "step":    1.0,
        "outline": 0.0,
    }
    relative_params: dict = {}

    @classmethod
    def parserArguments(
        cls,
        parser: argparse.ArgumentParser,
        prefix: str | None = None,
        **defaults: object,
    ) -> None:
        """Register all text arguments in a dedicated *Text Settings* group."""
        prefix = prefix or "Text"

        group = parser.add_argument_group("Text Settings")
        group.prefix = prefix  # type: ignore[attr-defined]

        group.add_argument(
            f"--{prefix}_text",
            action="store", type=str,
            default=str(defaults.get("text", cls.absolute_params["text"])),
            help="Text to engrave on the label (leave blank to omit)")

        x_field = f"{prefix}_x"
        y_field = f"{prefix}_y"

        group.add_argument(
            f"--{x_field}",
            action="store", type=FloatStepper(1.0),
            default=float(defaults.get("x", cls.absolute_params["x"])),  # type: ignore[arg-type]
            help="Text X offset from centre [mm]")

        group.add_argument(
            f"--{y_field}",
            action="store", type=FloatStepper(1.0),
            default=float(defaults.get("y", cls.absolute_params["y"])),  # type: ignore[arg-type]
            help="Text Y offset from centre [mm]")

        group.add_argument(
            f"--{prefix}_step",
            action="store", type=DPadMoverArg(x_field, y_field, step=0.5),
            default=float(defaults.get("step", cls.absolute_params["step"])),  # type: ignore[arg-type]
            help="D-pad: click arrows to move text, · to re-centre")

        group.add_argument(
            f"--{prefix}_outline",
            action="store", type=FloatStepper(0.1),
            default=float(defaults.get("outline", cls.absolute_params["outline"])),  # type: ignore[arg-type]
            help="Outside stroke width around each glyph [mm] (0 = no outline)")

    def __init__(self, thickness: float, relative: bool = True, **kw: object) -> None:
        # No relative params; thickness stored for API compatibility only.
        self.values: dict = {}
        self.thickness = thickness
