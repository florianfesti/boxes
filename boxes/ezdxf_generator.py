from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable, Sequence

import ezdxf
from ezdxf import units
from ezdxf.math import Vec3

from boxes.test_path import Test_Path

Command = Sequence[object]


class EZDXFBuilder:
    """Render drawing commands into DXF entities using ezdxf."""

    _POINT_TOL = 1e-6
    _ARC_TOL = 1e-3
    _FULL_CIRCLE_TOL = 1e-2

    def __init__(self, *, layer: str = "0", lineweight: float | None = None) -> None:
        self.doc = ezdxf.new("R2010", setup=True)
        self.doc.units = units.MM
        self.msp = self.doc.modelspace()
        self.layer = layer
        lw_value = self._lineweight_to_hundredths(lineweight) if lineweight is not None else None
        self.entity_attribs = {"layer": layer}
        if lw_value is not None:
            self.entity_attribs["lineweight"] = lw_value

    @staticmethod
    def _lineweight_to_hundredths(value: float) -> int:
        return max(0, int(round(value * 100.0)))

    @staticmethod
    def _vec(x: float, y: float) -> Vec3:
        return Vec3(float(x), float(y), 0.0)

    @staticmethod
    def _evaluate_cubic(p0: Vec3, p1: Vec3, p2: Vec3, p3: Vec3, t: float) -> Vec3:
        mt = 1.0 - t
        return (
            p0 * (mt ** 3)
            + p1 * (3.0 * mt * mt * t)
            + p2 * (3.0 * mt * t * t)
            + p3 * (t ** 3)
        )

    def _approximate_cubic(self, p0: Vec3, p1: Vec3, p2: Vec3, p3: Vec3, steps: int = 16) -> list[Vec3]:
        points = [p0]
        for step in range(1, steps):
            t = step / steps
            points.append(self._evaluate_cubic(p0, p1, p2, p3, t))
        points.append(p3)
        return points

    @staticmethod
    def _line_segment(start: Vec3, end: Vec3) -> dict[str, Vec3]:
        return {"type": "line", "start": start, "end": end}

    @staticmethod
    def _arc_sweep(segment: dict) -> float:
        if segment["orientation"] > 0:
            return segment["end_angle"] - segment["start_angle"]
        return segment["start_angle"] - segment["end_angle"]

    @classmethod
    def _arc_start_point(cls, segment: dict) -> Vec3:
        return cls._point_on_arc(segment["center"], segment["radius"], segment["start_angle"])

    @classmethod
    def _arc_end_point(cls, segment: dict) -> Vec3:
        return cls._point_on_arc(segment["center"], segment["radius"], segment["end_angle"])

    @staticmethod
    def _point_on_arc(center: Vec3, radius: float, angle: float) -> Vec3:
        return Vec3(
            center.x + radius * math.cos(angle),
            center.y + radius * math.sin(angle),
            0.0,
        )

    @classmethod
    def _try_cubic_as_arc(cls, start: Vec3, ctrl1: Vec3, ctrl2: Vec3, end: Vec3):
        span = (end - start).magnitude
        if span <= cls._POINT_TOL:
            return None

        t_start = (ctrl1 - start) * 3.0
        t_end = (end - ctrl2) * 3.0
        det = t_start.x * t_end.y - t_start.y * t_end.x
        if abs(det) <= 1e-8:
            return None

        s_dot = start.x * t_start.x + start.y * t_start.y
        e_dot = end.x * t_end.x + end.y * t_end.y
        cx = (s_dot * t_end.y - e_dot * t_start.y) / det
        cy = (e_dot * t_start.x - s_dot * t_end.x) / det
        center = Vec3(cx, cy, 0.0)

        radius_start = (start - center).magnitude
        radius_end = (end - center).magnitude
        if radius_start <= cls._POINT_TOL:
            return None
        if abs(radius_start - radius_end) > max(radius_start, 1.0) * 1e-3:
            return None

        if abs((start - center).dot(t_start)) > max(radius_start, 1.0) * 1e-3:
            return None
        if abs((end - center).dot(t_end)) > max(radius_start, 1.0) * 1e-3:
            return None

        max_dev = 0.0
        for t in (0.25, 0.5, 0.75):
            point = cls._evaluate_cubic(start, ctrl1, ctrl2, end, t)
            deviation = abs((point - center).magnitude - radius_start)
            max_dev = max(max_dev, deviation)
        if max_dev > max(radius_start, 1.0) * cls._ARC_TOL:
            return None

        r0 = start - center
        r1 = end - center
        cross = r0.x * r1.y - r0.y * r1.x
        if abs(cross) <= max(radius_start, 1.0) * 1e-6:
            return None
        orientation = 1 if cross > 0 else -1

        start_angle = math.atan2(r0.y, r0.x)
        end_angle = math.atan2(r1.y, r1.x)
        if orientation > 0:
            while end_angle <= start_angle:
                end_angle += 2.0 * math.pi
        else:
            while end_angle >= start_angle:
                end_angle -= 2.0 * math.pi

        sweep = abs(end_angle - start_angle)
        if sweep <= 1e-3:
            return None

        full_circle = (
            (end - start).magnitude <= max(radius_start, 1.0) * 1e-3
            and abs(sweep - 2.0 * math.pi) <= cls._FULL_CIRCLE_TOL
        )
        return {
            "type": "arc",
            "center": center,
            "radius": radius_start,
            "start_angle": start_angle,
            "end_angle": end_angle,
            "orientation": orientation,
            "start": start,
            "end": end,
            "full_circle": full_circle,
        }

    def _segments_form_circle(self, segments: list[dict]) -> dict | None:
        if not segments:
            return None
        if len(segments) == 1 and segments[0]["type"] == "arc" and segments[0]["full_circle"]:
            arc = segments[0]
            return {"center": arc["center"], "radius": arc["radius"]}
        if any(seg["type"] != "arc" for seg in segments):
            return None
        center = segments[0]["center"]
        radius = segments[0]["radius"]
        orientation = segments[0]["orientation"]
        tol = max(radius, 1.0) * self._ARC_TOL
        sweep = 0.0
        start_point = segments[0]["start"]
        prev_end = start_point
        for seg in segments:
            if seg["orientation"] != orientation:
                return None
            if (seg["center"] - center).magnitude > tol:
                return None
            if abs(seg["radius"] - radius) > tol:
                return None
            if (seg["start"] - prev_end).magnitude > tol:
                return None
            sweep += self._arc_sweep(seg)
            prev_end = seg["end"]
        if (prev_end - start_point).magnitude > tol:
            return None
        if abs(abs(sweep) - 2.0 * math.pi) > self._FULL_CIRCLE_TOL:
            return None
        return {"center": center, "radius": radius}

    def _emit_circle(self, center: Vec3, radius: float) -> None:
        self.msp.add_circle(
            (center.x, center.y),
            radius,
            dxfattribs=self.entity_attribs,
        )

    def _emit_polyline(self, segments: list[dict]) -> None:
        if not segments:
            return
        vertices: list[list[float]] = []
        tol = self._POINT_TOL

        def add_vertex(point: Vec3, bulge: float) -> None:
            if vertices:
                last = Vec3(vertices[-1][0], vertices[-1][1], 0.0)
                if (point - last).magnitude <= tol:
                    vertices[-1][2] = bulge
                    return
            vertices.append([point.x, point.y, bulge])

        for idx, seg in enumerate(segments):
            if seg["type"] == "line":
                start = seg["start"]
                end = seg["end"]
                if (end - start).magnitude <= tol:
                    continue
                if not vertices:
                    add_vertex(start, 0.0)
                vertices[-1][2] = 0.0
                add_vertex(end, 0.0)
            elif seg["type"] == "arc":
                start = seg["start"]
                end = seg["end"]
                if (end - start).magnitude <= tol and not seg["full_circle"]:
                    continue
                if not vertices:
                    add_vertex(start, 0.0)
                sweep = self._arc_sweep(seg)
                bulge = math.tan(abs(sweep) / 4.0)
                if seg["orientation"] < 0:
                    bulge = -bulge
                vertices[-1][2] = bulge
                add_vertex(end, 0.0)
            else:
                raise ValueError(f"Unsupported segment type in polyline: {seg['type']}")

        if len(vertices) < 2:
            return
        start_pt = Vec3(vertices[0][0], vertices[0][1], 0.0)
        end_pt = Vec3(vertices[-1][0], vertices[-1][1], 0.0)
        is_closed = (end_pt - start_pt).magnitude <= tol
        if is_closed:
            vertices.pop()  # closing flag already handles closing edge

        self.msp.add_lwpolyline(
            [tuple(v) for v in vertices],
            format="xyb",
            close=is_closed,
            dxfattribs=self.entity_attribs,
        )

    def _emit_texts(self, texts: list[tuple]) -> None:
        if not texts:
            return
        align_map = {
            "left": "LEFT",
            "middle": "CENTER",
            "end": "RIGHT",
        }
        for x, y, text, params in texts:
            if not text:
                continue
            height = float(params.get("fs", 2.0))
            alignment = align_map.get(params.get("align", "left"), "LEFT")
            text_entity = self.msp.add_text(
                text,
                dxfattribs={
                    "height": height,
                    "layer": self.layer,
                },
            )
            text_entity.dxf.insert = (x, y, 0.0)
            if alignment != "LEFT":
                halign_codes = {"CENTER": 1, "RIGHT": 2}
                text_entity.dxf.halign = halign_codes.get(alignment, 0)
                text_entity.dxf.align_point = (x, y, 0.0)

    def _flush_block(self, segments: list[dict], texts: list[tuple]) -> None:
        if not segments:
            self._emit_texts(texts)
            return
        circle = self._segments_form_circle(segments)
        if circle:
            self._emit_circle(circle["center"], circle["radius"])
        else:
            self._emit_polyline(segments)
        self._emit_texts(texts)

    def add_commands(self, commands: Iterable[Command]) -> None:
        current_point: Vec3 | None = None
        segments: list[dict] = []
        texts: list[tuple] = []

        def flush():
            self._flush_block(segments, texts)
            segments.clear()
            texts.clear()

        for cmd in commands:
            if not cmd:
                continue
            letter = cmd[0]
            if letter == "M":
                flush()
                current_point = self._vec(cmd[1], cmd[2])
            elif letter == "L":
                if current_point is None:
                    raise ValueError("Line command without a starting point.")
                end_point = self._vec(cmd[1], cmd[2])
                if (end_point - current_point).magnitude > self._POINT_TOL:
                    segments.append(self._line_segment(current_point, end_point))
                current_point = end_point
            elif letter == "C":
                if current_point is None:
                    raise ValueError("Cubic command without a starting point.")
                end_point = self._vec(cmd[1], cmd[2])
                ctrl1 = self._vec(cmd[3], cmd[4])
                ctrl2 = self._vec(cmd[5], cmd[6])
                arc = self._try_cubic_as_arc(current_point, ctrl1, ctrl2, end_point)
                if arc:
                    segments.append(arc)
                else:
                    points = self._approximate_cubic(current_point, ctrl1, ctrl2, end_point)
                    for idx in range(1, len(points)):
                        start = points[idx - 1]
                        end = points[idx]
                        if (end - start).magnitude > self._POINT_TOL:
                            segments.append(self._line_segment(start, end))
                current_point = end_point
            elif letter == "A":
                if current_point is None:
                    raise ValueError("Arc command without a starting point.")
                end_point = self._vec(cmd[1], cmd[2])
                center = self._vec(cmd[3], cmd[4])
                radius = abs(float(cmd[5]))
                start_angle = math.atan2(current_point.y - center.y, current_point.x - center.x)
                end_angle = math.atan2(end_point.y - center.y, end_point.x - center.x)
                orientation = int(cmd[8])
                if orientation > 0:
                    while end_angle <= start_angle:
                        end_angle += 2.0 * math.pi
                else:
                    while end_angle >= start_angle:
                        end_angle -= 2.0 * math.pi

                sweep_param = float(cmd[7]) - float(cmd[6])
                if orientation < 0:
                    sweep_param = -sweep_param
                is_full_circle = (
                    math.hypot(end_point.x - current_point.x, end_point.y - current_point.y) <= 1e-4
                    and math.isclose(abs(sweep_param), 2.0 * math.pi, rel_tol=1e-6)
                )
                segments.append(
                    {
                        "type": "arc",
                        "center": center,
                        "radius": radius,
                        "start_angle": start_angle,
                        "end_angle": end_angle,
                        "orientation": orientation if orientation != 0 else 1,
                        "start": current_point,
                        "end": end_point,
                        "full_circle": is_full_circle,
                    }
                )
                current_point = end_point
            elif letter == "T":
                x, y = float(cmd[1]), float(cmd[2])
                text = cmd[4]
                params = cmd[5] if len(cmd) > 5 else {}
                texts.append((x, y, text, params))
            else:
                raise ValueError(f"Unsupported drawing command: {letter}")

        flush()

    def save(self, output: str | Path) -> Path:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.doc.saveas(output_path)
        return output_path


def export_test_path_ezdxf(output: str | Path = "test_path_ezdxf.dxf") -> Path:
    builder = EZDXFBuilder(lineweight=0.1)
    builder.add_commands(Test_Path)
    return builder.save(output)


if __name__ == "__main__":
    export_test_path_ezdxf()
