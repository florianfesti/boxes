"""Generate sample JPG images for generators that have a reference SVG.

Usage:
    python scripts/gen_sample_images.py [GeneratorName ...]

If no names are given, regenerates all SVGs found in examples/ that have
a matching entry in static/samples/.

The output JPG is 1200 px wide (project convention) with a white background.
Thumbnails are NOT regenerated here – run scripts/gen_thumbnails.sh for that.
"""

from __future__ import annotations

import io
import pathlib
import sys

from PIL import Image
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

EXAMPLES_DIR = pathlib.Path(__file__).parent.parent / "examples"
SAMPLES_DIR = pathlib.Path(__file__).parent.parent / "static" / "samples"
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

    if names:
        targets = [EXAMPLES_DIR / f"{n}.svg" for n in names]
    else:
        # Only update JPGs that already exist in static/samples/
        targets = [
            svg
            for svg in EXAMPLES_DIR.glob("*.svg")
            if (SAMPLES_DIR / svg.with_suffix(".jpg").name).exists()
        ]

    for svg_path in sorted(targets):
        if not svg_path.exists():
            print(f"SKIP  {svg_path} (not found)")
            continue
        jpg_path = SAMPLES_DIR / svg_path.with_suffix(".jpg").name
        try:
            svg_to_jpg(svg_path, jpg_path)
            make_thumbnail(jpg_path)
        except Exception as exc:
            print(f"ERROR {svg_path}: {exc}")


if __name__ == "__main__":
    main()
