#!/usr/bin/env python3
"""Build model.html: an interactive 3D model of the four nested HingeBoxes.

usage: make_model.py [--fragment] [OUT.html]

--fragment leaves out the <!doctype>/<head> wrapper (for hosts that add their own).

Every piece is the real outline from the stock HingeBox generator (same
settings as generate.sh, but no kerf so the parts meet exactly), extruded to
the material thickness and folded into place:

* While the generator draws each wall, the drawing frame at the wall's inner
  corner is recorded (the rectangularWall callback for edge 0).  Mapping the
  wall's paths through the inverse of that frame gives its outline in wall
  coordinates: u along the bottom edge, v inwards, the x by h inner rectangle
  at [0, x] x [0, h].
* Each hinge piece is taken from the generator's hinge parts the same way,
  using the frame at its pin hole.  The pieces go where the generator cut the
  t x t holes for them in the back walls of box and lid.
* The page (model_template.html) extrudes each outline with three.js and
  draws the engraved text (engraving.py: the same outlines as on the cut
  sheets) on each box's front wall and under its bottom.

World frame of one box: X along the width, Y from front to back, Z up; the
inner space of the box is [0, x] x [0, y] x [0, h] and the lid sits on top up
to h + lidheight.  The lid turns about the hinge pin, which is on the outer
face of the back wall at height h.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from affine import Affine  # noqa: E402

from boxes.generators.hingebox import HingeBox  # noqa: E402

import engraving  # noqa: E402

T = 3.0
LIDHEIGHT = 20.0
EYES = 7
SIZES = [(160, 80, 60), (168, 95, 68), (176, 110, 76), (184, 125, 84)]  # x, y, h as in generate.sh
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#b0367c"]  # as in color_layouts.py
BEZIER_STEPS = 8


class RecordingHingeBox(HingeBox):
    """HingeBox that remembers where each wall and hinge piece was drawn."""

    def __init__(self):
        super().__init__()
        self.walls = []          # (x, y, edges, frame at inner corner, paths)
        self.hinge_frames = []   # frame at each hinge piece's pin hole
        self.hinge_paths = []
        self._in_hinges = False

    def _paths(self):
        return [p for part in self.surface.parts for p in part.pathes]

    def _new_paths(self, draw):
        before = {id(p) for p in self._paths()}
        draw()
        return [p for p in self._paths() if id(p) not in before]

    def rectangularWall(self, x, y, edges="eeee", callback=None, move=None, **kw):
        frame = []

        def record(i):
            if i == 0:
                frame.append(self.ctx._m)
        paths = self._new_paths(
            lambda: super(RecordingHingeBox, self).rectangularWall(x, y, edges, callback=record, move=move, **kw))
        if frame:
            self.walls.append((x, y, edges, frame[0], paths))

    def hole(self, x, y, r=0.0, d=0.0, tabs=0):
        if self._in_hinges:
            self.hinge_frames.append(self.ctx._m * Affine.translation(x, y))
        super().hole(x, y, r, d, tabs)

    def render(self):
        # HingeBox.render draws the hinge pieces last, with edges["u"].parts
        hinge_edge = self.edges["u"]
        parts = hinge_edge.parts

        def recorded_parts(*a, **kw):
            self._in_hinges = True
            self.hinge_paths = self._new_paths(lambda: parts(*a, **kw))
            self._in_hinges = False
        hinge_edge.parts = recorded_parts
        super().render()


def loops_of(paths):
    """Closed loops of boxes.drawing.Path objects, in raw drawing coordinates."""
    loops = []
    for p in paths:
        cur = None
        for c in p.path:
            if c[0] == "M":
                cur = [(c[1], c[2])]
                loops.append(cur)
            elif c[0] == "L":
                cur.append((c[1], c[2]))
            elif c[0] == "T":
                continue  # text (labels are off, but be safe)
            elif c[0] == "C":
                # boxes stores the destination first, then the two controls
                x0, y0 = cur[-1]
                x3, y3, x1, y1, x2, y2 = c[1:7]
                for k in range(1, BEZIER_STEPS + 1):
                    s = k / BEZIER_STEPS
                    a, b, cc, d = (1 - s) ** 3, 3 * s * (1 - s) ** 2, 3 * s * s * (1 - s), s ** 3
                    cur.append((a * x0 + b * x1 + cc * x2 + d * x3, a * y0 + b * y1 + cc * y2 + d * y3))
    return stitch([lp for lp in loops if len(lp) > 1])


def stitch(paths):
    """Join open paths that meet end to start into closed loops."""
    closed, open_ = [], []
    for p in paths:
        (closed if math.dist(p[0], p[-1]) < 0.01 else open_).append(list(p))
    while open_:
        cur = open_.pop(0)
        grown = True
        while grown and math.dist(cur[0], cur[-1]) >= 0.01:
            grown = False
            for i, q in enumerate(open_):
                if math.dist(cur[-1], q[0]) < 0.01:
                    cur += q[1:]
                elif math.dist(cur[-1], q[-1]) < 0.01:
                    cur += q[::-1][1:]
                else:
                    continue
                open_.pop(i)
                grown = True
                break
        closed.append(cur)
    return closed


def area(lp):
    return 0.5 * sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(lp, lp[1:] + lp[:1]))


def local(lp, frame):
    inv = ~frame
    pts = [inv * p for p in lp]
    if math.dist(pts[0], pts[-1]) < 0.01:
        pts = pts[:-1]
    return [(round(x, 3), round(y, 3)) for x, y in pts]


def shape(loops):
    """Outline (largest loop, counter-clockwise) and holes (clockwise)."""
    loops = sorted(loops, key=lambda lp: -abs(area(lp)))
    outer, holes = loops[0], loops[1:]
    if area(outer) < 0:
        outer = outer[::-1]
    holes = [h if area(h) < 0 else h[::-1] for h in holes]
    return outer, holes


def square_holes(holes, t):
    """Centres of the t x t holes the hinge pieces hook through."""
    out = []
    for h in holes:
        xs, ys = [p[0] for p in h], [p[1] for p in h]
        if abs(max(xs) - min(xs) - t) < 0.05 and abs(max(ys) - min(ys) - t) < 0.05:
            out.append(((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2))
    return sorted(out)


def build_box(size_x, size_y, size_h):
    # The generate.sh arguments (which leave --outside at its default), plus
    # no kerf and no labels.
    b = RecordingHingeBox()
    b.parseArgs(["--x", str(size_x), "--y", str(size_y), "--h", str(size_h), "--lidheight", str(LIDHEIGHT),
                 "--thickness", str(T), "--CabinetHinge_eyes_per_hinge", str(EYES),
                 "--burn", "0", "--reference", "0", "--labels", "0"])
    b.open()
    b.render()
    t, hl = b.thickness, b.lidheight
    # inner size as drawn: the front wall is x by h, a side wall y by h
    x, h = b.walls[0][0], b.walls[0][1]
    y = b.walls[1][0]
    e = b.edges["u"].settings.eye  # relative settings are already in mm

    # Placement of each wall: world = origin + u * U + v * V + w * W, with
    # w in [0, t] going outwards.  Walls are seen from outside, u to the
    # right and v up (the bottom plate and lid top are seen from above).
    placements = {
        # edges: (name, group, origin, U, V, W)
        "FFeF": [("front", "box", (0, 0, 0), (1, 0, 0), (0, 0, 1), (0, -1, 0))],
        "Ffef": [("left", "box", (0, y, 0), (0, -1, 0), (0, 0, 1), (-1, 0, 0)),
                 ("right", "box", (x, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 0))],
        "FFuF": [("back", "box", (x, y, 0), (-1, 0, 0), (0, 0, 1), (0, 1, 0))],
        "UFFF": [("lid back", "lid", (x, y, h), (-1, 0, 0), (0, 0, 1), (0, 1, 0))],
        "efFf": [("lid left", "lid", (0, y, h), (0, -1, 0), (0, 0, 1), (-1, 0, 0)),
                 ("lid right", "lid", (x, 0, h), (0, 1, 0), (0, 0, 1), (1, 0, 0))],
        "eFFF": [("lid front", "lid", (0, 0, h), (1, 0, 0), (0, 0, 1), (0, -1, 0))],
        "ffff": [("bottom", "box", (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, -1)),
                 ("lid top", "lid", (0, 0, h + hl), (1, 0, 0), (0, 1, 0), (0, 0, 1))],
    }
    pieces, back_holes = [], {}
    for wx, wy, edges, frame, paths in b.walls:
        name, group, o, U, V, W = placements[edges].pop(0)
        outer, holes = shape([local(lp, frame) for lp in loops_of(paths)])
        pieces.append({"name": name, "group": group, "outline": outer, "holes": holes,
                       "origin": o, "u": U, "v": V, "w": W})
        if name in ("back", "lid back"):
            back_holes[group] = (o, U, V, square_holes(holes, t))

    # One hinge piece in the frame of its pin hole: the pin at (0, 0), the
    # piece reaching into its wall along +y, x = 0 at the wall's outer face
    # (x < 0 inside the box, the knuckle sticks out to x = e).
    frame0 = b.hinge_frames[0]
    hinge_loops = [local(lp, frame0) for lp in loops_of(b.hinge_paths)]
    near = [lp for lp in hinge_loops
            if all(-3 * t - 0.1 < px < e + 0.1 and -e - 0.1 < py < e + 3 * t + 0.1 for px, py in lp)]
    hinge_outline, hinge_holes = shape(near)

    hinges = []
    for group, sign in (("box", -1), ("lid", 1)):
        o, U, V, centres = back_holes[group]
        for cu, cv in centres:
            # pin axis position along X from the hole centre; the piece is t
            # thick, centred on the hole
            px = o[0] + cu * U[0]
            hinges.append({"group": group, "x": round(px - t / 2, 3), "dir": sign})
    return {
        "size": [size_x, size_y, size_h], "outside": bool(b.outside),
        "x": x, "y": y, "h": h, "lidheight": hl, "t": t, "eye": e,
        "pin": {"y": y + t, "z": h, "r": b.edges["u"].settings.bore / 2},
        "pieces": pieces, "hinges": hinges,
        "hinge": {"outline": hinge_outline, "holes": hinge_holes},
    }


def main():
    args = sys.argv[1:]
    fragment = "--fragment" in args
    args = [a for a in args if a != "--fragment"]
    out = Path(args[0]) if args else HERE / "model.html"
    boxes = []
    for n, (x, y, h) in enumerate(SIZES, 1):
        box = build_box(x, y, h)
        box.update(name=f"Box {n}", color=COLORS[n - 1])
        boxes.append(box)
    # Engraved text and lid artwork on each face's inner area, origin at its top-left corner
    text = engraving.box_text([(0, 0, b["x"], b["h"]) for b in boxes],
                              [(0, 0, b["x"], b["y"]) for b in boxes],
                              [(0, 0, b["x"], b["y"]) for b in boxes])
    for b, t in zip(boxes, text):
        b["text"] = {face: {k: v for k, v in f.items() if k != "ink"} for face, f in t.items()}
    data = json.dumps({"boxes": boxes}, separators=(",", ":"))
    html = (HERE / "model_template.html").read_text().replace("/*MODEL_DATA*/null", data)
    if not fragment:
        html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                '<style>body{margin:0}[hidden]{display:none!important}</style>\n</head>\n<body>\n'
                + html + '\n</body>\n</html>\n')
    out.write_text(html)
    print(out, f"{len(data) / 1024:.0f} kB of geometry")


if __name__ == "__main__":
    main()
