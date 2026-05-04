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
    python scripts/regen_svg.py --examples   # also regenerate hash-suffixed SVGs from examples.yml

The script writes the SVG next to the generator source file (same stem,
``.svg`` extension) and prints one line per file so you can pipe it straight
into ``git add``.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import io
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import redirect_stdout
from pathlib import Path

import yaml

# Allow running from the repo root without installing the package.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import boxes.generators  # noqa: E402  (after sys.path fix)

# Maximum number of parallel SVG generation threads.
MAX_WORKERS: int = 10


def _svg_path(cls: type) -> Path:
    """Return the reference SVG path for a generator class.

    Handles both the legacy flat layout (``xxx.py``) and the new
    per-generator folder layout where the source is ``xxx/__init__.py``.
    """
    gen_file = Path(inspect.getfile(cls))
    if gen_file.name == "__init__.py":
        return gen_file.parent / (gen_file.parent.name + ".svg")
    return gen_file.with_suffix(".svg")


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

    out = _svg_path(cls)
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


def regen_examples() -> None:
    """Regenerate hash-suffixed SVGs for all entries in examples.yml."""
    examples_file = ROOT / "examples.yml"
    if not examples_file.is_file():
        print("examples.yml not found – skipping.", flush=True)
        return

    with examples_file.open() as f:
        config = yaml.safe_load(f)

    all_generators = boxes.generators.getAllBoxGenerators()
    by_name = {v.__name__: v for v in all_generators.values()}

    def _regen_entry(entry: dict) -> tuple[str, str]:
        """Regenerate one examples.yml entry. Returns (status, gen_name)."""
        gen_name = entry.get("box_type", "")
        if not gen_name or gen_name == "__ALL__":
            return ("skip", gen_name)
        args_dict: dict = entry.get("args", {})
        cls = by_name.get(gen_name)
        if cls is None:
            print(f"  SKIP {gen_name}: not found", flush=True)
            return ("skip", gen_name)

        box_args = [f"--{k}={v}" for k, v in args_dict.items()]
        args_hash = hashlib.sha1(" ".join(sorted(box_args)).encode()).hexdigest()

        gen_file = Path(inspect.getfile(cls))
        stem = gen_file.parent.name if gen_file.name == "__init__.py" else gen_file.stem
        out = gen_file.parent / f"{stem}_{args_hash[:8]}.svg"

        b = cls()
        b.parseArgs(box_args)
        b.metadata["reproducible"] = True
        b.metadata["args_hash"] = args_hash
        with redirect_stdout(io.StringIO()):
            b.open()
            b.render()
            data = b.close()
        if data is None:
            print(f"  SKIP {gen_name}: no SVG output", flush=True)
            return ("skip", gen_name)
        out.write_bytes(data.getvalue())
        print(str(out), flush=True)
        return ("ok", gen_name)

    ok = skipped = failed = 0
    entries = [e for e in config.get("Boxes", []) if e.get("box_type")]
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_regen_entry, entry): entry.get("box_type", "") for entry in entries}
        for future in as_completed(futures):
            gen_name = futures[future]
            try:
                status, _ = future.result()
                if status == "ok":
                    ok += 1
                else:
                    skipped += 1
            except Exception as exc:
                print(f"  ERROR {gen_name}: {exc}", flush=True)
                failed += 1

    print(f"\nExamples done: {ok} regenerated, {skipped} skipped, {failed} failed.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("generators", nargs="*", metavar="GeneratorName",
                        help="One or more generator class names.")
    parser.add_argument("--all", action="store_true",
                        help="Regenerate SVGs for all generators.")
    parser.add_argument("--examples", action="store_true",
                        help="Also regenerate hash-suffixed SVGs from examples.yml.")
    args = parser.parse_args()

    if args.examples and not args.all and not args.generators:
        regen_examples()
        return

    if args.all:
        names = sorted({v.__name__ for v in boxes.generators.getAllBoxGenerators().values()})
    elif args.generators:
        names = args.generators
    else:
        names = interactive_select()

    ok = skipped = failed = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(regen, name): name for name in names}
        for future in as_completed(futures):
            name = futures[future]
            try:
                if future.result():
                    ok += 1
                else:
                    skipped += 1
            except Exception as exc:
                print(f"  ERROR {name}: {exc}", flush=True)
                failed += 1

    if len(names) > 1:
        print(f"\nDone: {ok} regenerated, {skipped} skipped, {failed} failed.")

    if args.examples:
        regen_examples()


if __name__ == "__main__":
    main()
