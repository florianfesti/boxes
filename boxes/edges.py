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
    Supports absolutevalues and settings that grow with the thinckness
    of the material used.
    """
    absolute_params = { }
    relative_params = { }

    def __init__(self, thickness, relative=True, **kw):
        self.values = self.absolute_params.copy()

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
        :param relative:  (Default value = True) Do scale by thinckness
        :param **kw: parameters to set

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


class Edge:
    """Straight edge"""
    char = 'e'

    def __init__(self, boxes, settings):
        self.boxes = boxes
        self.ctx = boxes.ctx
        self.settings = settings

    def __getattr__(self, name):
        """Hack for using unalter code form Boxes class"""
        return getattr(self.boxes, name)

    def __call__(self, length, **kw):
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

    def startAngle(self):
        """Not yet supported"""
        return 0.0

    def endAngle(self):
        """Not yet supported"""
        return 0.0

class OutSetEdge(Edge):
    """Straight edge out set by one thickness"""
    char = 'E'

    def width(self):
        return self.boxes.thickness

class CompoundEdge(Edge):
    """Edge composed of multiple different Edges"""

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

class Slot(Edge):
    """Edge with an slot to slid another pice through """
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

class SlottedEdge(Edge):
    """Edge with multiple slots"""

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

class FingerJointSettings(Settings):
    """Setting for all different finger joint components

    Both sides should use the same instance to ensure they match"""

    absolute_params = {
        "surroundingspaces" : 2,
        }

    relative_params = {
        "space" : 1.0,
        "finger" : 1.0,
        "height" : 1.0,
        "width" : 1.0,
        }

class FingerJointEdge(Edge):
    """Finger joint edge """
    char = 'f'
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
    positive = False

    def width(self):
        """ """
        return self.boxes.thickness

    def margin(self):
        """ """
        return self.boxes.spacing

class FingerHoleEdge(Edge):
    """Edge with holes for a parallel finger joint"""
    char = 'h'

    def __call__(self, length, dist=None,
                 bedBolts=None, bedBoltSettings=None, **kw):
        if dist is None:
            dist = self.fingerHoleEdgeWidth * self.thickness
        self.ctx.save()
        self.moveTo(0, dist+self.thickness/2)
        self.fingerHoles(length, bedBolts, bedBoltSettings)
        self.ctx.restore()
        # XXX continue path
        self.ctx.move_to(0, 0)
        self.ctx.line_to(length, 0)
        self.ctx.translate(*self.ctx.get_current_point())

    def width(self):
        """ """
        return (self.fingerHoleEdgeWidth+1) * self.thickness

class FingerHoles:
    """Hole mathcing a finger joint edge"""
    def __init__(self, boxes, settings):
        self.boxes = boxes
        self.ctx = boxes.ctx
        self.settings = settings

    def __call__(self, length, bedBolts=None, bedBoltSettings=None):
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

        self.ctx.move_to(0, length)
        self.ctx.translate(*self.ctx.get_current_point())

class CrossingFingerHoleEdge(Edge):
    """Edge with holes for finger joints 90° above"""
    def __init__(self, boxes, height, **kw):
        Edge.__init__(self, boxes, None, **kw)
        self.height = height

    def __call__(self, length, **kw):
        self.fingerHolesAt(length/2.0, 0, self.height)
        Edge.__call__(self, length)

    
class DoveTailSettings(Settings):
    """Settings used for dove tail joints

    Both sides should use the same instance to ensure they match"""
    absolute_params = {
        "angle" : 50,
        }
    relative_params = {
        "size" : 3,
        "depth" : 1.5,
        "radius" : 0.2,
        }

class DoveTailJoint(Edge):
    """Edge with dove tail joints """
    char = 'd'
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

    positive = False

    def width(self):
        return self.settings.depth

    def margin(self):
        return self.boxes.spacing

class FlexSettings(Settings):
    """Settings for one directional flex cuts"""
    relative_params = {
        "distance" : 0.5,
        "connection" : 1.0,
        "width" : 5.0,
        }
    absolute_params = {
        "stretch" : 1.0,
        }

class FlexEdge(Edge):
    """Edge with flex cuts - use straight edge for the opposing side"""
    char = 'X'

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
