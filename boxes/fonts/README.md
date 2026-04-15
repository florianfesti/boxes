# Custom Fonts for Label Generator

Place `.ttf` or `.otf` font files directly in this folder **or in a
sub-folder** (one sub-folder per font family is recommended).

They will be **automatically discovered** and appear as choices in the
`--font` parameter of the `Label` generator (and any other generator that
calls `self.ctx.set_font()`).

The font will be **embedded as a base64 data URI** inside the SVG output,
so the resulting file is fully self-contained and renders correctly on any
machine or laser-cutter software.

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
