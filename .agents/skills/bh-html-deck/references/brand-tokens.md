# Birch Hill brand tokens

The full design system lives in `colors_and_type.css`. Copy this file verbatim from any existing deck — **never modify it per-deck**. If a brand update is needed, update the source repo (`birch-hill-labs/birch-hill-ui`) and propagate.

## Color tokens — the family

```
--bh-emerald-deepest:  #001F1E    /* Hero / dark section backgrounds */
--bh-emerald-footer:   #012120    /* Footer background */
--bh-emerald-dark:     #103F3D    /* Dark CTAs (Tempo Series LLC anchor card fill) */
--bh-emerald-tile:     #17423C    /* Card tiles */
--bh-emerald-rich:     #195E3B    /* Primary-hover / accent dark */
--bh-emerald-section:  #25584C    /* Mid-section header tile */
--bh-primary:          #00693E    /* PRIMARY — CTA / link / hot-edge highlight */
--bh-primary-bright:   #0B7C4A    /* Secondary CTA */
--bh-accent:           #55A461    /* Positive metric / success */
--bh-sage:             #78A291    /* Desaturated tile bg */
--bh-sage-soft:        #88AE83    /* Label color / chip / gradient stop */
--bh-sage-pale:        #A6D3B3    /* Accent-pale */
--bh-mint-pale:        #B2C4A9    /* Framework gradient top */
--bh-cream-bg:         #EEFAE8
--bh-cream-tint:       #F3F8F4    /* Page background */
--bh-cream-divider:    #F0F5F1    /* Subtle dividers / hover backgrounds */
--bh-gold:             #EAD2A8    /* On-dark accents only — fine print, regulatory */
```

**Quick rule:** any non-brand color in a Birch Hill deliverable needs a reason. The Cantor diagram uses some bespoke palette beyond the BH greens (the cantor gold `#F0D58A`, Morpho navy `#1F4F7A`, lilac `#E8DDF2`, etc.) because those represent specific external entities — not BH-controlled surfaces. Brand surfaces (the Vault 1 box, the QA Keeper diamond, the Fence card) always use BH greens.

## Diagram-specific palette additions

These extend the brand system for the diagram's narrative coding. They are reused across decks for consistent storytelling:

```
/* Flow colors */
edgeCash:   #5D89B4    /* Cash flows — blue */
edgeSec:    #C39C40    /* Securities flows — gold */
edgeHot:    #00693E    /* Facility events (same as BH primary) */
edgeCollat: #7E5BAF    /* Collateral / legal plumbing — purple */
edgeEngine: #6F9879    /* Anchor capital — sage */

/* Counterparty fills */
warehouseFill:  #E3EEF8 / warehouseStroke: #5D89B4    /* light blue */
instFill:       #E0EBE0 / instStroke:      #6B8F73    /* sage */
stablendFill:   #E8EFE2 / stablendStroke:  #85A06A    /* mint */
cantorFill:     #F0D58A / cantorStroke:    #C39C40    /* gold (warm) */
bsFill:         #FBEFD0 / bsStroke:        #C39C40    /* cream gold (balance sheet) */
spvFill:        #E8DDF2 / spvStroke:       #8B6CB7    /* lilac */
strataFill:     #C9B7E0 / strataStroke:    #7E5BAF    /* purple */
treasFill:      #EAF3EC / treasStroke:     #A0BFA6    /* pale mint */
morphoFill:     #1F4F7A                              /* deep navy */
engine1Fill:    #C8E2CF / engine1Stroke:   #6F9879    /* sage */
engine2Fill:    #DDE9CC / engine2Stroke:   #8AA770    /* sage variant */
```

## Type

**Display:** Versailles LT Std (Light 300, Roman 400, Bold 700, Black 900). Used for hero, section headers, big numerics, "Cantor's Balance Sheet" inside the pivot circle.

**Body / UI:** Inter (200, 300, 400, 500, 600, 700). Used for everything else.

**Mono:** Geist Mono (only for code snippets, rare in client decks).

## Type scale (root 16px)

```
--fs-micro:       12px   /* uppercase eyebrow */
--fs-small:       14px   /* supporting */
--fs-body:        16px   /* body */
--fs-h3:          20px
--fs-h2:          24px
--fs-h1:          32px
--fs-display:     40px
--fs-display-lg:  48px   /* section opener */
--fs-display-xl:  60px   /* hero */
```

Hero title and section titles use `clamp()` for responsive scaling — e.g., `font-size: clamp(48px, 6.4vw, 88px)` for the hero.

## Spacing — 4px base

```
--space-1: 4px
--space-2: 8px
--space-3: 12px
--space-4: 16px
--space-5: 24px
--space-6: 32px
--space-7: 48px
--space-8: 64px
--space-9: 96px
```

Use `var(--space-N)` consistently. Sections use `--space-9` for vertical padding, grids use `--space-7` for column gaps.

## Motion

```
--ease-out:      cubic-bezier(0.2, 0.6, 0.2, 1)     /* preferred for most transitions */
--ease-in-out:   cubic-bezier(0.4, 0, 0.2, 1)
--duration-fast: 140ms
--duration-base: 220ms
--duration-slow: 320ms
```

Use `--duration-base` for diagram node/edge state transitions, `--duration-slow` for scrollytelling step fades.

## Layout

```
--content-max: 1280px
--content-px:  24px
```

The `.container` class uses `max-width: 1320px; margin: 0 auto; padding: 0 var(--space-7)`. Slightly wider than the token's `--content-max` — that's intentional for client decks where horizontal real estate matters.
