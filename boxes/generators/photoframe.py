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

import logging
import math
from dataclasses import dataclass, fields

from boxes import BoolArg, Boxes, Color, edges

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


@dataclass
class Dimensions:
    x: float
    y: float
    golden_mat: bool
    matting_w_param: float
    matting_h_param: float
    matting_overlap: float
    frame_w: float
    frame_h: float
    frame_overlap: float
    split_parts: bool
    unsplit_parts: bool
    mount_hole_dia: float
    corner_radius: float
    guide_fudge: float = 2.0

    def __post_init__(self):
        if not self.unsplit_parts and not self.split_parts:
            self.unsplit_parts = True

        if self.golden_mat and (self.matting_w_param or self.matting_h_param):
            raise ValueError("Golden matting and explicit matting dimensions are mutually exclusive")
        self.check()

    @property
    def photo_x(self):
        return self.x

    @property
    def photo_y(self):
        return self.y

    @property
    def mat_hole_x(self):
        return self.photo_x - 2 * self.matting_overlap

    @property
    def mat_hole_y(self):
        return self.photo_y - 2 * self.matting_overlap

    @property
    def golden_matting_width(self):
        # Calculate the width of the matting border
        # that gives a golden ratio for the matting+photo area / photo area
        # see e.g. https://robertreiser.photography/golden-ratio-print-borders/

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
    def matting_w(self):
        if self.golden_mat:
            return self.golden_matting_width
        return self.matting_w_param

    @property
    def matting_h(self):
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
        return self.mat_x - self.frame_overlap * 2

    @property
    def window_y(self):
        return self.mat_y - self.frame_overlap * 2

    @property
    def base_x(self):
        return self.window_x + 2 * self.frame_w

    @property
    def base_y(self):
        return self.window_y + 2 * self.frame_h

    @property
    def centre_x(self):
        return self.base_x / 2

    @property
    def centre_y(self):
        return self.base_y / 2

    def check(self):
        photo_info = f"Photo: {self.photo_x:.0f} x {self.photo_y:.0f}"
        mat_hole_info = f"Matting hole: {self.mat_hole_x:.0f} x {self.mat_hole_y:.0f} (O {self.matting_overlap:.0f})"
        mat_info = f"Matting: {self.mat_x:.0f} x {self.mat_y:.0f} (W {self.matting_w:.0f}, H {self.matting_h:.0f})"
        base_info = f"Base: {self.base_x} x {self.base_y} (W {self.frame_w:.0f}, H {self.frame_h:.0f})"
        base_x_info = f"Base x: {self.base_x:.0f} = {self.window_x:.0f} + 2 * ({self.frame_w:.0f} - {self.frame_overlap:.0f})"
        base_y_info = f"Base y: {self.base_y:.0f} = {self.window_y:.0f} + 2 * ({self.frame_h:.0f} - {self.frame_overlap:.0f})"
        window_info = f"Window: {self.window_x} x {self.window_y} (rim {self.frame_overlap:.0f})"

        for field in fields(self):
            logger.debug(f"{field.name}: {getattr(self, field.name)}")
            if isinstance(getattr(self, field.name), float):
                v = getattr(self, field.name)
                if v < 0:
                    raise ValueError(f"{field.name} must be positive")

        for info in (photo_info, mat_hole_info, mat_info, window_info, base_info, base_x_info, base_y_info):
            logger.debug(info)


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
    
    Features available in the mysterious future:
    
    * add a hole for hanging the frame on the wall
    * rounded corners (works now on selected layers)
    * calculate the frame size based on the piece of glass/acrylic you already have
    * determine the width of the internal area based on the thickness of the matting and glass
    """

    x = 100 / 2
    y = 150 / 2
    golden_mat = True
    matting_w = 0
    matting_h = 0
    matting_overlap = 2
    frame_w = 20.0
    frame_h = 20.0
    frame_overlap = 5.0
    unsplit_parts = True
    split_parts = True
    mount_hole_dia = 6.0
    corner_radius = 0.0
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
            frame_w=self.frame_w,
            frame_h=self.frame_h,
            frame_overlap=self.frame_overlap,
            split_parts=self.split_parts,
            unsplit_parts=self.unsplit_parts,
            corner_radius=self.corner_radius,
            mount_hole_dia=self.mount_hole_dia,
            guide_fudge=self.guide_fudge,
        )

        self.render_base()
        self.render_middle()
        self.render_top()
        self.render_matting()
        self.render_photo()

    def render_middle(self):
        d = self.d
        stack_n = 1

        if d.unsplit_parts:
            for _ in range(stack_n):
                self.middle_unsplit()

        if d.split_parts:
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

    def render_top(self):
        if self.d.unsplit_parts:
            self.front_unsplit()

        if self.d.split_parts:
            self.front_split()

    def front_unsplit(self):
        lyr = "Front"
        d = self.d
        dims_str = f"{lyr} {d.base_x:.0f}x{d.base_y:.0f} - {d.window_x:.0f}x{d.window_y:.0f}"
        border_str = f"Widths {d.frame_w:.0f}x {d.frame_h:.0f}y {d.frame_overlap:.0f} overlap"
        label = f"{dims_str}\n{border_str}"

        r = d.corner_radius

        if r:
            centre_x = d.centre_x - r
            callback = [lambda: self.rectangularHole(centre_x, d.centre_y, d.window_x, d.window_y, r=r)]
            self.roundedPlate(d.base_x, d.base_y, r, "e", callback=callback, extend_corners=False, move="up", label=label)
        else:
            callback = [lambda: self.rectangularHole(d.centre_x, d.centre_y, d.window_x, d.window_y, r=r)]
            self.rectangularWall(d.base_x, d.base_y, "eeee", callback=callback, move="up", label=label)

    def front_split(self):
        lyr = "Front"
        d = self.d

        edge_lengths = (d.frame_w, d.base_x - 2 * d.frame_w, d.frame_w)
        e = edges.CompoundEdge(self, "DeD", edge_lengths)

        side_h = d.base_y - 2 * d.frame_h
        move = "up"
        self.rectangularWall(d.base_x, d.frame_h, ["e", "e", e, "e"], move=move, label=f"{lyr} btm {d.base_x:.0f}x{d.frame_h:.0f}")
        self.rectangularWall(side_h, d.frame_w, "eded", move=move, label=f"{lyr} side {d.frame_w:.0f}x{side_h:.0f}")
        self.rectangularWall(side_h, d.frame_w, "eded", move=move, label=f"{lyr} side {d.frame_w:.0f}x{side_h:.0f}")
        self.rectangularWall(d.base_x, d.frame_h, [e, "e", "e", "e"], move=move, label=f"{lyr} top {d.base_x:.0f}x{d.frame_h:.0f}")

    def render_base(self):
        d = self.d
        label = f"Base {d.base_x:.0f}x{d.base_y:.0f} for photo {d.photo_x:.0f}x{d.photo_y:.0f}"
        callback = [lambda: self.photo_registration_rectangle(offset=1)]
        self.roundedPlate(d.base_x, d.base_y, d.corner_radius, "e", callback, extend_corners=False, move="up", label=label)

    def photo_registration_rectangle(self, offset=0):
        """
        Draw a rectangle with registration marks for the photo

        :param offset:  (Default value = 0) sequence number, used to trick roundedPlate into drawing it in the right place
        """

        d = self.d
        r = d.corner_radius

        self.set_source_color(Color.ETCHING)
        rect_x = d.base_x / 2
        rect_y = d.base_y / 2
        if offset == 1:
            rect_x = (d.base_x - r * 2) / 2  # center, but not including the radius
        elif offset == 2:
            rect_y = (d.base_y - r * 2) / 2

        self.rectangular_etching(rect_x, rect_y, d.photo_x, d.photo_y, r=0.0)
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
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.DoveTailSettings, size=2.0, depth=1)
        self.buildArgParser(x=self.x, y=self.y)
        self.argparser.add_argument(
            "--golden_mat", action="store", type=BoolArg(), default=self.golden_mat, help="Use golden ratio to calculate matting width"
        )
        self.argparser.add_argument(
            "--matting_w",
            action="store",
            type=float,
            default=self.matting_w,
            help="Width of the matting border around the photo",
        )
        self.argparser.add_argument(
            "--matting_h",
            action="store",
            type=float,
            default=self.matting_h,
            help="Height of the matting border around the photo",
        )
        self.argparser.add_argument(
            "--matting_overlap",
            action="store",
            type=float,
            default=self.matting_overlap,
            help="Matting overlap of the photo, e.g. 2mm if photo has border, 5mm if not",
        )
        self.argparser.add_argument(
            "--frame_w",
            action="store",
            type=float,
            default=self.frame_w,
            help="Width of the frame border around the matting",
        )
        self.argparser.add_argument(
            "--frame_h",
            action="store",
            type=float,
            default=self.frame_h,
            help="Height of the frame border around the matting",
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
            "--corner_radius",
            action="store",
            type=float,
            default=self.corner_radius,
            help="Radius of the corners of the frame",
        )
        self.argparser.add_argument(
            "--split_parts",
            action="store",
            type=BoolArg(),
            default=self.split_parts,
            help="Split frame and guides into thin rectangles to save material",
        )
        self.argparser.add_argument(
            "--unsplit_parts", action="store", type=BoolArg(), default=self.unsplit_parts, help="Cut frame and guides as one piece"
        )
        # self.argparser.add_argument(
        #     "--mount_hole_dia",
        #     action="store",
        #     type=float,
        #     default=self.mount_hole_dia,
        #     help="Diameter of the mounting hole (TODO)",
        # )

    def render_photo(self):
        d = self.d
        self.set_source_color(Color.ANNOTATIONS)
        label = f"Photo {d.photo_x:.0f}x{d.photo_y:.0f}"
        self.rectangularWall(d.photo_x, d.photo_y, "eeee", label=label, move="up")
        self.set_source_color(Color.BLACK)
