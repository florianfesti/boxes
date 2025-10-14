from __future__ import annotations

import io
import math
from typing import Any

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
        for cmd in commands:
            letter = cmd[0]
            if letter == "M":
                current = (cmd[1], cmd[2])
            elif letter == "L":
                target = (cmd[1], cmd[2])
                if current and not points_equal(current[0], current[1], target[0], target[1]):
                    entities.extend(self._line_entity(current, target))
                current = target
            elif letter == "C":
                if current is None:
                    current = (cmd[1], cmd[2])
                    continue
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
                start_angle = math.degrees(cmd[6])
                end_angle = math.degrees(cmd[7])
                orientation = cmd[8]
                if radius > EPS:
                    if orientation < 0:
                        start_angle, end_angle = end_angle, start_angle
                    start_angle = self._format_angle(start_angle)
                    end_angle = self._format_angle(end_angle)
                    entities.extend(self._arc_entity(center, radius, start_angle, end_angle))
                current = end_point
            elif letter == "T":
                text_entities = self._text_entity(cmd)
                if text_entities:
                    entities.extend(text_entities)
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
