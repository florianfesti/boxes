#!/usr/bin/python

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

class Boxes:

    def __init__(self, width=300, height=200, thickness=3.0, burn=0.1):
        self.thickness = thickness
        self.burn = burn
        self.fingerJointSettings = (10.0, 10.0)
        self.fingerHoleEdgeWidth = 1.0    # multitudes of self.thickness
        self.bedBoltSettings = (3, 5.5, 2, 20, 15) #d, d_nut, h_nut, l, l1
        self.doveTailJointSettings = (10, 5, 50, 0.4) # width, depth, angle, radius
        self.flexSettings = (1.5, 3.0, 15.0) # line distance, connects, width
        self.hexHolesSettings = (5, 3, 'circle') # r, dist, style
        self.output = "box.svg"
        self._init_surface(width, height)

    def _init_surface(self, width, height):
        mm2pt = 90 / 25.4 / 1.25
        width *= mm2pt
        height *= 3.543307
        self.surface = cairo.SVGSurface(self.output, width, height)
        self.ctx = ctx = cairo.Context(self.surface)
        ctx.translate(0, height)
        ctx.scale(mm2pt, -mm2pt)

        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()

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

    def fingerJoint(self, length, positive=True, settings=None,
                    bedBolts=None, bedBoltSettings=None):
        # assumes, we are already moved out by self.burn!
        # negative also assumes we are moved out by self.thinkness!
        space, finger = settings or self.fingerJointSettings
        fingers = int((length-space) // (space+finger))
        if bedBolts:
            fingers = bedBolts.numFingers(fingers)
        leftover = length - fingers*(space+finger) - finger
        s, f, thickness = space, finger, self.thickness
        d, d_nut, h_nut, l, l1 = bedBoltSettings or self.bedBoltSettings
        p = 1 if positive else -1

        self.edge(leftover/2.0)
        for i in xrange(fingers):
            if not positive and bedBolts and bedBolts.drawBolt(i):
                self.hole(0.5*space,
                          0.5*self.thickness, 0.5*d)
            if positive and bedBolts and bedBolts.drawBolt(i):
                self.bedBoltHole(s, bedBoltSettings)
            else:
                self.edge(s)
            self.corner(-90*p)
            self.edge(thickness)
            self.corner(90*p)
            self.edge(f)
            self.corner(90*p)
            self.edge(thickness)
            self.corner(-90*p)
        self.edge(s+leftover/2.0)

    def fingerHoles(self, length, settings=None,
                    bedBolts=None, bedBoltSettings=None):
        s, f = settings or self.fingerJointSettings
        fingers = int((length-s) // (s+f))
        if bedBolts:
            fingers = bedBolts.numFingers(fingers)
            d, d_nut, h_nut, l, l1 = bedBoltSettings or self.bedBoltSettings
        leftover = length - fingers*(s+f) - f
        b = self.burn
        for i in xrange(fingers):
            pos = leftover/2.0+i*(s+f)
            if bedBolts and bedBolts.drawBolt(i):
                self.hole(pos+0.5*s, 0, d*0.5)
            self.ctx.rectangle(pos+s+b, -self.thickness/2+b,
                               f-2*b, self.thickness - 2*b)

        self.ctx.move_to(0, length)
        self.ctx.translate(*self.ctx.get_current_point())

    def fingerHoleEdge(self, length, dist=None, settings=None,
                       bedBolts=None, bedBoltSettings=None):
        if dist is None:
            dist = self.fingerHoleEdgeWidth * self.thickness
        self.ctx.save()
        self.moveTo(0, dist+self.thickness/2)
        self.fingerHoles(length, settings, bedBolts, bedBoltSettings)
        self.ctx.restore()
        # XXX continue path
        self.ctx.move_to(0, 0)
        self.ctx.line_to(length, 0)
        self.ctx.translate(*self.ctx.get_current_point())

    def doveTailJoint(self, length, positive=True, settings=None):
        width, depth, angle, radius = settings or self.doveTailJointSettings
        radius = max(radius, self.burn) # no smaller than burn
        a = angle + 90
        alpha = 0.5*math.pi - math.pi*angle/180.0

        l1 = radius/math.tan(alpha/2.0)
        diffx = 0.5*depth/math.tan(alpha)
        l2 = 0.5*depth / math.sin(alpha)

        sections = int((length) // (width*2))
        leftover = length - sections*width*2

        p = 1 if positive else -1

        self.edge((width+leftover)/2.0+diffx-l1)
        for i in xrange(sections):
            self.corner(-1*p*a, radius)
            self.edge(2*(l2-l1))
            self.corner(p*a, radius)
            self.edge(2*(diffx-l1)+width)
            self.corner(p*a, radius)
            self.edge(2*(l2-l1))
            self.corner(-1*p*a, radius)
            if i<sections-1: # all but the last
                self.edge(2*(diffx-l1)+width)
        self.edge((width+leftover)/2.0+diffx-l1)
        self.ctx.translate(*self.ctx.get_current_point())

    def flex(self, x, h, settings=None, burn=None):
        dist, connection, width = settings or self.flexSettings
        if burn is None:
            burn = self.burn
        h += 2*burn
        lines = int(x // dist)
        leftover = x - lines * dist
        sections = int((h-connection) // width)
        sheight = ((h-connection) / sections)-connection

        for i in xrange(lines):
            pos = i*dist + leftover/2
            if i % 2:
                self.ctx.move_to(pos, 0)
                self.ctx.line_to(pos, connection+sheight)
                for j in range((sections-1)/2):
                    self.ctx.move_to(pos, (2*j+1)* sheight+ (2*j+2)*connection)
                    self.ctx.line_to(pos, (2*j+3)* (sheight+ connection))
                if not sections % 2:
                    self.ctx.move_to(pos, h - sheight- connection)
                    self.ctx.line_to(pos, h)
            else:
                if sections % 2:
                    self.ctx.move_to(pos, h)
                    self.ctx.line_to(pos, h-connection-sheight)
                    for j in range((sections-1)/2):
                         self.ctx.move_to(
                             pos, h-((2*j+1)* sheight+ (2*j+2)*connection))
                         self.ctx.line_to(
                             pos, h-(2*j+3)* (sheight+ connection))

                else:
                    for j in range(sections/2):
                        self.ctx.move_to(pos, 
                                         h-connection-2*j*(sheight+connection))
                        self.ctx.line_to(pos, h-2*(j+1)*(sheight+connection))

        self.ctx.move_to(0, 0)
        self.ctx.line_to(x, 0)
        self.ctx.translate(*self.ctx.get_current_point())

    def grip(self, length, depth):
        """corrugated edge useful as an gipping area"""
        grooves = int(length // (depth*2.0)) + 1
        depth = length / grooves / 4.0
        for groove in xrange(grooves):
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

    def handle(self, x, h, hl, r=20):
        """Creates and Edge with a handle"""
        d = (x-hl-2*r)/2.0
        if d < 0:
            print "Handle too wide"

        self.ctx.save()

        # Hole
        self.moveTo(d+20+r, 0)
        self.edge(hl-2*r)
        self.corner(-90, r)
        self.edge(h-20-2*r)
        self.corner(-90, r)
        self.edge(hl-2*r)
        self.corner(-90, r)
        self.edge(h-20-2*r)
        self.corner(-90, r)

        self.ctx.restore()
        self.moveTo(0,0)

        self.curveTo(d, 0, d, 0, d, -h+r)
        self.curveTo(r, 0, r, 0, r, r)
        self.edge(hl)
        self.curveTo(r, 0, r, 0, r, r)
        self.curveTo(h-r, 0, h-r, 0, h-r, -d)

    ### Navigation

    def moveTo(self, x, y, degrees=0):
        self.ctx.translate(x, y)
        self.ctx.rotate(degrees*math.pi/180.0)
        self.ctx.move_to(0, 0)

    def continueDirection(self, angle=0):
        self.ctx.translate(*self.ctx.get_current_point())
        self.ctx.rotate(angle)

    # Building blocks

    def fingerHolesAt(self, x, y, length, angle=90, burn=None,
                      settings=None, bedBolts=None, bedBoltSettings=None):
        if burn is None:
            burn = self.burn
        # XXX burn with callbacks
        self.ctx.save()
        self.moveTo(x, y+burn, angle)
        self.fingerHoles(length, settings, bedBolts, bedBoltSettings)
        self.ctx.restore()

    @restore
    def hole(self, x, y, r):
        self.moveTo(x+r, y)
        self.ctx.arc(-r, 0, r, 0, 2*math.pi)

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

        for i in xrange(cy//2):
            for j in xrange((cx-(i%2))//2):
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
        print h, leftover
        if grow=='space ':
            b += leftover / (cy-1) / 2

        # recalulate with adjusted values
        w = r+b/2.0
        dist = w * math.cos(math.pi/6.0)

        self.moveTo(h/2.0-(cy//2)*2*w, h/2.0)
        for j in xrange(cy):
            self.hole(2*j*w, 0, r)
        for i in xrange(1, cy/2+1):
            for j in xrange(cy-i):
                self.hole(j*2*w+i*w, i*2*dist, r)
                self.hole(j*2*w+i*w, -i*2*dist, r)

    ##################################################
    ### parts
    ##################################################

    def roundedPlate(self, x, y, r, callback=None,
                     holesMargin=None, holesSettings=None,
                     bedBolts=None, bedBoltSettings=None):
        """fits surroundingWall
        first edge is split to have a joint in the middle of the side
        callback is called at the beginning of the straight edges
        0, 1 for the two part of the first edge, 2, 3, 4 for the others

        set holesMargin to get hex holes.
        """

        self.ctx.save()
        self.moveTo(r, 0)
        self.cc(callback, 0)
        self.fingerJoint(x/2.0-r, bedBolts=self.getEntry(bedBolts, 0),
                         bedBoltSettings=self.getEntry(bedBoltSettings, 0))
        self.cc(callback, 1)
        self.fingerJoint(x/2.0-r, bedBolts=self.getEntry(bedBolts, 1),
                         bedBoltSettings=self.getEntry(bedBoltSettings, 1))
        for i, l in zip(range(3), (y, x, y)):
            self.corner(90, r)
            self.cc(callback, i+2)
            self.fingerJoint(l-2*r, bedBolts=self.getEntry(bedBolts, i+2),
                         bedBoltSettings=self.getEntry(bedBoltSettings, i+2))
        self.corner(90, r)

        self.ctx.restore()
        self.ctx.save()

        if holesMargin is not None:
            self.moveTo(holesMargin, holesMargin)
            if r > holesMargin:
                r -= holesMargin
            else:
                r = 0
            self.hexHolesPlate(x-2*holesMargin, y-2*holesMargin, r,
                               settings=holesSettings)
        self.ctx.restore()

    def _edge(self, l, style,
              bedBolts=None, bedBoltSettings=None):
        if type(style) is tuple:
            style = style[0]
        if callable(style):
            return style(l)
        if style in 'eE':
            self.edge(l)
        elif style == 'h':
            self.fingerHoleEdge(l, bedBolts=bedBolts,
                                bedBoltSettings=bedBoltSettings)
        elif style == 'f':
            self.fingerJoint(l, bedBolts=bedBolts,
                             bedBoltSettings=bedBoltSettings)
        elif style == 'F':
            self.fingerJoint(l, positive=False, bedBolts=bedBolts,
                                bedBoltSettings=bedBoltSettings)
        elif style in 'dD':
            self.doveTailJoint(l, positive=(style=='d'))

    def _edgewidth(self, style):
        """return how far a given edge type needs to be set out"""
        if type(style) is tuple:
            return style[1]
        if style == 'h':
            return (self.fingerHoleEdgeWidth+1) * self.thickness
        elif style in 'FE':
            return self.thickness
        return 0.0

    def surroundingWall(self, x, y, r, h,
                        bottom='e', top='e',
                        callback=None):
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
        topwidth = self._edgewidth(top)
        bottomwidth = self._edgewidth(bottom)

        self.cc(callback, 0, y=bottomwidth+self.burn)
        self._edge(x/2.0-r, bottom)
        for i, l in zip(range(4), (y, x, y, 0)):
            self.flex(c4, h+topwidth+bottomwidth)
            self.cc(callback, i+1, y=bottomwidth+self.burn)
            if i < 3:
                self._edge(l-2*r, bottom)
        self._edge(x/2.0-r, bottom)

        self.corner(90)
        self.edge(bottomwidth)
        self.doveTailJoint(h)
        self.edge(topwidth)
        self.corner(90)

        self._edge(x/2.0-r, top)
        for i, l in zip(range(4), (y, x, y, 0)):
            self.edge(c4)
            if i < 3:
                self._edge(l - 2*r, top)
        self._edge(x/2.0-r, top)

        self.corner(90)
        self.edge(topwidth)
        self.doveTailJoint(h, positive=False)
        self.edge(bottomwidth)
        self.corner(90)

    @restore
    def rectangularWall(self, x, y, edges="eeee",
                        holesMargin=None, holesSettings=None,
                        bedBolts=None, bedBoltSettings=None):
        if len(edges) != 4:
            raise ValueError, "four edges required"
        edges += edges # append for wrapping around
        for i, l in enumerate((x, y, x, y)):
            self._edge(self._edgewidth(edges[i-1]), 'e')
            self._edge(l, edges[i],
                       bedBolts=self.getEntry(bedBolts, i),
                       bedBoltSettings=self.getEntry(bedBoltSettings, i))
            self._edge(self._edgewidth(edges[i+1]), 'e')
            self.corner(90)

        if holesMargin is not None:
            self.moveTo(holesMargin+self._edgewidth(edges[-1]),
                        holesMargin+self._edgewidth(edges[0]))
            self.hexHolesRectangle(x-2*holesMargin, y-2*holesMargin)

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


        self.ctx.stroke()
        self.surface.flush()

if __name__ == '__main__':
    b = Boxes(900, 700)
    b.render(100, 161.8, 120)
