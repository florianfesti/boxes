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

"""Color audit for a folder of pre-drawn svg artwork (e.g. miniature/fantasy).

Boxes.py maps colors to laser roles (:mod:`boxes.Color`): black = outer cut,
blue = inner cut, red = annotations (never sent to the laser), green/cyan =
etching, magenta = solid fill. Artwork imported from other tools rarely uses
those exact colors, so this module reports every fill/stroke color found in
each svg file next to its closest matching role and how far off it is --
letting a human decide whether the source file needs fixing before it is
trusted for laser output.

Scanning never rewrites anything. :func:`fix_folder` can rewrite svg files,
but only a color at a time and only after the user confirms each swap.
"""

from __future__ import annotations

import pathlib
import re

from boxes.Color import Color

_COLOR_ATTR_RE = re.compile(r'(?:fill|stroke)="(#[0-9a-fA-F]{3,8}|[a-zA-Z]+)"')

# Roles a piece of artwork could plausibly be mapped to (excludes ANNOTATIONS'
# aliases that just duplicate another named color in boxes.Color).
_ROLES = ("OUTER_CUT", "INNER_CUT", "ANNOTATIONS", "ETCHING", "ETCHING_DEEP", "SOLID_FILL")

# Roles that are stripped before the laser ever sees them -- landing here by
# accident silently drops geometry, so it is always worth flagging.
_DISCARDED_ROLES = {"ANNOTATIONS"}

EXACT_MATCH_TOLERANCE = 1e-6
# Distance is euclidean over 0..255 per channel (max possible ~441.7).
NEAR_MATCH_DISTANCE = 40.0


def _hex_to_rgb255(value: str) -> tuple[int, int, int] | None:
    value = value.strip()
    if not value.startswith("#"):
        return None  # named CSS colors are reported as-is, not resolved
    h = value[1:]
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) not in (6, 8):
        return None
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def nearest_role(hex_color: str) -> tuple[str | None, float | None]:
    """Return (role_name, distance_0_255) of the closest boxes.Color role.

    Returns (None, None) if *hex_color* isn't a resolvable #rrggbb(aa) value.
    """
    rgb = _hex_to_rgb255(hex_color)
    if rgb is None:
        return None, None
    best_role: str | None = None
    best_dist: float | None = None
    for role in _ROLES:
        r, g, b = (v * 255 for v in getattr(Color, role))
        dist = ((rgb[0] - r) ** 2 + (rgb[1] - g) ** 2 + (rgb[2] - b) ** 2) ** 0.5
        if best_dist is None or dist < best_dist:
            best_role, best_dist = role, dist
    return best_role, best_dist


def colors_in_svg(path: pathlib.Path) -> list[str]:
    """Return the sorted distinct fill/stroke color values found in an svg file."""
    text = path.read_text(encoding="utf-8", errors="replace")
    found = {m.group(1) for m in _COLOR_ATTR_RE.finditer(text)}
    found.discard("none")
    return sorted(found)


def _describe_color(color: str) -> tuple[str, str]:
    """Return (status, role) markdown cell contents for *color*."""
    role, dist = nearest_role(color)
    if role is None or dist is None:
        return "unresolved (named CSS color, not checked)", "--"
    if dist <= EXACT_MATCH_TOLERANCE:
        status = "OK exact match"
    elif dist <= NEAR_MATCH_DISTANCE:
        status = f"WARNING approx match (distance {dist:.1f})"
    else:
        status = f"WARNING no close match (distance {dist:.1f})"
    if role in _DISCARDED_ROLES:
        status += " -- discarded before laser, check intended"
    return status, role


def scan_folder(folder: pathlib.Path) -> str:
    """Scan every .svg file under *folder* and return a markdown report."""
    folder = pathlib.Path(folder)
    lines = [f"# Color scan of `{folder}`", ""]
    svg_files = sorted(folder.rglob("*.svg"))
    if not svg_files:
        lines.append("(no svg files found)")
        return "\n".join(lines)

    lines += ["| File | Color | Nearest role | Status |", "| --- | --- | --- | --- |"]
    for svg_file in svg_files:
        rel = svg_file.relative_to(folder)
        colors = colors_in_svg(svg_file)
        if not colors:
            lines.append(f"| {rel} | -- | -- | (no fill/stroke colors found) |")
            continue
        for i, color in enumerate(colors):
            status, role = _describe_color(color)
            lines.append(f"| {rel if i == 0 else ''} | `{color}` | {role} | {status} |")
    return "\n".join(lines)


def write_scan_log(folder: pathlib.Path, log_path: pathlib.Path | None = None) -> pathlib.Path:
    """Write the report from :func:`scan_folder` to *log_path* (default: folder/scan.md)."""
    folder = pathlib.Path(folder)
    log_path = pathlib.Path(log_path) if log_path is not None else folder / "scan.md"
    log_path.write_text(scan_folder(folder), encoding="utf-8")
    return log_path


def _replace_color_attr(text: str, old_color: str, new_color: str) -> str:
    """Replace *old_color* with *new_color* in every fill="..."/stroke="..." attribute."""
    pattern = re.compile(r'(fill|stroke)="' + re.escape(old_color) + r'"')
    return pattern.sub(lambda m: f'{m.group(1)}="{new_color}"', text)


def fix_folder(folder: pathlib.Path, ask=input, tell=print) -> list[pathlib.Path]:
    """Walk every .svg under *folder*, offering to swap each non-exact color to
    its nearest laser role's exact hex value.

    For every fill/stroke color that isn't already an exact match for a role
    (and isn't an unresolved named CSS color), prompts via *ask* with
    ``"y"`` to swap, ``"n"`` to leave it, or ``"q"`` to stop scanning
    entirely. Only files with at least one confirmed swap are rewritten.
    Returns the list of files that were changed.
    """
    folder = pathlib.Path(folder)
    changed_files = []
    for svg_file in sorted(folder.rglob("*.svg")):
        rel = svg_file.relative_to(folder)
        text = svg_file.read_text(encoding="utf-8", errors="replace")
        file_changed = False
        for color in colors_in_svg(svg_file):
            role, dist = nearest_role(color)
            if role is None or dist is None or dist <= EXACT_MATCH_TOLERANCE:
                continue  # unresolved name or already an exact match, nothing to fix
            new_color = Color.to_hex(getattr(Color, role))
            answer = ask(f"{rel}: swap {color} -> {new_color} ({role})? [y/N/q] ").strip().lower()
            if answer == "q":
                if file_changed:
                    svg_file.write_text(text, encoding="utf-8")
                    changed_files.append(svg_file)
                return changed_files
            if answer == "y":
                text = _replace_color_attr(text, color, new_color)
                file_changed = True
        if file_changed:
            svg_file.write_text(text, encoding="utf-8")
            changed_files.append(svg_file)
            tell(f"fixed {rel}")
    return changed_files


if __name__ == "__main__":
    import sys

    target = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).parent / "fantasy"
    out = write_scan_log(target)
    print(f"Wrote {out}")

    #if "--fix" in sys.argv[2:]:
    #    fix_folder(target)

    fix_folder(target)
