from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable, Sequence

import ezdxf
from ezdxf import units
from ezdxf.math import Vec3, Bezier4P, bezier_to_bspline

from boxes.test_path import Test_Path

Command = Sequence[object]


class EZDXFBuilder:
    """Utility that translates drawing commands into DXF entities using ezdxf."""

    _POINT_TOL = 1e-6
    _ARC_DEVIATION_FACTOR = 2e-3

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

    @classmethod
    def _try_cubic_as_arc(cls, start: Vec3, ctrl1: Vec3, ctrl2: Vec3, end: Vec3):
        # Reject degenerate curves with minimal length.
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

        # Ensure tangents are perpendicular to radius, within tolerance.
        if abs((start - center).dot(t_start)) > max(radius_start, 1.0) * 1e-3:
            return None
        if abs((end - center).dot(t_end)) > max(radius_start, 1.0) * 1e-3:
            return None

        # Sample deviation from fitted circle.
        max_dev = 0.0
        for t in (0.25, 0.5, 0.75):
            point = cls._evaluate_cubic(start, ctrl1, ctrl2, end, t)
            deviation = abs((point - center).magnitude - radius_start)
            max_dev = max(max_dev, deviation)
        if max_dev > max(radius_start, 1.0) * cls._ARC_DEVIATION_FACTOR:
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

        is_full_circle = (
            (end - start).magnitude <= max(radius_start, 1.0) * 1e-3
            and abs(sweep - 2.0 * math.pi) <= 1e-2
        )
        return {
            "center": center,
            "radius": radius_start,
            "start_angle": start_angle,
            "end_angle": end_angle,
            "orientation": orientation,
            "full_circle": is_full_circle,
        }

    def add_commands(self, commands: Iterable[Command]) -> None:
        current_point: Vec3 | None = None
        for raw in commands:
            if not raw:
                continue
            code = raw[0]
            if code == "M":
                current_point = self._vec(raw[1], raw[2])
            elif code == "L":
                end_point = self._vec(raw[1], raw[2])
                if current_point is not None:
                    self.msp.add_line(current_point, end_point, dxfattribs=self.entity_attribs)
                current_point = end_point
            elif code == "C":
                if current_point is None:
                    raise ValueError("Bezier segment without a defined starting point.")
                end_point = self._vec(raw[1], raw[2])
                ctrl1 = self._vec(raw[3], raw[4])
                ctrl2 = self._vec(raw[5], raw[6])
                if (
                    (end_point - current_point).magnitude <= self._POINT_TOL
                    and (ctrl1 - current_point).magnitude <= self._POINT_TOL
                    and (ctrl2 - current_point).magnitude <= self._POINT_TOL
                ):
                    current_point = end_point
                    continue
                arc = self._try_cubic_as_arc(current_point, ctrl1, ctrl2, end_point)
                if arc:
                    start_deg = math.degrees(arc["start_angle"])
                    end_deg = math.degrees(arc["end_angle"])
                    center_tuple = (arc["center"].x, arc["center"].y)
                    attribs = dict(self.entity_attribs)
                    if arc["full_circle"]:
                        self.msp.add_circle(center_tuple, arc["radius"], dxfattribs=attribs)
                    else:
                        self.msp.add_arc(
                            center_tuple,
                            arc["radius"],
                            start_angle=start_deg,
                            end_angle=end_deg,
                            is_counter_clockwise=arc["orientation"] > 0,
                            dxfattribs=attribs,
                        )
                else:
                    bezier = Bezier4P((current_point, ctrl1, ctrl2, end_point))
                    nurbs = bezier_to_bspline([bezier])
                    spline_entity = self.msp.add_spline(dxfattribs=self.entity_attribs)
                    spline_entity.apply_construction_tool(nurbs)
                current_point = end_point
            elif code == "A":
                end_point = self._vec(raw[1], raw[2])
                center = self._vec(raw[3], raw[4])
                radius = abs(float(raw[5]))
                start_param = float(raw[6])
                end_param = float(raw[7])
                orientation = int(raw[8])

                start_point = self._vec(
                    center.x + radius * math.cos(start_param),
                    center.y + radius * math.sin(start_param),
                )
                if current_point is None:
                    current_point = start_point
                elif math.hypot(current_point.x - start_point.x, current_point.y - start_point.y) > 1e-4:
                    current_point = start_point

                start_angle_deg = math.degrees(math.atan2(current_point.y - center.y, current_point.x - center.x))
                end_angle_deg = math.degrees(math.atan2(end_point.y - center.y, end_point.x - center.x))

                sweep = end_param - start_param
                if orientation < 0:
                    sweep = -sweep
                    start_angle_deg, end_angle_deg = end_angle_deg, start_angle_deg

                is_full_circle = (
                    math.hypot(end_point.x - start_point.x, end_point.y - start_point.y) <= 1e-4
                    and math.isclose(abs(sweep), 2.0 * math.pi, rel_tol=1e-6)
                )

                center_tuple = (center.x, center.y)
                if is_full_circle:
                    self.msp.add_circle(center_tuple, radius, dxfattribs=self.entity_attribs)
                else:
                    self.msp.add_arc(
                        center_tuple,
                        radius,
                        start_angle=start_angle_deg,
                        end_angle=end_angle_deg,
                        dxfattribs=self.entity_attribs,
                    )
                current_point = end_point
            elif code == "T":
                text = raw[4]
                if not text:
                    continue
                x, y = float(raw[1]), float(raw[2])
                params = raw[5] if len(raw) > 5 else {}
                height = float(params.get("fs", 2.0))
                align = params.get("align", "left")
                align_map = {
                    "left": "LEFT",
                    "middle": "CENTER",
                    "end": "RIGHT",
                }
                text_entity = self.msp.add_text(
                    text,
                    dxfattribs={
                        "height": height,
                        "layer": self.layer,
                    },
                )
                text_entity.dxf.insert = (x, y, 0.0)
                alignment = align_map.get(align, "LEFT")
                if alignment != "LEFT":
                    halign_codes = {"CENTER": 1, "RIGHT": 2}
                    text_entity.dxf.halign = halign_codes.get(alignment, 0)
                    text_entity.dxf.align_point = (x, y, 0.0)
            else:
                raise ValueError(f"Unsupported drawing command: {code}")

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
