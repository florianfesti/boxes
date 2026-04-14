"""Generate sample JPG images for generators that have a reference SVG.

Usage:
    python scripts/gen_sample_images.py [GeneratorName ...]

If no names are given, regenerates all JPGs for generators whose SVG
(stored next to the generator source file) already has a matching entry
in static/samples/.

The output JPG is 1200 px wide (project convention) with a white background.
Thumbnails are NOT regenerated here – run scripts/gen_thumbnails.sh for that.
"""

from __future__ import annotations

import inspect
import io
import pathlib
import sys

from PIL import Image
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import boxes.generators  # noqa: E402

SAMPLES_DIR = ROOT / "static" / "samples"
TARGET_W = 1200
THUMB_W = 200


def make_thumbnail(jpg_path: pathlib.Path) -> None:
    thumb_path = jpg_path.with_name(jpg_path.stem + "-thumb.jpg")
    img = Image.open(jpg_path)
    ratio = THUMB_W / img.width
    thumb = img.resize((THUMB_W, int(img.height * ratio)), Image.LANCZOS)
    thumb.save(str(thumb_path), "JPEG", quality=85)
    print(f"Written {thumb_path}  ({thumb.width}x{thumb.height})")


def svg_to_jpg(svg_path: pathlib.Path, jpg_path: pathlib.Path) -> None:
    drawing = svg2rlg(str(svg_path))
    if drawing is None:
        raise ValueError(f"Could not parse {svg_path}")

    scale = TARGET_W / drawing.width
    drawing.width *= scale
    drawing.height *= scale
    drawing.transform = (scale, 0, 0, scale, 0, 0)

    png_bytes = renderPM.drawToString(drawing, fmt="PNG")
    img = Image.open(io.BytesIO(png_bytes)).convert("RGB")

    # White background (SVG is transparent)
    bg = Image.new("RGB", img.size, (255, 255, 255))
    bg.paste(img)

    jpg_path.parent.mkdir(parents=True, exist_ok=True)
    bg.save(str(jpg_path), "JPEG", quality=90)
    print(f"Written {jpg_path}  ({img.width}x{img.height})")


def main() -> None:
    names: list[str] = sys.argv[1:]

    all_gens = boxes.generators.getAllBoxGenerators()
    by_class_name = {v.__name__: v for v in all_gens.values()}

    # Build list of (class_name, svg_path) pairs to process
    targets: list[tuple[str, pathlib.Path]] = []

    if names:
        for n in names:
            cls = by_class_name.get(n)
            if cls is None:
                print(f"SKIP  {n} (unknown generator)")
                continue
            svg = pathlib.Path(inspect.getfile(cls)).with_suffix('.svg')
            targets.append((cls.__name__, svg))
    else:
        # Only update JPGs that already exist in static/samples/
        seen: set[str] = set()
        for cls in all_gens.values():
            if cls.__name__ in seen:
                continue
            seen.add(cls.__name__)
            svg = pathlib.Path(inspect.getfile(cls)).with_suffix('.svg')
            jpg = SAMPLES_DIR / f"{cls.__name__}.jpg"
            if svg.exists() and jpg.exists():
                targets.append((cls.__name__, svg))

    for class_name, svg_path in sorted(targets):
        if not svg_path.exists():
            print(f"SKIP  {svg_path} (not found)")
            continue
        jpg_path = SAMPLES_DIR / f"{class_name}.jpg"
        try:
            svg_to_jpg(svg_path, jpg_path)
            make_thumbnail(jpg_path)
        except Exception as exc:
            print(f"ERROR {svg_path}: {exc}")


if __name__ == "__main__":
    main()
