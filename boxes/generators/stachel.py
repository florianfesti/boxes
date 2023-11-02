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

from boxes import *


class Stachel(Boxes):
    """Bass Recorder Endpin"""
    
    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.argparser.add_argument(
            "--flutediameter",  action="store", type=float, default=115.0,
            help="diameter of the flutes bottom in mm")
        self.argparser.add_argument(
            "--polediameter",  action="store", type=float, default=25.,
            help="diameter if the pin in mm")
        self.argparser.add_argument(
            "--wall",  action="store", type=float, default=7.,
            help="width of the surrounding wall in mm")

    def layer(self, ri, ro, rp, holes=False, move=""):

        r = 2.5 # radius
        l = 25 # depth of clamp
        w = 20 # width of clamp

        wp = rp+8 # width pole

        tw = 2*ro + 2*rp
        th = 2*ro + l
        
        if self.move(tw, th, move, True):
            return

        self.moveTo(ro, r, 90)

        a1 = math.degrees(math.asin(w / ro))
        a2 = math.degrees(math.asin(wp / ro))
        l1 = ro*(1-math.cos(math.radians(a1)))
        a3 = math.degrees(math.asin(1./rp))
        self.polyline(ro-ri+l-r, 90, 0, (-355, ri), 0, 90, ro-ri+l-r, # inside
                      (90, r), w-2*r, (90, r))
        if holes: # right side main clamp
            poly1 = [(l+l1-2)/2-r, 90, w-2, -90, 2, -90, w-2, 90,
                          (l+l1-2)/2]
            self.polyline(*poly1)
        else:
            self.polyline(l+l1-r)
        self.polyline(0, -90+a1, 0 , (90-a1-a2, ro), 0, -90+a2)
        if holes:
            poly2 = [2*rp+15, 90, wp-2, -90, 2, -90, wp-2, 90, 10-2-r]
            self.polyline(*poly2)
        else:
            self.polyline(25+2*rp-r)
        self.polyline(0, (90, r), wp-1-r, 90, 20, 90-a3, 0, (-360+2*a3, rp), 0, 90-a3, 20, 90, wp-1-r, (90, r))
        if holes:
            self.polyline(*list(reversed(poly2)))
        else:
            self.polyline(25+2*rp-r)
        self.polyline(0, -90+a2, 0, (270-a2-a1-5, ro), 0, (-90+a1))
        if holes: # left sidemain clamp
            self.polyline(*list(reversed(poly1)))
        else:
            self.polyline(l+l1-r)
        self.polyline(0, (90, r), w-2*r, (90, r))
        
        self.move(tw, th, move)
        
        

    def render(self):

        ri = self.flutediameter / 2.0
        ro = ri + self.wall
        rp = self.polediameter / 2.0
        w = self.wall
        self.layer(ri-20, ro, rp, move="up")
        self.layer(ri, ro, rp, True, move="up")
        self.layer(ri, ro, rp, move="up")


