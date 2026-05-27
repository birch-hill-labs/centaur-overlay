# Diagram patterns

## When to reach for the figure-8

The Cantor diagram uses two tangent ellipses meeting at a single circle (Cantor's Balance Sheet). This works specifically when:

- The platform has **two distinct circuits** that share a node
- The shared node has narrative weight (loans are born in one circuit, consumed by another)
- The two circuits have different "kinds" of flow (cash vs. securities)

If the platform is more of a **pipeline** (linear flow from intake → underwriting → settlement → distribution), use a linear layout instead. If it's **hub-and-spoke** (one central operator with many counterparty arms), use a radial layout. Don't force the figure-8 if the model doesn't actually have two loops.

**Figure-8 math:** Top ellipse `cy + ry = pivot_y`. Bottom ellipse `cy - ry = pivot_y`. The two ellipses tangent at exactly one point — the pivot center. The pivot circle sits on top of that tangent point.

```
Top ellipse: cx=600, cy=395, rx=560, ry=310 → bottom edge at y=700
Pivot:       cx=600, cy=700, r=85
Bottom:      cx=600, cy=985, rx=580, ry=285 → top edge at y=700
```

Use radial gradients to give the ellipses subtle fills (blue tint for the cash ring, gold tint for the securities ring). The gradients have low opacity (0.07–0.22) so they read as "atmospheric" not "intrusive."

A faint dashed `<line>` running vertically at `x=600` from below the header to above the engines reinforces the central spine.

## The 3-column grid

Default to:
```
Col A:   x=60 – 400  (340w)    Underwriting infrastructure (Vault, Facility, SPV, Strata)
Col B:   x=420 – 780 (360w)    The "spine" (Cantor, Borrowers, Pivot, ABS Vault, MMFs)
Col C:   x=800 – 1140 (340w)   External counterparties (Buy Box, QA, Inst Buyers, Morpho)
```

Gutters of ~20–110px between columns. Wider gutters help when arrow labels need to live between columns ("loans", "subscribe · receive RWABS"). For Circuit 02 specifically, push columns wider (270 / 600 / 930 centers, 110px gutters) so step 6's full subscription label fits without overlapping boxes.

Every node center snaps to its column center. Spanning multiple columns (e.g., the BH Reporting Dashboard across Col A+B) is OK when warranted.

## Pivot circle treatment

Use `circleNode(id, cx, cy, r, opts)`. The pivot circle gets:
- A soft radial **glow** behind it (separate `<circle>` with `fill="url(#pivotGlow-${idSuf})"`, no stroke)
- **Two concentric outer rings** (r+33, r+17, no fill, gold stroke at 0.22 / 0.32 opacity)
- The main circle at r=85 with a 2.5px gold stroke and pale cream fill
- Inside: an eyebrow ("WHERE THE CIRCUITS MEET"), a two-line serif title ("Cantor's / Balance Sheet"), and an italic subtitle ("the pivot")

The circle is the only round node — it breaks the rectangular grid intentionally to read as the focal point.

## Edge color coding

| Color | Meaning | Hex |
|-------|---------|-----|
| **Blue** | Cash flows (deposits, draws, originations, supply USD) | `#5D89B4` (stroke), `#3F5C7D` (label) |
| **Gold** | Securities flows (loan sales, subscribe, RWABS) | `#C39C40` (stroke), `#8A6F2E` (label) |
| **Green** (BH primary) | Facility events / hot beats (approve, paydown) | `#00693E` |
| **Purple** | Collateral / legal plumbing (Buy Box → Facility, Strata) | `#7E5BAF` |
| **Sage** | Anchor capital from the Tempo Series LLC (Mode A, Mode B, Liquidator) | `#6F9879` |
| **Gray** | Generic flow indicators that don't fit elsewhere ("$ for purchase", "idle buffer") | `#7A8B7E` |

Each edge color gets its own arrow marker in `<defs>`: `arrow-cash`, `arrow-sec`, `arrow-hot`, `arrow-collat`, `arrow-engine`, plus the default `arrow`. Pass `markerKey: "arrow-cash"` to the `edge()` helper.

## Arrow routing

Prefer in this order:
1. **Short straight lines** between adjacent boxes in the same row/column
2. **Right-angle polylines** for long-distance routes (engines → vaults via canvas margins)
3. **Smooth Bezier curves** when right angles would feel mechanical or run into boxes
4. **Long diagonal paths** as a last resort

Right-angle paths can use rounded corners with `Q` (quadratic) commands for a softer feel:
```
M515,700 L 50,700 Q 30,700 30,680 L 30,330 Q 30,310 50,310 L 488,310
```

When routing Bezier curves, sample them at t=0.3, 0.5, 0.7 to verify they don't cross through boxes. Adjust control points to push the apex into empty gutters between columns.

## Label placement rules

1. Labels go in **empty space**, never inside or overlapping a box
2. **Color-match the label** to its arrow's purpose color (cash blue, securities gold, etc.)
3. For vertical arrows: label to the **right** of the arrow with `text-anchor="start"`
4. For horizontal arrows: label **above** the arrow with `text-anchor="middle"`
5. If a row gutter is tight (e.g., 22px between rows), labels go inside the gutter at the row's vertical midpoint — but only if there's clear horizontal space
6. If the gutter is too narrow for the full label, **shorten the label** before moving it elsewhere ("tokenized as collateral" → "as collateral")

When step badges and labels share a tight area, put the badge in the gutter and the label adjacent.

## Operational infrastructure sidebar

For nodes that aren't part of the primary flow (Fence, Reporting Dashboard, monitoring tools), group them in a sidebar **between** the two circuits, off to the right. Use `groupFrame()` to wrap them with a dashed border and a tab label ("OPERATIONAL INFRASTRUCTURE"). The sidebar lives in the dead space at the figure-8's waist where neither ellipse reaches.

## Dollar callouts

Use sparingly — only for the 2–4 most important money movements (day-1 deployment, draw amount, subscription size, paydown). Position them so they appear in clear empty space when their beat is active. The callout is 140×48 with the dollar value in serif and a small uppercase caption.

## Things to avoid

- **Two-line node labels.** Almost always means the label is too long or the box is too narrow. Shorten the label or widen the box.
- **Arrows that cross other arrows at low angles.** Reroute one of them — usually the older arrow keeps its path and the new one takes the longer route.
- **Multiple identical-colored arrows entering one node from different directions.** Hard to read which represents which flow. Stagger their entry points on the target box's perimeter.
- **Dollar callouts permanently visible.** They lose impact. Tied to specific beats only.
- **Group frames with a thick stroke.** They overwhelm the nodes inside. Dashed 1px at 0.55 opacity is the right weight.
