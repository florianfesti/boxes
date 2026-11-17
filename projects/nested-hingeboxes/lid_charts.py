#!/usr/bin/env python3
"""Line art for the lid top of box 3 ("Problematic Data"): three charts, each
broken in its own way.

usage: lid_charts.py [OUT.svg [PREVIEW.png]]
       (default art/broken-charts.svg and previews/lid-box3.png)

The SVG is the lid top's inner face, 170 x 104 mm (box 3's x by y panel less
t all round), with the art as filled outlines in boxes.py's etching colour
(green).  A red rectangle marks the face's edge; it is unfilled, so
engraving.lid_art leaves it out.  engraving.LID_ART puts the art on box 3's
lid, where it is scaled to leave LID_PAD clear: drawn just inside that, so
it goes on at very nearly full size.

The charts, left to right: a line that loops and runs off its axes; bars that
lean, bend and wobble; a column of points and one outlier, whose fit line
follows the outlier alone.
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw
from shapely import affinity
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.ops import substring, unary_union

import engraving

W, H = 170.0, 104.0        # mm, inner face of box 3's lid top (176 x 110 less 2t)
U, UY = 1.5, 0.95          # mm per chart unit across and up: each chart's axes are 30 x 34 units
GAP = 8.4                  # mm between one chart's axes and the next
TICK = 1.5                 # mm, length of the axis ticks
AXIS = 0.7                 # mm, line widths
DATA = 0.8
THIN = 0.6
DOT = 1.3                  # mm, radius of the scatter points
GREEN, RED = "rgb(0,255,0)", "rgb(255,0,0)"


# Charts are drawn in chart units with y up, the axes' corner at (0, 0).
# Positions scale by U and UY; line widths and dot sizes are in mm and don't.
def mm(pts):
    return [(U * x, UY * y) for x, y in pts]


def stroke(pts, w=DATA):
    return LineString(mm(pts)).buffer(w / 2, quad_segs=8, cap_style="round", join_style="round")


def dot(x, y, r=DOT):
    return Point(U * x, UY * y).buffer(r, quad_segs=8)


def smooth(pts, n=4):
    """Chaikin corner cutting, keeping the end points."""
    for _ in range(n):
        out = [pts[0]]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            out += [(0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1), (0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1)]
        pts = out + [pts[-1]]
    return pts


def dashes(pts, dash=2.4, gap=1.4, w=DATA):
    """A dashed stroke, dash and gap in mm along the line, square-ended."""
    line = LineString(mm(pts))
    return [substring(line, a, min(a + dash, line.length)).buffer(w / 2, quad_segs=8, cap_style="flat")
            for a in [i * (dash + gap) for i in range(int(line.length // (dash + gap)) + 1)] if a < line.length]


def axes(w=30, h=34, ticks=4):
    parts = [stroke([(0, h), (0, 0), (w, 0)], AXIS)]
    parts += [stroke([(0, k * h / (ticks + 0.5)), (-TICK / U, k * h / (ticks + 0.5))], THIN) for k in range(1, ticks + 1)]
    parts += [stroke([(k * w / (ticks + 0.5), 0), (k * w / (ticks + 0.5), -TICK / UY)], THIN) for k in range(1, ticks + 1)]
    return parts


def runaway_line():
    """A line that starts out well enough, loops, and leaves the chart."""
    pts = mm(smooth([(1, 5), (5, 9), (9, 7), (13, 12), (17, 10), (20.5, 14.5), (24, 18), (27, 20.5), (28, 25),
                     (24.5, 27.5), (21.5, 24), (24.5, 19.8), (28, 23.5), (29, 29), (29, 35)]))
    (xa, ya), (xb, yb) = pts[-2], pts[-1]
    a = math.atan2(yb - ya, xb - xa)
    tip = (xb + 2.2 * math.cos(a), yb + 2.2 * math.sin(a))
    head = Polygon([tip] + [(xb + 1.7 * math.cos(a + s * math.pi / 2), yb + 1.7 * math.sin(a + s * math.pi / 2))
                            for s in (1, -1)])
    line = LineString(pts).buffer(DATA / 2, quad_segs=8, cap_style="round", join_style="round")
    return axes() + [line, head]


def crooked_bars():
    """Bars that lean, bend and wobble."""
    bars = [[(6, -3), (5.3, 8), (3.6, 16)],                        # leans left
            [(11, -3), (11.3, 9), (13.2, 17), (17, 24)],           # bends right
            [(20.5, -3), (21.8, 5), (19.8, 11), (21.6, 18)],       # wobbles
            [(26.5, -3), (27.6, 12), (29.6, 29)]]                  # leans right
    parts = [LineString(mm(smooth(b, 3))).buffer(1.8 * U, quad_segs=8, cap_style="flat", join_style="round")
             .intersection(box(0, 0, 40 * U, 40 * UY)) for b in bars]
    return axes() + parts


def lone_outlier():
    """Anscombe's fourth dataset: every point but one shares the same x, and that
    one point alone sets the slope of a confident fit line."""
    col, ys = 12, [5, 8.5, 11.5, 15, 18.3, 21.5, 25]
    out = (28, 31)
    my = sum(ys) / len(ys)
    slope = (out[1] - my) / (out[0] - col)                     # least squares: through the column's mean and the outlier
    fit = [(x, my + slope * (x - col)) for x in (0.8, 30)]
    return axes() + [dot(col, y) for y in ys] + [dot(*out)] + dashes(fit)


CHARTS = [runaway_line, crooked_bars, lone_outlier]


def art():
    """The charts side by side as one shape, in mm on the face, y down: axes
    on one baseline, GAP apart, centred on the face by ink."""
    g = unary_union([affinity.translate(unary_union(chart()), i * (30 * U + GAP), 0)
                     for i, chart in enumerate(CHARTS)])
    g = affinity.scale(g, 1, -1, origin=(0, 0)).simplify(0.02)   # well under the laser's resolution
    x0, y0, x1, y1 = g.bounds
    g = affinity.translate(g, (W - x0 - x1) / 2, (H - y0 - y1) / 2)
    x0, y0, x1, y1 = g.bounds
    assert x0 >= 5 and y0 >= 5 and x1 <= W - 5 and y1 <= H - 5, f"art runs off the face: {g.bounds}"
    return g


def write_svg(g, path):
    Path(path).write_text(
        f'<?xml version="1.0" encoding="utf-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:g}mm" height="{H:g}mm" viewBox="0 0 {W:g} {H:g}">\n'
        f'<title>Box 3 lid top: Problematic Data</title>\n'
        f'<rect x="0" y="0" width="{W:g}" height="{H:g}" fill="none" stroke="{RED}" stroke-width="0.2"/>\n'
        f'<path class="engraving" d="{engraving._path(g)}" fill="{GREEN}" stroke="{GREEN}" '
        f'stroke-width="0.01" fill-rule="evenodd"/>\n</svg>\n')


def write_png(g, path, px_per_mm=10):
    img = Image.new("RGB", (round(W * px_per_mm), round(H * px_per_mm)), (226, 196, 150))   # plywood
    draw = ImageDraw.Draw(img)
    s = lambda ring: [(x * px_per_mm, y * px_per_mm) for x, y in ring.coords]  # noqa: E731
    # containers first, so a shape inside another's hole isn't painted over
    for p in sorted(g.geoms if isinstance(g, MultiPolygon) else [g], key=lambda p: -p.envelope.area):
        draw.polygon(s(p.exterior), fill=(92, 58, 30))
        for hole in p.interiors:
            draw.polygon(s(hole), fill=(226, 196, 150))
    img.save(path)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "art/broken-charts.svg"
    png = sys.argv[2] if len(sys.argv) > 2 else "previews/lid-box3.png"
    g = art()
    write_svg(g, out)
    write_png(g, png)
    x0, y0, x1, y1 = g.bounds
    print(f"{out}, {png}: {len(CHARTS)} charts, ink {x1 - x0:.1f} x {y1 - y0:.1f} mm, "
          f"clear {x0:.1f} mm left/right, {y0:.1f} mm top/bottom")
