/* ─────────────────────────────────────────────────────────────────────────────
   Controller skeleton — adapt beat definitions and pulse map to your nodes.

   Defines:
     · applyBeat()      — toggles is-on/is-dim/is-hot/is-pulse classes
     · withSuf()        — appends mount-point suffix to bare IDs
     · union()          — merges beat sets
     · buildStep()      — builds a step beat that dims everything not hot
     · B.empty          — intro state, every main element on
     · B.s1_v1..s1_ops  — Section 1 progressive build beats
     · B.step1..step8   — Section 4 step beats
     · B.modeA/B/Combined — Section 3 mode beats
     · rolePulses       — Section 2 role-card → node mapping
   ───────────────────────────────────────────────────────────────────────────── */
(function () {
  const D = {};

  function mountDiagram(container, idSuf) {
    container.innerHTML = window.buildBHDiagram(idSuf);
    return container.querySelector("svg.diagram-svg");
  }

  function applyBeat(svg, beat) {
    if (!svg) return;
    const onSet     = new Set(beat.on     || []);
    const dimSet    = new Set(beat.dim    || []);
    const hotSet    = new Set(beat.hot    || []);
    const pulseSet  = new Set(beat.pulse  || []);
    const dollarSet = new Set(beat.dollars|| []);
    const stepN     = beat.step;

    svg.querySelectorAll(".node").forEach((n) => {
      n.classList.remove("is-on", "is-dim", "is-pulse", "is-hot");
      if (hotSet.has(n.id))         n.classList.add("is-on", "is-hot");
      else if (pulseSet.has(n.id))  n.classList.add("is-on");
      else if (onSet.has(n.id))     n.classList.add("is-on");
      else if (dimSet.has(n.id))    n.classList.add("is-dim");
      if (pulseSet.has(n.id)) {
        n.classList.remove("is-pulse");
        void n.offsetWidth;
        n.classList.add("is-pulse");
      }
    });
    svg.querySelectorAll(".group-frame").forEach((f) => {
      f.classList.remove("is-on", "is-dim");
      if (onSet.has(f.id) || hotSet.has(f.id)) f.classList.add("is-on");
      else if (dimSet.has(f.id)) f.classList.add("is-dim");
    });
    svg.querySelectorAll(".edge").forEach((e) => {
      e.classList.remove("is-on", "is-dim", "is-hot");
      if (hotSet.has(e.id))     e.classList.add("is-on", "is-hot");
      else if (onSet.has(e.id)) e.classList.add("is-on");
      else if (dimSet.has(e.id)) e.classList.add("is-dim");
    });
    svg.querySelectorAll(".edge-label").forEach((l) => {
      l.classList.remove("is-on", "is-dim", "is-hot");
      if (hotSet.has(l.id))     l.classList.add("is-on", "is-hot");
      else if (onSet.has(l.id)) l.classList.add("is-on");
      else if (dimSet.has(l.id)) l.classList.add("is-dim");
    });
    svg.querySelectorAll(".dollar").forEach((d) => {
      d.classList.toggle("is-on", dollarSet.has(d.id));
    });
    svg.querySelectorAll(".step-badge").forEach((b) => {
      const n = parseInt(b.getAttribute("data-step"));
      b.classList.toggle("is-on", n === stepN);
    });
  }

  function withSuf(beat, suf) {
    const map = (arr) => (arr || []).map((id) => `${id}-${suf}`);
    return {
      on: map(beat.on), dim: map(beat.dim), hot: map(beat.hot),
      pulse: map(beat.pulse), dollars: map(beat.dollars),
      step: beat.step,
    };
  }
  function union(...beats) {
    const u = { on: [], dim: [], hot: [], pulse: [], dollars: [] };
    for (const b of beats) {
      for (const k of Object.keys(u)) u[k] = u[k].concat(b[k] || []);
    }
    if (beats.some((b) => b.step != null)) u.step = beats.filter(b => b.step != null).slice(-1)[0].step;
    return u;
  }

  // ─── Beat library — REPLACE node IDs with your diagram's ──────────────────
  const B = {};

  // B.empty must have every main element on so the intro shows the full platform
  B.empty = {
    on: [
      "l-c1-eyebrow", "l-c1-title", "l-c2-eyebrow", "l-c2-title",
      // ALL nodes
      // ALL edges + labels
      // ALL group frames (g-engines, g-ops, etc.)
    ],
  };

  // Section 1 progressive build beats
  B.s1_v1 = {
    on: [
      "l-c1-eyebrow", "l-c1-title",
      // Circuit 1 nodes + their edges
    ],
  };
  B.s1_origination = union(B.s1_v1, {
    on: [/* origination nodes + edges */],
  });
  B.s1_v2 = union(B.s1_origination, {
    on: ["l-c2-eyebrow", "l-c2-title", /* Circuit 2 nodes + edges */],
  });
  B.s1_engines = union(B.s1_v2, {
    on: ["g-engines", /* engine nodes + edges */],
  });
  B.s1_ops = union(B.s1_engines, {
    on: ["g-ops", /* operational infrastructure nodes + edges */],
  });

  // Section 2 role-card → pulse mapping
  const rolePulses = {
    // role-card data-role value : { pulse: [node IDs] }
    // Example:
    // cantor: { pulse: ["n-cantor"] },
    // tempo:  { pulse: ["n-engine1", "n-engine2"] },
  };

  // Section 4 step beats. buildStep dims everything in s1_ops that isn't hot.
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

  B.step1 = buildStep(1, [/* hot IDs */]);
  B.step2 = buildStep(2, [/* hot IDs */]);
  B.step3 = buildStep(3, [/* hot IDs */], ["d-step3"]);
  B.step4 = buildStep(4, [/* hot IDs */]);
  B.step5 = buildStep(5, [/* hot IDs */]);
  B.step6 = buildStep(6, [/* hot IDs */], ["d-step6"]);
  B.step7 = buildStep(7, [/* hot IDs */], ["d-step7-buy", "d-step7-idle"]);
  B.step8 = buildStep(8, [/* hot IDs */], ["d-step8"]);

  // Section 3 mode beats
  B.modeA = buildStep(null, [/* Mode A path */], ["d-engine1-v1"]);
  B.modeB = buildStep(null, [/* Mode B path */], ["d-engine1-v2"]);
  B.modeCombined = union(B.modeA, B.modeB, {
    dollars: ["d-engine1-v1", "d-engine1-v2", "d-combined"],
  });

  // ─── Wire up ──────────────────────────────────────────────────────────────
  function init() {
    const platformStage = document.getElementById("platform-diagram");
    const flowStage     = document.getElementById("flow-diagram");
    const modeStage     = document.getElementById("mode-diagram");

    if (platformStage) D.platform = { svg: mountDiagram(platformStage, "p") };
    if (flowStage)     D.flow     = { svg: mountDiagram(flowStage, "f") };
    if (modeStage)     D.mode     = { svg: mountDiagram(modeStage, "m") };

    if (D.platform) applyBeat(D.platform.svg, withSuf(B.s1_ops, "p"));
    if (D.flow)     applyBeat(D.flow.svg,     withSuf(B.step1, "f"));
    if (D.mode)     applyBeat(D.mode.svg,     withSuf(B.modeA, "m"));

    // Section 1 scrollytelling observer
    const scrollySteps = document.querySelectorAll("[data-beat]");
    let currentBeatKey = null;
    const io = new IntersectionObserver(() => {
      const visible = [...scrollySteps].filter((el) => {
        const r = el.getBoundingClientRect();
        return r.top < window.innerHeight * 0.55 && r.bottom > window.innerHeight * 0.2;
      });
      const active = visible[visible.length - 1] || visible[0];
      if (!active) return;
      scrollySteps.forEach((s) => s.classList.toggle("is-active", s === active));
      const beatName = active.getAttribute("data-beat");
      const target   = active.getAttribute("data-target") || "platform";
      const suf      = target === "platform" ? "p" : (target === "flow" ? "f" : "m");
      if (beatName && B[beatName] && D[target]) {
        const key = beatName + ":" + target;
        if (currentBeatKey !== key) {
          currentBeatKey = key;
          applyBeat(D[target].svg, withSuf(B[beatName], suf));
        }
      }
    }, { rootMargin: "-30% 0% -40% 0%", threshold: [0, 0.5, 1] });
    scrollySteps.forEach((el) => io.observe(el));

    // Section 2 role cards
    const roleCards = document.querySelectorAll(".role-card");
    roleCards.forEach((card) => {
      card.addEventListener("click", () => {
        const wasOpen = card.classList.contains("is-open");
        roleCards.forEach((c) => c.classList.remove("is-open"));
        if (!wasOpen) card.classList.add("is-open");
        const roleKey = card.getAttribute("data-role");
        const pulseBeat = rolePulses[roleKey];
        if (pulseBeat && D.platform) {
          applyBeat(D.platform.svg, withSuf(union(B.s1_ops, pulseBeat), "p"));
        }
      });
    });

    // Section 3 mode toggle
    const modeButtons = document.querySelectorAll("[data-mode]");
    function setMode(mode) {
      modeButtons.forEach((b) => b.classList.toggle("is-on", b.getAttribute("data-mode") === mode));
      document.querySelectorAll("[data-mode-panel]").forEach((p) => {
        p.style.display = (p.getAttribute("data-mode-panel") === mode) ? "block" : "none";
      });
      const beat = mode === "A" ? B.modeA : mode === "B" ? B.modeB : B.modeCombined;
      if (D.mode) applyBeat(D.mode.svg, withSuf(beat, "m"));
    }
    modeButtons.forEach((b) => b.addEventListener("click", () => setMode(b.getAttribute("data-mode"))));

    // Section 4 step rail
    const railBtns   = document.querySelectorAll(".flow-rail button");
    const flowPrev   = document.getElementById("flow-prev");
    const flowNext   = document.getElementById("flow-next");
    const flowReset  = document.getElementById("flow-reset");
    const flowProg   = document.getElementById("flow-progress");
    const stepCards  = document.querySelectorAll("[data-step-card]");
    let currentStep = 1;
    function setStep(n) {
      if (n < 1 || n > 8) return;
      currentStep = n;
      railBtns.forEach((b) => b.classList.toggle("is-on", parseInt(b.getAttribute("data-step")) === n));
      stepCards.forEach((c) => c.hidden = parseInt(c.getAttribute("data-step-card")) !== n);
      if (D.flow) applyBeat(D.flow.svg, withSuf(B["step" + n], "f"));
      if (flowPrev) flowPrev.disabled = n === 1;
      if (flowNext) flowNext.disabled = n === 8;
      if (flowProg) flowProg.innerHTML = `<strong>0${n}</strong> / 08`;
    }
    railBtns.forEach((b) => b.addEventListener("click", () => setStep(parseInt(b.getAttribute("data-step")))));
    if (flowPrev) flowPrev.addEventListener("click", () => setStep(currentStep - 1));
    if (flowNext) flowNext.addEventListener("click", () => setStep(currentStep + 1));
    if (flowReset) flowReset.addEventListener("click", () => setStep(1));
    document.addEventListener("keydown", (e) => {
      const sec4 = document.getElementById("section-flow");
      if (!sec4) return;
      const r = sec4.getBoundingClientRect();
      const inView = r.top < window.innerHeight * 0.5 && r.bottom > window.innerHeight * 0.3;
      if (!inView) return;
      if (e.key === "ArrowRight" || e.key === "ArrowDown") { e.preventDefault(); setStep(currentStep + 1); }
      if (e.key === "ArrowLeft"  || e.key === "ArrowUp")   { e.preventDefault(); setStep(currentStep - 1); }
    });
    setStep(1);

    // Top nav section tracking
    const sections = document.querySelectorAll("[data-section]");
    const navLinks = document.querySelectorAll(".topnav-link");
    const sectionIo = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting && e.intersectionRatio > 0.25) {
          navLinks.forEach((l) => l.classList.toggle("active", l.getAttribute("href") === "#" + e.target.id));
        }
      });
    }, { threshold: [0.25, 0.5] });
    sections.forEach((s) => sectionIo.observe(s));

    // Dark topnav while hero is in view
    const heroEl = document.querySelector(".hero");
    const topnav = document.querySelector(".topnav");
    if (heroEl && topnav) {
      const heroIo = new IntersectionObserver((entries) => {
        entries.forEach((e) => topnav.classList.toggle("dark", e.intersectionRatio > 0.3));
      }, { threshold: [0.3] });
      heroIo.observe(heroEl);
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
