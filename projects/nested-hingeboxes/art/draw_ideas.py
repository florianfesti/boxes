#!/usr/bin/env python3
"""Draw art/ideas.svg, the lid artwork for box 4 ("Exuberant Ideas").

A brain with ideas bursting out of it in a wide fan: a light bulb, gears, speech
and thought bubbles (one with a lab flask), a signal, lightning, an atom, a paper plane, stars and
confetti.  No text.

Everything is built as shapely shapes in mm on a 160 x 100 canvas (y down) and
written out as black filled outlines, one path per piece, outline anticlockwise
and holes clockwise on screen, which is what engraving.art expects.  Outlines are
drawn at an even weight; inner detail is drawn with a brush that tapers, so it
reads as inked by hand.  The brain is in true side-view proportion with its
main grooves where they are on a real brain; the smaller folds are grown from
the notches in its outline and then into whatever room is left, from a fixed
random seed, so the drawing comes out the same every run.

Run it again after changing anything here, then rerun generate.sh.
"""
import math
import random
from pathlib import Path

import numpy as np
import shapely
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
OUT = HERE / "ideas.svg"
W, H = 160.0, 100.0
BOLD = 1.2    # mm, outlines
LINE = 0.85   # mm, inner detail
FINE = 0.6    # mm, the smallest details

rng = random.Random(11)
ink = []


# --- drawing helpers ---------------------------------------------------------
def spline(pts, closed=False, n=12):
    """Catmull-Rom curve through pts."""
    ext = [pts[-1], *pts, pts[0], pts[1]] if closed else [pts[0], *pts, pts[-1]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1:i + 3]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * p1[j] + (p2[j] - p0[j]) * t
                                    + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (3 * p1[j] - p0[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    out.append(pts[0] if closed else pts[-1])
    return out


def resample(pts, step=0.3):
    ls = LineString(pts)
    n = max(1, round(ls.length / step))
    return [ls.interpolate(ls.length * k / n).coords[0] for k in range(n + 1)]


def brush(pts, w, start=0.0, end=0.0, floor=0.18):
    """A line w mm wide that narrows to a point over the first `start` and the
    last `end` fraction of its length."""
    P = resample(pts)
    n = len(P) - 1

    def r(k):
        t, f = k / n, 1.0
        if start:
            f = min(f, t / start)
        if end:
            f = min(f, (1 - t) / end)
        return max(floor, w * math.sin(math.pi / 2 * max(0.0, min(1.0, f)))) / 2

    discs = [Point(p).buffer(r(k), quad_segs=6) for k, p in enumerate(P)]
    return unary_union([discs[k].union(discs[k + 1]).convex_hull for k in range(n)])


def stroke(geom, w):
    """A line (or the outline of a shape) drawn w mm wide, round ends."""
    if isinstance(geom, (list, tuple)):
        geom = LineString(geom)
    elif geom.geom_type == "Polygon":
        geom = geom.exterior
    return geom.buffer(w / 2, quad_segs=8)


def arc(cx, cy, r, a0, a1, n=24):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


def star(cx, cy, r, points=5, inner=0.45, rot=-90.0, round_=0.25):
    pts = []
    for k in range(2 * points):
        a = math.radians(rot + 180 * k / points)
        rr = r if k % 2 == 0 else r * inner
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return Polygon(pts).buffer(-round_).buffer(round_)


def twinkle(cx, cy, r):
    """A four-pointed sparkle with curved sides."""
    pts = []
    for k in range(64):
        a = 2 * math.pi * k / 64
        c, s = math.cos(a), math.sin(a)
        rr = r / (abs(c) ** 0.5 + abs(s) ** 0.5) ** 2
        pts.append((cx + rr * c, cy + rr * s))
    return Polygon(pts)


def dot(cx, cy, r):
    return Point(cx, cy).buffer(r, quad_segs=16)


def ellipse(cx, cy, rx, ry, rot=0.0):
    e = affinity.scale(Point(0, 0).buffer(1, quad_segs=32), rx, ry, origin=(0, 0))
    return affinity.translate(affinity.rotate(e, rot, origin=(0, 0)), cx, cy)


def place(geoms, at, rot=0.0):
    return [affinity.translate(affinity.rotate(g, rot, origin=(0, 0)), *at) for g in geoms]


# --- the brain -----------------------------------------------------------------
# A left side view in true proportion, drawn in a 100-unit frame (frontal pole at
# u = 0, occipital pole at u = 100, top at v = 0) and mapped onto the canvas.
# The cerebrum is long and low, highest just behind the middle, with a blunt
# frontal lobe, a narrower occipital lobe and, below the lateral fissure, the
# temporal lobe, whose tip sits in a notch under the frontal lobe.  The
# cerebellum tucks in under the back and the stem comes down between the two.
BRAIN_AT, BRAIN_SCALE = (45.0, 40.5), 0.7


def U(pts):
    return [(BRAIN_AT[0] + BRAIN_SCALE * u, BRAIN_AT[1] + BRAIN_SCALE * v) for u, v in pts]


BASE = U([(0, 36), (2, 24), (8, 13), (17, 5), (29, 1), (42, 0), (55, 0.5), (67, 3), (78, 8),
          (88, 15), (95, 24), (99, 33), (100, 41), (97, 47), (90, 51), (82, 54), (74, 58),
          (64, 61), (52, 62), (42, 61.5), (33, 58.5), (28.5, 54.5), (27, 50), (28.5, 46.5),
          (22, 45), (12, 44.5), (4, 41.5)])


def lobed(base, spacing=6.2):
    """The base outline bulged out a little between notches about `spacing` mm
    apart, like the rounded ends of the folds showing at the edge of a brain.
    The underside stays smoother.  Returns the outline and, for each notch, the
    point and the inward direction there."""
    loop = LineString(spline(base, closed=True, n=30))
    poly = Polygon(loop.coords)
    L = loop.length
    cuts, s = [], 0.0
    while s < L - spacing * 0.7:
        cuts.append(s)
        s += spacing * rng.uniform(0.75, 1.25)
    cuts.append(L)

    def normal(s):
        x, y = loop.interpolate(s % L).coords[0]
        x2, y2 = loop.interpolate((s + 0.2) % L).coords[0]
        nx, ny = -(y2 - y), x2 - x
        d = math.hypot(nx, ny)
        nx, ny = nx / d, ny / d
        if poly.contains(Point(x + nx * 0.3, y + ny * 0.3)):
            nx, ny = -nx, -ny
        return (x, y), (nx, ny)

    out, notch_pts = [], []
    for a, b in zip(cuts, cuts[1:]):
        (_, under) = normal((a + b) / 2)[1]
        amp = min(1.25, 0.18 * (b - a)) * (0.45 if under > 0.55 else 1.0)
        steps = max(4, int((b - a) / 0.25))
        for k in range(steps):
            (x, y), (nx, ny) = normal(a + (b - a) * k / steps)
            bump = amp * math.sin(math.pi * k / steps) ** 0.75
            out.append((x + bump * nx, y + bump * ny))
            if k == 0 and ny < 0.5:
                notch_pts.append(((x, y), (-nx, -ny)))
    return Polygon(out), notch_pts


CEREBRUM, NOTCH_PTS = lobed(BASE)
CEREBELLUM = Polygon(spline(U([(68, 60), (74, 55.5), (84, 53), (93, 53.5), (99, 58), (99.5, 65),
                               (95, 71.5), (86, 75), (77, 74), (70.5, 69.5)]), closed=True))
STEM = Polygon(spline(U([(58, 58), (56.5, 64), (57, 70), (59.5, 77), (61, 82.5), (64, 84.5), (66.5, 82),
                         (67, 75), (68.5, 66), (70, 59)]), closed=True))
BRAIN = unary_union([CEREBRUM, CEREBELLUM, STEM])

ink.append(stroke(CEREBRUM, BOLD))
ink.append(stroke(CEREBELLUM.exterior.difference(CEREBRUM), BOLD))
ink.append(stroke(STEM.exterior.difference(CEREBRUM.union(CEREBELLUM)), BOLD))
# the cerebellum's fine parallel folds, following its lower edge
for k, v in enumerate((60.5, 64.5, 68.5)):
    g = U([(70 + 2 * k, v + 1.5), (78, v - 0.5), (87, v - 1), (95, v + 0.5), (100, v + 3)])
    ink.append(brush(spline(g), FINE, 0.2, 0.2).intersection(CEREBELLUM.buffer(-0.5))
               .difference(CEREBRUM.buffer(0.6)))

# The landmark grooves where they are on a real brain: the lateral fissure and
# its two short branches, the central sulcus with the sulci either side of it,
# the frontal sulci running forward, the temporal sulci running along under
# the fissure, and the intraparietal sulcus running back.
LANDMARKS = [  # (points in the 100-unit frame, width, taper at start, taper at end)
    ([(28.5, 46.5), (36, 43.5), (45, 41.2), (54, 39.5), (63, 36.5), (69, 32), (71.5, 28)], 1.15, 0.0, 0.3),
    ([(33, 44.5), (31.5, 40), (32.5, 36)], LINE, 0.0, 0.5),
    ([(36.5, 43.8), (38, 39), (36.8, 35.5)], LINE, 0.0, 0.5),
    ([(53, 0.4), (51.5, 6), (53, 10), (49.5, 16), (50.5, 21), (47, 27), (46, 33)], 1.0, 0.0, 0.3),
    ([(42, 1.5), (40.5, 8), (41.5, 13), (39, 19)], LINE, 0.0, 0.4),
    ([(38.5, 23), (36.5, 28.5), (37, 33.5)], LINE, 0.25, 0.4),
    ([(63, 2.5), (60.5, 8.5), (61.5, 14), (58, 20), (57.5, 27)], LINE, 0.0, 0.35),
    ([(39.5, 13), (32, 12.5), (25, 14.5), (17, 14), (11, 17.5)], LINE, 0.25, 0.3),
    ([(37, 24.5), (29, 24), (21, 26.5), (13, 26.5), (6, 30)], LINE, 0.25, 0.3),
    ([(33.5, 53), (41, 50.5), (50, 48.5), (59, 46.5), (67, 43), (73, 38.5), (75, 34.5)], LINE, 0.3, 0.3),
    ([(42, 57), (51, 56), (60, 54.5), (68, 52.5)], LINE, 0.3, 0.4),
    ([(58, 21), (66, 20.5), (73, 22.5), (80, 26.5), (86, 28.5)], LINE, 0.3, 0.35),
    ([(80, 34), (87, 37.5), (92.5, 42.5)], LINE, 0.3, 0.4),
]
folds = []
for pts, w, t0, t1 in LANDMARKS:
    line = spline(U(pts))
    folds.append(LineString(line))
    ink.append(brush(line, w, t0, t1).intersection(CEREBRUM.buffer(-0.2)))

OUTLINE = CEREBRUM.exterior
INSIDE = CEREBRUM.buffer(-1.7)
CLEAR = 2.4   # mm between neighbouring folds


def grow(p, heading, length, others, curl=None, free=1.2):
    """A wandering fold from p, turning a little as it goes, stopped where it
    would come within CLEAR of another fold or run out of the brain."""
    a = rng.uniform(0.12, 0.26) * rng.choice((-1, 1))
    lam = rng.uniform(7, 12)
    ph = rng.uniform(0, 2 * math.pi)
    curl = rng.choice((-1, 1)) * rng.uniform(0.35, 0.6) if curl is None else curl
    pts, s, step = [p], 0.0, 0.35
    x, y = p
    while s < length:
        k = a * math.sin(2 * math.pi * s / lam + ph)
        if s > length - 2.2:
            k += curl          # finish with a hook
        heading += k * step
        x, y = x + step * math.cos(heading), y + step * math.sin(heading)
        s += step
        q = Point(x, y)
        if s > free and (not INSIDE.contains(q) or (others is not None and others.distance(q) < CLEAR)):
            break
        pts.append((x, y))
    return pts, s


# folds running in from each notch in the outline
for (x, y), (nx, ny) in NOTCH_PTS:
    if any(Point(x, y).distance(f) < 2.4 for f in folds):
        continue
    others = unary_union(folds).difference(Point(x, y).buffer(0.5))
    h = math.atan2(ny, nx) + rng.uniform(-0.35, 0.35)
    pts, s = grow((x, y), h, rng.uniform(4, 9), others, free=2.6)
    if s >= 3.0:
        folds.append(LineString(pts))
        ink.append(brush(pts, LINE, 0.0, 0.3))

# then short curled folds wherever there is still room
gx, gy = np.meshgrid(np.arange(44, 117, 0.8), np.arange(40, 87, 0.8))
grid = shapely.points(gx.ravel(), gy.ravel())
grid = grid[shapely.contains(INSIDE.buffer(-0.8), grid)]
for _ in range(80):
    taken = unary_union(folds + [OUTLINE])
    d = shapely.distance(grid, taken)
    i = int(np.argmax(d))
    if d[i] < 3.0:
        break
    seed = grid[i].coords[0]
    h = rng.uniform(0, 2 * math.pi)
    half1, _ = grow(seed, h, rng.uniform(2.5, 5.5), taken)
    half2, _ = grow(seed, h + math.pi, rng.uniform(2.5, 5.5), taken)
    pts = half2[::-1] + half1[1:]
    line = LineString(pts) if len(pts) > 1 else None
    if line is None or line.length < 3.0:
        grid = np.delete(grid, i)
        continue
    folds.append(line)
    ink.append(brush(pts, LINE, 0.18, 0.18))


# --- the light bulb --------------------------------------------------------------
# Drawn upright around the centre of the glass, then tipped back to the upper left.
R = 12.0
glass = [(R * math.cos(math.radians(a)), R * math.sin(math.radians(a))) for a in range(40, -221, -20)]
glass = Polygon(spline(glass + [(-6.6, 13), (-5.3, 18), (5.3, 18), (6.6, 13)], closed=True))
bulb = [stroke(glass, BOLD)]
bulb.append(brush(arc(0, 0, R - 3.2, 192, 252), 1.5, 0.3, 0.3))     # shine
bulb.append(brush(arc(0, 0, R - 2.6, 20, 62), 0.7, 0.4, 0.4))       # shade on the far side
# glass stem, support wires and a coiled filament
bulb.append(brush([(-2.4, 18), (-1.2, 10.5)], FINE))
bulb.append(brush([(2.4, 18), (1.2, 10.5)], FINE))
bulb.append(brush([(-1.2, 10.5), (-3.4, 5.2)], 0.45))
bulb.append(brush([(1.2, 10.5), (3.4, 5.2)], 0.45))
coil = [(-3.4 + 6.8 * t - 0.75 * math.sin(2 * math.pi * 5 * t), 5.2 - 1.1 * math.sin(math.pi * t)
         - 1.0 * math.cos(2 * math.pi * 5 * t) + 1.0) for t in (k / 200 for k in range(201))]
bulb.append(brush(coil, 0.42))
# screw base: three threads, then the contact
for k, y in enumerate((19.6, 22.1, 24.6)):
    half = 5.6 - 0.35 * k
    bulb.append(LineString([(-half, y), (half, y + 0.5)]).buffer(0.95, quad_segs=8))
bulb.append(Polygon(spline([(-3.0, 26.2), (-2.2, 27.9), (0, 28.6), (2.2, 27.9), (3.0, 26.2)]) +
                    [(-3.0, 26.2)]).buffer(0.25))
BULB_C, BULB_TILT, BULB_SCALE = (40, 23), -16, 0.64
BULB_INK = place([affinity.scale(g, BULB_SCALE, BULB_SCALE, origin=(0, 0)) for g in bulb], BULB_C, BULB_TILT)
ink += BULB_INK
# its glow, added once everything else is placed (see below), so that a glow
# line that would touch something is left out
GLOW = []
for k, a in enumerate(range(-160, 30, 19)):
    a = math.radians(a + BULB_TILT)
    r0, r1 = (15.3, 21) if k % 2 == 0 else (15.8, 19)
    GLOW.append(brush([(BULB_C[0] + BULB_SCALE * r * math.cos(a), BULB_C[1] + BULB_SCALE * r * math.sin(a))
                       for r in (r0, r1)], 1.0, 0.0, 0.6))


# --- gears -----------------------------------------------------------------------
MOD = 1.3


def gear(c, teeth, rot, style):
    cx, cy = c
    rp = MOD * teeth / 2
    pts = []
    for i in range(teeth):
        a = math.radians(rot) + 2 * math.pi * i / teeth
        p = math.pi / teeth
        for da, r in ((-0.6, rp - 0.75 * MOD), (-0.36, rp + 0.8 * MOD), (0.36, rp + 0.8 * MOD),
                      (0.6, rp - 0.75 * MOD)):
            pts.append((cx + r * math.cos(a + da * p), cy + r * math.sin(a + da * p)))
    body = Polygon(pts).buffer(-0.3).buffer(0.3)
    if style == "holes":
        body = body.difference(dot(cx, cy, rp * 0.2))
        for i in range(5):
            a = math.radians(rot) + 2 * math.pi * (i + 0.5) / 5
            body = body.difference(dot(cx + rp * 0.55 * math.cos(a), cy + rp * 0.55 * math.sin(a), rp * 0.19))
    elif style == "ring":
        body = body.difference(dot(cx, cy, rp * 0.6)).union(stroke(Point(cx, cy).buffer(rp * 0.3), LINE))
    else:
        body = body.difference(dot(cx, cy, rp * 0.36))
    return body, rp


GA = (112, 20)
ga, ra = gear(GA, 12, 0, "holes")
ink.append(ga)
for teeth, ang, style in ((8, 52, "ring"), (6, -36, "plain")):
    rb = MOD * teeth / 2
    th = math.radians(ang)
    c = (GA[0] + (ra + rb + 0.5) * math.cos(th), GA[1] + (ra + rb + 0.5) * math.sin(th))
    # turned so that its teeth fall between A's where they meet
    ink.append(gear(c, teeth, ang + 180 + 180 / teeth + ang * 12 / teeth, style)[0])


# --- bubbles -----------------------------------------------------------------------
def speech(cx, cy, rx, ry, tail):
    body = ellipse(cx, cy, rx, ry)
    tx, ty = tail
    dx, dy = tx - cx, ty - cy
    n = math.hypot(dx, dy)
    ux, uy = dx / n, dy / n
    base = 0.42 * min(rx, ry)
    tri = Polygon([(cx + ux * 0.5 * rx - uy * base, cy + uy * 0.5 * ry + ux * base),
                   (cx + ux * 0.5 * rx + uy * base, cy + uy * 0.5 * ry - ux * base), (tx, ty)])
    return unary_union([body, tri]).buffer(0.8).buffer(-0.8)


def shine(cx, cy, rx, ry):
    """A short highlight inside the upper left of an oval."""
    pts = [(cx + 0.72 * rx * math.cos(math.radians(a)), cy + 0.66 * ry * math.sin(math.radians(a)))
           for a in range(195, 246, 3)]
    return brush(pts, 0.9, 0.35, 0.35)


def flask(cx, cy, h):
    """A conical lab flask h mm tall, half full, bubbling."""
    k = h / 8
    body = Polygon([(cx + k * x, cy + k * y) for x, y in (
        (-1.1, -4), (1.1, -4), (1.1, -1.2), (3.6, 3.2), (3.6, 4), (-3.6, 4), (-3.6, 3.2), (-1.1, -1.2))])
    body = body.buffer(-0.35 * k).buffer(0.35 * k)
    out = [stroke(body, FINE), brush([(cx - 1.7 * k, cy - 4 * k), (cx + 1.7 * k, cy - 4 * k)], 0.75)]
    liquid = body.buffer(-0.6 * k).intersection(box(cx - 5 * k, cy + 0.9 * k, cx + 5 * k, cy + 5 * k))
    for bx, by, br in ((-1.2, 2.6, 0.45), (0.9, 1.9, 0.35), (1.6, 3.1, 0.3)):
        liquid = liquid.difference(dot(cx + bx * k, cy + by * k, br * k))
    out.append(liquid)
    for bx, by, br in ((0.3, -5.3, 0.45), (-0.6, -6.6, 0.32)):
        out.append(stroke(Point(cx + bx * k, cy + by * k).buffer(br * k), 0.4))
    return out


# upper left: a speech bubble with a bubbling flask in it
ink.append(stroke(speech(17, 16, 8.5, 6, (22, 26.5)), BOLD))
ink.append(shine(17, 16, 8.5, 6))
ink += flask(17.6, 17.2, 6.6)

# upper right: a thought cloud with three dots, trailing down towards the brain
CLOUD, CS = (144, 15), 0.75
cloud = unary_union([dot(CLOUD[0] + CS * dx, CLOUD[1] + CS * dy, CS * r) for dx, dy, r in (
    (-8, 1.5, 4.8), (-3.5, -3, 5.4), (3, -3.5, 5.2), (8.2, 0.5, 4.6), (5, 5, 4.4),
    (-1.5, 5.2, 4.6), (-7, 5.5, 3.6), (0, 1, 6))])
ink.append(stroke(cloud, BOLD))
ink.append(brush(arc(CLOUD[0] - CS * 3.5, CLOUD[1] - CS * 3, CS * 3.4, 200, 260), 0.8, 0.35, 0.35))
for dx in (-3.4, 0, 3.4):
    ink.append(dot(CLOUD[0] + dx, CLOUD[1] + 1.4, 1.0))
ink.append(stroke(Point(136, 25.5).buffer(1.5), LINE))
ink.append(stroke(Point(133.5, 29.3).buffer(0.9), FINE))

# right: a speech bubble with a sparkle
SB = (143, 47)
ink.append(stroke(speech(*SB, 8, 5.8, (134, 54)), BOLD))
ink.append(shine(*SB, 8, 5.8))
ink.append(twinkle(SB[0] + 0.4, SB[1] + 0.2, 4.0))
ink.append(twinkle(SB[0] + 4.3, SB[1] - 2.8, 1.6))

# left: a signal, beaming up and out
SIG = (14, 50)
ink.append(dot(*SIG, 1.4))
for r in (3.6, 6.0, 8.4):
    ink.append(brush(arc(*SIG, r, -92, -8, 20), 1.15, 0.12, 0.12, floor=0.55))

# lightning
BOLT = [(0.3, 0), (1, 0), (0.62, 0.4), (0.95, 0.4), (0.08, 1.22), (0.38, 0.58), (0.02, 0.58)]


def bolt(at, w, h, rot):
    return place([Polygon([(x * w, y * h) for x, y in BOLT]).buffer(-0.15).buffer(0.15)], at, rot)[0]


ink.append(bolt((57, 20), 5.4, 7.6, 16))
ink.append(bolt((123, 55), 4.8, 6.6, -18))

# lower left: an atom
ATOM = (24, 82)
for a in (0, 60, 120):
    ink.append(stroke(ellipse(*ATOM, 7.6, 2.8, a), LINE))
ink.append(dot(*ATOM, 1.4))
ink.append(dot(ATOM[0] + 7.6, ATOM[1], 0.75))

# lower right: a paper plane taking off, its trail dashed behind it
T, W1, N, W2 = [(137 + 0.75 * (x - 137), 81 + 0.75 * (y - 81))
                for x, y in ((148, 70), (124, 80.5), (132, 83.5), (135, 92.5))]
ink.append(stroke(Polygon([T, W1, N, W2]), BOLD))
ink.append(Polygon([N, T, (137 + 0.75 * (133.6 - 137), 81 + 0.75 * (87.6 - 81))]).buffer(0.25))          # the shaded keel
trail = LineString(spline([(125.5, 83.5), (121.5, 86), (119, 90), (116.5, 93.5)]))
s = 0.0
while s < trail.length:
    seg = [trail.interpolate(s + t).coords[0] for t in (0, 0.9, min(1.8, trail.length - s))]
    ink.append(brush(seg, FINE, 0.3, 0.3))
    s += 3.2

# buzzing either side of the brain
for a0, a1 in ((158, 186), (-14, 12)):
    for r in (36.5, 39.5):
        ink.append(brush(arc(80, 66, r + 3, a0 + (r - 36.5), a1 - (r - 36.5)), 1.0, 0.3, 0.3))

# a few big stars to set the rhythm; the confetti fills in around them later
for x, y, r in ((6.5, 32, 2.8), (32, 5, 2.4), (8, 68, 2.6), (92, 6, 2.3), (155, 31, 2.8),
                (154, 64, 2.6), (66, 8, 2.1)):
    ink.append(star(x, y, r))

near_bulb = unary_union([g for g in ink if not any(g is b for b in BULB_INK)]).buffer(1.4)
ink += [g for g in GLOW if not g.intersects(near_bulb)]

# --- the burst ---------------------------------------------------------------------
# Wedges fan out from inside the top of the brain, between everything else, each
# shortened until it is clear of whatever it would run into.
O = (80, 55)
FRAME = box(-50, -50, W + 50, H + 50).difference(box(2, 2, W - 2, H - 2))
KEEP_OUT = unary_union(ink).difference(BRAIN.buffer(2.5)).buffer(1.8).union(FRAME)


def ray(angle, length, width, hollow=False, gap=3.2):
    u = (math.cos(math.radians(angle)), math.sin(math.radians(angle)))
    r1 = 0.0
    while BRAIN.distance(Point(O[0] + r1 * u[0], O[1] + r1 * u[1])) < gap or \
            BRAIN.contains(Point(O[0] + r1 * u[0], O[1] + r1 * u[1])):
        r1 += 0.2
    n = (-u[1], u[0])
    p = lambda r, s: (O[0] + r * u[0] + s * n[0], O[1] + r * u[1] + s * n[1])  # noqa: E731
    while length >= 6:
        r2 = r1 + length
        w = Polygon([p(r1, -0.12), p(r2, -width / 2), p(r2, width / 2), p(r1, 0.12)])
        w = w.union(Point(p(r2, 0)).buffer(width / 2, quad_segs=12))
        w = stroke(w.buffer(0.5).buffer(-0.5), LINE) if hollow else w
        if not w.intersects(KEEP_OUT):
            return w
        length -= 0.5
    return Polygon()


RAYS = [  # (angle, length, outer width, hollow)
    (-178, 24, 1.7, False), (-168, 18, 2.8, True), (-157, 26, 2.0, False), (-121, 10, 1.3, False),
    (-106, 16, 1.7, False), (-91, 38, 3.2, True), (-77, 22, 1.5, False), (-64, 15, 1.6, False),
    (-48, 14, 1.6, False), (-34, 22, 2.0, False), (-24, 18, 2.8, True), (-13, 28, 2.0, False),
    (-2, 22, 1.7, False),
]
rays = [ray(*r) for r in RAYS]
ink += rays

# --- confetti --------------------------------------------------------------------
# Small stars, sparkles, plus signs, dots and rings, spread evenly into the gaps.
taken = unary_union([Polygon(g.exterior) for g in getattr(unary_union(ink), "geoms", [])])
placed = []
cands = [(x + rng.uniform(-1.2, 1.2), y + rng.uniform(-1.2, 1.2))
         for x in np.arange(3.5, W - 3, 3.0) for y in np.arange(3.5, H - 3, 3.0)]
rng.shuffle(cands)
kinds = ["star", "twinkle", "plus", "dot", "ring"]
for x, y in cands:
    q = Point(x, y)
    if taken.distance(q) < 6.0 or any(q.distance(o) < 17.0 for o in placed):
        continue
    if BRAIN.buffer(6).contains(q):
        continue
    kind = kinds[len(placed) % len(kinds)]
    if kind == "star":
        g = star(x, y, rng.uniform(1.3, 1.8), rot=rng.uniform(-110, -70), round_=0.12)
    elif kind == "twinkle":
        g = twinkle(x, y, rng.uniform(1.7, 2.2))
    elif kind == "plus":
        g = unary_union([brush([(x - 1.1, y), (x + 1.1, y)], 0.65), brush([(x, y - 1.1), (x, y + 1.1)], 0.65)])
    elif kind == "dot":
        g = dot(x, y, rng.uniform(0.7, 1.0))
    else:
        g = stroke(Point(x, y).buffer(rng.uniform(0.8, 1.1)), FINE)
    placed.append(q)
    ink.append(g)


def main():
    art = unary_union(ink)
    polys = getattr(art, "geoms", [art])
    n = lambda v: f"{v:.2f}".rstrip("0").rstrip(".")  # noqa: E731
    paths = []
    for q in polys:
        q = orient(q.simplify(0.01), 1.0)
        d = "".join("M" + "L".join(f"{n(x)} {n(y)}" for x, y in ring.coords[:-1]) + "Z"
                    for ring in (q.exterior, *q.interiors))
        paths.append(f'<path d="{d}" fill="#000000"/>')
    OUT.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:g}mm" height="{H:g}mm" '
                   f'viewBox="0 0 {W:g} {H:g}">\n' + "\n".join(paths) + "\n</svg>\n")
    x0, y0, x1, y1 = art.bounds
    print(f"{OUT}: {len(paths)} paths, {len(folds)} brain folds, {len(placed)} confetti, "
          f"ink {x1 - x0:.1f} x {y1 - y0:.1f} mm")


if __name__ == "__main__":
    main()
