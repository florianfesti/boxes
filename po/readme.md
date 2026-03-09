# Translation files

## Overview

This directory contains the gettext translation files for Boxes.py.

| File                                       | Purpose                                                              |
|--------------------------------------------|----------------------------------------------------------------------|
| `boxes.py.pot`                             | Master template – all translatable strings extracted from the source |
| `<lang>.po`                                | Human-readable translations for each language                        |
| `../locale/<lang>/LC_MESSAGES/boxes.py.mo` | Compiled binary loaded by the server at runtime                      |

Supported languages: `de` (German), `en` (English), `fr` (French), `zh_CN` (Simplified Chinese).

---

## ⚠️ Zanata is dead – do not use it

The original workflow relied on **Zanata** as an online translation platform.
**Zanata has been unmaintained since August 2018** and the platform is no longer
operational – the website does not respond and the project repository
(`github.com/zanata/zanata-platform`) has been archived.

> Do **not** use `zanata-cli push` / `zanata-cli pull`.
> All translation work is now done directly in the `.po` files in this directory.

---

## How to update translations

### 1 – Regenerate the `.pot` template after source changes

Run this from the repo root whenever you add or change a user-visible string
(generator description, argparse `help=`, UI label in `boxesserver.py`,
color role label in `Color.py`, …):

```powershell
python scripts/boxes2pot po/boxes.py.pot
```

`boxes2pot` instantiates every generator, reads their argparsers, and also
calls `readServerStrings()` to capture UI strings from the web server and
`Color.ROLE_LABELS`.

### 2 – Merge new strings into every `.po` and recompile `.mo`

```powershell
python scripts/update_po.py
```

This script:

- Parses the freshly generated `boxes.py.pot`
- Adds any missing `msgid` entries (with empty `msgstr ""`) to each `.po`
- Recompiles every `.mo` binary under `locale/`
- Prints a summary: `+N new strings | translated/total | .mo written`

### 3 – Fill in the translations

Open the relevant `.po` file (e.g. `po/fr.po`) and fill in the `msgstr` for
every entry where it is empty. Each block looks like:

```po
#. color role label for OUTER_CUT
#: boxes/Color.py
msgid "Outer Cut"
msgstr "Découpe extérieure"
```

### 4 – Recompile after editing a `.po`

```powershell
python scripts/update_po.py
```

Run this again so the `.mo` files pick up the new `msgstr` values.
The server reads the `.mo` at startup – restart it to see the changes.

---

## Adding a new language

1. Copy an existing `.po` as a starting point:
   ```powershell
   Copy-Item po\en.po po\es.po
   ```
2. Edit the header in `po/es.po` (language code, team, etc.).
3. Add `"es"` to the `LANGUAGES` tuple in `scripts/update_po.py`.
4. Run `python scripts/update_po.py` to compile the `.mo`.

---

## Quick-reference cheat sheet

```powershell
# Full workflow after touching any source string:
python scripts/boxes2pot po/boxes.py.pot
python scripts/update_po.py
# Edit po/<lang>.po to fill msgstr values
python scripts/update_po.py   # recompile .mo
```
