from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree

import pytest

from boxes.generators.gridfinitytraylayout import GridfinityTrayLayout
from boxes.generators.traylayout import TrayLayout


LAYOUT = """ ,> 50.00mm
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


@pytest.mark.parametrize("generator", [TrayLayout, GridfinityTrayLayout])
@pytest.mark.parametrize("explicit_input", [False, True])
def test_layout_from_file(generator, explicit_input, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout_file = tmp_path / ("custom.txt" if explicit_input else "traylayout.txt")
    layout_file.write_text(LAYOUT)
    box = generator()
    box.parseArgs([f"--input={layout_file}"] if explicit_input else [])
    box.open()
    box.render()
    assert len(box.x) == 3
    assert len(box.y) == 3
    assert box.hwalls == [[True] * 3 for _ in range(4)]
    assert box.vwalls == [[True] * 4 for _ in range(3)]


def test_traylayout_input_cli(tmp_path):
    layout_file = tmp_path / "layout.txt"
    layout_file.write_text(LAYOUT)
    output_file = tmp_path / "tray.svg"
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, str(root / "scripts" / "boxes"), "TrayLayout",
         "--sx=50*3", "--sy=50*3", f"--input={layout_file}",
         f"--output={output_file}"],
        cwd=tmp_path, env={**os.environ, "PYTHONPATH": str(root)},
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert ElementTree.parse(output_file).getroot().tag == "{http://www.w3.org/2000/svg}svg"


@pytest.mark.parametrize("generator", [TrayLayout, GridfinityTrayLayout])
def test_explicit_layout_takes_precedence(generator, tmp_path):
    layout_file = tmp_path / "invalid.txt"
    layout_file.write_text("not a layout")
    box = generator()
    box.parseArgs([f"--input={layout_file}", f"--layout={LAYOUT}"])
    box.open()
    box.render()
    assert len(box.x) == len(box.y) == 3


@pytest.mark.parametrize("generator", [TrayLayout, GridfinityTrayLayout])
def test_invalid_explicit_layout_is_not_ignored(generator, tmp_path):
    layout_file = tmp_path / "valid.txt"
    layout_file.write_text(LAYOUT)
    box = generator()
    box.parseArgs([f"--input={layout_file}", "--layout=not a layout"])
    box.open()
    with pytest.raises(ValueError, match="Need more than one wall in x direction"):
        box.render()


def test_gridfinity_generated_layout(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    box = GridfinityTrayLayout()
    box.parseArgs([])
    box.open()
    box.render()
    assert len(box.x) == box.countx
    assert len(box.y) == box.county


@pytest.mark.parametrize("generator", [TrayLayout, GridfinityTrayLayout])
def test_web_layout_default_is_preserved(generator, monkeypatch):
    monkeypatch.setattr(generator, "UI", "web")
    box = generator()
    box.parseArgs([])
    assert box.layout == "\n"
    assert not hasattr(box, "input")
    box.parseArgs([f"--layout={LAYOUT}"])
    box.open()
    box.render()
    assert len(box.x) == len(box.y) == 3


def test_traylayout_missing_input(tmp_path):
    box = TrayLayout()
    box.parseArgs([f"--input={tmp_path / 'missing.txt'}"])
    box.open()
    with pytest.raises(RuntimeError, match="traylayout requires"):
        box.render()
