#!/usr/bin/env python3
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

"""regen_svg.py – regenerate reference SVG(s) for one or more generators.

Usage::

    python scripts/regen_svg.py GameCounterRing
    python scripts/regen_svg.py GameCounterRing ABox ClosedBox
    python scripts/regen_svg.py --all

The script writes to ``examples/<GeneratorName>.svg`` and prints one line per
file so you can pipe it straight into ``git add``.
"""

from __future__ import annotations

import argparse
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

# Allow running from the repo root without installing the package.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import boxes.generators  # noqa: E402  (after sys.path fix)


def regen(name: str) -> bool:
    """Regenerate the reference SVG for generator *name*.

    Returns True on success, False if the generator does not produce SVG output.
    """
    all_generators = boxes.generators.getAllBoxGenerators()
    # getAllBoxGenerators keys are full paths like 'boxes.generators.foo.Bar'.
    # Accept both the full key and the short class name.
    cls = all_generators.get(name)
    if cls is None:
        by_class = {v.__name__: v for v in all_generators.values()}
        cls = by_class.get(name)
    if cls is None:
        short_names = sorted({v.__name__ for v in all_generators.values()})
        raise SystemExit(f"Unknown generator: {name!r}.\nAvailable: {short_names}")

    b = cls()
    b.parseArgs([])
    b.metadata["reproducible"] = True
    with redirect_stdout(io.StringIO()):
        b.open()
        b.render()
        data = b.close()

    if data is None:
        print(f"  (skipped {name} – no SVG output)", flush=True)
        return False

    out = ROOT / "examples" / f"{name}.svg"
    out.write_bytes(data.getvalue())
    print(str(out), flush=True)
    return True


def interactive_select() -> list[str]:
    """Display a numbered list of all generators and let the user pick."""
    all_generators = boxes.generators.getAllBoxGenerators()
    names = sorted({v.__name__ for v in all_generators.values()})

    print("Available generators:")
    for i, name in enumerate(names, 1):
        print(f"  {i:3d}. {name}")

    print("\nEnter numbers separated by spaces/commas, or 'all' to regenerate everything.")
    print("Press Enter without input to cancel.")
    raw = input("> ").strip()

    if not raw:
        raise SystemExit("Cancelled.")
    if raw.lower() == "all":
        return names

    selected: list[str] = []
    for token in raw.replace(",", " ").split():
        try:
            idx = int(token)
        except ValueError:
            print(f"  Skipping invalid token: {token!r}")
            continue
        if 1 <= idx <= len(names):
            selected.append(names[idx - 1])
        else:
            print(f"  Out of range: {idx}")

    if not selected:
        raise SystemExit("No valid selection.")
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("generators", nargs="*", metavar="GeneratorName",
                        help="One or more generator class names.")
    parser.add_argument("--all", action="store_true",
                        help="Regenerate SVGs for all generators.")
    args = parser.parse_args()

    if args.all:
        names = sorted({v.__name__ for v in boxes.generators.getAllBoxGenerators().values()})
    elif args.generators:
        names = args.generators
    else:
        names = interactive_select()

    ok = skipped = failed = 0
    for name in names:
        try:
            if regen(name):
                ok += 1
            else:
                skipped += 1
        except Exception as exc:
            print(f"  ERROR {name}: {exc}", flush=True)
            failed += 1

    if len(names) > 1:
        print(f"\nDone: {ok} regenerated, {skipped} skipped, {failed} failed.")


if __name__ == "__main__":
    main()
