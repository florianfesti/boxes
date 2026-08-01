# Copyright (C) 2026 Oliver Jensen
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


class FrameLoom(Boxes):
    """
    A frame loom with a rotating heddle bar. At default-ish sizes, you can fit all the parts inside the loom cutout.
    """

    description ='''
This is a parametrized version of my [frame loom on Thingiverse](https://www.thingiverse.com/thing:7056512).
That in turn was modeled after the [Rocket Loom](https://www.popoutprojects.com/products/kitset-weaving-loom)
with some notable quality-of-life improvements.

![Loaded](static/samples/FrameLoom-2.jpg)

It's a good idea to gently round off sharp edges on the heddle bar, shuttles, and needles with some sandpaper,
so that they don't catch on the yarn.

To assemble, insert one foot (hole towards you) by hooking in the upper tab, then pushing the foot in so that it
snaps into place. Then insert the heddle into the hole, and lock it into place by inserting the second foot.
To switch heddles (e.g. to a pattern one) remove one foot, swap out the heddle, and replace the foot. If you're
assembling the pattern heddles, glue the parts together so that the etched `>` and `<` symbols face each other.

To load the shuttles, wrap thread so that you make two Xes along one side, then two Xes along the other side,
and repeat. You will get much more yarn on a shuttle for a given thickness than you would just wrapping yarn
around the middle.

To make bracelets, set the comb to have one fewer pins than warp threads you'll use, and you can avoid having the
piece pull together as you weave.

![Bracelet](static/samples/FrameLoom-3.jpg)
'''

    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)

        self.argparser.add_argument(
            "--warpthreads", action="store", type=int, default=38,
            help="Maximum number of threads in the warp (affects frame width)")
        self.argparser.add_argument(
            "--warpspacing", action="store", type=float, default=3.5,
            help="Millimeters per warp thread (2 - 5.5)")
        self.argparser.add_argument(
            "--outerframelength", action="store", type=float, default=235,
            help="Full length of the loom")

        self.argparser.add_argument(
            "--includeframe", action="store", type=boolarg, default=True,
            help="Whether or not to include the frame")
        self.argparser.add_argument(
            "--includeheddle", action="store", type=boolarg, default=True,
            help="Whether or not to include the standard heddle")
        self.argparser.add_argument(
            "--include2by2heddle", action="store", type=boolarg, default=False,
            help="Whether or not to include the 2x2 pattern heddle")
        self.argparser.add_argument(
            "--includediamondheddle", action="store", type=boolarg, default=False,
            help="Whether or not to include the diamond pattern heddle")
        self.argparser.add_argument(
            "--includeneedles", action="store", type=boolarg, default=True,
            help="Whether or not to include the needles")
        self.argparser.add_argument(
            "--combpins", action="store", type=int, default=12,
            help="Number of pins on the comb;set 0 to skip the comb")
        self.argparser.add_argument(
            "--numshuttles", action="store", type=int, default=2,
            help="how many shuttles to include")


    def frame(self, pin_width, num_warp_threads, frame_thickness, outer_frame_length, foot_attachment_x_offset, move=None):

        min_curve_radius = 0.5
        pin_tip_ratio = 1 / 2.5
        pin_base_radius = 0.5
        pin_ease_radius = 4.0
        pin_flank = 4.0
        pin_shaft = 1.0
        pin_tip_radius = max(min_curve_radius, pin_width * pin_tip_ratio / 2)
        _a = pin_base_radius - pin_ease_radius
        _b = pin_flank
        _c = pin_width / 2 - pin_tip_radius - pin_ease_radius
        _hyp = math.hypot(_a, _b)
        pin_flare = (180.0
                        - math.degrees(math.asin(_c / _hyp))
                        - math.degrees(math.atan2(_b, _a)))
        if not 0.0 < pin_flare <= 90.0:
            raise ValueError(
                "pin_width %.3f is out of range; supported range is 2.0 to 5.5 mm "
                "for the current pin shape constants" % pin_width)

        def drawPin():
            # Tapered spike, exactly pin_width wide at the frame edge.
            self.corner(pin_flare, pin_base_radius)
            self.edge(pin_flank)
            self.corner(90 - pin_flare, pin_ease_radius)
            self.edge(pin_shaft)
            self.corner(-180, pin_tip_radius)
            self.edge(pin_shaft)
            self.corner(90 - pin_flare, pin_ease_radius)
            self.edge(pin_flank)
            self.corner(pin_flare, pin_base_radius)

        def drawThreadHolder(thread_holder_height):
            self.corner(90)
            self.edge(10)
            self.corner(-180, thread_holder_height/2)
            self.edge(10)
            self.corner(90)

        thread_holder_height = 0.33

        corner_radius = 8
        corner_inner_radius = 4
        pin_area_height = 20
        pin_area_width = num_warp_threads*pin_width

        heddle_easing = 50
        heddle_easing_shift_radius = 3
        inner_frame_easing = pin_width / 2

        tw = 2*frame_thickness + pin_area_width
        th = outer_frame_length
        if self.move(tw, th, move, before=True):
            return

        self.moveTo(frame_thickness, 0)

        # outer frame
        with self.saved_context():
            for idx in range(num_warp_threads):
                drawPin()
                with self.saved_context():
                    self.moveTo(-pin_width/2, 8)
                    self.text(str(idx+1), align="center", fontsize=2, color=Color.ETCHING)
            self.edge(frame_thickness - corner_radius)
            self.corner(90, corner_radius)
            drawThreadHolder(thread_holder_height)

            self.edge(outer_frame_length - 2*corner_radius - 2*thread_holder_height)

            drawThreadHolder(thread_holder_height)
            self.corner(90, corner_radius)
            self.edge(frame_thickness - corner_radius)

            for idx in  range(num_warp_threads):
                font_size = 2
                if pin_width < 3:
                    font_size = 1.5
                drawPin()
                with self.saved_context():
                    self.moveTo(-pin_width/2, 10)
                    self.text(str(num_warp_threads-idx), align="center", fontsize=font_size, color=Color.ETCHING, angle=180)

            self.edge(frame_thickness - corner_radius)
            self.corner(90, corner_radius)
            drawThreadHolder(thread_holder_height)

            self.edge(outer_frame_length - 2*corner_radius - 2*thread_holder_height)

            drawThreadHolder(thread_holder_height)
            self.corner(90, corner_radius)

            self.edge(frame_thickness - corner_radius)

        # cutout
        with self.saved_context():
            self.moveTo(0, pin_area_height)
            self.moveTo(-inner_frame_easing + corner_inner_radius, 0)

            heddle_easing_angle = 45
            heddle_easing_shift_sideways = 2 * heddle_easing_shift_radius * (1-math.cos(math.radians(heddle_easing_angle)))
            heddle_easing_shift_vertical = 2 * heddle_easing_shift_radius * (math.sin(math.radians(heddle_easing_angle)))

            length_bottom = pin_area_width + 2*inner_frame_easing - 2*corner_inner_radius
            length_side = outer_frame_length - 2*pin_area_height - 2*corner_inner_radius
            height_below_easing = length_side - heddle_easing
            height_in_easing = heddle_easing - heddle_easing_shift_vertical
            length_top = length_bottom + 2*heddle_easing_shift_sideways

            self.edge(length_bottom)
            self.corner(90, corner_inner_radius)
            self.edge(height_below_easing)

            # this easing moves us heddle_easing_shift up and right
            self.corner(-heddle_easing_angle, heddle_easing_shift_radius)
            self.corner(heddle_easing_angle, heddle_easing_shift_radius)

            self.edge(height_in_easing)
            self.corner(90, corner_inner_radius)
            self.edge(length_top)
            self.corner(90, corner_inner_radius)
            self.edge(height_in_easing)

            # easign moves us heddle_easing_shift down and right
            self.corner(45, heddle_easing_shift_radius)
            self.corner(-45, heddle_easing_shift_radius)

            self.edge(height_below_easing)
            self.corner(90, corner_inner_radius)

        # foot holes
        with self.saved_context():
            holex = self.thickness
            holey = 23
            up = outer_frame_length - holey/2 - pin_area_height - corner_inner_radius/2
            self.rectangularHole(-foot_attachment_x_offset, up, holex, holey)
            self.rectangularHole(foot_attachment_x_offset+pin_area_width, up, holex, holey)

        self.move(tw, th, move)

    def foot(self, hole_radius, move=None):

        width = 33
        height = 40
        neck = 23
        cutout_tab_height = 2
        cutout_depth = 0.75 * height
        cutout_angle = 178
        cutout_radius = 0.5

        residual_angle = math.radians(180-cutout_angle)
        cutout_return_length = cutout_depth / math.cos(residual_angle) + cutout_radius * math.tan(residual_angle)
        cutout_width = cutout_depth * math.tan(residual_angle) + cutout_radius * (1.0 + 1.0 / math.cos(residual_angle))

        tw = width
        th = height + self.thickness + 3
        if self.move(tw, th, move, before=True):
            return

        self.moveTo(5 + 2, 3, 90)

        self.edge(self.thickness)
        self.corner(90)
        self.edge(5)
        # body
        self.corner(-90, 2)
        self.edge(height - width/2 - 2)
        self.corner(-180, width/2)
        self.edge(height - width/2 - 0.5)
        self.corner(-90, 0.5)

        self.edge(2.5)
        self.corner(90)
        self.edge(self.thickness)
        # small tab
        self.corner(90)
        self.corner(-180, 1.5)
        self.edge(cutout_tab_height)
        self.corner(-90)
        # cutout
        self.edge(cutout_depth)
        self.corner(cutout_angle, cutout_radius)
        self.edge(cutout_return_length)
        # end cutout
        self.corner(90 - cutout_angle)
        self.edge(neck - cutout_tab_height - cutout_width)
        # large tab
        self.corner(-180, 1.5)

        # hole
        self.corner(90)
        self.hole(self.thickness + 6.2, -1.3, hole_radius)

        self.move(tw, th, move)


    def drawHeddlePinsFromPattern(self, nib_radius, heddle_corner_radius, heddle_height, pin_width, pattern):
        #print(''.join(pattern))
        previous = 0
        for point in pattern:
            if previous == 0 and point == 1:
                self.corner(-90, heddle_corner_radius)
                self.edge(heddle_height - heddle_corner_radius)
                self.corner(90, nib_radius)
            elif previous == 1 and point == 0:
                self.corner(90, nib_radius)
                self.edge(heddle_height - heddle_corner_radius)
                self.corner(-90, heddle_corner_radius)

            if point == 1:
                self.corner(90, nib_radius)
                self.corner(-90, nib_radius)
                self.edge(pin_width - 4*nib_radius)
                self.corner(-90, nib_radius)
                self.corner(90, nib_radius)
            elif point == 0:
               if previous == 0:
                   self.edge(pin_width)
               else:
                   self.edge(pin_width - 2*nib_radius - 2*heddle_corner_radius)
            previous = point

        if previous == 1:
            self.corner(90, nib_radius)
            self.edge(heddle_height - heddle_corner_radius)
            self.corner(-90, heddle_corner_radius)
        else:
            self.edge(pin_width - nib_radius - heddle_corner_radius)

    def heddle(self, pattern_left, pattern_right,
               pin_width, num_warp_threads, foot_attachment_x_offset, foot_hole_radius,
               handle=True, holes=False, clipons=False,
               move=None):

        # patterns are passed in from bottom to top, so reverse the left pattern
        patterns = [pattern_left, pattern_right[::-1]]

        handle_length = 20
        heddle_height = 18
        heddle_corner_radius = 0.25 * pin_width
        nib_radius = 0.33
        lip_size = 1

        handle_width = math.sqrt(4*foot_hole_radius**2 - self.thickness**2)
        handle_radius = (handle_width)/2
        pin_area = pin_width * num_warp_threads
        axle_side_length = foot_attachment_x_offset - self.thickness / 2

        hole_length = pin_area/8
        num_holes   = 3
        if hole_length < self.thickness:
            num_holes = 1
            hole_length = max(3*hole_length, 2*self.thickness)
        elif hole_length < 2*self.thickness:
            num_holes = 2
            hole_length *= 2


        tw = 2*heddle_height + handle_width + 2
        th = 2*handle_length + 2*axle_side_length + pin_area
        if self.move(tw, th, move, before=True):
            return

        self.moveTo(heddle_height, handle_length)

        for idx in range(2):
            self.edge(lip_size)
            if handle:
                self.corner(-90)
                self.edge(handle_length - handle_radius)
                self.corner(180, handle_radius)
                self.edge(handle_length - handle_radius)
                self.corner(-90)
            elif clipons:
                self.edge(handle_radius - 0.5*self.thickness)
                self.moveTo(self.thickness)
                self.edge(handle_radius - 0.5*self.thickness)
            else:
                self.edge(2*handle_radius)
            self.edge(lip_size)
            self.corner(90)

            self.edge(axle_side_length - heddle_corner_radius - nib_radius)
            self.drawHeddlePinsFromPattern(nib_radius, heddle_corner_radius, heddle_height, pin_width, patterns[idx])
            self.edge(axle_side_length - heddle_corner_radius - nib_radius)

            self.corner(90)

        if holes:
            with self.saved_context():
                self.moveTo(lip_size + handle_radius, pin_area/2 + axle_side_length)

                if num_holes != 2:
                    self.rectangularHole(0, 0, self.thickness, hole_length)
                if num_holes != 1:
                    self.rectangularHole(0, pin_area/3, self.thickness, hole_length)
                    self.rectangularHole(0, -pin_area/3, self.thickness, hole_length)
                self.moveTo(-self.thickness/2, -pin_area/3 - hole_length/2)
                self.text(">", align="right", fontsize=4, color=Color.ETCHING_DEEP)

        if clipons:
            ha = hole_length/2
            a = axle_side_length + pin_area/6 - ha
            b = pin_area/3 - ha
            c = pin_area/3 - ha
            d = axle_side_length + pin_area/6

            with self.saved_context():
                self.moveTo(lip_size + handle_radius + self.thickness/2, a)
                self.text("<", align="left", fontsize=4, color=Color.ETCHING_DEEP)

            with self.saved_context():

                self.moveTo(lip_size + handle_radius - self.thickness/2, 0, 90)

                def zig():
                    with self.saved_context():
                        self.moveTo(0,0,-90)
                        self.edge(self.thickness)
                        self.moveTo(0, hole_length/2, 180)
                        self.edge(self.thickness / 2)

                for _ in range(2):
                    self.edge(a)
                    if num_holes != 1:
                        zig()
                        self.moveTo(ha)
                    else:
                        self.edge(ha)
                    self.edge(b)
                    if num_holes != 2:
                        zig()
                        self.moveTo(ha)
                    else:
                        self.edge(ha)
                    self.edge(c)
                    if num_holes != 1:
                        zig()
                        self.moveTo(ha)
                    else:
                        self.edge(ha)
                    self.edge(d)
                    self.moveTo(0, -self.thickness, 180)


        self.move(tw, th, move)


    def shuttle(self, shuttle_length, move=None):

        cutout_depth = min(20, .2 * shuttle_length)
        outer_radius = 2
        inner_radius = 4

        shuttle_length_edge = shuttle_length - 2*outer_radius
        cutout_depth_edge = cutout_depth - outer_radius - inner_radius

        tw = outer_radius*4 + inner_radius*2
        th = shuttle_length
        if self.move(tw, th, move, before=True):
            return

        self.moveTo(0, outer_radius, 90)

        self.edge(shuttle_length_edge)
        self.corner(-180, outer_radius)
        self.edge(cutout_depth_edge)
        self.corner(180, inner_radius)
        self.edge(cutout_depth_edge)
        self.corner(-180, outer_radius)
        self.edge(shuttle_length_edge)
        self.corner(-180, outer_radius)
        self.edge(cutout_depth_edge)
        self.corner(180, inner_radius)
        self.edge(cutout_depth_edge)
        self.corner(-180, outer_radius)

        self.move(tw, th, move)

    def needle(self, needle_length, big_radius=3, small_radius=0.75, move=None):

        hole_clearance = 2

        def drawNeedleShape(needle_length, big_radius, small_radius):
            needle_length_centers = needle_length - big_radius - small_radius
            needle_angle_r = math.asin((big_radius - small_radius) / needle_length_centers)
            needle_angle = math.degrees(needle_angle_r)
            side_length = needle_length_centers * math.cos(needle_angle_r)
            big_radius_angle = 180 + 2*needle_angle
            small_radius_angle = 180 - 2*needle_angle
            with self.saved_context():
                self.moveTo(0, big_radius, -90 - needle_angle)
                self.corner(big_radius_angle, big_radius)
                self.edge(side_length)
                self.corner(small_radius_angle, small_radius)
                self.edge(side_length)

        tw = big_radius * 2
        th = needle_length
        if self.move(tw, th, move, before=True):
            return

        with self.saved_context():
            drawNeedleShape(needle_length, big_radius, small_radius)
        self.moveTo(big_radius + hole_clearance/2 + 0.25, 10 + hole_clearance, 180)
        drawNeedleShape(10, big_radius=big_radius-hole_clearance, small_radius=0.1)


        self.move(tw, th, move)


    def comb(self, comb_num_pins, loom_pin_width, move=None):

        comb_pin_length = 10
        comb_pin_radius = max(0.5, 0.2*loom_pin_width)
        comb_gap_radius = (loom_pin_width - 2*comb_pin_radius)/2
        comb_handle_radius = 10

        print(comb_pin_radius)
        print(comb_gap_radius)

        tw = comb_pin_length + comb_pin_radius + comb_gap_radius + 2*comb_handle_radius
        th = 2*comb_handle_radius + comb_num_pins*loom_pin_width
        if self.move(tw, th, move, before=True):
            return

        self.moveTo(0, comb_handle_radius, -90)
        self.corner(180, comb_handle_radius)
        for _ in range(comb_num_pins):
            self.corner(-90, comb_gap_radius)
            self.edge(comb_pin_length)
            self.corner(180, comb_pin_radius)
            self.edge(comb_pin_length)
            self.corner(-90, comb_gap_radius)
        self.corner(180, comb_handle_radius)
        self.edge(comb_num_pins * loom_pin_width)

        self.move(tw, th, move)


    def render(self):

        pin_width = self.warpspacing
        foot_attachment_x_offset = 8
        foot_hole_radius = 4.25
        num_warp_threads = self.warpthreads
        outer_frame_length = self.outerframelength
        frame_thickness = 15

        transverse_length = self.warpthreads * pin_width + 2*frame_thickness + 20

        if self.includeframe:
            self.frame(pin_width, num_warp_threads, frame_thickness, outer_frame_length, foot_attachment_x_offset, move="right")
            with self.saved_context():
                self.foot(foot_hole_radius, move="up")
                self.foot(foot_hole_radius, move="up")
                if self.combpins > 0:
                    self.comb(self.combpins, pin_width, move="up")
            self.foot(foot_hole_radius, move="right only")
        else:
            if self.combpins > 0:
                self.comb(self.combpins, pin_width, move="right")

        if self.includeheddle:
            right, left = FrameLoom.heddle_patterns([0,1], num_warp_threads, 1)
            self.heddle(right, left, pin_width, num_warp_threads, foot_attachment_x_offset, foot_hole_radius, move="right")

        if self.include2by2heddle:
            right, left = FrameLoom.heddle_patterns(
                [1,1,0,0], num_warp_threads, 2)
            right_2, left_2 = FrameLoom.heddle_patterns(
                [1,0,0,1], num_warp_threads, 2)
            self.heddle(right, left,
                        pin_width, num_warp_threads, foot_attachment_x_offset, foot_hole_radius,
                        holes=True,
                        move="right")
            self.heddle(right_2, left_2,
                        pin_width, num_warp_threads, foot_attachment_x_offset, foot_hole_radius,
                        handle=False, clipons=True,
                        move="right")

        if self.includediamondheddle:
            pattern_up, pattern_right = FrameLoom.heddle_patterns(
                [0,1,0,0,1,1,1,0], num_warp_threads, 4)
            pattern_down, pattern_left = FrameLoom.heddle_patterns(
                [1,0,1,1,0,0,0,1], num_warp_threads, 4)

            # note: these don't match the original rocketloom version for some reason. Theirs seem to have the
            # following overrides:
            #
            # right[0]  to 1
            # up[0]     to 1
            # down[0]   to 0
            #
            # down[-1]  to 0
            # right[-1] to 1
            #
            # I'm not yet sure why.
            #
            # (order is down, right, up, left)

            self.heddle(pattern_up, pattern_down,
                        pin_width, num_warp_threads, foot_attachment_x_offset, foot_hole_radius,
                        holes=True,
                        move="right")
            self.heddle(pattern_right, pattern_left,
                        pin_width, num_warp_threads, foot_attachment_x_offset, foot_hole_radius,
                        handle=False, clipons=True,
                        move="right")

        if self.includeneedles:
            self.needle(transverse_length, move="right")
            self.needle(50, move="right")

        for _ in range(self.numshuttles):
            self.shuttle(transverse_length, move="right")

    @staticmethod
    def heddle_patterns(seed, length, shift):
        chunks = math.ceil(length / len(seed))
        base = seed * chunks
        up = base[:length]
        down = FrameLoom.rotate(base, shift)[:length]
        return up, down

    @staticmethod
    def rotate(list, n):
        return list[-n:] + list[:len(list)-n]


    # def part_template(self, move=None):
    #     tw = 1
    #     th = 1
    #     if self.move(tw, th, move, before=True):
    #         return
    #     self.move(tw, th, move)


    # def drawCurve(self):
    #     def drawPoint(x, y):
    #         with self.saved_context():
    #             self.moveTo(x, y)
    #             self.corner(360, 0.3)
    #     x1 = 3
    #     y1 = 0
    #     x2 = 1
    #     y2 = 180
    #     x3 = 2
    #     y3 = 180
    #     with self.saved_context():
    #         self.edge(1)
    #     drawPoint(0, 0)
    #     drawPoint(x1, y1)
    #     drawPoint(x2, y2)
    #     drawPoint(x3, y3)
    #     self.curveTo(x1, x2, y1, y2, x3, y3)
