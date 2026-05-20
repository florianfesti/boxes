# Converting Generator Parameters to Stepper Types

Use `FloatStepper` and `IntStepper` for generator numeric parameters so the web UI gets `- / +` buttons.

## Why use steppers

- Faster tuning in touch UI.
- Fewer typing mistakes for decimal values.
- Better defaults for common units (`mm`, counts, angles).

## Quick migration pattern

```python
from boxes import *
from boxes.args import FloatStepper, IntStepper

class MyGenerator(Boxes):
    my_float: float = 10.0
    my_count: int = 3

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.argparser.add_argument(
            "--my_float",
            action="store",
            type=FloatStepper(0.1),
            default=self.my_float,
            help="Float value [mm]",
        )
        self.argparser.add_argument(
            "--my_count",
            action="store",
            type=IntStepper(1),
            default=self.my_count,
            help="Count value",
        )
```

## Step size recommendations

- `FloatStepper(0.05)` for fit/tolerance values like `play`.
- `FloatStepper(0.1)` for small diameters and holes.
- `FloatStepper(0.5)` for offsets and spacing.
- `FloatStepper(1.0)` for main dimensions (`x`, `y`, `h`, radii).
- `IntStepper(1)` for counts and index-like values.

## Nullable float (`auto`) mode

If a parameter supports `None` (`auto` in UI), use:

```python
score_radius: float | None = None

self.argparser.add_argument(
    "--score_radius",
    action="store",
    type=FloatStepper(0.5, auto_default=10.0, auto=True),
    default=self.score_radius,
    help="Label radius [mm] (auto = derive from geometry)",
)
```

Notes:

- `auto=True` renders an `auto` button.
- Clicking `auto` writes `"auto"`; converter returns `None`.
- Keep the class stub typed as `float | None`.

## Using `stepper=True` in `buildArgParser`

For the standard box dimensions (`x`, `y`, `h`, `hi`) pass `stepper=True` to
`buildArgParser` instead of registering them manually:

```python
class MyGenerator(Boxes):
    x: float = 100.0
    y: float = 80.0
    h: float = 50.0

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.buildArgParser(x=self.x, y=self.y, h=self.h, outside=True, stepper=True)
        # custom params still use add_argument as usual
        self.argparser.add_argument(
            "--my_param",
            action="store",
            type=FloatStepper(0.1),
            default=10.0,
            help="Custom param [mm]",
        )
```

- `stepper=True` wraps `x`, `y`, `h`, `hi` with `FloatStepper(1.0)` automatically.
- All other params (`sx`/`sy`/`sh`, `outside`, `nema_mount`, …) are unaffected.
- No need to import `FloatStepper` / `IntStepper` just for the standard dimensions.

## One-file conversion checklist

1. For standard dims (`x`, `y`, `h`, `hi`): add `stepper=True` to `buildArgParser` — done.
2. For custom params: add stepper imports from `boxes.args`.
3. Replace each `type=float` with `FloatStepper(step)`.
4. Replace each `type=int` with `IntStepper(1)` (or another integer step).
5. Keep `boolarg`, `str`, and custom types unchanged.
6. Run mypy on touched generator files.
7. Regenerate the touched generator reference SVG.
8. Run `tests/test_svg.py`.
9. Run `pre-commit run --all-files`.
