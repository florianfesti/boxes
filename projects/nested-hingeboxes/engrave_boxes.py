#!/usr/bin/env python3
"""Add the engraved text (engraving.py) to the box SVGs from the HingeBox generator.

usage: engrave_boxes.py BOX1.svg BOX2.svg BOX3.svg BOX4.svg     (edits them in place)

The n-th file gets the n-th box's text: on its front wall and on one of its two
x by y panels, which becomes the bottom.  If the box has lid artwork
(engraving.LID_ART), it goes on the other x by y panel, which becomes the lid
top.  Everything is filled outlines in boxes.py's etching colour (green), inside
the piece's group, so it moves with the piece when the sheets are packed.

The pieces are symmetric (checked here), so either face can go outside: the
engraved face is the outside.  On the front wall the top of the text faces the
open top edge.  On the bottom and the lid top it faces whichever long edge
becomes the front (bottom) or the back (lid top).

Running it again replaces the text it added before.
"""
import sys
import xml.etree.ElementTree as ET

from shapely import affinity
from shapely.geometry import Polygon
from svgpathtools import parse_path

import engraving

T = 3.0       # --thickness in generate.sh
BURN = 0.1    # boxes.py's default kerf allowance, which generate.sh keeps
BLACK, BLUE = "rgb(0,0,0)", "rgb(0,0,255)"
GREEN = "rgb(0,255,0)"   # boxes.py Color.ETCHING
SVG_NS = "http://www.w3.org/2000/svg"
NAMESPACES = {"": SVG_NS, "cc": "http://creativecommons.org/ns#", "dc": "http://purl.org/dc/elements/1.1/",
              "inkscape": "http://www.inkscape.org/namespaces/inkscape",
              "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
              "xlink": "http://www.w3.org/1999/xlink"}   # SVG as the default namespace, no svg: prefix
for prefix, uri in NAMESPACES.items():
    ET.register_namespace(prefix, uri)


def outline(d):
    pts = []
    for seg in parse_path(d):
        n = 1 if seg.__class__.__name__ == "Line" else 8
        pts += [seg.point(i / n) for i in range(n)]
    return Polygon([(z.real, z.imag) for z in pts]).buffer(0)


def symmetric(poly, axis):
    """True if the piece looks the same mirrored about its vertical ("x") or
    horizontal ("y") centre line."""
    x0, y0, x1, y1 = poly.bounds
    m = affinity.scale(poly, -1 if axis == "x" else 1, -1 if axis == "y" else 1,
                       origin=((x0 + x1) / 2, (y0 + y1) / 2))
    return poly.symmetric_difference(m).area < 0.01 * poly.length


def pieces(root):
    """Single-outline groups without holes: (group, outline polygon)."""
    out = []
    for g in root:
        if not isinstance(g.tag, str) or not g.tag.endswith("g"):   # skip comments
            continue
        paths = [c for c in g if c.tag.endswith("path") and c.get("class") != "engraving"]
        if len(paths) == 1 and paths[0].get("stroke") == BLACK:
            out.append((g, outline(paths[0].get("d"))))
    return out


def engrave(path):
    tree = ET.parse(path, ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
    root = tree.getroot()
    for g in root:
        for c in [c for c in g if c.get("class") == "engraving"]:
            g.remove(c)

    # The front wall comes first in the file and matches the back wall (the
    # group with eight t x t holes).  The bottom is the first of the two x by y
    # panels: the tallest pieces as wide as the front.
    back = next(g for g in root if sum(c.get("stroke") == BLUE for c in g) == 8)
    bb = outline(next(c for c in back if c.get("stroke") == BLACK).get("d")).bounds
    size = lambda b: (round(b[2] - b[0], 2), round(b[3] - b[1], 2))   # noqa: E731
    cands = pieces(root)
    front = next((g, p) for g, p in cands if size(p.bounds) == size(bb))
    wide = [(g, p) for g, p in cands if size(p.bounds)[0] == size(bb)[0]]
    tallest = max(size(p.bounds)[1] for _, p in wide)
    panels = [(g, p) for g, p in wide if size(p.bounds)[1] == tallest]
    assert len(panels) == 2, f"{path}: expected two x by y panels, found {len(panels)}"
    bottom, lid = panels

    # Inner face areas: the front's F edges add t left, right and below, the
    # bottom's f edges t all round; the outline is BURN larger on every side.
    x0, y0, x1, y1 = front[1].bounds
    front_face = (x0 + BURN + T, y0 + BURN, x1 - x0 - 2 * BURN - 2 * T, y1 - y0 - 2 * BURN - T)
    x0, y0, x1, y1 = bottom[1].bounds
    bottom_face = (x0 + BURN + T, y0 + BURN + T, x1 - x0 - 2 * BURN - 2 * T, y1 - y0 - 2 * BURN - 2 * T)
    x0, y0, x1, y1 = lid[1].bounds
    lid_face = (x0 + BURN + T, y0 + BURN + T, x1 - x0 - 2 * BURN - 2 * T, y1 - y0 - 2 * BURN - 2 * T)
    assert symmetric(front[1], "x"), f"{path}: front wall not left-right symmetric"
    for name, (_, poly) in (("bottom", bottom), ("lid top", lid)):
        assert symmetric(poly, "x") and symmetric(poly, "y"), f"{path}: {name} not symmetric"
    return tree, (front[0], front_face), (bottom[0], bottom_face), (lid[0], lid_face)


def main(files):
    jobs = [engrave(f) for f in files]
    text = engraving.box_text(*([j[k][1] for j in jobs] for k in (1, 2, 3)))
    for f, (tree, front, bottom, lid), t in zip(files, jobs, text):
        # coordinates written out in full (no transform): SvgMerge's bounding
        # boxes, which pack_sheets.py uses, ignore transforms.  The artwork is
        # one path per shape (see engraving.art).
        for (g, _), key in ((front, "front"), (bottom, "bottom"), (lid, "lid")):
            if key not in t:
                continue
            ds = t[key]["d"]
            for d in [ds] if isinstance(ds, str) else ds:
                ET.SubElement(g, f"{{{SVG_NS}}}path", {
                    "class": "engraving", "d": d, "stroke": GREEN, "fill": GREEN,
                    "stroke-width": "0.01"})
        tree.write(f, encoding="utf-8", xml_declaration=True)
        msg = (f"{f}: front “{' '.join(t['front']['lines'])}” {t['front']['size']:.2f} mm, "
               f"bottom “{' '.join(t['bottom']['lines'])}” {t['bottom']['size']:.2f} mm")
        if "lid" in t:
            x0, y0, x1, y1 = t["lid"]["ink"]
            msg += f", lid {t['lid']['art']} {x1 - x0:.1f} × {y1 - y0:.1f} mm"
        print(msg)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(sys.argv[1:])
