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

"""Font discovery and embedding helpers for boxes SVG output.

Drop any ``.ttf`` or ``.otf`` file into ``boxes/fonts/`` and it will be
auto-discovered.  The font name exposed to users is the bare filename stem
(e.g. ``OpenSans-Bold`` for ``OpenSans-Bold.ttf``).

Built-in generic families (``sans-serif``, ``serif``, ``monospaced``) are
always available and do *not* require a file.
"""

from __future__ import annotations

import base64
import pathlib

# Folder that holds custom font files shipped with (or added to) the project.
FONTS_DIR: pathlib.Path = pathlib.Path(__file__).parent / "fonts"

# Generic CSS families that are always available without a font file.
BUILTIN_FONTS: list[str] = ["sans-serif", "serif", "monospaced"]

# Supported font file extensions.
_FONT_EXTENSIONS: frozenset[str] = frozenset({".ttf", ".otf", ".woff2", ".woff"})

# MIME type for each extension.
_FONT_MIME: dict[str, str] = {
    ".ttf":   "font/ttf",
    ".otf":   "font/otf",
    ".woff2": "font/woff2",
    ".woff":  "font/woff",
}


def _normalize(name: str) -> str:
    """Lowercase and replace spaces/underscores with hyphens for fuzzy matching."""
    return name.lower().replace(" ", "-").replace("_", "-")


def discover_fonts() -> list[str]:
    """Return a sorted list of all available font names.

    The list starts with the three built-in generics, followed by the stems
    of every ``.ttf`` / ``.otf`` file found anywhere inside :data:`FONTS_DIR`
    (including sub-folders).
    """
    custom: list[str] = []
    if FONTS_DIR.is_dir():
        custom = sorted(
            p.stem
            for p in FONTS_DIR.rglob("*")
            if p.is_file() and p.suffix.lower() in _FONT_EXTENSIONS
        )
    return BUILTIN_FONTS + custom


def font_path(name: str) -> pathlib.Path | None:
    """Return the :class:`~pathlib.Path` for a custom font name, or ``None``.

    Returns ``None`` for the three built-in generic families.
    Searches recursively through all sub-folders of :data:`FONTS_DIR`.
    Matches both exact stem and a normalised form (lowercase, spaces→hyphens).
    """
    if name in BUILTIN_FONTS:
        return None
    if not FONTS_DIR.is_dir():
        return None
    norm = _normalize(name)
    for p in FONTS_DIR.rglob("*"):
        if p.is_file() and p.suffix.lower() in _FONT_EXTENSIONS:
            if p.stem == name or _normalize(p.stem) == norm:
                return p
    return None


def font_as_data_uri(name: str) -> str | None:
    """Return a base64 data URI for *name*, or ``None`` if not found."""
    path = font_path(name)
    if path is None:
        return None
    mime = _FONT_MIME.get(path.suffix.lower(), "font/ttf")
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"
