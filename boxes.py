#!/usr/bin/python

import cairo
import math


class Boxes:

    def __init__(self, width=300, height=200, thickness=3.0):
        self.thickness = thickness
        self.burn = 0.1
        self.fingerJointSettings = (10.0, 10.0)
        self.fingerHoleEdgeWidth = 1.0 # multitudes of self.thickness
        self.doveTailJointSettings = (10, 5, 50, 0.4) # width, depth, angle, radius
        self.flexSettings = (1.5, 3.0, 15.0) # line distance, connects, width
        self.output = "box.svg"
        self._init_surface(width, height)

    def _init_surface(self, width, height):
        self.surface = cairo.SVGSurface(self.output, width, height)
        self.ctx = ctx = cairo.Context(self.surface)
        ctx.translate(0, height)
        ctx.scale(1, -1)

        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()

        ctx.set_source_rgb(0.0, 0.0, 0.0)
        ctx.set_line_width(0.1)


    def cc(self, callback, number, x=0.0, y=0.0):
        """call callback"""
        self.ctx.save()
        self.moveTo(x, y)
        if callable(callback):
            callback(number)
        elif hasattr(callback, '__getitem__'):
            try:
                callback = callback[number]
                if callable(callback):
                    callback()
            except KeyError:
                pass
            except:
                self.ctx.restore()
                raise
        self.ctx.restore()

    ############################################################
    ### Turtle graphics commands
    ############################################################

    def corner(self, degrees, radius=0):
        d =  1 if (degrees > 0) else -1
        rad = degrees*math.pi/180
        if degrees > 0:
            self.ctx.arc(0, radius+self.burn, radius+self.burn,
                     -0.5*math.pi, rad - 0.5*math.pi)
        else:
            self.ctx.arc_negative(0, -(radius+self.burn), radius+self.burn,
                     0.5*math.pi, rad + 0.5*math.pi)
            
        self.continueDirection(rad)

    def edge(self, length):
        self.ctx.line_to(length, 0)
        self.ctx.translate(*self.ctx.get_current_point())

    def curveTo(self, x1, y1, x2, y2, x3, y3):
        """control point 1, control point 2, end point"""
        self.ctx.curve_to(x1, y1, x2, y2, x3, y3)
        dx = x3-x2
        dy = y3-y2
        rad = math.atan2(dy, dx)
        self.continueDirection(rad)

    def fingerJoint(self, length, positive=True, settings=None):
        # assumes, we are already moved out by self.burn!
        # negative also assumes we are moved out by self.thinkness!
        space, finger = settings or self.fingerJointSettings
        fingers = int((length-space) // (space+finger))
        leftover = length - fingers*(space+finger) - finger
        b = self.burn
        s, f, thickness = space, finger, self.thickness
        if not positive:
            b = -b
            thickness = -thickness

        self.ctx.move_to(0, 0)
        for i in xrange(fingers):
            pos = leftover/2.0+i*(space+finger)
            self.ctx.line_to(pos+s-b, 0)
            self.ctx.line_to(pos+s-b, -thickness)
            self.ctx.line_to(pos+s+f+b, -thickness)
            self.ctx.line_to(pos+s+f+b, 0)
        self.ctx.line_to(length, 0)
        self.ctx.translate(*self.ctx.get_current_point())

    def fingerHoles(self, length, settings=None):
        space, finger = settings or self.fingerJointSettings
        fingers = int((length-space) // (space+finger))
        leftover = length - fingers*(space+finger) - finger
        b = self.burn
        s, f = space, finger
        for i in xrange(fingers):
            pos = leftover/2.0+i*(space+finger)
            self.ctx.rectangle(pos+s+b, -self.thickness/2+b,
                               f-2*b, self.thickness - 2*b)

        self.ctx.move_to(0, length)
        self.ctx.translate(*self.ctx.get_current_point())

    def fingerHoleEdge(self, length, dist, settings=None):
        self.ctx.save()
        self.moveTo(0, dist+self.thickness/2)
        self.fingerHoles(length, settings)
        self.ctx.restore()
        # XXX continue path
        self.ctx.move_to(0, 0)
        self.ctx.line_to(length, 0)
        self.ctx.translate(*self.ctx.get_current_point())


    # helpers for doveTailJoint
    # not intended for general use
    def _turnLeft(self, radius, angle):
        self.ctx.arc(0, radius, radius,
                     -0.5*math.pi, angle)
        self.continueDirection(0.5*math.pi+angle)

    def _turnRight(self, radius, angle):
        self.ctx.arc_negative(0, -radius, radius,
                              0.5*math.pi, -angle)
        self.continueDirection(-0.5*math.pi - angle)

    def _turn(self, radius, angle, right=True):
        if right:
            self._turnRight(radius, angle)
        else:
            self._turnLeft(radius, angle)

    def doveTailJoint(self, length, positive=True, settings=None):
        width, depth, angle, radius = settings or self.doveTailJointSettings
        angle = math.pi*angle/180.0
        alpha = 0.5*math.pi - angle

        l1 = radius/math.tan(alpha/2.0)
        diffx = 0.5*depth/math.tan(alpha)
        l2 = 0.5*depth / math.sin(alpha)

        sections = int((length) // (width*2))
        leftover = length - sections*width*2

        p = 1 if positive else -1

        self.edge((width+leftover)/2.0+diffx-l1)
        for i in xrange(sections):
            self._turn(radius-p*self.burn, angle, right=positive)
            self.edge(2*(l2-l1))
            self._turn(radius+p*self.burn, angle, right=not positive)
            self.edge(2*(diffx-l1)+width)
            self._turn(radius+p*self.burn, angle, right=not positive)
            self.edge(2*(l2-l1))
            self._turn(radius-p*self.burn, angle, right=positive)
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
                    self.ctx.move_to(pos, h - sheight- 2*connection)
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

    ### Navigation

    def moveTo(self, x, y, degrees=0):
        self.ctx.translate(x, y)
        self.ctx.rotate(degrees*math.pi/180.0)
        self.ctx.move_to(0, 0)

    def continueDirection(self, angle=0):
        self.ctx.translate(*self.ctx.get_current_point())
        self.ctx.rotate(angle)

    # Building blocks

    def fingerHolesAt(self, x, y, length, angle=90, burn=None):
        if burn is None:
            burn = self.burn
        # XXX burn with callbacks
        self.ctx.save()
        self.moveTo(x, y+burn, angle)
        self.fingerHoles(length)
        self.ctx.restore()


    def hole(self, x, y, r):
        self.ctx.save()
        self.moveTo(x+r, y)
        self.ctx.arc(-r, 0, r, 0, 2*math.pi)
        self.ctx.restore()

    def hexHolesRectangle(self, x, y, r, b, style="circle"):
        w = r+b/2.0
        dist = w * math.cos(math.pi/6.0)
        # XXX leftover
        cx = int(x // dist) # ???
        cy = int(y // dist) # ???
        self.moveTo(dist/2, r)
        for i in xrange(cy//2):
            for j in xrange(cx):
                self.hole(2*j*w, i*4*dist, r)
            for j in xrange(cx-1):
                self.hole(2*j*w+w, i*4*dist + 2*dist, r)

    def hexHolesHex(self, h, r, b, style="circle", grow=None):
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


    def roundedPlate(self, x, y, r, callback=None):
        """fits surroundingWall
        first edge is split to have a joint in the middle of the side
        callback is called at the beginning of the straight edges
        0, 1 for the two part of the first edge, 2, 3, 4 for the others"""
        self.ctx.save()
        self.moveTo(r, 0)
        self.cc(callback, 0)
        self.fingerJoint(x/2.0-r)
        self.cc(callback, 1)
        self.fingerJoint(x/2.0-r)
        for i, l in zip(range(3), (y, x, y)):
            self.corner(90, r)
            self.cc(callback, i+2)
            self.fingerJoint(l-2*r)
        self.corner(90, r)
        self.ctx.restore()

    def _edge(self, l, style):
        if style == 'edge':
            self.edge(l)
        elif style == 'holes':
            self.fingerHoleEdge(l, 5)
        elif style == 'finger':
            self.fingerJoint(l, positive=False)

    def _edgewidth(self, style):
        if style == 'holes':
            return (self.fingerHoleEdgeWidth+1) * self.thickness
        elif style == 'finger':
            return self.thickness
        return 0.0

    def surroundingWall(self, x, y, r, h,
                        bottom='edge', top='edge',
                        callback=None):
        """
        h : inner height, not counting the joints
        callback is called a beginn of the flat sides with
          0 for right half of first x side;
          1 and 3 for y sides;
          2 for second x side
          4 for second half of thefirst x side
        """
        c4 = (r+self.burn)*math.pi*0.5 # circumference of quarter circle
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

    ####################################################################
    ### Parts
    ####################################################################

    def basePlate(self, x=100, y=100, r=0):
        self.ctx.save()
        self.moveTo(r, 0)

        # two walls
        self.fingerHolesAt(x/3.0-r, 0, 0.5*y-self.thickness)
        self.fingerHolesAt(x*2/3.0-r, 0, 0.5*y-self.thickness)

        self.fingerJoint(0.5*x-r)
        self.fingerJoint(0.5*x-r)

        self.corner(90, r)

        # Middle wall
        self.fingerHolesAt(y/2.0-r, 0, x)

        self.fingerJoint(y-2*r)
        self.corner(90, r)

        # single wall
        self.fingerHolesAt(x/2.0-r, 0, 0.5*y-self.thickness)

        self.fingerJoint(x-2*r)

        self.corner(90, r)
        self.fingerJoint(y-2*r)
        self.corner(90, r)

        self.ctx.restore()

    def wall(self, x=100, y=100, h=100, r=0):
        self.surroundingWall(x,y,r,h, bottom='finger', callback={
                0 : lambda: self.fingerHolesAt(x/6.0, 0, h),
                4 : lambda: self.fingerHolesAt(x/3.0-r, 0, h),
                1 : lambda: self.fingerHolesAt(y/2.0-r, 0, h),
                3 : lambda: self.fingerHolesAt(y/2.0-r, 0, h),
                2 : lambda: self.fingerHolesAt(x/2.0-r, 0, h),
                })

    def smallWall(self, y, h):
        l = 0.5*y - self.thickness

        self.ctx.save()
        self.moveTo(10, 0)

        self.fingerJoint(l)
        self.corner(90)
        self.fingerJoint(h-20)
        self.corner(90)
        self.edge(l)
        self.corner(90)
        self.fingerJoint(h-20)
        self.corner(90)

        self.ctx.restore()


    def handle(self, x, h, hl, r=20):
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

    def centerWall(self, x, h):
        self.ctx.save()

        for i in range(2, 5):
            self.fingerHolesAt(i*x/6.0, 0, h-20)

        self.fingerJoint(x)
        self.corner(90)
        self.fingerJoint(h-20)
        self.corner(90)

        self.handle(x, 150, 120)

        self.corner(90)
        self.fingerJoint(h-20)
        self.corner(90)
        self.ctx.restore()

    ##################################################
    ### main
    ##################################################

    def render(self, x, y, h, r):
        self.ctx.save()

        self.moveTo(10, 10)
        self.wall(x, y, h+self.thickness+5, r)
        self.moveTo(0, h+20)
        self.centerWall(x,h)
        self.moveTo(x+20, 0)

        for i in range(3):
            self.smallWall(y, h)
            self.moveTo(y/2.0+20, 0)

        self.moveTo(-1.5*y-80, h)
        self.basePlate(x, y, r)

        self.ctx.restore()

        self.ctx.stroke()
        self.surface.flush()

if __name__ == '__main__':
    b = Boxes(900, 700)
    b.render(250, 250/1.618, 120, 30)
