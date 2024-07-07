# Copyright (C) 2013-2016 Florian Festi, 2024 marauder37
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
import inspect
import logging
import math
from dataclasses import dataclass, fields

from boxes import BoolArg, Boxes, Color, edges

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


@dataclass
class Dimensions:
    """
    Calculate the dimensions of a photo frame with matting and glass.

    What changes if the user specifies the dimensions of the glass?
    - the matting outer dimension is fixed by the glass instead of calculated out from the photo
    - the matting width and height must be calculated from the photo dimensions
    - so you can't have golden matting or user-specified matting width/height
    """

    x: float
    y: float
    golden_mat: bool
    matting_w_param: float
    matting_h_param: float
    matting_overlap: float
    glass_w: float
    glass_h: float
    frame_w: float
    frame_overlap: float
    split_front_param: bool
    split_middle_param: bool
    guide_fudge: float = 2.0

    def __post_init__(self):
        self.check_matting_params()
        self.check()

    @property
    def photo_x(self):
        """Width of the photo"""
        return self.x

    @property
    def photo_y(self):
        """Height of the photo"""
        return self.y

    @property
    def frame_h(self):
        """
        Width of the top and bottom sections of the framing 'border' formed by the top layer

        I can't think of a reason for this to be different from frame_w, but if you think of one,
        this is where to handle it.
        """

        return self.frame_w

    @property
    def mat_hole_x(self):
        """Width of the hole in the matting that shows the photo"""
        return self.photo_x - 2 * self.matting_overlap

    @property
    def mat_hole_y(self):
        """Height of the hole in the matting that shows the photo"""
        return self.photo_y - 2 * self.matting_overlap

    @property
    def golden_matting_width(self):
        """
        Calculate the width of the matting border that gives a golden ratio for the matting+photo area / photo area
        See e.g. https://robertreiser.photography/golden-ratio-print-borders/
        """

        phi = (1 + math.sqrt(5)) / 2
        a = 4
        x = self.mat_hole_x
        y = self.mat_hole_y
        b = 2 * (x + y)
        c = -(phi - 1) * x * y
        disc = b**2 - 4 * a * c
        x1 = (-b + math.sqrt(disc)) / (2 * a)
        return x1

    @property
    def fixed_glass_size(self) -> bool:
        """
        Whether user has specified the size of the glass, or we should work it out from the photo
        """
        return bool(self.glass_w and self.glass_h)

    @property
    def matting_w(self):
        """
        Width of the visible matting border on the sides of photo, not including the bit that's hidden by the frame
        """

        if self.fixed_glass_size:
            visible = self.glass_w - 2 * self.frame_overlap
            return (visible - self.mat_hole_x) / 2
        if self.golden_mat:
            return self.golden_matting_width
        return self.matting_w_param

    @property
    def matting_h(self):
        """
        Height of the visible matting border on the top and bottom of photo, not including the bit that's hidden by the frame
        """
        if self.fixed_glass_size:
            visible = self.glass_h - 2 * self.frame_overlap
            return (visible - self.mat_hole_y) / 2
        if self.golden_mat:
            return self.golden_matting_width
        return self.matting_h_param

    @property
    def mat_x(self):
        """Width of the matting including the bit that's hidden by the frame"""
        return self.mat_hole_x + 2 * self.matting_w + 2 * self.frame_overlap

    @property
    def mat_y(self):
        """Height of the matting including the bit that's hidden by the frame"""
        return self.mat_hole_y + 2 * self.matting_h + 2 * self.frame_overlap

    @property
    def visible_mat_ratio(self):
        """
        Ratio of the visible matting area to the visible photo area

        For the most aesthetic result, this should be the golden ratio phi ~= 1.618.
        Contrary to popular belief, this is all about the area, not length of side or perimeter.
        """

        visible_mat_area = self.window_x * self.window_y
        visible_photo_area = self.mat_hole_x * self.mat_hole_y
        return visible_mat_area / visible_photo_area

    @property
    def pocket_x(self):
        """Width of the pocket formed by the guide including the fudge"""
        return self.mat_x + self.guide_fudge

    @property
    def pocket_y(self):
        """Height of the pocket formed by the guide including the fudge"""
        return self.base_y - self.guide_h

    @property
    def guide_w(self):
        """Width of the guide that holds the matting and glass in place"""
        return (self.base_x - self.pocket_x) / 2

    @property
    def guide_h(self):
        """Height of the guide that holds the matting and glass in place"""
        return (self.base_y - self.mat_y) / 2

    @property
    def window_x(self):
        """Width of the window that shows the photo"""
        return self.mat_x - self.frame_overlap * 2

    @property
    def window_y(self):
        """Height of the window that shows the photo"""
        return self.mat_y - self.frame_overlap * 2

    @property
    def base_x(self):
        """Width of the base layer, which is also the overall width of the piece"""
        return self.window_x + 2 * self.frame_w

    @property
    def base_y(self):
        """Height of the base layer, which is also the overall height of the piece"""
        return self.window_y + 2 * self.frame_h

    @property
    def centre_x(self):
        """
        Midpoint of the whole frame
        """
        return self.base_x / 2

    @property
    def centre_y(self):
        """
        Midpoint of the whole frame
        """
        return self.base_y / 2

    @property
    def split_middle(self):
        return self.split_middle_param

    @property
    def unsplit_middle(self):
        return not self.split_middle_param

    @property
    def split_front(self):
        return self.split_front_param

    @property
    def unsplit_front(self):
        return not self.split_front_param

    def check_matting_params(self):
        whinge_threshold_mm = 0.5
        if self.golden_mat and self.fixed_glass_size:
            calc = f"Calculated matting width x: {self.matting_w:.1f}, y: {self.matting_h:.1f} for glass {self.glass_w:.1f} x {self.glass_h:.1f}."
            advice = "If you want to specify the glass size, do not use golden matting."
            raise ValueError(f"Cannot have golden matting and fixed glass size at the same time. {calc} {advice}")

        if self.fixed_glass_size and (self.matting_w_param or self.matting_h_param):
            d_w = self.matting_w_param - self.matting_w
            d_h = self.matting_h_param - self.matting_h
            if abs(d_w) > whinge_threshold_mm or abs(d_h) > whinge_threshold_mm:
                msg = f"Calculated matting width {self.matting_w:.1f} differs from specified matting widths {self.matting_w_param:.1f},  {self.matting_h_param:.1f}."
                advice = "If you want to specify the matting widths, set the glass size to zero. If you want to specify the glass size, set the matting widths to 0."
                logger.warning(msg)
                raise ValueError(f"Fixed glass size and explicit matting dimensions are mutually exclusive. {msg} {advice}")

        if self.golden_mat and (self.matting_w_param or self.matting_h_param):
            d_w = self.matting_w_param - self.golden_matting_width
            d_h = self.matting_h_param - self.golden_matting_width
            if abs(d_w) > whinge_threshold_mm or abs(d_h) > whinge_threshold_mm:
                msg = f"Golden matting width {self.golden_matting_width:.1f} differs from specified matting widths {self.matting_w_param:.1f},  {self.matting_h_param:.1f}"
                advice = "If you want to specify the matting width, set the glass size to zero. If you want to specify the glass size, set the matting widths to 0."
                logger.warning(msg)
                raise ValueError(f"Golden matting and explicit matting dimensions are mutually exclusive. {msg} {advice}")

    def check(self):
        photo_info = f"Photo: {self.photo_x:.0f} x {self.photo_y:.0f}"
        mat_hole_info = f"Matting hole: {self.mat_hole_x:.0f} x {self.mat_hole_y:.0f} (O {self.matting_overlap:.0f})"
        matting_w_info = f"Matting widths: {self.matting_w:.0f} sides, {self.matting_h:.0f} top/bottom"
        mat_info = f"Mat size: {self.mat_x:.0f} x {self.mat_y:.0f} (W {self.matting_w:.0f}, H {self.matting_h:.0f})"
        base_info = f"Back of frame: {self.base_x} x {self.base_y} (W {self.frame_w:.0f}, H {self.frame_h:.0f})"
        base_x_info = f"Back of frame x: {self.base_x:.0f} = {self.window_x:.0f} + 2 * ({self.frame_w:.0f} - {self.frame_overlap:.0f})"
        base_y_info = f"Back of frame y: {self.base_y:.0f} = {self.window_y:.0f} + 2 * ({self.frame_h:.0f} - {self.frame_overlap:.0f})"
        window_info = f"Viewing window in front layer: {self.window_x} x {self.window_y} (rim {self.frame_overlap:.0f})"
        pocket_info = f"Pocket for glass and matting: {self.pocket_x:.0f} x {self.pocket_y:.0f} (guide {self.guide_fudge:.0f})"
        if self.fixed_glass_size:
            glass_info = f"Glass size: {self.glass_w:.0f} x {self.glass_h:.0f} (fixed)"
        else:
            glass_info = "Glass size: not specified"
        info = [
            photo_info,
            mat_hole_info,
            matting_w_info,
            glass_info,
            mat_info,
            window_info,
            pocket_info,
            base_info,
            base_x_info,
            base_y_info,
        ]

        issues = []

        for field in fields(self):
            if isinstance(getattr(self, field.name), float):
                v = getattr(self, field.name)
                if v < 0:
                    issues.append(f"{field.name} must be positive")

        # Check all properties
        for name, value in inspect.getmembers(self.__class__, lambda o: isinstance(o, property)):
            prop_value = getattr(self, name)
            if isinstance(prop_value, float):
                if prop_value < 0:
                    issues.append(f"{name} must be positive")

        if issues:
            info_str = "\n".join(info)
            issues_str = "\n".join(issues)
            raise ValueError(f"Invalid dimensions:\n{issues_str}\n{info_str}")


class PhotoFrame(Boxes):
    """
    3-layer photo frame with a slot at the top to slide matboard/acrylic/glass over the photo after glue-up.
    """

    ui_group = "Misc"

    description = """
3-layer photo frame.

Selected excellent features:

* easy to change the photo after glue-up, without disassembling the frame
* calculates the ideal matting size for your photo based on ancient Greek mathematics
* can make the frame in one piece or split into 4 pieces to save material
* can make a frame to fit the piece of glass/acrylic you already have
* adds a hole for hanging the frame on the wall

Features available in the mysterious future:

* rounded corners
* a stand on the back to display the frame on a table

## How to frame things like a pro

There are 1 or 2 things that you can't change when framing: the size of the artwork
and the size of the glass. So we generate everything else to fit those measurements.

Set `x` and `y` to the dimensions of the actual artwork.

* If your photo has a border, measure inside it.
* If your photo does not have a border, still measure the actual artwork. Don't reduce the dimensions to allow for mounting. We do that separately.

A real pro measures the photo, calculates the matting, and cuts the glass to fit the matting.
We will assume that you are not in fact a real pro, and can't be trusted with a glass cutter.
So measure your glass and we'll calculate the matting to suit it. If you aren't using glass,
we'll calculate the matting size based on "golden ratio of areas" like the pros do. Everyone
will think your frame is perfect, but they won't know why.

Matting is just cardboard. Its jobs are to keep the glass off the photo, provide a clean border around the artwork,
and make the whole thing look fancy. You can attach the photo to the matting or to the back of the frame.
Either way, the matting conceals all sorts of sins like bad cuts, glue marks, or mounting with blue painter's tape.
Matting also lets you reuse the frame for different sized photos. Just generate a new mat with the same glass dimensions.

The hole in the matting is smaller than the photo. This is so the photo doesn't fall out.
Even if your photo has a border, the hole needs to be a bit smaller than the photo,
or you will struggle to line up the photo without the edges showing.
Recommended overlaps are given in the settings. Don't worry about "losing" too much of the photo.
The matting will make the photo look bigger and more important. There's never anything
interesting in the last 2mm of a photo anyway.
"""

    x = 100
    y = 150
    golden_mat = True
    matting_w = 0
    matting_h = 0
    matting_overlap = 2
    glass_w = 0
    glass_h = 0
    frame_w = 20.0
    frame_overlap = 5.0
    split_middle = True  # not exposed in the UI
    split_front = True
    mount_hole_dia = 6.0
    guide_fudge = 2.0

    d = None

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.add_arguments()

    def render(self):
        self.d = Dimensions(
            x=self.x,
            y=self.y,
            golden_mat=self.golden_mat,
            matting_w_param=self.matting_w,
            matting_h_param=self.matting_h,
            matting_overlap=self.matting_overlap,
            glass_w=self.glass_w,
            glass_h=self.glass_h,
            frame_w=self.frame_w,
            frame_overlap=self.frame_overlap,
            split_middle_param=self.split_middle,
            split_front_param=self.split_front,
            guide_fudge=self.guide_fudge,
        )

        self.render_base()
        self.render_middle()
        self.render_front()
        self.render_matting()
        self.render_photo()

    def render_middle(self):
        """
        Render the middle layer of the frame, which holds the matting and glass in place

        Local variable `stack_n` is reserved for future use where multiple middle layers
        are needed to hold thicker glass or matting. I have needed this in the past
        but not often enough to add it to the UI.
        """

        stack_n = 1

        if self.d.unsplit_middle:
            for _ in range(stack_n):
                self.middle_unsplit()

        if self.d.split_middle:
            for _ in range(stack_n):
                self.middle_split()

    def middle_split(self):
        lyr = "Middle"
        d = self.d
        edge_types = "DeD"
        edge_lengths = (d.guide_w, d.base_x - 2 * d.guide_w, d.guide_w)
        e = edges.CompoundEdge(self, edge_types, edge_lengths)
        move = "up"
        self.rectangularWall(d.base_x, d.guide_h, ["e", "e", e, "e"], move=move, label=f"{lyr} btm {d.base_x:.0f}x{d.guide_h:.0f}")
        self.rectangularWall(d.pocket_y, d.guide_w, "edee", move=move, label=f"{lyr} side {d.guide_w:.0f}x{d.pocket_y:.0f}")
        self.rectangularWall(d.pocket_y, d.guide_w, "edee", move=move, label=f"{lyr} side {d.guide_w:.0f}x{d.pocket_y:.0f}")

    def middle_unsplit(self):
        lyr = "Middle"
        d = self.d
        dims_str = f"{lyr} {d.base_x:.0f}x{d.base_y:.0f} with pocket {d.pocket_x:.0f}x{d.pocket_y:.0f} for mat {d.mat_x:.0f}x{d.mat_y:.0f}"
        border_str = f"Widths {d.guide_w:.0f}x {d.guide_h:.0f}y x-fudge {d.guide_fudge:.0f}"
        label = f"{dims_str}\n{border_str}"

        # start at bottom left
        poly = [d.base_x, 90, d.base_y, 90, d.guide_w, 90, d.pocket_y, -90, d.pocket_x, -90, d.pocket_y, 90, d.guide_w, 90, d.base_y, 90]
        self.polygonWall(poly, "eeee", move="up", label=label)

    def render_matting(self):
        d = self.d
        dims_str = f"Matting {d.mat_x:.0f}x{d.mat_y:.0f} - {d.mat_hole_x:.0f}x{d.mat_hole_y:.0f} (ratio {d.visible_mat_ratio:.2f})"
        border_str = f"Borders {d.matting_w:.0f}w {d.matting_h:.0f}h"
        overlap_str = f"Overlaps photo {d.matting_overlap:.0f}, frame {d.frame_overlap:.0f}"
        label = f"{dims_str}\n{border_str}\n{overlap_str}"

        callback = [lambda: self.rectangularHole(d.mat_x / 2, d.mat_y / 2, d.mat_hole_x, d.mat_hole_y, r=0.0)]
        self.rectangularWall(d.mat_x, d.mat_y, "eeee", callback=callback, move="right", label=label)

    def golden_matting_width(self, photo_width, photo_height):
        # Calculate the width of the matting border
        phi = (1 + math.sqrt(5)) / 2
        a = 4
        b = 2 * (photo_width + photo_height)
        c = -(phi - 1) * photo_width * photo_height
        disc = b**2 - 4 * a * c
        x1 = (-b + math.sqrt(disc)) / (2 * a)
        return x1

    # Function to display the results
    def display_results(self, photo_width, photo_height, matting_width):
        photo_area = photo_width * photo_height
        photo_perimeter = 2 * (photo_width + photo_height)
        mat_x = photo_width + 2 * matting_width
        mat_y = photo_height + 2 * matting_width
        mat_perimeter = 2 * (mat_x + mat_y)
        total_area = (photo_width + 2 * matting_width) * (photo_height + 2 * matting_width)
        ratio = total_area / photo_area
        diff = total_area - photo_area
        logger.debug(f"\n\nPhoto dims: {photo_width:.0f} x {photo_height:.0f}")
        logger.debug(f"Photo perimeter: {photo_perimeter:.0f}")
        logger.debug(f"Photo area: {photo_area:.0f}")
        logger.debug(f"Mat dims: {mat_x:.0f} x {mat_y:.0f}")
        logger.debug(f"Mat perimeter: {mat_perimeter:.0f}")
        logger.debug(f"Mat area: {diff:.0f}")
        logger.debug(f"Total area: {total_area:.0f}")
        logger.debug(f"Matting width: {matting_width:.1f}")
        logger.debug(f"Ratio: {ratio:.2f}")

    def render_front(self):
        if self.d.unsplit_front:
            self.front_unsplit()

        if self.d.split_front:
            self.front_split()

    def front_unsplit(self):
        lyr = "Front"
        d = self.d
        dims_str = f"{lyr} {d.base_x:.0f}x{d.base_y:.0f} - {d.window_x:.0f}x{d.window_y:.0f}"
        border_str = f"Widths {d.frame_w:.0f}x {d.frame_h:.0f}y {d.frame_overlap:.0f} overlap"
        label = f"{dims_str}\n{border_str}"

        callback = [lambda: self.rectangularHole(d.centre_x, d.centre_y, d.window_x, d.window_y)]
        self.rectangularWall(d.base_x, d.base_y, "eeee", callback=callback, move="up", label=label)

    def front_split(self):
        lyr = "Front"
        d = self.d
        hypo_h = math.sqrt(2 * d.frame_h**2)
        hypo_w = math.sqrt(2 * d.frame_w**2)

        tops = [d.base_x, 90 + 45, hypo_h, 90 - 45, d.base_x - 2 * d.frame_h, 90 - 45, hypo_h, None]
        sides = [d.base_y, 90 + 45, hypo_w, 90 - 45, d.base_y - 2 * d.frame_w, 90 - 45, hypo_w, None]

        for bit in ("top", "btm"):
            label = f"{lyr} {bit} {d.base_x:.0f}x{d.frame_h:.0f}"
            self.polygonWall(tops, "eded", move="up", label=label)

        for bit in "LR":
            label = f"{lyr} side {bit} {d.frame_w:.0f}x{d.base_y:.0f}"
            self.polygonWall(sides, "eDeD", move="up", label=label)

    def render_base(self):
        d = self.d
        label = f"Base {d.base_x:.0f}x{d.base_y:.0f} for photo {d.photo_x:.0f}x{d.photo_y:.0f}"

        callback = [lambda: self.photo_registration_rectangle(), None, None, None]
        holes = self.edgesettings.get("Mounting", {}).get("num", 0)
        self.rectangularWall(d.base_x, d.base_y, "eeGe" if holes else "eeee", callback=callback, move="up", label=label)

        # I can't work out the interface for roundedPlate with edge settings other than "e"
        # so no rounded corners for you!
        # self.roundedPlate(d.base_x, d.base_y, d.corner_radius, "e", callback, extend_corners=False, move="up", label=label)

    def photo_registration_rectangle(self):
        """
        Draw a rectangle with registration marks for the photo
        """

        d = self.d
        self.set_source_color(Color.ETCHING)
        self.rectangular_etching(d.centre_x, d.centre_y, d.photo_x, d.photo_y)
        self.ctx.stroke()

    def rectangular_etching(self, x, y, dx, dy, r=0.0, center_x=True, center_y=True):
        """
        Draw a rectangular etching (from GridfinityTrayLayout.rectangularEtching)
        Same as rectangularHole, but with no burn margin

        :param x: position
        :param y: position
        :param dx: width
        :param dy: height
        :param r:  (Default value = 0) radius of the corners
        :param center_x:  (Default value = True) if True, x position is the center, else the start
        :param center_y:  (Default value = True) if True, y position is the center, else the start
        """

        logger.debug(f"rectangular_etching: {x=} {y=} {dx=} {dy=} {r=} {center_x=} {center_y=}")

        r = min(r, dx / 2.0, dy / 2.0)
        x_start = x if center_x else x + dx / 2.0
        y_start = y - dy / 2.0 if center_y else y
        self.moveTo(x_start, y_start, 180)
        self.edge(dx / 2.0 - r)  # start with an edge to allow easier change of inner corners
        for d in (dy, dx, dy, dx / 2.0 + r):
            self.corner(-90, r)
            self.edge(d - 2 * r)

    def add_arguments(self):
        # landlords seem to love using 8GA screws in masonry sleeves for wall mounts
        self.addSettingsArgs(edges.MountingSettings, num=3, d_head=8.0, d_shaft=4.0)
        self.addSettingsArgs(edges.DoveTailSettings, size=2.0, depth=1.0)
        self.buildArgParser()
        self.argparser.add_argument(
            "--x",
            action="store",
            type=float,
            default=self.x,
            help="Width of the photo, not including any border",
        )
        self.argparser.add_argument(
            "--y",
            action="store",
            type=float,
            default=self.y,
            help="Height of the photo, not including any border",
        )
        self.argparser.add_argument(
            "--golden_mat", action="store", type=BoolArg(), default=self.golden_mat, help="Use golden ratio to calculate matting width"
        )
        self.argparser.add_argument(
            "--matting_w",
            action="store",
            type=float,
            default=self.matting_w,
            help="Width of the matting border around the sides of the photo",
        )
        self.argparser.add_argument(
            "--matting_h",
            action="store",
            type=float,
            default=self.matting_h,
            help="Width of the matting border around top/bottom of the photo",
        )
        self.argparser.add_argument(
            "--matting_overlap",
            action="store",
            type=float,
            default=self.matting_overlap,
            help="Matting overlap of the photo, e.g. 2mm if photo has border, 5mm if not",
        )
        self.argparser.add_argument(
            "--glass_w",
            action="store",
            type=float,
            default=self.glass_w,
            help="Width of the pre-cut glass or acrylic",
        )
        self.argparser.add_argument(
            "--glass_h",
            action="store",
            type=float,
            default=self.glass_h,
            help="Height of the pre-cut glass or acrylic",
        )
        self.argparser.add_argument(
            "--frame_w",
            action="store",
            type=float,
            default=self.frame_w,
            help="Width of the frame border around the matting",
        )
        self.argparser.add_argument(
            "--guide_fudge",
            action="store",
            type=float,
            default=self.guide_fudge,
            help="Clearance in the guide pocket to help slide the matting/glass in",
        )
        self.argparser.add_argument(
            "--frame_overlap",
            action="store",
            type=float,
            default=self.frame_overlap,
            help="Frame overlap to hold the matting/glass in place",
        )
        self.argparser.add_argument(
            "--split_front",
            action="store",
            type=BoolArg(),
            default=self.split_front,
            help="Split front into thin rectangles to save material",
        )

    def render_photo(self):
        d = self.d
        self.set_source_color(Color.ANNOTATIONS)
        label = f"Photo {d.photo_x:.0f}x{d.photo_y:.0f}"
        self.rectangularWall(d.photo_x, d.photo_y, "eeee", label=label, move="up")
        self.set_source_color(Color.BLACK)
