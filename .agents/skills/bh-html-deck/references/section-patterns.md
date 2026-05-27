# Section patterns

Every deck follows a similar arc:

```
Hero  →  S1 Platform (scrolly)  →  S1b Benefits  →  S2 Roles  →  S3 Modes  →  S4 Flow  →  Flywheel callout  →  Footnotes  →  Footer
```

You can skip sections if they don't apply, but maintain the order. The diagram (mounted in S1, S3, S4) is the through-line.

## Hero

```html
<header class="hero">
  <div class="container hero-inner">
    <div class="hero-lockup">
      <img class="bh-mark" src="assets/bh-logo-desktop.svg" alt="Birch Hill"/>
      <span class="sep">×</span>
      <img class="tempo-wordmark-hero" src="assets/wordmark-white.svg" alt="Tempo"/>
    </div>
    <div class="hero-eyebrow">Joint working session · [Counterparty Name]</div>
    <h1 class="hero-title">[The deck title across two lines]</h1>
    <p class="hero-sub">[One-sentence positioning statement]</p>
    <div class="hero-meta">
      <div class="hero-meta-item"><span class="lbl">Presented by</span><span class="val">...</span></div>
      <div class="hero-meta-item"><span class="lbl">For</span><span class="val">[Counterparty]</span></div>
      <div class="hero-meta-item"><span class="lbl">Date</span><span class="val">[Month YYYY]</span></div>
      <div class="hero-meta-item"><span class="lbl">Classification</span><span class="val">Proprietary &amp; Confidential</span></div>
    </div>
  </div>
  <div class="hero-scroll"><span>Scroll</span><span class="line"></span></div>
</header>
```

The hero uses `align-items: flex-start` with `padding-top: 110px` so content top-aligns. Background is `var(--bh-emerald-deepest)` with a tree silhouette SVG at the bottom 320px. The subtitle should sit visually above the tree color break.

## Section shell

```html
<section class="section" id="section-platform" data-section="section-platform">
  <div class="container">
    <div style="max-width: 900px;">
      <div class="section-eyebrow"><span class="num">01</span>The Platform</div>
      <h2 class="section-title">[Headline statement.]</h2>
      <p class="section-sub">[1–2 sentence subhead.]</p>
    </div>
    <!-- content -->
  </div>
</section>
```

The `data-section` attribute powers top-nav active state. Use `.section.dark` for dark-background sections (typically S3, sometimes hero).

## Scrollytelling (Section 1)

```html
<div class="scrolly">
  <div class="scrolly-narration">

    <div class="scrolly-step is-active" data-beat="empty" data-target="platform">
      <div class="step-eyebrow"><span class="marker"></span>[Intro label]</div>
      <h4>[Intro headline.]</h4>
      <p>[Body paragraph.]</p>
    </div>

    <div class="scrolly-step" data-beat="s1_v1" data-target="platform">
      <div class="step-eyebrow"><span class="marker"></span>Circuit 1 — Underwriting</div>
      <h4>[Headline for circuit 1.]</h4>
      <ol><li>[Bullet]</li>...</ol>
    </div>

    <!-- ...continue for s1_origination, s1_v2, s1_engines, s1_ops... -->

  </div>

  <div class="diagram-stage">
    <div class="diagram-wrap" id="platform-diagram"></div>
  </div>
</div>
```

The grid is `340px 1fr` — narration on the left, sticky diagram on the right. Each step has `data-beat="<beat-name>"` matching a key in the controller's `B` object, and `data-target="platform"` to apply it to the platform-diagram mount.

The first step is `data-beat="empty"` and uses the all-on `B.empty` beat so the intro shows the full platform.

## Benefits grid (Section 1b)

```html
<div class="benefits">
  <div class="benefit">
    <div class="num">01</div>
    <h4>[Benefit headline.]</h4>
    <p>[1–2 sentences.]</p>
  </div>
  <!-- 4 more -->
</div>
```

`grid-template-columns: repeat(5, 1fr)` — five equal columns. Each card has a serif number, a serif headline, and a body paragraph.

## Role cards (Section 2)

```html
<div class="roles-grid">
  <div class="role-card" data-role="cantor">
    <span class="role-chev">+</span>
    <div class="role-cat">Originator</div>
    <h4>Cantor Fitzgerald</h4>
    <div class="role-line">[One-sentence role summary.]</div>
    <div class="role-detail">[Longer detail shown when card is open.]</div>
  </div>
  <!-- more cards -->
</div>
```

The `data-role` attribute is the key the controller looks up in `rolePulses`. Update `controller.js` `rolePulses` to map every role to its corresponding node ID(s).

Cards toggle open on click. Open cards turn dark green with white text. The matching node in the platform diagram pulses (brief scale + glow).

A `<div class="service-stack">` at the bottom of Section 2 lists service providers (Counsel, Custody, Audit, etc.) inline.

## Mode toggle (Section 3)

```html
<div class="modes-shell">
  <div class="modes-controls">
    <div class="mode-toggle">
      <button data-mode="A" class="is-on"><span>Mode A · Warehouse Seed</span><span class="badge">$25M</span></button>
      <button data-mode="B"><span>Mode B · RWA Anchor</span><span class="badge">$35M</span></button>
      <button data-mode="C"><span>Combined · Day-1 Deployment</span><span class="badge">$60M</span></button>
    </div>

    <div class="mode-panel" data-mode-panel="A" style="display:block;">
      <div class="m-tag">Mode A · Engine 1 → Credit Facility</div>
      <h3>[Mode A headline.]</h3>
      <div class="m-money">$25M<small>into the [target]</small></div>
      <ul><li>...</li></ul>
      <div class="m-fn">Function</div>
      <div class="m-fn-text">[Function summary.]</div>
    </div>
    <!-- Mode B panel hidden by default -->
    <!-- Combined panel hidden by default -->
  </div>

  <div class="mode-diagram" id="mode-diagram"></div>
</div>
```

The controller's `setMode()` handler swaps which panel is visible and applies `B.modeA` / `B.modeB` / `B.modeCombined` to the mode-diagram mount.

## Flow rail (Section 4)

```html
<div class="flow-shell">
  <div class="flow-control">
    <div class="flow-rail">
      <button data-step="1" class="is-on">
        <span class="rn">01</span><span class="rt">[Step title]</span><span class="rd">→</span>
      </button>
      <!-- steps 2-8 -->
    </div>

    <div class="flow-step-card" data-step-card="1">
      <div class="fsc-eyebrow">Step 01 · [Phase]</div>
      <h4>[Step headline.]</h4>
      <p>[Body.]</p>
      <div class="step-money">
        <span class="lbl">[Money label]</span>
        <span class="v">$25M</span>
        <span style="font-size:11px;">[Subcaption]</span>
      </div>
    </div>
    <!-- step cards 2-8 hidden by default via [hidden] -->

    <div class="flow-nav">
      <button id="flow-prev" class="secondary">← Prev</button>
      <button id="flow-next">Next →</button>
      <button id="flow-reset" class="secondary">Reset</button>
      <span class="progress" id="flow-progress"><strong>01</strong> / 08</span>
    </div>
  </div>

  <div class="flow-diagram">
    <div class="diagram-wrap" id="flow-diagram"></div>
  </div>
</div>
```

Grid `420px 1fr`. Left column is sticky. Step buttons use `data-step="N"` which the controller maps to `B.stepN` beats. Right arrow / left arrow keyboard shortcuts also work when Section 4 is in view.

## Flywheel callout

```html
<div class="flywheel-callout">
  <div class="icon"><svg viewBox="0 0 72 72">...</svg></div>
  <div>
    <h3>[Closing summary headline.]</h3>
    <p>[Body paragraph wrapping up the flow.]</p>
  </div>
</div>
```

Dark emerald background, serif headline, sage circle icon. Closes Section 4.

## Footnotes

```html
<div class="footnotes">
  <h5>Open items · for resolution in working session</h5>
  <p>[Open item 1]</p>
  <p>[Open item 2]</p>
</div>
```

Small uppercase header, em-dash bullets, cream background. For unresolved questions you want to flag explicitly to the counterparty.

## Footer

```html
<footer class="foot">
  <div class="container">
    <div class="marks">
      <img src="assets/bh-logo-desktop.svg" alt="Birch Hill"/>
      <span class="sep">×</span>
      <img class="tempo-wordmark-foot" src="assets/wordmark-white.svg" alt="Tempo"/>
    </div>
    <div class="legal">[Engagement description] · [Date] · Proprietary &amp; Confidential</div>
  </div>
</footer>
```

## Top nav (sticky)

```html
<nav class="topnav dark">
  <div class="topnav-inner">
    <div class="topnav-brand">
      <img src="assets/bh-logo-mark.svg" alt="Birch Hill" style="height:22px; width:auto;"/>
      <span class="topnav-brand-word">Birch Hill</span>
      <span class="x-sep">×</span>
      <img src="assets/wordmark-white.svg" alt="Tempo" class="tempo-wordmark-nav"/>
    </div>
    <div class="topnav-links">
      <a class="topnav-link" href="#section-platform">01 · Platform</a>
      <a class="topnav-link" href="#section-roles">02 · Roles</a>
      <a class="topnav-link" href="#section-modes">03 · Go-to-Market</a>
      <a class="topnav-link" href="#section-flow">04 · Flow of Funds</a>
    </div>
  </div>
</nav>
```

Toggles `dark` class based on whether the hero is in view (`heroIo` observer). The Tempo wordmark uses CSS `filter: invert()` to flip from white (over hero) to dark (over content).
