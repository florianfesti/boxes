from __future__ import annotations

import io
import math
from typing import Any, Sequence

from .drawing import EPS, Surface, points_equal

__all__ = ["DXFSurface"]


class DXFSurface(Surface):
    """Surface capable of turning drawing commands into a DXF byte stream."""

    scale = 1.0
    invert_y = False

    def finish(self, inner_corners: str = "loop", dogbone_radius=None):
        extents = self.prepare_paths(inner_corners, dogbone_radius)
        entities: list[str] = []
        for part in self.parts:
            if not part.pathes:
                continue
            for path in part.pathes:
                entities.extend(self._entities_from_path(path.path))

        return self._build_dxf(extents, entities)

    @staticmethod
    def _pair(container: list[str], code: int, value: Any) -> None:
        container.append(f"{code:>3}")
        container.append(str(value))

    @staticmethod
    def _format_angle(angle_deg: float) -> float:
        angle = angle_deg % 360.0
        if math.isclose(angle, 360.0, abs_tol=1e-9):
            angle = 0.0
        return angle

    def _entities_from_path(self, commands):
        entities: list[str] = []
        current: tuple[float, float] | None = None
        pending_arc: dict[str, Any] | None = None
        sweep_tol = 1e-4
        circle_sweep = 2.0 * math.pi

        def flush_pending_arc() -> None:
            nonlocal pending_arc
            if not pending_arc:
                return
            emit_arc_entity(
                pending_arc["center"],
                pending_arc["radius"],
                pending_arc["start_angle"],
                pending_arc["end_angle"],
                pending_arc["orientation"],
            )
            pending_arc = None

        def emit_arc_entity(
            center: tuple[float, float],
            radius: float,
            start_angle: float,
            end_angle: float,
            orientation: int,
        ) -> None:
            if orientation < 0:
                start_angle, end_angle = end_angle, start_angle
            start_deg = self._format_angle(math.degrees(start_angle))
            end_deg = self._format_angle(math.degrees(end_angle))
            entities.extend(
                self._arc_entity(center, radius, start_deg, end_deg)
            )

        def process_arc_segment(
            start_point: tuple[float, float],
            end_point: tuple[float, float],
            center: tuple[float, float],
            radius: float,
            start_angle_rad: float,
            end_angle_rad: float,
            orientation: int,
        ) -> None:
            nonlocal pending_arc
            if radius <= EPS:
                flush_pending_arc()
                return
            orient = 1 if orientation >= 0 else -1
            start_angle, end_angle = self._normalize_arc_angles(
                float(start_angle_rad), float(end_angle_rad), orient
            )
            sweep = end_angle - start_angle if orient > 0 else start_angle - end_angle
            if sweep <= 1e-9:
                flush_pending_arc()
                return
            segment = {
                "center": center,
                "radius": abs(radius),
                "orientation": orient,
                "start_angle": start_angle,
                "end_angle": end_angle,
                "start_point": start_point,
                "end_point": end_point,
                "sweep": sweep,
            }
            if points_equal(start_point[0], start_point[1], end_point[0], end_point[1]) and abs(
                sweep - circle_sweep
            ) <= sweep_tol:
                flush_pending_arc()
                entities.extend(self._circle_entity(center, abs(radius)))
                return

            if pending_arc:
                same_orientation = orient == pending_arc["orientation"]
                same_radius = abs(segment["radius"] - pending_arc["radius"]) <= 1e-4
                center_dx = segment["center"][0] - pending_arc["center"][0]
                center_dy = segment["center"][1] - pending_arc["center"][1]
                same_center = math.hypot(center_dx, center_dy) <= 1e-4
                contiguous = points_equal(
                    pending_arc["end_point"][0],
                    pending_arc["end_point"][1],
                    start_point[0],
                    start_point[1],
                )
                if same_orientation and same_radius and same_center and contiguous:
                    predicted_sweep = pending_arc["total_sweep"] + sweep
                    if predicted_sweep > circle_sweep + sweep_tol:
                        flush_pending_arc()
                    else:
                        pending_arc["total_sweep"] = predicted_sweep
                        pending_arc["end_point"] = end_point
                        pending_arc["end_angle"] = segment["end_angle"]
                        if (
                            points_equal(
                                pending_arc["start_point"][0],
                                pending_arc["start_point"][1],
                                end_point[0],
                                end_point[1],
                            )
                            and abs(predicted_sweep - circle_sweep) <= sweep_tol
                        ):
                            entities.extend(self._circle_entity(center, abs(radius)))
                            pending_arc = None
                        return
                else:
                    flush_pending_arc()

            pending_arc = {
                "center": segment["center"],
                "radius": segment["radius"],
                "orientation": segment["orientation"],
                "total_sweep": segment["sweep"],
                "start_angle": segment["start_angle"],
                "end_angle": segment["end_angle"],
                "start_point": start_point,
                "end_point": end_point,
            }

        for cmd in commands:
            letter = cmd[0]
            if letter == "M":
                flush_pending_arc()
                current = (cmd[1], cmd[2])
            elif letter == "L":
                flush_pending_arc()
                target = (cmd[1], cmd[2])
                if current and not points_equal(current[0], current[1], target[0], target[1]):
                    entities.extend(self._line_entity(current, target))
                current = target
            elif letter == "C":
                if current is None:
                    current = (cmd[1], cmd[2])
                    continue
                arc = self._cubic_to_arc(current, cmd)
                if arc:
                    center, radius, start_angle_deg, end_angle_deg, is_full_circle = arc
                    if is_full_circle:
                        flush_pending_arc()
                        entities.extend(self._circle_entity(center, radius))
                    else:
                        process_arc_segment(
                            current,
                            (cmd[1], cmd[2]),
                            center,
                            radius,
                            math.radians(start_angle_deg),
                            math.radians(end_angle_deg),
                            1,
                        )
                    current = (cmd[1], cmd[2])
                    continue
                flush_pending_arc()
                control1 = (cmd[3], cmd[4])
                control2 = (cmd[5], cmd[6])
                end_point = (cmd[1], cmd[2])
                prev = current
                for point in self._approximate_cubic(current, control1, control2, end_point):
                    if not points_equal(prev[0], prev[1], point[0], point[1]):
                        entities.extend(self._line_entity(prev, point))
                    prev = point
                current = end_point
            elif letter == "A":
                if current is None:
                    current = (cmd[1], cmd[2])
                end_point = (cmd[1], cmd[2])
                center = (cmd[3], cmd[4])
                radius = cmd[5]
                start_angle_rad = float(cmd[6])
                end_angle_rad = float(cmd[7])
                orientation = cmd[8]
                if radius > EPS:
                    process_arc_segment(
                        current,
                        end_point,
                        center,
                        radius,
                        start_angle_rad,
                        end_angle_rad,
                        orientation,
                    )
                current = end_point
            elif letter == "T":
                flush_pending_arc()
                text_entities = self._text_entity(cmd)
                if text_entities:
                    entities.extend(text_entities)
        flush_pending_arc()
        return entities

    def _line_entity(self, start, end):
        if points_equal(start[0], start[1], end[0], end[1]):
            return []
        items: list[str] = []
        self._pair(items, 0, "LINE")
        self._pair(items, 8, "0")
        self._pair(items, 10, f"{start[0]:.6f}")
        self._pair(items, 20, f"{start[1]:.6f}")
        self._pair(items, 30, "0.0")
        self._pair(items, 11, f"{end[0]:.6f}")
        self._pair(items, 21, f"{end[1]:.6f}")
        self._pair(items, 31, "0.0")
        return items

    def _arc_entity(self, center, radius, start_angle, end_angle):
        items: list[str] = []
        self._pair(items, 0, "ARC")
        self._pair(items, 8, "0")
        self._pair(items, 10, f"{center[0]:.6f}")
        self._pair(items, 20, f"{center[1]:.6f}")
        self._pair(items, 30, "0.0")
        self._pair(items, 40, f"{abs(radius):.6f}")
        self._pair(items, 50, f"{start_angle:.6f}")
        self._pair(items, 51, f"{end_angle:.6f}")
        return items

    def _circle_entity(self, center, radius):
        items: list[str] = []
        self._pair(items, 0, "CIRCLE")
        self._pair(items, 8, "0")
        self._pair(items, 10, f"{center[0]:.6f}")
        self._pair(items, 20, f"{center[1]:.6f}")
        self._pair(items, 30, "0.0")
        self._pair(items, 40, f"{abs(radius):.6f}")
        return items

    @staticmethod
    def _normalize_vector(dx: float, dy: float) -> tuple[float, float] | None:
        length = math.hypot(dx, dy)
        if length <= EPS:
            return None
        return dx / length, dy / length

    @staticmethod
    def _rotate_vector(vec: tuple[float, float], orientation: int) -> tuple[float, float]:
        x, y = vec
        return (-y, x) if orientation > 0 else (y, -x)

    @staticmethod
    def _cross(a: tuple[float, float], b: tuple[float, float]) -> float:
        return a[0] * b[1] - a[1] * b[0]

    def _line_intersection_params(
        self,
        origin_a: tuple[float, float],
        dir_a: tuple[float, float],
        origin_b: tuple[float, float],
        dir_b: tuple[float, float],
    ) -> tuple[float, float, tuple[float, float]] | None:
        det = self._cross(dir_a, dir_b)
        if abs(det) <= 1e-9:
            return None
        diff = (origin_b[0] - origin_a[0], origin_b[1] - origin_a[1])
        u = self._cross(diff, dir_b) / det
        v = self._cross(diff, dir_a) / det
        center = (
            origin_a[0] + u * dir_a[0],
            origin_a[1] + u * dir_a[1],
        )
        return u, v, center

    @staticmethod
    def _evaluate_cubic(
        start: tuple[float, float],
        ctrl1: tuple[float, float],
        ctrl2: tuple[float, float],
        end: tuple[float, float],
        t: float,
    ) -> tuple[float, float]:
        mt = 1.0 - t
        x = (
            mt * mt * mt * start[0]
            + 3 * mt * mt * t * ctrl1[0]
            + 3 * mt * t * t * ctrl2[0]
            + t * t * t * end[0]
        )
        y = (
            mt * mt * mt * start[1]
            + 3 * mt * mt * t * ctrl1[1]
            + 3 * mt * t * t * ctrl2[1]
            + t * t * t * end[1]
        )
        return x, y

    @staticmethod
    def _normalize_arc_angles(start_angle: float, end_angle: float, orientation: int) -> tuple[float, float]:
        if orientation > 0:
            while end_angle <= start_angle + 1e-9:
                end_angle += 2.0 * math.pi
        else:
            while end_angle >= start_angle - 1e-9:
                end_angle -= 2.0 * math.pi
        return start_angle, end_angle

    def _cubic_to_arc(self, start: tuple[float, float], cmd: Sequence[float]) -> tuple[tuple[float, float], float, float, float, bool] | None:
        end = (cmd[1], cmd[2])
        ctrl1 = (cmd[3], cmd[4])
        ctrl2 = (cmd[5], cmd[6])

        tangent_start = self._normalize_vector(ctrl1[0] - start[0], ctrl1[1] - start[1])
        tangent_end = self._normalize_vector(end[0] - ctrl2[0], end[1] - ctrl2[1])
        if tangent_start is None or tangent_end is None:
            return None

        for orientation in (1, -1):
            normal_start = self._rotate_vector(tangent_start, orientation)
            normal_end = self._rotate_vector(tangent_end, orientation)
            intersection = self._line_intersection_params(start, normal_start, end, normal_end)
            if intersection is None:
                continue
            u, v, center = intersection
            if u <= EPS or v <= EPS:
                continue
            radius_start = math.hypot(center[0] - start[0], center[1] - start[1])
            radius_end = math.hypot(center[0] - end[0], center[1] - end[1])
            if radius_start <= EPS or abs(radius_start - radius_end) > max(1.0, radius_start) * 1e-3:
                continue
            dot_start = (center[0] - start[0]) * normal_start[0] + (center[1] - start[1]) * normal_start[1]
            dot_end = (center[0] - end[0]) * normal_end[0] + (center[1] - end[1]) * normal_end[1]
            if dot_start < 0 or dot_end < 0:
                continue
            start_vec = (start[0] - center[0], start[1] - center[1])
            end_vec = (end[0] - center[0], end[1] - center[1])
            cross = self._cross(start_vec, end_vec)
            actual_orientation = 1 if cross > 0 else -1 if cross < 0 else 0
            if actual_orientation == 0 or actual_orientation != orientation:
                continue
            start_angle = math.atan2(start_vec[1], start_vec[0])
            end_angle = math.atan2(end_vec[1], end_vec[0])
            start_angle, end_angle = self._normalize_arc_angles(start_angle, end_angle, orientation)
            midpoint = self._evaluate_cubic(start, ctrl1, ctrl2, end, 0.5)
            radius_mid = math.hypot(midpoint[0] - center[0], midpoint[1] - center[1])
            if abs(radius_mid - radius_start) > max(1.0, radius_start) * 5e-4:
                continue
            sweep = end_angle - start_angle if orientation > 0 else start_angle - end_angle
            is_full_circle = (
                points_equal(start[0], start[1], end[0], end[1])
                and math.isclose(abs(sweep), 2.0 * math.pi, abs_tol=1e-6)
            )
            if orientation < 0:
                start_angle, end_angle = end_angle, start_angle
            start_angle_deg = math.degrees(start_angle)
            end_angle_deg = math.degrees(end_angle)
            start_angle_deg = self._format_angle(start_angle_deg)
            end_angle_deg = self._format_angle(end_angle_deg)
            return center, radius_start, start_angle_deg, end_angle_deg, is_full_circle
        return None

    def _text_entity(self, cmd):
        _, x, y, _m, text, params = cmd
        if not text:
            return []
        height = params.get("fs", 10.0)
        items: list[str] = []
        self._pair(items, 0, "TEXT")
        self._pair(items, 8, "0")
        self._pair(items, 10, f"{x:.6f}")
        self._pair(items, 20, f"{y:.6f}")
        self._pair(items, 30, "0.0")
        self._pair(items, 40, f"{height:.6f}")
        self._pair(items, 1, text)
        return items

    def _approximate_cubic(self, p0, p1, p2, p3, steps=12):
        result: list[tuple[float, float]] = []
        for step in range(1, steps + 1):
            t = step / steps
            mt = 1.0 - t
            x = (
                mt * mt * mt * p0[0]
                + 3 * mt * mt * t * p1[0]
                + 3 * mt * t * t * p2[0]
                + t * t * t * p3[0]
            )
            y = (
                mt * mt * mt * p0[1]
                + 3 * mt * mt * t * p1[1]
                + 3 * mt * t * t * p2[1]
                + t * t * t * p3[1]
            )
            result.append((x, y))
        return result

    def _build_dxf(self, extents, entities):
        lines: list[str] = []

        def add(code: int, value: Any) -> None:
            self._pair(lines, code, value)

        add(0, "SECTION")
        add(2, "HEADER")
        add(9, "$ACADVER")
        add(1, "AC1009")
        add(9, "$INSUNITS")
        add(70, 4)
        add(9, "$MEASUREMENT")
        add(70, 1)
        add(9, "$EXTMIN")
        add(10, f"{extents.xmin:.6f}")
        add(20, f"{extents.ymin:.6f}")
        add(30, "0.0")
        add(9, "$EXTMAX")
        add(10, f"{extents.xmax:.6f}")
        add(20, f"{extents.ymax:.6f}")
        add(30, "0.0")
        add(0, "ENDSEC")

        add(0, "SECTION")
        add(2, "TABLES")
        add(0, "TABLE")
        add(2, "LAYER")
        add(70, 1)
        add(0, "LAYER")
        add(2, "0")
        add(70, 0)
        add(62, 7)
        add(6, "CONTINUOUS")
        add(0, "ENDTAB")
        add(0, "ENDSEC")

        add(0, "SECTION")
        add(2, "ENTITIES")
        lines.extend(entities)
        add(0, "ENDSEC")

        add(0, "SECTION")
        add(2, "BLOCKS")
        add(0, "ENDSEC")

        add(0, "SECTION")
        add(2, "OBJECTS")
        add(0, "ENDSEC")
        add(0, "EOF")

        data = ("\r\n".join(lines) + "\r\n").encode("ascii", "ignore")
        buffer = io.BytesIO(data)
        buffer.seek(0)
        return buffer
