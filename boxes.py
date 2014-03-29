#!/usr/bin/python
# Copyright (C) 2013-2014 Florian Festi
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

import cairo
import math
from functools import wraps

def dist(dx, dy):
    return (dx*dx+dy*dy)**0.5

def restore(func):
    @wraps(func)
    def f(self, *args, **kw):
        self.ctx.save()
        pt = self.ctx.get_current_point()
        func(self, *args, **kw)
        self.ctx.restore()
        self.ctx.move_to(*pt)
    return f

class BoltPolicy:
    """Abstract class
    Distributes (bed) bolts on a number of segments
    (fingers of a finger joint)
    """
    def drawbolt(self, pos):
        """Add a bolt to this segment?"""
        return False

    def numFingers(self, numfingers):
        """returns next smaller, possible number of fingers"""
        return numFingers

    def _even(self, numFingers):
        return (numFingers//2) * 2
    def _odd(self, numFingers):
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
        return 0.0

    def margin(self):
        return self.boxes.spacing

    def spacing(self):
        return self.width() + self.margin()

    def startAngle(self):
        return 0.0

    def endAngle(self):
        return 0.0

class OutSetEdge(Edge):
    char = 'E'

    def width(self):
        return self.boxes.thickness


class FingerJointSettings(Settings):
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
        d, d_nut, h_nut, l, l1 = bedBoltSettings or self.bedBoltSettings
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
        return self.boxes.spacing + self.boxes.thickness

class FingerJointEdgeCounterPart(FingerJointEdge):
    char = 'F'
    positive = False

    def width(self):
        return self.boxes.thickness

    def margin(self):
        return self.boxes.spacing

class FingerHoleEdge(Edge):
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
        return (self.fingerHoleEdgeWidth+1) * self.thickness

class DoveTailSettings(Settings):
    absolute_params = {
        "angle" : 50,
        }
    relative_params = {
        "size" : 3,
        "depth" : 1.5,
        "radius" : 0.2,
        }

class DoveTailJoint(Edge):
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
        return self.settings.depth + self.boxes.spacing

class DoveTailJointCounterPart(DoveTailJoint):
    char = 'D'

    positive = False

    def width(self):
        return self.settings.depth

    def margin(self):
        return self.boxes.spacing

class FlexSettings(Settings):
    relative_params = {
        "distance" : 0.5,
        "connection" : 1.0,
        "width" : 5.0,
        }
    absolute_params = {
        "stretch" : 1.0,
        }

class FlexEdge(Edge):
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

#############################################################################
### Building blocks
#############################################################################

class FingerHoles:
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
            d, d_nut, h_nut, l, l1 = bedBoltSettings or self.bedBoltSettings
        leftover = length - fingers*(s+f) - f
        b = self.boxes.burn
        if self.boxes.debug:
            self.ctx.rectangle(0, -self.settings.width/2+b,
                               length, self.settings.width - 2*b)
        for i in range(fingers):
            pos = leftover/2.0+i*(s+f)
            if bedBolts and bedBolts.drawBolt(i):
                self.hole(pos+0.5*s, 0, d*0.5)
            self.ctx.rectangle(pos+s+b, -self.settings.width/2+b,
                               f-2*b, self.settings.width - 2*b)

        self.ctx.move_to(0, length)
        self.ctx.translate(*self.ctx.get_current_point())

class NutHole:
    sizes = {
        "M1.6" : 3.2,
        "M2" : 4,
        "M2.5" : 5,
        "M3" : 5.5,
        "M4" : 7,
        "M5" : 8,
        "M6" : 10,
        "M8" : 13,
        "M10" : 16,
        "M12" : 18,
        "M14" : 21,
        "M16" : 24,
        "M20" : 30,
        "M24" : 36,
        "M30" : 46,
        "M36" : 55,
        "M42" : 65,
        "M48" : 75,
        "M56" : 85,
        "M64" : 95,
        }

    def __init__(self, boxes, settings):
        self.boxes = boxes
        self.ctx = boxes.ctx
        self.settings = settings

    @restore
    def __call__(self, size, x=0, y=0, angle=0):
        size = self.sizes.get(size, size)
        side = size / 3**0.5
        self.boxes.moveTo(x, y, angle)
        self.boxes.moveTo(-0.5*side, 0.5*size, angle)
        for i in range(6):
            self.boxes.edge(side)
            self.boxes.corner(-60)

class Boxes:

    def __init__(self, width=300, height=200, thickness=3.0, burn=0.05):
        self.thickness = thickness
        self.burn = burn
        self.spacing = 2*self.burn + 0.5 * self.thickness

        self.fingerHoleEdgeWidth = 1.0    # multitudes of self.thickness
        self.bedBoltSettings = (3, 5.5, 2, 20, 15) #d, d_nut, h_nut, l, l1
        self.hexHolesSettings = (5, 3, 'circle') # r, dist, style
        self.output = "box.svg"
        self.debug = 0
        self._init_surface(width, height)
        self._buildObjects()

    def addPart(self, part, name=None):
        if name is None:
            name = part.__class__.__name__
            name = name[0].lower() + name[1:]
        if not hasattr(self, name):
            setattr(self, name, part)
        if isinstance(part, Edge):
            self.edges[part.char] = part

    def _buildObjects(self):
        self.edges = {}
        self.addPart(Edge(self, None))
        self.addPart(OutSetEdge(self, None))

        # Share settings object
        s = FingerJointSettings(self.thickness)
        self.addPart(FingerJointEdge(self, s))
        self.addPart(FingerJointEdgeCounterPart(self, s))
        self.addPart(FingerHoleEdge(self, s))
        self.addPart(FingerHoles(self, s))

        s = DoveTailSettings(self.thickness)
        self.addPart(DoveTailJoint(self, s))
        self.addPart(DoveTailJointCounterPart(self, s))
        s = FlexSettings(self.thickness)
        self.addPart(FlexEdge(self, s))

        self.addPart(NutHole(self, None))

    def _init_surface(self, width, height):
        #mm2pt = 90 / 25.4 / 1.25
        mm2pt = 1
        #width *= mm2pt
        #height *= mm2pt #3.543307
        self.surface = cairo.SVGSurface(self.output, width, height)
        self.ctx = ctx = cairo.Context(self.surface)
        ctx.translate(0, height)
        ctx.scale(mm2pt, -mm2pt)

        #ctx.set_source_rgb(1.0, 1.0, 1.0)
        #ctx.rectangle(0, 0, width, height)
        #ctx.fill()

        ctx.set_source_rgb(0.0, 0.0, 0.0)
        ctx.set_line_width(2*self.burn)


    def cc(self, callback, number, x=0.0, y=None):
        """call callback"""
        if y is None:
            y = self.burn
        self.ctx.save()
        self.moveTo(x, y)
        if callable(callback):
            callback(number)
        elif hasattr(callback, '__getitem__'):
            try:
                callback = callback[number]
                if callable(callback):
                    callback()
            except (KeyError, IndexError):
                pass
            except:
                self.ctx.restore()
                raise
        self.ctx.restore()

    def getEntry(self, param, idx):
        if isinstance(param, list):
            if len(param)>idx:
                return param[idx]
            else:
                return None
        else:
            return param

    def close(self):
        self.ctx.stroke()
        self.surface.flush()
        self.surface.finish()

        f = open(self.output, "r+")
        s = f.read(1024)
        pos = s.find('pt"')
        if pos > 0:
            f.seek(pos)
            f.write("mm")
        else:
            print "Could not replace pt with mm"
        pos = s.find('pt"', pos+3)
        if pos > 0:
            f.seek(pos)
            f.write("mm")
        else:
            print "Could not replace pt with mm"

    ############################################################
    ### Turtle graphics commands
    ############################################################

    def corner(self, degrees, radius=0):
        rad = degrees*math.pi/180
        if degrees > 0:
            self.ctx.arc(0, radius+self.burn, radius+self.burn,
                     -0.5*math.pi, rad - 0.5*math.pi)
        elif radius > self.burn:
            self.ctx.arc_negative(0, -(radius-self.burn), radius-self.burn,
                     0.5*math.pi, rad + 0.5*math.pi)
        else: # not rounded inner corner
            self.ctx.arc_negative(0, self.burn-radius, self.burn-radius,
                         -0.5*math.pi, -0.5*math.pi+rad)

        self.continueDirection(rad)

    def edge(self, length):
        self.ctx.move_to(0,0)
        self.ctx.line_to(length, 0)
        self.ctx.translate(*self.ctx.get_current_point())

    def curveTo(self, x1, y1, x2, y2, x3, y3):
        """control point 1, control point 2, end point"""
        self.ctx.curve_to(x1, y1, x2, y2, x3, y3)
        dx = x3-x2
        dy = y3-y2
        rad = math.atan2(dy, dx)
        self.continueDirection(rad)

    def bedBoltHole(self, length, bedBoltSettings=None):
        d, d_nut, h_nut, l, l1 = bedBoltSettings or self.bedBoltSettings
        self.edge((length-d)/2.0)
        self.corner(90)
        self.edge(l1)
        self.corner(90)
        self.edge((d_nut-d)/2.0)
        self.corner(-90)
        self.edge(h_nut)
        self.corner(-90)
        self.edge((d_nut-d)/2.0)
        self.corner(90)
        self.edge(l-l1-h_nut)
        self.corner(-90)
        self.edge(d)
        self.corner(-90)
        self.edge(l-l1-h_nut)
        self.corner(90)
        self.edge((d_nut-d)/2.0)
        self.corner(-90)
        self.edge(h_nut)
        self.corner(-90)
        self.edge((d_nut-d)/2.0)
        self.corner(90)
        self.edge(l1)
        self.corner(90)
        self.edge((length-d)/2.0)


    def grip(self, length, depth):
        """corrugated edge useful as an gipping area"""
        grooves = int(length // (depth*2.0)) + 1
        depth = length / grooves / 4.0
        for groove in range(grooves):
            self.corner(90, depth)
            self.corner(-180, depth)
            self.corner(90, depth)

    def _latchHole(self, length):
        self.edge(1.1*self.thickness)
        self.corner(-90)
        self.edge(length/2.0+0.2*self.thickness)
        self.corner(-90)
        self.edge(1.1*self.thickness)

    def _latchGrip(self, length):
        self.corner(90, self.thickness/4.0)
        self.grip(length/2.0-self.thickness/2.0-0.2*self.thickness, self.thickness/2.0)
        self.corner(90, self.thickness/4.0)

    def latch(self, length, positive=True, reverse=False):
        """Fix a flex box door at the box
        positive: False: Door side; True: Box side
        reverse: True when running away from the latch
        """
        if positive:
            if reverse:
                self.edge(length/2.0-self.burn)
            self.corner(-90)
            self.edge(self.thickness)
            self.corner(90)
            self.edge(length/2.0)
            self.corner(90)
            self.edge(self.thickness)
            self.corner(-90)
            if not reverse:
                self.edge(length/2.0-self.burn)
        else:
            if reverse:
                self._latchGrip(length)
            else:
                self.corner(90)
            self._latchHole(length)
            if not reverse:
                self._latchGrip(length)
            else:
                self.corner(90)

    def handle(self, x, h, hl, r=30):
        """Creates and Edge with a handle"""
        d = (x-hl-2*r)/2.0
        if d < 0:
            print("Handle too wide")

        self.ctx.save()

        # Hole
        self.moveTo(d+2*r, 0)
        self.edge(hl-2*r)
        self.corner(-90, r)
        self.edge(h-3*r)
        self.corner(-90, r)
        self.edge(hl-2*r)
        self.corner(-90, r)
        self.edge(h-3*r)
        self.corner(-90, r)

        self.ctx.restore()
        self.moveTo(0,0)

        self.curveTo(d, 0, d, 0, d, -h+r)
        self.curveTo(r, 0, r, 0, r, r)
        self.edge(hl)
        self.curveTo(r, 0, r, 0, r, r)
        self.curveTo(h-r, 0, h-r, 0, h-r, -d)

    ### Navigation

    def moveTo(self, x, y=0.0, degrees=0):
        self.ctx.move_to(0, 0)
        self.ctx.translate(x, y)
        self.ctx.rotate(degrees*math.pi/180.0)
        self.ctx.move_to(0, 0)

    def continueDirection(self, angle=0):
        self.ctx.translate(*self.ctx.get_current_point())
        self.ctx.rotate(angle)

    def move(self, x, y, where, before=False):
        """Intended to be used by parts
        where can be combinations of "up", "down", "left", "right" and "only"
        when "only" is included the move is only done when before is True
        The function returns whether actual drawing of the part
        should be omited.
        """
        if not where:
            return False

        terms = where.split()
        dontdraw = before and "only" in terms

        moves = {
            "up": (0, y, False),
            "down" : (0, -y, True),
            "left" : (-x, 0, True),
            "right" : (x, 0, False),
            "only" : (0, 0, None),
            }
        for term in terms:
            if not term in moves:
                raise ValueError("Unknown direction: '%s'" % term)
            x, y, movebeforeprint = moves[term]
            if movebeforeprint and before:
                self.moveTo(x, y)
            elif (not movebeforeprint and not before) or dontdraw:
                self.moveTo(x, y)
        return dontdraw



    # Building blocks

    def fingerHolesAt(self, x, y, length, angle=90,
                      bedBolts=None, bedBoltSettings=None):
        self.ctx.save()
        self.moveTo(x, y, angle)
        self.fingerHoles(length, bedBolts, bedBoltSettings)
        self.ctx.restore()

    @restore
    def hole(self, x, y, r):
        self.moveTo(x+r, y)
        self.ctx.arc(-r, 0, r, 0, 2*math.pi)

    @restore
    def rectangularHole(self, x, y, dx, dy, r=0):
        self.moveTo(x+r-dx/2.0, y-dy/2.0, 180)
        for d in (dy, dx, dy, dx):
            self.corner(-90, r)
            self.edge(d)

    @restore
    def text(self, text, x=0, y=0, angle=0, align=""):
        self.moveTo(x, y, angle)
        (tx, ty, width, height, dx, dy) = self.ctx.text_extents(text)
        align = align.split()
        moves = {
            "top" : (0, -height),
            "middle" : (0, -0.5*height),
            "bottom" : (0, 0),
            "left" : (0, 0),
            "center" : (-0.5*width, 0),
            "right" : (-width, 0),
        }
        for a in align:
            if a in moves:
                self.moveTo(*moves[a])
            else:
                raise ValueError("Unknown alignment: %s" % align)

        self.ctx.scale(1, -1)
        self.ctx.show_text(text)

    @restore
    def NEMA(self, size, x=0, y=0, angle=0):
        nema = {
            #    motor,flange, holes, screws 
             8 : (20.3, 16,   15.4, 3),
            11 : (28.2, 22,   23,   4),
            14 : (35.2, 22,   26,   4),
            16 : (39.2, 22,   31,   4),
            17 : (42.2, 22,   31,   4),
            23 : (56.4, 38.1, 47.1, 5.2),
            24 : (60,   36,   49.8, 5.1),
            34 : (86.3, 73,   69.8, 6.6),
            42 : (110,  55.5, 89,   8.5),
             }
        width, flange, holedistance, diameter = nema[size]
        self.moveTo(x, y, angle)
        if self.debug:
            self.rectangularHole(0, 0, width, width)
        self.hole(0,0, 0.5*flange)
        for x in (-1, 1):
            for y in (-1, 1):
                self.hole(x*0.5*holedistance,
                          y*0.5*holedistance,
                          0.5*diameter)


    # hexHoles

    def hexHolesRectangle(self, x, y, settings=None, skip=None):
        """
        Fills a rectangle with holes.
        r : radius of holes
        b : space between holes
        style : what types of holes (not yet implemented)
        skip : function to check if hole should be present
               gets x, y, r, b, posx, posy
        """
        if settings is None:
            settings = self.hexHolesSettings
        r, b, style = settings

        w = r+b/2.0
        dist = w * math.cos(math.pi/6.0)

        # how many half circles do fit
        cx = int((x-2*r) // (w)) + 2
        cy = int((y-2*r) // (dist)) + 2

        # what's left on the sides
        lx = (x - (2*r+(cx-2)*w))/2.0
        ly = (y - (2*r+((cy//2)*2)*dist-2*dist))/2.0

        for i in range(cy//2):
            for j in range((cx-(i%2))//2):
                px = 2*j*w + r + lx
                py = i*2*dist + r + ly
                if i % 2:
                    px += w
                if skip and skip(x, y, r, b, px, py):
                    continue
                self.hole(px, py, r)

    def __skipcircle(self, x, y, r, b, posx, posy):
        cx, cy = x/2.0, y/2.0
        return (dist(posx-cx, posy-cy) > (cx-r))

    def hexHolesCircle(self, d, settings=None):
        d2 = d/2.0
        self.hexHolesRectangle(d, d, settings=settings, skip=self.__skipcircle)

    def hexHolesPlate(self, x, y, rc, settings=None):
        def skip(x, y, r, b, posx, posy):
            posx = abs(posx-(x/2.0))
            posy = abs(posy-(y/2.0))

            wx = 0.5*x-rc-r
            wy = 0.5*y-rc-r

            if (posx <= wx) or (posy <= wx):
                return 0
            return dist(posx-wx, posy-wy) > rc

        self.hexHolesRectangle(x, y, settings, skip=skip)

    def hexHolesHex(self, h, settings=None, grow=None):
        if settings is None:
            settings = self.hexHolesSettings
        r, b, style = settings

        self.ctx.rectangle(0, 0, h, h)
        w = r+b/2.0
        dist = w * math.cos(math.pi/6.0)
        cy = 2 * int((h-4*dist)// (4*w)) + 1

        leftover = h-2*r-(cy-1)*2*r
        if grow=='space ':
            b += leftover / (cy-1) / 2

        # recalulate with adjusted values
        w = r+b/2.0
        dist = w * math.cos(math.pi/6.0)

        self.moveTo(h/2.0-(cy//2)*2*w, h/2.0)
        for j in range(cy):
            self.hole(2*j*w, 0, r)
        for i in range(1, cy/2+1):
            for j in range(cy-i):
                self.hole(j*2*w+i*w, i*2*dist, r)
                self.hole(j*2*w+i*w, -i*2*dist, r)

    ##################################################
    ### parts
    ##################################################

    def roundedPlate(self, x, y, r, callback=None,
                     holesMargin=None, holesSettings=None,
                     bedBolts=None, bedBoltSettings=None,
                     move=None):
        """fits surroundingWall
        first edge is split to have a joint in the middle of the side
        callback is called at the beginning of the straight edges
        0, 1 for the two part of the first edge, 2, 3, 4 for the others

        set holesMargin to get hex holes.
        """

        overallwidth = x+2*self.fingerJointEdge.spacing()
        overallheight = y+2*self.fingerJointEdge.spacing()

        if self.move(overallwidth, overallheight, move, before=True):
            return

        self.ctx.save()
        self.moveTo(self.fingerJointEdge.margin(),
                    self.fingerJointEdge.margin())
        self.moveTo(r, 0)

        self.cc(callback, 0)
        self.fingerJointEdge(x/2.0-r, bedBolts=self.getEntry(bedBolts, 0),
                         bedBoltSettings=self.getEntry(bedBoltSettings, 0))
        self.cc(callback, 1)
        self.fingerJointEdge(x/2.0-r, bedBolts=self.getEntry(bedBolts, 1),
                         bedBoltSettings=self.getEntry(bedBoltSettings, 1))
        for i, l in zip(range(3), (y, x, y)):
            self.corner(90, r)
            self.cc(callback, i+2)
            self.fingerJointEdge(l-2*r, bedBolts=self.getEntry(bedBolts, i+2),
                         bedBoltSettings=self.getEntry(bedBoltSettings, i+2))
        self.corner(90, r)

        self.ctx.restore()
        self.ctx.save()

        self.moveTo(self.fingerJointEdge.margin(),
                    self.fingerJointEdge.margin())

        if holesMargin is not None:
            self.moveTo(holesMargin, holesMargin)
            if r > holesMargin:
                r -= holesMargin
            else:
                r = 0
            self.hexHolesPlate(x-2*holesMargin, y-2*holesMargin, r,
                               settings=holesSettings)
        self.ctx.restore()
        self.ctx.stroke()
        self.move(overallwidth, overallheight, move)

    def surroundingWall(self, x, y, r, h,
                        bottom='e', top='e',
                        callback=None,
                        move=None):
        """
        h : inner height, not counting the joints
        callback is called a beginn of the flat sides with
          0 for right half of first x side;
          1 and 3 for y sides;
          2 for second x side
          4 for second half of the first x side
        """
        c4 = (r+self.burn)*math.pi*0.5 # circumference of quarter circle
        c4 = 0.9 * c4 # stretch flex 10%

        top = self.edges.get(top, top)
        bottom = self.edges.get(bottom, bottom)

        topwidth = top.width()
        bottomwidth = bottom.width()

        overallwidth = 2*x + 2*y - 8*r + 4*c4 + \
            self.edges["d"].spacing() + self.edges["D"].spacing()
        overallheight = h + top.spacing() + bottom.spacing()


        if self.move(overallwidth, overallheight, move, before=True):
            return

        self.ctx.save()
        self.moveTo(self.edges["D"].margin(), bottom.margin())

        self.cc(callback, 0, y=bottomwidth+self.burn)
        bottom(x/2.0-r)
        for i, l in zip(range(4), (y, x, y, 0)):
            self.flexEdge(c4, h+topwidth+bottomwidth)
            self.cc(callback, i+1, y=bottomwidth+self.burn)
            if i < 3:
                bottom(l-2*r)
        bottom(x/2.0-r)

        self.corner(90)
        self.edge(bottomwidth)
        self.doveTailJoint(h)
        self.edge(topwidth)
        self.corner(90)

        top(x/2.0-r)
        for i, l in zip(range(4), (y, x, y, 0)):
            self.edge(c4)
            if i < 3:
                top(l - 2*r)
        top(x/2.0-r)

        self.corner(90)
        self.edge(topwidth)
        self.doveTailJointCounterPart(h)
        self.edge(bottomwidth)
        self.corner(90)

        self.ctx.restore()
        self.ctx.stroke()

        self.move(overallwidth, overallheight, move)


    def rectangularWall(self, x, y, edges="eeee",
                        holesMargin=None, holesSettings=None,
                        bedBolts=None, bedBoltSettings=None,
                        callback=None,
                        move=None):
        if len(edges) != 4:
            raise ValueError("four edges required")
        edges = [self.edges.get(e, e) for e in edges]
        edges += edges # append for wrapping around

        overallwidth = x + edges[-1].spacing() + edges[1].spacing()
        overallheight = y + edges[0].spacing() + edges[2].spacing()

        if self.move(overallwidth, overallheight, move, before=True):
            return

        self.ctx.save()
        self.moveTo(edges[-1].margin(), edges[0].margin())
        for i, l in enumerate((x, y, x, y)):
            self.edge(edges[i-1].width())
            self.cc(callback, i, y=edges[i].width()+self.burn)
            edges[i](l,
                     bedBolts=self.getEntry(bedBolts, i),
                     bedBoltSettings=self.getEntry(bedBoltSettings, i))
            self.edge(edges[i+1].width())
            self.corner(90-edges[i].endAngle()-edges[i+1].startAngle())

        if holesMargin is not None:
            self.moveTo(holesMargin+edges[-1].width(),
                        holesMargin+edges[0].width())
            self.hexHolesRectangle(x-2*holesMargin, y-2*holesMargin)
        self.ctx.restore()
        self.ctx.stroke()

        self.move(overallwidth, overallheight, move)


    ##################################################
    ### main
    ##################################################

    def render(self, x, y, h):
        self.ctx.save()

        self.moveTo(10, 10)
        self.roundedPlate(x, y, 0)
        self.moveTo(x+40, 0)
        self.rectangularWall(x, y, "FFFF")

        self.ctx.restore()

        self.moveTo(10, y+20)
        for i in range(2):
            for l in (x, y):
                self.rectangularWall(l, h, "hffF")
                self.moveTo(l+20, 0)
            self.moveTo(-x-y-40, h+20)


        self.close()

if __name__ == '__main__':
    b = Boxes(900, 700)
    b.render(100, 161.8, 120)
