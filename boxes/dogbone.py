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

# Utilities for inserting dogbone reliefs into tool paths.
PathLike = MutableSequence[Any]
Vector = tuple[float, float]
Point = tuple[float, float]

TAU = math.tau


def _normalize_angles(start: float, end: float, orientation: int, eps: float) -> tuple[float, float]:
    if orientation > 0:
        while end <= start + eps:
            end += TAU
    else:
        while end >= start - eps:
            end -= TAU
    return start, end


def _angle_in_span(angle: float, start: float, end: float, orientation: int, eps: float) -> bool:
    if orientation > 0:
        while angle < start - eps:
            angle += TAU
        while angle > end + eps:
            angle -= TAU
        return start - eps <= angle <= end + eps
    while angle > start + eps:
        angle -= TAU
    while angle < end - eps:
        angle += TAU
    return end - eps <= angle <= start + eps


def _point_on_arc(segment: dict[str, Any], point: Point, eps: float) -> bool:
    cx, cy = segment["center"]
    radius = segment["radius"]
    if abs(math.hypot(point[0] - cx, point[1] - cy) - radius) > eps:
        return False
    angle = math.atan2(point[1] - cy, point[0] - cx)
    return _angle_in_span(angle, segment["start_angle"], segment["end_angle"], segment["orientation"], eps)


def _circle_intersections(center_a: Point, radius_a: float, center_b: Point, radius_b: float, tol: float) -> list[Point]:
    dx = center_b[0] - center_a[0]
    dy = center_b[1] - center_a[1]
    d2 = dx * dx + dy * dy
    if d2 <= tol:
        return []
    dist = math.sqrt(d2)
    if dist > radius_a + radius_b + tol or dist < abs(radius_a - radius_b) - tol:
        return []
    a = (radius_a * radius_a - radius_b * radius_b + d2) / (2 * dist)
    h_sq = radius_a * radius_a - a * a
    if h_sq < -tol:
        return []
    h = math.sqrt(max(0.0, h_sq))
    xm = center_a[0] + a * dx / dist
    ym = center_a[1] + a * dy / dist
    rx = -dy * (h / dist)
    ry = dx * (h / dist)
    return [(xm + rx, ym + ry), (xm - rx, ym - ry)]


def dogbone_clearance(radius: float) -> float:
    """Return c = R * (1 + sqrt(2)/2 + sqrt(5/2 - sqrt(2)))."""
    # Closed form of the clearance distance used by Boxes.py.
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

    # These offsets define where the auxiliary arcs start and end relative to the corner.
    sqrt_inner = math.sqrt(2.5 - sqrt2)
    clearance = dogbone_clearance(radius)
    prev_clearance = clearance - radius
    end_offset_next = (radius / 2.0) * (sqrt2 / 2.0 - 1.0)
    end_offset_prev = (radius / 2.0) * (sqrt2 + sqrt_inner)

    def _normalize(vec: Vector) -> Vector | None:
        if vlength(vec) < eps:
            return None
        return normalize_vec(vec)

    def _arc_command(center: Point, start: Point, end: Point, orientation: int) -> list[Any] | None:
        radius = vlength(vdiff(center, start))
        if radius < eps or vlength(vdiff(center, end)) < eps:
            return None
        start_angle = math.atan2(start[1] - center[1], start[0] - center[0])
        end_angle = math.atan2(end[1] - center[1], end[0] - center[0])
        start_angle, end_angle = _normalize_angles(start_angle, end_angle, orientation, eps)
        return [
            "A",
            end[0],
            end[1],
            center[0],
            center[1],
            radius,
            start_angle,
            end_angle,
            orientation,
        ]

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
            # Work on inner corners expressed as line-curve-line.
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
            if prev_len <= eps or next_len <= eps:
                i += 1
                continue

            d_prev = _normalize(prev_vec)
            d_next = _normalize(next_vec)
            if d_prev is None or d_next is None:
                i += 1
                continue

            # Skip corners that are not approximately orthogonal.
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

            # Precompute axes to place the transition and finishing arcs.
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

            pre_arc = _arc_command(new_arc_center, new_arc_start, transition_point, orientation2)
            if pre_arc is None:
                i += 1
                continue

            main_arc = _arc_command(center, transition_point, transition_point_next, orientation)
            if main_arc is None:
                i += 1
                continue

            post_arc = _arc_command(new_arc_center_next, transition_point_next, new_arc_end, orientation2)
            if post_arc is None:
                i += 1
                continue

            path[i - 1] = ["L", new_arc_start[0], new_arc_start[1]]
            path[i : i + 1] = [pre_arc, main_arc, post_arc]
            i += 3
            continue

        i += 1

    _trim_overlaps(path, eps)
    return True


def _trim_overlaps(path: PathLike, eps: float) -> None:
    overlaps: list[dict[str, Any]] = []
    arcs_since_line: list[dict[str, Any]] = []
    line_state: dict[str, Any] | None = None
    current: Point | None = None

    def evaluate_candidate(line_data: dict[str, Any], right_arc: dict[str, Any]) -> dict[str, Any] | None:
        best: dict[str, Any] | None = None
        start = line_data["start"]
        end = line_data["end"]
        lx = end[0] - start[0]
        ly = end[1] - start[1]
        length = math.hypot(lx, ly)
        if length <= eps:
            return None
        length_sq = length * length
        for left_arc in line_data["left_arcs"]:
            for point in _circle_intersections(left_arc["center"], left_arc["radius"], right_arc["center"], right_arc["radius"], eps):
                if not _point_on_arc(left_arc, point, eps):
                    continue
                if not _point_on_arc(right_arc, point, eps):
                    continue
                px = point[0] - start[0]
                py = point[1] - start[1]
                projection = (px * lx + py * ly) / length_sq
                distance = abs(px * ly - py * lx) / length
                score = (
                    0 if 0.0 <= projection <= 1.0 else 1,
                    distance,
                    abs(projection - 0.5),
                )
                candidate = {
                    "score": score,
                    "point": point,
                    "left_arc": left_arc,
                    "right_arc": right_arc,
                    "line_index": line_data["index"],
                }
                if best is None or candidate["score"] < best["score"]:
                    best = candidate
        return best

    def finalize_line_state() -> None:
        nonlocal line_state
        if line_state and line_state.get("best"):
            overlaps.append(line_state["best"])
        line_state = None

    for index, segment in enumerate(path):
        code = segment[0]
        if code == "M":
            finalize_line_state()
            current = (segment[1], segment[2])
            arcs_since_line = []
        elif code == "L":
            finalize_line_state()
            start = current if current is not None else (segment[1], segment[2])
            end = (segment[1], segment[2])
            line_state = {
                "index": index,
                "start": start,
                "end": end,
                "left_arcs": arcs_since_line.copy(),
                "best": None,
            }
            arcs_since_line = []
            current = end
        elif code == "A":
            if current is None:
                current = (segment[1], segment[2])
            arc_info = {
                "index": index,
                "start": current,
                "end": (segment[1], segment[2]),
                "center": (segment[3], segment[4]),
                "radius": float(segment[5]),
                "start_angle": float(segment[6]),
                "end_angle": float(segment[7]),
                "orientation": int(segment[8]),
            }
            arcs_since_line.append(arc_info)
            if line_state and line_state["left_arcs"]:
                candidate = evaluate_candidate(line_state, arc_info)
                if candidate and (line_state["best"] is None or candidate["score"] < line_state["best"]["score"]):
                    line_state["best"] = candidate
            current = arc_info["end"]
        else:
            current = (segment[1], segment[2]) if len(segment) >= 3 else current

    finalize_line_state()
    if not overlaps:
        return

    left_targets: dict[int, Point] = {}
    line_targets: dict[int, Point] = {}
    skip_indices: set[int] = set()

    for overlap in overlaps:
        left_idx = overlap["left_arc"]["index"]
        right_idx = overlap["right_arc"]["index"]
        line_idx = overlap["line_index"]
        point = overlap["point"]
        left_targets[left_idx] = point
        line_targets[line_idx] = point
        for idx in range(left_idx + 1, right_idx):
            if idx != line_idx:
                skip_indices.add(idx)

    updated_path: PathLike = []
    for idx, segment in enumerate(path):
        if idx in skip_indices:
            continue
        cmd = segment.copy()
        if idx in line_targets and cmd[0] == "L":
            px, py = line_targets[idx]
            cmd[1], cmd[2] = px, py
        if idx in left_targets and cmd[0] == "A":
            px, py = left_targets[idx]
            cmd[1], cmd[2] = px, py
        updated_path.append(cmd)

    current_point: Point | None = None
    for segment in updated_path:
        code = segment[0]
        if code == "M":
            current_point = (segment[1], segment[2])
        elif code == "L":
            current_point = (segment[1], segment[2])
        elif code == "A":
            if current_point is None:
                current_point = (segment[1], segment[2])
            cx, cy = segment[3], segment[4]
            orientation = int(segment[8])
            start_angle = math.atan2(current_point[1] - cy, current_point[0] - cx)
            end_angle = math.atan2(segment[2] - cy, segment[1] - cx)
            start_angle, end_angle = _normalize_angles(start_angle, end_angle, orientation, eps)
            segment[6] = start_angle
            segment[7] = end_angle
            current_point = (segment[1], segment[2])
        elif len(segment) >= 3:
            current_point = (segment[1], segment[2])

    path[:] = updated_path
