import math

import boxes.vectors


class EyeEdge(boxes.edges.FingerHoleEdge):

    char = "m"

    def __init__(self, boxes, servo, fingerHoles=None, driven=False,
                 outset=False, **kw) -> None:
        self.servo = servo
        self.outset = outset
        self.driven = driven
        super().__init__(boxes, fingerHoles, **kw)

    def __call__(self, length, bedBolts=None, bedBoltSettings=None, **kw):
        t = self.fingerHoles.settings.thickness
        dist = self.fingerHoles.settings.edge_width

        pos_axle = self.servo.hinge_depth()
        self.ctx.save()
        self.hole(length/2.0, -pos_axle,
                  self.servo.axle/2.0 if self.driven else
                  self.servo.servo_axle/2.0)
        if self.outset:
            self.fingerHoles(t, self.thickness / 2, length-2*t, 0)
        else:
            self.fingerHoles(0, self.thickness / 2, length, 0)
        self.ctx.restore()
        r = self.servo.servo_axle * 2
        a, l = boxes.vectors.tangent(length/2, pos_axle, r)
        angle = math.degrees(a)
        self.polyline(0, -angle, l, (2*angle, r), l, -angle, 0)

    def startwidth(self) -> float:
        return self.fingerHoles.settings.thickness

    def margin(self) -> float:
        return self.servo.hinge_depth() + self.fingerHoles.settings.thickness + self.servo.servo_axle * 2

def buildEdges(boxes, servo, chars="mMnN"):
    result = {}
    for n, char in enumerate(chars):
        e = EyeEdge(boxes, servo, outset=(n<2), driven=(n % 2))
        e.char = char
        result[char] = e
    return result

class ServoArg:

    def __init__(self, includenone=False) -> None:
        self.servos = ["Servo9g"]
        if includenone:
            self.servos[0:0] = ["none"]

    def __call__(self, arg):
        return str(arg)

    def choices(self):
        return [name for name in self.servos]

    def html(self, name, default, translate):
        options = "\n".join(
            """<option value="%s"%s>%s</option>""" %
             (name, ' selected="selected"' if name == default else "",
              name) for name in self.servos)
        return f"""<select name="{name}" size="1">\n{options}</select>\n"""


class Servo:
    def __init__(self, boxes, axle=3) -> None:
        self.boxes = boxes
        self.axle = axle
        self._edges = buildEdges(boxes, self)

    def edges(self, edges):
        return [self._edges.get(e, e) for e in edges]

class Servo9g(Servo):

    height = 22.5
    length = 28.0 # one tab in the wall
    width = 12.0
    axle_pos = 6.0
    servo_axle = 4.6 # 6.9 for servo arm
    
    def top(self, x=0.0, y=0.0, angle=90.0):
        self.boxes.moveTo(x, y, angle)
        self.boxes.hole(6, 0, 6)
        self.boxes.hole(12, 0, 3)

    def bottom(self, x=0.0, y=0.0, angle=90.0):
        self.boxes.moveTo(x, y, angle)
        self.boxes.hole(6, 0, self.axle/2.0)

    def front(self, x=0.0, y=0.0, angle=90.0):
        self.boxes.moveTo(x, y, angle)
        self.boxes.rectangularHole(5.4, 0, 2.4, 12)
        self.boxes.rectangularHole(17, 0, 4, 16)

    def hinge_width(self):
        return self.height + self.boxes.thickness + 4.5

    def hinge_depth(self):
        return self.height # XXX

class Servo9gt(Servo9g):
    height = 35

    def top(self, x=0.0, y=0.0, angle=90.0):
        self.boxes.moveTo(x, y, angle)
        self.boxes.hole(6, 0, 6)
        self.boxes.hole(12, 0, 5)

    def bottom(self, x=0.0, y=0.0, angle=90.0):
        self.boxes.moveTo(x, y, angle)
        self.boxes.hole(6, 0, self.axle)

    def front(self, x=0.0, y=0.0, angle=90.0):
        self.boxes.moveTo(x, y, angle)
        self.boxes.rectangularHole(5.4, 0, 2.4, 12)
