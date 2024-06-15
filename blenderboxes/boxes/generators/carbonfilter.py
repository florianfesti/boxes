# Copyright (C) 2013-2023 Florian Festi
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

from boxes import *

class CarbonFilter(Boxes):
    """Compact filter for activated char coal pellets"""

    description = """The filter does not include the top rim. You need some rectangular wooden strip about 2-3cm in size to glue around. The x and y are without this rim and should be about 5 cm smaller that the nominal size.

The following sizes are currently hard coded:

* Height of rails on top: 50mm
* Borders on top: 40mm
* Char coal width (horizontal): 40mm
* Bottom width: 40 + 20 + 40 mm

For assembly it is important that all bottom plates are the same way up. This allows the ribs of adjacent pockets to pass beside each other.

There are three type of ribs:

* Those with staight tops go in the middle of the bottom plates
* Those pointier angle go at the outer sides and meet with the side bars
* The less pointy go at all other sides of the bottom plates that will end up on the inside

The last two types of ribs do not have finger joints on the outside but still need to be glued to the top beam of the adjacent pocket or the left or right side bar.
"""

    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser(x=550, y=550, h=250)
        self.argparser.add_argument(
            "--pockets",  action="store", type=int, default=3,
            help="number of V shaped filter pockets")
        self.argparser.add_argument(
            "--ribs",  action="store", type=int, default=12,
            help="number of ribs to hold the bottom and the mesh")

    def sideCB(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness
        p = self.pockets

        posx = t
        w = self.w
        a = self.a

        self.fingerHolesAt(t/2, h, 50, -90)
        self.fingerHolesAt(x-t/2, h, 50, -90)
        
        for i in range(p):
            self.fingerHolesAt(posx + t/2, h, 50, -90+a)
            self.fingerHolesAt(posx + 40 + t/2, h, 50, -90+a)
            self.fingerHolesAt(posx + w - t/2, h, 50, -90-a)            
            self.fingerHolesAt(posx + w - 40 - t/2, h, 50, -90-a)

            self.fingerHolesAt(posx + w/2 -50 + t, 3.5*t, 100 - 2*t, 0)
            
            posx += w

    def bottomCB(self):
        t = self.thickness
        for i in range(self.ribs):
            self.fingerHolesAt((i+1) * self.y / (self.ribs + 1) - 1.5 * t,
                               0, 4*t, 90)
            self.fingerHolesAt((i+1) * self.y / (self.ribs + 1) - 1.5 * t,
                               40 - t, 20, 90)

    def topRailCB(self):
        t = self.thickness
        for i in range(self.ribs):
            self.fingerHolesAt((i+1) * self.y / (self.ribs + 1) - 1.5 * t,
                               0, 30, 90)
            
    def innerRibs(self, n, move=None):

        x, y, h = self.x, self.y, self.h
        t = self.thickness
        a = self.a
        a_ = math.radians(a)

        l = (h-4*t) / math.cos(a_) - 0.5 * t * math.sin(a_)

        tw = n * (20 + self.spacing) + l * math.sin(a_)
        th = h-3*t - 20 * math.cos(a_) + self.spacing

        if self.move(tw, th, move, True):
            return
        
        self.moveTo(0, t)

        for i in range(n):
            self.edges["f"](20)
            self.polyline(0, 90-a, l - 50, 90, t, -90)
            self.edges["f"](30)
            self.polyline(0, 90 + a, 20-t, 90 - a, l-20 + t * math.sin(a_),
                          90+a)

            self.moveTo(20 + self.spacing)
            self.ctx.stroke()
        
        self.move(tw, th, move, label="Inner ribs")

    def sideHolders(self, n, move=None):

        x, y, h = self.x, self.y, self.h
        t = self.thickness
        a = self.a
        a_ = math.radians(a)

        l = (h-4*t) / math.cos(a_) - 0.5 * t * math.sin(a_) - 50

        tw = n * (10 + self.spacing) + l * math.sin(a_)
        th = h - 4*t - 50

        if self.move(tw, th, move, True):
            return

        for i in range(n):
            self.polyline(10, 90-a, l, 90+a, 10, 90-a, l, 90+a)
            self.ctx.stroke()
            self.moveTo(10+self.spacing)

        self.move(tw, th, move, label="Inner ribs")

    def topStabilizers(self, n, move=None):
        t = self.thickness

        l = 2* (self.h-60) * math.sin(math.radians(self.a)) - 20
        tw = n * (6*t + self.spacing)
        th = l + 4*t

        if self.move(tw, th, move, True):
            return

        self.moveTo(t)
        for i in range(n):
            for j in range(2):
                self.polyline(0, 90, 2*t, -90, t, -90, 2*t, 90, 3*t, (90, t),
                              l+2*t, (90, t))
            self.ctx.stroke()
            self.moveTo(6*t + self.spacing)

        self.move(tw, th, move, label="Inner ribs")

    def outerRibs(self, n, n_edge, move=None):

        x, y, h = self.x, self.y, self.h
        t = self.thickness
        a = self.a
        a_ = math.radians(a)

        l = (h-4*t) / math.cos(a_) + 0.5 * t * math.sin(a_)

        dl = (20 - t) * (math.tan(math.pi/2 - 2*a_) + math.sin(a_))
        dll = (20 - t) * (1 / math.sin(2*a_))

        dl2 = (20 - t) * (math.tan(math.pi/2 - a_) + math.sin(a_))
        dll2 = (20 - t) * (1 / math.sin(a_))

        tw = (n // 2) * (40 + t) + l * math.sin(a_)
        th = h + 5*t

        if self.move(tw, th, move, True):
            return

        self.moveTo(2*t)
        
        for i in range(n):
            self.polyline(0*t + 20, (90, 2*t), 2*t, -a)
            if i < n_edge:
                self.polyline(l - dl2 - t * math.sin(a_), a,
                              dll2, 180 - a, 20)
            else:
                self.polyline(l - dl - t * math.sin(a_), 2*a,
                              dll, 180 - 2*a, 20)
            self.edges["f"](30)
            self.polyline(0, -90, t, 90, l - 50, a, t, -90)
            self.edges["f"](4*t)
            self.polyline(0, 90, 1*t, (90, 2*t))

            self.moveTo(t + 40)# + self.spacing)
            if i + 1 == n // 2:
                self.moveTo(2*t+0.7*self.spacing, h + 5*t, 180)
            self.ctx.stroke()

        self.move(tw, th, move, label="Outer ribs")
        
    def render(self):
        # adjust to the variables you want in the local scope
        x, y, h = self.x, self.y, self.h

        self.y = y = self.adjustSize(y)
        
        t = self.thickness
        
        self.w = (x - 2*t) / self.pockets
        self.a = math.degrees(math.atan((self.w - 100) / 2 / (h - 4*t)))

        # sides
        for i in range(2):
            self.rectangularWall(x, h, callback=[self.sideCB], move="up")
        for i in range(2):
            self.rectangularWall(y, 50, "efef", label="Sides", move="up")

        # top rails
        for i in range(self.pockets * 4):
            self.rectangularWall(y, 50, "efef",
                                 callback=[self.topRailCB],
                                 label="Top rails", move="up")

        # bottoms
        w = 100 - 2*t
        for i in range(self.pockets):
            self.rectangularWall(
                y, w, "efef",
                callback=[self.bottomCB, None, self.bottomCB],
                label="bottom plate", move="up")

        self.innerRibs(self.pockets * self.ribs * 2, move="up")
        self.outerRibs(self.pockets * self.ribs * 2, self.ribs * 2, move="up")
        self.sideHolders(self.pockets * 8, move="up")
        self.topStabilizers(min(3, self.ribs) *self.pockets)
