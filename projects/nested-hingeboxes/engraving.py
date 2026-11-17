"""What is engraved on the boxes: the text (words, sizes, outlines), the line-art
Christmas tree and menorah either side of the bottom text, and the lid artwork.

Shared by engrave_boxes.py (the cut files) and make_model.py (the 3D model), so
both show exactly the same outlines.  The text is set in Special Elite
(fonts/SpecialElite-Regular.ttf, Apache License 2.0) and turned into paths, so
the laser software doesn't need the font.  The artwork comes from an SVG in art/,
scaled to fit the lid top.

Coordinates are mm on the face that carries the engraving, origin at the top-left
corner of the face's inner area, x to the right, y down (as in SVG).  The inner
area of the front wall is x by h, of the bottom and the lid top x by y.
"""
import math
import xml.etree.ElementTree as ET
from functools import cache
from pathlib import Path

import numpy as np
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from shapely import affinity
from shapely.geometry import LineString, MultiPolygon, Point, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from svgpathtools import CubicBezier, Line, parse_path
from svgpathtools.parser import parse_transform
from svgpathtools.path import transform

HERE = Path(__file__).resolve().parent
SVG_NS = "http://www.w3.org/2000/svg"
FONT = HERE / "fonts" / "SpecialElite-Regular.ttf"

# Text on the front of each box and under its bottom, one tuple of lines per box.
FRONT_TEXT = [("Scientific", "Discoveries"), ("Feline", "Facts"), ("Problematic", "Data"),
              ("Exuberant", "Ideas")]
BOTTOM_TEXT = [(name, "Chrismukkah 2026")
               for name in ("Ember Barber", "Leah Barber", "Rina Foygel Barber", "Mathew Barber")]

PAD = 12.0          # mm clear around the front text on the box with the lowest front
LEADING = 1.2       # line pitch, in font sizes
BOTTOM_SIZE = 6.0   # mm, font size of the bottom text
ART_H = 24.0        # mm, height of the menorah beside the bottom text (the tree is drawn to the same scale)
ART_LINE = 0.7      # mm, line width of the tree and menorah outlines
CANDLE_LINE = 0.55  # mm, line width of the candles

# Artwork on the lid top, one SVG (or None) per box.  Only its filled shapes are
# engraved: unfilled paths, such as a stock file's corner marks, are left out,
# and white shapes are bare wood, cut out of whatever is painted below them.
LID_ART = [HERE / "art" / "AdobeStock_2095995062.svg", HERE / "art" / "AdobeStock_939770434.svg",
           HERE / "art" / "broken-charts.svg", None]   # box 3's is drawn by lid_charts.py
LID_PAD = 8.0       # mm clear around the lid artwork
LID_TOLERANCE = 0.02  # mm, how far flattened curves may stray, for art with white shapes
WHITE = ("#ffffff", "#fff", "white")


@cache
def _font():
    f = TTFont(FONT)
    return f, f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm, _kerning(f)


def _kerning(f):
    """Pair kerning (x advance adjustments, font units) from the GPOS kern lookups."""
    kern = {}
    gpos = f["GPOS"].table
    for li in {i for fr in gpos.FeatureList.FeatureRecord if fr.FeatureTag == "kern"
               for i in fr.Feature.LookupListIndex}:
        for st in gpos.LookupList.Lookup[li].SubTable:
            if st.Format == 1:
                for first, ps in zip(st.Coverage.glyphs, st.PairSet):
                    for pv in ps.PairValueRecord:
                        v = getattr(pv.Value1, "XAdvance", 0) or 0
                        kern.setdefault((first, pv.SecondGlyph), v)
            else:
                c1, c2 = st.ClassDef1.classDefs, st.ClassDef2.classDefs
                for first in st.Coverage.glyphs:
                    rec = st.Class1Record[c1.get(first, 0)]
                    for second in f.getGlyphOrder():
                        v = getattr(rec.Class2Record[c2.get(second, 0)].Value1, "XAdvance", 0) or 0
                        if v:
                            kern.setdefault((first, second), v)
    return kern


def _line(text):
    """Glyph names and their x positions (font units) for one line."""
    f, _, cmap, _, kern = _font()
    hmtx = f["hmtx"]
    x, out, prev = 0, [], None
    for ch in text:
        g = cmap[ord(ch)]
        if prev:
            x += kern.get((prev, g), 0)
        out.append((g, x))
        x += hmtx[g][0]
        prev = g
    return out


@cache
def _glyph_bounds(g):
    _, gs, _, _, _ = _font()
    pen = BoundsPen(gs)
    gs[g].draw(pen)
    return pen.bounds  # None for a space


def _ink(lines, size):
    """Ink box of the lines at `size` mm: each line centred on x = 0 by its ink,
    baseline of line k at y = k * LEADING * size (y down).  Returns the box and
    each line's x offset."""
    _, _, _, upem, _ = _font()
    s = size / upem
    x0 = y0 = float("inf")
    x1 = y1 = float("-inf")
    offsets = []
    for k, text in enumerate(lines):
        bs = [(px + b[0], b[1], px + b[2], b[3]) for g, px in _line(text)
              if (b := _glyph_bounds(g))]
        lx0, lx1 = min(b[0] for b in bs) * s, max(b[2] for b in bs) * s
        dx = -(lx0 + lx1) / 2
        offsets.append(dx)
        base = k * LEADING * size
        x0, x1 = min(x0, lx0 + dx), max(x1, lx1 + dx)
        y0 = min(y0, base - max(b[3] for b in bs) * s)
        y1 = max(y1, base - min(b[1] for b in bs) * s)
    return (x0, y0, x1, y1), offsets


def fit(lines, w, h, pad=PAD):
    """Largest font size (mm) at which the lines fit a w x h face with `pad` all round."""
    (x0, y0, x1, y1), _ = _ink(lines, 1.0)
    return min((w - 2 * pad) / (x1 - x0), (h - 2 * pad) / (y1 - y0))


def front_sizes(faces):
    """Font sizes for the fronts, faces = [(lines, w, h), ...]: the lowest front gets
    the largest size that fits it; the others scale up from it with their front's
    height, never past their own fit."""
    ref = min(faces, key=lambda f: f[2])
    s = fit(*ref)
    return [min(s * h / ref[2], fit(lines, w, h)) for lines, w, h in faces]


def outlines(lines, size, w, h, at=(0.0, 0.0)):
    """SVG path data of the lines at `size` mm, centred on a w x h face (by ink)
    whose top-left corner is at `at`, plus the ink box."""
    _, gs, _, upem, _ = _font()
    s = size / upem
    (x0, y0, x1, y1), offsets = _ink(lines, size)
    ox, oy = at[0] + w / 2 - (x0 + x1) / 2, at[1] + h / 2 - (y0 + y1) / 2
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    for k, text in enumerate(lines):
        base = oy + k * LEADING * size
        for g, px in _line(text):
            gs[g].draw(TransformPen(pen, (s, 0, 0, -s, ox + offsets[k] + px * s, base)))
    return pen.getCommands(), (x0 + ox, y0 + oy, x1 + ox, y1 + oy)


# The tree and menorah, drawn in art units (y down) as polylines stroked at a
# width in mm, and filled shapes.  Both use the same scale, set by the menorah.
def _quad(p0, p1, p2, n=8):
    """Points along a quadratic Bezier, without its end point."""
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            for t in (i / n for i in range(n))]


def _flame(x, y):
    """Teardrop flame standing on (x, y), 2.8 wide and 4 tall."""
    return _quad((x, y), (x - 1.4, y - 1.6), (x, y - 4)) + _quad((x, y - 4), (x + 1.4, y - 1.6), (x, y))


def _star(cx, cy, r, ri):
    return [(cx + (r if k % 2 == 0 else ri) * math.sin(k * math.pi / 5),
             cy - (r if k % 2 == 0 else ri) * math.cos(k * math.pi / 5)) for k in range(10)]


TREE_OUTLINE = [(15, 7.5), (8, 15), (11, 15), (5, 24), (9, 24), (2, 34), (28, 34), (21, 24), (25, 24),
                (19, 15), (22, 15), (15, 7.5)]
TREE = {
    "lines": [(TREE_OUTLINE, ART_LINE), ([(13, 34), (13, 40), (17, 40), (17, 34)], ART_LINE)],
    "fills": [_star(15, 3.2, 3.2, 1.3)] + [Point(x, y).buffer(1.1, quad_segs=4).exterior.coords
                                            for x, y in ((12, 20), (19, 28), (17, 14), (9, 30), (23, 31))],
}
_ARMS = [[(20 - d * math.cos(math.pi * i / 24), 16 + d * math.sin(math.pi * i / 24)) for i in range(25)]
         for d in (4, 8, 12, 16)]
MENORAH = {   # nine branches; the shamash in the middle stands higher
    "lines": [(a, ART_LINE) for a in _ARMS]
    + [([(20, 10), (20, 35)], ART_LINE), ([(12, 40), (28, 40), (25, 35), (15, 35), (12, 40)], ART_LINE)]
    + [([(x, 16), (x, 11)], CANDLE_LINE) for x in range(4, 37, 4) if x != 20]
    + [([(20, 10), (20, 5)], CANDLE_LINE)],
    "fills": [_flame(x, 9.5) for x in range(4, 37, 4) if x != 20] + [_flame(20, 3.5)],
}


@cache
def _art():
    """The tree and the menorah, each as one shapely shape in mm centred on (0, 0) by its ink."""
    s = ART_H / (40 - -0.5)   # the menorah's height in art units, flame tip to base
    out = []
    for art in (TREE, MENORAH):
        parts = [affinity.scale(Polygon(p), s, s, origin=(0, 0)) for p in art["fills"]]
        parts += [affinity.scale(LineString(p), s, s, origin=(0, 0)).buffer(w / 2, quad_segs=8)
                  for p, w in art["lines"]]
        g = unary_union(parts)
        x0, y0, x1, y1 = g.bounds
        out.append(affinity.translate(g, -(x0 + x1) / 2, -(y0 + y1) / 2))
    return out


def _num(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def _path(g):
    """SVG path data of a shapely (multi)polygon, holes wound against their outline."""
    d = []
    for p in g.geoms if isinstance(g, MultiPolygon) else [g]:
        p = orient(p)
        for ring in (p.exterior, *p.interiors):
            d.append("M" + "L".join(f"{_num(x)} {_num(y)}" for x, y in ring.coords[:-1]) + "Z")
    return "".join(d)


def bottom_art(ink, face):
    """SVG path data of the tree (left) and menorah (right) beside the bottom text
    whose ink box is `ink`, on the face (x, y, w, h): each centred halfway between
    the text and the face's edge, level with the text.  Also the ink box of text
    and art together."""
    fx, _, fw, _ = face
    x0, y0, x1, y1 = ink
    cy = (y0 + y1) / 2
    tree, menorah = _art()
    tree = affinity.translate(tree, (fx + x0) / 2, cy)
    menorah = affinity.translate(menorah, (x1 + fx + fw) / 2, cy)
    assert tree.bounds[2] < x0 and menorah.bounds[0] > x1, "no room beside the bottom text for the art"
    b = [g.bounds for g in (tree, menorah)] + [ink]
    return _path(tree) + _path(menorah), (min(v[0] for v in b), min(v[1] for v in b),
                                          max(v[2] for v in b), max(v[3] for v in b))


@cache
def _art_shapes(src):
    """The filled shapes of an SVG in paint order, as (svgpathtools path in its user
    units with the path's own transform applied, True if white), plus the ink box
    of the shapes that aren't white."""
    root = ET.parse(src).getroot()
    shapes = []
    for el in root.iter(f"{{{SVG_NS}}}path"):
        fill = el.get("fill", "black").lower()
        if fill == "none":
            continue
        p = parse_path(el.get("d"))
        if el.get("transform"):
            p = transform(p, parse_transform(el.get("transform")))
        shapes.append((p, fill in WHITE))
    boxes = [p.bbox() for p, white in shapes if not white]
    ink = (min(b[0] for b in boxes), min(b[2] for b in boxes),
           max(b[1] for b in boxes), max(b[3] for b in boxes))
    return shapes, ink


def _d(path):
    """SVG path data of an svgpathtools path, to 0.01 mm."""
    n = lambda z: f"{_num(z.real)} {_num(z.imag)}"  # noqa: E731
    out = []
    for sub in path.continuous_subpaths():
        out.append(f"M{n(sub.start)}")
        for seg in sub:
            if isinstance(seg, CubicBezier):
                out.append(f"C{n(seg.control1)} {n(seg.control2)} {n(seg.end)}")
            else:   # pymupdf's SVG output has only lines and cubics
                out.append(f"L{n(seg.end)}")
        if sub.isclosed():
            out.append("Z")
    return "".join(out)


def _region(path):
    """The area a closed svgpathtools path fills, as a shapely geometry, curves
    flattened to LID_TOLERANCE (path in mm).  Subpaths overlap even-odd, which
    matches the nonzero rule for a shape whose holes don't cross its outline."""
    region = Polygon()
    for sub in path.continuous_subpaths():
        pts = [sub.start]
        for seg in sub:
            n = 1 if isinstance(seg, Line) else max(2, math.ceil(math.sqrt(seg.length() / (8 * LID_TOLERANCE)) * 2))
            pts += [seg.point(k / n) for k in range(1, n + 1)]
        if len(pts) >= 4:
            region = region.symmetric_difference(Polygon([(z.real, z.imag) for z in pts]).buffer(0))
    return region


def lid_art(src, w, h, at=(0.0, 0.0), pad=LID_PAD):
    """The filled shapes of the SVG `src`, as large as fits a w x h face with `pad`
    all round, centred on it (by ink), the face's top-left corner at `at`.
    Returns a list of path data strings and the ink box.  Without white shapes,
    one string per shape, curves kept (kept apart so that each keeps its own holes
    under the nonzero fill rule).  With white shapes, the painted area is worked
    out in paint order (dark shapes added, white ones cut out) and comes back as
    one string per piece of it, curves flattened."""
    shapes, (x0, y0, x1, y1) = _art_shapes(src)
    s = min((w - 2 * pad) / (x1 - x0), (h - 2 * pad) / (y1 - y0))
    ox = at[0] + w / 2 - s * (x0 + x1) / 2
    oy = at[1] + h / 2 - s * (y0 + y1) / 2
    fit = np.array([[s, 0, ox], [0, s, oy], [0, 0, 1]])
    ink = (x0 * s + ox, y0 * s + oy, x1 * s + ox, y1 * s + oy)
    if not any(white for _, white in shapes):
        return [_d(transform(p, fit)) for p, _ in shapes], ink
    dark = Polygon()
    for p, white in shapes:
        r = _region(transform(p, fit))
        dark = dark.difference(r) if white else dark.union(r)
    polys = getattr(dark, "geoms", [dark])
    return [_path(q) for q in polys if q.geom_type == "Polygon" and not q.is_empty], ink


def box_text(faces_front, faces_bottom, faces_lid):
    """All engravings: for each box a dict with the front and bottom outlines (the
    bottom's include the tree and menorah), and the lid artwork if it has one.
    faces_front / faces_bottom / faces_lid = [(x, y, w, h), ...] per box: where the
    face's inner area starts and its size in mm."""
    sizes = front_sizes([(t, w, h) for t, (_, _, w, h) in zip(FRONT_TEXT, faces_front)])
    out = []
    for i, ((fx, fy, fw, fh), (bx, by, bw, bh), (lx, ly, lw, lh)) in enumerate(
            zip(faces_front, faces_bottom, faces_lid)):
        fd, fink = outlines(FRONT_TEXT[i], sizes[i], fw, fh, (fx, fy))
        bd, bink = outlines(BOTTOM_TEXT[i], BOTTOM_SIZE, bw, bh, (bx, by))
        ad, bink = bottom_art(bink, (bx, by, bw, bh))
        bd += ad
        out.append({
            "front": {"lines": FRONT_TEXT[i], "size": sizes[i], "w": fw, "h": fh, "d": fd, "ink": fink},
            "bottom": {"lines": BOTTOM_TEXT[i], "size": BOTTOM_SIZE, "w": bw, "h": bh, "d": bd, "ink": bink},
        })
        if LID_ART[i]:
            ld, link = lid_art(LID_ART[i], lw, lh, (lx, ly))
            out[-1]["lid"] = {"art": LID_ART[i].name, "w": lw, "h": lh, "d": ld, "ink": link}
    return out
