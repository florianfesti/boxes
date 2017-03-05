from math import *
from boxes import vectors

def arcOnCircle(spanning_angle, outgoing_angle, r=1.0):
    angle = spanning_angle + 2 * outgoing_angle
    radius = r * sin(radians(0.5 * spanning_angle)) / sin(radians(180 - outgoing_angle - 0.5 * spanning_angle))
    return angle, abs(radius)


class Parts:
    def __init__(self, boxes):
        self.boxes = boxes

    """
    def roundKnob(self, diameter, n=20, callback=None, move=""):
        size = diameter+diameter/n
        if self.move(size, size, move, before=True):
            return
        self.moveTo(size/2, size/2)
        self.cc(callback, None, 0, 0)
        
        self.move(size, size, move)
    """

    def __getattr__(self, name):
        return getattr(self.boxes, name)

    def disc(self, diameter, hole=0, callback=None, move=""):
        size = diameter
        r = diameter / 2.0

        if self.move(size, size, move, before=True):
            return

        self.moveTo(size / 2, size / 2)

        if hole:
            self.hole(0, 0, hole / 2)

        self.cc(callback, None, 0, 0)
        self.moveTo(r + self.burn, 0, 90)
        self.corner(360, r)
        self.move(size, size, move)

    def waivyKnob(self, diameter, n=20, angle=45, hole=0, callback=None, move=""):
        size = diameter + pi * diameter / n

        if self.move(size, size, move, before=True):
            return

        self.moveTo(size / 2, size / 2)
        self.cc(callback, None, 0, 0)

        if hole:
            self.hole(0, 0, hole / 2)

        self.moveTo(diameter / 2, 0, angle)
        a, r = arcOnCircle(360. / n, angle, diameter / 2)
        a2, r2 = arcOnCircle(360. / n, -angle, diameter / 2)

        for i in range(n // 2):
            self.boxes.corner(a, r)
            self.boxes.corner(a2, r2)

        self.move(size, size, move)

    def concaveKnob(self, diameter, n=3, rounded=0.2, angle=70, hole=0,
                    callback=None, move=""):
        size = diameter

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
            self.corner(360. / n * rounded, diameter / 2)
            self.corner(angle)

        self.move(size, size, move)

    def ringSegment(self, r_outside, r_inside, angle, n=1, move=None):
        space = 360 * r_inside / self.spacing
        n = min(n, 360 / (angle+space))

        # XXX be smarter about space
        if self.move(r_outside, r_outside, move, True):
            return

        self.moveTo(r_outside)
        for i in range(n):
            self.polyline(0, (angle, r_outside), 0, 90, (r_outside-r_inside),
                          90, (angle, r_inside), 0, 90, (r_outside-r_inside),
                          90)
            x, y = vectors.circlepoint(r_outside, math.radians(angle+space))
            self.moveTo(y, r_outside-x, angle+space)
        self.move(r_outside, r_outside)
        return n
