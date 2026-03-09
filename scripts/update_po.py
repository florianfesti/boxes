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
"""Merge po/boxes.py.pot into every .po and recompile the .mo files.

Usage (from repo root):
    python scripts/update_po.py

Run this after boxes2pot has regenerated po/boxes.py.pot.
Requires: babel  (pip install babel)
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

try:
    from babel.messages.catalog import Message
    from babel.messages.mofile import write_mo
    from babel.messages.pofile import read_po, write_po
except ImportError:
    print("ERROR: babel is required.  Run: pip install babel", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).parent.parent
POT_FILE  = REPO_ROOT / "po" / "boxes.py.pot"
PO_DIR    = REPO_ROOT / "po"
LOCALE_DIR = REPO_ROOT / "locale"
LANGUAGES  = ("de", "en", "fr", "zh_CN")


def parse_pot_msgids(pot_path: Path) -> list[tuple[str, list[str], list[tuple[str, int]]]]:
    """Parse a .pot file and return (msgid, auto_comments, locations) for each entry.

    We avoid using Babel's read_po on the .pot directly because boxes2pot
    leaves the header dates as placeholder strings that Babel cannot parse.
    """
    entries: list[tuple[str, list[str], list[tuple[str, int]]]] = []
    text = pot_path.read_text(encoding="utf-8")
    blocks = re.split(r"\n\n+", text.strip())

    for block in blocks:
        lines = block.strip().splitlines()
        auto_comments: list[str] = []
        locations: list[tuple[str, int]] = []
        msgid_parts: list[str] = []
        in_msgid = False

        for line in lines:
            if line.startswith("#. "):
                auto_comments.append(line[3:])
            elif line.startswith("#: "):
                locations.append((line[3:], 0))
            elif line.startswith('msgid '):
                in_msgid = True
                val = line[6:].strip().strip('"')
                if val:
                    msgid_parts.append(val)
            elif line.startswith("msgstr"):
                in_msgid = False
            elif in_msgid and line.startswith('"'):
                msgid_parts.append(line.strip().strip('"'))

        # Unescape literal \n sequences written by boxes2pot
        msgid = "".join(msgid_parts).replace("\\n", "\n")
        if msgid:
            entries.append((msgid, auto_comments, locations))

    return entries


def fix_po_header_dates(content: str) -> str:
    """Replace unfilled placeholder dates so Babel can parse the header."""
    # Pattern 1: literal placeholder text
    content = re.sub(
        r"(PO-Revision-Date: )YEAR-MO-DA HO:MI\+ZONE",
        r"\g<1>2019-01-01 00:00+0000",
        content,
    )
    content = re.sub(
        r"(POT-Creation-Date: )YEAR-MO-DA HO:MI\+ZONE",
        r"\g<1>2019-01-01 00:00+0000",
        content,
    )
    # Pattern 2: empty value  (e.g. zh_CN has  "PO-Revision-Date: \n")
    content = re.sub(
        r"(PO-Revision-Date: )\\n",
        r"\g<1>2019-01-01 00:00+0000\\n",
        content,
    )
    content = re.sub(
        r"(POT-Creation-Date: )\\n",
        r"\g<1>2019-01-01 00:00+0000\\n",
        content,
    )
    return content


def main() -> None:
    if not POT_FILE.exists():
        print(f"ERROR: {POT_FILE} not found.  Run scripts/boxes2pot first.", file=sys.stderr)
        sys.exit(1)

    pot_entries = parse_pot_msgids(POT_FILE)
    print(f"Parsed {len(pot_entries)} msgids from {POT_FILE.name}")

    for lang in LANGUAGES:
        po_path = PO_DIR / f"{lang}.po"
        if not po_path.exists():
            print(f"  {lang}: .po not found, skipping")
            continue

        content = fix_po_header_dates(po_path.read_text(encoding="utf-8"))
        catalog = read_po(io.BytesIO(content.encode("utf-8")), locale=lang)

        existing_ids: set[str | tuple[str, str]] = set(catalog._messages.keys())
        added = 0
        for msgid, auto_comments, locations in pot_entries:
            if msgid not in existing_ids:
                catalog[msgid] = Message(
                    msgid,
                    string="",
                    locations=locations,
                    auto_comments=auto_comments,
                )
                added += 1

        with po_path.open("wb") as f:
            write_po(f, catalog)

        mo_path = LOCALE_DIR / lang / "LC_MESSAGES" / "boxes.py.mo"
        mo_path.parent.mkdir(parents=True, exist_ok=True)
        with mo_path.open("wb") as f:
            write_mo(f, catalog)

        translated = sum(1 for m in catalog if m.id and m.string)
        total      = sum(1 for m in catalog if m.id)
        print(f"  {lang}: +{added} new strings  |  {translated}/{total} translated  |  .mo written")


if __name__ == "__main__":
    main()
