from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, MutableSequence

from affine import Affine
from boxes.dxf import DXFSurface
from boxes.drawing import SVGSurface

PathLike = MutableSequence[MutableSequence[Any]]


def _text_params() -> dict[str, Any]:
    """Return default text styling for labels in the test path."""
    return {
        "ff": ("sans-serif", False, False),
        "fs": 2.0,
        "lw": 0.0,
        "rgb": (0.0, 0.0, 0.0),
        "align": "middle",
    }


Test_Path: PathLike = [
    # Retangulo 6 x 3
    ["M", 0.0, 0.0],
    ["L", 6.0, 0.0],
    ["C", 6.0, 0.0, 6.0, 0.0, 6.0, 0.0],
    ["L", 6.0, 3.0],
    ["C", 6.0, 3.0, 6.0, 3.0, 6.0, 3.0],
    ["L", 0.0, 3.0],
    ["C", 0.0, 3.0, 0.0, 3.0, 0.0, 3.0],
    ["L", 0.0, 0.0],
    ["C", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    ["T", 3.0, 1.5, Affine.identity(), "1", _text_params()],
    # Circulo de diametro 10 descrito com segmentos cubicos.
    ["M", 18.0, 5.0],
    ["C", 13.0, 10.0, 18.0, 7.761423749153968, 15.761423749153968, 10.0],
    ["C", 8.0, 5.0, 10.238576250846032, 10.0, 8.0, 7.761423749153968],
    ["C", 13.0, 0.0, 8.0, 2.2385762508460325, 10.238576250846032, 0.0],
    ["C", 18.0, 5.0, 15.761423749153968, 0.0, 18.0, 2.2385762508460325],
    ["T", 13.0, 5.0, Affine.identity(), "2", _text_params()],
    # Circulo de diametro 10 descrito com arco.
    ["M", 33.0, 5.0],
    ["A", 33.0, 5.0, 28.0, 5.0, 5.0, 0.0, 6.283185307179586, 1],
    ["T", 28.0, 5.0, Affine.identity(), "3", _text_params()],
    # Segmento: linha 10, curva equivalente ao arco horario, linha 10.
    ["M", 38.0, 5.0],
    ["L", 43.0, 5.0],
    ["C", 48.0, 0.0, 45.76142374915397, 5.0, 48.0, 2.761423749153968],
    ["L", 48.0, -10.0],
    ["T", 45.5, -2.5, Affine.identity(), "4", _text_params()],
    # Loop estilo inner-corner loop.
    ["M", 63.0, 0.0],
    ["L", 73.0, 0.0],
    ["C", 73.0, 0.0, 83.0, 0.0, 73.0, -10.0],
    ["L", 73.0, -20.0],
    ["T", 78.0, -5.0, Affine.identity(), "5", _text_params()],
    # Canto 90 graus com dogbone (D=5).
    ["M", 83.0, 0.0],  # start=(83.0,0.0)
    ["L", 84.25441226126739, 0.0],
    # start=(83.0,0.0) end=(84.25441226126739,0.0)
    ["A", 86.85943917766733, 0.7322330470336311, 84.25441226126739, 5.0, 5.0, -1.5707963267948966, -1.0227679191745838, 1],
    # start=(84.25441226126739,0.0) end=(86.85943917766733,0.7322330470336311)
    ["A", 93.73223304703363, -6.140560822332672, 89.46446609406726, -3.5355339059327373, 5.0, 2.1188247344152096, -0.5480284076203126, -1],
    # start=(86.85943917766733,0.7322330470336311) end=(93.73223304703363,-6.140560822332672)
    ["A", 93.0, -8.745587738732608, 98.0, -8.745587738732608, 5.0, 2.5935642459694805, 3.141592653589793, 1],
    # start=(93.73223304703363,-6.140560822332672) end=(93.0,-8.745587738732608)
    ["L", 93.0, -10.0],
    # start=(93.0,-8.745587738732608) end=(93.0,-10.0)
    ["T", 88.5, -3.0, Affine.identity(), "6", _text_params()],
]


def export_test_path_dxf(
    output: str | Path = "test_path.dxf",
    *,
    inner_corners: str = "loop",
    dogbone_diameter: float | None = None,
) -> Path:
    """Render Test_Path to a DXF file and return the written path."""
    surface = DXFSurface()
    surface.set_metadata(
        {
            "name": "TestPath",
            "short_description": "Sample path for manual testing",
            "description": "",
            "group": "dev",
            "url": "",
            "url_short": "",
            "cli": "",
            "cli_short": "",
            "creation_date": datetime.now(),
            "reproducible": True,
        }
    )

    for cmd in Test_Path:
        surface.append(*cmd)
    surface.stroke(lw=0.1, rgb=(0.0, 0.0, 0.0))

    dogbone_radius = dogbone_diameter / 2.0 if dogbone_diameter else None
    buffer = surface.finish(inner_corners=inner_corners, dogbone_radius=dogbone_radius)

    output_path = Path(output)
    output_path.write_bytes(buffer.getvalue())
    return output_path


def export_test_path_svg(
    output: str | Path = "test_path.svg",
    *,
    inner_corners: str = "loop",
    dogbone_diameter: float | None = None,
) -> Path:
    """Render Test_Path to an SVG file and return the written path."""
    surface = SVGSurface()
    surface.set_metadata(
        {
            "name": "TestPath",
            "short_description": "Sample path for manual testing",
            "description": "",
            "group": "dev",
            "url": "",
            "url_short": "",
            "cli": "",
            "cli_short": "",
            "creation_date": datetime.now(),
            "reproducible": True,
        }
    )

    for cmd in Test_Path:
        surface.append(*cmd)
    surface.stroke(lw=0.1, rgb=(0.0, 0.0, 0.0))

    dogbone_radius = dogbone_diameter / 2.0 if dogbone_diameter else None
    buffer = surface.finish(inner_corners=inner_corners, dogbone_radius=dogbone_radius)

    output_path = Path(output)
    output_path.write_bytes(buffer.getvalue())
    return output_path
