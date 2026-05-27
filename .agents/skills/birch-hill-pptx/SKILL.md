---
name: birch-hill-pptx
description: |
  Brand-compliant PowerPoint deck creation for Birch Hill Holdings. Use this skill whenever a presentation, pitch deck, roadshow deck, case study, strategy overview, or slide deck needs to be created for Birch Hill — whether the user says "Birch Hill deck," "make a presentation," "build slides," "pitch deck," or references any Birch Hill strategy or client material that should be in slide format. Also trigger when editing or restyling an existing Birch Hill .pptx to match brand guidelines, or when the user asks to "make this look like Birch Hill" or "use the BH template."
---

# Birch Hill Holdings — Presentation Build System

This skill is the authoritative guide for building Birch Hill decks. It is grounded in two working reference files:
- `assets/BH_Template.pptx` — the starter template with 18 pre-built layout archetypes
- The seed deck (`Birch_Hill_Seed_Deck_vF_s.pptx`) — the canonical example of what a real, polished BH deck looks like in practice

Everything here was derived by inspecting those files directly. **Do not rely on guesswork.**

---

## The Two Rules That Override Everything

**Rule 1 — Every slide must wear the brand chrome.** Five persistent elements (logo, title, subtitle, green rule, footer band) appear on every non-cover slide, in exactly the same positions, on every deck. This is the Birch Hill "uniform." Get these right and a slide reads as on-brand before you draw a single piece of content.

**Rule 2 — Inside the chrome, layout is deliberately flexible.** The seed deck proves the point: of 21 slides, 9 use the bare `1_DEFAULT` layout with fully custom content (a flywheel with numbered step circles, an infrastructure stack with category bands, case-study phase cards, partnership tiles with color bars). The 18 template archetypes are **starters**, not a cage. Reach for an archetype when it fits the content; drop to `1_DEFAULT` and compose freely when it doesn't.

The correct workflow, every time:

```
1. Copy assets/BH_Template.pptx to a working file
2. For each slide, decide: archetype (edit in place) or 1_DEFAULT (build freely)
3. Apply the brand chrome to every non-cover slide
4. Trim unused template slides from the ZIP directly
5. QA every slide visually — re-check chrome before content
```

---

## The Brand Chrome — Mandatory on Every Non-Cover Slide

These five elements are the Birch Hill signature. They are non-negotiable. Every slide that is not the Cover or Disclosures page **must** have all of them, in exactly these positions. This is what the seed deck enforces across all 18 of its content slides.

| Element | Shape / Type | Position (in) | Size (in) | Spec |
|---------|--------------|---------------|-----------|------|
| **Logo** (top-right, subtle) | Picture | x=19.00, y=0.30 | 0.51 × 0.80 | EMF from `assets/bh_logo_dark.emf` (or `bh_logo_light.emf` on dark-header slides). Small. Never resized larger. Functions as a watermark, not a headline. |
| **Title** | Text box | x=1.00, y=0.20–0.50 | 17.60 × 0.80 | 40pt, `#1F2937` (or white on dark header), Inter bold. Left-aligned. |
| **Subtitle / tagline** | Text box | x=1.00, y=1.00 | 18.00 × 0.30 | 16pt, `#4B5563`, Inter regular. One-line summary of the slide's point. Optional but strongly preferred. |
| **Green horizontal rule** | Line connector | from (1.00, 1.50) to (19.00, 1.50) | 18.00 × 0 | Color `#195E3B`, weight 2pt (25,400 EMU). Separates header from content. |
| **Footer band** | Rectangle | x=0.00, y=10.45 | 20.00 × 0.80 | Solid fill `#17423C` (dark green). Full bleed left-to-right. |
| ↳ Confidential text | Text box | x=0.60, y=10.70 | 4.20 × 0.30 | "Birch Hill  \|  Proprietary & Confidential" — 10pt Inter, `#EAD2A8` (gold). |
| ↳ Slide number | Text box | x=18.74, y=10.65 | 0.80 × 0.40 | Inter 10pt right-aligned, gold. |
| ↳ Source attribution (optional) | Text box | x=8.80, y=10.75 | 10.00 × 0.20 | 9pt Inter italic, gold. Use for footnotes like "DeFiLlama – Data as of 4/17/2026". |

**The content zone** is everything between the rule (y=1.50) and the footer band (y=10.45): a **18.0" wide × 8.95" tall** canvas. How you fill it is a per-slide design decision — see "Layout Strategy" below.

### Brand chrome helper

Copy this verbatim. Call `apply_brand_chrome(slide, title, subtitle, slide_num, source=None, dark_header=False)` on every non-cover slide after filling content.

```python
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

LOGO_DARK = '/mnt/skills/user/birch-hill-pptx/assets/bh_logo_dark.emf'
LOGO_LIGHT = '/mnt/skills/user/birch-hill-pptx/assets/bh_logo_light.emf'

def apply_brand_chrome(slide, title, subtitle=None, slide_num=None,
                       source=None, dark_header=False):
    # Logo — top-right, small, ALWAYS present
    logo = LOGO_LIGHT if dark_header else LOGO_DARK
    slide.shapes.add_picture(logo, Inches(19.00), Inches(0.30),
                             width=Inches(0.51), height=Inches(0.80))

    # Title
    tb = slide.shapes.add_textbox(Inches(1.00), Inches(0.50),
                                  Inches(17.60), Inches(0.80))
    set_tf(tb, title, size_pt=40, bold=True,
           color=C_WHITE if dark_header else C_BODY)

    # Subtitle / tagline (optional but preferred)
    if subtitle:
        tb = slide.shapes.add_textbox(Inches(1.00), Inches(1.00),
                                      Inches(18.00), Inches(0.30))
        set_tf(tb, subtitle, size_pt=16,
               color=C_LIGHT_GREEN if dark_header else C_BODY2)

    # Green rule — mandatory separator between header and content
    line = slide.shapes.add_connector(1, Inches(1.00), Inches(1.50),
                                      Inches(19.00), Inches(1.50))
    line.line.color.rgb = RGBColor(0x19, 0x5E, 0x3B)
    line.line.width = Emu(25400)  # 2pt

    # Footer band — dark green, full bleed
    band = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0),
                                  Inches(10.45), Inches(20.00), Inches(0.80))
    band.fill.solid(); band.fill.fore_color.rgb = C_DARK_GREEN
    band.line.fill.background()

    # Confidential
    tb = slide.shapes.add_textbox(Inches(0.60), Inches(10.70),
                                  Inches(4.20), Inches(0.30))
    set_tf(tb, "Birch Hill  |  Proprietary & Confidential",
           size_pt=10, color=C_GOLD)

    # Slide number
    if slide_num is not None:
        tb = slide.shapes.add_textbox(Inches(18.74), Inches(10.65),
                                      Inches(0.80), Inches(0.40))
        set_tf(tb, str(slide_num), size_pt=10, color=C_GOLD,
               align=PP_ALIGN.RIGHT)

    # Source attribution (optional)
    if source:
        tb = slide.shapes.add_textbox(Inches(8.80), Inches(10.75),
                                      Inches(10.00), Inches(0.20))
        set_tf(tb, source, size_pt=9, italic=True, color=C_GOLD,
               align=PP_ALIGN.RIGHT)
```

**QA test for chrome:** render any non-cover slide as an image. If you cannot see, simultaneously, (1) the subtle logo in the top-right, (2) the title and subtitle, (3) the thin green rule below, and (4) the dark green footer band with confidential text and a slide number — **the chrome is broken and the slide is not on-brand.** Fix before reviewing content.

---

## Template File

```
Path:   /mnt/skills/user/birch-hill-pptx/assets/BH_Template.pptx
Canvas: 20.0" x 11.25"  <-- NOT standard 13.333"x7.5". This is critical.
```

The template contains 18 slides, each a different layout archetype. Use them as starters — or ignore them entirely and compose on `1_DEFAULT`.

---

## Layout Strategy — When to Use What

The seed deck uses **six distinct layouts**, not 18. This is the real design language:

| Layout | Use it for | Seed deck example |
|--------|------------|-------------------|
| **Cover** | Title slide only | Slide 0 |
| **Header Green - Opt 3** | Slides with a dark green full-width header band — use for section openers or slides where the header visual is part of the story | Slides 1, 4 |
| **1_DEFAULT** *(workhorse)* | Any custom content: flywheels, stacks, case-study cards, partnership tiles, roadmaps, revenue models, use-of-funds charts | Slides 2, 3, 5, 7, 9, 15, 16, 17, 18 |
| **Dark - One Line** | Team page with a one-line title and dark cards | Slide 6 |
| **Light** | Horizontal band-based layouts: partnerships, stack diagrams, vault tiers, use-of-funds rows | Slides 8, 10, 11, 14, 19, 20 |
| **Case Study** | 3-phase horizontal card layout with table below | Slides 12, 13 |

**Default to `1_DEFAULT` when in doubt.** The freedom is the feature. The brand chrome keeps it on-brand; the content zone is yours to design.

### Patterns the seed deck uses inside 1_DEFAULT

Study these as proof the custom-content approach works. Each of these is a "1_DEFAULT" slide that looks nothing like the others, yet all read as the same deck because the chrome is identical.

- **Two side-by-side charts with annotated growth arrows and CAGR callouts** (slide 2: "Institutional Onchain Credit Opportunity"). Charts at ~9.0" wide, arrow connectors overlaid, text boxes with percentage deltas.
- **2×2 business-line grid with icon + title + tag line** (slide 3: "Institutional Onchain Capital Platform"). Each card 8.2×3.0", category label above, 0.65×0.65" icon in top-left.
- **Horizontal flywheel with 4 numbered steps** (slide 4: "The Flywheel"). 4 columns × 6.6" tall, numbered circles at the top, tri-section internal divider (WHAT / FEEDS INTO / REVENUE), arrow connectors between columns.
- **Split-screen: custom infographic + narrative table** (slide 5: "Rebuilding Securitization Onchain"). Dense icon composition on the left, two-row text tiles on the right.
- **5-row horizontal client cards** (slide 7: live client engagements). Each row 18.0×1.4", all five stacked.
- **2×2 partnership matrix with color-bar label** (slide 8). Each cell is a `Rectangle 18×1.8` with a 0.15"-wide accent bar on the left.
- **Vault infrastructure stack — 6 horizontal bands with category column on the left and logo clusters on the right** (slide 11). Category labels at y=2.0/4.6/7.2 spanning multiple rows; each row has layer label + partner logos.
- **Case-study 3-phase cards with star marker, sub-label, table below** (slides 12, 13). Three 5.2×3.5–5.0" cards with rounded corners + a 17.2×3.0" table at the bottom.
- **Dual-engine strategy page with stacked content zones** (slide 15).
- **Competitive landscape with highlight column and logo row** (slide 16). Logos at top, 18×5.1" table below, 2.9×6.5" highlight rectangle.
- **Use-of-funds: one big number + 4 horizontal budget rows with percentages** (slide 19).

These are not in the 18-template layout map. They were built directly on `1_DEFAULT`. The brand chrome made them cohesive.

---

## Working on 1_DEFAULT — Composition Rules

When building custom layouts on `1_DEFAULT`, follow these conventions so the result matches the seed deck's visual language:

**Columns.** The seed deck uses 3-column and 4-column grids most often:
- 3-column on 18" width: columns at x = 1.40, 7.30, 13.20; width 5.20–5.40; gap ~0.5"
- 4-column on 18" width: columns at x = 1.00, 5.60, 10.20, 14.80; width 4.20; gap 0.4"
- 5-column on 18" width: columns at x = 1.30, 4.95, 8.60, 12.25, 15.90; width 3.65

**Card pattern.** A "card" in the seed deck is a rounded rectangle (`Shape 3`) with:
- Fill `#FFFFFF` or `#F0F5F1` (light cream)
- No visible border (line fill background)
- Height 3.5–6.6" depending on content
- A category label in uppercase 11pt `#89AF84` at the top-left
- A bold title at 18–24pt `#00693E` below it
- Body text at 13–15pt `#4B5563`

**Numbered step circles.** Small `#00693E`-filled ovals, 0.45×0.45", with white Inter bold 16pt number. Used to mark phases or steps (flywheel, case studies).

**Accent bars.** 0.10–0.15" wide vertical rectangles in `#55A461` or `#00693E` on the left edge of horizontal cards (partnership tiles, use-of-funds rows).

**Connectors.** Thin arrow connectors in `#55A461`, 1–2pt, to indicate flow between columns (flywheel, phase sequences).

**Icons.** 0.40–0.65" PNG/SVG glyphs at the top-left of cards. Keep consistent sizing across a slide.

**Charts.** Stay inside the content zone (y=1.80 to y=10.40). Use Inter for all labels. Axis/grid color `#9DA3AE`. Series colors from the brand palette below.

---

## Canonical Build Script

Copy this verbatim as the skeleton for every deck build:

```python
import copy, shutil, zipfile, re
from pptx import Presentation
from pptx.util import Pt, Inches, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from lxml import etree

TMPL = '/mnt/skills/user/birch-hill-pptx/assets/BH_Template.pptx'
WORK = '/home/claude/deck_work.pptx'
OUT  = '/home/claude/deck_final.pptx'

shutil.copy(TMPL, WORK)
prs = Presentation(WORK)

# ── Edit slides in-place here ──────────────────────────────────────────────
# Option A: use an archetype — prs.slides[4] (roadmap), fill existing shapes.
# Option B: clear all content shapes from a 1_DEFAULT slide and compose freely.
# Call apply_brand_chrome(slide, title, subtitle, slide_num) on each non-cover slide.

prs.save(WORK)

# ── Trim: keep only slides you filled in ───────────────────────────────────
KEEP = 7  # number of slides to keep (slides 1..KEEP survive)

with zipfile.ZipFile(WORK, 'r') as zin:
    content = {name: zin.read(name) for name in zin.namelist()}

# Remove extra sldId entries from presentation.xml
prs_xml = etree.fromstring(content['ppt/presentation.xml'])
ns = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}
sldIdLst = prs_xml.find('.//p:sldIdLst', ns)
for sld_id in list(sldIdLst)[KEEP:]:
    sldIdLst.remove(sld_id)
content['ppt/presentation.xml'] = etree.tostring(
    prs_xml, xml_declaration=True, encoding='UTF-8', standalone=True)

# Remove slide XML files beyond KEEP
slides_to_remove = set()
for i in range(KEEP + 1, 19):
    slides_to_remove.add(f'ppt/slides/slide{i}.xml')
    slides_to_remove.add(f'ppt/slides/_rels/slide{i}.xml.rels')

# Remove relationship entries for dropped slides
rels_xml = etree.fromstring(content['ppt/_rels/presentation.xml.rels'])
slide_rel = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide'
for rel in list(rels_xml):
    if rel.get('Type') == slide_rel:
        m = re.search(r'slide(\d+)\.xml', rel.get('Target', ''))
        if m and int(m.group(1)) > KEEP:
            rels_xml.remove(rel)
content['ppt/_rels/presentation.xml.rels'] = etree.tostring(rels_xml)

# Write clean output ZIP
with zipfile.ZipFile(OUT, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
    for name, data in content.items():
        if name not in slides_to_remove:
            zout.writestr(name, data)
```

**Why trim via ZIP manipulation, not python-pptx slide removal?**
`prs.slides._sldIdLst.remove()` removes the slide reference but leaves the XML files in the ZIP, causing duplicate-entry errors that corrupt the file. Direct ZIP manipulation is the only reliable approach.

---

## Core Text Helper

Every text write must go through this helper. The font name `"Inter"` must be set on every run — python-pptx will otherwise fall back to the theme default (Calibri), which is wrong.

```python
def set_tf(shape, text, size_pt=None, bold=None, color=None,
           align=PP_ALIGN.LEFT, italic=False):
    tf = shape.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.name = "Inter"          # ALWAYS set this
    if size_pt: r.font.size = Pt(size_pt)
    if bold is not None: r.font.bold = bold
    if color: r.font.color.rgb = color
    if italic: r.font.italic = True
```

---

## Brand Colors

Sourced from template slide 18 (the official swatch slide) and the seed deck:

```python
# Primary brand
C_DARK_GREEN = RGBColor(0x17, 0x42, 0x3C)  # #17423C -- footer band, header fills, dark cards
C_RULE_GREEN = RGBColor(0x19, 0x5E, 0x3B)  # #195E3B -- the mandatory header rule color
C_MID_GREEN  = RGBColor(0x55, 0xA4, 0x61)  # #55A461 -- accents, positive metrics, arrows
C_LIGHT_GREEN= RGBColor(0xA6, 0xD3, 0xB3)  # #A6D3B3 -- pale text on dark bg, subheads
C_PALE_GREEN = RGBColor(0xD5, 0xE1, 0xAE)  # #D5E1AE -- very pale accents
C_CREAM      = RGBColor(0xEE, 0xFA, 0xE8)  # #EEFAE8 -- slide bg, card bg

# Content colors
C_TITLE_GRN  = RGBColor(0x00, 0x69, 0x3E)  # #00693E -- Dartmouth Green, the canonical Birch Hill brand green; card titles, green text on light
C_SUBTITLE   = RGBColor(0x89, 0xAF, 0x84)  # #89AF84 -- muted subheads, uppercase labels
C_BODY       = RGBColor(0x1F, 0x29, 0x37)  # #1F2937 -- primary body text
C_BODY2      = RGBColor(0x4B, 0x55, 0x63)  # #4B5563 -- secondary body text
C_MUTED      = RGBColor(0x9D, 0xA3, 0xAE)  # #9DA3AE -- labels, footnotes, axis lines

# Functional
C_CARD_BG    = RGBColor(0xF0, 0xF5, 0xF1)  # #F0F5F1 -- card tag label backgrounds
C_CALLOUT    = RGBColor(0xDF, 0xE9, 0xE2)  # #DFE9E2 -- callout band fill
C_WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
C_GOLD       = RGBColor(0xEA, 0xD2, 0xA8)  # #EAD2A8 -- footer text on dark
```

---

## The 18 Template Slides — Archetype Map

Starters, not a cage. Use an archetype when the content fits cleanly; otherwise use `1_DEFAULT`.

| Index | Layout Name | Archetype Use |
|-------|-------------|---------------|
| 0 | Cover | Title slide — centered logo, title/subtitle/date bottom-left |
| 1 | H: Green 2.1 / C: 2 Cols | Engagement overview — big green header, two white cards |
| 2 | H: Green 3.1 / C: 3 Cols | "How we support X" — green header, 3 dark-top/light-bottom cards |
| 3 | H: Green 2.1 FN / C: Text | Risk partner / capability — 4 header boxes + table below |
| 4 | H: 2 Lines / C: 4 Cols | Roadmap — 4 numbered phase columns + callout band |
| 5 | H: Green 1.1 / C: 5 Cols | Capability matrix — 5 columns with tag + 3 items each |
| 6 | H: Green 1.2 / C: Text | Phase detail — 3 horizontal risk cards + 3 numbered step cards + callout |
| 7 | H: 1 Line / C: Text | Light bg, thin green rule, free-form text content |
| 8 | H: 1 Line / C: Text | Table slide (pre-built table + callout banner) |
| 9 | H: 1 Line / C: Text | Large clean table (8 rows × 4 cols) |
| 10 | H: 1 Line / C: 5 Rows | 5 horizontal content rows with left accent bar |
| 11 | H: 1 Line / C: 3 Cols | 3 icon-topped cards (has embedded icons) |
| 12 | H: 1 Line / C: 3 Cols Alt | 3-column metric flow (label → big number → body) |
| 13 | H: Green 4.1 / C: Team | Team slide — 4-person grid |
| 14 | H: 1 Line / C: Text | Free text / single callout |
| 15 | H: Green 1.1 / C: Contacts | Contact / closing |
| 16 | H: 1 Line / C: Roadmap | Horizontal timeline with step flags and investor logos |
| 17 | Disclosures | Important Disclosures page |

Specifics of each archetype's shape positions are preserved below for reference — use them when filling in an archetype slide.

---

## Shape Position Reference (Archetypes)

When you use an archetype slide, these are the exact measured positions (in inches) of every editable shape. Use them to target shapes precisely. When you use `1_DEFAULT`, ignore this — you're composing fresh.

### Slide 0 — Cover

| Shape | x | y | w | h | Content |
|---|---|---|---|---|---|
| Text Placeholder 10 | 1.5 | 9.0 | 17.2 | 0.53 | Main title |
| Text Placeholder 11 | 1.5 | 9.65 | 17.2 | 0.30 | Subtitle |
| Text Placeholder 12 | 1.5 | 10.2 | 2.0 | 0.27 | Date |

### Slide 1 — 2-Col Engagement Overview

Header band (from layout): dark green full width, covers top ~40% of slide.

| Shape | x | y | w | h | Role |
|---|---|---|---|---|---|
| Title 10 | 1.0 | 0.6 | 17.6 | 1.3 | Slide title (white 48pt) |
| Text Placeholder 11 | 1.4 | 2.8 | 16.0 | 0.34 | Subtitle line (white 20pt) |
| Text 5 left | 2.4 | 5.6 | 6.4 | 0.25 | Left card label — 15pt #89AF84 |
| Text 6 left | 2.4 | 6.3 | 6.4 | 0.54 | Left card headline — MAX 20pt #00693E |
| Text 7 left | 2.4 | 7.2 | 6.4 | 0.34 | Left card body — MAX 14pt #4B5563 |
| Text 5 right | 11.21 | 5.6 | 6.4 | 0.25 | Right card label |
| Text 6 right | 11.21 | 6.3 | 6.4 | 0.54 | Right card headline — MAX 20pt |
| Text 7 right | 11.21 | 7.2 | 6.4 | 0.34 | Right card body — MAX 14pt |

WARNING: Text 6 boxes are only 0.54" tall. At 32pt the text overflows into the body below. Use 20pt maximum for card headlines on this layout.

### Slide 2 — 3-Col "How We Support"

| Shape | x | y | Role |
|---|---|---|---|
| Title | 1.0 | 0.6 | Slide title |
| Subtitle placeholder | 1.4 | 2.8 | Tagline |
| Header title col 1/2/3 | 2.0 / 7.9 / 13.8 | 4.8 | Dark card title — 28pt white |
| Header sub col 1/2/3 | 2.0 / 7.9 / 13.8 | 6.1 | Dark card sub — 20pt #A6D3B3 |
| Light title col 1/2/3 | 2.0 / 7.9 / 13.8 | 7.6 | Light card bold title — 24pt #00693E |
| Light body col 1/2/3 | 2.0 / 7.9 / 13.8 | 8.2 | Light card body — 15pt #4B5563 |

### Slide 3 — 4-Header + Capability Table

| Shape | x | y | Role |
|---|---|---|---|
| Title | 1.0 | 0.6 | Slide title |
| Subtitle | 1.4 | 2.6 | Tagline |
| Header title 4 cols | 1.701 / 6.094 / 10.499 / 14.899 | 3.8 | Column header bold — 22pt white |
| Header sub 4 cols | same x | 4.597 | Column sub — 16pt #A6D3B3 |
| Text 19 table label | 1.398 | 5.8 | Label above table — 24pt |
| Table 29 | 1.398 | 6.4 | 17.2×3.41" table (7 rows × 2 cols) |

Table cell formatting: Header row fill #17423C, white bold 15pt. Body col 1: #00693E bold. Body col 2: #1F2937.

### Slide 4 — 4-Col Roadmap

| Shape | x | y | Role |
|---|---|---|---|
| Title | 1.0 | 0.5 | Slide title — 40pt #1F2937 |
| Placeholder 18 | 1.0 | 1.396 | Subtitle — 20pt #4B5563 |
| Phase headers 4 | 1.997 / 6.6 / 11.2 / 15.8 | 2.7 | Phase name — 22pt white |
| Phase timing 4 | same x | 3.321 | Timing — 16pt #A6D3B3 |
| Detail title row 1 | 1.4 / 5.994 / 10.597 / 15.197 | 4.8 | Item title — 14pt #00693E |
| Detail body row 1 | same x | 5.2 | Item body — 15pt #4B5563 |
| Detail title row 2 | same x | 6.8 | Second item title |
| Detail body row 2 | same x | 7.2 | Second item body |
| Text 43 callout | 1.2 | 9.3 | Callout band text — 18pt #00693E centered |

### Slide 5 — 5-Col Capability

| Shape | x | y | Role |
|---|---|---|---|
| Title | 1.0 | 0.5 | Slide title — 40pt #1F2937 |
| Text Placeholder 4 | 1.0 | 1.9 | DO NOT USE — invisible, bleeds behind graphic |
| Col headers 5 | 1.301 / 4.954 / 8.600 / 12.249 / 15.899 | 3.3 | Header — 16pt white bold |
| Shape 6 tag 5 | 1.501 / 5.154 / 8.801 / 12.449 / 16.099 | 4.6 | Tag label — 15pt #00693E bold |
| Text 8 sub 5 | same x | 5.55 | Sub — 12pt #9DA3AE |
| Text 10 item 1 title | same x | 6.6 | Bold item — 14pt #1F2937 |
| Text 11 item 1 body | same x | 7.0 | Body — 12pt #4B5563 |
| Text 13 item 2 title | same x | 7.9 | Bold item — 14pt #1F2937 |
| Text 14 CTA | same x | 9.1 | Green CTA — 12pt #55A461 |

WARNING: Text Placeholder 4 on this layout sits behind a decorative graphic in the header band. Any text placed there will bleed visibly onto the slide. Leave it empty.

### Slide 6 — Phase Detail (3 Risk Cards + 3 Step Cards)

| Shape | x | y | Role |
|---|---|---|---|
| Title | 1.0 | 0.5 | Slide title — 40pt #1F2937 |
| Placeholder 2 | 1.0 | 1.9 | Subtitle — 20pt #4B5563 |
| Text 3 | 1.0 | 3.1 | Section label between rows — 20pt |
| Shape 6 metric box | 5.4 / 11.5 / 17.6 | 3.7 | Right metric box in each card (1.4×2.0") |
| Text 6 card title | 1.6 / 7.7 / 13.8 | 4.0 | Card title — 22pt #1F2937 bold |
| Text 13 card body | same x | 4.7 | Card body — 14pt #4B5563 |
| Text 16 center label | 8.0 | 6.2 | Label between rows — set or clear |
| Shape 4 number circles | 1.4 / 7.6 / 13.8 | 7.131 | Number circle (0.45×0.45") |
| Text 6 step title | 2.1 / 8.3 / 14.5 | 7.1 | Step title — 22pt #00693E bold |
| Text 13 step body | same x | 7.8 | Step body — 14pt #4B5563 |
| Text 43 callout | 1.2 | 9.3 | Callout band text — 18pt #00693E centered |

---

## Shape Targeting Pattern (for Archetypes)

Never rely on shape names alone — the template uses duplicate names like "Text 6" across columns. Always match on both name AND position:

```python
for sh in slide.shapes:
    if not sh.has_text_frame:
        continue
    lx = sh.left / 914400   # convert EMU to inches
    t  = sh.top  / 914400

    # Target a specific cell: right card headline on slide 1
    if abs(lx - 11.206) < 0.2 and abs(t - 6.3) < 0.15:
        set_tf(sh, "Your headline here", size_pt=20, color=C_TITLE_GRN)
```

Tolerance of 0.2" is appropriate for most shapes. Use 0.15" when shapes are closely packed (roadmap detail cells). Use 0.12" for the 5-column layout where columns are ~3.6" apart.

Always guard against the Slide Number Placeholder:
```python
# Safe pattern: skip slide number placeholders before writing
if 'slide number' in sh.name.lower():
    continue
```

---

## Building on 1_DEFAULT — Recipe

When composing a custom layout:

```python
# Pick a 1_DEFAULT slide from the template (e.g. one of the simpler archetypes)
slide = prs.slides[7]  # "H: 1 Line / C: Text" is a good blank-ish start

# Clear the archetype's placeholder content (keep only layout-level shapes)
# Be conservative — only delete shapes from the content zone (y > 1.80, y < 10.40)
to_remove = []
for sh in slide.shapes:
    t = sh.top / 914400
    if 1.80 < t < 10.40:
        to_remove.append(sh)
for sh in to_remove:
    sh._element.getparent().remove(sh._element)

# Apply brand chrome (idempotent — safe to call even if title/line already exist;
# in practice clear first then re-add to guarantee exact positions)
apply_brand_chrome(slide, "Your Title", "Your subtitle tagline",
                   slide_num=3, source="Source note if needed")

# Compose your content inside the content zone (y=1.80 to y=10.40, x=0 to x=20)
# Use Inches() for all positions. Reference the color palette. Always set font=Inter.
# See "Patterns the seed deck uses inside 1_DEFAULT" for design recipes.
```

---

## Pitfalls Reference

### 1. Never add_slide() and copy — it creates duplicate ZIP entries

Wrong:
```python
new_prs = Presentation(TMPL)
new_prs.slides._sldIdLst.clear()   # does not remove XML files from ZIP
new_slide = new_prs.slides.add_slide(layout)
```
This leaves all 18 original slide XMLs in the ZIP and adds duplicates. The file is corrupted.

Right: Copy the template, edit existing slides in-place, trim via ZIP manipulation.

### 2. Never remove slides with sldIdLst.remove() alone

`prs.slides._sldIdLst.remove(sld_id)` removes the reference but not the XML file from the ZIP. You must also remove the XML entries and relationship entries directly as shown in the canonical build script.

### 3. Text Placeholder 4 on slide 5 is a trap

Sits at (1.0", 1.9") directly behind a decorative graphic. Text placed there bleeds. Leave it empty.

### 4. Slide Number Placeholder at (18.74", 10.65") on every slide

If position-matching tolerance is too loose, you can write content into the page number box by accident. It renders in the bottom-right corner and overflows the slide. Guard against it by name.

### 5. Text box height constrains font size

Key size limits derived from template measurements:
- Slide 1 card headline (Text 6, h=0.54"): 20pt max
- Slide 1 card body (Text 7, h=0.34"): 14pt max
- Slide 4 roadmap detail cells (h=0.27"–0.51"): 14–15pt max
- Slide 5 card items (h=0.25"–0.30"): 12–14pt max

Exceeding these causes overflow into the shape below.

### 6. LibreOffice renders Inter differently from PowerPoint

The template uses Inter typeface. LibreOffice (used for PDF/QA conversion) may show minor overlap on tight text boxes that looks fine in PowerPoint. Don't chase LibreOffice pixel-perfect rendering — verify in PowerPoint for final review.

### 7. Forgetting the logo on 1_DEFAULT slides

The `1_DEFAULT` template slide does **not** include the top-right logo by default. If you build a custom layout and forget `apply_brand_chrome()`, the logo will be missing — the most common on-brand failure. The QA checklist below is designed to catch this every time.

### 8. Oversized logo

The logo is 0.51" × 0.80" — about the size of a fingernail. It's a watermark, not a headline. If it looks prominent, it's wrong. Do not scale it up for "visibility."

---

## Regulatory Language

Birch Hill is pre-registration as of early 2026. These substitutions are Cooley-approved:

| Never Use | Always Use |
|-----------|------------|
| management (as BH's action) | design, curation |
| underwriting | assessment |
| managed strategies | curated strategies |
| investment management | institutional curation |

The test: if Birch Hill is the grammatical subject performing the verb, use approved vocabulary. Category labels ("RISK MANAGEMENT" as a header) are fine.

---

## QA Checklist

After building, run:
```bash
python /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf /path/to/deck.pptx
pdftoppm -jpeg -r 150 /path/to/deck.pdf slide
```

Inspect every slide image for:

**Brand chrome (check first — non-negotiable):**
1. Logo visible in top-right corner, small (~0.5×0.8"), not resized
2. Title in top-left, subtitle beneath it
3. Thin green horizontal rule at y≈1.50" spanning the slide width
4. Dark green footer band at the bottom with "Birch Hill | Proprietary & Confidential" and a slide number
5. No stray text in bottom-right corner (Slide Number Placeholder not filled)

**Content quality:**
6. No text overflow — text not bleeding outside its box
7. No `[ ]` placeholders — all template placeholder text replaced
8. Slide count correct — ZIP trim removed exactly the right slides
9. Colors on-brand — green headers, no default blue or black
10. Regulatory language clean — no "management/underwriting/managed" as BH actions

---

## Full Process Reference

Step 1: Inspect the template layouts
```bash
python3 -c "
from pptx import Presentation
prs = Presentation('/mnt/skills/user/birch-hill-pptx/assets/BH_Template.pptx')
for i, s in enumerate(prs.slides):
    print(f'Slide {i}: {s.slide_layout.name}')
"
```

Step 2: Measure shapes for each layout you will use (only needed for archetype slides — skip for 1_DEFAULT)
```bash
python3 -c "
from pptx import Presentation
prs = Presentation('/mnt/skills/user/birch-hill-pptx/assets/BH_Template.pptx')
for sh in prs.slides[N].shapes:
    if hasattr(sh, 'left'):
        txt = sh.text_frame.text[:40] if sh.has_text_frame else ''
        print(f'[{sh.name}] ({sh.left/914400:.2f}\",{sh.top/914400:.2f}\") {sh.width/914400:.2f}\"x{sh.height/914400:.2f}\" \"{txt}\"')
"
```

Step 3: Build using the canonical build script — pick archetype or 1_DEFAULT per slide, always `apply_brand_chrome()`

Step 4: QA every slide visually via PDF render — brand chrome first, content second

Step 5: Fix issues (adjust font sizes, clear stray placeholders, verify logo present), re-QA, deliver

---

## Full QA Process (Mandatory — Do Not Skip)

The first render is almost never correct. Treat QA as a bug hunt, not a sign-off.

### Step 1 — Verify the ZIP before rendering

Before spending time on PDF conversion, confirm the output file is structurally clean:

```python
import zipfile, re

with zipfile.ZipFile('/home/claude/deck_final.pptx') as z:
    all_names = z.namelist()
    slides = sorted([n for n in all_names if re.match(r'ppt/slides/slide\d+\.xml$', n)])
    dups = [n for n in all_names if all_names.count(n) > 1]
    print(f"Slide XMLs: {slides}")
    print(f"Duplicates: {set(dups) if dups else 'none'}")
```

If there are duplicates: **stop and fix the build script**. The ZIP trim step did not run correctly.

If slide count is wrong (e.g. 18 instead of 7): the trim step didn't remove the extra slides. Check the `KEEP` value and re-run.

### Step 2 — Convert to images

```bash
python /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf /home/claude/deck_final.pptx
rm -f /home/claude/qa-*.jpg
pdftoppm -jpeg -r 150 /home/claude/deck_final.pdf /home/claude/qa
ls -1 /home/claude/qa-*.jpg
```

### Step 3 — Visually inspect every slide

Use the `view` tool on each image. Do not skim. For each slide:

**Chrome check (do this FIRST on every slide):**
```
□ Logo visible top-right, small, not resized
□ Title and subtitle populated and on-brand
□ Green horizontal rule spans the slide just below the subtitle
□ Footer band is dark green, full-bleed, visible
□ "Birch Hill | Proprietary & Confidential" visible in footer
□ Slide number visible in bottom-right (not overflowing)
```

**Content check:**
```
□ All text boxes have real content (no "[ ]" remaining)
□ No text bleeding outside its containing box
□ Callout bands have content
□ Tables have filled header rows (dark green) and body rows with real text
□ Colors match the brand (dark greens, no default blue or black)
```

### Step 4 — Fix and re-verify

When issues are found:

1. **Missing chrome element** (most common): the slide skipped `apply_brand_chrome()` or called it with dark_header=True where wrong. Fix and re-render.

2. **Logo resized large**: check the `width=Inches(0.51), height=Inches(0.80)` args in `add_picture`. Reset to those exact values.

3. **Text overflow / font too large**: Reduce `size_pt` in the `set_tf()` call. Reference the size limits in the Shape Position Reference section.

4. **`[ ]` placeholder still showing**: The shape was not matched. Re-check the x/y coordinates and tighten the position match.

5. **Stray text in bottom-right**: A `set_tf()` call accidentally targeted the Slide Number Placeholder. Add a guard: `if 'slide number' in sh.name.lower(): continue`.

6. **Wrong slide count**: The ZIP trim KEEP value is wrong, or the trim script didn't run.

7. **After any fix**: Re-run `prs.save(WORK)` → re-run the ZIP trim → re-run the PDF conversion → re-inspect the affected slides.

**Do not declare success until you have completed at least one full fix-and-re-verify cycle with zero new issues found — and until every slide has passed the chrome check.**

### Step 5 — Programmatic text checks

Run this after visual QA to catch any remaining placeholder text:

```bash
python -m markitdown /home/claude/deck_final.pptx | grep -E "\[ \]|Add text|Click to edit"
```

If this returns results, those slides still have unfilled template placeholders.
