# game_counter_circular – Design Specification

> Status: **Definition / pre-coding phase**
> File: `boxes/generators/game_counter_circular.py`

---

## 1. Concept Overview

A physical, laser-cut **point counter** for board games.
Two flat circular discs are stacked concentrically and held together with
small neodymium cylinder magnets so they can **rotate freely** against each
other without falling apart.

The user rotates the inner disc relative to the outer ring to count
points **up or down**.

---

## 2. Physical Description

### Piece A — Outer Ring (the "frame")

```
        ┌──────────────────────────┐
        │   0   1   2   3  ...  20 │  ← score numbers engraved on inner edge
        │  ┌────────────────────┐  │
        │  │   (inner cutout)   │  │
        │  └────────────────────┘  │
        │  ● ●     magnets     ● ● │  ← magnet pockets near inner edge
        └──────────────────────────┘
```

- Full disc with a **circular cutout** in the center → a ring shape.
- **Score numbers / tick marks** engraved (ETCHING) around the inner edge at
  regular angular intervals on the visible face.
- **Magnet pockets** (INNER_CUT) placed symmetrically near the inner edge of
  the ring.
- Outer profile cut in OUTER_CUT color.

### Piece B — Inner Disc (the "dial")

```
        ┌─────────────────────┐
        │          ▲          │  ← pointer/arrow etched at 0°
        │        ●   ●        │  ← magnet pockets (matching Piece A)
        │    ●           ●    │
        │        ( O )        │  ← optional thumb grip hole
        └─────────────────────┘
```

- Solid disc whose radius is slightly **smaller** than the cutout in Piece A
  (gap = `play` parameter + kerf compensation).
- An **indicator arrow / triangle** etched (ETCHING) at one point on the
  circumference → the player reads the score off Piece A.
- **Matching magnet holes** on the top face so Piece A snaps onto Piece B.
- Optional **central thumb-grip hole** for easy spinning.
- Outer profile cut in OUTER_CUT color.

---

## 3. Assembly

1. Insert magnets into the pockets of **Piece B** (inner disc).
2. Place **Piece A** (outer ring) on top, aligning the magnet pockets.
3. Magnets hold the stack together while still allowing free rotation.
4. Rotate **Piece B** to count up / down — the pointer reads against the
   numbers on the fixed ring.

---

## 4. Laser Color Convention

| Color            | Hex      | Usage in this generator                      |
|------------------|----------|----------------------------------------------|
| `OUTER_CUT` (black) | `#000000` | Perimeter cuts — outer ring profile, disc outline |
| `INNER_CUT` (blue)  | `#0000ff` | Interior cuts — magnet pockets, center hole  |
| `ETCHING` (green)   | `#00ff00` | Score numbers, tick marks, pointer arrow     |
| `ANNOTATIONS` (red) | `#ff0000` | Debug / alignment guides only (not printed)  |

> **Note:** The provided `simple-counter.svg` reference already uses:
> - Red strokes for outer/cut paths
> - Blue fills for engraved glyphs (score numbers around the ring)
>
> This maps directly to the boxes `INNER_CUT` (blue) and `OUTER_CUT` (black/red)
> convention. The blue number glyphs in the SVG confirm that numbers are
> **engraved**, not cut through.

---

## 5. Parameters

| Argument           | Type  | Default | Description                                      |
|--------------------|-------|---------|--------------------------------------------------|
| `--outer_radius`   | float | 60      | Total outer radius of the counter [mm]           |
| `--inner_radius`   | float | 40      | Radius of the inner disc / center cutout [mm]    |
| `--magnet_diameter`| float | 6       | Diameter of cylindrical magnets [mm]             |
| `--magnet_height`  | float | 2       | Depth of magnet pocket [mm]                      |
| `--magnet_count`   | int   | 4       | Number of magnets, evenly spaced angularly       |
| `--score_min`      | int   | 0       | Minimum score value displayed on the ring        |
| `--score_max`      | int   | 20      | Maximum score value displayed on the ring        |
| `--play`           | float | 0.3     | Radial gap between ring cutout and disc [mm]     |
| `--font_size`      | float | 5       | Font size for score numbers [mm]                 |
| `--pointer_size`   | float | 4       | Height of the pointer triangle on Piece B [mm]   |
| `--thumb_hole`     | float | 0       | Diameter of optional center thumb-grip hole [mm] |

> `outer_radius` must be > `inner_radius` + material thickness for a valid ring.
> `inner_radius` must be > `magnet_diameter/2` + margin.

---

## 6. SVG Analysis (simple-counter.svg reference)

The provided reference SVG (`simple-counter.svg`, ~44 × 94 mm) contains:

| Element                         | Color / style      | Interpretation                            |
|---------------------------------|--------------------|-------------------------------------------|
| Large outer circle (r ≈ 22 mm)  | Red stroke, no fill | Outer perimeter cut of the ring           |
| Curved arrow path               | Red stroke, no fill | Cut-through arrow-shaped cutout or guide  |
| Two small circles (r = 2 mm)    | Red stroke          | Small cut indicators / pivot markers      |
| Many small filled paths         | Blue fill, no stroke | Engraved score glyphs (numbers/letters)  |

**Key conclusions:**
- The counter fits in ~44 mm diameter → maps to `outer_radius ≈ 22 mm`.
- Blue filled glyphs are the **score indicators** engraved onto the disc.
- The red arrow-shaped path suggests a **pointer or directional marker**
  that is cut through or very deeply engraved.
- The two small red circles at the edges of the arrow are likely
  **registration / alignment holes**.

---

## 7. Boxes Library Tools Mapping

| Need                          | Boxes tool / method                                  |
|-------------------------------|------------------------------------------------------|
| Outer disc shape (Piece B)    | `self.parts.disc(diameter, hole=0, move=...)`        |
| Ring shape (Piece A)          | `self.circle()` for outer + `self.hole()` for inner  |
| Magnet pockets                | `self.hole(x, y, d=magnet_diameter)` with INNER_CUT  |
| Score numbers (engraved)      | `self.text(str(n), x, y, angle, color=Color.ETCHING)`|
| Tick marks                    | `self.edge(length)` after `self.moveTo()` + rotation |
| Pointer arrow on Piece B      | `self.polyline(...)` drawn in ETCHING color          |
| Switch laser color            | `self.set_source_color(Color.X)`                     |
| Polar placement of items      | `self.moveTo(0,0, angle)` + `self.moveTo(r, 0)`      |
| Context isolation per item    | `with self.saved_context(): ...`                     |
| Side-by-side piece layout     | `move="right"` on first piece call                   |

---

## 8. Method Plan

```
GameCounterCircular
├── __init__()
│     └── argparser for all parameters above
│
├── outerRing(move, label)
│     ├── draw outer circle (OUTER_CUT)
│     ├── draw inner hole / cutout (INNER_CUT)
│     ├── for each score value: place number via text() (ETCHING)
│     ├── draw tick marks at each angular step (ETCHING)
│     └── place magnet holes near inner edge (INNER_CUT)
│
├── innerDisc(move, label)
│     ├── draw disc outer circle (OUTER_CUT)
│     ├── draw pointer/arrow at 0° (ETCHING)
│     ├── place matching magnet holes (INNER_CUT)
│     └── optional thumb grip hole at center (INNER_CUT)
│
└── render()
      ├── outerRing(move="right", label="Piece A – Outer Ring")
      └── innerDisc(move="right", label="Piece B – Inner Disc")
```

---

## 9. Open Questions / Future Iterations

- [ ] Should the numbers go on **Piece A** (outer, fixed) or **Piece B** (inner, rotating)?
      Current decision: **Piece A** (outer ring) carries the numbers so the
      scale is always visible; the player rotates **Piece B** (the dial).
- [ ] Tick mark style: short lines only, or number + tick?
- [ ] Score range 0–20 or configurable asymmetric range (e.g. −10 to +20)?
- [ ] Multiple layers: engrave numbers vs cut-through window in ring to see
      numbers printed on a lower layer?
- [ ] Should the pointer be a cut-through notch on Piece B or an etched mark?
- [ ] Add locking detents (small teeth between ring and disc for haptic clicks)?
- [ ] Magnet pocket depth: full thickness (cut-through) vs half (pocket)?
      → Half-depth pocket requires Z-control on laser — cut-through is simpler.
- [ ] Provide example output SVG in `examples/` once first render is working.
