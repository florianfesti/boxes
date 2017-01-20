#!/usr/bin/env python3
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

try:
    import cairocffi

    cairocffi.install_as_pycairo()
except ImportError:
    pass
import cairo
import math
import argparse
from argparse import ArgumentParser
import re
from functools import wraps
from boxes import edges
from boxes import formats
from boxes import gears
from boxes import pulley
from boxes import parts


### Helpers

def dist(dx, dy):
    """
    Return distance

    :param dx: delta x
    :param dy: delat y
    """
    return (dx * dx + dy * dy) ** 0.5


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


def holeCol(func):
    """
    Wrapper: color holes differently

    :param func: function to wrap

    """

    @wraps(func)
    def f(self, *args, **kw):
        self.ctx.stroke()
        self.ctx.set_source_rgb(0.0, 0.0, 1.0)
        func(self, *args, **kw)
        self.ctx.stroke()
        self.ctx.set_source_rgb(0.0, 0.0, 0.0)

    return f


#############################################################################
### Building blocks
#############################################################################

class NutHole:
    """Draw a hex nut"""
    sizes = {
        "M1.6": (3.2, 1.3),
        "M2": (4, 1.6),
        "M2.5": (5, 2.0),
        "M3": (5.5, 2.4),
        "M4": (7, 3.2),
        "M5": (8, 4.7),
        "M6": (10, 5.2),
        "M8": (13.7, 6.8),
        "M10": (16, 8.4),
        "M12": (18, 10.8),
        "M14": (21, 12.8),
        "M16": (24, 14.8),
        "M20": (30, 18.0),
        "M24": (36, 21.5),
        "M30": (46, 25.6),
        "M36": (55, 31),
        "M42": (65, 34),
        "M48": (75, 38),
        "M56": (85, 45),
        "M64": (95, 51),
    }

    def __init__(self, boxes, settings):
        self.boxes = boxes
        self.ctx = boxes.ctx
        self.settings = settings

    @restore
    @holeCol
    def __call__(self, size, x=0, y=0, angle=0):
        size = self.sizes.get(size, (size,))[0]
        side = size / 3 ** 0.5
        self.boxes.moveTo(x, y, angle)
        self.boxes.moveTo(-0.5 * side, 0.5 * size, angle)
        for i in range(6):
            self.boxes.edge(side)
            self.boxes.corner(-60)


##############################################################################
### Argument types
##############################################################################

def argparseSections(s):
    """
    Parse sections parameter

    :param s: string to parse

    """
    m = re.match(r"(\d+(\.\d+)?)/(\d+)", s)
    if m:
        n = int(m.group(3))
        print([float(m.group(1))] * n)
        return [float(m.group(1)) / n] * n
    m = re.match(r"(\d+(\.\d+)?)\*(\d+)", s)
    if m:
        n = int(m.group(3))
        return [float(m.group(1))] * n
    try:
        return [float(part) for part in s.split(":")]
    except ValueError:
        raise argparse.ArgumentTypeError("Don't understand sections string")


class ArgparseEdgeType:
    names = edges.getDescriptions()
    edges = []

    def __init__(self, edges=None):
        if edges:
            self.edges = list(edges)

    def __call__(self, pattern):
        if len(pattern) != 1:
            raise ValueError("Edge type can only have one letter.")
        if pattern not in self.edges:
            raise ValueError("Use one of the following values: " +
                             ", ".join(edges))
        return pattern

    def html(self, name, default):
        options = "\n".join(
            ("""<option value="%s"%s>%s %s</option>""" %
             (e, ' selected="selected"' if e == default else "",
              e, self.names.get(e, "")) for e in self.edges))
        return """<select name="%s" size="1">\n%s</select>\n""" % (name, options)

class BoolArg:
    def __call__(self, arg):
        if not arg or arg in ("None", "0", "off", "False"):
            return False
        return True

    def html(self, name, default):
        return """<input name="%s" type="hidden" value="0">
<input name="%s" type="checkbox" value="1"%s>""" % \
            (name, name, ' checked="checked"' if default else "")

boolarg = BoolArg()

##############################################################################
### Main class
##############################################################################

class Boxes:
    """Main class -- Generator should sub class this """

    webinterface = True

    def __init__(self):
        self.formats = formats.Formats()
        self.argparser = ArgumentParser(description=self.__doc__)
        self.edgesettings = {}
        self.argparser._action_groups[1].title = self.__class__.__name__ + " Settings"

        defaultgroup = self.argparser.add_argument_group(
                        "Default Settings")
        defaultgroup.add_argument(
            "--thickness", action="store", type=float, default=4.0,
            help="thickness of the material")
        defaultgroup.add_argument(
            "--output", action="store", type=str, default="box.svg",
            help="name of resulting file")
        defaultgroup.add_argument(
            "--format", action="store", type=str, default="svg",
            choices=self.formats.getFormats(),
            help="format of resulting file")
        defaultgroup.add_argument(
            "--debug", action="store", type=boolarg, default=False,
            help="print surrounding boxes for some structures")
        defaultgroup.add_argument(
            "--reference", action="store", type=float, default=100,
            help="print reference rectangle with given length")
        defaultgroup.add_argument(
            "--burn", action="store", type=float, default=0.05,
            help="burn correction in mm (bigger values for tighter fit)")

    def open(self):
        """
        Prepare for rendering

        Call this function from your .render() method
        """
        self.spacing = 2 * self.burn + 0.5 * self.thickness

        self.bedBoltSettings = (3, 5.5, 2, 20, 15)  # d, d_nut, h_nut, l, l1
        self.hexHolesSettings = (5, 3, 'circle')  # r, dist, style
        self.surface, self.ctx = self.formats.getSurface(self.format, self.output)
        self.ctx.set_line_width(2 * self.burn)
        self._buildObjects()
        if self.reference:
            self.move(10, 10, "up", before=True)
            self.ctx.rectangle(0, 0, self.reference, 10)
            if self.reference < 40:
                self.text("%.fmm" % self.reference, self.reference + 5, 5,
                          align="middle left")
            else:
                self.text("%.fmm" % self.reference, self.reference / 2.0, 5,
                          align="middle center")
            self.move(10, 10, "up")

    def buildArgParser(self, *l):
        """
        Add commonly used commandf line parameters

        :param \*l: parameter names

        """
        for arg in l:
            if arg == "x":
                self.argparser.add_argument(
                    "--x", action="store", type=float, default=100.0,
                    help="inner width in mm")
            elif arg == "y":
                self.argparser.add_argument(
                    "--y", action="store", type=float, default=100.0,
                    help="inner depth in mm")
            elif arg == "sx":
                self.argparser.add_argument(
                    "--sx", action="store", type=argparseSections,
                    default="50*3",
                    help="""sections left to right in mm. Possible formats: overallwidth/numberof sections e.g. "250/5"; sectionwidth*numberofsections e.g. "50*5"; section widths separated by ":" e.g. "30:25.5:70"
""")
            elif arg == "sy":
                self.argparser.add_argument(
                    "--sy", action="store", type=argparseSections,
                    default="50*3",
                    help="""sections back to front in mm. See --sx for format""")
            elif arg == "h":
                self.argparser.add_argument(
                    "--h", action="store", type=float, default=100.0,
                    help="inner height in mm")
            elif arg == "hi":
                self.argparser.add_argument(
                    "--hi", action="store", type=float, default=0.0,
                    help="inner height of inner walls in mm (leave to zero for same as outer walls)")
            elif arg == "bottom_edge":
                self.argparser.add_argument(
                    "--bottom_edge", action="store",
                    type=ArgparseEdgeType("Fhs"), choices=list("Fhs"),
                    default="h",
                    help="edge type for bottom edge")
            elif arg == "top_edge":
                self.argparser.add_argument(
                    "--top_edge", action="store",
                    type=ArgparseEdgeType("ecESikfL"), choices=list("ecESikfL"),
                    default="e", help="edge type for top edge")
            elif arg == "outside":
                self.argparser.add_argument(
                    "--outside", action="store", type=boolarg, default=True,
                    help="treat sizes as outside measurements that include the walls")
            else:
                raise ValueError("No default for argument", arg)

    def addSettingsArgs(self, settings, prefix=None, **defaults):
        prefix = prefix or settings.__name__[:-len("Settings")]
        settings.parserArguments(self.argparser, prefix, **defaults)
        self.edgesettings[prefix] =  {}
        

    def parseArgs(self, args=None):
        """
        Parse command line parameters

        :param args:  (Default value = None) parameters, None for using sys.argv

        """
        for key, value in vars(self.argparser.parse_args(args=args)).items():
            # treat edge settings separately 
            for setting in self.edgesettings:
                if key.startswith(setting + '_'):
                    self.edgesettings[setting][key[len(setting)+1:]] = value
                    continue
            setattr(self, key, value)

        # Change file ending to format if not given explicitly
        if getattr(self, 'output', None) == 'box.svg':
            self.output = 'box.' + getattr(self, "format", "svg")

    def addPart(self, part, name=None):
        """
        Add Edge or other part instance to this one and add it as attribute

        :param part: Callable
        :param name:  (Default value = None) attribute name (__name__ as default)

        """
        if name is None:
            name = part.__class__.__name__
            name = name[0].lower() + name[1:]
        # if not hasattr(self, name):
        if isinstance(part, edges.BaseEdge):
            self.edges[part.char] = part
        else:
            setattr(self, name, part)

    def addParts(self, parts):
        for part in parts:
            self.addPart(part)

    def _buildObjects(self):
        """Add default edges and parts """
        self.edges = {}
        self.addPart(edges.Edge(self, None))
        self.addPart(edges.OutSetEdge(self, None))
        edges.GripSettings(self.thickness).edgeObjects(self)

        # Finger joints
        # Share settings object
        s = edges.FingerJointSettings(self.thickness, True,
                **self.edgesettings.get("FingerJoint", {}))
        s.edgeObjects(self)
        self.addPart(edges.FingerHoles(self, s), name="fingerHolesAt")
        # Stackable
        edges.StackableSettings(self.thickness, True,
            **self.edgesettings.get("Stackable", {})).edgeObjects(self)
        # Dove tail joints
        edges.DoveTailSettings(self.thickness, True,
            **self.edgesettings.get("DoveTail", {})).edgeObjects(self)
        # Flex
        s = edges.FlexSettings(self.thickness, True,
                **self.edgesettings.get("Flex", {}))
        self.addPart(edges.FlexEdge(self, s))
        # Clickable
        edges.ClickSettings(self.thickness, True,
                **self.edgesettings.get("Click", {})).edgeObjects(self)
        # Hinges
        edges.HingeSettings(self.thickness, True,
                **self.edgesettings.get("Hinge", {})).edgeObjects(self)
        # Sliding Lid
        edges.LidSettings(self.thickness, True,
                **self.edgesettings.get("Lid", {})).edgeObjects(self)

        # Nuts
        self.addPart(NutHole(self, None))
        # Gears
        self.addPart(gears.Gears(self))
        s = edges.GearSettings(self.thickness, True,
                **self.edgesettings.get("Gear", {}))
        self.addPart(edges.RackEdge(self, s))
        self.addPart(pulley.Pulley(self))
        self.addPart(parts.Parts(self))

    def adjustSize(self, l, e1=True, e2=True):
        try:
            total = sum(l)
            walls = (len(l) - 1) * self.thickness
        except TypeError:
            total = l
            walls = 0

        if isinstance(e1, edges.BaseEdge):
            walls += e1.startwidth() + e1.margin()
        elif e1:
            walls += self.thickness

        if isinstance(e2, edges.BaseEdge):
            walls += e2.startwidth + e2.margin()
        elif e2:
            walls += self.thickness

        try:
            factor = (total - walls) / total
            return [s * factor for s in l]
        except TypeError:
            return l - walls

    def render(self):
        """Implement this method in your sub class.

        You will typically need to call .parseArgs() before calling this one"""
        self.open()
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

        if hasattr(callback, '__getitem__'):
            try:
                callback = callback[number]
                number = None
            except (KeyError, IndexError):
                pass

        if callback and callable(callback):
            self.ctx.save()
            self.moveTo(x, y)
            if number is None:
                callback()
            else:
                callback(number)
            self.ctx.restore()
            self.ctx.move_to(0, 0)

    def getEntry(self, param, idx):
        """
        Get entry from list or items itself

        :param param: list or item
        :param idx: index in list

        """
        if isinstance(param, list):
            if len(param) > idx:
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

        self.formats.convert(self.output, self.format)

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
        if radius > 0.5* self.thickness:
            while degrees > 100:
                self.corner(90, radius)
                degrees -= 90
            while degrees < -100:
                self.corner(-90, radius)
                degrees -= -90

        rad = degrees * math.pi / 180
        if degrees > 0:
            self.ctx.arc(0, radius + self.burn, radius + self.burn,
                         -0.5 * math.pi, rad - 0.5 * math.pi)
        elif radius > self.burn:
            self.ctx.arc_negative(0, -(radius - self.burn), radius - self.burn,
                                  0.5 * math.pi, rad + 0.5 * math.pi)
        else:  # not rounded inner corner
            self.ctx.arc_negative(0, self.burn - radius, self.burn - radius,
                                  -0.5 * math.pi, -0.5 * math.pi + rad)

        self.continueDirection(rad)

    def edge(self, length):
        """
        Simple line
        :param length: length in mm

        """
        self.ctx.move_to(0, 0)
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
        dx = x3 - x2
        dy = y3 - y2
        rad = math.atan2(dy, dx)
        self.continueDirection(rad)

    def polyline(self, *args):
        """
        Draw multiple connected lines

        :param \*args: Alternating length in mm and angle. angle may be tuple
                       (angle, radius)

        """
        for i, arg in enumerate(args):
            if i % 2:
                if isinstance(arg, tuple):
                    self.corner(*arg)
                else:
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
        self.edge((length - d) / 2.0)
        self.corner(90)
        self.edge(l1)
        self.corner(90)
        self.edge((d_nut - d) / 2.0)
        self.corner(-90)
        self.edge(h_nut)
        self.corner(-90)
        self.edge((d_nut - d) / 2.0)
        self.corner(90)
        self.edge(l - l1 - h_nut)
        self.corner(-90)
        self.edge(d)
        self.corner(-90)
        self.edge(l - l1 - h_nut)
        self.corner(90)
        self.edge((d_nut - d) / 2.0)
        self.corner(-90)
        self.edge(h_nut)
        self.corner(-90)
        self.edge((d_nut - d) / 2.0)
        self.corner(90)
        self.edge(l1)
        self.corner(90)
        self.edge((length - d) / 2.0)

    def edgeCorner(self, edge1, edge2, angle=90):
        """Make a corner between two Edges. Take width of edges into account"""
        self.edge(edge2.startwidth() * math.tan(math.radians(angle/2.)))
        self.corner(angle)
        self.edge(edge1.endwidth() * math.tan(math.radians(angle/2.)))

    def regularPolygon(self, corners=3, radius=None, h=None, side=None):
        """Give messures of a regular polygone
        :param corners: number of corners of the polygone
        :param radius: distance center to one of the corners
        :param h: distance center to one of the sides (height of sector)
        :param side: length of one side
        :return (radius, h, side)
        """
        if radius:
            side = 2 * math.sin(math.radians(180.0/corners)) * radius
            h = radius * math.cos(math.radians(180.0/corners))
        elif h:
            side = 2 * math.tan(math.radians(180.0/corners)) * h
            radius = ((side/2.)**2+h**2)**0.5
        elif side:
            h = 0.5 * side * math.tan(math.radians(90-180./corners))
            radius = ((side/2.)**2+h**2)**0.5

        return radius, h, side

    @restore
    def regularPolygonAt(self, x, y, corners, angle=0, r=None, h=None, side=None):
        """Draw regular polygone"""
        self.moveTo(x, y, angle)
        r, h, side  = self.regularPolygon(corners, r, h, side)
        self.moveTo(-side/2.0, -h-self.burn)
        for i in range(corners):
            self.edge(side)
            self.corner(360./corners)

    def regularPolygonWall(self, corners=3, r=None, h=None, side=None,
                           edges='e', hole=None, callback=None, move=None):
        """Create regular polygone as a wall
        :param corners: number of corners of the polygone
        :param radius: distance center to one of the corners
        :param h: distance center to one of the sides (height of sector)
        :param side: length of one side
        :param edges:  (Default value = "e", may be string/list of length corners)
        :param hole: diameter of central hole (Default value = 0)
        :param callback:  (Default value = None, middle=0, then sides=1..)
        :param move:  (Default value = None)
        """
        r, h, side  = self.regularPolygon(corners, r, h, side)

        t = self.thickness

        if corners % 2:
            th = r + h + 2*t
        else:
            th = 2*h + 2*t
        tw = 2*r + 3*t

        if self.move(tw, th, move, before=True):
            return

        self.moveTo(r-0.5*side, 0)

        if not hasattr(edges, "__getitem__") or len(edges) == 1:
            edges = [edges] * corners
        edges = [self.edges.get(e, e) for e in edges]
        edges += edges # append for wrapping around

        if hole:
            self.hole(side/2., h+edges[0].startwidth() + self.burn, hole/2.)
        self.cc(callback, 0, side/2., h+edges[0].startwidth() + self.burn)
        for i in range(corners):
            self.cc(callback, i+1, 0, edges[i].startwidth() + self.burn)
            edges[i](side)
            self.edgeCorner(edges[i], edges[i+1], 360.0/corners)

        self.ctx.stroke()
        self.move(tw, th, move)

    def grip(self, length, depth):
        """Corrugated edge useful as an gipping area

        :param length: length
        :param depth: depth of the grooves

        """
        grooves = int(length // (depth * 2.0)) + 1
        depth = length / grooves / 4.0
        for groove in range(grooves):
            self.corner(90, depth)
            self.corner(-180, depth)
            self.corner(90, depth)

    def _latchHole(self, length):
        """

        :param length:

        """
        self.edge(1.1 * self.thickness)
        self.corner(-90)
        self.edge(length / 2.0 + 0.2 * self.thickness)
        self.corner(-90)
        self.edge(1.1 * self.thickness)

    def _latchGrip(self, length):
        """

        :param length:

        """
        self.corner(90, self.thickness / 4.0)
        self.grip(length / 2.0 - self.thickness / 2.0 - 0.2 * self.thickness, self.thickness / 2.0)
        self.corner(90, self.thickness / 4.0)

    def latch(self, length, positive=True, reverse=False):
        """Latch to fix a flex box door to the box

        :param length: length in mm
        :param positive:  (Default value = True) False: Door side; True: Box side
        :param reverse:  (Default value = False) True when running away from the latch

        """
        if positive:
            if reverse:
                self.edge(length / 2.0)
            self.corner(-90)
            self.edge(self.thickness)
            self.corner(90)
            self.edge(length / 2.0)
            self.corner(90)
            self.edge(self.thickness)
            self.corner(-90)
            if not reverse:
                self.edge(length / 2.0)
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
        d = (x - hl - 2 * r) / 2.0
        if d < 0:
            print("Handle too wide")

        self.ctx.save()

        # Hole
        self.moveTo(d + 2 * r, 0)
        self.edge(hl - 2 * r)
        self.corner(-90, r)
        self.edge(h - 3 * r)
        self.corner(-90, r)
        self.edge(hl - 2 * r)
        self.corner(-90, r)
        self.edge(h - 3 * r)
        self.corner(-90, r)

        self.ctx.restore()
        self.moveTo(0, 0)

        self.curveTo(d, 0, d, 0, d, -h + r)
        self.curveTo(r, 0, r, 0, r, r)
        self.edge(hl)
        self.curveTo(r, 0, r, 0, r, r)
        self.curveTo(h - r, 0, h - r, 0, h - r, -d)

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
        self.ctx.rotate(degrees * math.pi / 180.0)
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
            where = ""

        terms = where.split()
        dontdraw = before and "only" in terms

        x += self.spacing
        y += self.spacing
        moves = {
            "up": (0, y, False),
            "down": (0, -y, True),
            "left": (-x, 0, True),
            "right": (x, 0, False),
            "only": (0, 0, None),
        }

        if not before:
            # restore position
            self.ctx.restore()

        for term in terms:
            if not term in moves:
                raise ValueError("Unknown direction: '%s'" % term)
            x, y, movebeforeprint = moves[term]
            if movebeforeprint and before:
                self.moveTo(x, y)
            elif (not movebeforeprint and not before) or dontdraw:
                self.moveTo(x, y)
        if not dontdraw:
            if before:
                # save position
                self.ctx.save()
                self.moveTo(self.spacing / 2.0, self.spacing / 2.0)
        return dontdraw

    @restore
    @holeCol
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
        self.moveTo(x + r, y)
        a = 0
        n = 10
        da = 2 * math.pi / n
        for i in range(n):
            self.ctx.arc(-r, 0, r, a, a+da)
            a += da

    @restore
    @holeCol
    def rectangularHole(self, x, y, dx, dy, r=0):
        """
        Draw an rectangulat hole

        :param x: position
        :param y: position
        :param dx: width
        :param dy: height
        :param r:  (Default value = 0) radius of the corners

        """
        self.moveTo(x + r - dx / 2.0, y - dy / 2.0, 180)
        for d in (dy, dx, dy, dx):
            self.corner(-90, r)
            self.edge(d - 2 * r)

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
            "top": (0, -height),
            "middle": (0, -0.5 * height),
            "bottom": (0, 0),
            "left": (0, 0),
            "center": (-0.5 * width, 0),
            "right": (-width, 0),
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
            8: (20.3, 16, 15.4, 3),
            11: (28.2, 22, 23, 4),
            14: (35.2, 22, 26, 4),
            16: (39.2, 22, 31, 4),
            17: (42.2, 22, 31, 4),
            23: (56.4, 38.1, 47.1, 5.2),
            24: (60, 36, 49.8, 5.1),
            34: (86.3, 73, 69.8, 6.6),
            42: (110, 55.5, 89, 8.5),
        }
        width, flange, holedistance, diameter = nema[size]
        self.moveTo(x, y, angle)
        if self.debug:
            self.rectangularHole(0, 0, width, width)
        self.hole(0, 0, 0.5 * flange)
        for x in (-1, 1):
            for y in (-1, 1):
                self.hole(x * 0.5 * holedistance,
                          y * 0.5 * holedistance,
                          0.5 * diameter)

    # hexHoles

    def hexHolesRectangle(self, x, y, settings=None, skip=None):
        """Fills a rectangle with holes in a hex pattern.

        Settings have:
        r : radius of holes
        b : space between holes
        style : what types of holes (not yet implemented)

        :param x: width
        :param y: height
        :param settings:  (Default value = None)
        :param skip:  (Default value = None) function to check if hole should be present
               gets x, y, r, b, posx, posy


        """
        if settings is None:
            settings = self.hexHolesSettings
        r, b, style = settings

        w = r + b / 2.0
        dist = w * math.cos(math.pi / 6.0)

        # how many half circles do fit
        cx = int((x - 2 * r) // (w)) + 2
        cy = int((y - 2 * r) // (dist)) + 2

        # what's left on the sides
        lx = (x - (2 * r + (cx - 2) * w)) / 2.0
        ly = (y - (2 * r + ((cy // 2) * 2) * dist - 2 * dist)) / 2.0

        for i in range(cy // 2):
            for j in range((cx - (i % 2)) // 2):
                px = 2 * j * w + r + lx
                py = i * 2 * dist + r + ly
                if i % 2:
                    px += w
                if skip and skip(x, y, r, b, px, py):
                    continue
                self.hole(px, py, r)

    def __skipcircle(self, x, y, r, b, posx, posy):
        cx, cy = x / 2.0, y / 2.0
        return (dist(posx - cx, posy - cy) > (cx - r))

    def hexHolesCircle(self, d, settings=None):
        """
        Fill circle with holes in a hex pattern

        :param d: diameter of the circle
        :param settings:  (Default value = None)

        """
        d2 = d / 2.0
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
            posx = abs(posx - (x / 2.0))
            posy = abs(posy - (y / 2.0))

            wx = 0.5 * x - rc - r
            wy = 0.5 * y - rc - r

            if (posx <= wx) or (posy <= wx):
                return 0
            return dist(posx - wx, posy - wy) > rc

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
        w = r + b / 2.0
        dist = w * math.cos(math.pi / 6.0)
        cy = 2 * int((h - 4 * dist) // (4 * w)) + 1

        leftover = h - 2 * r - (cy - 1) * 2 * r
        if grow == 'space ':
            b += leftover / (cy - 1) / 2

        # recalulate with adjusted values
        w = r + b / 2.0
        dist = w * math.cos(math.pi / 6.0)

        self.moveTo(h / 2.0 - (cy // 2) * 2 * w, h / 2.0)
        for j in range(cy):
            self.hole(2 * j * w, 0, r)
        for i in range(1, cy / 2 + 1):
            for j in range(cy - i):
                self.hole(j * 2 * w + i * w, i * 2 * dist, r)
                self.hole(j * 2 * w + i * w, -i * 2 * dist, r)

    def flex2D(self, x, y, width=1):
        width *= self.thickness
        cx = int(x // (5 * width))
        wx = x / 5. / cx
        cy = int(y // (5 * width))
        wy = y / 5. / cy

        armx = (4 * wx, 90, 4 * wy, 90, 2 * wx, 90, 2 * wy)
        army = (4 * wy, 90, 4 * wx, 90, 2 * wy, 90, 2 * wx)
        for i in range(cx):
            for j in range(cy):
                if (i + j) % 2:
                    self.ctx.save()
                    self.moveTo((5 * i) * wx, (5 * j) * wy)
                    self.polyline(*armx)
                    self.ctx.restore()
                    self.ctx.save()
                    self.moveTo((5 * i + 5) * wx, (5 * j + 5) * wy, -180)
                    self.polyline(*armx)
                    self.ctx.restore()
                else:
                    self.ctx.save()
                    self.moveTo((5 * i + 5) * wx, (5 * j) * wy, 90)
                    self.polyline(*army)
                    self.ctx.restore()
                    self.ctx.save()
                    self.moveTo((5 * i) * wx, (5 * j + 5) * wy, -90)
                    self.polyline(*army)
                    self.ctx.restore()
        self.ctx.stroke()

    ##################################################
    ### parts
    ##################################################

    def roundedPlate(self, x, y, r, edge="f", callback=None,
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

        overallwidth = x + 2 * self.edges[edge].spacing()
        overallheight = y + 2 * self.edges[edge].spacing()

        if self.move(overallwidth, overallheight, move, before=True):
            return

        lx = x - 2*r
        ly = y - 2*r
        r += self.edges[edge].startwidth()

        self.moveTo(self.edges[edge].margin(),
                    self.edges[edge].margin())
        self.moveTo(r, 0)

        self.cc(callback, 0)
        self.edges[edge](lx / 2.0 , bedBolts=self.getEntry(bedBolts, 0),
                        bedBoltSettings=self.getEntry(bedBoltSettings, 0))
        self.cc(callback, 1)
        self.edges[edge](lx / 2.0, bedBolts=self.getEntry(bedBolts, 1),
                        bedBoltSettings=self.getEntry(bedBoltSettings, 1))
        for i, l in zip(range(3), (ly, lx, ly)):
            self.corner(90, r)
            self.cc(callback, i + 2)
            self.edges[edge](l, bedBolts=self.getEntry(bedBolts, i + 2),
                            bedBoltSettings=self.getEntry(bedBoltSettings, i + 2))
        self.corner(90, r)

        self.ctx.restore()
        self.ctx.save()

        self.moveTo(self.edges[edge].margin(),
                    self.edges[edge].margin())

        if holesMargin is not None:
            self.moveTo(holesMargin, holesMargin)
            if r > holesMargin:
                r -= holesMargin
            else:
                r = 0
            self.hexHolesPlate(x - 2 * holesMargin, y - 2 * holesMargin, r,
                               settings=holesSettings)
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
        c4 = (r + self.burn) * math.pi * 0.5  # circumference of quarter circle
        c4 = c4 / self.edges["X"].settings.stretch

        top = self.edges.get(top, top)
        bottom = self.edges.get(bottom, bottom)
        left = self.edges.get(left, left)
        right = self.edges.get(right, right)

        # XXX assumes startwidth == endwidth
        topwidth = top.startwidth()
        bottomwidth = bottom.startwidth()

        overallwidth = 2 * x + 2 * y - 8 * r + 4 * c4 + \
                       self.edges["d"].spacing() + self.edges["D"].spacing()
        overallheight = h + top.spacing() + bottom.spacing()

        if self.move(overallwidth, overallheight, move, before=True):
            return

        self.moveTo(left.spacing(), bottom.margin())

        self.cc(callback, 0, y=bottomwidth + self.burn)
        bottom(x / 2.0 - r)
        if (y - 2 * r) < 1E-3:
            self.edges["X"](2 * c4, h + topwidth + bottomwidth)
            self.cc(callback, 2, y=bottomwidth + self.burn)
            bottom(x - 2 * r)
            self.edges["X"](2 * c4, h + topwidth + bottomwidth)
            self.cc(callback, 4, y=bottomwidth + self.burn)
        else:
            for i, l in zip(range(4), (y, x, y, 0)):
                self.edges["X"](c4, h + topwidth + bottomwidth)
                self.cc(callback, i + 1, y=bottomwidth + self.burn)
                if i < 3:
                    bottom(l - 2 * r)
        bottom(x / 2.0 - r)

        self.edgeCorner(bottom, right, 90)
        right(h)
        self.edgeCorner(right, top, 90)

        top(x / 2.0 - r)
        for i, l in zip(range(4), (y, x, y, 0)):
            self.edge(c4)
            if i < 3:
                top(l - 2 * r)
        top(x / 2.0 - r)

        self.edgeCorner(top, left, 90)
        left(h)
        self.edgeCorner(left, bottom, 90)

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
        edges += edges  # append for wrapping around
        overallwidth = x + edges[-1].spacing() + edges[1].spacing()
        overallheight = y + edges[0].spacing() + edges[2].spacing()

        if self.move(overallwidth, overallheight, move, before=True):
            return

        self.moveTo(edges[-1].spacing(), edges[0].margin())
        for i, l in enumerate((x, y, x, y)):
            self.cc(callback, i, y=edges[i].startwidth() + self.burn)
            edges[i](l,
                     bedBolts=self.getEntry(bedBolts, i),
                     bedBoltSettings=self.getEntry(bedBoltSettings, i))
            self.edgeCorner(edges[i], edges[i + 1], 90)

        if holesMargin is not None:
            self.moveTo(holesMargin + edges[-1].endwidth(),
                        holesMargin + edges[0].startwidth())
            self.hexHolesRectangle(x - 2 * holesMargin, y - 2 * holesMargin)

        self.ctx.stroke()

        self.move(overallwidth, overallheight, move)

    def rectangularTriangle(self, x, y, edges="eee", num=1,
                        bedBolts=None, bedBoltSettings=None,
                        callback=None,
                        move=None):
        """
        Rectangular triangular wall

        :param x: width
        :param y: height
        :param edges:  (Default value = "eee") bottom, right[, diagonal]
        :param num: (Default value = 1) number of triangles
        :param bedBolts:  (Default value = None)
        :param bedBoltSettings:  (Default value = None)
        :param callback:  (Default value = None)
        :param move:  (Default value = None)

        """
        edges = [self.edges.get(e, e) for e in edges]
        if len(edges) == 2:
            edges.append(self.edges["e"])
        if len(edges) != 3:
            raise ValueError("two or three edges required")

        width = x + edges[-1].spacing() + edges[1].spacing()
        height = y + edges[0].spacing() + edges[2].spacing()
        if num > 1:
            width += edges[-1].spacing() + edges[1].spacing() + 2*self.spacing
            height += edges[0].spacing() + edges[2].spacing() + self.spacing

        overallwidth = width * (num // 2 + num % 2)
        overallheight = height

        alpha = math.degrees(math.atan(y/float(x)))

        if self.move(overallwidth, overallheight, move, before=True):
            return

        if num > 1:
            self.moveTo(self.spacing + edges[-1].spacing())

        for n in range(num):
            self.moveTo(edges[-1].spacing()+self.spacing, edges[0].margin())
            if n % 2 == 1:
                self.moveTo(2*edges[1].spacing()+self.spacing, 0)
            if num > 1:
                self.moveTo(edges[1].spacing(), 0)
            for i, l in enumerate((x, y)):
                self.cc(callback, i, y=edges[i].startwidth() + self.burn)
                edges[i](l,
                         bedBolts=self.getEntry(bedBolts, i),
                         bedBoltSettings=self.getEntry(bedBoltSettings, i))
                self.edgeCorner(edges[i], edges[i + 1], 90)

            self.corner(alpha)
            self.cc(callback, 2)
            edges[2]((x**2+y**2)**0.5)
            self.corner(180-alpha)
            self.ctx.stroke()

            if n % 2:
                self.moveTo(-edges[1].spacing()-2*self.spacing-edges[-1].spacing(), height-edges[1].spacing(), 180)
            else:
                self.moveTo(width+1*edges[1].spacing()-self.spacing-2*edges[-1].spacing(), height-edges[1].spacing(), 180)


        self.move(overallwidth, overallheight, move)

    ##################################################
    ### Place Parts
    ##################################################

    def partsMatrix(self, n, width, move, part, *l, **kw):

        rows = n//width + (1 if n % width else 0)

        if not move:
            move = ""
        move = move.split()

        #move down / left before
        for m in move:
            if m == "left":
                kw["move"] = "left only"
                for i in range(width):
                    part(*l, **kw)
            if m == "down":
                kw["move"] = "down only"
                for i in range(rows):
                    part(*l, **kw)
        # draw matrix
        for i in range(rows):
            self.ctx.save()
            for j in range(width):
                if width*i+j >= n:
                    break
                kw["move"] = "right"
                part(*l, **kw)
            self.ctx.restore()
            kw["move"] = "up only"
            part(*l, **kw)

        # Move back down
        if "up" not in move:
            kw["move"] = "down only"
            for i in range(rows):
                part(*l, **kw)

        # Move right
        if "right" in move:
            kw["move"] = "right only"
            for i in range(n):
                part(*l, **kw)
