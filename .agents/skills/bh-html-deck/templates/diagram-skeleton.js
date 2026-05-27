/* ─────────────────────────────────────────────────────────────────────────────
   Diagram skeleton — adapt for the new client.

   The `buildDiagram(idSuf)` function returns the full SVG as a string with every
   addressable element's ID suffixed by idSuf. The same SVG is mounted up to
   three times: "-p" platform, "-f" flow, "-m" mode.

   To adapt:
     1. Update the palette `C` with any client-specific fills/strokes
     2. Lay out the node positions (column grid + pivot)
     3. Define edges with paths matching node positions
     4. Wire step badges to the right arrows
     5. Position dollar callouts in clear empty areas

   Helpers provided:
     rectNode(id, x, y, w, h, label, sub, opts)   — standard rectangle node
     circleNode(id, cx, cy, r, opts)              — for the pivot
     diamondNode(id, cx, cy, halfW, halfH, lbl, sub, opts)
     edge(id, d, opts)                            — arrow path
     edgeLabel(id, x, y, text, opts)              — text label
     stepBadge(id, cx, cy, n)                     — numbered circle
     dollarCallout(id, x, y, value, sub)          — money chip
     groupFrame(id, x, y, w, h, label, opts)      — dashed rect + tab label
   ───────────────────────────────────────────────────────────────────────────── */
(function () {
  // ─── Palette ────────────────────────────────────────────────────────────────
  const C = {
    // Brand greens
    bhGreen: "#00693E",
    bhDark: "#0F2E2C",

    // Capital sources / counterparties (lighten the variant)
    warehouseFill: "#E3EEF8", warehouseStroke: "#5D89B4",
    instFill: "#E0EBE0", instStroke: "#6B8F73",
    stablendFill: "#E8EFE2", stablendStroke: "#85A06A",

    // The counterparty being engaged (warm gold for visibility)
    cantorFill: "#F0D58A", cantorStroke: "#C39C40",
    bsFill: "#FBEFD0", bsStroke: "#C39C40",

    // SPV / Buy Box / Strata (lilac/purple plumbing)
    spvFill: "#E8DDF2", spvStroke: "#8B6CB7",
    strataFill: "#C9B7E0", strataStroke: "#7E5BAF",

    // Treasuries / MMFs (pale mint)
    treasFill: "#EAF3EC", treasStroke: "#A0BFA6",

    // Morpho (navy)
    morphoFill: "#1F4F7A",

    // Engines (sage)
    engine1Fill: "#C8E2CF", engine1Stroke: "#6F9879",
    engine2Fill: "#DDE9CC", engine2Stroke: "#8AA770",

    // Edge colors
    edgeDefault: "#7A8B7E",
    edgeHot:     "#00693E",
    edgeCash:    "#5D89B4",
    edgeSec:     "#C39C40",
    edgeCollat:  "#7E5BAF",
    edgeEngine:  "#6F9879",

    text:       "#0F2E2C",
    textOnDark: "#FFFFFF",
  };

  // ─── Helpers ────────────────────────────────────────────────────────────────
  function rectNode(id, x, y, w, h, label, sub, opts = {}) {
    const fill   = opts.fill || C.bhGreen;
    const stroke = opts.stroke || "none";
    const radius = opts.radius != null ? opts.radius : 8;
    const labelColor = opts.dark ? C.textOnDark : C.text;
    const subColor   = opts.dark ? "rgba(255,255,255,0.78)" : "#455046";
    const lines = (opts.lines || [label]).filter(Boolean);
    const cx = x + w / 2;
    const lineHeight = 15;
    const subHeight  = sub ? 16 : 0;
    const totalTextHeight = (lines.length - 1) * lineHeight + subHeight;
    const startY = y + h / 2 + 4 - totalTextHeight / 2;
    return `
      <g class="node" data-node="${id}" id="${id}">
        <rect class="node-fill" x="${x}" y="${y}" width="${w}" height="${h}"
              rx="${radius}" fill="${fill}" stroke="${stroke}" stroke-width="${stroke === "none" ? 0 : 1.5}"/>
        ${lines.map((ln, i) => `
          <text class="node-label" x="${cx}" y="${startY + i * lineHeight}"
                text-anchor="middle" fill="${labelColor}">${ln}</text>`).join("")}
        ${sub ? `<text class="node-sub" x="${cx}" y="${y + h - 12}"
                  text-anchor="middle" fill="${subColor}">${sub}</text>` : ""}
      </g>`;
  }

  function diamondNode(id, cx, cy, halfW, halfH, label, sub, opts = {}) {
    const fill = opts.fill || C.bhGreen;
    const p = `M${cx},${cy - halfH} L${cx + halfW},${cy} L${cx},${cy + halfH} L${cx - halfW},${cy} Z`;
    return `
      <g class="node" data-node="${id}" id="${id}">
        <path class="node-fill" d="${p}" fill="${fill}" stroke="none"/>
        <text class="node-label" x="${cx}" y="${cy - 2}" text-anchor="middle" fill="${C.textOnDark}">${label}</text>
        <text class="node-sub" x="${cx}" y="${cy + 16}" text-anchor="middle" fill="rgba(255,255,255,0.82)">${sub || ""}</text>
      </g>`;
  }

  // Circle node for the pivot. Custom inner text layout.
  function circleNode(id, cx, cy, r, opts = {}) {
    const fill = opts.fill || C.bsFill;
    const stroke = opts.stroke || C.bsStroke;
    const eyebrow = opts.eyebrow || "WHERE  THE  CIRCUITS  MEET";
    const titleLines = opts.titleLines || ["Cantor's", "Balance Sheet"];
    const subtitle = opts.subtitle || "the pivot";
    const lh = 22;
    const topYBase = cy - (titleLines.length - 1) * lh / 2 - 4;
    return `
      <g class="node node-pivot" data-node="${id}" id="${id}">
        <circle class="node-fill" cx="${cx}" cy="${cy}" r="${r}"
                fill="${fill}" stroke="${stroke}" stroke-width="2.5"/>
        <text class="pivot-eyebrow" x="${cx}" y="${cy - r * 0.36}" text-anchor="middle"
              fill="#6B7B6F" font-size="9" font-weight="700"
              letter-spacing="0.22em">${eyebrow}</text>
        ${titleLines.map((line, i) => `
        <text x="${cx}" y="${topYBase + i * lh}" text-anchor="middle"
              font-family="Versailles LT Std, Georgia, serif" font-size="18"
              fill="${C.text}">${line}</text>`).join("")}
        <text x="${cx}" y="${cy + r * 0.52}" text-anchor="middle"
              font-family="Inter, sans-serif" font-size="10.5" font-style="italic"
              fill="#7A6A40">${subtitle}</text>
      </g>`;
  }

  function edge(id, d, opts = {}) {
    const stroke = opts.stroke || C.edgeDefault;
    const width  = opts.width || 1.6;
    const dash   = opts.dash ? `stroke-dasharray="${opts.dash === true ? "5 4" : opts.dash}"` : "";
    const markerId = opts.markerKey || "arrow";
    const arrow  = opts.noArrow ? "" : `marker-end="url(#${markerId}-${opts.suf})"`;
    const cls    = `edge ${opts.cls || ""}`.trim();
    return `<path class="${cls}" id="${id}" d="${d}"
              stroke="${stroke}" stroke-width="${width}" fill="none" ${arrow} ${dash}/>`;
  }

  function edgeLabel(id, x, y, text, opts = {}) {
    const anchor = opts.anchor || "middle";
    const fill = opts.fill || "#455046";
    const cls = `edge-label ${opts.cls || ""}`.trim();
    return `<text class="${cls}" id="${id}" x="${x}" y="${y}"
              text-anchor="${anchor}" fill="${fill}">${text}</text>`;
  }

  function stepBadge(id, cx, cy, n) {
    return `
      <g class="step-badge" id="${id}" data-step="${n}">
        <circle cx="${cx}" cy="${cy}" r="13" fill="#FFFFFF" stroke="#00693E" stroke-width="1.6"/>
        <text x="${cx}" y="${cy + 4}" text-anchor="middle"
              font-family="Inter, sans-serif" font-size="11" font-weight="700" fill="#00693E">${n}</text>
      </g>`;
  }

  function dollarCallout(id, x, y, value, sub) {
    return `
      <g class="dollar" data-dollar="${id}" id="${id}">
        <rect class="dollar-bg" x="${x - 70}" y="${y - 32}" width="140" height="48"
              rx="6" fill="#00693E"/>
        <text class="dollar-v" x="${x}" y="${y - 12}" text-anchor="middle" fill="#FFFFFF"
              font-family="Versailles LT Std, serif" font-size="22" font-weight="400"
              letter-spacing="-0.02em">${value}</text>
        <text class="sub" x="${x}" y="${y + 6}" text-anchor="middle"
              fill="rgba(255,255,255,0.88)" font-family="Inter, sans-serif"
              font-size="9.5" font-weight="600" letter-spacing="0.08em"
              text-transform="uppercase">${sub}</text>
      </g>`;
  }

  function groupFrame(id, x, y, w, h, label, opts = {}) {
    const tabFill = opts.tabFill || "#0F2E2C";
    const frameStroke = opts.frameStroke || "#A8B8AA";
    const tabWidth = label.length * 6.4 + 36;
    const tabX = x + (w - tabWidth) / 2;
    return `
      <g class="group-region" data-group="${id}">
        <rect class="group-frame" id="${id}" x="${x}" y="${y}" width="${w}" height="${h}"
              rx="10" fill="${opts.fill || "none"}" stroke="${frameStroke}" stroke-width="1"
              stroke-dasharray="3 5" opacity="${opts.frameOpacity || 0.55}"/>
        <rect class="group-tab" x="${tabX}" y="${y - 11}" width="${tabWidth}" height="22"
              rx="4" fill="${tabFill}"/>
        <text class="group-label" id="${id}-label" x="${x + w / 2}" y="${y + 4}"
              text-anchor="middle" fill="#FFFFFF" font-family="Inter, sans-serif"
              font-size="10.5" font-weight="700" letter-spacing="0.22em">${label}</text>
      </g>`;
  }

  // ─── Build the SVG ──────────────────────────────────────────────────────────
  function buildDiagram(idSuf) {
    const s = (n) => `${n}-${idSuf}`;
    return `
<svg class="diagram-svg" viewBox="0 0 1200 1400" preserveAspectRatio="xMidYMid meet"
     xmlns="http://www.w3.org/2000/svg" aria-label="[CLIENT] Platform diagram">

  <defs>
    <marker id="arrow-${idSuf}" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="${C.edgeDefault}"/>
    </marker>
    <marker id="arrow-hot-${idSuf}" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="${C.edgeHot}"/>
    </marker>
    <marker id="arrow-cash-${idSuf}" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="${C.edgeCash}"/>
    </marker>
    <marker id="arrow-sec-${idSuf}" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="${C.edgeSec}"/>
    </marker>
    <marker id="arrow-collat-${idSuf}" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="${C.edgeCollat}"/>
    </marker>
    <marker id="arrow-engine-${idSuf}" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="${C.edgeEngine}"/>
    </marker>

    <!-- Figure-8 background ring gradients (delete if not using figure-8 metaphor) -->
    <radialGradient id="ringCashGrad-${idSuf}" cx="50%" cy="50%" r="60%">
      <stop offset="0%"   stop-color="#5D89B4" stop-opacity="0.22"/>
      <stop offset="60%"  stop-color="#5D89B4" stop-opacity="0.07"/>
      <stop offset="100%" stop-color="#5D89B4" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="ringSecGrad-${idSuf}" cx="50%" cy="50%" r="60%">
      <stop offset="0%"   stop-color="#C39C40" stop-opacity="0.22"/>
      <stop offset="60%"  stop-color="#C39C40" stop-opacity="0.07"/>
      <stop offset="100%" stop-color="#C39C40" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="pivotGlow-${idSuf}" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#F0D58A" stop-opacity="0.65"/>
      <stop offset="55%"  stop-color="#F0D58A" stop-opacity="0.20"/>
      <stop offset="100%" stop-color="#F0D58A" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <!-- BACKGROUND — figure-8 ellipses (REPLACE / REMOVE if not using this metaphor) -->
  <ellipse cx="600" cy="395" rx="560" ry="310" fill="url(#ringCashGrad-${idSuf})"/>
  <ellipse cx="600" cy="985" rx="580" ry="285" fill="url(#ringSecGrad-${idSuf})"/>
  <ellipse cx="600" cy="395" rx="555" ry="305" fill="none"
           stroke="#5D89B4" stroke-width="1.2" stroke-dasharray="2 7" opacity="0.34"/>
  <ellipse cx="600" cy="985" rx="575" ry="280" fill="none"
           stroke="#C39C40" stroke-width="1.2" stroke-dasharray="2 7" opacity="0.34"/>

  <!-- Central vertical spine -->
  <line x1="600" y1="80" x2="600" y2="1200"
        stroke="#0F2E2C" stroke-width="0.7" stroke-dasharray="2 7" opacity="0.20"/>

  <!-- CIRCUIT 01 TITLE — replace narrative -->
  <text id="${s("l-c1-eyebrow")}" x="600" y="38" text-anchor="middle"
        font-family="Inter, sans-serif" font-size="11" font-weight="700"
        letter-spacing="0.42em" text-transform="uppercase" fill="#6B7B6F">CIRCUIT  01</text>
  <text id="${s("l-c1-title")}" x="600" y="68" text-anchor="middle"
        font-family="Versailles LT Std, Georgia, serif" font-size="26"
        font-style="italic" fill="#0F2E2C">[Top circuit verb].</text>

  <!-- ═══════════════ EDGES (draw before nodes) ═══════════════ -->
  <!-- Example edges — REPLACE with the actual flows for this engagement.
       Use the s() helper for IDs. Pass markerKey to color-code the arrow head. -->

  ${edge(s("e-example"), "M600,168 L600,188", { suf: idSuf, stroke: C.edgeCash, width: 2.2, markerKey: "arrow-cash" })}
  ${edgeLabel(s("l-example"), 615, 182, "example label", { anchor: "start", fill: "#3F5C7D", cls: "cash" })}

  <!-- ═══════════════ NODES ═══════════════ -->
  <!-- Use rectNode for boxes, diamondNode for the QA gate, circleNode for the pivot. -->

  ${rectNode(s("n-example1"), 490, 100, 220, 68, "Example Node", "subtitle",
        { fill: C.warehouseFill, stroke: C.warehouseStroke })}

  ${circleNode(s("n-pivot"), 600, 700, 85, {
    titleLines: ["Pivot's", "Big Name"],
    subtitle: "the pivot"
  })}

  <!-- ═══════════════ STEP BADGES ═══════════════ -->
  ${stepBadge(s("b-step1"), 760, 404, 1)}

  <!-- ═══════════════ DOLLAR CALLOUTS ═══════════════ -->
  ${dollarCallout(s("d-example"), 385, 250, "$25M", "example caption")}

</svg>`;
  }

  window.buildBHDiagram = buildDiagram;
})();
