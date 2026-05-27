---
name: bh-design
description: |
  Brand-compliant document creation for Birch Hill Holdings — reports, strategy memos,
  counterparty briefs, one-pagers, and any non-deck deliverable. Use this skill whenever
  the user asks to "write a report," "create a one-pager," "draft a memo," "build a brief,"
  "format this as a BH document," or any request producing a .docx or .pdf that should
  follow Birch Hill's institutional brand. Also trigger when editing an existing document
  to match BH formatting, or when the user says "make this look like Birch Hill."
  NOT for slide decks — those are handled by birch-hill-pptx.
---

# BH Design — Document & One-Pager Skill

## What This Skill Does

Produces brand-compliant Birch Hill Holdings documents in `.docx` or `.pdf` format. Every deliverable follows the BH Report & Document Template Guide (v1.0, February 2026) — the single source of truth for non-deck materials.

This skill covers: strategy memos, counterparty briefs, research reports, board materials, partnership frameworks, tear sheets, one-pagers, LOIs, and any other document that isn't a slide deck.

For presentations, use the `birch-hill-pptx` skill instead.

## Grounding Documents in the Vault

Before drafting any strategy memo, counterparty brief, or board document, read from the Obsidian vault so the document reflects current reality rather than generic boilerplate:

- `atlas/rwasp-platform.md` — architecture hub (module ownership, entity roles, canonical narrative)
- `atlas/rwasp/entities/*.yaml` — BH entities (BHDS, Labs, DAM, Solutions) — for any doc that references entity roles, revenue lines, or regulatory status
- `atlas/rwasp/counterparties/*.yaml` — for any counterparty-facing brief (Sky, Ethena, Cap, Fulcrum, etc.)
- `atlas/rwasp/modules/*.yaml` — the three BH platform modules (securitization-tokenization, underwriting-servicing, loan-quality-assurance)
- `atlas/rwasp/dcv/sizing-rules.yaml` — DCV sizing and Dual-Engine strategy
- `atlas/rwasp/scenarios/*.yaml` — for any doc quoting numbers (base-sky, coc-shock, dcv-constrained-growth)
- `atlas/rwasp/gaps.md` — open questions; cite "Open Questions" in documents from here rather than inventing them
- Linear project [Birch Hill Brain Buildout](https://linear.app/birch-hill/project/birch-hill-brain-buildout-05679827a198) — for any "Next Steps" / "Open Items" section in a board doc or strategy memo

Never put a number in a document that isn't backed by a YAML value or a model run. If a figure isn't committed in the vault, leave it out or flag it as TBD — don't pattern-match a plausible number.

### Write-Back from Document Work

When producing a document surfaces new information (a decision made in drafting, a constraint discovered, a counterparty reframing), update the vault before shipping the document:

- Counterparty numbers confirmed → update the relevant `atlas/rwasp/counterparties/<name>.yaml`
- Architecture / entity-role changes → edit `atlas/rwasp-platform.md` (hub) with surgical precision
- New workstream surfaced → create a Linear issue (Birch Hill Brain Buildout), don't add to the hub's legacy Open Items block
- Gap resolved by the document → remove or mark resolved in `atlas/rwasp/gaps.md`

## Brand System — Document Design

### Color Palette

| Hex       | Name              | Usage                                              |
|-----------|-------------------|----------------------------------------------------|
| `#2D4A3E` | Dark Green        | Headlines, borders, structural elements, title rule |
| `#333333` | Body Text         | Main body copy, section headings                    |
| `#777777` | Muted Gray        | Subtitles, brand header, tag labels                 |
| `#999999` | Light Muted       | Dates, confidentiality lines, footnotes, disclaimers|
| `#E8E4DE` | Rules / Borders   | Section rules, table cell borders, grid lines       |
| `#2D6B46` | Metric Green      | Positive values in metric cards                     |
| `#8B3A3A` | Metric Red        | Negative values in metric cards                     |
| `#C4873B` | Amber             | Secondary modules, NEW tags                         |
| `#F5F3EF` | Card Background   | Callout boxes, metric card backgrounds              |

**Important:** The document palette (`#2D4A3E`) differs from the presentation palette (`#17423C`). Never mix them.

### Typography

**Single typeface: Arial. No exceptions.**

| Element              | Size   | Weight  | Color     |
|----------------------|--------|---------|-----------|
| Brand Header         | 9pt    | Bold    | `#777777` |
| Document Title       | 28pt   | Bold    | `#2D4A3E` |
| Subtitle Line 1      | 12pt   | Regular | `#777777` |
| Subtitle Line 2      | 10.5pt | Regular | `#777777` |
| Date / Confidentiality| 9pt   | Regular | `#999999` |
| Section Heading      | 16pt   | Bold    | `#333333` |
| Sub-Heading          | 13pt   | Bold    | `#333333` |
| Body Text            | 10.5pt | Regular | `#333333` |
| Table Header         | 7.5pt  | Bold    | `#FFFFFF` on `#2D4A3E` |
| Table Body           | 9pt    | Regular | `#333333` (col 1 bold) |
| Footnote / Disclaimer| 7pt    | Regular | `#999999` |

**Line spacing:** 1.4× (340 twips) for body text.

### Page Layout

- **Page size:** A4 (210mm × 297mm / 11906 × 16838 DXA)
- **Margins:** 18mm all sides (~1300 DXA)
- **Content width:** ~174mm (~9306 DXA)

### Title Block (Every Document)

Every BH document opens with a centered title block in this exact order:

1. **"BIRCH HILL HOLDINGS"** — 9pt bold, letter-spaced, `#777777`, centered
2. **Document Title** — 28pt bold `#2D4A3E`, centered
3. **Primary Subtitle** — 12pt regular `#777777`, centered
4. **Secondary Subtitle** — 10.5pt regular `#777777`, centered
5. **Date + Confidentiality** — 9pt regular `#999999`, centered
6. **Full-width 2pt rule** — `#2D4A3E`

### Section Format

- **Heading:** 16pt bold `#333333`, left-aligned
- **Rule:** 0.75pt `#E8E4DE` immediately below heading
- **Spacing:** ~8pt gap after rule before body
- **No hard page breaks between sections** — content flows naturally

### Mandatory Footer / Disclaimer

Every document ends with:

- 0.75pt `#E8E4DE` separator rule
- **"BIRCH HILL HOLDINGS • PROPRIETARY & CONFIDENTIAL"** — 7.5pt bold `#777777`, centered
- Disclaimer text — 7pt `#999999`, centered:

> *"This document is for informational purposes only and does not constitute investment advice. Backtest results are based on historical data and do not guarantee future performance. No commitments have been made by Birch Hill, [partners], or any other party as of the date of this document."*

Customize `[partners]` per counterparty when applicable.

## Component Library

### Data Tables

```
Header row:  #2D4A3E background, white bold 7.5pt text
Body rows:   9pt text (col 1 bold), alternating white / #F9F8F5
Borders:     0.5pt #E8E4DE all cells
Padding:     80 twips top/bottom, 120 twips left/right
Widths:      Always DXA (absolute), never percentages
```

### Callout Boxes

Single-cell borderless table:
- Background: `#F5F3EF`
- No border (clean, no accent stripe)
- Padding: ~14pt all sides
- Always begin with a bold label (e.g., "Core Thesis:", "Key Risk:", "Backtest Result:")

### Metric Cards

Horizontal row of KPI cells:
- Background: `#F5F3EF` with 0.5pt `#E8E4DE` border
- Label: 7pt bold `#777777`, centered, uppercase
- Value: 20–24pt bold, centered
  - Positive: `#2D6B46` / Negative: `#8B3A3A` / Neutral: `#333333`
- Footnote: 7pt `#999999` below card row

### Tag Headings

Colored pill labels for strategy modules:
- Dark green (`#2D4A3E`) tags: core modules (LOOP, RISK)
- Amber (`#C4873B`) tags: secondary/new features (CARRY, NEW)
- 7.5pt bold white text, 3px rounded corners
- Heading text: 13pt bold `#333333`, 10px gap after pill

### Bullet Points

- Unicode bullet (•) with hanging indent
- 360 twips left indent, 180 twips hanging
- Format: **Bold Label:** Regular description text.
- Same line height as body (1.4×), 4pt gap between items

## Document Types

### Strategy Memo

Purpose: Internal strategy analysis — Model A vs B, counterparty posture, platform decisions.

Structure:
1. Title block (standard)
2. Executive Summary (callout box with "Core Thesis:" label)
3. Context / Background section
4. Analysis sections (with sub-headings as needed)
5. Recommendation section
6. Open Questions / Next Steps
7. Footer disclaimer

### Counterparty Brief

Purpose: External-facing material for a specific counterparty (Sky, Ethena, Cap, etc.).

Structure:
1. Title block — subtitle includes counterparty name and engagement context
2. Partnership Overview (what BH and the counterparty each bring)
3. Economic Summary (metric cards showing key numbers)
4. Structure / Mechanics (data tables, flow descriptions)
5. Risk Framework (callout boxes for key risks)
6. Terms / Next Steps
7. Footer disclaimer — customize `[partners]` with counterparty name

### Research Report

Purpose: Data-driven analysis — vault backtests, yield comparisons, market assessments.

Structure:
1. Title block
2. Key Findings (metric cards)
3. Methodology
4. Data Analysis sections (tables, callout boxes for key results)
5. Limitations / Caveats
6. Appendix (if needed)
7. Footer disclaimer

### One-Pager / Tear Sheet

Purpose: Single-page summary for quick distribution — fund overview, strategy summary, partnership snapshot.

Structure:
1. Title block (compressed — smaller title, no secondary subtitle)
2. Metric cards row (3–5 KPIs)
3. Two-column layout:
   - Left: narrative summary (2–3 paragraphs max)
   - Right: key terms table or structure diagram
4. Footer disclaimer

Design constraint: Must fit on one A4 page. Use 9pt body text if needed to fit.

### Board Materials

Purpose: Quarterly updates, strategic decisions requiring board input.

Structure:
1. Title block — subtitle: "Board of Directors • [Quarter] [Year]"
2. Metric cards (portfolio-level KPIs)
3. Narrative sections per agenda item
4. Decision items (callout boxes with "Decision Required:" label)
5. Financial summary tables
6. Footer disclaimer

## How to Use This Skill

### Creating a New Document (.docx)

1. Read the `docx` skill (at `.claude/skills/docx/SKILL.md`) for infrastructure — it handles the actual docx-js code generation, validation, and packing.
2. Apply the BH brand system from this skill on top of the docx infrastructure:
   - Set A4 page size, 18mm margins
   - Configure Arial as the only font via styles
   - Build the title block as the first content
   - Apply section heading format (16pt bold + thin rule)
   - Use the component library (tables, callouts, metric cards) per the specs above
   - End with the mandatory disclaimer footer
3. Validate with `python scripts/office/validate.py`

### Creating a PDF One-Pager

1. Read the `pdf` skill (at `.claude/skills/pdf/SKILL.md`) for reportlab infrastructure.
2. Use reportlab's canvas or platypus to build the one-pager following BH brand specs.
3. Same brand rules apply — A4, Arial, title block, dark green accents, disclaimer footer.

### Editing an Existing Document

1. Follow the docx skill's unpack → edit XML → repack workflow.
2. Check that the result still passes the BH brand checklist (below).

## Pre-Publish Checklist

Before delivering any BH document, verify:

1. **Title block** — centered, letter-spaced brand header, 28pt green title, 2pt green rule
2. **Font** — Arial only, no other typefaces anywhere
3. **Section headings** — 16pt bold + thin `#E8E4DE` rule underneath
4. **Body text** — 10.5pt `#333333`, 1.4× line spacing
5. **Tables** — dark green header, alternating rows, DXA widths, cell padding
6. **Callout boxes** — `#F5F3EF` background, no border, bold prefix label
7. **Metric cards** — centered label + value, correct green/red/neutral coloring
8. **No unnecessary page breaks** — content flows naturally
9. **Footer disclaimer** — present and centered, counterparty customized if applicable
10. **Regulatory language** — "design" not "management," "assessment" not "underwriting," "curated strategies" not "managed strategies"

## Regulatory Language Guardrails

Birch Hill is pre-registration. All documents must use Cooley-approved terminology:

| Do NOT say            | Say instead              |
|-----------------------|--------------------------|
| management            | design                   |
| underwriting          | assessment               |
| managed strategies    | curated strategies       |
| fund                  | Series                   |
| investors             | participants             |

These guardrails apply to all external documents. Internal strategy memos may use more direct language where context is clear, but err on the side of compliance.

## Dependencies

- `docx` skill — for .docx creation infrastructure (docx-js, validation, XML editing)
- `pdf` skill — for .pdf creation infrastructure (reportlab, pypdf)
- `birch-hill-pptx` skill — for presentations (this skill does NOT handle decks)
- Brand guide source: project knowledge `docs/birch_hill_brand_guide.md`
