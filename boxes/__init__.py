#!/usr/bin/python3
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
import argparse
from argparse import ArgumentParser
import re
from functools import wraps
from boxes import edges

def dist(dx, dy):
    """
    Return distance

    :param dx: delta x
    :param dy: delat y
    """
    return (dx*dx+dy*dy)**0.5

def restore(func):
    """
    Wrapper: Restore coordiantes after function

    :param func: function to wrap

    """
    @wraps(func)
    def f(self, *args, **kw):
        self.ctx.save()
        pt = self.ctx.get_current_point()
        func(self, *args, **kw)
        self.ctx.restore()
        self.ctx.move_to(*pt)
    return f


#############################################################################
### Building blocks
#############################################################################

class NutHole:
    """Draw a hex nut"""
    sizes = {
        "M1.6" : (3.2, 1.3),
        "M2" : (4, 1.6),
        "M2.5" : (5, 2.0),
        "M3" : (5.5, 2.4),
        "M4" : (7, 3.2),
        "M5" : (8, 4.7),
        "M6" : (10, 5.2),
        "M8" : (13, 6.8),
        "M10" : (16, 8.4),
        "M12" : (18, 10.8),
        "M14" : (21, 12.8),
        "M16" : (24, 14.8),
        "M20" : (30, 18.0),
        "M24" : (36, 21.5),
        "M30" : (46, 25.6),
        "M36" : (55, 31),
        "M42" : (65, 34),
        "M48" : (75, 38),
        "M56" : (85, 45),
        "M64" : (95, 51),
        }

    def __init__(self, boxes, settings):
        self.boxes = boxes
        self.ctx = boxes.ctx
        self.settings = settings

    @restore
    def __call__(self, size, x=0, y=0, angle=0):
        size = self.sizes.get(size, (size,))[0]
        side = size / 3**0.5
        self.boxes.moveTo(x, y, angle)
        self.boxes.moveTo(-0.5*side, 0.5*size, angle)
        for i in range(6):
            self.boxes.edge(side)
            self.boxes.corner(-60)

def argparseSections(s):
    """
    Parse sections parameter

    :param s: string to parse

    """
    m = re.match(r"(\d+(\.\d+)?)/(\d+)", s)
    if m:
        n = int(m.group(3))
        print([ float(m.group(1)) ] * n)
        return [ float(m.group(1))/n ] * n
    m = re.match(r"(\d+(\.\d+)?)\*(\d+)", s)
    if m:
        n = int(m.group(3))
        return [ float(m.group(1)) ] * n
    try:
        return [float(part) for part in s.split(":")]
    except ValueError:
        raise argparse.ArgumentTypeError("Don't understand sections string")

class Boxes:
    """Main class -- Generator should sub class this """

    def __init__(self):
        self.argparser = ArgumentParser(description=self.__doc__)
        self.argparser.add_argument(
            "--fingerjointfinger",  action="store", type=float, default=1.0,
            help="width of the fingers in multiples of thickness")
        self.argparser.add_argument(
            "--fingerjointspace",  action="store", type=float, default=1.0,
            help="width of the space between fingers in multiples of thickness")
        self.argparser.add_argument(
            "--fingerjointsurrounding",  action="store", type=float, default=1.0,
            help="amount of space needed at the end in multiples of normal spaces")
        self.argparser.add_argument(
            "--thickness",  action="store", type=float, default=4.0,
            help="thickness of the material")
        self.argparser.add_argument(
            "--output",  action="store", type=str, default="box.svg",
            help="name of resulting file")
        self.argparser.add_argument(
            "--debug",  action="store_true", default=False,
            help="print surrounding boxes for some structures")
        self.argparser.add_argument(
            "--burn",  action="store", type=float, default=0.05,
            help="burn correction in mm")

    def open(self, width, height):
        """
        Prepare for rendering

        Call this function from your .render() method

        :param width: width of canvas in mm
        :param height: height of canvas in mm

        """
        self.spacing = 2*self.burn + 0.5 * self.thickness

        self.fingerHoleEdgeWidth = 1.0    # multitudes of self.thickness
        self.bedBoltSettings = (3, 5.5, 2, 20, 15) #d, d_nut, h_nut, l, l1
        self.hexHolesSettings = (5, 3, 'circle') # r, dist, style
        self._init_surface(width, height)
        self._buildObjects()

    def buildArgParser(self, *l):
        """
        Add commonly used commandf line parameters

        :param \*l: parameter names

        """
        for arg in l:
            if arg == "x":
                self.argparser.add_argument(
                    "--x",  action="store", type=float, default=100.0,
                    help="inner width in mm")
            elif arg == "y":
                self.argparser.add_argument(
                    "--y",  action="store", type=float, default=100.0,
                    help="inner depth in mm")
            elif arg == "sx":
                self.argparser.add_argument(
                    "--sx",  action="store", type=argparseSections,
                    default="50*3",
                    help="""sections left to right in mm. Possible formats: overallwidth/numberof sections e.g. "250/5"; sectionwith*numberofsections e.g. "50*5"; section widths separated by ":" e.g. "30:25.5:70"
""")
            elif arg == "sy":
                self.argparser.add_argument(
                    "--sy",  action="store", type=argparseSections,
                    default="50*3",
                    help="""sections back to front in mm. See --sx for format""")
            elif arg == "h":
                self.argparser.add_argument(
                    "--h",  action="store", type=float, default=100.0,
                    help="inner height in mm")
            elif arg == "hi":
                self.argparser.add_argument(
                    "--hi",  action="store", type=float, default=0.0,
                    help="inner height of inner walls in mm (leave to zero for same as outer walls)")
            else:
                raise ValueError("No default for argument", arg)

    def parseArgs(self, args=None):
        """
        Parse command line parameters

        :param args:  (Default value = None) parameters, None for using sys.argv

        """
        self.argparser.parse_args(args=args, namespace=self)

    def addPart(self, part, name=None):
        """
        Add Edge or other part instance to this one and add it as attribute

        :param part: Callable
        :param name:  (Default value = None) attribute name (__name__ as default)

        """
        if name is None:
            name = part.__class__.__name__
            name = name[0].lower() + name[1:]
        #if not hasattr(self, name):
        if isinstance(part, edges.Edge):
            self.edges[part.char] = part
        else:
            setattr(self, name, part)

    def _buildObjects(self):
        """Add default edges and parts """
        self.edges = {}
        self.addPart(edges.Edge(self, None))
        self.addPart(edges.OutSetEdge(self, None))

        # Share settings object
        s = edges.FingerJointSettings(self.thickness)
        s.setValues(self.thickness,
                    finger=getattr(self, "fingerjointfinger", 1.0),
                    space=getattr(self, "fingerjointspace", 1.0),
                    surroundingspaces=getattr(self, "fingerjointsurrounding", 1.0))
        self.addPart(edges.FingerJointEdge(self, s))
        self.addPart(edges.FingerJointEdgeCounterPart(self, s))
        self.addPart(edges.FingerHoleEdge(self, s))
        self.addPart(edges.FingerHoles(self, s))

        s = edges.DoveTailSettings(self.thickness)
        self.addPart(edges.DoveTailJoint(self, s))
        self.addPart(edges.DoveTailJointCounterPart(self, s))
        s = edges.FlexSettings(self.thickness)
        self.addPart(edges.FlexEdge(self, s))

        self.addPart(NutHole(self, None))

    def _init_surface(self, width, height):
        """
        Initialize cairo canvas

        :param width: canvas size
        :param height: canvas height

        """
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

    def render(self):
        """Implement this method in your sub class.

        You will typically need to call .parseArgs() before calling this one"""
        self.open(100, 100)
        # Change settings and creat new Edges and part classes here
        raise NotImplemented
        self.close()

    def cc(self, callback, number, x=0.0, y=None):
        """Call callback from edge of a part

        :param callback: callback (callable or list of callables)
        :param number: number of the callback
        :param x:  (Default value = 0.0) x position to be call on
        :param y:  (Default value = None) y position to be called on (default does burn correction)

        """
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
        """
        Get entry from list or items itself

        :param param: list or item
        :param idx: index in list

        """
        if isinstance(param, list):
            if len(param)>idx:
                return param[idx]
            else:
                return None
        else:
            return param

    def close(self):
        """Finish rendering

        Call at the end of your .render() method"""
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
            print("Could not replace pt with mm")
        pos = s.find('pt"', pos+3)
        if pos > 0:
            f.seek(pos)
            f.write("mm")
        else:
            print("Could not replace pt with mm")

    ############################################################
    ### Turtle graphics commands
    ############################################################

    def corner(self, degrees, radius=0):
        """
        Draw a corner

        This is what does the burn corrections

        :param degrees: angle
        :param radius:  (Default value = 0)

        """
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
        """
        Simple line
        :param length: length in mm

        """
        self.ctx.move_to(0,0)
        self.ctx.line_to(length, 0)
        self.ctx.translate(*self.ctx.get_current_point())

    def curveTo(self, x1, y1, x2, y2, x3, y3):
        """control point 1, control point 2, end point

        :param x1: 
        :param y1: 
        :param x2: 
        :param y2: 
        :param x3: 
        :param y3: 

        """
        self.ctx.curve_to(x1, y1, x2, y2, x3, y3)
        dx = x3-x2
        dy = y3-y2
        rad = math.atan2(dy, dx)
        self.continueDirection(rad)

    def polyline(self, *args):
        """
        Draw multiple connected lines

        :param \*args: Alternating length in mm and angle

        """
        for i, arg in enumerate(args):
            if i % 2:
                self.corner(arg)
            else:
                self.edge(arg)

    def bedBoltHole(self, length, bedBoltSettings=None):
        """
        Draw an edge with slot for a bed bolt

        :param length: length of the edge in mm
        :param bedBoltSettings:  (Default value = None) Dimmensions of the slot

        """
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
        """Corrugated edge useful as an gipping area

        :param length: length
        :param depth: depth of the grooves

        """
        grooves = int(length // (depth*2.0)) + 1
        depth = length / grooves / 4.0
        for groove in range(grooves):
            self.corner(90, depth)
            self.corner(-180, depth)
            self.corner(90, depth)

    def _latchHole(self, length):
        """

        :param length:

        """
        self.edge(1.1*self.thickness)
        self.corner(-90)
        self.edge(length/2.0+0.2*self.thickness)
        self.corner(-90)
        self.edge(1.1*self.thickness)

    def _latchGrip(self, length):
        """

        :param length:

        """
        self.corner(90, self.thickness/4.0)
        self.grip(length/2.0-self.thickness/2.0-0.2*self.thickness, self.thickness/2.0)
        self.corner(90, self.thickness/4.0)

    def latch(self, length, positive=True, reverse=False):
        """Latch to fix a flex box door to the box

        :param length: length in mm
        :param positive:  (Default value = True) False: Door side; True: Box side
        :param reverse:  (Default value = False) True when running away from the latch

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
        """Creates an Edge with a handle

        :param x: width in mm
        :param h: height in mm
        :param hl: height if th grip hole
        :param r:  (Default value = 30) radius of the corners

        """
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
        """
        Move coordinate system to given point

        :param x:
        :param y:  (Default value = 0.0)
        :param degrees:  (Default value = 0)

        """
        self.ctx.move_to(0, 0)
        self.ctx.translate(x, y)
        self.ctx.rotate(degrees*math.pi/180.0)
        self.ctx.move_to(0, 0)

    def continueDirection(self, angle=0):
        """
        Set coordinate system to current position (end point)

        :param angle:  (Default value = 0) heading

        """
        self.ctx.translate(*self.ctx.get_current_point())
        self.ctx.rotate(angle)

    def move(self, x, y, where, before=False):
        """Intended to be used by parts
        where can be combinations of "up", "down", "left", "right" and "only"
        when "only" is included the move is only done when before is True
        The function returns whether actual drawing of the part
        should be omited.

        :param x: width of part
        :param y: height of part
        :param where: which direction to move
        :param before:  (Default value = False) called before or after part being drawn

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
        """
        Draw holes for a matching finger joint edge

        :param x: position
        :param y: position
        :param length: length of matching edge
        :param angle:  (Default value = 90)
        :param bedBolts:  (Default value = None)
        :param bedBoltSettings:  (Default value = None)

        """
        self.ctx.save()
        self.moveTo(x, y, angle)
        self.fingerHoles(length, bedBolts, bedBoltSettings)
        self.ctx.restore()

    @restore
    def hole(self, x, y, r):
        """
        Draw a round hole

        :param x: position
        :param y: postion
        :param r: radius

        """
        r -= self.burn
        if r < 0:
            r = 1E-9
        self.moveTo(x+r, y)
        self.ctx.arc(-r, 0, r, 0, 2*math.pi)

    @restore
    def rectangularHole(self, x, y, dx, dy, r=0):
        """
        Draw an rectangulat hole

        :param x: position
        :param y: position
        :param dx: width
        :param dy: height
        :param r:  (Default value = 0) radius of the corners

        """
        self.moveTo(x+r-dx/2.0, y-dy/2.0, 180)
        for d in (dy, dx, dy, dx):
            self.corner(-90, r)
            self.edge(d-2*r)

    @restore
    def text(self, text, x=0, y=0, angle=0, align=""):
        """
        Draw text

        :param text: text to render
        :param x:  (Default value = 0)
        :param y:  (Default value = 0)
        :param angle:  (Default value = 0)
        :param align:  (Default value = "") string with combinations of (top|middle|bottom) and (left|center|right) separated by a space

        """
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
        """Draw holes for mounting a NEMA stepper motor

        :param size: Nominal size in tenths of inches
        :param x:  (Default value = 0)
        :param y:  (Default value = 0)
        :param angle:  (Default value = 0)

        """
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
        """Fills a rectangle with holes in a hex pattern.

        Settings have:
        r : radius of holes
        b : space between holes
        style : what types of holes (not yet implemented)

        :param x: width
        :param y: heigth
        :param settings:  (Default value = None)
        :param skip:  (Default value = None) function to check if hole should be present
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
        """
        Fill circle with holes in a hex pattern

        :param d: diameter of the circle
        :param settings:  (Default value = None)

        """
        d2 = d/2.0
        self.hexHolesRectangle(d, d, settings=settings, skip=self.__skipcircle)

    def hexHolesPlate(self, x, y, rc, settings=None):
        """
        Fill a plate with holes in a hex pattern

        :param x: width
        :param y: height
        :param rc: radius of the corners
        :param settings:  (Default value = None)

        """
        def skip(x, y, r, b, posx, posy):
            """

            :param x: 
            :param y: 
            :param r: 
            :param b: 
            :param posx: 
            :param posy: 

            """
            posx = abs(posx-(x/2.0))
            posy = abs(posy-(y/2.0))

            wx = 0.5*x-rc-r
            wy = 0.5*y-rc-r

            if (posx <= wx) or (posy <= wx):
                return 0
            return dist(posx-wx, posy-wy) > rc

        self.hexHolesRectangle(x, y, settings, skip=skip)

    def hexHolesHex(self, h, settings=None, grow=None):
        """
        Fill a hexagon with holes in a hex pattern

        :param h: height
        :param settings:  (Default value = None)
        :param grow:  (Default value = None)

        """
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
        """Plate with rounded corner fitting to .surroundingWall()

        First edge is split to have a joint in the middle of the side
        callback is called at the beginning of the straight edges
        0, 1 for the two part of the first edge, 2, 3, 4 for the others

        :param x: width
        :param y: hight
        :param r: radius of the corners
        :param callback:  (Default value = None)
        :param holesMargin:  (Default value = None) set to get hex holes
        :param holesSettings:  (Default value = None)
        :param bedBolts:  (Default value = None)
        :param bedBoltSettings:  (Default value = None)
        :param move:  (Default value = None)

        """

        overallwidth = x+2*self.edges["f"].spacing()
        overallheight = y+2*self.edges["f"].spacing()

        if self.move(overallwidth, overallheight, move, before=True):
            return

        self.ctx.save()
        self.moveTo(self.edges["f"].margin(),
                    self.edges["f"].margin())
        self.moveTo(r, 0)

        self.cc(callback, 0)
        self.edges["f"](x/2.0-r, bedBolts=self.getEntry(bedBolts, 0),
                         bedBoltSettings=self.getEntry(bedBoltSettings, 0))
        self.cc(callback, 1)
        self.edges["f"](x/2.0-r, bedBolts=self.getEntry(bedBolts, 1),
                         bedBoltSettings=self.getEntry(bedBoltSettings, 1))
        for i, l in zip(range(3), (y, x, y)):
            self.corner(90, r)
            self.cc(callback, i+2)
            self.edges["f"](l-2*r, bedBolts=self.getEntry(bedBolts, i+2),
                         bedBoltSettings=self.getEntry(bedBoltSettings, i+2))
        self.corner(90, r)

        self.ctx.restore()
        self.ctx.save()

        self.moveTo(self.edges["f"].margin(),
                    self.edges["f"].margin())

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
                        left="D", right="d",
                        callback=None,
                        move=None):
        """h : inner height, not counting the joints
        callback is called a beginn of the flat sides with

        *  0 for right half of first x side;
        *  1 and 3 for y sides;
        *  2 for second x side
        *  4 for second half of the first x side

        :param x: width of matching roundedPlate
        :param y: height of matching roundedPlate
        :param r: corner radius of matching roundedPlate
        :param h: height of the wall
        :param bottom:  (Default value = 'e') Edge type
        :param top:  (Default value = 'e') Edge type
        :param callback:  (Default value = None)
        :param move:  (Default value = None)

        """
        c4 = (r+self.burn)*math.pi*0.5 # circumference of quarter circle
        c4 = c4 / self.edges["X"].settings.stretch

        top = self.edges.get(top, top)
        bottom = self.edges.get(bottom, bottom)
        left = self.edges.get(left, left)
        right = self.edges.get(right, right)

        topwidth = top.width()
        bottomwidth = bottom.width()

        overallwidth = 2*x + 2*y - 8*r + 4*c4 + \
            self.edges["d"].spacing() + self.edges["D"].spacing()
        overallheight = h + top.spacing() + bottom.spacing()


        if self.move(overallwidth, overallheight, move, before=True):
            return

        self.ctx.save()
        self.moveTo(left.margin(), bottom.margin())

        self.cc(callback, 0, y=bottomwidth+self.burn)
        bottom(x/2.0-r)
        if (y-2*r) < 1E-3:
            self.edges["X"](2*c4, h+topwidth+bottomwidth)
            self.cc(callback, 2, y=bottomwidth+self.burn)
            bottom(x-2*r)
            self.edges["X"](2*c4, h+topwidth+bottomwidth)
        else:
            for i, l in zip(range(4), (y, x, y, 0)):
                self.edges["X"](c4, h+topwidth+bottomwidth)
                self.cc(callback, i+1, y=bottomwidth+self.burn)
                if i < 3:
                    bottom(l-2*r)
        bottom(x/2.0-r)

        self.corner(90)
        self.edge(bottomwidth)
        right(h)
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
        left(h)
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
        """
        Rectangular wall for all kind of box like objects

        :param x: width
        :param y: height
        :param edges:  (Default value = "eeee") bottom, right, top, left
        :param holesMargin:  (Default value = None)
        :param holesSettings:  (Default value = None)
        :param bedBolts:  (Default value = None)
        :param bedBoltSettings:  (Default value = None)
        :param callback:  (Default value = None)
        :param move:  (Default value = None)

        """
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

class DemoBox(Boxes):
    """A simple fully enclosed box showcasing different finger joints"""
    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("x", "y", "h")

    def render(self):
        """ """
        x, y, h, t = self.x, self.y, self.h, self.thickness
        self.open(2*x+10*self.thickness, y+2*h+20*self.thickness)
        self.ctx.save()

        self.moveTo(t, t)
        self.rectangularWall(x, y, "ffff")
        self.moveTo(x+4*t, 0)
        self.rectangularWall(x, y, "FFFF")

        self.ctx.restore()

        self.moveTo(t, y+4*t)
        for i in range(2):
            for l in (x, y):
                self.rectangularWall(l, h, "hffF")
                self.moveTo(l+4*t, 0)
            self.moveTo(-x-y-8*t, h+4*t)


        self.close()

if __name__ == '__main__':
    b = DemoBox()
    b.parseArgs()
    b.render()
