#!/usr/bin/python

from boxes import Boxes

class Silverware(Boxes):
    ####################################################################
    ### Parts
    ####################################################################

    def basePlate(self, x, y, r):
        self.roundedPlate(x, y, r, callback=[
                lambda: self.fingerHolesAt(x/3.0-r, 0, 0.5*y-self.thickness),
                lambda: self.fingerHolesAt(x/6.0, 0, 0.5*y-self.thickness),
                lambda: self.fingerHolesAt(y/2.0-r, 0, x),
                lambda: self.fingerHolesAt(x/2.0-r, 0, 0.5*y-self.thickness)
                ])

    def wall(self, x=100, y=100, h=100, r=0):
        self.surroundingWall(x,y,r,h, bottom='holes', callback={
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

b = Silverware(900, 700)
b.render(250, 250/1.618, 120, 30)
