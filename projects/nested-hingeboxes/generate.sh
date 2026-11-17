#!/usr/bin/env bash
# Regenerate every file in this folder.
# Needs the boxes.py dependencies (see pyproject.toml), run from anywhere:
#   projects/nested-hingeboxes/generate.sh
# Set PYTHON to pick an interpreter (default: python3).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
PY="${PYTHON:-python3}"
cd "$HERE"
mkdir -p boxes sheets

# 1. The four boxes: outside dimensions (HingeBox's default), 3 mm material,
#    lid height 20 mm.
i=1
while read -r x y h; do
  PYTHONPATH="$ROOT" "$PY" "$ROOT/scripts/boxes" HingeBox --x "$x" --y "$y" --h "$h" \
    --lidheight 20 --thickness 3 --CabinetHinge_eyes_per_hinge 7 --reference 0 --output "boxes/box$i.svg"
  i=$((i + 1))
done <<'SIZES'
160 80 60
168 95 68
176 110 76
184 125 84
SIZES
BOXES=(boxes/box1.svg boxes/box2.svg boxes/box3.svg boxes/box4.svg)

# 1b. Engraved text on each box's front and bottom (engraving.py has the words).
"$PY" engrave_boxes.py "${BOXES[@]}"

# 2. N equal sheets, plus as many spare hinge pieces as fit (runs in parallel).
#    Sheet sizes are kept from the earlier size search (done for 5-piece hinges)
#    and grown only where the required pieces no longer fit.  Drop --sheet to
#    run the size search from scratch.  If only the engraving has changed, each
#    sheet file keeps its layout and just gets the new engraving; set REPACK=1
#    to pack from scratch anyway.
while read -r n size; do
  "$PY" pack_sheets.py --sheet "$size" ${REPACK:+--repack} "$n" "sheets/sheets$n.svg" "${BOXES[@]}" &
done <<'SHEETS'
6 278x255
8 188x285
9 256x189
10 222x197
12 188x198
SHEETS
wait

# 3. Independent check of every multi-sheet file.
"$PY" check_layout.py sheets/sheets*.svg

# 4. Colour-coded layout views (layouts/), one per cut file.
"$PY" color_layouts.py sheets/sheets*.svg

# 5. Comparison table of all layouts.
"$PY" compare.py

# 6. Interactive 3D model of the four boxes (model.html).
"$PY" make_model.py
