# Custom Fonts for Label Generator

Place `.ttf` or `.otf` font files directly in this folder **or in a
sub-folder** (one sub-folder per font family is recommended).

They will be **automatically discovered** and appear as choices in the
`--font` parameter of the `Label` generator (and any other generator that
calls `self.ctx.set_font()`).

The font will be **embedded as a base64 data URI** inside the SVG output,
so the resulting file is fully self-contained and renders correctly on any
machine or laser-cutter software.

## ⚠️ TTF/OTF mandatory for text-to-path conversion

Every font **must** be present as a `.ttf` or `.otf` file.  The text-to-path
engine (`fontmanager.text_to_svg_path`) uses **fontTools**, which loads TTF/OTF
natively.  Without a plain TTF/OTF the generator silently falls back to a
`<text>` element, which most laser-cutter applications cannot engrave correctly.

If you only have a `.woff2` (e.g. from Google Fonts), convert it once with
fontTools before committing:

```powershell
# PowerShell – convert a single woff2 to ttf
python -c "
from fontTools.ttLib import TTFont
f = TTFont('boxes/fonts/myfont/my-font.woff2')
f.flavor = None   # strip the woff2 wrapper, keep the outlines
f.save('boxes/fonts/myfont/my-font.ttf')
print('Done')
"
```

For a batch conversion of every woff/woff2 in the fonts tree that has no
matching ttf/otf yet:

```powershell
python -c "
from pathlib import Path
from fontTools.ttLib import TTFont

fonts_dir = Path('boxes/fonts')
for src in fonts_dir.rglob('*.woff*'):
    ttf = src.with_suffix('.ttf')
    if not ttf.exists():
        try:
            f = TTFont(str(src))
            f.flavor = None
            f.save(str(ttf))
            print(f'Converted: {ttf}')
        except Exception as e:
            print(f'FAILED {src}: {e}')
"
```

You may keep the original `.woff2` alongside the `.ttf` — it is used for
browser embedding via `@font-face`.  The path engine will automatically prefer
`.ttf` over `.woff2` when both are present.

## ⚠️ Licence requirement (mandatory)

Every font you add **must** include its licence file in the same sub-folder.

| Licence type          | Typical filename       |
|-----------------------|------------------------|
| SIL Open Font Licence | `OFL.txt`              |
| Apache 2.0            | `LICENSE.txt`          |
| Other                 | any clearly named file |

**Do not commit a font without its licence file.**
If you cannot redistribute the font, do not add it here.

## Recommended folder layout

```
boxes/fonts/
    MyFont/
        MyFont-Regular.ttf
        MyFont-Bold.ttf
        OFL.txt          ← licence file (required)
    AnotherFont/
        AnotherFont.otf
        LICENSE.txt      ← licence file (required)
```

## Naming convention

The font name exposed in the UI is derived from the **filename stem**
(not the folder name):

| File                          | UI name          |
|-------------------------------|------------------|
| `MyFont/MyFont-Regular.ttf`   | `MyFont-Regular` |
| `AnotherFont/AnotherFont.otf` | `AnotherFont`    |

## Built-in generic families (always available, no file needed)

| Name         | CSS equivalent                   |
|--------------|----------------------------------|
| `sans-serif` | Helvetica / Arial fallback stack |
| `serif`      | Times New Roman fallback stack   |
| `monospaced` | Courier New fallback stack       |

## Free font sources

- <https://fonts.google.com> (OFL or Apache 2.0)
- <https://www.fontsquirrel.com>
- <https://github.com/google/fonts>
