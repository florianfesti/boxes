#!/usr/bin/python

import cairo
import math


class Boxes:

    def __init__(self, thickness=3.0):
        self.thickness = thickness
        self.burn = 0.1
        self.fingerJointSettings = (10.0, 10.0)
        self.doveTailJointSettings = (15, 10, 60, 2) # width, depth, angle, radius
        self.flexSettings = (1.5, 3.0, 15.0) # line distance, connects, width
        self.output = "box.svg"
        self._init_surface()

    def _init_surface(self):
        width = 700
        height = 400

        self.surface = cairo.SVGSurface(self.output, width, height)
        self.ctx = ctx = cairo.Context(self.surface)
        ctx.translate(0, height)
        ctx.scale(1, -1)

        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()

        ctx.set_source_rgb(0.0, 0.0, 0.0)
        ctx.set_line_width(0.1)


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
            self.ctx.rectangle(pos+s+b, self.thickness/2-b,
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

        self.edge((width+leftover)/2.0+diffx-l1)
        for i in xrange(sections):
            self._turn(radius+self.burn, angle, right=positive)
            self.edge(2*(l2-l1))
            self._turn(radius-self.burn, angle, right=not positive)
            self.edge(2*(diffx-l1)+width)
            self._turn(radius-self.burn, angle, right=not positive)
            self.edge(2*(l2-l1))
            self._turn(radius+self.burn, angle, right=positive)
            if i<sections-1: # all but the last
                self.edge(2*(diffx-l1)+width)
        self.edge((width+leftover)/2.0+diffx-l1)
        self.ctx.translate(*self.ctx.get_current_point())

    def flex(self, x, h, settings=None):
        dist, connection, width = settings or self.flexSettings
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

    ####################################################################
    ### Parts
    ####################################################################

    def basePlate(self, x=100, y=100, r=0):
        self.ctx.save()
        self.moveTo(r, 0)

        self.fingerJoint(0.5*x-r)
        self.fingerJoint(0.5*x-r)
        self.corner(90, r)
        self.fingerJoint(y-2*r)
        self.corner(90, r)

        self.fingerJoint(x-2*r)
        self.corner(90, r)
        self.fingerJoint(y-2*r)
        self.corner(90, r)

        self.ctx.restore()

    def wall(self, x=100, y=100, h=100, r=0):
        self.ctx.save()
        self.moveTo(20, 0)
        c4 = (r+self.burn)*math.pi*0.5 # circumference of quarter circle  

        #self.fingerJoint(0.5*x-r, positive=False)
        self.fingerHoleEdge(0.5*x-r, 5)
        self.flex(c4, h)
        #self.fingerJoint(y-2*r, positive=False)
        self.fingerHoleEdge(y-2*r, 5)
        self.flex(c4, h)
        self.fingerHoleEdge(x-2*r, 5)
        #self.fingerJoint(x-2*r, positive=False)
        self.flex(c4, h)
        self.fingerHoleEdge(y-2*r, 5)
        self.flex(c4, h)
        #self.fingerJoint(0.5*x-r, positive=False)
        self.fingerHoleEdge(0.5*x-r, 5)

            
        self.corner(90)
        self.edge(20)
        self.doveTailJoint(h-20, positive=False)
        self.corner(90)

        self.edge(2*(x+y-4*r)+4*c4)

        self.corner(90)
        self.doveTailJoint(h-20)
        self.edge(20)
        self.corner(90)

        self.ctx.restore()

    ##################################################
    ### main
    ##################################################

    def render(self, x, y, r):

        self.moveTo(20,20)
        self.basePlate(x, y, r)
        self.moveTo(0, y+20)
        self.wall(x, y, 120, r)
        
        self.ctx.stroke()
        self.surface.flush()

if __name__ == '__main__':
    b = Boxes()
    b.render(200, 150, 30)
