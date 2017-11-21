#!/usr/bin/env python3
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
import math

class Stachel(Boxes): # Change class name!
    """Bass Recorder Endpin"""
    
    ui_group = "Unstable" # see ./__init__.py for names

    def __init__(self):
        Boxes.__init__(self)

        # Uncomment the settings for the edge types you use
        # use keyword args to set default values
        # self.addSettingsArgs(edges.FingerJointSettings, finger=1.0,space=1.0)
        # self.addSettingsArgs(edges.StackableSettings)
        # self.addSettingsArgs(edges.HingeSettings)
        # self.addSettingsArgs(edges.LidSettings)
        # self.addSettingsArgs(edges.ClickSettings)
        # self.addSettingsArgs(edges.FlexSettings)

        # remove cli params you do not need
        #self.buildArgParser(x=100, sx="3*50", y=100, sy="3*50", h=100, hi=0)
        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--flutediameter",  action="store", type=float, default=115.0,
            help="DESCRIPTION")
        self.argparser.add_argument(
            "--polediameter",  action="store", type=float, default=25.,
            help="DESCRIPTION")
        self.argparser.add_argument(
            "--wall",  action="store", type=float, default=7.,
            help="DESCRIPTION")

    def layer(self, ri, ro, rp, holes=False, move=""):

        l = 20
        tw = 2*ro + 2*rp
        th = 2*ro + l
        r = 2.5

        
        if self.move(tw, th, move, True):
            return

        self.moveTo(ro, r, 90)

        a1 = math.degrees(math.asin(30 / ro))
        a2 = math.degrees(math.asin(25 / ro))
        l1 = ro*(1-math.cos(math.radians(a1)))
        a3 = math.degrees(math.asin(1./rp))
        print(a1, a2, a3, ro)
        self.polyline(ro-ri+l-r, 90, 0, (-355, ri), 0, 90, ro-ri+l-r, # inside
                      (90, r), 30-2*r, (90, r))
        if holes: # right side main clamp
            poly1 = [(l+l1-2)/2-r, 90, 27, -90, 2, -90, 27, 90,
                          (l+l1-2)/2]
            self.polyline(*poly1)
        else:
            self.polyline(l+l1-r)
        self.polyline(0, -90+a1, 0 , (90-a1-a2, ro), 0, -90+a2)
        if holes:
            poly2 = [2*rp+15, 90, 22, -90, 2, -90, 22, 90, 10-r]
            self.polyline(*poly2)
        else:
            self.polyline(25+2*rp-r)
        self.polyline(0, (90, r), 24-r, 90, 20, 90-a3, 0, (-360+2*a3, rp), 0, 90-a3, 20, 90, 24-r, (90, r))
        if holes:
            self.polyline(*list(reversed(poly2)))
        else:
            self.polyline(25+2*rp-r)
        self.polyline(0, -90+a2, 0, (270-a2-a1-5, ro), 0, (-90+a1))
        if holes: # left sidemain clamp
            self.polyline(*list(reversed(poly1)))
        else:
            self.polyline(l+l1-r)
        self.polyline(0, (90, r), 30-2*r, (90, r))
        
        self.move(tw, th, move)
        
        

    def render(self):
        # adjust to the variables you want in the local scope
        t = self.thickness
        # Initialize canvas
        self.open()

        ri = self.flutediameter / 2.0
        ro = ri + self.wall
        rp = self.polediameter / 2.0
        w = self.wall
        self.layer(ri-20, ro, rp, move="up")
        self.layer(ri, ro, rp, True, move="up")
        self.layer(ri, ro, rp, move="up")

        self.close()

