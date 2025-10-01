from __future__ import annotations

import math
from typing import Any, Callable, MutableSequence

PathLike = MutableSequence[Any]


def apply_dogbone(path: PathLike, dogbone_radius: Any, eps: float, line_intersection: Callable[[tuple[Any, Any], tuple[Any, Any]], tuple[bool, float | None, float | None]]) -> bool:
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

    def _normalize(vx: float, vy: float) -> tuple[float, float] | None:
        length = math.hypot(vx, vy)
        if length < eps:
            return None
        return (vx / length, vy / length)

    def _rotate_cw(vx: float, vy: float) -> tuple[float, float]:
        return (vy, -vx)

    def _rotate_ccw(vx: float, vy: float) -> tuple[float, float]:
        return (-vy, vx)

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

            prev_len = math.hypot(ox - p11[0], oy - p11[1])
            next_len = math.hypot(p22[0] - ox, p22[1] - oy)
            if prev_len <= offset + eps or next_len <= offset + eps:
                i += 1
                continue

            d_prev = _normalize(ox - p11[0], oy - p11[1])
            d_next = _normalize(p22[0] - ox, p22[1] - oy)
            if d_prev is None or d_next is None:
                i += 1
                continue

            dot = d_prev[0] * d_next[0] + d_prev[1] * d_next[1]
            if abs(dot) > 1e-3:
                i += 1
                continue

            turn = d_prev[0] * d_next[1] - d_prev[1] * d_next[0]
            if abs(turn) < 1e-9:
                i += 1
                continue

            if turn > 0:
                inward = (-d_prev[1], d_prev[0])
                inward = (inward[0] + -d_next[1], inward[1] + d_next[0])
            else:
                inward = (d_prev[1], -d_prev[0])
                inward = (inward[0] + d_next[1], inward[1] + -d_next[0])

            n_in = _normalize(*inward)
            if n_in is None:
                i += 1
                continue

            cx, cy = ox + n_in[0] * radius, oy + n_in[1] * radius
            sx, sy = ox - d_prev[0] * offset, oy - d_prev[1] * offset
            ex, ey = ox + d_next[0] * offset, oy + d_next[1] * offset

            rad_start = (sx - cx, sy - cy)
            rad_end = (ex - cx, ey - cy)
            if (
                math.hypot(*rad_start) < eps
                or math.hypot(*rad_end) < eps
            ):
                i += 1
                continue

            mid_cw_vec = _rotate_cw(*rad_start)
            mid_ccw_vec = _rotate_ccw(*rad_start)
            mid_cw = (cx + mid_cw_vec[0], cy + mid_cw_vec[1])
            mid_ccw = (cx + mid_ccw_vec[0], cy + mid_ccw_vec[1])
            score_cw = (mid_cw[0] - ox) * n_in[0] + (mid_cw[1] - oy) * n_in[1]
            score_ccw = (mid_ccw[0] - ox) * n_in[0] + (mid_ccw[1] - oy) * n_in[1]
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
            segments = max(1, int(math.ceil(abs(delta) / (math.pi / 2))))
            new_segments: list[tuple[float, ...]] = []
            for seg_idx in range(segments):
                t0 = theta_start + delta * (seg_idx / segments)
                t1 = theta_start + delta * ((seg_idx + 1) / segments)
                k = 4.0 / 3.0 * math.tan((t1 - t0) / 4.0)
                cos0, sin0 = math.cos(t0), math.sin(t0)
                cos1, sin1 = math.cos(t1), math.sin(t1)
                p0x, p0y = cx + radius * cos0, cy + radius * sin0
                p3x, p3y = cx + radius * cos1, cy + radius * sin1
                c1x = p0x - k * radius * sin0
                c1y = p0y + k * radius * cos0
                c2x = p3x + k * radius * sin1
                c2y = p3y - k * radius * cos1
                new_segments.append((p3x, p3y, c1x, c1y, c2x, c2y))

            path[i - 1] = ("L", sx, sy)
            path[i : i + 1] = [
                ("C", px, py, c1x, c1y, c2x, c2y)
                for (px, py, c1x, c1y, c2x, c2y) in new_segments
            ]
            i += len(new_segments)
            continue

        i += 1

    return True
