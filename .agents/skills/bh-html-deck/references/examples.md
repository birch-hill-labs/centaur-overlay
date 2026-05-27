# Reference implementations

## Cantor Fitzgerald — the canonical example

Built jointly with Connor in May 2026 over an extended iteration (v1 → v8). The canonical files to study before starting a new deck:

Reference repo: **`birch-hill-labs/cantor-fitzgerald`** (https://github.com/birch-hill-labs/cantor-fitzgerald, internal). The canonical files under `docs/`:

```
docs/
  BH Onchain Origination - Cantor.html    # Full deck — every section pattern used
  styles.css                              # Layout + animation states + responsive breakpoints
  colors_and_type.css                     # Brand tokens (do not modify per-deck)
  diagram.js                              # buildBHDiagram with all helpers + v8 layout
  controller.js                           # Full beat library + observers + section tracking
  sandbox.js                              # Section 5 economic modeling (Strata-aligned math)
  index.html                              # Pages redirect to the deck file

  assets/
    bh-logo-desktop.svg                   # BH desktop logo (leaf + wordmark) — deprecated in hero
    bh-logo-mark.svg                      # BH mark (leaf only) — used in both topnav + hero now
    wordmark-white.svg                    # Tempo wordmark
    mark-white.svg                        # Tempo mark (just "T")
    hero-trees.svg                        # Hero background ornament

  fonts/                                  # Versailles LT Std variants
```

A second working example lives at `birch-hill-labs/fulcrum`. Either is a valid starting point.

## What's worth copying directly

- `styles.css` — every layout + animation state. Copy verbatim, adapt only the hero margins/padding if the new deck has different content density.
- `colors_and_type.css` — never modify per-deck.
- `assets/bh-logo-*.svg`, `wordmark-white.svg`, `mark-white.svg`, `hero-trees.svg` — copy verbatim.

## What's the diagram-specific work

Each new deck needs:

1. **A new `buildDiagram()` body in `diagram.js`** with the new node IDs, layout, and SVG content. Helpers (`rectNode`, `edge`, etc.) stay the same.
2. **A new `B` beat library in `controller.js`** matching the new node IDs. The plumbing (`applyBeat`, `withSuf`, `union`, `buildStep`, the init wiring) stays the same.
3. **New narrative content in the deck HTML.** The section shells stay the same.

## Lessons from the Cantor build that apply to future decks

- **Brainstorm the model before drawing.** Spent 4–5 versions iterating on the diagram layout. Most fixes traced back to a wrong initial mental model (e.g., "Buy Box and SPV are the same thing" vs. "they're two separate entities with different roles").
- **Build a standalone preview first.** `diagram-v2-preview.html` is an inline-SVG version of the diagram for fast iteration without rebuilding the whole deck. Use this from the start.
- **Color-code edges by purpose, not entity.** Blue arrows = cash flowing somewhere. Gold arrows = securities. Doesn't matter which entity is on either end — the *what* of the flow is more important than the *who*.
- **The pivot circle was the breakthrough.** Once Cantor's Balance Sheet became a circle and broke the rectangular grid, the figure-8 metaphor finally landed visually.
- **Dramatic baseline opacity.** Initially baseline was 0.78 — the scrollytelling fell flat because dimmed elements were still too visible. Dropped to 0.30 for nodes, 0.18 for edges. Combined with `B.empty` putting everything on, the contrast became dramatic.
- **Operational infrastructure deserves its own real estate.** Fence and Reporting Dashboard were originally crammed into Circuit 2's bottom row. Pulling them out into a dedicated sidebar made both the circuits and the infra read more clearly.
- **Right-angle paths along canvas margins.** For long routes like Engine 1 → Vault 1 (1100px+), don't use a curve — route along the far-left margin with right angles. Looks intentional and architectural.

## Sister Birch Hill skills

- **`birch-hill-pptx`** — for slide decks (when the deliverable is a .pptx, not a web deck)
- **`bh-design`** — for reports, memos, one-pagers in .docx / .pdf format
- **`birch-hill-vault`** — for vault reads/writes via the obsidian_vault tool (e.g. to ground deck content in atlas YAMLs)

This skill (`bh-html-deck`) is the right pick when **the medium is web** rather than slides or print.
