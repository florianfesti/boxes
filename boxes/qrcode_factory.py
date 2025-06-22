from __future__ import annotations

from decimal import Decimal
from typing import Any, IO

import qrcode.image.base
import qrcode.image.svg


class BoxesQrCodeFactory(qrcode.image.base.BaseImage):
    """
    SVG image builder
    Creates a QR-code image as a SVG document fragment.
    """
    _SVG_namespace = "http://www.w3.org/2000/svg"
    kind = "SVG"
    allowed_kinds = ("SVG",)

    def __init__(self, *args, ctx=None, x: float = 0, y: float = 0, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ctx = ctx
        self.x, self.y = x, y
        # Save the unit size, for example the default box_size of 10 is '1mm'.
        self.unit_size = self.units(self.box_size)

    def drawrect(self, row: float, col: float) -> None:
        self.ctx.rectangle(*self._rect(row, col))
        self._img.append(self._rect(row, col))

    def units(self, pixels: Any, text: bool = True) -> Decimal | str:
        """
        A box_size of 10 (default) equals 1mm.
        """
        units = Decimal(pixels) / 10
        if not text:
            return units
        return f'{units}mm'

    def save(self, stream: IO[bytes], kind: str | None = None) -> None:
        self.check_kind(kind=kind)
        self._write(stream)

    def to_string(self) -> str:
        return f"".join(self._img)

    def new_image(self, **kwargs: Any) -> Any:
        self._img = []  # type: ignore
        return self._img

    def _rect(self, row: float, col: float) -> tuple[float, float, float, float]:
        size = self.box_size / 10
        x = self.x + (row + self.border) * size
        y = self.y + (col + self.border) * size
        return x, y, size, size

    def _write(self, stream) -> None:
        stream.write("".join(self._img))


if __name__ == "__main__":
    import qrcode
    import qrcode.image

    q = qrcode.QRCode(image_factory=BoxesQrCodeFactory, box_size=10)
    q.add_data("hello")
    img = q.make_image(ctx="a context")
    print(img.to_string())
