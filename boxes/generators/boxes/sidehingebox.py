# Copyright (C) 2024 Guillaume Collic
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

import math

from boxes import *


class SideHingeBox(Boxes):
    """Box, with an hinge that does not protrude from the back of the box, and a latch."""

    description = """
This box is another take on a hinge box.
The hinges doesn't protrude from the box, but the sides needs double walls.
When opened, 2 sides are opening, improving access inside the box.
An optional latch is included, based on a mechanical switch and a 3D printed button.
The latch is one-way: the box can be closed freely
(this side of the button is angled, and totally smooth since it's the printing bed surface),
but can't be inadvertently opened.
"""

    ui_group = "Box"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.buildArgParser("x", "y", "h", "outside")
        self.addSettingsArgs(edges.FingerJointSettings, finger=2.0, space=2.0)

        self.argparser.add_argument(
            "--play",  action="store", type=float, default=0.15,
            help="play between the two sides as multiple of the wall thickness")

        self.argparser.add_argument(
            "--hinge_center",  action="store", type=float, default=0.0,
            help="distance between the hinge center and adjacent sides (0.0 for default)")

        self.argparser.add_argument(
            "--hinge_radius",  action="store", type=float, default=5.5,
            help="radius of the hinge inner circle")

        self.argparser.add_argument(
            "--cherrymx_latches",  action="store", type=int, default=0,
            choices=[0, 1, 2],
            help="add one or two latches, based on 3D printing and a cherry mx compatible mechanical keyboard switch")


    def render(self):
        x, yi, hi = self.x, self.y, self.h
        t = self.thickness
        p = self.play * t
        hinge_radius = self.hinge_radius
        hinge_center = self.hinge_center if self.hinge_center else 2*t + hinge_radius
        latches = self.cherrymx_latches
        self.mx_width = 15.4
        self.mx_length = t+16.4+2.8 #2.8 can be removed if the switch is trimmed flush

        if self.outside:
            x -= 2*t
            yi -= 4*t + 2*p
            hi -= 2*t

        yo = yi + 2*(t+p)
        ho = hi + t

        # one side is shared between inside and outside part,
        # so that the lid can rotate and lay flat, without touching the inner bottom
        fingered_hi = 2*hinge_center-t
        # a small gap is also needed for both part to rotate freely
        # (for a rounded angled finish, a gapless version could be added, with manual sanding or mechanical round milling)
        gap = math.sqrt(abs(pow(hinge_center*math.sqrt(2),2)-pow(hinge_center-t,2)))-hinge_center
        fingered_ho = ho - gap - 2*hinge_center

        with self.saved_context():
            self.inner_side(x, hi, hinge_center, hinge_radius, fingered_hi, latches, reverse=True)
            self.rectangularWall(
                yi,
                hi,
                "fFeF",
                callback=[lambda:self.back_cb(yi, latches)],
                move="right",
                label="inner - full side D")
            self.inner_side(x, hi, hinge_center, hinge_radius, fingered_hi, latches)
        self.rectangularWall(0, hi, "ffef", move="up only")

        with self.saved_context():
            self.outer_side(x, ho, hinge_center, hinge_radius, fingered_ho, latches)
            with self.saved_context():
                self.rectangularWall(yo, fingered_ho, "fFeF", move="up", label="outer - small side B")
                self.moveTo(t+p,0)
                self.rectangularWall(yi, fingered_hi, "eFfF", move="right", label="inner - small side B")
            self.rectangularWall(yo, 0, "fFeF", move="right only")
            self.outer_side(x, ho, hinge_center, hinge_radius, fingered_ho, latches, reverse=True)
        self.rectangularWall(0, ho, "ffef", move="up only")

        bottom_callback = [
            lambda:self.fingerHolesAt(x-self.mx_width-t/2, 0, self.mx_length),
            lambda:self.back_cb(yi, latches),
            lambda:self.fingerHolesAt(self.mx_width+t/2, 0, self.mx_length) if latches>1 else None,
        ] if latches else None
        self.rectangularWall(x, yi, "FFFF", callback=bottom_callback, move="right", label="inner - bottom")
        self.rectangularWall(x, yo, "FEFF", move="right", label="outer - upper lid")
        for _ in range(2):
            self.rectangularWall(2*t, 1.5*t, "eeee", move="right")

        if latches:
            for _ in range(latches):
                with self.saved_context():
                    self.rectangularWall(self.mx_width, self.mx_width, "eeee", move="right")
                    self.rectangularWall(self.mx_width, self.mx_width, "ffef", move="right")
                    self.rectangularWall(self.mx_length, self.mx_width, "ffeF", move="right")
                self.rectangularWall(self.mx_length, self.mx_width, "ffeF", move="up only")
            self.text(f"""
OpenSCAD code for 3D printing the cherry MX latch button:
#############################################
play = 0.1;
plywood_t = {t};
ear_t = 0.4;
ear_d = 15;
btn_d = 11.4;
btn_ext_h = min(plywood_t, 3.7);
btn_h = ear_t + plywood_t + btn_ext_h;
module mx_outer() {{
  translate([0,0,btn_h+4])
    mirror([0,0,1])
    linear_extrude(height = 4.2) {{
      offset(r=1, $fn=32){{
        square([4.5, 2.8], center=true);
      }}
    }};
}}
module mx_inner() {{
  translate([0,0,btn_h+4.01])
  mirror([0,0,1])
  for (rect = [ [4.05, 1.32], [1.22, 5] ]) {{
    linear_extrude(height = 4)
      square(rect, center=true);
    hull() {{
      linear_extrude(height = 0.01)
        offset(delta = 0.4)
        square(rect, center=true);
      translate([0, 0, 0.5])
        linear_extrude(height = 0.01)
        square(rect, center=true);
    }};
  }}
}}
angle = atan2(btn_ext_h+0.2, btn_d/2);
rotate([0, angle, 0]) difference(){{
  union(){{
    cylinder(d=btn_d-2*play, h=btn_h, $fn=512);
    translate([0, 0, btn_h-ear_t/2])
      cube([btn_d/2, ear_d, ear_t], center=true);
    mx_outer();
  }}
  rotate([0, 90-angle, 0])
    translate([0, -btn_d/2, 0])
    cube(btn_d);
  mx_inner();
}}""")

    def back_cb(self, y, latches):
        if latches>0:
            self.fingerHolesAt(self.mx_length+self.thickness/2, 0, self.mx_width)
        if latches>1:
            self.fingerHolesAt(y-self.mx_length-self.thickness/2, 0, self.mx_width)

    def inner_side_cb(self, x, reverse):
        if reverse:
            self.fingerHolesAt(x-self.mx_width-self.thickness/2, 0, self.mx_width)
            self.circle(x-self.mx_width/2, self.mx_width/2, 5.7+self.burn)
        else:
            self.fingerHolesAt(self.mx_width+self.thickness/2, 0, self.mx_width)
            self.circle(self.mx_width/2, self.mx_width/2, 5.7+self.burn)

    def inner_side(self, x, h, hinge_center, hinge_radius, fingered_h, latches, reverse=False):
        sides = Inner2SidesEdge(
            self, x,  h, hinge_center, hinge_radius, fingered_h, reverse
        )
        noop_edge = edges.NoopEdge(self, margin=self.thickness if reverse else 0)

        self.rectangularWall(
            x,
            h,
            ["f", "f", sides, noop_edge] if reverse else["f", sides, noop_edge, "f"],
            move="right",
            label="inner - hinge side " + ("A" if reverse else "C"),
            callback=[
                lambda: self.inner_side_cb(x, reverse)
            ] if (latches and reverse) or latches>1 else None,
        )

    def outer_side(self, x, h, hinge_center, hinge_radius, fingered_h, latches, reverse=False):
        t = self.thickness
        sides = Outer2SidesEdge(
            self, x,  h, hinge_center, hinge_radius, fingered_h, reverse
        )
        noop_edge = edges.NoopEdge(self, margin=t if reverse else 0)

        latch_x, latch_y = (t+self.mx_width/2, self.mx_width/2)
        if reverse:
            latch_x, latch_y = latch_y, latch_x
        self.rectangularWall(
            x,
            h,
            ["f", "E", sides, noop_edge] if reverse else["f", sides, noop_edge, "E"],
            move="right",
            label="outer - hinge side " + ("C" if reverse else "A"),
            callback=[
                None,
                None,
                lambda: self.circle(latch_x, latch_y, 5.7+self.burn)
            ] if (latches and not reverse) or latches>1 else None,
        )

class Inner2SidesEdge(edges.BaseEdge):
    """
    The next edge should be a NoopEdge
    """

    def __init__(self, boxes, length, height, hinge_center, hinge_radius, fingered_h, reverse) -> None:
        super().__init__(boxes, None)
        self.length = length
        self.height = height
        self.hinge_center=hinge_center
        self.hinge_radius=hinge_radius
        self.fingered_h=fingered_h
        self.reverse=reverse

    def __call__(self, _, **kw):
        actions = [self.hinge_hole, self.fingers, self.smooth_corner]
        actions = list(reversed(actions)) if self.reverse else actions
        for action in actions:
            action()

    def fingers(self):
        self.boxes.edges['f'](self.fingered_h)

    def smooth_corner(self):
        # the corner has to be rounded to rotate freely
        hinge_to_lid = self.height+self.boxes.thickness-self.hinge_center
        hinge_to_side = self.hinge_center-self.boxes.thickness
        corner_height = hinge_to_lid-math.sqrt(math.pow(hinge_to_lid, 2) - math.pow(hinge_to_side, 2))
        angle = math.degrees(math.asin(hinge_to_side/hinge_to_lid))
        path = [
            self.height-self.fingered_h-corner_height,
            (90-angle, 0),
            0,
            (angle, hinge_to_lid),
            self.boxes.thickness+self.length-self.hinge_center,
        ]
        path = list(reversed(path)) if self.reverse else path
        self.polyline(*path)

    def hinge_hole(self):
        direction = -1 if self.reverse else 1
        x = direction*(self.hinge_center-self.boxes.thickness-self.boxes.burn)
        y = self.hinge_center-self.boxes.thickness
        t = self.boxes.thickness
        self.boxes.rectangularHole(x, y, 1.5*t, t)

    def margin(self) -> float:
        return 0 if self.reverse else self.boxes.edges['f'].margin()

class Outer2SidesEdge(edges.BaseEdge):
    """
    The next edge should be a NoopEdge
    """

    def __init__(self, boxes, length, height, hinge_center, hinge_radius, fingered_h, reverse) -> None:
        super().__init__(boxes, None)
        self.length = length
        self.height = height
        self.hinge_center=hinge_center
        self.hinge_radius=hinge_radius
        self.fingered_h=fingered_h
        self.reverse=reverse

    def __call__(self, _, **kw):
        actions = [self.fingers, self.smooth_corner, self.hinge_hole]
        actions = list(reversed(actions)) if self.reverse else actions
        for action in actions:
            action()

    def fingers(self):
        self.boxes.edges['f'](self.fingered_h)

    def smooth_corner(self):
        # the corner has to be rounded to rotate freely
        path = [
            0,
            (-90, 0),
            self.boxes.thickness,
            (90, 0),
            self.height-self.fingered_h-self.hinge_center,
            (90, self.hinge_center),
            self.boxes.thickness+self.length-self.hinge_center,
        ]
        path = list(reversed(path)) if self.reverse else path
        self.polyline(*path)

    @restore
    @holeCol
    def hinge_hole(self):
        direction = -1 if self.reverse else 1
        x = direction*(self.hinge_center-self.length-self.boxes.thickness-self.boxes.burn)
        y = self.hinge_center
        t = self.boxes.thickness
        self.boxes.circle(x, y, self.hinge_radius)
        self.boxes.rectangularHole(x, y, t, 1.5*t)

    def margin(self) -> float:
        return 0 if self.reverse else self.boxes.edges['f'].margin()
