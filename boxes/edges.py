#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math
import inspect
import argparse
import re

from boxes import gears

def getDescriptions():
    d = {edge.char: edge.description for edge in globals().values()
         if inspect.isclass(edge) and issubclass(edge, BaseEdge)
         and edge.char}
    d['k'] = "Straight edge with hinge eye (both ends)"
    return d


class BoltPolicy(object):
    """Abstract class

    Distributes (bed) bolts on a number of segments
    (fingers of a finger joint)

    """

    def drawbolt(self, pos):
        """Add a bolt to this segment?

        :param pos: number of the finger

        """
        return False

    def numFingers(self, numfingers):
        """Return next smaller, possible number of fingers

        :param numfingers: number of fingers to aim for

        """
        return numfingers

    def _even(self, numFingers):
        """
        Return same or next smaller even number

        :param numFingers:

        """
        return (numFingers // 2) * 2

    def _odd(self, numFingers):
        """
        Return same or next smaller odd number

        :param numFingers:

        """
        if numFingers % 2:
            return numFingers
        else:
            return numFingers - 1


class Bolts(BoltPolicy):
    """Distribute a fixed number of bolts evenly"""

    def __init__(self, bolts=1):
        self.bolts = bolts

    def numFingers(self, numFingers):
        if self.bolts % 2:
            self.fingers = self._even(numFingers)
        else:
            self.fingers = numFingers

        return self.fingers

    def drawBolt(self, pos):
        """
        Return if this finger needs a bolt

        :param pos: number of this finger

        """
        if pos > self.fingers // 2:
            pos = self.fingers - pos

        if pos == 0:
            return False

        if pos == self.fingers // 2 and not (self.bolts % 2):
            return False

        return (math.floor((float(pos) * (self.bolts + 1) / self.fingers) - 0.01) !=
                  math.floor((float(pos + 1) * (self.bolts + 1) / self.fingers) - 0.01))


#############################################################################
### Settings
#############################################################################

class Settings(object):
    """Generic Settings class

    Used by different other classes to store messurements and details.
    Supports absolute values and settings that grow with the thickness
    of the material used.

    Overload the absolute_params and relative_params class attributes with
    the suported keys and default values. The values are available via
    attribute access.
    """
    absolute_params = {}
    relative_params = {}

    @classmethod
    def parserArguments(cls, parser, prefix=None, **defaults):
        prefix = prefix or cls.__name__[:-len("Settings")]

        lines  = cls.__doc__.split("\n")

        # Parse doc string
        descriptions = {}
        r = re.compile(r"^ +\* +(\S+) +: .* : +(.*)")
        for l in lines:
            m = r.search(l)
            if m:
                descriptions[m.group(1)] = m.group(2)

        group = parser.add_argument_group(lines[0] or lines[1])
        group.prefix = prefix
        for name, default in (sorted(cls.absolute_params.items()) +
                              sorted(cls.relative_params.items())):
            if name in defaults:
                default = defaults[name]
            group.add_argument("--%s_%s" % (prefix, name),
                               type=type(default),
                               action="store", default=default,
                               help=descriptions.get(name))

    def __init__(self, thickness, relative=True, **kw):
        self.values = self.absolute_params.copy()
        self.thickness = thickness
        factor = 1.0
        if relative:
            factor = thickness
        for name, value in self.relative_params.items():
            self.values[name] = value * factor
        self.setValues(thickness, relative, **kw)

    def setValues(self, thickness, relative=True, **kw):
        """
        Set values

        :param thickness: thickness of the material used
        :param relative:  (Default value = True) Do scale by thickness
        :param \*\*kw: parameters to set

        """
        factor = 1.0
        if relative:
            factor = thickness
        print(kw.items())
        for name, value in kw.items():
            if name in self.absolute_params:
                self.values[name] = value
            elif name in self.relative_params:
                self.values[name] = value * factor
            else:
                raise ValueError("Unknown parameter for %s: %s" % (
                    self.__class__.__name__, name))

    def __getattr__(self, name):
        return self.values[name]


#############################################################################
### Edges
#############################################################################


class BaseEdge(object):
    """Abstract base class for all Edges"""
    char = None
    description = "Abstract Edge Class"

    def __init__(self, boxes, settings):
        self.boxes = boxes
        self.ctx = boxes.ctx
        self.settings = settings

    def __getattr__(self, name):
        """Hack for using unalter code form Boxes class"""
        return getattr(self.boxes, name)

    def __call__(self, length, **kw):
        """Draw edge of length mm"""
        self.ctx.move_to(0, 0)
        self.ctx.line_to(length, 0)
        self.ctx.translate(*self.ctx.get_current_point())

    def startwidth(self):
        """Amount of space the beginning of the edge is set below the inner space of the part """
        return 0.0

    def endwidth(self):
        return self.startwidth()

    def margin(self):
        """Space needed right of the starting point"""
        return 0.0

    def spacing(self):
        """Space the edge needs outside of the inner space of the part"""
        return self.startwidth() + self.margin()

    def startAngle(self):
        """Not yet supported"""
        return 0.0

    def endAngle(self):
        """Not yet supported"""
        return 0.0


class Edge(BaseEdge):
    """Straight edge"""
    char = 'e'
    description = "Straight Edge"


class OutSetEdge(BaseEdge):
    """Straight edge out set by one thickness"""
    char = 'E'
    description = "Straight Edge (outset by thickness)"

    def startwidth(self):
        return self.boxes.thickness


#############################################################################
####     Gripping Edge
#############################################################################

class GripSettings(Settings):
    """Settings for GrippingEdge
Values:

* absolute_params

 * style : A : "A" (wiggly line) or "B" (bumps)
 * outset : True : extend outward the straight edge

* relative (in multiples of thickness)

 * depth : 0.3 : depth of the grooves

"""

    absolute_params = {
        "style": "A",
        "outset": True,
    }

    relative_params = {
        "depth": 0.3,
    }


class GrippingEdge(BaseEdge):
    description = """Corrugated edge useful as an gipping area"""
    char = 'g'

    def A(self, length):
        depth = self.settings.depth
        grooves = int(length // (depth * 2.0)) + 1
        depth = length / grooves / 4.0

        o = 1 if self.settings.outset else -1
        for groove in range(grooves):
            self.corner(o * -90, depth)
            self.corner(o * 180, depth)
            self.corner(o * -90, depth)

    def B(self, length):
        depth = self.settings.depth
        grooves = int(length // (depth * 2.0)) + 1
        depth = length / grooves / 2.0
        o = 1 if self.settings.outset else -1

        if self.settings.outset:
            self.corner(-90)
        else:
            self.corner(90)
            self.edge(depth)
            self.corner(-180)

        for groove in range(grooves):
            self.corner(180, depth)
            self.corner(-180, 0)

        if self.settings.outset:
            self.corner(90)
        else:
            self.edge(depth)
            self.corner(90)

    def margin(self):
        if self.settings.outset:
            return self.settings.depth
        else:
            return 0.0

    def __call__(self, length, **kw):
        if length == 0.0:
            return
        getattr(self, self.settings.style)(length)


class CompoundEdge(BaseEdge):
    """Edge composed of multiple different Edges"""
    description = "Compound Edge"

    def __init__(self, boxes, types, lengths):
        super(CompoundEdge, self).__init__(boxes, None)

        self.types = [self.edges.get(edge, edge) for edge in types]
        self.lengths = lengths
        self.length = sum(lengths)

    def startwidth(self):
        return self.types[0].startwidth()

    def endwidth(self):
        return self.types[-1].endwidth()

    def margin(self):
        return max((e.margin() for e in self.types))

    def __call__(self, length, **kw):
        if length and abs(length - self.length) > 1E-5:
            raise ValueError("Wrong length for CompoundEdge")
        lastwidth = self.types[0].startwidth()

        for e, l in zip(self.types, self.lengths):
            diff = e.startwidth() - lastwidth

            if diff > 1E-5:
                self.boxes.corner(-90)
                self.boxes.edge(diff)
                self.boxes.corner(90)
            elif diff < -1E-5:
                self.boxes.corner(90)
                self.boxes.edge(-diff)
                self.boxes.corner(-90)

            e(l)
            lastwidth = e.endwidth()


#############################################################################
####     Slots
#############################################################################

class Slot(BaseEdge):
    """Edge with an slot to slid another pice through """

    description = "Slot"

    def __init__(self, boxes, depth):
        super(Slot, self).__init__(boxes, None)

        self.depth = depth

    def __call__(self, length, **kw):
        if self.depth:
            self.boxes.corner(90)
            self.boxes.edge(self.depth)
            self.boxes.corner(-90)
            self.boxes.edge(length)
            self.boxes.corner(-90)
            self.boxes.edge(self.depth)
            self.boxes.corner(90)
        else:
            self.boxes.edge(self.length)


class SlottedEdge(BaseEdge):
    """Edge with multiple slots"""
    description = "Straight Edge with slots"

    def __init__(self, boxes, sections, edge="e", slots=0):
        super(SlottedEdge, self).__init__(boxes, None)

        self.edge = self.edges.get(edge, edge)
        self.sections = sections
        self.slots = slots

    def startwidth(self):
        return self.edge.startwidth()

    def endwidth(self):
        return self.edge.endwidth()

    def margin(self):
        return self.edge.margin()

    def __call__(self, length, **kw):

        for l in self.sections[:-1]:
            self.edge(l)

            if self.slots:
                Slot(self.boxes, self.slots)(self.thickness)
            else:
                self.edge(self.thickness)

        self.edge(self.sections[-1])


#############################################################################
####     Finger Joints
#############################################################################

class FingerJointSettings(Settings):
    """Settings for Finger Joints

Values:

* absolute

  * surroundingspaces : 2 : maximum space at the start and end in multiple of normal spaces

* relative (in multiples of thickness)

  * space : 1.0 : space between fingers
  * finger : 1.0 : width of the fingers
  * height : 1.0 : length of the fingers
  * width : 1.0 : width of finger holes
  * edge_width : 1.0 : space below holes of FingerHoleEdge
  * play : 0.0 : extra space to allow movement

"""

    absolute_params = {
        "surroundingspaces": 2,
    }

    relative_params = {
        "space": 1.0,
        "finger": 1.0,
        "height": 1.0,
        "width": 1.0,
        "edge_width": 1.0,
        "play" : 0.0,
    }

class FingerJointBase:

    def calcFingers(self, length, bedBolts):
        space, finger = self.settings.space, self.settings.finger
        fingers = int((length - (self.settings.surroundingspaces - 1) * space) //
                      (space + finger))
        if not finger:
            fingers = 0
        if bedBolts:
            fingers = bedBolts.numFingers(fingers)
        leftover = length - fingers * (space + finger) + space

        if fingers <= 0:
            fingers = 0
            leftover = length

        return fingers, leftover

class FingerJointEdge(BaseEdge, FingerJointBase):
    """Finger joint edge """
    char = 'f'
    description = "Finger Joint"
    positive = True

    def __call__(self, length, bedBolts=None, bedBoltSettings=None, **kw):

        positive = self.positive

        s, f, thickness = self.settings.space, self.settings.finger, self.thickness

        p = 1 if positive else -1

        fingers, leftover = self.calcFingers(length, bedBolts)

        if not positive:
            play = self.settings.play
            f += play
            s -= play
            leftover -= play

        self.edge(leftover / 2.0)

        for i in range(fingers):
            if i != 0:
                if not positive and bedBolts and bedBolts.drawBolt(i):
                    self.hole(0.5 * space,
                              0.5 * self.thickness, 0.5 * d)

                if positive and bedBolts and bedBolts.drawBolt(i):
                    self.bedBoltHole(s, bedBoltSettings)
                else:
                    self.edge(s)

            self.corner(-90 * p)
            self.edge(self.settings.height)
            self.corner(90 * p)
            self.edge(f)
            self.corner(90 * p)
            self.edge(self.settings.height)
            self.corner(-90 * p)

        self.edge(leftover / 2.0)

    def margin(self):
        """ """
        return self.boxes.thickness


class FingerJointEdgeCounterPart(FingerJointEdge):
    """Finger joint edge - other side"""
    char = 'F'
    description = "Finger Joint (opposing side)"
    positive = False

    def startwidth(self):
        """ """
        return self.boxes.thickness

    def margin(self):
        """ """
        return 0.0


class FingerHoles(FingerJointBase):
    """Hole matching a finger joint edge"""

    def __init__(self, boxes, settings):
        self.boxes = boxes
        self.ctx = boxes.ctx
        self.settings = settings

    def __call__(self, x, y, length, angle=90, bedBolts=None, bedBoltSettings=None):
        """
        Draw holes for a matching finger joint edge

        :param x: position
        :param y: position
        :param length: length of matching edge
        :param angle:  (Default value = 90)
        :param bedBolts:  (Default value = None)
        :param bedBoltSettings:  (Default value = None)

        """
        self.boxes.ctx.save()
        self.boxes.moveTo(x, y, angle)

        s, f = self.settings.space, self.settings.finger
        p = self.settings.play
        b = self.boxes.burn

        fingers, leftover = self.calcFingers(length, bedBolts)

        if self.boxes.debug:
            self.ctx.rectangle(0, -self.settings.width / 2 + b,
                               length, self.settings.width - 2 * b)
        for i in range(fingers):
            pos = leftover / 2.0 + i * (s + f)

            if bedBolts and bedBolts.drawBolt(i):
                self.boxes.hole(pos + 0.5 * s, 0, d * 0.5)

            self.boxes.rectangularHole(pos + 0.5 * f, 0,
                                       f+p, self.settings.width+p)

        self.ctx.restore()
        self.ctx.move_to(0, 0)


class FingerHoleEdge(BaseEdge):
    """Edge with holes for a parallel finger joint"""
    char = 'h'
    description = "Edge (parallel Finger Joint Holes)"

    def __init__(self, boxes, fingerHoles=None, **kw):
        settings = None
        if isinstance(fingerHoles, Settings):
            settings = fingerHoles
            fingerHoles = FingerHoles(boxes, settings)
        super(FingerHoleEdge, self).__init__(boxes, settings, **kw)

        self.fingerHoles = fingerHoles or boxes.fingerHolesAt

    def __call__(self, length, bedBolts=None, bedBoltSettings=None, **kw):
        dist = self.fingerHoles.settings.edge_width
        self.ctx.save()
        self.fingerHoles(0, dist + self.thickness / 2, length, 0,
                         bedBolts=bedBolts, bedBoltSettings=bedBoltSettings)
        self.ctx.restore()
        # XXX continue path
        self.ctx.move_to(0, 0)
        self.ctx.line_to(length, 0)
        self.ctx.translate(*self.ctx.get_current_point())

    def startwidth(self):
        """ """
        return self.fingerHoles.settings.edge_width + self.thickness


class CrossingFingerHoleEdge(BaseEdge):
    """Edge with holes for finger joints 90° above"""

    description = "Edge (orthogonal Finger Joint Holes)"

    def __init__(self, boxes, height, fingerHoles=None, **kw):
        super(CrossingFingerHoleEdge, self).__init__(boxes, None, **kw)

        self.fingerHoles = fingerHoles or boxes.fingerHolesAt
        self.height = height

    def __call__(self, length, **kw):
        self.fingerHoles(length / 2.0, 0, self.height)
        super(CrossingFingerHoleEdge, self).__call__(length)


#############################################################################
####     Stackable Joints
#############################################################################

class StackableSettings(Settings):
    """Settings for Stackable Edges

Values:

* absolute_params

  * angle : 60 : inside angle of the feet

* relative (in multiples of thickness)

  * height : 2.0 : height of the feet
  * width  : 4.0 : width of the feet
  * holedistance : 1.0 : distance from finger holes to bottom edge

"""

    absolute_params = {
        "angle": 60,
    }

    relative_params = {
        "height": 2.0,
        "width": 4.0,
        "holedistance": 1.0,
    }


class StackableEdge(BaseEdge):
    """Edge for having stackable Boxes. The Edge creates feet on the bottom
    and has matching recesses on the top corners."""

    char = "s"
    description = "Stackable (bottom, finger joint holes)"
    bottom = True

    def __init__(self, boxes, settings, fingerjointsettings):
        super(StackableEdge, self).__init__(boxes, settings)

        self.fingerjointsettings = fingerjointsettings

    def __call__(self, length, **kw):
        s = self.settings
        r = s.height / 2.0 / (1 - math.cos(math.radians(s.angle)))
        l = r * math.sin(math.radians(s.angle))
        p = 1 if self.bottom else -1

        if self.bottom:
            self.boxes.fingerHolesAt(0, s.height + self.settings.holedistance + 0.5 * self.boxes.thickness,
                                     length, 0)

        self.boxes.edge(s.width)
        self.boxes.corner(p * s.angle, r)
        self.boxes.corner(-p * s.angle, r)
        self.boxes.edge(length - 2 * s.width - 4 * l)
        self.boxes.corner(-p * s.angle, r)
        self.boxes.corner(p * s.angle, r)
        self.boxes.edge(s.width)

    def _height(self):
        return self.settings.height + self.settings.holedistance + self.settings.thickness

    def startwidth(self):
        return self._height() if self.bottom else 0

    def margin(self):
        return 0 if self.bottom else self._height()


class StackableEdgeTop(StackableEdge):
    char = "S"
    description = "Stackable (top)"
    bottom = False


#############################################################################
####     Hinges
#############################################################################

class HingeSettings(Settings):
    """Settings for Hinges and HingePins
Values:

* absolute_params

 * style : B : currently "A" or "B"
 * outset : False : have lid overlap at the sides (similar to OutSetEdge)
 * pinwidth : 1.0 : set to lower value to get disks surrounding the pins
 * grip_percentage" : 0 : percentage of the lid that should get grips

* relative (in multiples of thickness)

 * hingestrength : 1 : thickness of the arc holding the pin in place
 * axle : 2 : diameter of the pin hole
 * grip_length : 0 : fixed length of the grips on he lids

"""
    absolute_params = {
        "style": "A",
        "outset": False,
        "pinwidth": 0.5,
        "grip_percentage": 0,
    }

    relative_params = {
        "hingestrength": 1,  # 1.5-0.5*2**0.5,
        "axle": 2,
        "grip_length": 0,
    }


class Hinge(BaseEdge):
    char = 'i'
    description = "Straight edge with hinge eye"

    def __init__(self, boxes, settings=None, layout=1):
        super(Hinge, self).__init__(boxes, settings)

        if not (0 < layout <= 3):
            raise ValueError("layout must be 1, 2 or 3 (got %i)" % layout)

        self.layout = layout
        self.char = "eijk"[layout]
        self.description = self.description + ('', ' (start)', ' (end)', ' (both ends)')[layout]

    def margin(self):
        return 3 * self.thickness

    def A(self, _reversed=False):
        t = self.thickness
        r = 0.5 * self.settings.axle
        alpha = math.degrees(math.asin(0.5 * t / r))
        pinl = (self.settings.axle ** 2 - self.thickness ** 2) ** 0.5 * self.settings.pinwidth
        pos = math.cos(math.radians(alpha)) * r
        hinge = (
            0,
            90 - alpha, 0,
            (-360, r), 0,
            90 + alpha,
            t,
            90,
            0.5 * t,
            (180, t + pos), 0,
            (-90, 0.5 * t), 0
        )

        if _reversed:
            hinge = reversed(hinge)
            self.polyline(*hinge)
            self.boxes.rectangularHole(-pos, -0.5 * t, pinl, self.thickness)
        else:
            self.boxes.rectangularHole(pos, -0.5 * t, pinl, self.thickness)
            self.polyline(*hinge)

    def Alen(self):
        t = self.thickness
        r = 0.5 * self.settings.axle
        alpha = math.degrees(math.asin(0.5 * t / r))
        pos = math.cos(math.radians(alpha)) * r

        return 2 * pos + 1.5 * t

    def B(self, _reversed=False):
        t = self.thickness

        hinge = (
            0, -90,
            0.5 * t,
            (180, 0.5 * self.settings.axle + self.settings.hingestrength), 0,
            (-90, 0.5 * t), 0
        )
        pos = 0.5 * self.settings.axle + self.settings.hingestrength
        pinl = (self.settings.axle ** 2 - self.thickness ** 2) ** 0.5 * self.settings.pinwidth

        if _reversed:
            hinge = reversed(hinge)
            self.hole(0.5 * t + pos, -0.5 * t, 0.5 * self.settings.axle)
            self.boxes.rectangularHole(0.5 * t + pos, -0.5 * t, pinl, self.thickness)
        else:
            self.hole(pos, -0.5 * t, 0.5 * self.settings.axle)
            self.boxes.rectangularHole(pos, -0.5 * t, pinl, self.thickness)

        self.polyline(*hinge)

    def Blen(self):
        return self.settings.axle + 2 * self.settings.hingestrength + 0.5 * self.thickness

    def __call__(self, l, **kw):
        hlen = getattr(self, self.settings.style + 'len')()

        if self.layout & 1:
            getattr(self, self.settings.style)()

        self.edge(l - (self.layout & 1) * hlen - bool(self.layout & 2) * hlen)

        if self.layout & 2:
            getattr(self, self.settings.style)(True)


class HingePin(BaseEdge):
    char = 'I'
    description = "Edge with hinge pin"

    def __init__(self, boxes, settings=None, layout=1):
        super(HingePin, self).__init__(boxes, settings)

        if not (0 < layout <= 3):
            raise ValueError("layout must be 1, 2 or 3 (got %i)" % layout)

        self.layout = layout
        self.char = "EIJK"[layout]
        self.description = self.description + ('', ' (start)', ' (end)', ' (both ends)')[layout]

    def startwidth(self):
        if self.layout & 1:
            return 0
        else:
            return self.settings.outset * self.boxes.thickness

    def endwidth(self):
        if self.layout & 2:
            return 0
        else:
            return self.settings.outset * self.boxes.thickness

    def margin(self):
        return self.thickness

    def A(self, _reversed=False):
        t = self.thickness
        r = 0.5 * self.settings.axle
        alpha = math.degrees(math.asin(0.5 * t / r))
        pos = math.cos(math.radians(alpha)) * r
        pinl = (self.settings.axle ** 2 - self.thickness ** 2) ** 0.5 * self.settings.pinwidth
        pin = (pos - 0.5 * pinl, -90,
               t, 90,
               pinl,
               90,
               t,
               -90)

        if self.settings.outset:
            pin += (
                pos - 0.5 * pinl + 1.5 * t,
                -90,
                t,
                90,
                0,
            )
        else:
            pin += (pos - 0.5 * pinl,)

        if _reversed:
            pin = reversed(pin)

        self.polyline(*pin)

    def Alen(self):
        t = self.thickness
        r = 0.5 * self.settings.axle
        alpha = math.degrees(math.asin(0.5 * t / r))
        pos = math.cos(math.radians(alpha)) * r

        if self.settings.outset:
            return 2 * pos + 1.5 * self.thickness
        else:
            return 2 * pos

    def B(self, _reversed=False):
        t = self.thickness
        pinl = (self.settings.axle ** 2 - t ** 2) ** 0.5 * self.settings.pinwidth
        d = (self.settings.axle - pinl) / 2.0
        pin = (self.settings.hingestrength + d, -90,
               t, 90,
               pinl,
               90,
               t,
               -90, d)

        if self.settings.outset:
            pin += (
                0,
                self.settings.hingestrength + 0.5 * t,
                -90,
                t,
                90,
                0,
            )

        if _reversed:
            pin = reversed(pin)

        self.polyline(*pin)

    def Blen(self):
        l = self.settings.hingestrength + self.settings.axle

        if self.settings.outset:
            l += self.settings.hingestrength + 0.5 * self.thickness

        return l

    def __call__(self, l, **kw):
        plen = getattr(self, self.settings.style + 'len')()
        glen = l * self.settings.grip_percentage + \
               self.settings.grip_length

        if not self.settings.outset:
            glen = 0.0

        glen = min(glen, l - plen)

        if self.layout & 1 and self.layout & 2:
            getattr(self, self.settings.style)()
            self.edge(l - 2 * plen)
            getattr(self, self.settings.style)(True)
        elif self.layout & 1:
            getattr(self, self.settings.style)()
            self.edge(l - plen - glen)
            self.edges['g'](glen)
        else:
            self.edges['g'](glen)
            self.edge(l - plen - glen)
            getattr(self, self.settings.style)(True)


#############################################################################
####     Slide-in lid
#############################################################################

class LidSettings(FingerJointSettings):
    absolute_params = FingerJointSettings.absolute_params.copy()
    relative_params = FingerJointSettings.relative_params.copy()

    relative_params.update( {
        "play" : 0.05,
        "second_pin" : 2,
        } )

class LidEdge(FingerJointEdge):
    char = "l"
    description = "Edge for slide on lid"

class LidHoleEdge(FingerHoleEdge):
    char = "L"
    description = "Edge for slide on lid"

class LidRight(BaseEdge):
    char = "n"
    description = "Edge for slide on lid (right)"
    rightside = True

    def __call__(self, length, **kw):
        t = self.boxes.thickness
        p = [t, 90, t, -90, length-t]
        pin = self.settings.second_pin

        if pin:
            p[-1:] = [length-2*t-pin, -90, t, 90, pin, 90, t, -90, t]

        if not self.rightside:
            p = list(reversed(p))
        self.polyline(*p)

    def startwidth(self):
        if self.rightside: # or self.settings.second_pin:
            return self.boxes.thickness
        else:
            return 0.0

    def endwidth(self):
        if not self.rightside: # or self.settings.second_pin:
            return self.boxes.thickness
        else:
            return 0.0

    def margin(self):
        if not self.rightside: # and not self.settings.second_pin:
            return self.boxes.thickness
        else:
            return 0.0

class LidLeft(LidRight):
    char = "m"
    description = "Edge for slide on lid (left)"
    rightside = False

class LidSideRight(BaseEdge):
    char = "N"
    description = "Edge for slide on lid (box right)"

    rightside = True
    def __call__(self, length,  **kw):
        t = self.boxes.thickness
        s = self.settings.play
        pin = self.settings.second_pin

        p = [t+s, -90, t+s, -90, 2*t+s, 90, t-s, 90, length+t]

        if pin:
            p[-1:] = [p[-1]-t-2*pin, 90, 2*t+s, -90, 2*pin+s, -90, t+s, -90,
                      pin, 90, t, 90, pin+t-s]
        if not self.rightside:
            p = list(reversed(p))
        self.polyline(*p)

    def startwidth(self):
        return 2*self.boxes.thickness if not self.rightside else 0.0

    def endwidth(self):
        return 2*self.boxes.thickness if self.rightside else 0.0

    def margin(self):
        return 2*self.boxes.thickness # if not self.rightside else 0.0

class LidSideLeft(LidSideRight):
    char = "M"
    description = "Edge for slide on lid (box left)"
    rightside = False

#############################################################################
####     Click Joints
#############################################################################

class ClickSettings(Settings):
    absolute_params = {
        "angle": 5,
    }

    relative_params = {
        "depth": 3.0,
        "bottom_radius": 0.1,
    }


class ClickConnector(BaseEdge):
    char = "c"
    description = "Click on (bottom side)"

    def hook(self, reverse=False):
        t = self.thickness
        a = self.settings.angle
        d = self.settings.depth
        r = self.settings.bottom_radius
        c = math.cos(math.radians(a))
        s = math.sin(math.radians(a))

        p1 = (0, 90 - a, c * d)
        p2 = (
            d + t,
            -90,
            t * 0.5,
            135,
            t * 2 ** 0.5,
            135,
            d + 2 * t + s * 0.5 * t)
        p3 = (c * d - s * c * 0.2 * t, -a, 0)

        if not reverse:
            self.polyline(*p1)
            self.corner(-180, r)
            self.polyline(*p2)
            self.corner(-180 + 2 * a, r)
            self.polyline(*p3)
        else:
            self.polyline(*reversed(p3))
            self.corner(-180 + 2 * a, r)
            self.polyline(*reversed(p2))
            self.corner(-180, r)
            self.polyline(*reversed(p1))

    def hookWidth(self):
        t = self.thickness
        a = self.settings.angle
        d = self.settings.depth
        r = self.settings.bottom_radius
        c = math.cos(math.radians(a))
        s = math.sin(math.radians(a))

        return 2 * s * d * c + 0.5 * c * t + c * 4 * r

    def hookOffset(self):
        a = self.settings.angle
        d = self.settings.depth
        r = self.settings.bottom_radius
        c = math.cos(math.radians(a))
        s = math.sin(math.radians(a))

        return s * d * c + 2 * r

    def finger(self, length):
        t = self.thickness
        self.polyline(
            2 * t,
            90,
            length,
            90,
            2 * t,
        )

    def __call__(self, length, **kw):
        t = self.thickness
        self.edge(4 * t)
        self.hook()
        self.finger(2 * t)
        self.hook(reverse=True)

        self.edge(length - 2 * (6 * t + 2 * self.hookWidth()))

        self.hook()
        self.finger(2 * t)
        self.hook(reverse=True)
        self.edge(4 * t)

    def margin(self):
        return 2 * self.thickness


class ClickEdge(ClickConnector):
    char = "C"
    description = "Click on (top)"

    def startwidth(self):
        return self.boxes.thickness

    def margin(self):
        return 0.0

    def __call__(self, length, **kw):
        t = self.thickness
        o = self.hookOffset()
        w = self.hookWidth()
        p1 = (
            4 * t + o,
            90,
            t,
            -90,
            2 * (t + w - o),
            -90,
            t,
            90,
            0)
        self.polyline(*p1)
        self.edge(length - 2 * (6 * t + 2 * w) + 2 * o)
        self.polyline(*reversed(p1))


#############################################################################
####     Dove Tail Joints
#############################################################################

class DoveTailSettings(Settings):
    """Settings for Dove Tail Joints

Values:

* absolute

  * angle : 50 : how much should fingers widen (-80 to 80)

* relative (in multiples of thickness)

  * size : 3 : from one middle of a dove tail to another
  * depth : 1.5 : how far the dove tails stick out of/into the edge
  * radius : 0.2 : radius used on all four corners

"""
    absolute_params = {
        "angle": 50,
    }

    relative_params = {
        "size": 3,
        "depth": 1.5,
        "radius": 0.2,
    }


class DoveTailJoint(BaseEdge):
    """Edge with dove tail joints """

    char = 'd'
    description = "Dove Tail Joint"
    positive = True

    def __call__(self, length, **kw):
        s = self.settings
        radius = max(s.radius, self.boxes.burn)  # no smaller than burn
        positive = self.positive
        a = s.angle + 90
        alpha = 0.5 * math.pi - math.pi * s.angle / 180.0

        l1 = radius / math.tan(alpha / 2.0)
        diffx = 0.5 * s.depth / math.tan(alpha)
        l2 = 0.5 * s.depth / math.sin(alpha)

        sections = int((length) // (s.size * 2))
        leftover = length - sections * s.size * 2

        p = 1 if positive else -1

        self.edge((s.size + leftover) / 2.0 + diffx - l1)

        for i in range(sections):
            self.corner(-1 * p * a, radius)
            self.edge(2 * (l2 - l1))
            self.corner(p * a, radius)
            self.edge(2 * (diffx - l1) + s.size)
            self.corner(p * a, radius)
            self.edge(2 * (l2 - l1))
            self.corner(-1 * p * a, radius)

            if i < sections - 1:  # all but the last
                self.edge(2 * (diffx - l1) + s.size)

        self.edge((s.size + leftover) / 2.0 + diffx - l1)
        self.ctx.translate(*self.ctx.get_current_point())

    def margin(self):
        """ """
        return self.settings.depth


class DoveTailJointCounterPart(DoveTailJoint):
    """Edge for other side of dove joints """
    char = 'D'
    description = "Dove Tail Joint (opposing side)"

    positive = False

    def margin(self):
        return 0.0


class FlexSettings(Settings):
    """Settings for one directional Flex Cuts

Values:

* absolute

 * stretch : 1.05 : Hint of how much the flex part should be shortend

* relative (in multiples of thickness)

 * distance : 0.5 : width of the pattern perpendicular to the cuts
 * connection : 1.0 : width of the gaps in the cuts
 * width" : 5.0 : width of the pattern in direction of the cuts

"""
    relative_params = {
        "distance": 0.5,
        "connection": 1.0,
        "width": 5.0,
    }

    absolute_params = {
        "stretch": 1.05,
    }


class FlexEdge(BaseEdge):
    """Edge with flex cuts - use straight edge for the opposing side"""
    char = 'X'
    description = "Flex cut"

    def __call__(self, x, h, **kw):
        dist = self.settings.distance
        connection = self.settings.connection
        width = self.settings.width

        burn = self.boxes.burn
        h += 2 * burn
        lines = int(x // dist)
        leftover = x - lines * dist
        sections = int((h - connection) // width)
        sheight = ((h - connection) / sections) - connection

        for i in range(1, lines):
            pos = i * dist + leftover / 2

            if i % 2:
                self.ctx.move_to(pos, 0)
                self.ctx.line_to(pos, connection + sheight)

                for j in range((sections - 1) // 2):
                    self.ctx.move_to(pos, (2 * j + 1) * sheight + (2 * j + 2) * connection)
                    self.ctx.line_to(pos, (2 * j + 3) * (sheight + connection))

                if not sections % 2:
                    self.ctx.move_to(pos, h - sheight - connection)
                    self.ctx.line_to(pos, h)
            else:
                if sections % 2:
                    self.ctx.move_to(pos, h)
                    self.ctx.line_to(pos, h - connection - sheight)

                    for j in range((sections - 1) // 2):
                        self.ctx.move_to(
                            pos, h - ((2 * j + 1) * sheight + (2 * j + 2) * connection))
                        self.ctx.line_to(
                            pos, h - (2 * j + 3) * (sheight + connection))

                else:
                    for j in range(sections // 2):
                        self.ctx.move_to(pos,
                                         h - connection - 2 * j * (sheight + connection))
                        self.ctx.line_to(pos, h - 2 * (j + 1) * (sheight + connection))

        self.ctx.move_to(0, 0)
        self.ctx.line_to(x, 0)
        self.ctx.translate(*self.ctx.get_current_point())

class GearSettings(Settings):

    absolute_params = {
        "dimension" : 3.0,
        "angle" : 20.0,
        "profile_shift" : 20.0,
        "clearance" : 0.0,
        }

    relative_params = {}

class RackEdge(BaseEdge):

    char = "R"

    def __init__(self, boxes, settings):
        super(RackEdge, self).__init__(boxes, settings)
        self.gear = gears.Gears(boxes)

    def __call__(self, length, **kw):
        params = self.settings.values.copy()
        params["draw_rack"] = True
        params["rack_base_height"] = -1E-36
        params["rack_teeth_length"] = int(length // params["dimension"])
        params["rack_base_tab"] = (length - (params["rack_teeth_length"]) * params["dimension"]) / 2.0
        s_tmp = self.boxes.spacing
        self.boxes.spacing = 0
        self.moveTo(length, 0, 180)
        self.gear(move="", **params)
        self.moveTo(0, 0, 180)
        self.boxes.spacing = s_tmp

    def margin(self):
        return self.settings.dimension * 1.1
