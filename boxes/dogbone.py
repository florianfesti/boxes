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


def dogbone_clearance(radius: float) -> float:
    """Return c = R * (1 + sqrt(2)/2 + sqrt(5/2 - sqrt(2)))."""
    sqrt2 = math.sqrt(2.0)
    return radius * (1.0 + sqrt2 / 2.0 + math.sqrt(2.5 - sqrt2))


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

    sqrt2 = math.sqrt(2.0)
    offset = sqrt2 * radius
    if offset < eps:
        return False

    sqrt_inner = math.sqrt(2.5 - sqrt2)
    clearance = dogbone_clearance(radius)
    prev_clearance = clearance - radius
    end_offset_next = (radius / 2.0) * (sqrt2 / 2.0 - 1.0)
    end_offset_prev = (radius / 2.0) * (sqrt2 + sqrt_inner)

    def _normalize(vec: Vector) -> Vector | None:
        if vlength(vec) < eps:
            return None
        return normalize_vec(vec)

    from boxes.drawing import Context, Surface

    def arc_segments(center: Point, start: Point, end: Point, orientation: int) -> list[tuple[float, ...]]:
        radius = vlength(vdiff(center, start))
        if radius < eps or vlength(vdiff(center, end)) < eps:
            return []
        angle_start = math.atan2(start[1] - center[1], start[0] - center[0])
        angle_end = math.atan2(end[1] - center[1], end[0] - center[0])
        full_turn = 2.0 * math.pi
        if orientation > 0:
            while angle_end <= angle_start + eps:
                angle_end += full_turn
        else:
            while angle_end >= angle_start - eps:
                angle_end -= full_turn
        surface = Surface()
        ctx = Context(surface)
        ctx.move_to(*start)
        (ctx.arc if orientation > 0 else ctx.arc_negative)(center[0], center[1], radius, angle_start, angle_end)
        ctx.stroke()
        parts = surface.parts
        if not parts or not parts[0].pathes:
            return []
        return [tuple(cmd) for cmd in parts[0].pathes[-1].path if cmd[0] == 'C']
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

            axis_prev = (-d_prev[0], -d_prev[1])
            axis_next = d_next

            center = vadd(corner, vscalmul(n_in, radius))
            main_end = vadd(corner, vscalmul(d_next, offset))
            transition_point = vadd(
                corner,
                vadd(
                    vscalmul(axis_next, end_offset_next),
                    vscalmul(axis_prev, end_offset_prev),
                ),
            )
            axis_prev_post = axis_next
            axis_next_post = axis_prev
            transition_point_next = vadd(
                corner,
                vadd(
                    vscalmul(axis_next_post, end_offset_next),
                    vscalmul(axis_prev_post, end_offset_prev),
                ),
            )
            new_arc_start = vadd(corner, vscalmul(axis_prev, prev_clearance))
            new_arc_center = vadd(
                corner,
                vadd(vscalmul(axis_prev, prev_clearance), vscalmul(axis_next, -radius)),
            )
            new_arc_end = vadd(corner, vscalmul(axis_prev_post, prev_clearance))
            new_arc_center_next = vadd(
                corner,
                vadd(vscalmul(axis_prev_post, prev_clearance), vscalmul(axis_next_post, -radius)),
            )

            rad_start = vdiff(center, transition_point)
            rad_end = vdiff(center, main_end)
            if vlength(rad_start) < eps or vlength(rad_end) < eps:
                i += 1
                continue

            mid_cw = vadd(center, vscalmul(vorthogonal(rad_start), -1.0))
            mid_ccw = vadd(center, vorthogonal(rad_start))
            score_cw = dotproduct(vdiff(corner, mid_cw), n_in)
            score_ccw = dotproduct(vdiff(corner, mid_ccw), n_in)
            orientation = 1 if score_cw >= score_ccw else -1
            orientation2 = -orientation

            pre_segments = arc_segments(new_arc_center, new_arc_start, transition_point, orientation2)
            if not pre_segments:
                i += 1
                continue

            main_segments = arc_segments(center, transition_point, transition_point_next, orientation)
            if not main_segments:
                i += 1
                continue

            post_segments = arc_segments(new_arc_center_next, transition_point_next, new_arc_end, orientation2)
            if not post_segments:
                i += 1
                continue

            combined_segments = pre_segments + main_segments + post_segments

            path[i - 1] = ("L", new_arc_start[0], new_arc_start[1])
            path[i : i + 1] = combined_segments
            i += len(combined_segments)
            continue

        i += 1

    return True
