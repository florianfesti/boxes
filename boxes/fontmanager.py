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
    # Prefer vector-outline formats (ttf/otf) that fontTools can load directly;
    # fall back to woff formats only when no ttf/otf is available.
    _PREFER_ORDER: list[str] = [".ttf", ".otf", ".woff", ".woff2"]
    candidates: list[pathlib.Path] = [
        p for p in FONTS_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() in _FONT_EXTENSIONS
        and (p.stem == name or _normalize(p.stem) == norm)
    ]
    candidates.sort(key=lambda p: _PREFER_ORDER.index(p.suffix.lower())
                    if p.suffix.lower() in _PREFER_ORDER else len(_PREFER_ORDER))
    return candidates[0] if candidates else None


def font_as_data_uri(name: str) -> str | None:
    """Return a base64 data URI for *name*, or ``None`` if not found."""
    path = font_path(name)
    if path is None:
        return None
    mime = _FONT_MIME.get(path.suffix.lower(), "font/ttf")
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


# Ordered candidate paths for each built-in generic, tried in sequence.
_GENERIC_SYSTEM_FONTS: dict[str, list[str]] = {
    "sans-serif": [
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        # macOS
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
        # Windows
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ],
    "serif": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
        "/System/Library/Fonts/Times.ttc",
        "/Library/Fonts/Times New Roman.ttf",
        "C:/Windows/Fonts/times.ttf",
        "C:/Windows/Fonts/georgia.ttf",
    ],
    "monospaced": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeMono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        "/Library/Fonts/Courier New.ttf",
        "C:/Windows/Fonts/cour.ttf",
        "C:/Windows/Fonts/consola.ttf",
    ],
}

# Cache resolved paths so the filesystem is only scanned once per session.
_generic_cache: dict[str, pathlib.Path | None] = {}


def resolve_font_path(name: str) -> pathlib.Path | None:
    """Return a font file path for *name*, including built-in generic families.

    For custom (file-based) fonts this is identical to :func:`font_path`.
    For built-in generics (``sans-serif``, ``serif``, ``monospaced``) the
    function probes common system font locations and returns the first match,
    enabling text-to-path conversion even for the default font families.
    Returns ``None`` only when no matching file can be found at all.
    """
    custom = font_path(name)
    if custom is not None:
        return custom
    if name not in BUILTIN_FONTS:
        return None
    if name in _generic_cache:
        return _generic_cache[name]
    result: pathlib.Path | None = None
    for candidate in _GENERIC_SYSTEM_FONTS.get(name, []):
        p = pathlib.Path(candidate)
        if p.is_file():
            result = p
            break
    _generic_cache[name] = result
    return result


def text_to_svg_path(
    text: str,
    font_name: str,
    size_mm: float,
    align: str = "left",
) -> str | None:
    """Convert *text* to a single SVG path ``d`` string using a file-based font.

    Returns ``None`` when the font is a built-in generic (no font file) or
    when fontTools is unavailable.  *align* matches SVG ``text-anchor``:
    ``"left"`` / ``"middle"`` / ``"end"``.

    Coordinate system: paths are emitted in the same mm-space as the rest of
    the SVG (Y-down).  The caller should apply the same transform matrix used
    for the original ``<text>`` element.
    """
    fpath = font_path(font_name)
    if fpath is None:
        return None

    try:
        from fontTools.pens.svgPathPen import SVGPathPen
        from fontTools.pens.transformPen import TransformPen
        from fontTools.ttLib import TTFont
    except ImportError:
        return None

    try:
        font = TTFont(str(fpath))
    except Exception:
        # e.g. corrupt file, unsupported format – fall back to <text>
        return None
    glyph_set = font.getGlyphSet()
    cmap: dict[int, str] = font.getBestCmap() or {}
    upm: int = font["head"].unitsPerEm
    scale = size_mm / upm

    # First pass: total advance width for alignment offset.
    total_width = 0.0
    for char in text:
        gname = cmap.get(ord(char))
        total_width += (glyph_set[gname].width * scale) if gname else (size_mm * 0.5)

    if align == "middle":
        x_offset = -total_width / 2.0
    elif align == "end":
        x_offset = -total_width
    else:
        x_offset = 0.0

    # Second pass: render each glyph with its accumulated x translation.
    parts: list[str] = []
    x_cursor = x_offset
    for char in text:
        gname = cmap.get(ord(char))
        if gname is None:
            x_cursor += size_mm * 0.5
            continue
        glyph = glyph_set[gname]
        svg_pen: SVGPathPen = SVGPathPen(glyph_set)
        # scale X, flip Y (font Y-up → SVG Y-down), translate by x_cursor
        xform_pen = TransformPen(svg_pen, (scale, 0, 0, -scale, x_cursor, 0))
        glyph.draw(xform_pen)
        d: str = svg_pen.getCommands()
        if d:
            parts.append(d)
        x_cursor += glyph.width * scale

    return " ".join(parts) if parts else None
