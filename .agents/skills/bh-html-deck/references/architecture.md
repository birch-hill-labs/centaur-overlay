# Architecture — the mount/beat/suffix system

## The big idea

One SVG definition. Three live mount points. Independent state per mount.

The SVG is built by `buildBHDiagram(idSuf)` — a function in `diagram.js` that returns the entire SVG as a string with every addressable element's ID suffixed by `idSuf`. Calling it three times with three different suffixes produces three independent DOM copies that don't collide on IDs.

```js
// In controller.js init()
const platformStage = document.getElementById("platform-diagram");
const flowStage     = document.getElementById("flow-diagram");
const modeStage     = document.getElementById("mode-diagram");

if (platformStage) D.platform = { svg: mountDiagram(platformStage, "p") };
if (flowStage)     D.flow     = { svg: mountDiagram(flowStage, "f") };
if (modeStage)     D.mode     = { svg: mountDiagram(modeStage, "m") };
```

After mounting, each `<svg>` has its own copies of every node, edge, marker, gradient — distinguished by the suffix.

## Why suffixes

SVG `id` attributes must be unique within a document. The same SVG mounted three times means the same `id="n-vault1"` would appear three times — invalid. By suffixing (`n-vault1-p`, `n-vault1-f`, `n-vault1-m`), we keep them unique.

The same suffixing applies to:

- All node `id`s and `data-node` attributes
- All edge `<path id="...">` attributes
- All text label `<text id="...">` attributes
- All step badge `<g id="b-step1-p">` attributes
- All dollar callout `<g id="d-step3-p">` attributes
- All group frame `<rect class="group-frame" id="g-engines-p">` attributes
- All defs: `<marker id="arrow-p">`, `<radialGradient id="ringCashGrad-p">`, etc.
- All `url(#...)` references that point at the above

In `diagram.js`, do this with a single helper:
```js
function buildDiagram(idSuf) {
  const s = (n) => `${n}-${idSuf}`;
  return `<svg ...>
    <defs>
      <marker id="arrow-${idSuf}" ...><path d="..."/></marker>
    </defs>
    ${rectNode(s("n-vault1"), ...)}
    ${edge(s("e-wh-v1"), "M...", { suf: idSuf, markerKey: "arrow" })}
  </svg>`;
}
```

The `s()` helper produces the suffixed ID. The `suf` option passed into helpers (like `edge`) lets them construct `marker-end="url(#arrow-${suf})"` correctly.

## The beat system

A **beat** is a snapshot of visual state — which nodes/edges are highlighted, which are dimmed, which step badge is active, which dollar callouts are shown.

```js
const beat = {
  on:      ["n-vault1", "n-facility", "e-v1-facility", "l-v1-facility"],
  dim:     ["n-presec", "n-vault2"],  // explicit dim
  hot:     ["n-cantor"],              // bright green highlight + animated dashes
  pulse:   ["n-qakeeper"],            // brief scale + glow animation
  dollars: ["d-step3"],               // dollar callout visible
  step:    3,                          // which step badge is active
};
```

When a beat is applied:
1. Every `.node` element gets `is-on`, `is-dim`, `is-hot`, or `is-pulse` class based on which set its ID is in
2. Every `.edge` element gets the same treatment
3. Every `.edge-label` element gets the same treatment
4. Every `.group-frame` element gets `is-on` / `is-dim`
5. Every `.step-badge` element with `data-step="N"` gets `is-on` if `N === beat.step`
6. Every `.dollar` element gets `is-on` if its ID is in `beat.dollars`

CSS in `styles.css` defines what those classes mean visually:
```css
.diagram-svg .node { opacity: 0.30; transition: opacity 200ms; }
.diagram-svg .node.is-on { opacity: 1; }
.diagram-svg .node.is-dim { opacity: 0.12; }
.diagram-svg .node.is-on.is-hot .node-fill {
  stroke: var(--bh-primary); stroke-width: 2.5;
  filter: drop-shadow(0 0 14px rgba(0,105,62,0.45));
}
```

The transition makes beat changes animate smoothly.

## Beats are defined without suffixes

In `controller.js`:
```js
B.s1_v1 = {
  on: ["n-warehouse", "n-vault1", "n-facility", "e-wh-v1", "l-wh-v1"],
};
```

When applied to a specific mount, the controller suffixes them via `withSuf()`:
```js
function withSuf(beat, suf) {
  const map = (arr) => (arr || []).map((id) => `${id}-${suf}`);
  return {
    on: map(beat.on), dim: map(beat.dim), hot: map(beat.hot),
    pulse: map(beat.pulse), dollars: map(beat.dollars),
    step: beat.step,
  };
}

applyBeat(D.platform.svg, withSuf(B.s1_v1, "p"));
```

This means **a single beat definition works across all three mount points**. The same `B.step3` beat can run the platform diagram, the flow diagram, and the mode diagram, just by passing different suffixes.

## B.empty as the intro state

The first scrollytelling step typically uses `data-beat="empty"`. If `B.empty = {}` (nothing in any set), every element falls back to CSS baseline opacity — heavily faded.

Instead, put **every main element in `B.empty.on`**. This makes the intro view show the full platform at full brightness. As the user scrolls into specific beats (`s1_v1`), most elements drop out of the `on` set and fade back to baseline, focusing the eye on what the narration is talking about.

```js
B.empty = {
  on: [
    // all nodes
    "n-warehouse", "n-vault1", "n-treas1", "n-facility", /* ...etc */,
    // all edges + labels
    "e-wh-v1", "l-wh-v1", "e-v1-facility", "l-v1-facility", /* ...etc */,
    // all groups
    "g-engines", "g-ops",
    // title labels
    "l-c1-eyebrow", "l-c1-title", "l-c2-eyebrow", "l-c2-title",
  ],
};
```

## Three observer types

**Scrollytelling (IntersectionObserver):** Watches `.scrolly-step[data-beat]` elements. The one currently in view determines the active beat. The `data-target` attribute determines which mount to apply it to (`platform`, `flow`, or `mode`).

**Click handlers:** Role cards (`.role-card[data-role]`), mode buttons (`[data-mode="A"]`), and step rail buttons (`[data-step="3"]`) all dispatch synchronously to `applyBeat()`.

**Section-tracker (IntersectionObserver):** Tracks which top-level section is in view to highlight the corresponding top-nav link.

## Building step beats

For Section 4's 8-step walkthrough, use `buildStep()`:
```js
function buildStep(stepN, hot, dollars) {
  const allOnIds = new Set([...(B.s1_ops.on || []), ...(B.s1_ops.hot || [])]);
  const hotSet = new Set(hot);
  return {
    step: stepN,
    hot: hot,
    dim: [...allOnIds].filter((id) => !hotSet.has(id)),
    dollars: dollars || [],
  };
}

B.step3 = buildStep(3, ["n-vault1", "n-facility", "e-facility-cantor"], ["d-step3"]);
```

This DIMS everything in the full-platform set that isn't hot. So during step 3, every node/edge except the step-3-relevant ones is heavily faded — a spotlight effect.

For Section 3 mode beats, use the same helper with `stepN = null`.
