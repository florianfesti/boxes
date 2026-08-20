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

"""ResourceSettings – reusable argparse group for picking one file out of a
folder of interchangeable assets (e.g. pre-drawn svg artwork).

One generator can load several independent resource pickers by registering
this settings group multiple times with a different prefix/folder each time::

    from boxes.settings.resource_settings import ResourceSettings, resource_path

    class MyGenerator(Boxes):
        def __init__(self) -> None:
            Boxes.__init__(self)
            self.addSettingsArgs(ResourceSettings, prefix="Character",
                                  folder=CHARACTER_DIR, label="Character")
            self.addSettingsArgs(ResourceSettings, prefix="Pet",
                                  folder=PET_DIR, label="Pet", optional=True)
            self.addSettingsArgs(ResourceSettings, prefix="Base",
                                  folder=BASE_DIR, label="Base", height=40.0,
                                  draw=[BASE_MINIATURE_HOLE])

        def render(self) -> None:
            path = resource_path(PET_DIR, self.Pet_resource)
            if path is not None:
                piece = load_svg_piece(path)
                ...
                draw_enabled_shapes(self, "Pet", [BASE_MINIATURE_HOLE], piece)

A ``draw`` shape is a :class:`DrawShape`: a name, an on/off checkbox default
and a ``draw(boxes, piece)`` callback that overlays extra geometry (e.g. an
assembly hole) on top of the imported artwork -- see :func:`draw_enabled_shapes`.
"""

from __future__ import annotations

import argparse
import pathlib
import random
from dataclasses import dataclass
from typing import Any, Callable

from boxes import FloatStepper, boolarg
from boxes.edges import Settings

# Sentinel choice used by optional resource pickers to mean "none selected".
NONE_CHOICE = "none"

# Sentinel meaning "the 'default' kwarg was not passed at all" -- distinct
# from a caller explicitly passing default=None (which means "start on the
# 'none' choice").
_DEFAULT_UNSET = object()


@dataclass(frozen=True)
class DrawShape:
    """One optional piece of geometry a resource picker can overlay on the
    imported artwork, toggled by its own on/off checkbox in the UI.

     * name    : argument suffix (``--{prefix}_draw_{name}``) and dict key
     * draw    : called as ``draw(boxes, piece)`` with ``boxes.ctx`` at the
                 piece's own origin -- same coordinate space as the artwork
                 (0,0 = bottom-left, y up), so it can be positioned relative
                 to ``piece.width``/``piece.height``
     * default : whether the checkbox starts checked
     * label   : human-readable name for the checkbox help text (defaults to
                 *name* with underscores turned into spaces)
    """

    name: str
    draw: Callable[[Any, Any], None]
    default: bool = True
    label: str | None = None


def draw_enabled_shapes(boxes_obj, prefix: str, shapes: list[DrawShape], piece) -> None:
    """Call ``shape.draw(boxes_obj, piece)`` for every *shapes* entry whose
    checkbox is currently on for *prefix* (as registered via ``draw=`` on
    :class:`ResourceSettings`)."""
    for shape in shapes:
        if getattr(boxes_obj, f"{prefix}_draw_{shape.name}"):
            shape.draw(boxes_obj, piece)


def discover_resources(folder, extensions: tuple[str, ...] = (".svg",)) -> list[str]:
    """Return the sorted stems of every matching file directly inside *folder*."""
    folder = pathlib.Path(folder)
    if not folder.is_dir():
        return []
    exts = {e.lower() for e in extensions}
    return sorted(p.stem for p in folder.iterdir() if p.is_file() and p.suffix.lower() in exts)


def resource_path(folder, name: str, extensions: tuple[str, ...] = (".svg",)) -> pathlib.Path | None:
    """Return the full path for a resource selected by stem *name*, or None."""
    if not name or name == NONE_CHOICE:
        return None
    folder = pathlib.Path(folder)
    exts = {e.lower() for e in extensions}
    for p in folder.iterdir():
        if p.is_file() and p.stem == name and p.suffix.lower() in exts:
            return p
    return None


class ResourceSettings(Settings):
    """Resource Settings

    Lets the user pick one file (by name) from a folder of interchangeable
    assets. Registering this group multiple times with different prefixes is
    the common way to offer several independent resource choices in one
    generator.

     * resource : "" : selected file name (stem), "none" when optional and unset.
       Its starting value is controlled by the ``default=`` kwarg -- see
       ``parserArguments`` below.
     * height : only present when registered with a ``height=<default mm>``
       kwarg (its value becomes this argument's default). Target height in
       mm; 0 means "use the artwork's native size". Any other value scales
       the resource proportionally, which also changes e.g. a round piece's
       diameter.
     * draw_{name} : one on/off checkbox per :class:`DrawShape` passed via
       ``draw=[...]``, defaulting to that shape's own ``default``. Call
       :func:`draw_enabled_shapes` in ``render()`` to act on them.
    """

    absolute_params: dict = {"resource": ""}
    relative_params: dict = {}

    @classmethod
    def parserArguments(
        cls,
        parser: argparse.ArgumentParser,
        prefix: str | None = None,
        **defaults: object,
    ) -> None:
        """Register a dynamic ``choices`` argument populated from *folder*.

        Required keyword: ``folder`` (path to the resource directory).
        Optional keywords: ``label`` (group title, defaults to *prefix*),
        ``extensions`` (defaults to ``(".svg",)``), ``optional`` (adds a
        "none" choice, defaults to ``False``), ``height`` (a default mm
        value that both enables and seeds a target-height argument used to
        scale the resource; omit it to not offer height scaling at all),
        ``draw`` (a list of :class:`DrawShape` -- each gets its own on/off
        checkbox, defaulting to that shape's ``default``) and ``default``
        (the starting selection -- omit it to just default to the first
        discovered resource, or pass ``None`` to start on "none" (requires
        ``optional=True``), ``"random"`` to pick a random resource each time
        this generator's argument parser is built, or any other string to
        search the discovered resource names for a case-insensitive
        substring match, falling back to the first resource if none match).
        """
        folder = defaults.pop("folder", None)
        if folder is None:
            raise ValueError("ResourceSettings requires a 'folder' kwarg pointing to the resource directory")
        extensions = defaults.pop("extensions", (".svg",))
        optional = bool(defaults.pop("optional", False))
        height_default = defaults.pop("height", None)
        shapes: list[DrawShape] = list(defaults.pop("draw", ()) or ())
        requested_default = defaults.pop("default", _DEFAULT_UNSET)
        label = str(defaults.pop("label", prefix or "Resource"))

        prefix = prefix or "Resource"
        group = parser.add_argument_group(f"{label} Settings")
        group.prefix = prefix  # type: ignore[attr-defined]

        choices = discover_resources(folder, extensions)
        if optional:
            choices = [NONE_CHOICE] + choices
        if not choices:
            choices = [NONE_CHOICE]

        if requested_default is _DEFAULT_UNSET:
            default = str(defaults.get("resource", ""))
            if default not in choices:
                default = choices[0]
        elif requested_default is None:
            default = NONE_CHOICE if NONE_CHOICE in choices else choices[0]
        elif requested_default == "random":
            pool = [c for c in choices if c != NONE_CHOICE] or choices
            default = random.choice(pool)
        else:
            search = str(requested_default).lower()
            matches = [c for c in choices if search in c.lower()]
            default = matches[0] if matches else choices[0]

        resource_action = group.add_argument(
            f"--{prefix}_resource",
            action="store", type=str,
            default=default,
            choices=choices,
            help=f"{label} to use")
        # The group heading ("{label} Settings") already names this control,
        # so its own row label would just repeat "resource" -- blank it out.
        resource_action.display_name = ""  # type: ignore[attr-defined]

        if height_default is not None:
            group.add_argument(
                f"--{prefix}_height",
                action="store", type=FloatStepper(0.5),
                default=float(height_default),
                help=f"{label} height in mm (0 = use the artwork's native size; "
                     f"scales it proportionally, e.g. also changes a round piece's diameter)")

        for shape in shapes:
            shape_label = shape.label or shape.name.replace("_", " ")
            group.add_argument(
                f"--{prefix}_draw_{shape.name}",
                action="store", type=boolarg,
                default=shape.default,
                help=f"Draw the {shape_label} on the {label.lower()}")

    def __init__(self, thickness: float, relative: bool = True, **kw: object) -> None:
        # No relative params; thickness stored for API compatibility only.
        self.values: dict = {}
        self.thickness = thickness
