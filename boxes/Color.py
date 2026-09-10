from dataclasses import dataclass
from random import randint
from typing import Final, ClassVar, Self
from typing import Annotated


@dataclass(frozen=True, slots=True)
class RGB:
    red: Annotated[int, "0–255"]
    green: Annotated[int, "0–255"]
    blue: Annotated[int, "0–255"]

    def __post_init__(self) -> None:
        """Validate value range while runtime."""
        if not (0 <= self.red <= 255):
            raise ValueError("red must be 0–255")
        if not (0 <= self.green <= 255):
            raise ValueError("green must be 0–255")
        if not (0 <= self.blue <= 255):
            raise ValueError("blue must be 0–255")

    @classmethod
    def random(cls) -> Self:
        return cls(
            red=randint(0, 255),
            green=randint(0, 255),
            blue=randint(0, 255),
        )

    def as_css(self) -> str:
        return f"rgb({self.red:.0f},{self.green:.0f},{self.blue:.0f})"

    def as_hex(self) -> str:
        return f"#{self.red:02X}{self.green:02X}{self.blue:02X}"

    def as_float_tuple(self) -> tuple[Annotated[float, "0.0–1.0"], Annotated[float, "0.0–1.0"], Annotated[float, "0.0–1.0"]]:
        return self.red / 255.0, self.green / 255.0, self.blue / 255.0

class ColorPalette:
    BLACK: Final[RGB] = RGB(0, 0, 0)
    BLUE: Final[RGB] = RGB(0, 0, 255)
    CYAN: Final[RGB] = RGB(0, 255, 255)
    GREEN: Final[RGB] = RGB(0, 255, 0)
    MAGENTA: Final[RGB] = RGB(255, 0, 255)
    RED: Final[RGB] = RGB(255, 0, 0)
    WHITE: Final[RGB] = RGB(255, 255, 255)
    YELLOW: Final[RGB] = RGB(255, 255, 0)


class ColorMode:
    # TODO: Make this configurable
    OUTER_CUT: ClassVar[RGB] = ColorPalette.BLACK
    INNER_CUT: ClassVar[RGB] = ColorPalette.BLUE
    ANNOTATIONS: ClassVar[RGB] = ColorPalette.RED
    ETCHING: ClassVar[RGB] = ColorPalette.GREEN
    ETCHING_DEEP: ClassVar[RGB] = ColorPalette.CYAN


class Color(ColorPalette, ColorMode):
    """
    Keep old behavior for existing generators.
    """
