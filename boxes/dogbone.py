from __future__ import annotations

import math
from typing import Any, Callable, MutableSequence

from boxes.vectors import (
    dotproduct,
    normalize as normalize_vec,
    vadd,
    vdiff,
    vlength,
    vorthogonal,
    vscalmul,
)

PathLike = MutableSequence[Any]
Vector = tuple[float, float]
Point = tuple[float, float]


def kappa_gamma(gamma_degrees: float) -> float:
    """Return kappa(gamma) = sqrt(2) + (1 + sqrt(2)) * tan(gamma - 45 degrees)."""
    sqrt2 = math.sqrt(2.0)
    angle = math.radians(gamma_degrees - 45.0)
    return sqrt2 + (1.0 + sqrt2) * math.tan(angle)


def apply_dogbone(
    path: PathLike,
    dogbone_radius: Any,
    eps: float,
    line_intersection: Callable[[tuple[Any, Any], tuple[Any, Any]], tuple[bool, float | None, float | None]],
) -> bool:
    """Apply dogbone adjustments to a path in-place.

    Returns False when the caller should abort further processing (e.g. invalid radius).
    """
    if dogbone_radius is None:
        return False

    radius = float(dogbone_radius)
    if radius <= 0:
        return False

    offset = math.sqrt(2.0) * radius
    if offset < eps:
        return False

    def _normalize(vec: Vector) -> Vector | None:
        if vlength(vec) < eps:
            return None
        return normalize_vec(vec)

    i = 0
    while i < len(path):
        segment = path[i]
        if (
            segment[0] == "C"
            and i > 1
            and i < len(path) - 1
            and path[i - 1][0] == "L"
            and path[i + 1][0] == "L"
        ):
            p11 = path[i - 2][1:3]
            p12 = path[i - 1][1:3]
            p21 = segment[1:3]
            p22 = path[i + 1][1:3]

            lines_intersect, ox, oy = line_intersection((p11, p12), (p21, p22))
            if not lines_intersect:
                i += 1
                continue

            corner: Point = (ox, oy)
            prev_vec = vdiff(p11, corner)
            next_vec = vdiff(corner, p22)

            prev_len = vlength(prev_vec)
            next_len = vlength(next_vec)
            if prev_len <= offset + eps or next_len <= offset + eps:
                i += 1
                continue

            d_prev = _normalize(prev_vec)
            d_next = _normalize(next_vec)
            if d_prev is None or d_next is None:
                i += 1
                continue

            if abs(dotproduct(d_prev, d_next)) > 1e-3:
                i += 1
                continue

            turn = d_prev[0] * d_next[1] - d_prev[1] * d_next[0]
            if abs(turn) < 1e-9:
                i += 1
                continue

            sign = 1.0 if turn > 0.0 else -1.0
            inward = vadd(
                vscalmul(vorthogonal(d_prev), sign),
                vscalmul(vorthogonal(d_next), sign),
            )
            n_in = _normalize(inward)
            if n_in is None:
                i += 1
                continue

            center = vadd(corner, vscalmul(n_in, radius))
            start_point = vadd(corner, vscalmul(d_prev, -offset))
            end_point = vadd(corner, vscalmul(d_next, offset))

            rad_start = vdiff(center, start_point)
            rad_end = vdiff(center, end_point)
            if vlength(rad_start) < eps or vlength(rad_end) < eps:
                i += 1
                continue

            mid_cw = vadd(center, vscalmul(vorthogonal(rad_start), -1.0))
            mid_ccw = vadd(center, vorthogonal(rad_start))
            score_cw = dotproduct(vdiff(corner, mid_cw), n_in)
            score_ccw = dotproduct(vdiff(corner, mid_ccw), n_in)
            orientation = 1 if score_cw >= score_ccw else -1

            theta_start = math.atan2(rad_start[1], rad_start[0])
            theta_end = math.atan2(rad_end[1], rad_end[0])
            if orientation == 1:
                while theta_end <= theta_start:
                    theta_end += 2 * math.pi
            else:
                while theta_end >= theta_start:
                    theta_end -= 2 * math.pi

            delta = theta_end - theta_start
            segments = max(1, int(math.ceil(abs(delta) / (math.pi / 2.0))))

            new_segments: list[tuple[float, ...]] = []
            for seg_idx in range(segments):
                t0 = theta_start + delta * (seg_idx / segments)
                t1 = theta_start + delta * ((seg_idx + 1) / segments)
                k = 4.0 / 3.0 * math.tan((t1 - t0) / 4.0)

                cos0, sin0 = math.cos(t0), math.sin(t0)
                cos1, sin1 = math.cos(t1), math.sin(t1)

                p0x, p0y = center[0] + radius * cos0, center[1] + radius * sin0
                p3x, p3y = center[0] + radius * cos1, center[1] + radius * sin1

                c1x = p0x - k * radius * sin0
                c1y = p0y + k * radius * cos0
                c2x = p3x + k * radius * sin1
                c2y = p3y - k * radius * cos1

                new_segments.append(("C", p3x, p3y, c1x, c1y, c2x, c2y))

            path[i - 1] = ("L", start_point[0], start_point[1])
            path[i : i + 1] = new_segments
            i += len(new_segments)
            continue

        i += 1

    return True
