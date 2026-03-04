# GitHub Copilot Instructions – boxes-acatoire

> These instructions apply to every file in this repository.
> Read them fully before suggesting, editing, or generating any code.

---

## 1. Project Overview

**Boxes.py** is a Python library and web application that generates parametric
SVG cutting plans for laser cutters. Each *generator* is a Python class that
inherits from `boxes.Boxes` and produces an SVG file composed of:

- **Cut paths** (laser cuts through the material)
- **Engraved paths** (laser marks on the surface)
- **Annotations** (assembly guides, never sent to the laser)

The project is pure Python (≥ 3.10). The main entry points are:

- `scripts/boxes` – CLI tool
- `scripts/boxesserver` – web server (Gunicorn / Flask-like)
- `boxes/generators/` – all generator classes, auto-discovered

---

## 2. Code Style & Quality Gate

### ⚠️ Always run before committing

```bash
pre-commit run --all-files
```

This single command runs **all** automated checks listed below.
Never skip it. CI (`precommit.yml`) will block the PR otherwise.

### What pre-commit enforces

| Hook                          | What it checks                                             |
|-------------------------------|------------------------------------------------------------|
| `trailing-whitespace`         | No trailing spaces                                         |
| `end-of-file-fixer`           | Files end with a single newline                            |
| `check-yaml` / `check-toml`   | Valid YAML / TOML syntax                                   |
| `check-added-large-files`     | No accidental binary blobs                                 |
| `python-use-type-annotations` | No old-style type comments                                 |
| `pyupgrade --py310-plus`      | Modern Python 3.10+ syntax                                 |
| `autoflake`                   | No unused imports                                          |
| `mypy`                        | Full static type checking on all `boxes/*.py` files        |
| `rstcheck`                    | Valid RST in docs                                          |
| `shellcheck`                  | Valid shell scripts                                        |
| `codespell`                   | No spelling mistakes (ignores `locale/`, `po/`, `static/`) |
| `pytest`                      | Full test suite must pass                                  |

### mypy configuration

- Configured in `pyproject.toml` under `[tool.mypy]`.
- `ignore_missing_imports = true` – third-party stubs are not required.
- `strict_bytes = true`, `strict_equality = true`.
- All new code in `boxes/` **must** be fully type-annotated.
- Use `from __future__ import annotations` at the top of every new file.
- Method signatures must include return types, e.g. `def render(self) -> None:`.

### Python version target

- Minimum: **Python 3.10** (`--py310-plus` in pyupgrade).
- Use `match` / `case`, `X | Y` union types, `list[T]` / `dict[K, V]` built-in
  generics (not `List`, `Dict` from `typing`).

---

## 3. Writing a New Generator

### File location & naming

```
boxes/generators/<snake_case_name>.py   # one file per generator
```

The class name must be `CamelCase` and match the file name semantically.
File names starting with `_` are ignored by the auto-discovery mechanism.

### Mandatory skeleton

Start from `boxes/generators/_template.py`. Every generator **must** have:

```python
from __future__ import annotations
from boxes import *  # imports Boxes, edges, parts, Color, math, etc.


class MyGenerator(Boxes):
    """One-line description shown in the web UI."""

    ui_group = "Misc"  # see boxes/generators/__init__.py for valid groups

    description = """
Optional longer Markdown/RST description shown below the form.
Include assembly instructions, tips, images references here.
"""

    def __init__(self) -> None:
        Boxes.__init__(self)
        # Add edge settings if needed:
        # self.addSettingsArgs(edges.FingerJointSettings, finger=1.0, space=1.0)
        self.argparser.add_argument(
            "--my_param", action="store", type=float, default=10.0,
            help="Description shown in the web UI [mm]")

    def render(self) -> None:
        # All drawing happens here.
        pass
```

### Valid `ui_group` values

| Value           | Shown as                          |
|-----------------|-----------------------------------|
| `"Box"`         | Boxes                             |
| `"FlexBox"`     | Boxes with flex                   |
| `"Tray"`        | Trays and Drawer Inserts          |
| `"Shelf"`       | Shelves                           |
| `"WallMounted"` | Wall Mounted                      |
| `"Holes"`       | Hole patterns                     |
| `"Part"`        | Parts and Samples                 |
| `"Misc"`        | Miscellaneous                     |
| `"Unstable"`    | Unstable – use for WIP generators |

### Parameters

- Use `self.buildArgParser(x=100, y=100, h=100, ...)` for standard box
  dimensions (x, y, h, hi, sx, sy, outside, …).
- Add custom parameters via `self.argparser.add_argument(...)`.
- Always provide sane metric defaults (mm).
- Access parsed values in `render()` via `self.my_param`.
- **Never hard-code dimensions** – use parameters.

---

## 4. Drawing API – Key Methods

All methods below are available on `self` inside any generator.

### Shapes

```python
# Circular disc (Piece B of a circular assembly)
self.parts.disc(diameter, hole=0.0, dwidth=1.0, callback=None, move="")

# Ring segment
self.parts.ringSegment(r_outside, r_inside, angle, n=1, move="")

# Wavy / concave knob edge
self.parts.wavyKnob(diameter, n=20, angle=45, hole=0, move="")
self.parts.concaveKnob(diameter, n=3, rounded=0.2, hole=0, move="")

# Full circle cut
self.circle(x, y, r)

# Rounded rectangular plate
self.roundedPlate(x, y, r, edges="eeee", move="")
```

### Holes (always drawn in `Color.INNER_CUT`)

```python
self.hole(x, y, r=0.0, d=0.0)  # circular hole
self.rectangularHole(x, y, dx, dy, r=0)  # rectangular hole with optional corner radius
self.dHole(x, y, r=None, d=None, rel_w=0.75, angle=0)  # D-shaped shaft hole
```

### Edges & polylines

```python
self.edge(length)  # straight line
self.corner(angle, radius=0)  # arc or sharp corner
self.polyline(*args)  # alternating lengths and angles
# e.g.: self.polyline(10, 90, 10, 90, 10, 90, 10, 90)
```

### Walls (finger-joint boxes)

```python
self.rectangularWall(x, h, edges="ffff", move="right", label="")
self.polygonWall(corners, edges="e", move="")
```

### Context & transforms

```python
self.moveTo(x, y, angle=0)  # move current position
with self.saved_context():  # isolate transforms / color changes
    ...
```

### Text & colors

```python
# Switch laser color for the next strokes
self.set_source_color(Color.ETCHING)

# Draw engraved text
self.text("Hello", x=0, y=0, angle=0, align="middle center",
          fontsize=10, color=Color.ETCHING, font="Arial")
```

### Color convention (never deviate from this)

| Constant             | RGB             | Laser use                           |
|----------------------|-----------------|-------------------------------------|
| `Color.OUTER_CUT`    | black `#000000` | Perimeter cuts – material falls out |
| `Color.INNER_CUT`    | blue `#0000ff`  | Interior cuts – holes, pockets      |
| `Color.ETCHING`      | green `#00ff00` | Surface engravings, numbers, marks  |
| `Color.ETCHING_DEEP` | cyan `#00ffff`  | Deep engravings                     |
| `Color.ANNOTATIONS`  | red `#ff0000`   | Debug / assembly guides only        |

### Layout helpers

```python
# Place multiple identical parts in a grid
self.partsMatrix(n, cols, direction, method, *args, **kwargs)

# move parameter controls part placement:
# "right"      → move right after drawing
# "up"         → move up after drawing
# "up only"    → move up but don't draw
# "right only" → move right but don't draw
# ""           → draw in place, don't move
```

### Gears

```python
self.gears(teeth=20, dimension=2.0, angle=20, internal_ring=False,
           spoke_width=5, mount_hole=6, profile_shift=20, move="up")
pitch, size, _ = self.gears.sizes(teeth=20, dimension=2.0, ...)
```

---

## 5. Testing a Generator

### Automatic test discovery

Every generator with a `render()` that works with **default parameters** is
automatically tested by `tests/test_svg.py::TestSVG::test_default_generator`.

The test:

1. Instantiates the generator, calls `parseArgs("")`, then `render()`.
2. Checks the output is valid XML.
3. **Compares byte-for-byte** against the reference SVG in `examples/`.

### Adding / updating the reference SVG

After writing or changing a generator, always regenerate its example:

```bash
boxes --examples                # regenerates all examples/
git add -f examples/MyGenerator.svg
```

For generators with non-default test args, add an entry to `examples.yml`:

```yaml
- box_type: MyGenerator
  args:
    my_param: 42.0
    outer_radius: 60
```

The test suite will create a hash-suffixed file: `examples/MyGenerator_<hash8>.svg`.

### Custom generator path (development)

```bash
export BOXES_GENERATOR_PATH=/path/to/my/generators
```

---

## 6. Running the Project

### Local web server

```bash
scripts/boxesserver
# → http://localhost:4455
```

### Docker (recommended for full environment)

```bash
docker-compose up
# → http://localhost:4455  (hot-reload enabled)
```

### CLI

```bash
boxes MyGenerator --my_param=42 --thickness=3 --output=out.svg
```

---

## 7. Adding Dependencies

Adding a dependency requires updating **all** of these files:

1. `requirements.txt`
2. `pyproject.toml` (under `[project]` or `[project.optional-dependencies]`)
3. `documentation/src/install.rst`
4. Relevant files in `documentation/src/install/`
5. `scripts/Dockerfile`

Avoid new dependencies unless strictly necessary.

---

## 8. Documentation

- Docs live in `documentation/src/` and are built with **Sphinx**.
- Generator docstrings are auto-extracted – keep them accurate and complete.
- Build locally: `cd documentation/src && make html`
- Output: `documentation/build/html/`
- RST syntax is linted by `rstcheck` (via pre-commit).
- Ignored words for `codespell` are in `pyproject.toml` under `[tool.codespell]`.

---

## 9. Git Workflow

- **Fork → feature branch → PR** (never commit directly to `master`).
- One generator or feature per branch.
- Squash/rebase before PR: `git rebase -i`.
- PR description must state the current status and intentions.
- CI runs on every push to `master` and every PR:
    - `precommit.yml` → pre-commit + pytest (Python 3.10 and 3.14)
    - `pages.yml` → Sphinx docs build + deploy to GitHub Pages
    - `docker-publish.yml` → Docker image build

---

## 10. Providing Photos / Sample Images

- File: `static/samples/<GeneratorName>.jpg` (CamelCase, 1200 px wide, ~square)
- Compress with [TinyPNG](https://tinypng.com/) first.
- Run `cd scripts && ./gen_thumbnails.sh` to create thumbnails.
- Commit: `static/samples/<GeneratorName>*.jpg` + `static/samples/samples.sha256`.

---

## 11. Project-specific Conventions

- **No `print()` or `logging.warn()`** in generator code – pre-commit blocks both.
  Use `logging.warning()` if needed (also blocked in generators – tests assert
  zero stdout/stderr).
- **No `eval()`** anywhere – `python-no-eval` hook enforces this.
- **Type annotations are mandatory** on all public methods and functions.
- **GPL-3.0-or-later header** must be present in every new `.py` file:

  ```python
  # Copyright (C) <year> <author>
  #
  #   This program is free software: you can redistribute it and/or modify
  #   it under the terms of the GNU General Public License as published by
  #   the Free Software Foundation, either version 3 of the License, or
  #   (at your option) any later version.
  #   ...
  ```

- **`thickness`** is always available as `self.thickness` (set at parse time,
  not a constructor argument).
- **Burn compensation** is available as `self.burn` – use it when computing
  geometry that must be exact (e.g. `r - self.burn` for hole radii).
- **`@restore` decorator** (from `boxes`) wraps drawing methods that should not
  change the global coordinate system.
- **`@holeCol` decorator** automatically switches color to `INNER_CUT` for
  hole-drawing methods.
