# boxes/generators/drinkcarrier.py

from boxes import *
import boxes.generators  # Required to access ui_groups_by_name

# --- Drink Carrier Generator ---

class DrinkCarrier(Boxes):
    """
    A carrier for up to X number of drinks (Even Numbers Only) with a central handle.
    Features a double-layer base, rounded handle,
    and fully interlocking joints.
    """

    # Required attributes
    slug = "drinkcarrier"
    name = "Drink Carrier"
    info = "A carrier for up to X number of drinks (Even Numbers Only) with a central handle and double base."

    # Assign to a UI group
    ui_group = "Misc"

    # DEFINE PARAMETERS in __init__
    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser(x=300.0, y=200.0, bottom_edge="hsF", top_edge="Fh")

        # Add our own custom parameters
        self.argparser.add_argument(
            "--box_h", action="store", type=float, default=80.0,
            help="Height from Base Support Plate to Top Plate")
        self.argparser.add_argument(
            "--base_support_h", action="store", type=float, default=20.0,
            help="Height of the bottom cup support plate from the solid base")
        self.argparser.add_argument(
            "--handle_h", action="store", type=float, default=220.0,
            help="Total height of the central handle from the solid base")
        self.argparser.add_argument(
            "--handle_r", action="store", type=float, default=15.0,
            help="Radius of the top corners of the handle")
        self.argparser.add_argument(
            "--cup_diameter", action="store", type=float, default=75.0,
            help="Diameter of the top cup holes")
        self.argparser.add_argument(
            "--cup_base_diameter", action="store", type=float, default=65.0,
            help="Diameter of the bottom support holes")
        self.argparser.add_argument(
            "--num_drinks", action="store", type=int, default=6,
            help="Total number of drinks (must be even)")
        self.argparser.add_argument(
            "--hole_spacing", action="store", type=float, default=90.0,
            help="Horizontal distance between cup centers (X-axis)")
        self.argparser.add_argument(
            "--handle_slot_width", action="store", type=float, default=100.0,
            help="Width of the hand slot")
        self.argparser.add_argument(
            "--handle_slot_height", action="store", type=float, default=30.0,
            help="Height of the hand slot")

    def render(self):
        # Unpack parameters
        x = self.x
        y = self.y
        box_h = self.box_h
        base_support_h = self.base_support_h
        handle_h = self.handle_h
        handle_r = self.handle_r
        thickness = self.thickness
        cup_diameter = self.cup_diameter
        cup_base_diameter = self.cup_base_diameter
        num_drinks = self.num_drinks
        hole_spacing = self.hole_spacing
        handle_slot_width = self.handle_slot_width
        handle_slot_height = self.handle_slot_height

        handle_width_internal = x - (2 * thickness)

        # Total height for the new single-piece walls
        total_wall_height = box_h + base_support_h

        # --- Sanity Checks ---
        if num_drinks % 2 != 0:
            raise ValueError("Number of drinks must be an even number.")
        if handle_h <= total_wall_height:
            raise ValueError("Handle Height must be greater than Box Height + Base Support Height.")
        if handle_r * 2 > handle_width_internal:
            raise ValueError("Handle Radius is too large for the handle width.")
        if handle_r > (handle_h - total_wall_height):
            raise ValueError("Handle Radius is too large.")

        drinks_per_side = num_drinks // 2

        # --- Helper Callbacks for Holes ---
        def add_holes(part_self, hole_diameter):
            total_hole_width = (drinks_per_side - 1) * hole_spacing
            if total_hole_width > (x - hole_diameter):
                print("WARNING: Hole pattern is wider than the box!")

            x_start = (x / 2.0) - (total_hole_width / 2.0)
            y_pos_left = y / 4.0
            y_pos_right = y * 0.75

            for i in range(drinks_per_side):
                hole_x = x_start + (i * hole_spacing)
                part_self.hole(hole_x, y_pos_left, d=hole_diameter)
                part_self.hole(hole_x, y_pos_right, d=hole_diameter)

        # --- Callbacks for Plates ---
        def bottom_plate_callback(part_edge_num):
            if part_edge_num == 0:
                hole_start_x = (x - handle_width_internal) / 2.0
                self.fingerHolesAt(
                    hole_start_x, y / 2.0, handle_width_internal, 0
                )

        def base_support_callback(part_edge_num):
            if part_edge_num == 0:
                self.rectangularHole(x / 2, y / 2, handle_width_internal, thickness, center_x=True, center_y=True)
                add_holes(self, cup_base_diameter)

        def top_plate_callback(part_edge_num):
            if part_edge_num == 0:
                self.rectangularHole(x / 2, y / 2, handle_width_internal, thickness, center_x=True, center_y=True)
                add_holes(self, cup_diameter)

        # --- Callbacks for Full-Height Walls ---

        def side_wall_callback(part_edge_num):
            if part_edge_num == 0:
                # Add horizontal finger slots for the Base Support Plate
                self.fingerHolesAt(0, base_support_h, x, 0)

        def end_wall_callback(part_edge_num):
            if part_edge_num == 0:
                # Add horizontal finger slots for Base Support Plate
                self.fingerHolesAt(0, base_support_h+0.5*thickness, y, 0)
                # Add vertical slot for the Center Handle to pass through
                self.fingerHolesAt(y/2, base_support_h-thickness, box_h, 90)

        # --- Part 1: Bottom Plate (Solid) ---
        self.rectangularWall(x, y, edges="ffff", move="up",
                             label="Bottom Plate (Solid)", callback=bottom_plate_callback)

        # --- Part 2: Base Support Plate ---
        self.rectangularWall(x, y, edges="ffff", move="up",
                             label="Base Support Plate", callback=base_support_callback)

        # --- Part 3: Top Plate ---
        self.rectangularWall(x, y, edges=self.top_edge * 4, move="up",
                             label="Top Plate", callback=top_plate_callback)

        # --- Part 4 & 5: Side Walls (Full Height) (x2) ---
        side_edges = self.bottom_edge + "FfF"
        self.rectangularWall(x, total_wall_height, edges=side_edges, move="up",
                             label="Side Wall", callback=side_wall_callback)
        # --- FIX: Added callback to the second wall ---
        self.rectangularWall(x, total_wall_height, edges=side_edges, move="up",
                             label="Side Wall", callback=side_wall_callback)

        # --- Part 6 & 7: End Walls (Full Height) (x2) ---
        # Replaces the 4 End Wall Halves
        end_edges = self.bottom_edge + "FfF" # Fingers on all 4 sides
        self.rectangularWall(y, total_wall_height, edges=end_edges, move="up",
                             label="End Wall", callback=end_wall_callback)
        self.rectangularWall(y, total_wall_height, edges=end_edges, move="up",
                             label="End Wall", callback=end_wall_callback)

        # --- Part 8: Center Handle ---
        if self.move(x+2*thickness, handle_h, "up", before=True, label="Center Handle"):
            return

        self.moveTo(2*thickness, thickness)
        handle_slot_y = handle_h - (handle_slot_height / 2) - (thickness * 2)
        self.rectangularHole(
            handle_width_internal / 2, handle_slot_y, handle_slot_width, handle_slot_height,
            r=handle_slot_height / 2.0, center_x=True, center_y=True
        )

        self.edges["f"](handle_width_internal)
        self.polyline(0, 90, base_support_h + thickness, -90, thickness, 90)
        self.edges["f"](box_h - thickness)
        self.polyline(0, 90, thickness, -90,
                      handle_h - total_wall_height - handle_r, (90, handle_r),
                      handle_width_internal - (2 * handle_r),
                      (90, handle_r), handle_h - total_wall_height - handle_r,
                      -90, thickness, 90)
        self.edges["f"](box_h  - thickness)
        self.polyline(0, 90, thickness, -90, base_support_h + thickness, 90)

        self.move(x+2*thickness, handle_h, "up", label="Center Handle")
