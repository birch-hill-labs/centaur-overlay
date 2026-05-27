---
name: bh-html-deck
description: Use when building an immersive HTML/CSS/JS single-page deck for a Birch Hill client engagement — joint working sessions, pitch decks, platform walkthroughs — typically with scrollytelling, a sticky interactive SVG diagram, mode toggles, or step-by-step flow walkthroughs. Also use when the deliverable is a web-based presentation rather than a .pptx or .pdf, or when the user references the Cantor Fitzgerald deck as a model.
---

# BH HTML Scrollytelling Deck

## Overview

A reproducible pattern for building immersive HTML decks for Birch Hill client engagements. One single-page HTML file, one CSS file (plus brand tokens), one JS file that builds an inline SVG diagram, and one JS controller that wires the diagram into scrollytelling beats, mode toggles, and step rails.

**Core principle:** the diagram is the centerpiece. Everything else is structured narration around it.

The proven reference implementation is the **Cantor Fitzgerald** deck — see `examples/cantor-fitzgerald-paths.md` for the full file list to study before starting a new one.

## When to Use

- Joint working session decks for Birch Hill counterparties (Cantor, Sky, Ethena, Cap, etc.)
- Platform walkthroughs where the user scrolls and the diagram animates / progressively builds
- Anything where a static slide deck would feel less compelling than a scroll-driven experience
- Web-based pitch decks intended to be shared as a URL or screen-shared in a live meeting

**Don't use for:** plain pitch decks (`birch-hill-pptx` skill is faster), reports/memos (`bh-design` skill), spreadsheets, or anything that needs to be printed cleanly.

## File Architecture

Every deck has the same five-file shape:

```
docs/                      # Folder name MUST be docs/ if deploying via GitHub Pages
  <Deck Title>.html        # The deck itself — sections, scrolly narration, role cards
  styles.css               # Layout + animation states for the diagram
  colors_and_type.css      # Birch Hill design tokens (rarely modified per-deck)
  diagram.js               # buildBHDiagram(idSuf) — returns the SVG as a string
  controller.js            # Mounts the SVG up to N times, wires beats / clicks / scroll
  sandbox.js               # Optional — interactive economic modeling section
  index.html               # Optional — redirect to the deck file for clean URLs
  assets/                  # Logos, illustrations, hero background
  fonts/                   # Versailles (display serif), Inter loaded via Google
```

The SVG is **mounted up to three times** with different ID suffixes (`-p` platform, `-f` flow, `-m` mode), so the same diagram can drive three sections simultaneously with different highlight states.

## Core Patterns

| Pattern | What it does |
|---------|--------------|
| **Beat-based state changes** | Controller toggles `is-on` / `is-dim` / `is-hot` / `is-pulse` classes on nodes/edges. CSS handles the visual states. |
| **Scrollytelling** | IntersectionObserver watches narration cards. Each card has `data-beat="s1_v1"` etc.; entering view triggers `applyBeat()` |
| **Mode toggle** | Buttons with `data-mode="A"` swap which beat is applied to the mode-diagram mount |
| **Step rail** | Buttons with `data-step="3"` advance through 8 step-beats in the flow-diagram mount, often with dollar callouts |
| **Role pulse** | Section 2 role cards each pulse their corresponding node when clicked |
| **Color-coded edges** | Blue = cash, gold = securities, green = facility events, purple = collateral / legal plumbing, sage = anchor capital |

## Workflow (in order)

1. **Brief well.** Ask the user about the platform's structure before drawing anything. What are the "verbs"? What's the pivot? What flows are recycling vs one-shot? Don't start the diagram until you have the model in your head.
2. **Sketch the diagram architecture.** Plan node IDs, columns, the pivot, the metaphor (figure-8, hub-and-spoke, linear pipeline, etc.). See `references/diagram-patterns.md`.
3. **Build the SVG via `diagram.js`.** Start from `templates/diagram-skeleton.js`. Use the helper functions (`rectNode`, `circleNode`, `diamondNode`, `edge`, `edgeLabel`, `stepBadge`, `dollarCallout`, `groupFrame`).
4. **Wire the beats in `controller.js`.** Start from `templates/controller-skeleton.js`. Define `B.empty` (everything on), `B.s1_v1`, `B.s1_origination`, etc. progressively, then step beats and mode beats. See `references/architecture.md`.
5. **Fill in the deck HTML.** Start from `templates/deck-skeleton.html`. Hero → Section 1 (scrolly) → Section 1b (benefits) → Section 2 (roles) → Section 3 (modes) → Section 4 (flow) → flywheel callout → footnotes → footer. See `references/section-patterns.md`.
6. **Iterate on the diagram with the user.** This is where most of the work happens. Build a standalone preview HTML file (`diagram-preview.html`) early so you can iterate on the visual without rebuilding the whole deck each time.

## Reference files in this skill

- **`references/architecture.md`** — how the mounting/beat/suffix system works end to end
- **`references/diagram-patterns.md`** — figure-8, pivot circles, color coding, three-column grids
- **`references/section-patterns.md`** — markup for hero, scrolly, role cards, modes, flow rail
- **`references/brand-tokens.md`** — the Birch Hill design tokens and how to use them

## Templates in this skill

- **`templates/deck-skeleton.html`** — section scaffolds with all the right `data-*` attributes
- **`templates/styles-skeleton.css`** — layout + the critical animation states
- **`templates/diagram-skeleton.js`** — all the helper functions, minimal starter SVG
- **`templates/controller-skeleton.js`** — mounting + beat dispatch + observers

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Designing the diagram before understanding the user's model | Brainstorm the verbs and pivot first. Diagrams designed without a model collapse on iteration. |
| Cramming too much into one diagram | Decide whether you need one diagram or two (architectural overview vs. step walkthrough). Don't compromise either by serving both with the same beats. |
| Forgetting to suffix all IDs | Every `id`, every `url(#marker)`, every `<text id>` must be suffixed. Use the `s()` helper consistently. |
| Baseline opacity too high | If `is-on` doesn't visually pop vs baseline, the scrollytelling falls flat. Baseline should be ~0.30 for nodes, ~0.18 for edges. |
| Putting the pivot off-axis | The pivot is the most important node — center it. Break the rectangular grid for it. Make it a circle if everything else is a rectangle. |
| Long curved arrows that cross each other | Reroute through gutters. Use right angles along canvas margins for long-distance arrows (engines → vaults). Pack labels into open space, never inside boxes. |

## Quick Reference — node ID conventions

Use `n-` for nodes, `e-` for edges, `l-` for labels, `b-` for step badges, `d-` for dollar callouts, `g-` for group frames. The controller's `withSuf()` appends the mount suffix at apply time, so define beats with bare IDs (`"n-vault1"`), not suffixed ones.
