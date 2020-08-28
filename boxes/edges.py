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
import abc

from boxes import gears

def getDescriptions():
    d = {edge.char: edge.description for edge in globals().values()
         if inspect.isclass(edge) and issubclass(edge, BaseEdge)
         and edge.char}
    d['j'] = d['i'] + " (other end)"
    d['J'] = d['I'] + " (other end)"
    d['k'] = d['i'] + " (both ends)"
    d['K'] = d['I'] + " (both ends)"
    d['O'] = d['o'] + ' (other end)'
    d['P'] = d['p'] + ' (other end)'
    d['U'] = d['u'] + ' top side'
    d['v'] = d['u'] + u' for 90° lid'
    d['V'] = d['u'] + u' 90° lid'
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
            # Handle choices
            choices = None
            if isinstance(default, tuple):
                choices = default
                t = type(default[0])
                for val in default:
                    if (type(val) is not t or
                        type(val) not in (bool, int, float, str)):
                        raise ValueError("Type not supported: %r", val)
                default = default[0]

            # Overwrite default
            if name in defaults:
                default = defaults[name]

            if type(default) not in (bool, int, float, str):
                raise ValueError("Type not supported: %r", default)
            if type(default) is bool:
                from boxes import BoolArg
                t = BoolArg()
            else:
                t = type(default)

            group.add_argument("--%s_%s" % (prefix, name),
                               type=t,
                               action="store", default=default,
                               choices=choices,
                               help=descriptions.get(name))

    def __init__(self, thickness, relative=True, **kw):
        self.values = {}
        for name, value in self.absolute_params.items():
            if isinstance(value, tuple):
                value = value[0]
            if type(value) not in (bool, int, float, str):
                raise ValueError("Type not supported: %r", value)
            self.values[name] = value

        self.thickness = thickness
        factor = 1.0
        if relative:
            factor = thickness
        for name, value in self.relative_params.items():
            self.values[name] = value * factor
        self.setValues(thickness, relative, **kw)

    def edgeObjects(self, boxes, chars="", add=True):
        """
        Generate Edge objects using this kind of settings

        :param boxes: Boxes object
        :param chars: sequence of chars to be used by Edge objects
        :param add: add the resulting Edge objects to the Boxes object's edges

        """
        edges = []
        return self._edgeObjects(edges, boxes, chars, add)

    def _edgeObjects(self, edges, boxes, chars, add):
        for i, edge in enumerate(edges):
            try:
                char = chars[i]
                edge.char = char
            except IndexError:
                pass
            except TypeError:
                pass
        if add:
            boxes.addParts(edges)
        return edges

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
        for name, value in kw.items():
            if name in self.absolute_params:
                self.values[name] = value
            elif name in self.relative_params:
                self.values[name] = value * factor
            else:
                raise ValueError("Unknown parameter for %s: %s" % (
                    self.__class__.__name__, name))
        self.checkValues()

    def checkValues(self):
        """
        Check if all values are in the right range. Raise ValueError if needed
        """
        return

    def __getattr__(self, name):
        if "values" in self.__dict__ and name in self.values:
            return self.values[name]
        raise AttributeError

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

    @abc.abstractmethod
    def __call__(self, length, **kw):
        pass

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
    positive = False

    def __call__(self, length, bedBolts=None, bedBoltSettings=None, **kw):
        """Draw edge of length mm"""
        if bedBolts:
            # distribute the bolts aequidistantly
            interval_length = length / bedBolts.bolts
            if self.positive:
                d = (bedBoltSettings or self.bedBoltSettings)[0]
                for i in range(bedBolts.bolts):
                    self.hole(0.5 * interval_length,
                              0.5 * self.thickness, 0.5 * d)
                    self.edge(interval_length, tabs=
                              (i == 0 or i == bedBolts.bolts - 1))
            else:
                for i in range(bedBolts.bolts):
                    self.bedBoltHole(interval_length, bedBoltSettings, tabs=
                                     (i == 0 or i == bedBolts.bolts - 1))
        else:
            self.edge(length, tabs=2)


class OutSetEdge(Edge):
    """Straight edge out set by one thickness"""
    char = 'E'
    description = "Straight Edge (outset by thickness)"
    positive = True

    def startwidth(self):
        return self.boxes.thickness


#############################################################################
####     GroovedEdge
#############################################################################

class GroovedSettings(Settings):
    """Settings for Grooved Edge
Values:

* absolute_params

 * style : "arc" : the style of grooves
 * tri_angle : 30 : the angle of triangular cuts
 * arc_angle : 120 : the angle of arc cuts
 * width : 0.2 : the groove width (fraction of the edge length)
 * gap : 0.1 : gap between grooves (fraction of the edge length)
 * margin : 0.3 : minimum margin around grooves (fraction of the edge length)
 * inverse : False : invert the groove directions
 * interleave : False : interleave groove directions
"""

    PARAM_ARC = "arc"
    PARAM_FLAT = "flat"
    PARAM_SOFTARC = "softarc"
    PARAM_TRIANGLE = "triangle"

    absolute_params = {
        "style": (PARAM_ARC, PARAM_FLAT, PARAM_TRIANGLE, PARAM_SOFTARC),
        "tri_angle": 30,
        "arc_angle": 120,
        "width": 0.2,
        "gap": 0.1,
        "margin": 0.3,
        "inverse": False,
        "interleave": False,
    }

    def edgeObjects(self, boxes, chars="zZ", add=True):
        edges = [GroovedEdge(boxes, self),
                 GroovedEdgeCounterPart(boxes, self)]
        return self._edgeObjects(edges, boxes, chars, add)


class GroovedEdgeBase(BaseEdge):
    def is_inverse(self):
        return self.settings.inverse != self.inverse

    def __call__(self, length, **kw):
        if length == 0.0:
            return

        style = self.settings.style
        width = self.settings.width
        margin = self.settings.margin
        gap = self.settings.gap
        interleave = self.settings.interleave

        # Check how many grooves fit
        count = int((1 - 2 * margin + gap) / (width + gap))
        inside_width = count * (width + gap) - gap
        margin = (1 - inside_width) / 2

        # Convert to actual length
        margin = length * margin
        gap = length * gap
        width = length * width

        # Determine the initial inversion
        inv = 1 if self.is_inverse() else -1
        if interleave and self.inverse and count % 2 == 0:
            inv = -inv

        # The edge until the first groove
        self.edge(margin)

        # Grooves
        for i in range(count):
            if i > 0:
                self.edge(gap)
                if interleave:
                    inv = -inv
            if style == GroovedSettings.PARAM_FLAT:
                self.edge(width)
            elif style == GroovedSettings.PARAM_ARC:
                angle = self.settings.arc_angle / 2
                side_length = width / math.sin(math.radians(angle)) / 2
                self.corner(inv * -angle)
                self.corner(inv * angle, side_length)
                self.corner(inv * angle, side_length)
                self.corner(inv * -angle)
            elif style == GroovedSettings.PARAM_SOFTARC:
                angle = self.settings.arc_angle / 2
                side_length = width / math.sin(math.radians(angle)) / 4
                self.corner(inv * -angle, side_length)
                self.corner(inv * angle, side_length)
                self.corner(inv * angle, side_length)
                self.corner(inv * -angle, side_length)
            elif style == GroovedSettings.PARAM_TRIANGLE:
                angle = self.settings.tri_angle
                side_length = width / math.cos(math.radians(angle)) / 2
                self.corner(inv * -angle)
                self.edge(side_length)
                self.corner(inv * 2 * angle)
                self.edge(side_length)
                self.corner(inv * -angle)
            else:
                raise ValueError("Unknown GroovedEdge style: %s)" % style)

        # The final edge
        self.edge(margin)


class GroovedEdge(GroovedEdgeBase):
    description = """Edge with grooves"""
    char = 'z'
    inverse = False


class GroovedEdgeCounterPart(GroovedEdgeBase):
    description = """Edge with grooves (opposing side)"""
    char = 'Z'
    inverse = True


#############################################################################
####     Gripping Edge
#############################################################################

class GripSettings(Settings):
    """Settings for GrippingEdge
Values:

* absolute_params

 * style : "wave : "wave" or "bumps"
 * outset : True : extend outward the straight edge

* relative (in multiples of thickness)

 * depth : 0.3 : depth of the grooves

"""

    absolute_params = {
        "style": ("wave", "bumps"),
        "outset": True,
    }

    relative_params = {
        "depth": 0.3,
    }

    def edgeObjects(self, boxes, chars="g", add=True):
        edges = [GrippingEdge(boxes, self)]
        return self._edgeObjects(edges, boxes, chars, add)

class GrippingEdge(BaseEdge):
    description = """Corrugated edge useful as an gipping area"""
    char = 'g'

    def wave(self, length):
        depth = self.settings.depth
        grooves = int(length // (depth * 2.0)) + 1
        depth = length / grooves / 4.0

        o = 1 if self.settings.outset else -1
        for groove in range(grooves):
            self.corner(o * -90, depth)
            self.corner(o * 180, depth)
            self.corner(o * -90, depth)

    def bumps(self, length):
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
        return max((e.margin() + e.startwidth() for e in self.types)) - self.types[0].startwidth()

    def __call__(self, length, **kw):
        if length and abs(length - self.length) > 1E-5:
            raise ValueError("Wrong length for CompoundEdge")
        lastwidth = self.types[0].startwidth()

        for e, l in zip(self.types, self.lengths):
            self.step(e.startwidth() - lastwidth)
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
        super(SlottedEdge, self).__init__(boxes, Settings(boxes.thickness))

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
                Slot(self.boxes, self.slots)(self.settings.thickness)
            else:
                self.edge(self.settings.thickness)

        self.edge(self.sections[-1])


#############################################################################
####     Finger Joints
#############################################################################

class FingerJointSettings(Settings):
    """Settings for Finger Joints

Values:

* absolute
  * style : "rectangular" : style of the fingers
  * surroundingspaces : 2 : maximum space at the start and end in multiple of normal spaces
  * angle: 90 : Angle of the walls meeting

* relative (in multiples of thickness)

  * space : 2.0 : space between fingers
  * finger : 2.0 : width of the fingers
  * width : 1.0 : width of finger holes
  * edge_width : 1.0 : space below holes of FingerHoleEdge
  * play : 0.0 : extra space to allow finger move in and out

"""

    absolute_params = {
        "style" : ("rectangular", "springs"),
        "surroundingspaces": 2.0,
        "angle" : 90.0,
    }

    relative_params = {
        "space": 2.0,
        "finger": 2.0,
        "width": 1.0,
        "edge_width": 1.0,
        "play" : 0.0,
    }

    def checkValues(self):
        if abs(self.space + self.finger) < 0.1:
            raise ValueError("FingerJointSettings: space + finger must not be close to zero")

    def edgeObjects(self, boxes, chars="fFh", add=True):
        edges = [FingerJointEdge(boxes, self),
                 FingerJointEdgeCounterPart(boxes, self),
                 FingerHoleEdge(boxes, self),
        ]
        return self._edgeObjects(edges, boxes, chars, add)

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

    def fingerLength(self, angle):
        if angle >=90:
            return self.settings.thickness, 0

        if angle < 0:
            return math.sin(math.radians(-angle)) * self.settings.thickness, 0

        # 0 to 90
        a = 90 - (180-angle) / 2.0
        fingerlength = self.settings.thickness * math.tan(math.radians(a))
        b = 90-2*a
        spacerecess = -math.sin(math.radians(b)) * fingerlength
        return fingerlength, spacerecess

class FingerJointEdge(BaseEdge, FingerJointBase):
    """Finger joint edge """
    char = 'f'
    description = "Finger Joint"
    positive = True

    def __call__(self, length, bedBolts=None, bedBoltSettings=None, **kw):

        positive = self.positive

        s, f, thickness = self.settings.space, self.settings.finger, self.settings.thickness

        p = 1 if positive else -1

        fingers, leftover = self.calcFingers(length, bedBolts)

        if not positive:
            play = self.settings.play
            f += play
            s -= play
            leftover -= play

        self.edge(leftover / 2.0, tabs=1)

        l1,l2 = self.fingerLength(self.settings.angle)
        h = l1-l2

        d = (bedBoltSettings or self.bedBoltSettings)[0]

        for i in range(fingers):
            if i != 0:
                if not positive and bedBolts and bedBolts.drawBolt(i):
                    self.hole(0.5 * s,
                              0.5 * self.settings.thickness, 0.5 * d)

                if positive and bedBolts and bedBolts.drawBolt(i):
                    self.bedBoltHole(s, bedBoltSettings)
                else:
                    self.edge(s)

            if positive and self.settings.style == "springs":
                self.polyline(
                    0, -90 * p, 0.8*h, (90 * p, 0.2*h),
                    0.1 * h, 90, 0.9*h, -180, 0.9*h, 90,
                    f - 0.6*h,
                    90, 0.9*h, -180, 0.9*h, 90, 0.1*h,
                (90 * p, 0.2 *h), 0.8*h, -90 * p)
            else:
                self.polyline(0, -90 * p, h, 90 * p, f, 90 * p, h, -90 * p)

        self.edge(leftover / 2.0, tabs=1)

    def margin(self):
        """ """
        widths = self.fingerLength(self.settings.angle)
        if self.positive:
            return widths[0] - widths[1]
        else:
            return 0

    def startwidth(self):
        widths = self.fingerLength(self.settings.angle)
        return widths[self.positive]


class FingerJointEdgeCounterPart(FingerJointEdge):
    """Finger joint edge - other side"""
    char = 'F'
    description = "Finger Joint (opposing side)"
    positive = False


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
        with self.boxes.saved_context():
            self.boxes.moveTo(x, y, angle)
            s, f = self.settings.space, self.settings.finger
            p = self.settings.play
            b = self.boxes.burn
            fingers, leftover = self.calcFingers(length, bedBolts)

            if self.boxes.debug:
                self.ctx.rectangle(b, -self.settings.width / 2 + b,
                                   length - 2 * b, self.settings.width - 2 * b)
            for i in range(fingers):
                pos = leftover / 2.0 + i * (s + f)

                if bedBolts and bedBolts.drawBolt(i):
                    d = (bedBoltSettings or self.boxes.bedBoltSettings)[0]
                    self.boxes.hole(pos - 0.5 * s, 0, d * 0.5)

                self.boxes.rectangularHole(pos + 0.5 * f, 0,
                                           f+p, self.settings.width+p)

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
        with self.saved_context():
            self.fingerHoles(
                0, self.burn + dist + self.settings.thickness / 2, length, 0,
                bedBolts=bedBolts, bedBoltSettings=bedBoltSettings)
        self.edge(length, tabs=2)

    def startwidth(self):
        """ """
        return self.fingerHoles.settings.edge_width + self.settings.thickness


class CrossingFingerHoleEdge(Edge):
    """Edge with holes for finger joints 90° above"""

    description = "Edge (orthogonal Finger Joint Holes)"
    char = '|'

    def __init__(self, boxes, height, fingerHoles=None, **kw):
        super(CrossingFingerHoleEdge, self).__init__(boxes, None, **kw)

        self.fingerHoles = fingerHoles or boxes.fingerHolesAt
        self.height = height

    def __call__(self, length, **kw):
        self.fingerHoles(length / 2.0, self.burn, self.height)
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

    def checkValues(self):
        if self.angle < 20:
            raise ValueError("StackableSettings: 'angle' is too small. Use value >= 20")
        if self.angle > 260:
            raise ValueError("StackableSettings: 'angle' is too big. Use value < 260")

    def edgeObjects(self, boxes, chars="sS", add=True, fingersettings=None):
        fingersettings = fingersettings or boxes.edges["f"].settings
        edges = [StackableEdge(boxes, self, fingersettings),
                 StackableEdgeTop(boxes, self, fingersettings)]
        return self._edgeObjects(edges, boxes, chars, add)

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

        self.boxes.edge(s.width, tabs=1)
        self.boxes.corner(p * s.angle, r)
        self.boxes.corner(-p * s.angle, r)
        self.boxes.edge(length - 2 * s.width - 4 * l)
        self.boxes.corner(-p * s.angle, r)
        self.boxes.corner(p * s.angle, r)
        self.boxes.edge(s.width, tabs=1)

    def _height(self):
        return self.settings.height + self.settings.holedistance + self.settings.thickness

    def startwidth(self):
        return self._height() if self.bottom else 0

    def margin(self):
        return 0 if self.bottom else self.settings.height


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

 * style : "outset" : "outset" or "flush"
 * outset : False : have lid overlap at the sides (similar to OutSetEdge)
 * pinwidth : 1.0 : set to lower value to get disks surrounding the pins
 * grip_percentage" : 0 : percentage of the lid that should get grips

* relative (in multiples of thickness)

 * hingestrength : 1 : thickness of the arc holding the pin in place
 * axle : 2 : diameter of the pin hole
 * grip_length : 0 : fixed length of the grips on he lids

"""
    absolute_params = {
        "style": ("outset", "flush"),
        "outset": False,
        "pinwidth": 0.5,
        "grip_percentage": 0,
    }

    relative_params = {
        "hingestrength": 1,  # 1.5-0.5*2**0.5,
        "axle": 2,
        "grip_length": 0,
    }

    def edgeObjects(self, boxes, chars="iIjJkK", add=True):
        edges = [
            Hinge(boxes, self, 1),
            HingePin(boxes, self, 1),
            Hinge(boxes, self, 2),
            HingePin(boxes, self, 2),
            Hinge(boxes, self, 3),
            HingePin(boxes, self, 3),
        ]
        return self._edgeObjects(edges, boxes, chars, add)

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
        return 3 * self.settings.thickness

    def outset(self, _reversed=False):
        t = self.settings.thickness
        r = 0.5 * self.settings.axle
        alpha = math.degrees(math.asin(0.5 * t / r))
        pinl = (self.settings.axle ** 2 - self.settings.thickness ** 2) ** 0.5 * self.settings.pinwidth
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
            self.boxes.rectangularHole(-pos, -0.5 * t, pinl, self.settings.thickness)
        else:
            self.boxes.rectangularHole(pos, -0.5 * t, pinl, self.settings.thickness)
            self.polyline(*hinge)

    def outsetlen(self):
        t = self.settings.thickness
        r = 0.5 * self.settings.axle
        alpha = math.degrees(math.asin(0.5 * t / r))
        pos = math.cos(math.radians(alpha)) * r

        return 2 * pos + 1.5 * t

    def flush(self, _reversed=False):
        t = self.settings.thickness

        hinge = (
            0, -90,
            0.5 * t,
            (180, 0.5 * self.settings.axle + self.settings.hingestrength), 0,
            (-90, 0.5 * t), 0
        )
        pos = 0.5 * self.settings.axle + self.settings.hingestrength
        pinl = (self.settings.axle ** 2 - self.settings.thickness ** 2) ** 0.5 * self.settings.pinwidth

        if _reversed:
            hinge = reversed(hinge)
            self.hole(0.5 * t + pos, -0.5 * t, 0.5 * self.settings.axle)
            self.boxes.rectangularHole(0.5 * t + pos, -0.5 * t, pinl, self.settings.thickness)
        else:
            self.hole(pos, -0.5 * t, 0.5 * self.settings.axle)
            self.boxes.rectangularHole(pos, -0.5 * t, pinl, self.settings.thickness)

        self.polyline(*hinge)

    def flushlen(self):
        return self.settings.axle + 2 * self.settings.hingestrength + 0.5 * self.settings.thickness

    def __call__(self, l, **kw):
        hlen = getattr(self, self.settings.style + 'len', self.outsetlen)()

        if self.layout & 1:
            getattr(self, self.settings.style, self.outset)()

        self.edge(l - (self.layout & 1) * hlen - bool(self.layout & 2) * hlen,
                  tabs=2)

        if self.layout & 2:
            getattr(self, self.settings.style, self.outset)(True)


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
        return self.settings.thickness

    def outset(self, _reversed=False):
        t = self.settings.thickness
        r = 0.5 * self.settings.axle
        alpha = math.degrees(math.asin(0.5 * t / r))
        pos = math.cos(math.radians(alpha)) * r
        pinl = (self.settings.axle ** 2 - self.settings.thickness ** 2) ** 0.5 * self.settings.pinwidth
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

    def outsetlen(self):
        t = self.settings.thickness
        r = 0.5 * self.settings.axle
        alpha = math.degrees(math.asin(0.5 * t / r))
        pos = math.cos(math.radians(alpha)) * r

        if self.settings.outset:
            return 2 * pos + 1.5 * self.settings.thickness
        else:
            return 2 * pos

    def flush(self, _reversed=False):
        t = self.settings.thickness
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

    def flushlen(self):
        l = self.settings.hingestrength + self.settings.axle

        if self.settings.outset:
            l += self.settings.hingestrength + 0.5 * self.settings.thickness

        return l

    def __call__(self, l, **kw):
        plen = getattr(self, self.settings.style + 'len', self.outsetlen)()
        glen = l * self.settings.grip_percentage + \
               self.settings.grip_length

        if not self.settings.outset:
            glen = 0.0

        glen = min(glen, l - plen)

        if self.layout & 1 and self.layout & 2:
            getattr(self, self.settings.style, self.outset)()
            self.edge(l - 2 * plen, tabs=2)
            getattr(self, self.settings.style, self.outset)(True)
        elif self.layout & 1:
            getattr(self, self.settings.style, self.outset)()
            self.edge(l - plen - glen, tabs=2)
            self.edges['g'](glen)
        else:
            self.edges['g'](glen)
            self.edge(l - plen - glen, tabs=2)
            getattr(self, self.settings.style, self.outset)(True)

#############################################################################
####     Chest Hinge
#############################################################################

class ChestHingeSettings(Settings):
    """Settings for Chest Hinges
Values:

* relative (in multiples of thickness)

 * pin_height : 2.0 : radius of the disc rotating in the hinge
 * hinge_strength : 1.0 : thickness of the arc holding the pin in place
"""

    relative_params = {
        "pin_height" : 2.0,
        "hinge_strength" : 1.0,
        "play" : 0.1,
        }

    def checkValues(self):
        if self.pin_height / self.thickness < 1.2:
            raise ValueError("ChestHingeSettings: 'pin_height' must be >= 1.2")

    def pinheight(self):
        return ((0.9*self.pin_height)**2-self.thickness**2)**0.5

    def edgeObjects(self, boxes, chars="oOpPqQ", add=True):
        edges = [
            ChestHinge(boxes, self),
            ChestHinge(boxes, self, 1),
            ChestHingeTop(boxes, self),
            ChestHingeTop(boxes, self, 1),
            ChestHingePin(boxes, self),
            ChestHingeFront(boxes, self),
        ]
        return self._edgeObjects(edges, boxes, chars, add)

class ChestHinge(BaseEdge):

    description = "Edge with chest hinge"

    char = "o"

    def __init__(self, boxes, settings=None, reversed=False):
        super(ChestHinge, self).__init__(boxes, settings)

        self.reversed = reversed
        self.char = "oO"[reversed]
        self.description = self.description + (' (start)', ' (end)')[reversed]

    def __call__(self, l, **kw):
        t = self.settings.thickness
        p = self.settings.pin_height
        s = self.settings.hinge_strength
        pinh = self.settings.pinheight()
        if self.reversed:
            self.hole(l+t, 0, p, tabs=4)
            self.rectangularHole(l+0.5*t, -0.5*pinh, t, pinh)
        else:
            self.hole(-t, -s-p, p, tabs=4)
            self.rectangularHole(-0.5*t, -s-p-0.5*pinh, t, pinh)

        poly = (0, -180, t, (270, p+s), 0, -90, l+t-p-s)
        if self.reversed:
            poly = reversed(poly)
        self.polyline(*poly)

    def margin(self):
        if self.reversed:
            return 0*(self.settings.pin_height+self.settings.hinge_strength)
        else:
            return 1*(self.settings.pin_height+self.settings.hinge_strength)

    def startwidth(self):
        if self.reversed:
            return self.settings.pin_height+self.settings.hinge_strength
        return 0

    def endwidth(self):
        if self.reversed:
            return 0
        return self.settings.pin_height+self.settings.hinge_strength

class ChestHingeTop(ChestHinge):

    "Edge above a chest hinge"

    char = "p"

    def __init__(self, boxes, settings=None, reversed=False):
        super(ChestHingeTop, self).__init__(boxes, settings)

        self.reversed = reversed
        self.char = "oO"[reversed]
        self.description = self.description + (' (start)', ' (end)')[reversed]

    def __call__(self, l, **kw):
        t = self.settings.thickness
        p = self.settings.pin_height
        s = self.settings.hinge_strength
        play = self.settings.play
        poly = (0, -180, t, -180, 0, (-90, p+s+play), 0, 90, l+t-p-s-play)
        if self.reversed:
            poly = reversed(poly)
        self.polyline(*poly)

    def startwidth(self):
        if self.reversed:
            return self.settings.play+self.settings.pin_height+self.settings.hinge_strength
        return 0

    def endwidth(self):
        if self.reversed:
            return 0
        return self.settings.play+self.settings.pin_height+self.settings.hinge_strength

    def margin(self):
        if self.reversed:
            return 0.
        else:
            return 1*(self.settings.play+self.settings.pin_height+self.settings.hinge_strength)

class ChestHingePin(BaseEdge):

    description = "Edge with pins for an chest hinge"

    char = "q"

    def __call__(self, l, **kw):
        t = self.settings.thickness
        p = self.settings.pin_height
        s = self.settings.hinge_strength
        pinh = self.settings.pinheight()
        poly = [0, -90, s+p-pinh, -90, t, 90, pinh, 90,]
        poly += [l+2*t,] + list(reversed(poly))
        self.polyline(*poly)

    def margin(self):
        return (self.settings.pin_height+self.settings.hinge_strength)


class ChestHingeFront(Edge):

    description = "Edge opposing a chest hinge"

    char = "Q"

    def startwidth(self):
        return self.settings.pin_height+self.settings.hinge_strength

#############################################################################
####     Cabinet Hinge
#############################################################################

class CabinetHingeSettings(Settings):
    """Settings for Cabinet Hinges
Values:

* absolute_params

 * bore : 3.2 : diameter of the pin hole in mm
 * eyes_per_hinge : 5 : pieces per hinge
 * hinges : 2 : number of hinges per edge
 * style : inside : style of hinge used

* relative (in multiples of thickness)

 * eye : 1.5 : radius of the eye (in multiples of thickness)
 * play : 0.05 : space between eyes (in multiples of thickness)
 * spacing : 2.0 : minimum space around the hinge
"""
    absolute_params = {
        "bore": 3.2,
        "eyes_per_hinge" : 5,
        "hinges" : 2,
        "style" : ("inside", "outside"),
    }

    relative_params = {
        "eye": 1.5,
        "play" : 0.05,
        "spacing": 2.0,
    }

    def edgeObjects(self, boxes, chars="uUvV", add=True):
        edges = [CabinetHingeEdge(boxes, self),
                 CabinetHingeEdge(boxes, self, top=True),
                 CabinetHingeEdge(boxes, self, angled=True),
                 CabinetHingeEdge(boxes, self, top=True, angled=True),
        ]
        for e, c in zip(edges, chars):
            e.char = c
        return self._edgeObjects(edges, boxes, chars, add)

class CabinetHingeEdge(BaseEdge):
    """Edge with cabinet hinges"""

    char = "u"
    description = "Edge with cabinet hinges"

    def __init__(self, boxes, settings=None, top=False, angled=False):
        super(CabinetHingeEdge, self).__init__(boxes, settings)
        self.top = top
        self.angled = angled
        self.char = "uUvV"[bool(top)+2*bool(angled)]

    def startwidth(self):
        return self.settings.thickness if self.top and self.angled else 0.0


    def __poly(self):
        n = self.settings.eyes_per_hinge
        p = self.settings.play
        e = self.settings.eye
        t = self.settings.thickness
        spacing = self.settings.spacing

        if self.settings.style == "outside" and self.angled:
            e = t
        elif self.angled and not self.top:
            # move hinge up to leave space for lid
            e -= t

        if self.top:
            # start with space
            poly = [spacing, 90, e+p, 180, 0]
        else:
            # start with hinge eye
            poly = [spacing+p, 90, e+p, 0]
        for i in range(n):
            if (i % 2) ^ self.top:
                # space
                poly += [90, t + 2*p, 90]
            else:
                # hinge eye
                poly += [t-p, -90, t, -90, t-p]

        if (n % 2) ^ self.top:
            # stopped with hinge eye
            poly += [0, e+p, 90, p+spacing]
        else:
            # stopped with space
            poly += [0, 180, e+p, 90, 0+spacing ]

        width = (t+p) * n + p + 2 * spacing

        return poly, width

    def __call__(self, l, **kw):
        n = self.settings.eyes_per_hinge
        p = self.settings.play
        e = self.settings.eye
        t = self.settings.thickness
        hn = self.settings.hinges

        poly, width = self.__poly()

        if self.settings.style == "outside" and self.angled:
            e = t
        elif self.angled and not self.top:
            # move hinge up to leave space for lid
            e -= t

        hn = min(hn, int(l // width))

        if hn == 1:
            self.edge((l-width) / 2, tabs=2)

        for j in range(hn):
            for i in range(n):
                if not (i % 2) ^ self.top:
                    self.rectangularHole(self.settings.spacing+0.5*t+p+i*(t+p), e+2.5*t, t, t)
            self.polyline(*poly)
            if j < (hn - 1):
                self.edge((l-hn*width) / (hn-1), tabs=2)

        if hn == 1:
            self.edge((l-width) / 2, tabs=2)

    def parts(self, move=None):
        e, b = self.settings.eye, self.settings.bore
        t = self.settings.thickness

        n = self.settings.eyes_per_hinge * self.settings.hinges
        pairs = n // 2 + 2 * (n % 2)

        if self.settings.style == "outside":
            th = 2*e + 4*t
            tw = n * (max(3*t, 2*e) + self.boxes.spacing)
        else:
            th = 4*e+3*t+self.boxes.spacing
            tw = max(e, 2*t) * pairs

        if self.move(tw, th, move, True):
            return

        if self.settings.style == "outside":
            ax = max(t/2, e-t)
            self.moveTo(t+ax)
            for i in range(n):
                if self.angled:
                    if i > n // 2:
                        l = 4 * t + ax
                    else:
                        l = 5 * t + ax
                else:
                    l = 3 * t + e
                self.hole(0, e, b/2.0)
                da = math.asin((t-ax) / e)
                dad = math.degrees(da)
                dy = e * (1-math.cos(da))
                self.polyline(0, (180-dad, e), 0, (-90+dad), dy+l-e, (90, t))
                self.polyline(0, 90, t, -90, t, 90, t, 90, t, -90, t, -90, t,
                              90, t, 90, (ax+t)-e, -90, l-3*t, (90, e))
                self.moveTo(2*max(e, 1.5*t) + self.boxes.spacing)

            self.move(tw, th, move)
            return

        if e <= 2*t:
            if self.angled:
                corner = [2*e-t, (90, 2*t - e), 0, -90, t, (90, e)]
            else:
                corner = [2*e, (90, 2*t)]
        else:
            a = math.asin(2*t/e)
            ang = math.degrees(a)
            corner = [e*(1-math.cos(a))+2*t, -90+ang, 0, (180-ang, e)]
        self.moveTo(max(e, 2*t))
        for i in range(n):
            self.hole(0, e, b/2.0)
            self.polyline(*[0, (180, e), 0, -90, t, 90, t, -90, t, -90, t, 90, t, 90, t, (90, t)] + corner)
            self.moveTo(self.boxes.spacing, 4*e+3*t+self.boxes.spacing, 180)
            if i % 2:
                self.moveTo(2*max(e, 2*t) + 2*self.boxes.spacing)

        self.move(th, tw, move)

#############################################################################
####     Slide-on lid
#############################################################################

class LidSettings(FingerJointSettings):

    """Settings for Slide-on Lids

Note that edge_width below also determines how much the sides extend above the lid.

Inherited:

    """
    __doc__ += FingerJointSettings.__doc__

    absolute_params = FingerJointSettings.absolute_params.copy()
    relative_params = FingerJointSettings.relative_params.copy()

    relative_params.update( {
        "play": 0.05,
        "finger": 3.0,
        "space": 2.0,
        } )

    absolute_params.update( {
        "second_pin": True,
        "spring": ("both", "none", "left", "right"),
        } )

    def edgeObjects(self, boxes, chars=None, add=True):
        edges = [LidEdge(boxes, self),
                 LidHoleEdge(boxes, self),
                 LidRight(boxes, self),
                 LidLeft(boxes, self),
                 LidSideRight(boxes, self),
                 LidSideLeft(boxes, self),
        ]
        return self._edgeObjects(edges, boxes, chars, add)

class LidEdge(FingerJointEdge):
    char = "l"
    description = "Edge for slide on lid (back)"

class LidHoleEdge(FingerHoleEdge):
    char = "L"
    description = "Edge for slide on lid (box back)"

class LidRight(BaseEdge):
    char = "n"
    description = "Edge for slide on lid (right)"
    rightside = True

    def __call__(self, length, **kw):
        t = self.boxes.thickness

        if self.rightside:
            spring = self.settings.spring in ("right", "both")
        else:
            spring = self.settings.spring in ("left", "both")

        if spring:
            l = min(6*t, length - 2*t)
            a = 30
            sqt = 0.4 * t / math.cos(math.radians(a))
            sw = 0.5 * t
            p = [0, 90, 1.5*t+sw, -90, l, (-180, 0.25*t), l-0.2*t, 90, sw, 90-a, sqt, 2*a, sqt, -a, length-t ]
        else:
            p = [t, 90, t, -90, length-t]

        pin = self.settings.second_pin

        if pin:
            pinl = 2*t
            p[-1:] = [length-2*t-pinl, -90, t, 90, pinl, 90, t, -90, t]

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
        edge_width = self.settings.edge_width
        r = edge_width/3

        if self.rightside:
            spring = self.settings.spring in ("right", "both")
        else:
            spring = self.settings.spring in ("left", "both")

        if spring:
            p = [s, -90, t+s, -90, t+s, 90, edge_width-s/2, 90, length+t]
        else:
            p = [t+s, -90, t+s, -90, 2*t+s, 90, edge_width-s/2, 90, length+t]

        if pin:
            pinl = 2*t
            p[-1:] = [p[-1]-1.5*t-2*pinl-r, (90, r), edge_width+t+s/2-r, -90, 2*pinl+s+0.5*t, -90, t+s, -90,
                      pinl-r, (90, r), edge_width-s/2-2*r, (90, r), pinl+t-s-r]

        holex = 0.6 * t
        holey = -0.5*t + self.burn - s / 2
        if self.rightside:
            p = list(reversed(p))
            holex = length - holex
            holey = edge_width + 0.5*t + self.burn

        if spring:
            self.rectangularHole(holex, holey, 0.4*t, t+2*s)
        self.polyline(*p)

    def startwidth(self):
        return self.boxes.thickness + self.settings.edge_width if self.rightside else -self.settings.play / 2

    def endwidth(self):
        return self.boxes.thickness + self.settings.edge_width if not self.rightside else -self.settings.play / 2

    def margin(self):
        return self.boxes.thickness + self.settings.edge_width + self.settings.play / 2 if not self.rightside else 0.0

class LidSideLeft(LidSideRight):
    char = "M"
    description = "Edge for slide on lid (box left)"
    rightside = False

#############################################################################
####     Click Joints
#############################################################################

class ClickSettings(Settings):
    """Settings for Click-on Lids
Values:

* absolute_params

  * angle : 5.0 : angle of the hooks bending outward

* relative (in multiples of thickness)

  * depth : 3.0 : length of the hooks
  * bottom_radius : 0.1 : radius at the bottom
"""

    absolute_params = {
        "angle": 5.0,
    }

    relative_params = {
        "depth": 3.0,
        "bottom_radius": 0.1,
    }

    def edgeObjects(self, boxes, chars="cC", add=True):
        edges = [ClickConnector(boxes, self),
                 ClickEdge(boxes, self)]
        return self._edgeObjects(edges, boxes, chars, add)

class ClickConnector(BaseEdge):
    char = "c"
    description = "Click on (bottom side)"

    def hook(self, reverse=False):
        t = self.settings.thickness
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
        t = self.settings.thickness
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
        t = self.settings.thickness
        self.polyline(
            2 * t,
            90,
            length,
            90,
            2 * t,
        )

    def __call__(self, length, **kw):
        t = self.settings.thickness
        self.edge(4 * t)
        self.hook()
        self.finger(2 * t)
        self.hook(reverse=True)

        self.edge(length - 2 * (6 * t + 2 * self.hookWidth()), tabs=2)

        self.hook()
        self.finger(2 * t)
        self.hook(reverse=True)
        self.edge(4 * t)

    def margin(self):
        return 2 * self.settings.thickness


class ClickEdge(ClickConnector):
    char = "C"
    description = "Click on (top)"

    def startwidth(self):
        return self.boxes.thickness

    def margin(self):
        return 0.0

    def __call__(self, length, **kw):
        t = self.settings.thickness
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
        self.edge(length - 2 * (6 * t + 2 * w) + 2 * o, tabs=2)
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

    def edgeObjects(self, boxes, chars="dD", add=True):
        edges = [DoveTailJoint(boxes, self),
                 DoveTailJointCounterPart(boxes, self)]
        return self._edgeObjects(edges, boxes, chars, add)

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

        self.edge((s.size + leftover) / 2.0 + diffx - l1, tabs=1)

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

        self.edge((s.size + leftover) / 2.0 + diffx - l1, tabs=1)

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
    """Settings for Flex

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

    def checkValues(self):
        if self.distance < 0.01:
            raise ValueError("Flex Settings: distance parameter must be > 0.01mm")
        if self.width < 0.1:
            raise ValueError("Flex Settings: width parameter must be > 0.1mm")

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
        sections = max(int((h - connection) // width), 1)
        sheight = ((h - connection) / sections) - connection

        self.ctx.stroke()
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

        self.ctx.stroke()
        self.ctx.move_to(0, 0)
        self.ctx.line_to(x, 0)
        self.ctx.translate(*self.ctx.get_current_point())

class GearSettings(Settings):

    """Settings for rack (and pinion) edge
Values:
* absolute_params

 * dimension : 3.0 : modulus of the gear (in mm)
 * angle : 20.0 : pressure angle
 * profile_shift : 20.0 : Profile shift
 * clearance : 0.0 : clearance
"""

    absolute_params = {
        "dimension" : 3.0,
        "angle" : 20.0,
        "profile_shift" : 20.0,
        "clearance" : 0.0,
        }

    relative_params = {}

class RackEdge(BaseEdge):

    char = "R"

    description = "Rack (and pinion) Edge"

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

class RoundedTriangleEdgeSettings(Settings):

    """Settings for RoundedTriangleEdge
Values:

* absolute_params

 * height : 150. : height above the wall
 * radius : 30. : radius of top corner
 * r_hole : 0. : radius of hole

* relative (in multiples of thickness)

 * outset : 0 : extend the triangle along the length of the edge

"""

    absolute_params = {
        "height" : 150.,
        "radius" : 30.,
        "r_hole" : 2.,
    }

    relative_params = {
        "outset" : 0.,
    }

    def edgeObjects(self, boxes, chars="t", add=True):
        edges = [RoundedTriangleEdge(boxes, self)]
        return self._edgeObjects(edges, boxes, chars, add)

class RoundedTriangleEdge(Edge):
    """Makes an 'edge' with a rounded triangular bumpout and
       optional hole"""
    description = "Triangle for handle"
    char = "t"
    def __call__(self, length, **kw):
        length += 2 * self.settings.outset
        r = self.settings.radius
        if r >  length / 2:
            r = length / 2
        if length-2*r < self.settings.height: # avoid division by zero
            angle = 90-math.degrees(math.atan(
                (length-2*r)/(2*self.settings.height)))
            l = self.settings.height / math.cos(math.radians(90-angle))
        else:
            angle = math.degrees(math.atan(
                2*self.settings.height/(length-2*r)))
            l = 0.5 * (length-2*r) / math.cos(math.radians(angle))
        if self.settings.outset:
            self.polyline(0, -180, self.settings.outset, 90)
        else:
            self.corner(-90)
        if self.settings.r_hole:
            self.hole(self.settings.height, length/2., self.settings.r_hole)
        self.corner(90-angle, r, tabs=1)
        self.edge(l, tabs=1)
        self.corner(2*angle, r, tabs=1)
        self.edge(l, tabs=1)
        self.corner(90-angle, r, tabs=1)
        if self.settings.outset:
            self.polyline(0, 90, self.settings.outset, -180)
        else:
            self.corner(-90)

    def margin(self):
        return self.settings.height + self.settings.radius

#############################################################################
####     Slat wall
#############################################################################

class SlatWallSettings(Settings):

    """Settings for SlatWallEdges
Values:

* absolute_params

 * bottom_hook : "hook" : "spring", "stud" or "none"

* relative (in multiples of thickness)

 * hook_extra_height : 2.0 : space surrounding connectors (in multiples of thickness)
 * edge_width : 1.0 : space below holes of FingerHoleEdge

"""

    absolute_params = {
        "bottom_hook" : ("hook", "spring", "stud", "none"),
    }

    relative_params = {
        "hook_extra_height" : 2.0,
        "edge_width": 1.0,
    }

    def edgeObjects(self, boxes, chars="aAbBcCdD", add=True):
        edges = [SlatWallEdge(boxes, self),
                 SlatWallEdgeReversed(boxes, self),
                 SlatWallJoinedEdge(boxes, self),
                 SlatWallJoinedEdgeReversed(boxes, self),
                 SlatWallBackEdge(boxes, self),
                 SlatWallBackEdgeReversed(boxes, self),
                 SlatWallHoleEdge(boxes, self),
                 SlatWallHoleEdgeReversed(boxes, self),
        ]
        return self._edgeObjects(edges, boxes, chars, add)


class SlatWallEdge(BaseEdge):

    char = "a"
    reversed_ = False

    def _top_hook(self, reversed_=False):
        w = 6
        ro = 6
        ri = 2
        rt = min(1, w/2)
        poly = [0, -90, 5.5-ri, (-90, ri), 12-ri-w-rt, (90, rt),
                w-2*rt, (90, rt), 12-ro-rt, (90, ro), 5.5+w-ro, -90,
                self.settings.hook_extra_height]
        if reversed_:
            poly = reversed(poly)
        self.polyline(*poly)

    def _top_hook_len(self):
        w = 6 + 1
        return (w, self.settings.hook_extra_height - 1)

    def _bottom_hook(self, reversed_=False):
        slot = 8

        if self.settings.bottom_hook == "spring":
            r_plug = slot*.4
            slotslot = slot - r_plug * 2**0.5
            poly = [self.settings.hook_extra_height, -90,
                    5.0, -45, 0, (135, r_plug),
                    0, 90, 10, -90, slotslot, -90, 10, 90, 0,
                    (135, r_plug), 0, -45, 5, -90,
                    self.settings.hook_extra_height]
        elif self.settings.bottom_hook == "hook":
            d = 2
            poly = [self.settings.hook_extra_height + d - 1, -90,
                    5.5+5, (90,1), slot-2, (90, 1), 5, 90, d,
                    -90, 5.5, -90, self.settings.hook_extra_height + 1]
        elif self.settings.bottom_hook == "stud":
            poly = [self.settings.hook_extra_height, -90,
                    6, (90, 1) , slot-2, (90, 1), 6, -90,
                    self.settings.hook_extra_height]
        else:
            poly = [2*self.settings.hook_extra_height + slot]

        if reversed_:
            poly = reversed(poly)
        self.polyline(*poly)

    def _bottom_hook_len(self):
        slot = 8
        return (slot + self.settings.hook_extra_height,
                self.settings.hook_extra_height)

    def _joint(self, length, reversed_=False):
        self.polyline(length)

    def __call__(self, length, **kw):
        step = 101.6 # 4"
        tht, thb = self._top_hook_len()
        bht, bhb = self._bottom_hook_len()

        if length >= step + tht + bhb and self.settings.bottom_hook != "none":
            top_len = ((length-tht-1) // step) * step - thb - bht
            bottom_len = (length-tht) % step - bhb
        else:
            top_len = length-tht-thb
            bottom_len = None

        if self.reversed_:
            if bottom_len is not None:
                self._joint(bottom_len, True)
                self._bottom_hook(True)
            self._joint(top_len, True)
            self._top_hook(True)
        else:
            self._top_hook()
            self._joint(top_len)
            if bottom_len is not None:
                self._bottom_hook()
                self._joint(bottom_len)

    def margin(self):
        return 6+5.5

class SlatWallEdgeReversed(SlatWallEdge):
    char = "A"
    reversed_ = True

class SlatWallJoinedEdge(SlatWallEdge):
    char = "b"

    def _joint(self, length, reversed_=False):
        t = self.settings.thickness
        self.polyline(0, 90, t, -90)
        self.edges["f"](length)
        self.polyline(0, -90, t, 90)

    def startwidth(self):
        return self.settings.thickness

class SlatWallJoinedEdgeReversed(SlatWallJoinedEdge):
    char = "B"
    reversed_ = True

class SlatWallBackEdge(SlatWallEdge):

    char = "c"

    def _top_hook(self, reversed_=False):
        self.polyline(sum(self._top_hook_len()))

    def _bottom_hook(self, reversed_=False):
        self.polyline(sum(self._bottom_hook_len()))

    def _joint(self, length, reversed_=False):
        t = self.settings.thickness
        self.polyline(0, -90, t, 90)
        self.edges["F"](length)
        self.polyline(0, 90, t, -90)

    def margin(self):
        return self.settings.thickness

class SlatWallBackEdgeReversed(SlatWallBackEdge):
    char = "C"
    reversed_ = True

class SlatWallHoles(SlatWallEdge):

    reversed_ = True

    def _top_hook(self, reversed_=False):
        h = sum(self._top_hook_len())
        self.rectangularHole(h/2, 0, h, self.settings.thickness)
        self.moveTo(h, 0)

    def _bottom_hook(self, reversed_=False):
        h = sum(self._bottom_hook_len())
        self.rectangularHole(h/2, 0, h, self.settings.thickness)
        self.moveTo(h, 0)

    def _joint(self, length, reversed_=False):
        self.fingerHolesAt(0, 0, length, 0)
        self.moveTo(length, 0)

    def __call__(self, x, y, length, angle, **kw):
        """
        Draw holes for a matching SlatWallJoinedEdge

        :param x: position
        :param y: position
        :param length: length of matching edge
        :param angle:  (Default value = 90)
        :param bedBolts:  (Default value = None)
        :param bedBoltSettings:  (Default value = None)

        """
        with self.boxes.saved_context():
            self.boxes.moveTo(x, y, angle)
            b = self.boxes.burn
            t = self.settings.thickness

            if self.boxes.debug: # XXX
                width = self.settings.thickness
                self.ctx.rectangle(b, -width / 2 + b,
                                   length - 2 * b, width - 2 * b)

            SlatWallEdge.__call__(self, length)

class SlatWallHoleEdge(BaseEdge):
    """Edge with holes for a parallel finger joint"""
    char = 'd'
    description = "Edge (parallel slot wall Holes)"
    reversed_ = False

    def __init__(self, boxes, slatWallHoles=None, **kw):
        settings = None
        if isinstance(slatWallHoles, Settings):
            settings = slatWallHoles
            slatWallHoles = SlatWallHoles(boxes, settings)
        super(SlatWallHoleEdge, self).__init__(boxes, settings, **kw)

        self.slatWallHoles = slatWallHoles or boxes.slatWallHolesAt

    def __call__(self, length, bedBolts=None, bedBoltSettings=None, **kw):
        dist = self.slatWallHoles.settings.edge_width
        with self.saved_context():
            px, angle = (0, 0) if self.reversed_ else (length, 180)
            self.slatWallHoles(
                px, dist + self.settings.thickness / 2, length, angle)
        self.edge(length, tabs=2)

    def startwidth(self):
        """ """
        return self.slatWallHoles.settings.edge_width + self.settings.thickness

class SlatWallHoleEdgeReversed(SlatWallHoleEdge):

    char = "D"
    reversed_ = True
