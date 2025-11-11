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

        # Override the base class default for 'spacing'.
        self.argparser.set_defaults(spacing="2.0")

        # Add settings for FingerJoints, which we will use
        self.addSettingsArgs(edges.FingerJointSettings)

        # Add common parameters
        self.buildArgParser(x=300.0, y=200.0)

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

        # --- THIS IS THE NEW PARAMETER ---
        self.argparser.add_argument(
            "--handle_r", action="store", type=float, default=15.0,
            help="Radius of the top corners of the handle")
        # --- END OF NEW PARAMETER ---

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
        handle_r = self.handle_r # <-- Get the new radius
        thickness = self.thickness
        cup_diameter = self.cup_diameter
        cup_base_diameter = self.cup_base_diameter
        num_drinks = self.num_drinks
        hole_spacing = self.hole_spacing
        handle_slot_width = self.handle_slot_width
        handle_slot_height = self.handle_slot_height

        # --- Handle Width ---
        # The handle must fit *between* the side walls
        handle_width_internal = x - (2 * thickness)

        # --- Sanity Checks ---
        if num_drinks % 2 != 0:
            raise ValueError("Number of drinks must be an even number.")

        total_wall_height = box_h + base_support_h

        if handle_h <= total_wall_height:
            raise ValueError("Handle Height must be greater than Box Height + Base Support Height.")

        # --- Sanity Checks for new radius ---
        if handle_r * 2 > handle_width_internal:
            raise ValueError("Handle Radius is too large for the handle width.")

        if handle_r > (handle_h - total_wall_height):
            raise ValueError("Handle Radius is too large (must be smaller than the upper flat section of the handle).")

        drinks_per_side = num_drinks // 2

        # --- Helper Callbacks for Holes ---

        def add_holes(part_self, hole_diameter):
            # This helper draws TWO rows of holes on a single plate
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

        # Callback for the solid bottom plate
        def bottom_plate_callback(part_edge_num):
            if part_edge_num == 0:
                # Hole pattern must be centered and use the new internal width
                hole_start_x = (x - handle_width_internal) / 2.0
                self.fingerHolesAt(
                    hole_start_x,           # x_start
                    y / 2.0,                # y_pos (center)
                    handle_width_internal,  # length
                    0                       # angle
                )

        # Callback for the Base Support Plate
        def base_support_callback(part_edge_num):
            if part_edge_num == 0:
                # Slot must match the new handle width
                self.rectangularHole(x / 2, y / 2, handle_width_internal, thickness, center_x=True, center_y=True)
                # Add holes for cup bases
                add_holes(self, cup_base_diameter)

        # Callback for the Top Plate
        def top_plate_callback(part_edge_num):
            if part_edge_num == 0:
                # Slot must match the new handle width
                self.rectangularHole(x / 2, y / 2, handle_width_internal, thickness, center_x=True, center_y=True)
                # Add holes for cup tops
                add_holes(self, cup_diameter)

        # --- Part 1: Bottom Plate (Solid) ---
        # Finger joints on all 4 sides
        self.rectangularWall(x, y, edges="ffff", move="up",
                             label="Bottom Plate (Solid)", callback=bottom_plate_callback)

        # --- Part 2: Base Support Plate ---
        # This plate now has joints on all 4 sides to
        # connect to the new "Upper" and "Lower" walls.
        self.rectangularWall(x, y, edges="FFFF", move="up",
                             label="Base Support Plate", callback=base_support_callback)

        # --- Part 3: Top Plate ---
        # All 4 sides are outer finger joints
        self.rectangularWall(x, y, edges="FFFF", move="up",
                             label="Top Plate", callback=top_plate_callback)

        # --- Part 4 & 5: Side Wall LOWERS (x2) ---
        # Height is base_support_h
        # Edges: B, R, T, L -> 'f' 'F' 'F' 'F'
        # 'f' connects to Bottom, 'F's connect to Base Support & Ends
        side_edges_lower = "fFFF"
        self.rectangularWall(x, base_support_h, edges=side_edges_lower, move="up",
                             label="Side Wall Lower")
        self.rectangularWall(x, base_support_h, edges=side_edges_lower, move="up",
                             label="Side Wall Lower")

        # --- Part 6 & 7: Side Wall UPPERS (x2) ---
        # Height is box_h
        # Edges: B, R, T, L -> 'f' 'F' 'f' 'F'
        # 'f' connects to Base Support & Top, 'F's connect to Ends
        side_edges_upper = "fFfF"
        self.rectangularWall(x, box_h, edges=side_edges_upper, move="up",
                             label="Side Wall Upper")
        self.rectangularWall(x, box_h, edges=side_edges_upper, move="up",
                             label="Side Wall Upper")


        # --- Part 8-11: End Wall Half LOWERS (x4) ---
        end_wall_width = (y / 2) - (thickness / 2)
        # Edges: B, R, T, L -> 'f' 'F' 'F' 'F'
        end_edges = "fFFF"
        for _ in range(4):
            self.rectangularWall(end_wall_width, base_support_h, edges=end_edges, move="up",
                                 label="End Wall Half Lower")

        # --- Part 12-15: End Wall Half UPPERS (x4) ---
        # Edges: B, R, T, L -> 'f' 'F' 'F' 'F'
        end_edges = "fFFF"
        for _ in range(4):
            self.rectangularWall(end_wall_width, box_h, edges=end_edges, move="up",
                                 label="End Wall Half Upper")


        # --- Part 16: Center Handle ---
        # This is drawn manually with the new INTERNAL width

        if self.move(handle_width_internal, handle_h, "up", before=True, label="Center Handle"):
            return


        # Add oval hand slot
        handle_slot_y = handle_h - (handle_slot_height / 2) - (thickness * 2)
        # Center the slot within the new handle width
        self.rectangularHole(
            handle_width_internal / 2, handle_slot_y, handle_slot_width, handle_slot_height,
            r=handle_slot_height / 2.0, center_x=True, center_y=True
        )

        # --- Draw the outline ---

        # Bottom edge (finger joints)
        self.edges["f"](handle_width_internal)
        self.corner(90)

        # Right edge (flat) - shortened for radius
        self.edge(handle_h - handle_r)

        # Top-Right rounded corner
        self.corner(90, handle_r)

        # Top edge (flat) - shortened for both radii
        self.edge(handle_width_internal - (2 * handle_r))

        # Top-Left rounded corner
        self.corner(90, handle_r)

        # Left edge (flat) - shortened for radius
        self.edge(handle_h - handle_r)

        self.corner(90)

        # Finish the part
        self.move(handle_width_internal, handle_h, "up", label="Center Handle")
