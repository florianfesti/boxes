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

        def render(self) -> None:
            path = resource_path(PET_DIR, self.Pet_resource)
            if path is not None:
                ...
"""

from __future__ import annotations

import argparse
import pathlib

from boxes.edges import Settings

# Sentinel choice used by optional resource pickers to mean "none selected".
NONE_CHOICE = "none"


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

     * resource : "" : selected file name (stem), "none" when optional and unset
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
        ``extensions`` (defaults to ``(".svg",)``) and ``optional`` (adds a
        "none" choice, defaults to ``False``).
        """
        folder = defaults.pop("folder", None)
        if folder is None:
            raise ValueError("ResourceSettings requires a 'folder' kwarg pointing to the resource directory")
        extensions = defaults.pop("extensions", (".svg",))
        optional = bool(defaults.pop("optional", False))
        label = str(defaults.pop("label", prefix or "Resource"))

        prefix = prefix or "Resource"
        group = parser.add_argument_group(f"{label} Settings")
        group.prefix = prefix  # type: ignore[attr-defined]

        choices = discover_resources(folder, extensions)
        if optional:
            choices = [NONE_CHOICE] + choices
        if not choices:
            choices = [NONE_CHOICE]

        default = str(defaults.get("resource", ""))
        if default not in choices:
            default = choices[0]

        group.add_argument(
            f"--{prefix}_resource",
            action="store", type=str,
            default=default,
            choices=choices,
            help=f"{label} to use")

    def __init__(self, thickness: float, relative: bool = True, **kw: object) -> None:
        # No relative params; thickness stored for API compatibility only.
        self.values: dict = {}
        self.thickness = thickness
