from __future__ import annotations

import sys
from pathlib import Path

import pytest

try:
    import boxes
except ImportError:
    sys.path.append(Path(__file__).resolve().parent.parent.__str__())
    import boxes

from boxes.generators.gridfinitytraylayout import GridfinityTrayLayout
from boxes.generators.traylayout import TrayLayout

LAYOUT = """\
 ,> 50.00mm
 | ,> 50.00mm
 | | ,> 50.00mm
+-+-+-+
| | | |  50.00mm
+-+-+-+
| | | |  50.00mm
+-+-+-+
| | | |  50.00mm
+-+-+-+
"""


def render(box_class, args: list[str]):
    box = box_class()
    box.parseArgs(args)
    box.metadata["reproducible"] = True
    box.open()
    box.render()
    data = box.close().getvalue()
    assert b"<svg" in data
    return box


def test_input_file_is_used_when_layout_is_not_given(tmp_path: Path) -> None:
    layout_file = tmp_path / "layout.txt"
    layout_file.write_text(LAYOUT)

    from_file = render(TrayLayout, ["--sx=50*3", "--sy=50*3", f"--input={layout_file}"])
    from_layout = render(TrayLayout, ["--sx=50*3", "--sy=50*3", f"--layout={LAYOUT}"])

    for attr in ("x", "y", "hwalls", "vwalls", "floors"):
        assert getattr(from_file, attr) == getattr(from_layout, attr)
    assert len(from_file.x) == len(from_file.y) == 3


def test_layout_argument_takes_precedence_over_input_file(tmp_path: Path) -> None:
    layout_file = tmp_path / "layout.txt"
    layout_file.write_text("not a layout\n")

    box = render(TrayLayout, [f"--input={layout_file}", f"--layout={LAYOUT}"])

    assert len(box.x) == len(box.y) == 3


def test_missing_layout_and_input_file_raises(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="requires --layout, --input"):
        render(TrayLayout, [f"--input={tmp_path / 'missing.txt'}"])


def test_gridfinity_generates_layout_when_none_is_given(tmp_path: Path) -> None:
    box = render(GridfinityTrayLayout, ["--h=6u", "--nx=3", "--ny=3", f"--input={tmp_path / 'missing.txt'}"])

    assert len(box.x) >= 1 and len(box.y) >= 1
