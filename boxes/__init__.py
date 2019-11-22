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
import sys
import argparse
from argparse import ArgumentParser
import re
from functools import wraps
from xml.sax.saxutils import quoteattr
from contextlib import contextmanager
import copy

try:  # py3
    from shlex import quote
except ImportError:  # py2
    from pipes import quote

from boxes import edges
from boxes import formats
from boxes import svgutil
from boxes import gears
from boxes import pulley
from boxes import parts
from boxes.Color  import *

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
        with self.saved_context():
            pt = self.ctx.get_current_point()
            func(self, *args, **kw)
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
        with self.saved_context():
            self.set_source_color(Color.BLUE)
            func(self, *args, **kw)
            self.ctx.stroke()

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

    def __getattr__(self, name):
        return getattr(self.boxes, name)

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

    result = []

    s = re.split(r"\s|:", s)

    try:
        for part in s:
            m = re.match(r"^(\d+(\.\d+)?)/(\d+)$", part)
            if m:
                n = int(m.group(3))
                result.extend([float(m.group(1)) / n] * n)
                continue
            m = re.match(r"^(\d+(\.\d+)?)\*(\d+)$", part)
            if m:
                n = int(m.group(3))
                result.extend([float(m.group(1))] * n)
                continue
            result.append(float(part))
    except ValueError:
        raise argparse.ArgumentTypeError("Don't understand sections string")

    if not result:
        result.append(0.0)

    return result

class ArgparseEdgeType:
    """argparse type to select from a set of edge types"""

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

    def inx(self, name, viewname, arg):
        return ('      <param name="%s" type="enum" gui-text="%s" gui-description=%s>\n' %
                (name, viewname, quoteattr(arg.help or "")) +
                ''.join(('        <item value="%s">%s %s</item>\n' % (
                    e, e, self.names.get(e, ""))
                         for e in self.edges)) +
                '      </param>\n')

class BoolArg:
    def __call__(self, arg):
        if not arg or arg.lower() in ("none", "0", "off", "false"):
            return False
        return True

    def html(self, name, default):
        if isinstance(default, (str)):
            default = self(default)
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
    ui_group = "Misc"

    description = "" # Markdown syntax is supported

    def __init__(self):
        self.formats = formats.Formats()
        self.ctx = None
        description = self.__doc__
        if self.description:
            description += "\n\n" + self.description
        self.argparser = ArgumentParser(description=description)
        self.edgesettings = {}
        self.inkscapefile = None

        self.metadata = {
            "name" : self.__class__.__name__,
            "description" : self.description,
            "group" : self.ui_group,
            "url" : "",
            "command_line" : ""
        }

        self.argparser._action_groups[1].title = self.__class__.__name__ + " Settings"
        defaultgroup = self.argparser.add_argument_group(
                        "Default Settings")
        defaultgroup.add_argument(
            "--thickness", action="store", type=float, default=3.0,
            help="thickness of the material")
        defaultgroup.add_argument(
            "--output", action="store", type=str, default="box.svg",
            help="name of resulting file")
        defaultgroup.add_argument(
            "--format", action="store", type=str, default="svg",
            choices=self.formats.getFormats(),
            help="format of resulting file")
        defaultgroup.add_argument(
            "--tabs", action="store", type=float, default=0.0,
            help="width of tabs holding the parts in place in mm (not supported everywhere)")
        defaultgroup.add_argument(
            "--debug", action="store", type=boolarg, default=False,
            help="print surrounding boxes for some structures")
        defaultgroup.add_argument(
            "--reference", action="store", type=float, default=100,
            help="print reference rectangle with given length (zero to disable)")
        defaultgroup.add_argument(
            "--burn", action="store", type=float, default=0.1,
            help='burn correction in mm (bigger values for tighter fit). Use BurnTest in "Parts and Samples" to find the right value.')

    @contextmanager
    def saved_context(self):
        """
        Generator: for saving and restoring cairo contexts.
        :param cr: cairo context
        """
        cr = self.ctx
        cr.save()
        try:
            yield cr
        finally:
            cr.restore()

    def set_source_color(self, color):
        """
        Sets the color of the pen.
        """
        self.ctx.set_source_rgb(*color)

    def open(self):
        """
        Prepare for rendering

        Create canvas and edge and other objects
        Call this before .render()
        """
        if self.ctx is not None:
            return

        self.bedBoltSettings = (3, 5.5, 2, 20, 15)  # d, d_nut, h_nut, l, l1
        self.hexHolesSettings = (5, 3, 'circle')  # r, dist, style
        self.surface, self.ctx = self.formats.getSurface(self.format, self.output)

        if self.format == 'svg_Ponoko':
            self.ctx.set_line_width(0.01)
            self.set_source_color(Color.BLUE)
        else:
            self.ctx.set_line_width(max(2 * self.burn, 0.05))
            self.set_source_color(Color.BLACK)

        self.spacing = 2 * self.burn + 0.5 * self.thickness
        self.ctx.select_font_face("sans-serif")
        self._buildObjects()
        if self.reference and self.format != 'svg_Ponoko':
            self.move(10, 10, "up", before=True)
            self.ctx.rectangle(0, 0, self.reference, 10)
            if self.reference < 40:
                self.text("%.fmm" % self.reference, self.reference + 5, 5,
                          align="middle left")
            else:
                self.text("%.fmm" % self.reference, self.reference / 2.0, 5,
                          align="middle center")
            self.move(10, 10, "up")
            self.ctx.stroke()

    def buildArgParser(self, *l, **kw):
        """
        Add commonly used arguments

        :param \*l: parameter names
        :param \*\*kw: parameters with new default values

        Supported parameters are

        * floats: x, y, h, hi
        * argparseSections: sx, sy, sh
        * ArgparseEdgeType: bottom_edge, top_edge
        * boolarg: outside
        * str (selection): nema_mount
        """
        for arg in l:
            kw[arg] = None
        for arg, default in kw.items():
            if arg == "x":
                if default is None: default = 100.0
                self.argparser.add_argument(
                    "--x", action="store", type=float, default=default,
                    help="inner width in mm (unless outside selected)")
            elif arg == "y":
                if default is None: default = 100.0
                self.argparser.add_argument(
                    "--y", action="store", type=float, default=default,
                    help="inner depth in mm (unless outside selected)")
            elif arg == "sx":
                if default is None: default = "50*3"
                self.argparser.add_argument(
                    "--sx", action="store", type=argparseSections,
                    default=default,
                    help="""sections left to right in mm. See --sy for format""")
            elif arg == "sy":
                if default is None: default = "50*3"
                self.argparser.add_argument(
                    "--sy", action="store", type=argparseSections,
                    default=default,
                    help="""sections back to front in mm. Possible formats: overallwidth/numberof sections e.g. "250/5"; sectionwidth*numberofsections e.g. "50*5"; section widths separated by ":" e.g. "30:25.5:70""")
            elif arg == "sh":
                if default is None: default = "50*3"
                self.argparser.add_argument(
                    "--sh", action="store", type=argparseSections,
                    default=default,
                    help="""sections bottom to top in mm. See --sy for format""")
            elif arg == "h":
                if default is None: default = 100.0
                self.argparser.add_argument(
                    "--h", action="store", type=float, default=default,
                    help="inner height in mm (unless outside selected)")
            elif arg == "hi":
                if default is None: default = 0.0
                self.argparser.add_argument(
                    "--hi", action="store", type=float, default=default,
                    help="inner height of inner walls in mm (unless outside selected)(leave to zero for same as outer walls)")
            elif arg == "bottom_edge":
                if default is None: default = "h"
                self.argparser.add_argument(
                    "--bottom_edge", action="store",
                    type=ArgparseEdgeType("Fhse"), choices=list("Fhse"),
                    default=default,
                    help="edge type for bottom edge")
            elif arg == "top_edge":
                if default is None: default = "e"
                self.argparser.add_argument(
                    "--top_edge", action="store",
                    type=ArgparseEdgeType("efFcESikvfLt"), choices=list("efFcESikvfLt"),
                    default=default, help="edge type for top edge")
            elif arg == "outside":
                if default is None: default = True
                self.argparser.add_argument(
                    "--outside", action="store", type=boolarg, default=default,
                    help="treat sizes as outside measurements that include the walls")
            elif arg == "nema_mount":
                if default is None: default = 23
                self.argparser.add_argument(
                    "--nema_mount", action="store",
                    type=int, choices=list(sorted(self.nema_sizes.keys())),
                    default=default, help="NEMA size of motor")
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
        if args is None:
            args = sys.argv[1:]
        if len(args) > 1 and args[-1][0] != "-":
            self.inkscapefile = args[-1]
            del args[-1]
        args = [a for a in args if not a.startswith('--tab=')]
        self.metadata["cli"] = "boxes " + self.__class__.__name__ + " " + " ".join((quote(arg) for arg in args))
        for key, value in vars(self.argparser.parse_args(args=args)).items():
            # treat edge settings separately 
            for setting in self.edgesettings:
                if key.startswith(setting + '_'):
                    self.edgesettings[setting][key[len(setting)+1:]] = value
                    continue
            setattr(self, key, value)

        # Change file ending to format if not given explicitly
        format = getattr(self, "format", "svg")
        if getattr(self, 'output', None) == 'box.svg':
            self.output = 'box.' + format.split("_")[0]

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
        edges.ChestHingeSettings(self.thickness, True,
                **self.edgesettings.get("ChestHinge", {})).edgeObjects(self)
        edges.CabinetHingeSettings(self.thickness, True,
                **self.edgesettings.get("CabinetHinge", {})).edgeObjects(self)
        # Sliding Lid
        edges.LidSettings(self.thickness, True,
                **self.edgesettings.get("Lid", {})).edgeObjects(self)
        # Rounded Triangle Edge
        edges.RoundedTriangleEdgeSettings(self.thickness, True,
                **self.edgesettings.get("RoundedTriangleEdge", {})).edgeObjects(self)

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
        # Char to edge object
        e1 = self.edges.get(e1, e1)
        e2 = self.edges.get(e2, e2)

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
            walls += e2.startwidth() + e2.margin()
        elif e2:
            walls += self.thickness

        try:
            if total > 0.0:
                factor = (total - walls) / total
            else:
                factor = 1.0
            return [s * factor for s in l]
        except TypeError:
            return l - walls

    def render(self):
        """Implement this method in your sub class.

        You will typically need to call .parseArgs() before calling this one"""
        self.open()
        # Change settings and creat new Edges and part classes here
        raise NotImplementedError
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
            with self.saved_context():
                self.moveTo(x, y)
                if number is None:
                    callback()
                else:
                    callback(number)
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

        Flush canvas to disk and convert output to requested format if needed.
        Call after .render()"""
        if self.ctx == None:
            return

        self.ctx.stroke()
        self.ctx = None
        self.surface.flush()
        self.surface.finish()

        self.formats.convert(self.output, self.format, self.metadata)
        if self.inkscapefile:
            try:
                out = sys.stdout.buffer
            except AttributeError:
                out= sys.stdout
            svgutil.svgMerge(self.output, self.inkscapefile, out)

    ############################################################
    ### Turtle graphics commands
    ############################################################

    def corner(self, degrees, radius=0, tabs=0):
        """
        Draw a corner

        This is what does the burn corrections

        :param degrees: angle
        :param radius:  (Default value = 0)

        """

        try:
            degrees, radius = degrees
        except:
            pass

        rad = degrees * math.pi / 180

        if tabs and self.tabs:
            if degrees > 0:
                r_ = radius + self.burn
                tabrad = self.tabs / r_
            else:
                r_ = radius - self.burn
                tabrad = -self.tabs / r_

            length = abs(r_ * rad)
            tabs = min(tabs, int(length // (tabs*3*self.tabs)))
        if tabs and self.tabs:
            l = (length - tabs * self.tabs) / tabs
            lang = math.degrees(l / r_)
            if degrees < 0:
                lang = -lang
            #print(degrees, radius, l, lang, tabs, math.degrees(tabrad))
            self.corner(lang/2., radius)
            for i in range(tabs-1):
                self.moveArc(math.degrees(tabrad), r_)
                self.corner(lang, radius)
            if tabs:
                self.moveArc(math.degrees(tabrad), r_)
            self.corner(lang/2., radius)
            return

        if radius > 0.5* self.thickness and abs(degrees) > 36:
            steps = int(abs(degrees)/ 36.) + 1
            for i in range(steps):
                self.corner(float(degrees)/steps, radius)
            return

        if degrees > 0:
            self.ctx.arc(0, radius + self.burn, radius + self.burn,
                         -0.5 * math.pi, rad - 0.5 * math.pi)
        elif radius > self.burn:
            self.ctx.arc_negative(0, -(radius - self.burn), radius - self.burn,
                                  0.5 * math.pi, rad + 0.5 * math.pi)
        else:  # not rounded inner corner
            self.ctx.arc_negative(0, self.burn - radius, self.burn - radius,
                                  -0.5 * math.pi, -0.5 * math.pi + rad)

        self._continueDirection(rad)

    def edge(self, length, tabs=0):
        """
        Simple line
        :param length: length in mm

        """
        self.ctx.move_to(0, 0)
        if tabs and self.tabs:
            if self.tabs > length:
                self.ctx.move_to(length, 0)
            else:
                tabs = min(tabs, max(1, int(length // (tabs*3*self.tabs))))
                l = (length - tabs * self.tabs) / tabs
                self.ctx.line_to(0.5*l, 0)
                for i in range(tabs-1):
                    self.ctx.move_to((i+0.5)*l+self.tabs, 0)
                    self.ctx.line_to((i+0.5)*l+self.tabs+l, 0)
                if tabs == 1:
                    self.ctx.move_to((tabs-0.5)*l+self.tabs, 0)
                else:
                    self.ctx.move_to((tabs-0.5)*l+2*self.tabs, 0)

                self.ctx.line_to(length, 0)
        else:
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
        self._continueDirection(rad)

    def polyline(self, *args):
        """
        Draw multiple connected lines

        :param \*args: Alternating length in mm and angle in degrees.

        lengths may be a tuple (length, #tabs)
        angles may be tuple (angle, radius)
        """
        for i, arg in enumerate(args):
            if i % 2:
                if isinstance(arg, tuple):
                    self.corner(*arg)
                else:
                    self.corner(arg)
            else:
                if isinstance(arg, tuple):
                    self.edge(*arg)
                else:
                    self.edge(arg)

    def bedBoltHole(self, length, bedBoltSettings=None, tabs=0):
        """
        Draw an edge with slot for a bed bolt

        :param length: length of the edge in mm
        :param bedBoltSettings:  (Default value = None) Dimmensions of the slot

        """
        d, d_nut, h_nut, l, l1 = bedBoltSettings or self.bedBoltSettings
        self.edge((length - d) / 2.0, tabs=tabs//2)
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
        self.edge((length - d) / 2.0, tabs=tabs-(tabs//2))

    def edgeCorner(self, edge1, edge2, angle=90):
        """Make a corner between two Edges. Take width of edges into account"""
        edge1 = self.edges.get(edge1, edge1)
        edge2 = self.edges.get(edge2, edge2)

        self.edge(edge2.startwidth() * math.tan(math.radians(angle/2.)))
        self.corner(angle)
        self.edge(edge1.endwidth() * math.tan(math.radians(angle/2.)))

    def regularPolygon(self, corners=3, radius=None, h=None, side=None):
        """Give messures of a regular polygone

        :param corners: number of corners of the polygone
        :param radius: distance center to one of the corners
        :param h: distance center to one of the sides (height of sector)
        :param side: length of one side
        :return: (radius, h, side)
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

        self.move(tw, th, move)

    def grip(self, length, depth):
        """Corrugated edge useful as an gipping area

        :param length: length
        :param depth: depth of the grooves

        """
        grooves = max(int(length // (depth * 2.0)) + 1, 1)
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

        # Hole
        with self.saved_context():
            self.moveTo(d + 2 * r, 0)
            self.edge(hl - 2 * r)
            self.corner(-90, r)
            self.edge(h - 3 * r)
            self.corner(-90, r)
            self.edge(hl - 2 * r)
            self.corner(-90, r)
            self.edge(h - 3 * r)
            self.corner(-90, r)

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

    def moveArc(self, angle, r=0.0):
        """
        :param angle:
        :param r: (Default value = 0.0)
        """
        if r < 0:
            r = -r
            angle = -angle

        rad = math.radians(angle)
        if angle > 0:
            self.moveTo(r*math.sin(rad),
                        r*(1-math.cos(rad)), angle)
        else:
            self.moveTo(r*math.sin(-rad),
                        -r*(1-math.cos(rad)), angle)

    def _continueDirection(self, angle=0):
        """
        Set coordinate system to current position (end point)

        :param angle:  (Default value = 0) heading

        """
        self.ctx.translate(*self.ctx.get_current_point())
        self.ctx.rotate(angle)

    def move(self, x, y, where, before=False):
        """Intended to be used by parts
        where can be combinations of "up" or "down", "left" or "right", "only",
        "mirror"
        when "only" is included the move is only done when before is True
        "mirror" will flip the part along the y axis
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
            "mirror": (0, 0, None),
        }

        if not before:
            self.ctx.stroke()
            # restore position
            self.ctx.restore()

        for term in terms:
            if not term in moves:
                raise ValueError("Unknown direction: '%s'" % term)
            mx, my, movebeforeprint = moves[term]
            if movebeforeprint and before:
                self.moveTo(mx, my)
            elif (not movebeforeprint and not before) or dontdraw:
                self.moveTo(mx, my)
        if not dontdraw:
            if before:
                # save position
                self.ctx.save()
                if self.debug:
                    self.ctx.rectangle(0, 0, x, y)
                if "mirror" in terms:
                    self.moveTo(x, 0)
                    self.ctx.scale(-1, 1)
                self.moveTo(self.spacing / 2.0, self.spacing / 2.0)
        return dontdraw

    @restore
    def circle(self, x, y, r):
        """
        Draw a round disc

        :param x: position
        :param y: postion
        :param r: radius

        """
        r += self.burn
        self.moveTo(x + r, y)
        a = 0
        n = 10
        da = 2 * math.pi / n
        for i in range(n):
            self.ctx.arc(-r, 0, r, a, a+da)
            a += da
        self.ctx.stroke()

    @restore
    @holeCol
    def hole(self, x, y, r=0.0, d=0.0, tabs=0):
        """
        Draw a round hole

        :param x: position
        :param y: postion
        :param r: radius

        """

        if not r:
            r = d / 2.0
        if r < self.burn:
            r = self.burn + 1E-9
        r_ = r - self.burn
        self.moveTo(x + r_, y, -90)
        self.corner(-360, r, tabs)

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
        r = min(r, dx/2., dy/2.)
        self.moveTo(x + r - dx / 2.0, y - dy / 2.0 + self.burn, 180)
        for d in (dy, dx, dy, dx):
            self.corner(-90, r)
            self.edge(d - 2 * r)

    @restore
    @holeCol
    def dHole(self, x, y, r=None, d=None, w=None, rel_w=0.75, angle=0):
        if r is None:
            r = d / 2.0
        if w is None:
            w = 2.0 * r * rel_w
        w -= r
        if r < 0.0:
            return
        if abs(w) > r:
            return self.hole(x, y, r)

        a = math.degrees(math.acos(w / r))
        self.moveTo(x, y, angle-a)
        self.moveTo(r-self.burn, 0, -90)
        self.corner(-360+2*a, r)
        self.corner(-a)
        self.edge(2*r*math.sin(math.radians(a)))

    @restore
    @holeCol
    def flatHole(self, x, y, r=None, d=None, w=None, rel_w=0.75, angle=0):
        if r is None:
            r = d / 2.0
        if w is None:
            w = r * rel_w
        else:
            w = w / 2.0

        if r < 0.0:
            return
        if abs(w) > r:
            return self.hole(x, y, r)

        a = math.degrees(math.acos(w / r))
        self.moveTo(x, y, angle-a)
        self.moveTo(r-self.burn, 0, -90)
        for i in range(2):
            self.corner(-180+2*a, r)
            self.corner(-a)
            self.edge(2*r*math.sin(math.radians(a)))
            self.corner(-a)

    @restore
    def text(self, text, x=0, y=0, angle=0, align="", fontsize=10, color=[0.0, 0.0, 0.0]):
        """
        Draw text

        :param text: text to render
        :param x:  (Default value = 0)
        :param y:  (Default value = 0)
        :param angle:  (Default value = 0)
        :param align:  (Default value = "") string with combinations of (top|middle|bottom) and (left|center|right) separated by a space

        """
        self.ctx.set_font_size(fontsize)
        self.moveTo(x, y, angle)
        text = text.split("\n")
        width = lheight = 0.0
        for line in text:
            (tx, ty, w, h, dx, dy) = self.ctx.text_extents(line)
            lheight = max(lheight, h)
            width = max(width, w)

        lines = len(text)
        height = lines * lheight + (lines - 1) * 0.4 * lheight
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

        self.ctx.stroke()
        self.set_source_color(Color.WHITE)
        self.ctx.rectangle(0, 0, width, height)
        self.ctx.stroke()
        self.set_source_color(color)
        self.ctx.scale(1, -1)
        for line in reversed(text):
            self.ctx.show_text(line)
            self.moveTo(0, 1.4 * -lheight)
        self.set_source_color(Color.BLACK)
        self.ctx.set_font_size(10)

    tx_sizes = {
        1 : 0.61,
        2 : 0.70,
        3 : 0.82,
        4 : 0.96,
        5 : 1.06,
        6 : 1.27,
        7 : 1.49,
        8 : 1.75,
        9 : 1.87,
        10 : 2.05,
        15 : 2.40,
        20 : 2.85,
        25 : 3.25,
        30 : 4.05,
        40 : 4.85,
        45 : 5.64,
        50 : 6.45,
        55 : 8.05,
        60 : 9.60,
        70 : 11.20,
        80 : 12.80,
        90 : 14.40,
        100 : 16.00,
        }

    @restore
    @holeCol
    def TX(self, size, x=0, y=0, angle=0):
        """Draw a star pattern

        :param size: 1 to 100
        :param x: (Default value = 0)
        :param y: (Default value = 0)
        :param angle: (Default value = 0)
        """
        self.moveTo(x, y, angle)

        size = self.tx_sizes.get(size, 0)
        ri = 0.5 * size * math.tan(math.radians(30))
        ro = ri * (2**0.5-1)

        self.moveTo(size * 0.5 - self.burn, 0, -90)
        for i in range(6):
            self.corner(45, ri)
            self.corner(-150, ro)
            self.corner(45, ri)

    nema_sizes = {
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

    @restore
    def NEMA(self, size, x=0, y=0, angle=0):
        """Draw holes for mounting a NEMA stepper motor

        :param size: Nominal size in tenths of inches
        :param x:  (Default value = 0)
        :param y:  (Default value = 0)
        :param angle:  (Default value = 0)

        """
        width, flange, holedistance, diameter = self.nema_sizes[size]
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
        """
        Fill a rectangle with a pattern allowing bending in both axis

        :param x: width
        :param y: height
        :param width: width between the lines of the pattern in multiples of thickness
        """
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
                    with self.saved_context():
                        self.moveTo((5 * i) * wx, (5 * j) * wy)
                        self.polyline(*armx)
                    with self.saved_context():
                        self.moveTo((5 * i + 5) * wx, (5 * j + 5) * wy, -180)
                        self.polyline(*armx)
                else:
                    with self.saved_context():
                        self.moveTo((5 * i + 5) * wx, (5 * j) * wy, 90)
                        self.polyline(*army)
                    with self.saved_context():
                        self.moveTo((5 * i) * wx, (5 * j + 5) * wy, -90)
                        self.polyline(*army)
        self.ctx.stroke()

    ##################################################
    ### parts
    ##################################################

    def _splitWall(self, pieces, side):
        """helper for roundedPlate and surroundingWall
        figures out what sides to split
        """
        return [
            (False, False, False, False, True),
            (True, False, False, False, True),
            (True, False, True, False, True),
            (True, True, True, False, True),
            (True, True, True, True, True),
        ][pieces][side]

    def roundedPlate(self, x, y, r, edge="f", callback=None,
                     holesMargin=None, holesSettings=None,
                     bedBolts=None, bedBoltSettings=None,
                     wallpieces=1,
                     move=None):
        """Plate with rounded corner fitting to .surroundingWall()

        For the callbacks the sides are counted depending on wallpieces

        :param x: width
        :param y: hight
        :param r: radius of the corners
        :param callback:  (Default value = None)
        :param holesMargin:  (Default value = None) set to get hex holes
        :param holesSettings:  (Default value = None)
        :param bedBolts:  (Default value = None)
        :param bedBoltSettings:  (Default value = None)
        :param wallpieces: (Default value = 1) # of separate surrounding walls
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

        if wallpieces > 4:
            wallpieces = 4

        wallcount = 0
        for nr, l in enumerate((lx, ly, lx, ly)):
            if self._splitWall(wallpieces, nr):
                for i in range(2):
                    self.cc(callback, wallcount)
                    self.edges[edge](l / 2.0 ,
                        bedBolts=self.getEntry(bedBolts, wallcount),
                        bedBoltSettings=self.getEntry(bedBoltSettings, wallcount))
                    wallcount += 1
            else:
                self.cc(callback, wallcount)
                self.edges[edge](l,
                    bedBolts=self.getEntry(bedBolts, wallcount),
                    bedBoltSettings=self.getEntry(bedBoltSettings, wallcount))
                wallcount += 1
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

        self.move(overallwidth, overallheight, move)

    def surroundingWall(self, x, y, r, h,
                        bottom='e', top='e',
                        left="D", right="d",
                        pieces=1,
                        callback=None,
                        move=None):
        """
        Wall(s) with flex fiting around a roundedPlate()

        For the callbacks the sides are counted depending on pieces

        :param x: width of matching roundedPlate
        :param y: height of matching roundedPlate
        :param r: corner radius of matching roundedPlate
        :param h: inner height of the wall (without edges) 
        :param bottom:  (Default value = 'e') Edge type
        :param top:  (Default value = 'e') Edge type
        :param left: (Default value = 'D') left edge(s)
        :param right: (Default value = 'd') right edge(s)
        :param pieces: (Default value = 1) number of separate pieces
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

        overallwidth = 2*x + 2*y - 8*r + 4*c4 + (self.edges["d"].spacing() + self.edges["D"].spacing() + self.spacing) * pieces
        overallheight = h + top.spacing() + bottom.spacing()

        if self.move(overallwidth, overallheight, move, before=True):
            return

        self.moveTo(left.spacing(), bottom.margin())

        wallcount = 0
        tops = [] # edges needed on the top for this wall segment

        if pieces<=2 and (y - 2 * r) < 1E-3:
            # remove zero length y sides
            c4 *= 2
            sides = (x/2-r, x - 2*r, x - 2*r)
            if pieces > 0: # hack to get the right splits
                pieces += 1
        else:
            sides = (x/2-r, y - 2*r, x - 2*r, y - 2*r, x - 2*r)

        for nr, l in enumerate(sides):
            if self._splitWall(pieces, nr) and nr > 0:
                self.cc(callback, wallcount, y=bottomwidth + self.burn)
                wallcount += 1
                bottom(l / 2.)
                tops.append(l / 2.)

                # complete wall segment
                with self.saved_context():
                    self.edgeCorner(bottom, right, 90)
                    right(h)
                    self.edgeCorner(right, top, 90)
                    for n, d in enumerate(reversed(tops)):
                        if n % 2: # flex
                            self.edge(d)
                        else:
                            top(d)
                    self.edgeCorner(top, left, 90)
                    left(h)
                    self.edgeCorner(left, bottom, 90)

                if nr == len(sides) - 1:
                    break
                # start new wall segment
                tops = []
                self.moveTo(right.margin() + left.margin() + self.spacing)
                self.cc(callback, wallcount, y=bottomwidth + self.burn)
                wallcount += 1
                bottom(l / 2.)
                tops.append(l / 2.)
            else:
                self.cc(callback, wallcount, y=bottomwidth + self.burn)
                wallcount += 1
                bottom(l)
                tops.append(l)
            self.edges["X"](c4, h + topwidth + bottomwidth)
            tops.append(c4)

        self.move(overallwidth, overallheight, move)

    def rectangularWall(self, x, y, edges="eeee",
                        ignore_widths=[],
                        holesMargin=None, holesSettings=None,
                        bedBolts=None, bedBoltSettings=None,
                        callback=None,
                        move=None):
        """
        Rectangular wall for all kind of box like objects

        :param x: width
        :param y: height
        :param edges:  (Default value = "eeee") bottom, right, top, left
        :param ignore_widths: list of edge_widths added to adjacent edge
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

        if 7 not in ignore_widths:
            self.moveTo(edges[-1].spacing())
        if 6 not in ignore_widths:
            self.moveTo(0, edges[0].margin())
        for i, l in enumerate((x, y, x, y)):
            self.cc(callback, i, y=edges[i].startwidth() + self.burn)
            e1, e2 = edges[i], edges[i + 1]
            if (2*i-1 in ignore_widths or
                2*i-1+8 in ignore_widths):
                l += edges[i-1].endwidth()
            if 2*i in ignore_widths:
                l += edges[i+1].startwidth()
                e2 = self.edges["e"]
            if 2*i+1in ignore_widths:
                e1 = self.edges["e"]

            edges[i](l,
                     bedBolts=self.getEntry(bedBolts, i),
                     bedBoltSettings=self.getEntry(bedBoltSettings, i))
            self.edgeCorner(e1, e2, 90)

        if holesMargin is not None:
            self.moveTo(holesMargin,
                        holesMargin + edges[0].startwidth())
            self.hexHolesRectangle(x - 2 * holesMargin, y - 2 * holesMargin, settings=holesSettings)

        self.move(overallwidth, overallheight, move)

    def flangedWall(self, x, y, edges="FFFF", flanges=None, r=0.0,
               callback=None, move=None):
        """Rectangular wall with flanges extending the regular size

        This is similar to the rectangularWall but it may extend to either side
        replacing the F edge with fingerHoles. Use with E and F for edges only.

        :param x: width
        :param y: height
        :param edges:  (Default value = "FFFF") bottom, right, top, left
        :param flanges: (Default value = None) list of width of the flanges
        :param r: radius of the corners of the flange
        :param callback:  (Default value = None)
        :param move:  (Default value = None)
        """

        t = self.thickness

        if not flanges:
            flanges = [0.0] * 4

        while len(flanges) < 4:
            flanges.append(0.0)

        flanges = flanges + flanges # double to allow looping around

        tw = x + 2*t + flanges[1] + flanges[3]
        th = y + 2*t + flanges[0] + flanges[2]

        if self.move(tw, th, move, True):
            return

        rl = min(r, max(flanges[-1], flanges[0]))
        self.moveTo(rl)

        for i in range(4):
            l = y if i % 2 else x

            rl = min(r, max(flanges[i-1], flanges[i]))
            rr = min(r, max(flanges[i], flanges[i+1]))
            self.cc(callback, i, x=-rl)
            if flanges[i]:
                if edges[i] == "F":
                    self.fingerHolesAt(flanges[i-1]+t-rl, 0.5*t+flanges[i], l,
                                       angle=0)
                self.edge(l+flanges[i-1]+flanges[i+1]+2*t-rl-rr)
            else:
                self.edge(flanges[i-1]+t-rl)
                self.edges.get(edges[i], edges[i])(l)
                self.edge(flanges[i+1]+t-rr)
            self.corner(90, rr)
        self.move(tw, th, move)

    def rectangularTriangle(self, x, y, edges="eee", r=0.0, num=1,
                        bedBolts=None, bedBoltSettings=None,
                        callback=None,
                        move=None):
        """
        Rectangular triangular wall

        :param x: width
        :param y: height
        :param edges:  (Default value = "eee") bottom, right[, diagonal]
        :param r: radius towards the hypothenuse
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

        r = min(r, x, y)

        width = x + edges[-1].spacing() + edges[1].spacing()
        height = y + edges[0].spacing() + edges[2].spacing()
        if num > 1:
            width += edges[-1].spacing() + edges[1].spacing() + 2*self.spacing
            height += 0.7*r + edges[0].spacing() + edges[2].spacing() + self.spacing

        overallwidth = width * (num // 2 + num % 2)
        overallheight = height

        alpha = math.degrees(math.atan((y-r)/float(x-r)))

        if self.move(overallwidth, overallheight, move, before=True):
            return

        if self.debug:
            self.rectangularHole(width/2., height/2., width, height)

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

            self.corner(alpha, r)
            self.cc(callback, 2)
            edges[2](((x-r)**2+(y-r)**2)**0.5)
            self.corner(90-alpha, r)
            self.corner(90)
            self.ctx.stroke()

            if n % 2:
                self.moveTo(-edges[1].spacing()-2*self.spacing-edges[-1].spacing(), height-edges[0].spacing(), 180)
            else:
                self.moveTo(width+1*edges[1].spacing()-self.spacing-2*edges[-1].spacing(), height-edges[0].spacing(), 180)


        self.move(overallwidth, overallheight, move)

    def trapezoidWall(self, w, h0, h1, edges="eeee",
                           callback=None, move=None):
        """
        Rectangular trapezoidal wall

        :param w: width
        :param h0: left height
        :param h1: right height
        :param edges:  (Default value = "eee") bottom, right, left
        :param callback:  (Default value = None)
        :param move:  (Default value = None)

        """

        edges = [self.edges.get(e, e) for e in edges]

        overallwidth = w + edges[-1].spacing() + edges[1].spacing()
        overallheight = max(h0, h1) + edges[0].spacing()

        if self.move(overallwidth, overallheight, move, before=True):
            return

        a = math.degrees(math.atan((h1-h0)/w))
        l = ((h0-h1)**2+w**2)**0.5

        self.moveTo(edges[-1].spacing(), edges[0].margin())
        self.cc(callback, 0, y=edges[0].startwidth())
        edges[0](w)
        self.edgeCorner(edges[0], edges[1], 90)
        self.cc(callback, 1, y=edges[1].startwidth())
        edges[1](h1)
        self.edgeCorner(edges[1], self.edges["e"], 90)
        self.corner(a)
        self.cc(callback, 2)
        edges[2](l)
        self.corner(-a)
        self.edgeCorner(self.edges["e"], edges[-1], 90)
        self.cc(callback, 3, y=edges[-1].startwidth())
        edges[3](h0)
        self.edgeCorner(edges[-1], edges[0], 90)

        self.move(overallwidth, overallheight, move)

    def trapezoidSideWall(self, w, h0, h1, edges="eeee",
                          radius=0.0, callback=None, move=None):
        """
        Rectangular trapezoidal wall

        :param w: width
        :param h0: left height
        :param h1: right height
        :param edges:  (Default value = "eeee") bottom, right, left
        :param radius: (Default vaule = 0.0) radius of upper corners
        :param callback:  (Default value = None)
        :param move:  (Default value = None)

        """

        edges = [self.edges.get(e, e) for e in edges]

        overallwidth = w + edges[-1].spacing() + edges[1].spacing()
        overallheight = max(h0, h1) + edges[0].spacing()

        if self.move(overallwidth, overallheight, move, before=True):
            return

        r = min(radius, abs(h0-h1))
        ws = w-r
        if h0 > h1:
            ws += edges[1].endwidth()
        else:
            ws += edges[3].startwidth()
        hs = abs(h1-h0) - r
        a = math.degrees(math.atan(hs/ws))
        l = (ws**2+hs**2)**0.5

        self.moveTo(edges[-1].spacing(), edges[0].margin())
        self.cc(callback, 0, y=edges[0].startwidth())
        edges[0](w)
        self.edgeCorner(edges[0], edges[1], 90)
        self.cc(callback, 1, y=edges[1].startwidth())
        edges[1](h1)

        if h0 > h1:
            self.polyline(0, (90-a, r))
            self.cc(callback, 2)
            edges[2](l)
            self.polyline(0, (a, r), edges[3].startwidth(), 90)
        else:
            self.polyline(0, 90, edges[1].endwidth(), (a, r))
            self.cc(callback, 2)
            edges[2](l)
            self.polyline(0, (90-a, r))
        self.cc(callback, 3, y=edges[-1].startwidth())
        edges[3](h0)
        self.edgeCorner(edges[-1], edges[0], 90)

        self.move(overallwidth, overallheight, move)

    ### polygonWall and friends

    def _polygonWallExtend(self, borders, edge, close=False):
        posx, posy = 0, 0
        ext = [ 0.0 ] * 4
        angle = 0

        def checkpoint(ext, x, y):
            ext[0] = min(ext[0], x)
            ext[1] = min(ext[1], y)
            ext[2] = max(ext[2], x)
            ext[3] = max(ext[3], y)

        for i in range(len(borders)):
            if i % 2:
                try:
                    a, r = borders[i]
                except TypeError:
                    angle = (angle + borders[i]) % 360
                    continue
                if a > 0:
                    centerx = posx + r * math.cos(math.radians(angle+90))
                    centery = posy + r * math.sin(math.radians(angle+90))
                else:
                    centerx = posx + r * math.cos(math.radians(angle-90))
                    centery = posy + r * math.sin(math.radians(angle-90))

                for direction in (0, 90, 180, 270):
                    if (a > 0 and
                        angle <= direction and (angle + a) % 360 >= direction):
                        direction -= 90
                    elif (a < 0 and
                          angle >= direction and (angle + a) % 360 <= direction):
                        direction -= 90
                    else:
                        continue
                    checkpoint(ext, centerx + r * math.cos(math.radians(direction)), centery + r * math.sin(math.radians(direction)))
                    #print("%4s %4s %4s %f %f" % (angle, direction+90, angle+a, centerx + r * math.cos(math.radians(direction)), centery + r * math.sin(math.radians(direction))))
                angle = (angle + a) % 360
                if a > 0:
                    posx = centerx + r * math.cos(math.radians(angle-90))
                    posy = centery + r * math.sin(math.radians(angle-90))
                else:
                    posx = centerx + r * math.cos(math.radians(angle+90))
                    posy = centery + r * math.sin(math.radians(angle+90))
            else:
                posx += borders[i] * math.cos(math.radians(angle))
                posy += borders[i] * math.sin(math.radians(angle))
            checkpoint(ext, posx, posy)

        ext[0] -= edge.margin()
        ext[1] -= edge.margin()
        ext[2] += edge.margin()
        ext[3] += edge.margin()

        return ext

    def polygonWall(self, borders, edge="f", turtle=False,
                    callback=None, move=None):

        e = self.edges.get(edge, edge)
        t = self.thickness # XXX edge.margin()

        minx, miny, maxx, maxy = self._polygonWallExtend(borders, e)

        tw, th = maxx - minx, maxy - miny

        if not turtle:
            if self.move(tw, th, move, True):
                return
        
            self.moveTo(-minx, -miny)

        length_correction = 0.
        for i in range(0, len(borders), 2):
            self.cc(callback, i)
            self.edge(length_correction)
            l = borders[i] - length_correction
            next_angle = borders[i+1]

            if isinstance(next_angle, (int, float)) and next_angle < 0:
                length_correction = t * math.tan(math.radians((-next_angle / 2)))
            else:
                length_correction = 0.0
            l -= length_correction
            e(l)
            self.edge(length_correction)
            self.corner(next_angle, tabs=1)

        if not turtle:
            self.move(tw, th, move)

    @restore
    def polygonWalls(self, borders, h, bottom="F", top="F", symetrical=True):
        bottom = self.edges.get(bottom, bottom)
        top = self.edges.get(top, top)
        t = self.thickness # XXX edge.margin()

        leftsettings = copy.deepcopy(self.edges["f"].settings)
        lf, lF, lh = leftsettings.edgeObjects(self, add=False)
        rightsettings = copy.deepcopy(self.edges["f"].settings)
        rf, rF, rh = rightsettings.edgeObjects(self, add=False)

        length_correction = 0.
        angle = borders[-1]
        i = 0
        part_cnt = 0

        self.moveTo(0, bottom.margin())
        while i < len(borders):
            if symetrical:
                if part_cnt % 2:
                    left, right = lf, rf
                else:
                    left, right = lF, rF
            else:
                left, right = lf, rF

            top_lengths = []
            top_edges = []

            self.moveTo(left.spacing() + self.spacing, 0)
            l = borders[i] - length_correction
            leftsettings.setValues(self.thickness, angle=angle)
            angle = borders[i+1]

            while isinstance(angle, (tuple, list)):
                bottom(l)
                angle, radius = angle
                lr = abs(math.radians(angle) * radius)
                self.edges["X"](lr, h + 2*t) # XXX
                top_lengths.append(l)
                top_lengths.append(lr)
                top_edges.append(top)
                top_edges.append("E")

                i += 2
                l = borders[i]
                angle = borders[i+1]

            rightsettings.setValues(self.thickness, angle=angle)
            if angle < 0:
                length_correction = t * math.tan(math.radians((-angle / 2)))
            else:
                length_correction = 0.0
            l -= length_correction

            bottom(l)

            top_lengths.append(l)
            top_edges.append(top)
            with self.saved_context():
                self.edgeCorner(bottom, right, 90)
                right(h)
                self.edgeCorner(right, top, 90)

                top_edges.reverse()
                top_lengths.reverse()
                edges.CompoundEdge(self, top_edges, top_lengths)(sum(top_lengths))
                self.edgeCorner(top, left, 90)
                left(h)
                self.edgeCorner(left, bottom, 90)

            self.moveTo(right.spacing() + self.spacing)
            part_cnt += 1
            i += 2


    ##################################################
    ### Place Parts
    ##################################################

    def partsMatrix(self, n, width, move, part, *l, **kw):
        """place many of the same part

        :param n: number of parts
        :param width: number of parts in a row
        :param move: (Default value = None)
        :param part: callable that draws a part and knows move param
        :param \*l: params for part
        :param \*\*kw: keyword params for part
        """
        if n <= 0:
            return

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
            with self.saved_context():
                for j in range(width):
                    if "only" in move:
                        break
                    if width*i+j >= n:
                        break
                    kw["move"] = "right"
                    part(*l, **kw)
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
            for i in range(width):
                part(*l, **kw)

    def mirrorX(self, f, offset=0.0):
        """Wrap a function to draw mirrored at the y axis

        :param f: function to wrap
        :param offset: (default value = 0.0) axis to mirror at
        """
        def r():
            self.moveTo(offset, 0)
            with self.saved_context():
                self.ctx.scale(-1, 1)
                f()
        return r

    def mirrorY(self, f, offset=0.0):
        """Wrap a function to draw mirrored at the x axis

        :param f: function to wrap
        :param offset: (default value = 0.0) axis to mirror at
        """
        def r():
            self.moveTo(0, offset)
            with self.saved_context():
                self.ctx.scale(1, -1)
                f()
        return r
