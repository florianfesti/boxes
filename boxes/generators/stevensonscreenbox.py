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

from dataclasses import dataclass
pass
import numpy as np
from boxes import Boxes, restore
from boxes import edges
from boxes.edges import Settings


@dataclass
class SlatGeometry:
    reduced_depth: float
    pitch: float
    n: int
    h: float


class StevensonScreenSettings(Settings):
    """Settings for a Stevenson Screen.

    Values:
    * absolute
      * angle : 45 : The angle the slats make with horizontal
      * overlap : 0.1 : The fraction of each slat that overlaps

    * relative
      * depth : 5 : The size of the slats, in multiples of thickness
    """
    absolute_params = {
        "angle": 45.0,
        "overlap": 0.1,
    }

    relative_params = {
        "depth": 7.0,
    }

    def checkValues(self) -> None:
        pass



class StevensonScreenBox(Boxes):
    """A box with Stevenson Screens front and back."""

    description = "This box is intended to hold a simple weather station."

    ui_group = "Box"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(StevensonScreenSettings, prefix="slat")
        self.buildArgParser("x", "y", "h")
        self.argparser.add_argument("--top_slope", default=6, help="The angle of the roof")

    @property
    def front_h(self):
        return self.h + self.x * np.sin(self.top_slope/180*np.pi)

    def calculate_slat_geometry(self, max_h) -> SlatGeometry:
        t = self.thickness
        angle = self.slat_angle
        overlap = self.slat_overlap
        depth = self.slat_depth * t

        # First, calculate the bounding box of a slat at its angle
        bbox_h = t*np.cos(np.radians(angle)) + depth*np.sin(np.radians(angle))
        bbox_w = t*np.sin(np.radians(angle)) + depth*np.cos(np.radians(angle))

        # That sets the pitch, once we shrink by the overlap
        pitch = bbox_h * (1-overlap)
        n = (max_h-bbox_h) // pitch + 1

        return SlatGeometry(
            reduced_depth=bbox_w,
            n=int(n),
            pitch=pitch,
            h = n * pitch # height on the outside including the top gap
        )

    @restore
    def slat_finger_holes(self, slats: SlatGeometry, h: float):
        # This mounts the slats to the sides, including the small
        # vertical wall at the top.
        # This function places the front of the slats at x=0
        t = self.thickness
        depth = self.slat_depth * t
        for i in range(slats.n):
            with self.saved_context():
                self.moveTo(0, i * slats.pitch, self.slat_angle)
                self.fingerHolesAt(0, t/2, depth, 0)
        self.fingerHolesAt(1.5*t, slats.h, h - slats.h, 90)

    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness
        top_slope = self.top_slope
        h1 = self.front_h

        # We'll make vertical walls at the top of the Stevenson Screen to take up any slack.
        # These will have a minimum height, let's guesstimate t*7.
        # They'll be inset by 1.5*t, so we can use finger holes to mount them.
        min_vertical = t*2
        front_h = h1 - np.sin(top_slope) * 2*t - t
        back_h = h
        front_slats = self.calculate_slat_geometry(front_h - min_vertical)
        back_slats = self.calculate_slat_geometry(back_h - min_vertical)

        def side_cb():
            # Draw holes for the
            self.slat_finger_holes(back_slats, back_h)
            self.moveTo(self.x, 0)
            self.ctx.scale(-1, 1)
            self.slat_finger_holes(front_slats, front_h)

        with self.saved_context():
            self.trapezoidWall(x, h, h1, "fefe", move="up", label="left", callback=[side_cb])
            self.trapezoidWall(x, h, h1, "fefe", move="mirror up", label="right", callback=[side_cb])

            self.rectangularWall(x, y, "FeFe", move="up", label="bottom")
        self.rectangularWall(x, y, "FeFe", move="right only")

        with self.saved_context():
            # Make the slats
            slat_d = self.slat_depth * t
            for i in range(front_slats.n):
                self.rectangularWall(y, slat_d, "efef", move="up", label="front slat")
            for i in range(back_slats.n):
                self.rectangularWall(y, slat_d, "efef", move="up", label="back slat")

            # Now the top parts of the front and back
            front_vertical_h = front_h - front_slats.h
            back_vertical_h = back_h - back_slats.h
            self.rectangularWall(y, front_vertical_h, "efef", move="up", label="front")
            self.rectangularWall(y, back_vertical_h, "efef", move="up", label="back")
        #self.rectangularWall(y, back_vertical_h, "efef", move="right only")

        #with self.saved_context():
            # The roof
            self.flangedWall(y, x/np.cos(top_slope), "eFeF", flanges=[t, t, t, t], r=t, move="up", label="top")
        #self.flangedWall(y, x/np.cos(top_slope), "eFeF", flanges=[t, t, t, t], r=t, move="right only")
