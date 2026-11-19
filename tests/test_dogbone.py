from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

try:
    pass
except ImportError:
    sys.path.append(Path(__file__).resolve().parent.parent.__str__())
    pass

from boxes.drawing import DOGBONE_CLEARANCE, apply_dogbones
from boxes.generators.closedbox import ClosedBox


def bezier_points(path, steps=400):
    """All points along the path (sampling the Bezier curves)"""
    points = []
    cur = None
    for c in path:
        if c[0] in "ML":
            cur = c[1:3]
            points.append(cur)
        elif c[0] == "C":
            p0, p3 = cur, c[1:3]
            p1, p2 = c[3:5], c[5:7]
            for i in range(1, steps + 1):
                t = i / steps
                u = 1 - t
                points.append(tuple(
                    u**3 * p0[k] + 3 * u**2 * t * p1[k] + 3 * u * t**2 * p2[k] + t**3 * p3[k]
                    for k in range(2)))
            cur = p3
    return points


def corner_path(theta_deg, r, length=20.0):
    """Closed outline of a part with one inner corner at (0, 0)

    The cut out area in the corner has the angle theta. The incoming line
    comes in along the negative x axis, the outgoing line leaves at theta
    below it. The part is on the other side.
    """
    t = math.radians(theta_deg)
    a = (-length, 0.0)
    v = (0.0, 0.0)
    d = (length * math.cos(math.pi - t), -length * math.sin(math.pi - t))
    return [
        ["M", *a],
        ["L", *v],
        ["D", *v, r, False],
        ["L", *d],
        ["L", 2 * length, d[1]],
        ["L", 2 * length, length],
        ["L", -length, length],
        ["L", *a],
    ], v


@pytest.mark.parametrize("theta", [60, 90, 120])
def test_dogbone_geometry(theta) -> None:
    r = 1.5
    path, v = corner_path(theta, r)
    result = apply_dogbones(path)

    assert not any(c[0] == "D" for c in result), "markers must be removed"
    curves = [c for c in result if c[0] == "C"]
    assert curves, "dog bone must be added"

    points = bezier_points(result)
    # the outline must go through the corner to cut it out completely
    assert min(math.dist(p, v) for p in points) < 1e-2

    # all points of the dog bone are on a circle of radius r
    # whose center is on the bisector at distance r from the corner
    t = math.radians(theta)
    d1 = (1.0, 0.0)
    d2 = (math.cos(math.pi - t), -math.sin(math.pi - t))
    b = (d2[0] - d1[0], d2[1] - d1[1])
    lb = math.hypot(*b)
    center = (v[0] + r * b[0] / lb, v[1] + r * b[1] / lb)
    arc_points = bezier_points([["M", *result[result.index(curves[0]) - 1][1:3]]] + curves)
    for p in arc_points:
        assert math.dist(p, center) == pytest.approx(r, abs=1e-3)

    # the dog bone starts and ends on the walls
    chord = 2 * r * math.cos(t / 2)
    assert math.dist(arc_points[0], v) == pytest.approx(chord, abs=1e-6)
    assert math.dist(arc_points[-1], v) == pytest.approx(chord, abs=1e-6)


def test_dogbone_overlap_in_narrow_slot() -> None:
    # slot 2mm wide and 5mm deep - too narrow for two separate dog bones
    r = 1.6
    path = [
        ["M", -10.0, 0.0],
        ["L", 0.0, 0.0],
        ["L", 0.0, -5.0],
        ["D", 0.0, -5.0, r, False],
        ["L", 2.0, -5.0],
        ["D", 2.0, -5.0, r, False],
        ["L", 2.0, 0.0],
        ["L", 12.0, 0.0],
        ["L", 12.0, 10.0],
        ["L", -10.0, 10.0],
        ["L", -10.0, 0.0],
    ]
    result = apply_dogbones(path)
    assert not any(c[0] == "D" for c in result)
    # the bottom of the slot is gone, the two dog bones meet directly
    assert not any(c[0] == "L" and abs(c[2] + 5.0) < 1e-6 for c in result)
    # both corners are still cut out
    points = bezier_points(result)
    for corner in ((0.0, -5.0), (2.0, -5.0)):
        assert min(math.dist(p, corner) for p in points) < 1e-2
    # the path is still closed
    assert result[0][1:3] == result[-1][1:3]


def test_dogbone_extends_past_short_wall() -> None:
    # wall of 1mm next to the corner - dog bone ends on the next line
    r = 1.6
    path = [
        ["M", -10.0, 0.0],
        ["L", 0.0, 0.0],
        ["L", 0.0, -1.0],
        ["D", 0.0, -1.0, r, False],
        ["L", 10.0, -1.0],
        ["L", 10.0, 10.0],
        ["L", -10.0, 10.0],
        ["L", -10.0, 0.0],
    ]
    result = apply_dogbones(path)
    assert any(c[0] == "C" for c in result)
    # the short wall is replaced by the dog bone
    assert not any(c[0] == "L" and c[1:3] == [0.0, 0.0] for c in result)
    points = bezier_points(result)
    assert min(math.dist(p, (0.0, -1.0)) for p in points) < 1e-2


def test_dogbone_skipped_if_it_does_not_fit() -> None:
    # incoming wall too short and no straight line before it to continue to
    r = 1.6
    path = [
        ["M", 0.0, 0.0],
        ["L", 0.0, -1.0],
        ["D", 0.0, -1.0, r, False],
        ["L", 10.0, -1.0],
    ]
    result = apply_dogbones(path)
    assert result == [["M", 0.0, 0.0], ["L", 0.0, -1.0], ["L", 10.0, -1.0]]


@pytest.mark.parametrize("burn", [0.0, 0.1])
def test_closedbox_dogbone(burn) -> None:
    def render(*args):
        box = ClosedBox()
        box.parseArgs(["--reference=0", f"--burn={burn}", *args])
        box.metadata["reproducible"] = True
        box.open()
        box.render()
        return box.close().getvalue()

    dogbone = render("--inner_corners=dogbone", "--bit_diameter=3.175")
    corner = render("--inner_corners=corner")
    assert dogbone != corner
    assert b" C " in dogbone
    assert b"Unknown" not in dogbone


def test_dogbone_radius_includes_clearance() -> None:
    box = ClosedBox()
    box.parseArgs(["--inner_corners=dogbone", "--bit_diameter=6", "--burn=0"])
    box.open()
    box.render()
    radii = {round(c[3], 6)
             for part in box.surface.parts
             for p in part.pathes
             for c in p.path if c[0] == "D"}
    assert radii == {round(3 + DOGBONE_CLEARANCE, 6)}
