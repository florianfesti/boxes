from __future__ import annotations

import math
from math import *
from typing import Any
from collections.abc import Callable

from boxes import vectors
from boxes.Color import Color
from boxes.drawing import Context


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

    def draw_outer_crenels(self, cx: float, cy: float, ro: float, ctx: Context,
                           n: int, depth: float, shape: str = "symmetric",
                           width: float = 0.5, rounded: bool = False,
                           radius: float = 0.0) -> None:
        """Draw gear-tooth outer perimeter centred at *(cx, cy)* with outer radius *ro*.

        :param cx: x centre of the ring
        :param cy: y centre of the ring
        :param ro: outer radius – tooth tips land here
        :param ctx: drawing context
        :param n: number of teeth (one per score value)
        :param depth: tooth height; the base circle sits at ``ro - depth``
        :param shape: ``symmetric``, ``radial``, or ``blade``
        :param width: fraction of each sector that the tooth occupies (0–1)
        :param rounded: round the tooth base corners
        :param radius: corner radius when *rounded* is True
        """
        if n < 1:
            return

        radial = (shape == "radial")
        r_corn = radius if rounded else 0.0
        ri = ro - depth

        angle_step = 2.0 * math.pi / n
        half = angle_step / 2.0
        tooth_half = angle_step * (1.0 - max(0.05, min(0.95, width))) / 2.0

        self.set_source_color(Color.OUTER_CUT)
        start_angle = math.pi  # tooth 0 at 9 o'clock, matches score-label placement

        def pt_on(r: float, a: float) -> tuple[float, float]:
            return cx + r * math.cos(a), cy + r * math.sin(a)

        def sym_outer_corners(ca_in: float) -> tuple[tuple[float, float], tuple[float, float]]:
            bx = math.cos(ca_in)
            by = math.sin(ca_in)
            ixl, iyl = pt_on(ri, ca_in - tooth_half)
            ixr, iyr = pt_on(ri, ca_in + tooth_half)
            return (ixl + depth * bx, iyl + depth * by), (ixr + depth * bx, iyr + depth * by)

        # ── blade: half-ellipse per sector, bases touching ──────────────────
        if shape == "blade":
            k_bez = 4.0 / 3.0 * (math.sqrt(2.0) - 1.0)   # Bézier quarter-ellipse constant
            a_chord = ri * math.sin(half)
            h_r = depth * k_bez
            h_t = a_chord * k_bez
            ctx.move_to(*pt_on(ri, start_angle - half))
            for i in range(n):
                center_a = start_angle + i * angle_step
                pl = pt_on(ri, center_a - half)
                pr = pt_on(ri, center_a + half)
                pt_tip = pt_on(ro, center_a)
                rl = (math.cos(center_a - half), math.sin(center_a - half))
                rr = (math.cos(center_a + half), math.sin(center_a + half))
                tt = (-math.sin(center_a), math.cos(center_a))
                ctx.curve_to(pl[0] + h_r * rl[0], pl[1] + h_r * rl[1],
                             pt_tip[0] - h_t * tt[0], pt_tip[1] - h_t * tt[1],
                             *pt_tip)
                ctx.curve_to(pt_tip[0] + h_t * tt[0], pt_tip[1] + h_t * tt[1],
                             pr[0] - h_r * rr[0], pr[1] - h_r * rr[1],
                             *pr)
            ctx.line_to(*pt_on(ri, start_angle - half))
            ctx.stroke()
            return
        # ────────────────────────────────────────────────────────────────────

        ctx.move_to(*pt_on(ri, start_angle - half))
        last_tooth_r: float = start_angle - half

        for i in range(n):
            center_a = start_angle + i * angle_step
            tooth_l = center_a - tooth_half
            tooth_r = center_a + tooth_half

            if radial:
                if r_corn <= 0.0 or ri <= 0.0:
                    ctx.arc(cx, cy, ri, center_a - half, tooth_l)
                    ctx.line_to(*pt_on(ro, tooth_l))
                    ctx.arc(cx, cy, ro, tooth_l, tooth_r)
                    ctx.line_to(*pt_on(ri, tooth_r))
                    last_tooth_r = tooth_r
                else:
                    da_i = min(r_corn / ri, tooth_half * 0.45)
                    da_o = min(r_corn / ro, tooth_half * 0.45)
                    ctx.arc(cx, cy, ri, center_a - half, tooth_l - da_i)
                    ctx.curve_to(*pt_on(ro, tooth_l - da_o),
                                 *pt_on(ro, tooth_l - da_o),
                                 *pt_on(ro, tooth_l + da_o))
                    ctx.arc(cx, cy, ro, tooth_l + da_o, tooth_r - da_o)
                    ctx.curve_to(*pt_on(ri, tooth_r + da_i),
                                 *pt_on(ri, tooth_r + da_i),
                                 *pt_on(ri, tooth_r + da_i))
                    last_tooth_r = tooth_r + da_i
            else:
                ol, or_ = sym_outer_corners(center_a)
                bx = math.cos(center_a)
                by = math.sin(center_a)
                if r_corn <= 0.0:
                    ctx.arc(cx, cy, ri, center_a - half, tooth_l)
                    ctx.line_to(*ol)
                    ctx.line_to(*or_)
                    ctx.line_to(*pt_on(ri, tooth_r))
                    last_tooth_r = tooth_r
                else:
                    da_i = min(r_corn / ri, tooth_half * 0.4)
                    rc = min(r_corn, ri * tooth_half * 0.4)
                    ctx.arc(cx, cy, ri, center_a - half, tooth_l - da_i)
                    fl_ctrl = (cx + ri * math.cos(tooth_l) + rc * bx,
                               cy + ri * math.sin(tooth_l) + rc * by)
                    ctx.curve_to(*fl_ctrl, *fl_ctrl, *ol)
                    ctx.line_to(*or_)
                    fr_ctrl = (cx + ri * math.cos(tooth_r) + rc * bx,
                               cy + ri * math.sin(tooth_r) + rc * by)
                    ctx.curve_to(*fr_ctrl, *fr_ctrl, *pt_on(ri, tooth_r + da_i))
                    last_tooth_r = tooth_r + da_i

        ctx.arc(cx, cy, ri, last_tooth_r, start_angle - half + 2.0 * math.pi)
        ctx.stroke()

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
