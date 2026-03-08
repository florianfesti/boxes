class Color:
    BLACK   = [ 0.0, 0.0, 0.0 ]
    BLUE    = [ 0.0, 0.0, 1.0 ]
    GREEN   = [ 0.0, 1.0, 0.0 ]
    RED     = [ 1.0, 0.0, 0.0 ]
    CYAN    = [ 0.0, 1.0, 1.0 ]
    YELLOW  = [ 1.0, 1.0, 0.0 ]
    MAGENTA = [ 1.0, 0.0, 1.0 ]
    WHITE   = [ 1.0, 1.0, 1.0 ]

    OUTER_CUT = BLACK
    INNER_CUT = BLUE
    ANNOTATIONS = RED
    ETCHING = GREEN
    ETCHING_DEEP = CYAN
    SOLID_FILL = MAGENTA

    # Human-readable labels and descriptions for the settings UI.
    ROLE_LABELS: dict[str, tuple[str, str]] = {
        "OUTER_CUT":   ("Outer Cut",   "Perimeter cuts – the material contour that falls out."),
        "INNER_CUT":   ("Inner Cut",   "Interior cuts – holes, pockets and slots."),
        "ANNOTATIONS": ("Annotations", "Assembly guides and debug marks – never sent to the laser."),
        "ETCHING":     ("Etching",     "Surface engravings, score numbers and decorative marks."),
        "ETCHING_DEEP":("Deep Etching","Deep engravings that go further into the material surface."),
        "SOLID_FILL":  ("Solid Fill",  "Solid-filled areas used by some generators."),
    }

    @staticmethod
    def from_hex(hex_color: str) -> list[float]:
        """Convert a CSS hex color (#rrggbb) to a [r, g, b] list of floats 0–1."""
        h = hex_color.lstrip("#")
        if len(h) != 6:
            raise ValueError(f"Invalid hex color: {hex_color!r}")
        return [int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4)]

    @staticmethod
    def to_hex(color: list[float]) -> str:
        """Convert a [r, g, b] float list to a CSS hex string (#rrggbb)."""
        return "#{:02x}{:02x}{:02x}".format(
            round(color[0] * 255),
            round(color[1] * 255),
            round(color[2] * 255),
        )

    @classmethod
    def apply_overrides(cls, overrides: dict[str, str]) -> None:
        """Apply a dict of {ROLE_NAME: '#rrggbb'} overrides to the class attributes."""
        for role, hex_val in overrides.items():
            if role in cls.ROLE_LABELS:
                setattr(cls, role, cls.from_hex(hex_val))
