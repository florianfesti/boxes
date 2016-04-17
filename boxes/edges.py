#!/usr/bin/python3
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

def getDescriptions():
    return {edge.char : edge.description for edge in globals().values()
            if inspect.isclass(edge) and issubclass(edge, BaseEdge)
            and edge.char}

class BoltPolicy:
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
        return numFingers

    def _even(self, numFingers):
        """
        Return same or next smaller even number

        :param numFingers:

        """
        return (numFingers//2) * 2
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
        if pos > self.fingers//2:
            pos = self.fingers - pos
        if pos==0:
            return False
        if pos == self.fingers//2 and not (self.bolts % 2):
            return False
        result = (math.floor((float(pos)*(self.bolts+1)/self.fingers)-0.01) !=
                  math.floor((float(pos+1)*(self.bolts+1)/self.fingers)-0.01))
        #print pos, result, ((float(pos)*(self.bolts+1)/self.fingers)-0.01), ((float(pos+1)*(self.bolts+1)/self.fingers)-0.01)
        return result

#############################################################################
### Settings
#############################################################################

class Settings:
    """Generic Settings class

    Used by different other classes to store messurements and details.
    Supports absolute values and settings that grow with the thickness
    of the material used.

    Overload the absolute_params and relative_params class attributes with
    the suported keys and default values. The values are available via
    attribute access.
    """
    absolute_params = { }
    relative_params = { }

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


class BaseEdge:
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
        self.ctx.move_to(0,0)
        self.ctx.line_to(length, 0)
        self.ctx.translate(*self.ctx.get_current_point())

    def width(self):
        """Amount of space the beginning of the edge is set below the inner space of the part """
        return 0.0

    def margin(self):
        """Space needed right of the starting point"""
        return self.boxes.spacing

    def spacing(self):
        """Space the edge needs outside of the inner space of the part"""
        return self.width() + self.margin()

class Edge(BaseEdge):
    """Straight edge"""
    char = 'e'
    description = "Straight Edge"    

class OutSetEdge(BaseEdge):
    """Straight edge out set by one thickness"""
    char = 'E'
    description = "Straight Edge (outset by thickness)"

    def width(self):
        return self.boxes.thickness

class CompoundEdge(BaseEdge):
    """Edge composed of multiple different Edges"""
    description = "Compound Edge"

    def __init__(self, boxes, types, lengths):
        Edge.__init__(self, boxes, None)
        self.types = [self.edges.get(edge, edge) for edge in types]
        self.lengths = lengths
        self.length = sum(lengths)

    def width(self):
        return self.types[0].width()
        
    def margin(self):
        return max((e.margin() for e in self.types))

    def __call__(self, length, **kw):
        if length and abs(length - self.length) > 1E-5:
            raise ValueError("Wrong length for CompoundEdge")
        for e, l in zip(self.types, self.lengths):
            # XXX different margins???
            e(l)

#############################################################################
####     Slots
#############################################################################

class Slot(BaseEdge):
    """Edge with an slot to slid another pice through """

    description = "Slot"

    def __init__(self, boxes, depth):
        Edge.__init__(self, boxes, None)
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
        Edge.__init__(self, boxes, None)
        self.edge = self.edges.get(edge, edge)
        self.sections = sections
        self.slots = slots

    def width(self):
        return self.edge.width()

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
    """Settings for finger joints

Values:

* absolute

  * surroundingspaces : 2 : maximum space at the start and end in multiple
    of normal spaces

* relative (in multiples of thickness)

  * space : 1.0 : space between fingers
  * finger : 1.0 : width of the fingers
  * height : 1.0 : length of the fingers
  * width : 1.0 : width of finger holes

"""

    absolute_params = {
        "surroundingspaces" : 2,
        }

    relative_params = {
        "space" : 1.0,
        "finger" : 1.0,
        "height" : 1.0,
        "width" : 1.0,
        }

class FingerJointEdge(BaseEdge):
    """Finger joint edge """
    char = 'f'
    description = "Finger Joint"
    positive = True

    def __call__(self, length,
                    bedBolts=None, bedBoltSettings=None, **kw):
        positive = self.positive
        space, finger = self.settings.space, self.settings.finger

        fingers = int((length-(self.settings.surroundingspaces-1)*space) //
                      (space+finger))

        if bedBolts:
            fingers = bedBolts.numFingers(fingers)
        leftover = length - fingers*(space+finger) + space

        s, f, thickness = space, finger, self.thickness
        d, d_nut, h_nut, l, l1 = bedBoltSettings or self.boxes.bedBoltSettings
        p = 1 if positive else -1

        if fingers <= 0:
            fingers = 0
            leftover = length

        self.edge(leftover/2.0)
        for i in range(fingers):
            if i !=0:
                if not positive and bedBolts and bedBolts.drawBolt(i):
                    self.hole(0.5*space,
                              0.5*self.thickness, 0.5*d)
                if positive and bedBolts and bedBolts.drawBolt(i):
                    self.bedBoltHole(s, bedBoltSettings)
                else:
                    self.edge(s)
            self.corner(-90*p)
            self.edge(self.settings.height)
            self.corner(90*p)
            self.edge(f)
            self.corner(90*p)
            self.edge(self.settings.height)
            self.corner(-90*p)
        self.edge(leftover/2.0)

    def margin(self):
        """ """
        return self.boxes.spacing + self.boxes.thickness

class FingerJointEdgeCounterPart(FingerJointEdge):
    """Finger joint edge - other side"""
    char = 'F'
    description = "Finger Joint (opposing side)"
    positive = False

    def width(self):
        """ """
        return self.boxes.thickness

    def margin(self):
        """ """
        return self.boxes.spacing

class FingerHoles:
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
        fingers = int((length-(self.settings.surroundingspaces-1)*s) //
                      (s+f))
        if bedBolts:
            fingers = bedBolts.numFingers(fingers)
            d, d_nut, h_nut, l, l1 = bedBoltSettings or self.boxes.bedBoltSettings
        leftover = length - fingers*(s+f) - f
        b = self.boxes.burn
        if self.boxes.debug:
            self.ctx.rectangle(0, -self.settings.width/2+b,
                               length, self.settings.width - 2*b)
        for i in range(fingers):
            pos = leftover/2.0+i*(s+f)
            if bedBolts and bedBolts.drawBolt(i):
                self.boxes.hole(pos+0.5*s, 0, d*0.5)
            self.ctx.rectangle(pos+s+b, -self.settings.width/2+b,
                               f-2*b, self.settings.width - 2*b)

        self.ctx.restore()

class FingerHoleEdge(BaseEdge):
    """Edge with holes for a parallel finger joint"""
    char = 'h'
    description = "Edge (parallel Finger Joint Holes)"
    def __init__(self, boxes, fingerHoles=None, **kw):
        Edge.__init__(self, boxes, None, **kw)
        self.fingerHoles = fingerHoles or boxes.fingerHolesAt

    def __call__(self, length, dist=None,
                 bedBolts=None, bedBoltSettings=None, **kw):
        if dist is None:
            dist = self.fingerHoleEdgeWidth * self.thickness
        self.ctx.save()
        self.fingerHoles(0, dist+self.thickness/2, length, 0,
                         bedBolts=bedBolts, bedBoltSettings=bedBoltSettings)
        self.ctx.restore()
        # XXX continue path
        self.ctx.move_to(0, 0)
        self.ctx.line_to(length, 0)
        self.ctx.translate(*self.ctx.get_current_point())

    def width(self):
        """ """
        return (self.fingerHoleEdgeWidth+1) * self.thickness

class CrossingFingerHoleEdge(BaseEdge):
    """Edge with holes for finger joints 90° above"""

    description = "Edge (orthogonal Finger Joint Holes)"

    def __init__(self, boxes, height, fingerHoles=None, **kw):
        Edge.__init__(self, boxes, None, **kw)
        self.fingerHoles = fingerHoles or boxes.fingerHolesAt
        self.height = height

    def __call__(self, length, **kw):
        self.fingerHoles(length/2.0, 0, self.height)
        Edge.__call__(self, length)

#############################################################################
####     Stackable Joints
#############################################################################

class StackableSettings(Settings):
    """Settings for StackableEdge classes

Values:

* absolute_params

  * angle : 60 : inside angle of the feet

* relative (in multiples of thickness)

  * height : 2.0 : height of the feet
  * width  : 4.0 : width of the feet
  * holedistance : 1.0 : distance from finger holes to bottom edge

"""

    absolute_params = {
        "angle" : 60,
    }
    relative_params = {
        "height" : 2.0,
        "width"  : 4.0,
        "holedistance" : 1.0,
    }

class StackableEdge(BaseEdge):
    """Edge for having stackable Boxes. The Edge creates feet on the bottom
    and has matching recesses on the top corners."""

    char = "s"
    description = "Stackable (bottom, finger joint holes)"
    bottom = True

    def __init__(self, boxes, settings, fingerjointsettings):
        Edge.__init__(self, boxes, settings)
        self.fingerjointsettings = fingerjointsettings

    def __call__(self, length, **kw):
        s = self.settings
        r = s.height / 2.0 / (1-math.cos(math.radians(s.angle)))
        l = r * math.sin(math.radians(s.angle))
        p = 1 if self.bottom else -1

        if self.bottom:
            self.boxes.fingerHolesAt(0, s.height+self.settings.holedistance+0.5*self.boxes.thickness,
                                     length, 0)

        self.boxes.edge(s.width)
        self.boxes.corner(p*s.angle, r)
        self.boxes.corner(-p*s.angle, r)
        self.boxes.edge(length-2*s.width-4*l)
        self.boxes.corner(-p*s.angle, r)
        self.boxes.corner(p*s.angle, r)
        self.boxes.edge(s.width)

    def _height(self):
        return self.settings.height + self.settings.holedistance + self.settings.thickness
        
    def width(self):
        return self._height() if self.bottom else 0

    def margin(self):
        return 0 if self.bottom else self._height()

class StackableEdgeTop(StackableEdge):
    char = "S"
    description = "Stackable (top)"
    bottom = False

#############################################################################
####     Dove Tail Joints
#############################################################################
    
class DoveTailSettings(Settings):
    """Settings used for dove tail joints

Values:

* absolute

  * angle : 50 : how much should fingers widen (-80 to 80)

* relative (in multiples of thickness)

  * size : 3 : from one middle of a dove tail to another
  * depth : 1.5 : how far the dove tails stick out of/into the edge
  * radius : 0.2 : radius used on all four corners

"""
    absolute_params = {
        "angle" : 50,
        }
    relative_params = {
        "size" : 3,
        "depth" : 1.5,
        "radius" : 0.2,
        }

class DoveTailJoint(BaseEdge):
    """Edge with dove tail joints """
    char = 'd'
    description = "Dove Tail Joint"
    positive = True

    def __call__(self, length, **kw):
        s = self.settings
        radius = max(s.radius, self.boxes.burn) # no smaller than burn
        positive = self.positive
        a = s.angle + 90
        alpha = 0.5*math.pi - math.pi*s.angle/180.0

        l1 = radius/math.tan(alpha/2.0)
        diffx = 0.5*s.depth/math.tan(alpha)
        l2 = 0.5*s.depth / math.sin(alpha)

        sections = int((length) // (s.size*2))
        leftover = length - sections*s.size*2

        p = 1 if positive else -1

        self.edge((s.size+leftover)/2.0+diffx-l1)
        for i in range(sections):
            self.corner(-1*p*a, radius)
            self.edge(2*(l2-l1))
            self.corner(p*a, radius)
            self.edge(2*(diffx-l1)+s.size)
            self.corner(p*a, radius)
            self.edge(2*(l2-l1))
            self.corner(-1*p*a, radius)
            if i<sections-1: # all but the last
                self.edge(2*(diffx-l1)+s.size)
        self.edge((s.size+leftover)/2.0+diffx-l1)
        self.ctx.translate(*self.ctx.get_current_point())

    def margin(self):
        """ """
        return self.settings.depth + self.boxes.spacing

class DoveTailJointCounterPart(DoveTailJoint):
    """Edge for other side of dove joints """
    char = 'D'
    description = "Dove Tail Joint (opposing side)"

    positive = False

    def width(self):
        return self.settings.depth

    def margin(self):
        return self.boxes.spacing

class FlexSettings(Settings):
    """Settings for one directional flex cuts

Values:

* absolute

 * stretch : 1.05 : Hint of how much the flex part should be shortend

* relative (in multiples of thickness)

 * distance : 0.5 : width of the pattern perpendicular to the cuts
 * connection : 1.0 : width of the gaps in the cuts
 * width" : 5.0 : width of the pattern in direction of the cuts

"""
    relative_params = {
        "distance" : 0.5,
        "connection" : 1.0,
        "width" : 5.0,
        }
    absolute_params = {
        "stretch" : 1.05,
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
        h += 2*burn
        lines = int(x // dist)
        leftover = x - lines * dist
        sections = int((h-connection) // width)
        sheight = ((h-connection) / sections)-connection

        for i in range(lines):
            pos = i*dist + leftover/2
            if i % 2:
                self.ctx.move_to(pos, 0)
                self.ctx.line_to(pos, connection+sheight)
                for j in range((sections-1)//2):
                    self.ctx.move_to(pos, (2*j+1)* sheight+ (2*j+2)*connection)
                    self.ctx.line_to(pos, (2*j+3)* (sheight+ connection))
                if not sections % 2:
                    self.ctx.move_to(pos, h - sheight- connection)
                    self.ctx.line_to(pos, h)
            else:
                if sections % 2:
                    self.ctx.move_to(pos, h)
                    self.ctx.line_to(pos, h-connection-sheight)
                    for j in range((sections-1)//2):
                         self.ctx.move_to(
                             pos, h-((2*j+1)* sheight+ (2*j+2)*connection))
                         self.ctx.line_to(
                             pos, h-(2*j+3)* (sheight+ connection))

                else:
                    for j in range(sections//2):
                        self.ctx.move_to(pos,
                                         h-connection-2*j*(sheight+connection))
                        self.ctx.line_to(pos, h-2*(j+1)*(sheight+connection))

        self.ctx.move_to(0, 0)
        self.ctx.line_to(x, 0)
        self.ctx.translate(*self.ctx.get_current_point())
