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
import math
from functools import partial

from boxes import *
from boxes import lids


class GridfinityBase(Boxes):
    """A parameterized Gridfinity base"""

    description = """This is a configurable gridfinity base.  This
    design is based on
    <a href="https://www.youtube.com/watch?app=desktop&v=ra_9zU-mnl8">Zach Freedman's Gridfinity system</a>"""

    ui_group = "Tray"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.DoveTailSettings, size=3, depth=.3, radius=.05, angle=40)
        self.addSettingsArgs(edges.FingerJointSettings, space=4, finger=4)
        self.addSettingsArgs(lids.LidSettings)
        self.argparser.add_argument("--sx", type=int, default=0, help="size of base in X direction (0=auto)")
        self.argparser.add_argument("--sy", type=int, default=0, help="size of base in Y direction (0=auto)")
        self.argparser.add_argument("--x", type=int, default=3, help="number of grids in X direction (0=auto)")
        self.argparser.add_argument("--y", type=int, default=2, help="number of grids in Y direction (0=auto)")
        self.argparser.add_argument("--h", type=float, default=7*3, help="height of sidewalls of the tray (mm)")
        self.argparser.add_argument("--m", type=float, default=0.5, help="Extra margin around the gridfinity base to allow it to drop into the carrier (mm)")
        self.argparser.add_argument(
            "--bottom_edge", action="store",
            type=ArgparseEdgeType("Fhse"), choices=list("Fhse"),
            default='F',
            help="edge type for bottom edge")
        self.argparser.add_argument("--pitch", type=int, default=42, help="The Gridfinity pitch, in mm.  Should always be 42.")
        self.argparser.add_argument("--opening", type=int, default=38, help="The cutout for each grid opening.  Typical is 38.")
        self.argparser.add_argument("--radius", type=float, default=1.6, help="The corner radius for each grid opening.  Typical is 1.6.")
        self.argparser.add_argument("--cut_pads", type=boolarg, default=False, help="cut pads to be used for gridinity boxes from the grid openings")
        self.argparser.add_argument("--cut_pads-mag-diameter", type=float, default=6.5, help="if pads are cut add holes for magnets. Typical is 6.5, zero to disable,")
        self.argparser.add_argument("--cut_pads-mag-offset", type=float, default=7.75, help="if magnet hole offset from pitch corners.  Typical is 7.75.")
        self.argparser.add_argument("--pad-radius", type=float, default=0.8, help="The corner radius for each grid opening.  Typical is 0.8,")
        self.argparser.add_argument("--panel-x", type=int, default=0, help="the maximum sized panel that can be cut in x direction")
        self.argparser.add_argument("--panel-y", type=int, default=0, help="the maximum sized panel that can be cut in y direction")


    def generate_grid(self, nx, ny, shift_x=0, shift_y=0):
        radius, pad_radius = self.radius, self.pad_radius
        pitch = self.pitch
        opening = self.opening

        for col in range(nx):
            for row in range(ny):
                lx = col*pitch+pitch/2 + shift_x
                ly = row*pitch+pitch/2 + shift_y

                self.rectangularHole(lx, ly, opening, opening, r=radius)
                if self.cut_pads:
                    self.rectangularHole(lx, ly, opening - 2, opening - 2, r=pad_radius)

                    if self.cut_pads_mag_diameter > 0:
                        # create a shorter variable names for use in the loop
                        ofs = self.cut_pads_mag_offset 
                        dia = self.cut_pads_mag_diameter
                        for xoff, yoff in ((1,1), (-1,1), (1,-1), (-1,-1)):
                            x = lx+((pitch // 2)-ofs)*xoff
                            y = ly+((pitch // 2)-ofs)*yoff
                            self.hole(x, y, d=dia)

    def subdivide_grid(self, X, Y, A, B):
        # Calculate the number of subdivisions needed in each dimension
        num_x = math.ceil(X / A)
        num_y = math.ceil(Y / B)
        
        # Compute balanced segment sizes
        segment_widths = [X // num_x] * num_x
        for i in range(X % num_x):  # Distribute remainder
            segment_widths[i] += 1
        
        segment_heights = [Y // num_y] * num_y
        for i in range(Y % num_y):  # Distribute remainder
            segment_heights[i] += 1
        
        # Generate the subdivisions
        grid_segments = {}
        y_start = 0
        row_index = 0 # Start from bottom row
        for h in segment_heights:
            x_start = 0
            col_index = 0  # Start from left column
            for w in segment_widths:
                grid_segments[(col_index, row_index)] = (x_start, y_start, w, h)
                x_start += w
                col_index += 1
            y_start += h
            row_index += 1  
        
        return len(segment_widths), len(segment_heights), grid_segments

    def render(self):
        if self.x == 0 and self.sx == 0:
            raise ValueError('either --sx or --x must be provided')
        if self.y == 0 and self.sy == 0:
            raise ValueError('either --sy or --y must be provided')

        if self.sx == 0:
            # if we are producting a minimally sized base sx will be zero
            self.sx = self.x*self.pitch
        else:
            if self.x == 0:
                # if we are producing an automatically determined maximum
                # number of grid cols self.x will be zero
                self.x = int(self.sx / self.pitch)
            # if both sx and x were provided, x takes precedence
            self.sx = max(self.sx, self.x*self.pitch)

        if self.sy == 0:
            # if we are producting a minimally sized base sy will be zero
            self.sy = self.y*self.pitch
        else:
            if self.y == 0:
                # if we are producing an automatically determined maximum
                # number of grid rows self.y will be zero
                self.y = int(self.sy / self.pitch)
            # if both sy and y were provided, y takes precedence
            self.sy = max(self.sy, self.y*self.pitch)
        
        opening = self.opening
        margin = self.m

        t = self.thickness
        self.sx += 2*margin
        self.sy += 2*margin
        
        if self.panel_x != 0 and self.panel_y != 0:
            self.render_split(self.sx, self.sy, self.h, self.x, self.y, self.pitch)
        else:
            self.render_unsplit(self.sx, self.sy, self.h, self.x, self.y, self.pitch)

    def render_split(self, x, y, h, nx, ny, pitch):
        """
        x : base width in mm
        y : base height in mm
        h : box wall height
        nx : number of gridfinity holes in x axis
        ny : number of gridfinity holes in y axis
        pitch : space between gridfinity holes
        """
        pad_x = self.sx - (nx * pitch)
        pad_y = self.sy - (ny * pitch)
        # compute maximum number of grids in each panel
        panel_nx = (self.panel_x // pitch)
        panel_ny = (self.panel_y // pitch)

        # Sub-divide the larger Grid into approximately equal sized segments
        # in both X and Y direction, not exceeding the provided panel size
        segments_cols, segments_rows, segments = self.subdivide_grid(nx, ny, panel_nx, panel_ny)

        # Render the primary grid
        for row in range(segments_rows):
            t0 = "e" if row == 0 else "d"
            t2 = "e" if row == segments_rows - 1 else "D"

            segment_pad_bottom, segment_pad_top = 0, 0
            if (row == 0):
                segment_pad_bottom = pad_y // 2
            if (row == segments_rows - 1):
                segment_pad_top = pad_y // 2
            
            with self.saved_context():
                for col in range(segments_cols):
                    nx, ny = segments[(col, row)][2:4]
                    t1 = "e" if col == segments_cols - 1 else "d"
                    t3 = "e" if col == 0 else "D"

                    segment_pad_left, segment_pad_right = 0, 0
                    if (col == 0):
                        segment_pad_left = pad_x // 2
                    if (col == segments_cols - 1):
                        segment_pad_right = pad_x // 2
                    
                    box_width = nx * self.pitch + segment_pad_left + segment_pad_right
                    box_height = ny * self.pitch + segment_pad_bottom + segment_pad_top

                    self.rectangularWall(
                        box_width,
                        box_height,
                        [t0, t1, t2, t3],
                        callback=[
                            partial(
                                self.generate_grid,
                                nx, ny,
                                segment_pad_left,
                                segment_pad_bottom
                            )
                        ]
                    )
                    self.rectangularWall(
                        box_width,
                        box_height,
                        [t0, t1, t2, t3],
                        move="right only",
                        label=str((row, col))
                    )
            self.rectangularWall(
                box_width,
                box_height,
                [t0, t1, t2, t3],
                move="up only",
                label=str((row, col))
            )

        # If requested, render the walls and floor
        if h > 0:
            t1, t2, t3, t4 = "eeee"
            b = self.edges.get(self.bottom_edge, self.edges["F"])
            sideedge = "F" # if self.vertical_edges == "finger joints" else "h"
            
            # Render walls in x direction
            for ii in range(2):
                resets = []
                for col in range(segments_cols):
                    nx, ny = segments[(col, 0)][2:4]
                    segment_pad_left, segment_pad_right = 0, 0
                    if (col == 0):
                        segment_pad_left = pad_x // 2
                    if (col == segments_cols - 1):
                        segment_pad_right = pad_x // 2
                    box_width = nx * self.pitch + segment_pad_left + segment_pad_right

                    if (col == 0):
                        ee = [b, "f", "e", "f"]
                    elif (col == (segments_cols-1)):
                        ee = [b, "f", "e", "F"]
                    else:
                        ee = [b, "f", "e", "F"]
                    
                    self.rectangularWall(box_width, h, ee,
                                        ignore_widths=[1, 6], move="right")
                    resets.append((box_width, ee))
                
                for width, ee in resets:
                    self.rectangularWall(width, 0, ee,
                                        ignore_widths=[1, 6], move="left only")
                    
                self.rectangularWall(self.sx, h, ee,
                                        ignore_widths=[1, 6], move="up only")
                
            # Render walls in y direction
            self.moveTo(self.sx + h*2, -(self.sy+h*2+self.thickness*2), 90)
            for ii in range(2):
                for row in range(segments_rows):
                    nx, ny = segments[(0, row)][2:4]
                    segment_pad_bottom, segment_pad_top = 0, 0
                    if (row == 0):
                        segment_pad_bottom = pad_y // 2
                    if (row == segments_rows - 1):
                        segment_pad_top = pad_y // 2
                    box_height = ny * self.pitch + segment_pad_bottom + segment_pad_top

                    if (row == 0):
                        ee = [b, "f", "e", "F"]
                    elif (row == (segments_rows-1)):
                        ee = [b, "F", "e", "F"]
                    else:
                        ee = [b, "f", "e", "F"]
                    self.rectangularWall(box_height, h, ee, 
                                        ignore_widths=[1, 6], move="right")
                    
                                    
                    #self.rectangularWall(box_height, h, [b, sideedge, t3, "f"],
                    #                    ignore_widths=[1, 6], move="left only")

                    #self.rectangularWall(box_height, h, [b, sideedge, t3, "f"],
                    #                    ignore_widths=[1, 6], move="down")
                    
                self.moveTo(-self.sy-h-self.thickness, -h-self.thickness*2)    

            # Render the floor, if requested
            self.moveTo(0, 0, -90)
            if self.bottom_edge != "e":
                # TODO - figure out how to make the dovetail different for the bottom panel
                for row in range(segments_rows):
                    t0 = "f" if row == 0 else "d"
                    t2 = "f" if row == segments_rows - 1 else "D"

                    segment_pad_bottom, segment_pad_top = 0, 0
                    if (row == 0):
                        segment_pad_bottom = pad_y // 2
                    if (row == segments_rows - 1):
                        segment_pad_top = pad_y // 2
                    
                    with self.saved_context():
                        for col in range(segments_cols):
                            nx, ny = segments[(col, row)][2:4]
                            t1 = "f" if col == segments_cols - 1 else "d"
                            t3 = "f" if col == 0 else "D"

                            segment_pad_left, segment_pad_right = 0, 0
                            if (col == 0):
                                segment_pad_left = pad_x // 2
                            if (col == segments_cols - 1):
                                segment_pad_right = pad_x // 2
                            
                            box_width = nx * self.pitch + segment_pad_left + segment_pad_right
                            box_height = ny * self.pitch + segment_pad_bottom + segment_pad_top

                            self.rectangularWall(
                                box_width,
                                box_height,
                                [t0, t1, t2, t3],
                            )
                            self.rectangularWall(
                                box_width,
                                box_height,
                                [t0, t1, t2, t3],
                                move="right only",
                                label=str((row, col))
                            )
                    self.rectangularWall(
                        box_width,
                        box_height,
                        [t0, t1, t2, t3],
                        move="up only",
                        label=str((row, col))
                    )

        # TODO - Lid not supported in split mode
        # self.lid(x, y)

    def render_unsplit(self, x, y, h, nx, ny, pitch):
        """
        x : base width in mm
        y : base height in mm
        h : box wall height
        nx : number of gridfinity holes in x axis
        ny : number of gridfinity holes in y axis
        pitch : space between gridfinity holes
        """
        t1, t2, t3, t4 = "eeee"
        b = self.edges.get(self.bottom_edge, self.edges["F"])
        sideedge = "F" # if self.vertical_edges == "finger joints" else "h"

        shift_x = (self.sx - (nx * pitch)) // 2
        shift_y = (self.sy - (ny * pitch)) // 2

        self.rectangularWall(
            self.sx,
            self.sy,
            move="up",
            callback=[partial(self.generate_grid, nx, ny, shift_x, shift_y)]
        )
        
        if h > 0:
            self.rectangularWall(x, h, [b, sideedge, t1, sideedge], 
                                ignore_widths=[1, 6], move="right")
            self.rectangularWall(y, h, [b, "f", t2, "f"],
                                ignore_widths=[1, 6], move="up")
            self.rectangularWall(y, h, [b, "f", t4, "f"],
                                ignore_widths=[1, 6], move="")
            self.rectangularWall(x, h, [b, sideedge, t3, sideedge],
                                ignore_widths=[1, 6], move="left up")

            if self.bottom_edge != "e":
                self.rectangularWall(x, y, "ffff", move="up")

        self.lid(x, y)
