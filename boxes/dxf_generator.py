from __future__ import annotations

import io
import logging
import math
from typing import Any, Iterable, Literal, Sequence, TypedDict, cast

import ezdxf
from ezdxf import units
from ezdxf.math import Vec3
from .drawing import Surface

Command = Sequence[object]

__all__ = ["EZDXFBuilder", "DXFSurface"]


_ezdxf_logger = logging.getLogger("ezdxf")
_ezdxf_logger.setLevel(logging.ERROR)
_ezdxf_logger.propagate = False


class LineSegment(TypedDict):
    type: Literal["line"]
    start: Vec3
    end: Vec3


class ArcSegment(TypedDict):
    type: Literal["arc"]
    center: Vec3
    radius: float
    start_angle: float
    end_angle: float
    orientation: int
    start: Vec3
    end: Vec3
    full_circle: bool


class CircleSummary(TypedDict):
    center: Vec3
    radius: float


Segment = LineSegment | ArcSegment
TextParams = dict[str, Any]
TextSpec = tuple[float, float, str, TextParams]


class EZDXFBuilder:
    """Render drawing commands into DXF entities using ezdxf."""

    _POINT_TOL = 1e-6
    _ARC_TOL = 1e-3
    _FULL_CIRCLE_TOL = 1e-2

    def __init__(self, *, layer: str = "0", lineweight: float | None = None) -> None:
        self.doc = ezdxf.new("R2010", setup=True)
        self.doc.units = units.MM
        self.doc.header["$INSUNITS"] = units.MM
        self.doc.header["$MEASUREMENT"] = 1
        self.msp = self.doc.modelspace()
        self.layer = layer
        lw_value = self._lineweight_to_hundredths(lineweight) if lineweight is not None else None
        self.entity_attribs = {"layer": layer}
        if lw_value is not None:
            self.entity_attribs["lineweight"] = lw_value

    def set_lineweight(self, value: float | None) -> None:
        """Update the current entity lineweight in hundredths of millimeters."""
        if value is None or value <= 0.0:
            self.entity_attribs.pop("lineweight", None)
            return
        self.entity_attribs["lineweight"] = self._lineweight_to_hundredths(value)

    def set_extents(self, xmin: float, ymin: float, xmax: float, ymax: float) -> None:
        """Write drawing extents to the DXF header."""
        self.doc.header["$EXTMIN"] = (float(xmin), float(ymin), 0.0)
        self.doc.header["$EXTMAX"] = (float(xmax), float(ymax), 0.0)

    def to_buffer(self) -> io.BytesIO:
        """Return the DXF document encoded into an in-memory buffer."""
        stream = io.StringIO()
        self.doc.write(stream)
        data = self.doc.encode(stream.getvalue())
        buffer = io.BytesIO(data)
        buffer.seek(0)
        return buffer

    @staticmethod
    def _lineweight_to_hundredths(value: float) -> int:
        hundredths = int(round(value * 100.0))
        return min(211, max(0, hundredths))

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
    def _line_segment(start: Vec3, end: Vec3) -> LineSegment:
        return {"type": "line", "start": start, "end": end}

    def _points_close(self, a: Vec3, b: Vec3, *, tol: float | None = None) -> bool:
        threshold = self._POINT_TOL if tol is None else tol
        return (a - b).magnitude <= threshold

    def _vectors_collinear(
        self, v1: Vec3, v2: Vec3, *, tol: float | None = None, allow_reverse: bool = False
    ) -> bool:
        threshold = self._POINT_TOL if tol is None else tol
        len1 = v1.magnitude
        len2 = v2.magnitude
        if len1 <= threshold or len2 <= threshold:
            return True
        cross = abs(v1.x * v2.y - v1.y * v2.x)
        max_len = max(len1, len2, 1e-9)
        if cross > threshold * max_len:
            return False
        norm = len1 * len2
        if norm <= threshold * threshold:
            return True
        cosine = v1.dot(v2) / norm
        angle_tol = min(1e-6, threshold / max_len)
        if allow_reverse:
            return abs(cosine) >= 1.0 - angle_tol
        return cosine >= -angle_tol

    def _merge_line_run_once(self, run: Sequence[LineSegment]) -> tuple[list[LineSegment], bool]:
        if not run:
            return [], False
        merged: list[LineSegment] = []
        tol = self._POINT_TOL
        changed = False
        for segment in run:
            start = segment["start"]
            end = segment["end"]
            if (end - start).magnitude <= tol:
                changed = True
                continue
            if merged:
                prev = merged[-1]
                v_prev = prev["end"] - prev["start"]
                v_curr = end - start
                tol_vec = max(v_prev.magnitude, v_curr.magnitude, 1.0) * self._POINT_TOL
                if self._points_close(prev["end"], start, tol=tol_vec):
                    if self._vectors_collinear(v_prev, v_curr, tol=tol_vec):
                        merged[-1] = self._line_segment(prev["start"], end)
                        changed = True
                        continue
            merged.append(self._line_segment(start, end))

        if len(merged) <= 1:
            return merged, changed

        first = merged[0]
        last = merged[-1]
        v_first = first["end"] - first["start"]
        v_last = last["end"] - last["start"]
        tol_vec = max(v_first.magnitude, v_last.magnitude, 1.0) * self._POINT_TOL
        share_both = (
            (
                self._points_close(first["start"], last["start"], tol=tol_vec)
                and self._points_close(first["end"], last["end"], tol=tol_vec)
            )
            or (
                self._points_close(first["start"], last["end"], tol=tol_vec)
                and self._points_close(first["end"], last["start"], tol=tol_vec)
            )
        )
        if share_both:
            merged.pop()
            changed = True
            return merged, changed
        if self._points_close(first["start"], last["end"], tol=tol_vec):
            if (
                v_first.magnitude > tol
                and v_last.magnitude > tol
                and self._vectors_collinear(v_last, v_first, tol=tol_vec, allow_reverse=True)
            ):
                merged[0] = self._line_segment(last["start"], first["end"])
                merged.pop()
                changed = True
        elif self._points_close(first["end"], last["start"], tol=tol_vec):
            if (
                v_first.magnitude > tol
                and v_last.magnitude > tol
                and self._vectors_collinear(v_first, v_last, tol=tol_vec, allow_reverse=True)
            ):
                merged[-1] = self._line_segment(first["start"], last["end"])
                merged.pop(0)
                changed = True
        return merged, changed

    def _merge_line_run(self, run: Sequence[LineSegment]) -> tuple[list[LineSegment], bool]:
        current = list(run)
        overall_changed = False
        while True:
            current, changed = self._merge_line_run_once(current)
            overall_changed = overall_changed or changed
            if not changed:
                break
        return current, overall_changed

    def _merge_line_segments_once(self, segments: Sequence[Segment]) -> tuple[list[Segment], bool]:
        merged: list[Segment] = []
        line_run: list[LineSegment] = []
        changed = False

        def flush_run() -> None:
            nonlocal changed
            if not line_run:
                return
            merged_run, run_changed = self._merge_line_run(line_run)
            if run_changed:
                changed = True
            merged.extend(merged_run)
            line_run.clear()

        for segment in segments:
            if segment["type"] == "line":
                line_run.append(cast(LineSegment, segment))
            else:
                flush_run()
                merged.append(segment)
        flush_run()
        return merged, changed

    def _merge_line_segments(self, segments: Sequence[Segment]) -> list[Segment]:
        if not segments:
            return []
        merged, changed = self._merge_line_segments_once(segments)
        if len(merged) >= 2 and merged[0]["type"] == "line" and merged[-1]["type"] == "line":
            first = cast(LineSegment, merged[0])
            last = cast(LineSegment, merged[-1])
            v_first = first["end"] - first["start"]
            v_last = last["end"] - last["start"]
            tol_vec = max(v_first.magnitude, v_last.magnitude, 1.0) * self._POINT_TOL
            same_direction = self._points_close(first["start"], last["start"], tol=tol_vec) and self._points_close(
                first["end"], last["end"], tol=tol_vec
            )
            opposite_direction = self._points_close(first["start"], last["end"], tol=tol_vec) and self._points_close(
                first["end"], last["start"], tol=tol_vec
            )
            if same_direction or opposite_direction:
                merged = list(merged[:-1])
                return self._merge_line_segments(merged)
            if self._points_close(first["start"], last["end"], tol=tol_vec) and self._vectors_collinear(
                v_last, v_first, tol=tol_vec, allow_reverse=True
            ):
                new_seg = self._line_segment(last["start"], first["end"])
                if not self._points_close(new_seg["start"], new_seg["end"], tol=tol_vec):
                    merged = [new_seg] + list(merged[1:-1])
                else:
                    merged = list(merged[1:-1])
                return self._merge_line_segments(merged)
            if self._points_close(first["end"], last["start"], tol=tol_vec) and self._vectors_collinear(
                v_first, v_last, tol=tol_vec, allow_reverse=True
            ):
                new_seg = self._line_segment(first["start"], last["end"])
                if not self._points_close(new_seg["start"], new_seg["end"], tol=tol_vec):
                    merged = [new_seg] + list(merged[1:-1])
                else:
                    merged = list(merged[1:-1])
                return self._merge_line_segments(merged)
        if not changed:
            return merged
        return self._merge_line_segments(merged)

    def _merge_arc_segments(self, segments: Sequence[Segment]) -> list[Segment]:
        merged: list[Segment] = []
        pending: ArcSegment | None = None
        pending_start_angle = 0.0
        sweep_acc = 0.0

        def start_pending(arc: ArcSegment) -> None:
            nonlocal pending, pending_start_angle, sweep_acc
            pending = self._arc_segment(
                center=arc["center"],
                radius=arc["radius"],
                start_angle=arc["start_angle"],
                end_angle=arc["end_angle"],
                orientation=arc["orientation"],
                start=arc["start"],
                end=arc["end"],
                full_circle=arc["full_circle"],
            )
            pending_start_angle = arc["start_angle"]
            sweep_acc = self._arc_sweep(arc)

        def flush_pending() -> None:
            nonlocal pending, sweep_acc, pending_start_angle
            if pending is None:
                return
            tol = max(pending["radius"], 1.0) * self._ARC_TOL
            if (
                not pending["full_circle"]
                and self._points_close(pending["start"], pending["end"], tol=tol)
                and abs(sweep_acc - 2.0 * math.pi) <= self._FULL_CIRCLE_TOL
            ):
                pending = self._arc_segment(
                    center=pending["center"],
                    radius=pending["radius"],
                    start_angle=pending["start_angle"],
                    end_angle=pending["end_angle"],
                    orientation=pending["orientation"],
                    start=pending["start"],
                    end=pending["end"],
                    full_circle=True,
                )
            pending_start_angle = 0.0
            merged.append(pending)
            pending = None
            sweep_acc = 0.0

        for segment in segments:
            if segment["type"] != "arc":
                flush_pending()
                merged.append(segment)
                continue

            arc = cast(ArcSegment, segment)
            if arc["full_circle"]:
                flush_pending()
                merged.append(
                    self._arc_segment(
                        center=arc["center"],
                        radius=arc["radius"],
                        start_angle=arc["start_angle"],
                        end_angle=arc["end_angle"],
                        orientation=arc["orientation"],
                        start=arc["start"],
                        end=arc["end"],
                        full_circle=True,
                    )
                )
                continue

            if pending is None:
                start_pending(arc)
                continue

            tol = max(pending["radius"], arc["radius"], 1.0) * self._ARC_TOL
            centers_close = (arc["center"] - pending["center"]).magnitude <= tol
            radii_close = abs(arc["radius"] - pending["radius"]) <= tol
            contiguous = self._points_close(pending["end"], arc["start"], tol=tol)
            same_orientation = arc["orientation"] == pending["orientation"]
            next_sweep = sweep_acc + self._arc_sweep(arc)

            if (
                centers_close
                and radii_close
                and contiguous
                and same_orientation
                and next_sweep <= 2.0 * math.pi + self._FULL_CIRCLE_TOL
            ):
                sweep_acc = next_sweep
                orientation = pending["orientation"]
                if orientation > 0:
                    end_angle = pending_start_angle + sweep_acc
                else:
                    end_angle = pending_start_angle - sweep_acc
                pending = self._arc_segment(
                    center=pending["center"],
                    radius=pending["radius"],
                    start_angle=pending_start_angle,
                    end_angle=end_angle,
                    orientation=orientation,
                    start=pending["start"],
                    end=arc["end"],
                    full_circle=pending["full_circle"] or arc["full_circle"],
                )
                continue

            flush_pending()
            start_pending(arc)

        flush_pending()
        return merged

    @staticmethod
    def _arc_segment(
        *,
        center: Vec3,
        radius: float,
        start_angle: float,
        end_angle: float,
        orientation: int,
        start: Vec3,
        end: Vec3,
        full_circle: bool,
    ) -> ArcSegment:
        return {
            "type": "arc",
            "center": center,
            "radius": radius,
            "start_angle": start_angle,
            "end_angle": end_angle,
            "orientation": orientation,
            "start": start,
            "end": end,
            "full_circle": full_circle,
        }

    @staticmethod
    def _arc_sweep(segment: ArcSegment) -> float:
        if segment["orientation"] > 0:
            return segment["end_angle"] - segment["start_angle"]
        return segment["start_angle"] - segment["end_angle"]

    @classmethod
    def _try_cubic_as_arc(cls, start: Vec3, ctrl1: Vec3, ctrl2: Vec3, end: Vec3) -> ArcSegment | None:
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
        return cls._arc_segment(
            center=center,
            radius=radius_start,
            start_angle=start_angle,
            end_angle=end_angle,
            orientation=orientation,
            start=start,
            end=end,
            full_circle=full_circle,
        )

    def _segments_form_circle(self, segments: list[Segment]) -> CircleSummary | None:
        if not segments:
            return None
        first = segments[0]
        if first["type"] != "arc":
            return None
        if len(segments) == 1 and first["full_circle"]:
            return {"center": first["center"], "radius": first["radius"]}
        if any(seg["type"] != "arc" for seg in segments):
            return None
        center = first["center"]
        radius = first["radius"]
        orientation = first["orientation"]
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

    def _emit_polyline(self, segments: list[Segment]) -> None:
        if not segments:
            return
        segments = self._merge_line_segments(segments)
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

    def _emit_texts(self, texts: list[TextSpec]) -> None:
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

    def _flush_block(self, segments: list[Segment], texts: list[TextSpec]) -> None:
        if not segments:
            self._emit_texts(texts)
            return
        merged_segments = self._merge_arc_segments(segments)
        circle = self._segments_form_circle(merged_segments)
        if circle:
            self._emit_circle(circle["center"], circle["radius"])
        else:
            self._emit_polyline(merged_segments)
        self._emit_texts(texts)

    def add_commands(self, commands: Iterable[Command]) -> None:
        current_point: Vec3 | None = None
        segments: list[Segment] = []
        texts: list[TextSpec] = []

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
                    self._arc_segment(
                        center=center,
                        radius=radius,
                        start_angle=start_angle,
                        end_angle=end_angle,
                        orientation=orientation if orientation != 0 else 1,
                        start=current_point,
                        end=end_point,
                        full_circle=is_full_circle,
                    )
                )
                current_point = end_point
            elif letter == "T":
                x, y = float(cmd[1]), float(cmd[2])
                text = cmd[4]
                params: TextParams = dict(cmd[5]) if len(cmd) > 5 and isinstance(cmd[5], dict) else {}
                texts.append((x, y, text, params))
            else:
                raise ValueError(f"Unsupported drawing command: {letter}")

        flush()

class DXFSurface(Surface):
    """Surface capable of producing DXF output via EZDXFBuilder."""

    def finish(self, inner_corners: str = "loop", dogbone_radius=None):
        try:
            prepare_paths = super().prepare_paths  # type: ignore[attr-defined]
        except AttributeError:
            extents = self._prepare_paths_for_dxf(inner_corners, dogbone_radius)
        else:
            try:
                extents = prepare_paths(inner_corners, dogbone_radius)
            except TypeError:
                extents = prepare_paths(inner_corners)
        builder = EZDXFBuilder()
        builder.set_extents(extents.xmin, extents.ymin, extents.xmax, extents.ymax)
        for part in self.parts:
            if not part.pathes:
                continue
            for path in part.pathes:
                if not path.path:
                    continue
                builder.set_lineweight(path.params.get("lw"))
                builder.add_commands(path.path)
        return builder.to_buffer()

    def _prepare_paths_for_dxf(self, inner_corners: str, dogbone_radius=None):
        for part in self.parts:
            for path in getattr(part, "pathes", ()):
                faster_edges = getattr(path, "faster_edges", None)
                if not callable(faster_edges):
                    continue
                self._harmonize_path_commands(path)
                if dogbone_radius is None:
                    try:
                        faster_edges(inner_corners)
                    except TypeError:
                        faster_edges(inner_corners, dogbone_radius)
                else:
                    try:
                        faster_edges(inner_corners, dogbone_radius)
                    except TypeError:
                        faster_edges(inner_corners)
                self._harmonize_path_commands(path)
        return self._adjust_coordinates()

    @staticmethod
    def _harmonize_path_commands(path):
        try:
            path.path = [list(cmd) if isinstance(cmd, tuple) else cmd for cmd in path.path]
        except AttributeError:
            return
