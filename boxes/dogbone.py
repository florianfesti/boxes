from __future__ import annotations

import math
from typing import Any, Callable, MutableSequence

from boxes.vectors import (
    dotproduct,
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
SQRT2 = math.sqrt(2.0)
SQRT_INNER = math.sqrt(2.5 - SQRT2)
DOGBONE_CLEARANCE_FACTOR = 1.0 + SQRT2 / 2.0 + SQRT_INNER
DOGBONE_PREV_CLEARANCE_FACTOR = DOGBONE_CLEARANCE_FACTOR - 1.0
END_OFFSET_NEXT_FACTOR = 0.5 * (SQRT2 / 2.0 - 1.0)
END_OFFSET_PREV_FACTOR = 0.5 * (SQRT2 + SQRT_INNER)


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
    return radius * DOGBONE_CLEARANCE_FACTOR


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

    offset = SQRT2 * radius
    if offset < eps:
        return False

    # These offsets define where the auxiliary arcs start and end relative to the corner.
    prev_clearance = radius * DOGBONE_PREV_CLEARANCE_FACTOR
    end_offset_next = radius * END_OFFSET_NEXT_FACTOR
    end_offset_prev = radius * END_OFFSET_PREV_FACTOR

    def _normalize(vec: Vector) -> Vector | None:
        length = vlength(vec)
        if length < eps:
            return None
        return (vec[0] / length, vec[1] / length)

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
            inward = vscalmul(vadd(vorthogonal(d_prev), vorthogonal(d_next)), sign)
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
            transition_point_next = vadd(
                corner,
                vadd(
                    vscalmul(axis_prev, end_offset_next),
                    vscalmul(axis_next, end_offset_prev),
                ),
            )
            new_arc_start = vadd(corner, vscalmul(axis_prev, prev_clearance))
            new_arc_center = vadd(
                corner,
                vadd(vscalmul(axis_prev, prev_clearance), vscalmul(axis_next, -radius)),
            )
            new_arc_end = vadd(corner, vscalmul(axis_next, prev_clearance))
            new_arc_center_next = vadd(
                corner,
                vadd(vscalmul(axis_next, prev_clearance), vscalmul(axis_prev, -radius)),
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
    overlap_positions: dict[int, int] = {}
    arcs_since_line: list[dict[str, Any]] = []
    line_state: dict[str, Any] | None = None
    current: Point | None = None
    first_right_arcs: list[dict[str, Any]] = []
    capture_first_right_arcs = False
    first_line_active = False
    subpath_start: Point | None = None
    subpath_move_index: int | None = None
    first_line_state: dict[str, Any] | None = None
    first_left_arc_indices: set[int] = set()
    move_targets: dict[int, Point] = {}

    def update_best(line_data: dict[str, Any] | None, candidate: dict[str, Any] | None) -> None:
        if line_data is None or candidate is None:
            return
        best = line_data.get("best")
        if best is None or candidate["score"] < best["score"]:
            line_data["best"] = candidate

    def consider_right_arc(line_data: dict[str, Any] | None, right_arc: dict[str, Any]) -> None:
        if line_data is None or not line_data.get("left_arcs"):
            return
        update_best(line_data, evaluate_candidate(line_data, right_arc))

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

    def record_overlap(candidate: dict[str, Any]) -> None:
        line_idx = candidate["line_index"]
        existing_pos = overlap_positions.get(line_idx)
        if existing_pos is None:
            overlap_positions[line_idx] = len(overlaps)
            overlaps.append(candidate)
        else:
            existing = overlaps[existing_pos]
            if candidate["score"] < existing["score"]:
                overlaps[existing_pos] = candidate

    def finalize_line_state(close_subpath: bool = False) -> None:
        nonlocal line_state, first_line_state
        if (
            close_subpath
            and line_state
            and first_right_arcs
            and subpath_start is not None
        ):
            end = line_state["end"]
            if abs(end[0] - subpath_start[0]) <= eps and abs(end[1] - subpath_start[1]) <= eps:
                wrap_left_arcs = line_state["left_arcs"]
                if first_line_state and wrap_left_arcs:
                    for arc in wrap_left_arcs:
                        idx = arc["index"]
                        if idx not in first_left_arc_indices:
                            first_line_state["left_arcs"].append(arc)
                            first_left_arc_indices.add(idx)
                    for right_arc in first_right_arcs:
                        consider_right_arc(first_line_state, right_arc)
                for right_arc in first_right_arcs:
                    consider_right_arc(line_state, right_arc)
        if line_state:
            best_candidate = line_state.get("best")
            if best_candidate:
                if close_subpath and subpath_move_index is not None:
                    move_targets[subpath_move_index] = best_candidate["point"]
                record_overlap(best_candidate)
        if close_subpath and first_line_state:
            best_candidate = first_line_state.get("best")
            if best_candidate:
                record_overlap(best_candidate)
        if close_subpath:
            first_right_arcs.clear()
            first_line_state = None
            first_left_arc_indices.clear()
        line_state = None

    for index, segment in enumerate(path):
        code = segment[0]
        if code == "M":
            finalize_line_state(close_subpath=True)
            current = (segment[1], segment[2])
            arcs_since_line = []
            subpath_start = current
            subpath_move_index = index
            first_right_arcs.clear()
            first_line_active = False
            capture_first_right_arcs = False
            first_line_state = None
            first_left_arc_indices.clear()
        elif code == "L":
            finalize_line_state()
            start = current if current is not None else (segment[1], segment[2])
            end = (segment[1], segment[2])
            line_state = {
                "index": index,
                "start": start,
                "end": end,
                "left_arcs": arcs_since_line,
                "best": None,
            }
            arcs_since_line = []
            current = end
            if not first_line_active:
                first_line_active = True
                capture_first_right_arcs = True
                first_line_state = line_state
                first_left_arc_indices.clear()
                first_left_arc_indices.update(arc["index"] for arc in line_state["left_arcs"])
            else:
                capture_first_right_arcs = False
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
            if capture_first_right_arcs:
                first_right_arcs.append(arc_info)
            consider_right_arc(line_state, arc_info)
            current = arc_info["end"]
        elif code == "Z":
            finalize_line_state(close_subpath=True)
            current = subpath_start
            arcs_since_line = []
            first_line_active = False
            capture_first_right_arcs = False
            first_line_state = None
            first_left_arc_indices.clear()
        else:
            current = (segment[1], segment[2]) if len(segment) >= 3 else current

    finalize_line_state(close_subpath=True)
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
        skip_indices.update(idx for idx in range(left_idx + 1, right_idx) if idx != line_idx)

    updated_path: PathLike = []
    for idx, segment in enumerate(path):
        if idx in skip_indices:
            continue
        cmd = segment.copy()
        for targets, expected_code in ((move_targets, "M"), (line_targets, "L"), (left_targets, "A")):
            target = targets.get(idx)
            if target is not None and cmd[0] == expected_code:
                cmd[1], cmd[2] = target
        updated_path.append(cmd)

    current_point: Point | None = None
    for segment in updated_path:
        code = segment[0]
        if code in {"M", "L"}:
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
