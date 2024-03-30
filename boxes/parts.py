from __future__ import annotations

from math import *
from typing import Any, Callable

from boxes import vectors


def arcOnCircle(spanning_angle: float, outgoing_angle: float, r: float = 1.0) -> tuple[float, float]:
    angle = spanning_angle + 2 * outgoing_angle
    radius = r * sin(radians(0.5 * spanning_angle)) / sin(radians(180 - outgoing_angle - 0.5 * spanning_angle))
    return angle, abs(radius)


class Parts:
    def __init__(self, boxes) -> None:
        self.boxes = boxes

    """
    def roundKnob(self, diameter: float, n: int = 20, callback: Callable | None = None, move: str = ""):
        size = diameter+diameter/n
        if self.move(size, size, move, before=True):
            return
        self.moveTo(size/2, size/2)
        self.cc(callback, None, 0, 0)

        self.move(size, size, move)
    """

    def __getattr__(self, name: str) -> Any:
        return getattr(self.boxes, name)

    def disc(self, diameter: float, hole: float = 0, dwidth: float = 1.0, callback: Callable | None = None, move: str = "", label: str = "") -> None:
        """Simple disc

        :param diameter: diameter of the disc
        :param hole: (Default value = 0)
        :param callback: (Default value = None) called in the center
        :param dwidth: (Default value = 1) flatten on right side to given ratio
        :param move: (Default value = "")
        :param label: (Default value = "")
        """
        size = diameter
        r = diameter / 2.0

        if self.move(size*dwidth, size, move, before=True, label=label):
            return

        self.moveTo(size / 2, size / 2)

        if hole:
            self.hole(0, 0, hole / 2)

        self.cc(callback, None, 0, 0)
        if dwidth == 1.0:
            self.moveTo(r + self.burn, 0, 90)
            self.corner(360, r, tabs=6)
        else:
            w = (2.0 * dwidth - 1) * r
            a = degrees(acos(w / r))
            self.moveTo(0, 0, -a)
            self.moveTo(r, 0, -90)
            self.corner(-360+2*a, r)
            self.corner(-a)
            self.edge(2*r*sin(radians(a)))
        self.move(size*dwidth, size, move, label=label)

    def wavyKnob(self, diameter: float, n: int = 20, angle: float = 45, hole: float = 0, callback: Callable | None = None, move: str = "") -> None:
        """Disc with a wavy edge to be easier to be gripped

        :param diameter: diameter of the knob
        :param n: (Default value = 20) number of waves
        :param angle: (Default value = 45) maximum angle of the wave
        :param hole: (Default value = 0)
        :param callback: (Default value = None) called in the center
        :param move: (Default value = "")
        """

        if n < 2:
            return

        size = diameter + pi * diameter / n

        if self.move(size, size, move, before=True):
            return

        self.moveTo(size / 2, size / 2)
        self.cc(callback, None, 0, 0)

        if hole:
            self.hole(0, 0, hole / 2)

        self.moveTo(diameter / 2, 0, 90-angle)
        a, r = arcOnCircle(360. / n / 2, angle, diameter / 2)
        a2, r2 = arcOnCircle(360. / n / 2, -angle, diameter / 2)

        for i in range(n):
            self.boxes.corner(a, r, tabs=(i % max(1, (n+1) // 6) == 0))
            self.boxes.corner(a2, r2)

        self.move(size, size, move)

    def concaveKnob(self, diameter: float, n: int = 3, rounded: float = 0.2, angle: float = 70, hole: float = 0,
                    callback: Callable | None = None, move: str = "") -> None:
        """Knob with dents to be easier to be gripped

        :param diameter: diameter of the knob
        :param n: (Default value = 3) number of dents
        :param rounded: (Default value = 0.2) proportion of circumference remaining
        :param angle: (Default value = 70) angle the dents meet the circumference
        :param hole: (Default value = 0)
        :param callback: (Default value = None) called in the center
        :param move: (Default value = "")
        """
        size = diameter

        if n < 2:
            return

        if self.move(size, size, move, before=True):
            return

        self.moveTo(size / 2, size / 2)

        if hole:
            self.hole(0, 0, hole / 2)

        self.cc(callback, None, 0, 0)
        self.moveTo(diameter / 2, 0, 90 + angle)
        a, r = arcOnCircle(360. / n * (1 - rounded), -angle, diameter / 2)

        if abs(a) < 0.01:  # avoid trying to make a straight line as an arc
            a, r = arcOnCircle(360. / n * (1 - rounded), -angle - 0.01, diameter / 2)

        for i in range(n):
            self.boxes.corner(a, r)
            self.corner(angle)
            self.corner(360. / n * rounded, diameter / 2, tabs=(i % max(1, (n+1) // 6) == 0))
            self.corner(angle)

        self.move(size, size, move)

    def ringSegment(self, r_outside: float, r_inside: float, angle: float, n: int = 1, move: str = "") -> None:
        """Ring Segment

        :param r_outside: outer radius
        :param r_inside: inner radius
        :param angle: angle the segment is spanning
        :param n: (Default value = 1) number of segments
        :param move: (Default value = "")
        """
        space = 360 * self.spacing / r_inside / 2 / pi
        nc = int(min(n, 360 / (angle+space)))

        while n > 0:
            if self.move(2*r_outside, 2*r_outside, move, True):
                return
            self.moveTo(0, r_outside, -90)
            for i in range(nc):
                self.polyline(
                    0, (angle, r_outside), 0, 90, (r_outside-r_inside, 2),
                    90, 0, (-angle, r_inside), 0, 90, (r_outside-r_inside, 2),
                    90)
                x, y = vectors.circlepoint(r_outside, radians(angle+space))
                self.moveTo(y, r_outside-x, angle+space)
                n -=1
                if n == 0:
                    break
            self.move(2*r_outside, 2*r_outside, move)
