/**
 * Metrix AI — public UI
 * EN default · RU/EN parent layer (no mixed chrome)
 * Modes: marketplace | request | tasks | generate
 * Layers: matryoshka · 4 tariffs · online/offline gen forecast
 */
(function () {
  const D = window.METRIX_DATA;
  if (!D) {
    console.error("METRIX_DATA missing");
    return;
  }

  const MODES = ["marketplace", "request", "tasks", "generate", "promo"];

  const state = {
    mode: "marketplace",
    industry: "all",
    selectedFlagship: null,
    marqueeTimer: null,
    marqueeIndex: 0,
    lastProcess: null,
    lastGenerate: null,
    freeWorkId: null,
    freeWork: null,
    genChoices: {},
    assistSessionId: null,
    pendingQuestions: [],
    liveLogId: null,
    lastIdentityPack: null,
  };

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  function t(key) {
    return D.t ? D.t(key) : key;
  }

  function lang() {
    return D.getLang ? D.getLang() : "en";
  }

  function escapeHtml(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function apiBase() {
    const b = (D.api && D.api.baseUrl) || "";
    if (b) return b.replace(/\/$/, "");
    if (location.hostname === "localhost" || location.hostname === "127.0.0.1") {
      return "http://127.0.0.1:8787";
    }
    return "https://metrix-ai-production.up.railway.app";
  }

  function init() {
    try {
      if (!localStorage.getItem("metrix_lang")) {
        D.setLang("en");
      }
    } catch (e) {
      /* ignore */
    }

    document.addEventListener("metrix:lang", () => {
      applyLangChrome();
      renderAll();
      loadServices();
      startMarquee();
    });

    applyLangChrome();
    renderAll();
    bindModeSwitch();
    bindLang();
    bindScrollJumps();
    bindModal();
    bindForm();
    bindFreeWork();
    bindGenerate();
    bindPromo();
    startMarquee();
    loadServices();

    const params = new URLSearchParams(location.search);
    if (params.get("lang") === "ru" || params.get("lang") === "en") {
      D.setLang(params.get("lang"));
    }
    const hashMode = (location.hash || "").replace(/^#/, "").toLowerCase();
    if (params.get("mode")) setMode(params.get("mode"));
    else if (hashMode === "generate" || hashMode === "mode-generate") setMode("generate");
    else if (hashMode === "tasks" || hashMode === "mode-tasks") setMode("tasks");
    else if (hashMode === "request" || hashMode === "consult") setMode("request");
    if (params.get("industry")) {
      state.industry = params.get("industry");
      const el = $("#req-industry");
      if (el) el.value = state.industry;
    }

    // public debug helper
    window.metrixSetMode = setMode;
  }

  function applyLangChrome() {
    const L = lang();
    document.documentElement.lang = L;
    $$(".lang-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.lang === L);
    });
    $$("[data-i18n]").forEach((el) => {
      // Keep dynamic free-work title if already painted from API
      if (el.id === "fw-title" && state.freeWork && (state.freeWork.title || state.freeWork.summary)) {
        return;
      }
      const key = el.getAttribute("data-i18n");
      if (key) el.textContent = t(key);
    });
    $$("[data-i18n-ph]").forEach((el) => {
      const key = el.getAttribute("data-i18n-ph");
      if (key) el.placeholder = t(key);
    });
    const sub = $("#master-offer-sub");
    if (sub) {
      sub.textContent = "";
      sub.hidden = true;
    }
    const sub2 = $("#master-offer-sub2");
    if (sub2) {
      sub2.textContent = t("hero_sub");
      sub2.hidden = !t("hero_sub");
      sub2.classList.add("hero-sub-shimmer");
    }
    const disc = $("#pricing-discount");
    if (disc) {
      disc.textContent = t("pricing_discount");
      disc.hidden = !t("pricing_discount");
    }
    const lead = $("#how-it-works-lead");
    if (lead) lead.textContent = t("how_lead");
  }

  function renderAll() {
    fillRequestSelects();
    fillChannelSelect();
    renderNicheGrid();
    renderFlagshipDetails();
    renderFlagships();
    renderHowItWorks();
    renderAudienceSplit();
    renderMatryoshka();
    renderPricing();
    paintMarquee(state.marqueeIndex || 0);
  }

  function fillChannelSelect() {
    const el = $("#gen-channel");
    if (!el) return;
    const cur = el.value || "auto";
    const opts = [
      ["auto", "gen_channel_auto"],
      ["online", "gen_channel_online"],
      ["offline", "gen_channel_offline"],
      ["hybrid", "gen_channel_hybrid"],
    ];
    el.innerHTML = opts
      .map(
        ([v, key]) =>
          `<option value="${escapeHtml(v)}">${escapeHtml(t(key))}</option>`
      )
      .join("");
    el.value = cur;
  }

  function bindLang() {
    $$(".lang-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        const next = btn.dataset.lang;
        if (!next || next === lang()) return;
        D.setLang(next);
        // metrix:lang handler applies chrome + re-render
      });
    });
  }

  function setMode(mode) {
    if (mode === "consult") mode = "request";
    if (mode === "workers") mode = "marketplace";
    if (mode === "business" || mode === "biz" || mode === "gen") mode = "generate";
    if (mode === "business-tasks" || mode === "business_tasks") mode = "tasks";
    if (!MODES.includes(mode)) mode = "marketplace";
    state.mode = mode;

    $$(".mode-switch button[data-mode]").forEach((btn) => {
      const on = btn.getAttribute("data-mode") === mode;
      btn.classList.toggle("active", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });

    $$(".mode-panel").forEach((panel) => {
      const panelId = panel.getAttribute("data-panel") || "";
      const on = panelId === mode;
      panel.classList.toggle("active", on);
      // class-driven visibility; keep hidden attr in sync for a11y
      if (on) {
        panel.removeAttribute("hidden");
        panel.setAttribute("aria-hidden", "false");
        // force paint in case UA [hidden] lag
        panel.style.display = "block";
      } else {
        panel.setAttribute("hidden", "");
        panel.setAttribute("aria-hidden", "true");
        panel.style.display = "none";
      }
    });

    if (mode === "tasks") loadServices();

    try {
      const url = new URL(location.href);
      url.searchParams.set("mode", mode);
      history.replaceState(null, "", url.pathname + url.search + url.hash);
    } catch (_) {}

    const target = document.getElementById("mode-" + mode);
    if (target) {
      // after display:block, scroll next frame
      requestAnimationFrame(() => {
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
  }

  function bindModeSwitch() {
    // Event delegation — works for nav + any later buttons
    document.addEventListener("click", (e) => {
      const modeBtn = e.target.closest(".mode-switch button[data-mode]");
      if (modeBtn) {
        e.preventDefault();
        setMode(modeBtn.getAttribute("data-mode"));
        return;
      }
      const jump = e.target.closest("[data-mode-jump]");
      if (!jump) return;
      e.preventDefault();
      const m = jump.getAttribute("data-mode-jump");
      if (m === "pricing") {
        $("#pricing")?.scrollIntoView({ behavior: "smooth" });
        return;
      }
      if (m === "techwrite" || m === "consult-tech") {
        setMode("request");
        const tr = $("#req-track");
        if (tr) tr.value = "product";
        return;
      }
      setMode(m === "consult" ? "request" : m);
    });
  }

  function bindScrollJumps() {
    $$("[data-scroll]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const sel = btn.dataset.scroll;
        if (sel) $(sel)?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
  }

  function fillRequestSelects() {
    const ind = $("#req-industry");
    const tr = $("#req-track");
    const industries = D.getIndustries();
    const tracks = D.getTracks();
    if (ind) {
      const cur = ind.value;
      ind.innerHTML =
        `<option value="">${escapeHtml(t("select"))}</option>` +
        industries
          .map((i) => `<option value="${escapeHtml(i.id)}">${escapeHtml(i.name)}</option>`)
          .join("");
      if (cur) ind.value = cur;
    }
    if (tr) {
      const cur = tr.value;
      tr.innerHTML =
        `<option value="">${escapeHtml(t("all_tracks"))}</option>` +
        tracks.map((x) => `<option value="${escapeHtml(x.id)}">${escapeHtml(x.label)}</option>`).join("");
      if (cur) tr.value = cur;
    }
  }

  function renderNicheGrid() {
    const root = $("#niche-grid");
    if (!root) return;
    const industries = D.getIndustries();
    root.innerHTML = industries
      .map(
        (ind) => `
      <button type="button" class="niche-card niche-card-compact" data-industry="${escapeHtml(ind.id)}"
        style="--flag-accent:${escapeHtml(ind.accent || "#5eead4")}">
        <span class="niche-icon">${ind.icon || "◇"}</span>
        <span class="niche-title-row"><strong>${escapeHtml(ind.short || ind.name)}</strong></span>
        <span class="niche-blurb">${escapeHtml(ind.blurb || "")}</span>
      </button>`
      )
      .join("");
    root.onclick = (e) => {
      const card = e.target.closest("[data-industry]");
      if (!card) return;
      state.industry = card.dataset.industry;
      const el = $("#req-industry");
      if (el) el.value = state.industry;
      setMode("request");
    };
  }

  function renderFlagshipDetails() {
    const root = $("#flagship-detail-grid");
    if (!root) return;
    const list = D.getFlagshipDetails();
    root.innerHTML = list
      .map(
        (f) => `
      <article class="flagship-detail-card">
        <h3>${escapeHtml(f.title)}</h3>
        <p>${escapeHtml(f.text)}</p>
      </article>`
      )
      .join("");
  }

  function flagshipCtaLabel(cta) {
    if (cta === "generate") return t("tariff_cta_generate") || t("cta_generate");
    if (cta === "promo") return t("tariff_cta_promo") || t("nav_promo");
    if (cta === "later" || cta === "none") return t("after_one_step") || t("tariff_cta_later");
    if (cta === "request" || cta === "techwrite" || cta === "consult") {
      return t("tariff_cta_consult") || t("cta_consult");
    }
    return t("details");
  }

  function applyFlagshipCta(cta) {
    if (cta === "generate") {
      setMode("generate");
      return;
    }
    if (cta === "promo") {
      setMode("promo");
      return;
    }
    if (cta === "pricing") {
      $("#pricing")?.scrollIntoView({ behavior: "smooth" });
      return;
    }
    if (cta === "later" || cta === "none") return;
    setMode("request");
  }

  function renderFlagships() {
    const grid = $("#program-grid");
    if (!grid) return;
    const list = D.getFlagships();
    grid.innerHTML = list
      .map((f) => {
        const accent = f.accent || "#5eead4";
        const sticker = f.sticker
          ? `<span class="card-sticker">${escapeHtml(f.sticker)}</span>`
          : "";
        const marquee = f.marquee
          ? `<div class="marquee-body" data-marquee-host>
              <div class="marquee-label" data-marquee-label></div>
              <p class="marquee-text" data-marquee-text></p>
              <div class="marquee-dots" data-marquee-dots></div>
            </div>`
          : `<p>${escapeHtml(f.essence)}</p>`;
        const later = f.cta === "later" || f.cta === "none";
        const footLink = later
          ? `<span class="card-later-note">${escapeHtml(t("after_one_step") || t("tariff_cta_later"))}</span>`
          : `<span class="linkish">${escapeHtml(t("details"))}</span>`;
        return `
      <button type="button" class="card card-flag${f.marquee ? " card-flag-marquee" : ""}${later ? " card-flag-later" : ""}" data-flag="${f.id}"
        style="--flag-accent:${accent}">
        ${sticker}
        <h3>${escapeHtml(f.title)}</h3>
        ${marquee}
        <div class="card-foot">
          <span class="tag accent">${escapeHtml(f.track)}</span>
          ${footLink}
        </div>
      </button>`;
      })
      .join("");

    grid.onclick = (e) => {
      const card = e.target.closest("[data-flag]");
      if (!card) return;
      openFlagship(card.dataset.flag);
    };
    paintMarquee(state.marqueeIndex || 0);
  }

  function startMarquee() {
    if (state.marqueeTimer) clearInterval(state.marqueeTimer);
    const slides = D.getWhyUs();
    if (!slides.length) return;
    state.marqueeIndex = 0;
    paintMarquee(0);
    state.marqueeTimer = setInterval(() => {
      state.marqueeIndex = (state.marqueeIndex + 1) % slides.length;
      paintMarquee(state.marqueeIndex);
    }, 9000);
  }

  function paintMarquee(idx) {
    const slides = D.getWhyUs();
    if (!slides.length) return;
    const s = slides[idx % slides.length];
    $$("[data-marquee-host]").forEach((host) => {
      const label = host.querySelector("[data-marquee-label]");
      const text = host.querySelector("[data-marquee-text]");
      const dots = host.querySelector("[data-marquee-dots]");
      if (label) label.textContent = s.title;
      if (text) {
        text.style.opacity = "0";
        window.setTimeout(() => {
          text.textContent = s.text;
          text.style.opacity = "1";
        }, 180);
      }
      if (dots) {
        dots.innerHTML = slides
          .map(
            (_, i) =>
              `<span class="marquee-dot${i === idx % slides.length ? " active" : ""}"></span>`
          )
          .join("");
      }
    });
  }

  function openFlagship(id) {
    const f = D.getFlagships().find((x) => x.id === id);
    if (!f) return;
    state.selectedFlagship = id;
    $("#modal-title").textContent = f.title;
    const stick = f.sticker
      ? `<span class="tag accent">${escapeHtml(f.sticker)}</span>`
      : "";
    $("#modal-tags").innerHTML = `${stick}<span class="tag">${escapeHtml(f.track)}</span>`;

    let body = "";
    if (f.marquee) {
      body = D.getWhyUs()
        .map(
          (s) => `
        <div class="detail-block">
          <h4>${escapeHtml(s.title)}</h4>
          <p style="color:var(--text-muted);font-size:0.95rem;line-height:1.65">${escapeHtml(s.text)}</p>
        </div>`
        )
        .join("");
    } else {
      const detail = escapeHtml(f.detail || f.essence || "").replace(/\n/g, "<br/>");
      body = `
        <p style="color:var(--text);font-size:1.05rem;margin-bottom:0.75rem">${escapeHtml(f.essence)}</p>
        <p style="color:var(--text-muted);font-size:0.95rem;line-height:1.7">${detail}</p>`;
    }
    $("#modal-body").innerHTML = body;

    const primary = $("#modal-request");
    if (primary) {
      const later = f.cta === "later" || f.cta === "none";
      if (later) {
        primary.hidden = true;
        primary.disabled = true;
        primary.classList.add("btn-disabled-later");
      } else {
        primary.hidden = false;
        primary.disabled = false;
        primary.classList.remove("btn-disabled-later");
        primary.textContent = flagshipCtaLabel(f.cta);
      }
    }

    $("#modal").classList.add("open");
    document.body.style.overflow = "hidden";
  }

  function bindModal() {
    const close = () => {
      $("#modal")?.classList.remove("open");
      document.body.style.overflow = "";
    };
    $("#modal-close")?.addEventListener("click", close);
    $("#modal-close-2")?.addEventListener("click", close);
    $("#modal")?.addEventListener("click", (e) => {
      if (e.target.id === "modal") close();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") close();
    });
    $("#modal-request")?.addEventListener("click", () => {
      const f = D.getFlagships().find((x) => x.id === state.selectedFlagship);
      if (f?.cta === "later" || f?.cta === "none") return;
      close();
      if (f?.cta === "generate" || f?.cta === "promo" || f?.cta === "pricing") {
        applyFlagshipCta(f.cta);
        return;
      }
      // Consult + Tech-TZ is one path (product track when techwrite)
      setMode("request");
      if (f) {
        const tr = $("#req-track");
        if (tr) {
          if (f.cta === "techwrite" || f.track === "product") tr.value = "product";
          else if (f.track === "promotion") tr.value = "promotion";
          else if (f.track && f.track !== "models") tr.value = f.track;
          else if (f.track === "models") tr.value = "models";
        }
        if (f.industryHint) {
          state.industry = f.industryHint;
          const ind = $("#req-industry");
          if (ind) ind.value = f.industryHint;
        }
      }
    });
  }

  function renderMatryoshka() {
    const host = $("#matryoshka-rings");
    const title = $("#matryoshka-title");
    const text = $("#matryoshka-text");
    const indexEl = $("#matryoshka-index");
    const accent = $("#matryoshka-accent");
    if (!host || !D.getSystemLayers) return;

    const layers = D.getSystemLayers();
    // Soft refined palette — never solid “kindergarten” fills
    const palette = [
      { stroke: "rgba(167,139,250,0.55)", fill: "rgba(167,139,250,0.04)", active: "rgba(167,139,250,0.72)" },
      { stroke: "rgba(125,211,252,0.5)", fill: "rgba(56,189,248,0.035)", active: "rgba(125,211,252,0.7)" },
      { stroke: "rgba(56,189,248,0.52)", fill: "rgba(56,189,248,0.04)", active: "rgba(56,189,248,0.72)" },
      { stroke: "rgba(94,234,212,0.5)", fill: "rgba(94,234,212,0.04)", active: "rgba(94,234,212,0.7)" },
      { stroke: "rgba(45,212,191,0.65)", fill: "rgba(45,212,191,0.06)", active: "rgba(94,234,212,0.78)" },
    ];
    // viewBox wide enough for labels outside the rings
    const vb = 520;
    const cx = 248;
    const cy = 250;
    // Thin rings, outer → core
    const radii = [168, 136, 104, 74, 48];
    // Anchor dots at different angles (degrees) so labels don’t stack
    const angles = [-28, 42, 118, 198, 268];

    const polar = (r, deg) => {
      const a = ((deg - 90) * Math.PI) / 180;
      return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) };
    };

    // Brand mesh / lattice pattern (subtle metrix geometry)
    const meshLines = [];
    for (let i = -4; i <= 4; i++) {
      const o = i * 22;
      meshLines.push(
        `<line x1="${cx - 150}" y1="${cy + o}" x2="${cx + 150}" y2="${cy + o}" />`,
        `<line x1="${cx + o}" y1="${cy - 150}" x2="${cx + o}" y2="${cy + 150}" />`
      );
    }
    // Diagonal lattice
    for (let i = -5; i <= 5; i++) {
      const o = i * 28;
      meshLines.push(
        `<line x1="${cx - 140 + o}" y1="${cy - 140}" x2="${cx + 140 + o}" y2="${cy + 140}" />`
      );
    }

    // Concentric hairline guides
    const hairlines = [188, 156, 124, 92, 62]
      .map(
        (r) =>
          `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="rgba(94,234,212,0.06)" stroke-width="0.6"/>`
      )
      .join("");

    // Ring bands: thin stroke + very light fill between outer and next
    const ringEls = layers
      .map((layer, i) => {
        const p = palette[i] || palette[0];
        const r = radii[i];
        const rInner = i < radii.length - 1 ? radii[i + 1] : Math.max(20, r - 22);
        const ang = angles[i] != null ? angles[i] : i * 55 - 30;
        const pt = polar(r, ang);
        // label offset outward a bit
        const lab = polar(r + 28, ang);
        const isCore = layer.id === "core" || i === layers.length - 1;
        const label = layer.short || layer.label;
        // text-anchor by side of circle
        const anchor = pt.x >= cx ? "start" : "end";
        const lx = pt.x >= cx ? lab.x + 2 : lab.x - 2;

        if (isCore) {
          return `
            <g class="mx-ring-group mx-core-group" data-layer="${escapeHtml(layer.id)}" data-i="${i}"
               style="--mx-stroke:${p.stroke};--mx-fill:${p.fill};--mx-active:${p.active}">
              <circle class="mx-ring-fill" cx="${cx}" cy="${cy}" r="${r}" fill="${p.fill}" />
              <circle class="mx-ring-line" cx="${cx}" cy="${cy}" r="${r}"
                fill="none" stroke="${p.stroke}" stroke-width="1.15" />
              <text class="mx-core-word" x="${cx}" y="${cy + 5}" text-anchor="middle">Metrix</text>
              <circle class="mx-ring-hit mx-ring-hit-core" cx="${cx}" cy="${cy}" r="${r + 4}"
                fill="transparent" data-layer="${escapeHtml(layer.id)}" tabindex="0" role="button"
                aria-label="${escapeHtml(layer.label)}" />
            </g>`;
        }

        // Donut-ish soft fill via larger circle with inner cut isn't easy without mask —
        // use low-opacity disc + thin rim; hits via thick invisible stroke
        return `
          <g class="mx-ring-group" data-layer="${escapeHtml(layer.id)}" data-i="${i}"
             style="--mx-stroke:${p.stroke};--mx-fill:${p.fill};--mx-active:${p.active}">
            <circle class="mx-ring-fill" cx="${cx}" cy="${cy}" r="${(r + rInner) / 2}"
              fill="none" stroke="${p.fill}" stroke-width="${Math.max(8, r - rInner - 2)}" />
            <circle class="mx-ring-line" cx="${cx}" cy="${cy}" r="${r}"
              fill="none" stroke="${p.stroke}" stroke-width="1.1" />
            <circle class="mx-ring-line-inner" cx="${cx}" cy="${cy}" r="${rInner + 1}"
              fill="none" stroke="${p.stroke}" stroke-width="0.55" opacity="0.35" />
            <g class="mx-node" transform="translate(${pt.x.toFixed(1)},${pt.y.toFixed(1)})">
              <circle class="mx-node-dot" r="3.2" />
              <circle class="mx-node-ring" r="6.5" fill="none" />
            </g>
            <text class="mx-node-label" x="${lx.toFixed(1)}" y="${lab.y.toFixed(1)}"
              text-anchor="${anchor}" dominant-baseline="middle">${escapeHtml(label)}</text>
            <circle class="mx-ring-hit" cx="${cx}" cy="${cy}" r="${r}"
              fill="none" stroke="transparent" stroke-width="16"
              data-layer="${escapeHtml(layer.id)}" tabindex="0" role="button"
              aria-label="${escapeHtml(layer.label)}" />
          </g>`;
      })
      .join("");

    host.innerHTML = `
      <svg class="matryoshka-svg" viewBox="0 0 ${vb} ${vb}" role="img" aria-label="Metrix layers">
        <defs>
          <clipPath id="mxMeshClip">
            <circle cx="${cx}" cy="${cy}" r="186"/>
          </clipPath>
          <radialGradient id="mxBrandFade" cx="42%" cy="38%" r="68%">
            <stop offset="0%" stop-color="rgba(94,234,212,0.09)"/>
            <stop offset="55%" stop-color="rgba(14,22,32,0.2)"/>
            <stop offset="100%" stop-color="rgba(7,10,15,0.55)"/>
          </radialGradient>
          <pattern id="mxMicroGrid" width="14" height="14" patternUnits="userSpaceOnUse">
            <path d="M14 0H0V14" fill="none" stroke="rgba(94,234,212,0.07)" stroke-width="0.5"/>
          </pattern>
          <linearGradient id="mxArcSoft" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="rgba(56,189,248,0.2)"/>
            <stop offset="50%" stop-color="rgba(94,234,212,0.12)"/>
            <stop offset="100%" stop-color="rgba(167,139,250,0.16)"/>
          </linearGradient>
        </defs>

        <!-- Soft stage plate, left-weighted composition -->
        <circle cx="${cx}" cy="${cy}" r="198" fill="url(#mxBrandFade)" />
        <circle cx="${cx}" cy="${cy}" r="198" fill="url(#mxMicroGrid)" opacity="0.85" />

        <!-- Brand geometry / pattern field -->
        <g class="mx-mesh" clip-path="url(#mxMeshClip)" opacity="0.55">
          ${meshLines.join("")}
        </g>
        ${hairlines}

        <!-- Decorative brand arcs (not interactive) -->
        <path class="mx-deco-arc" d="M ${cx - 150} ${cy} A 150 150 0 0 1 ${cx + 106} ${cy - 106}"
          fill="none" stroke="url(#mxArcSoft)" stroke-width="0.9" stroke-linecap="round"/>
        <path class="mx-deco-arc" d="M ${cx + 130} ${cy + 40} A 140 140 0 0 1 ${cx - 40} ${cy + 134}"
          fill="none" stroke="rgba(94,234,212,0.14)" stroke-width="0.7" stroke-linecap="round"/>
        <path class="mx-deco-arc" d="M ${cx - 90} ${cy - 140} A 160 160 0 0 1 ${cx + 140} ${cy - 50}"
          fill="none" stroke="rgba(167,139,250,0.12)" stroke-width="0.7" stroke-linecap="round"/>

        ${ringEls}
      </svg>`;

    const show = (layer, i) => {
      if (!layer) return;
      const idx = i != null ? i : layers.findIndex((l) => l.id === layer.id);
      host.querySelectorAll(".mx-ring-group").forEach((g) => {
        g.classList.toggle("is-active", g.dataset.layer === layer.id);
      });
      host.querySelectorAll(".mx-ring-hit").forEach((el) => {
        el.setAttribute("aria-pressed", el.dataset.layer === layer.id ? "true" : "false");
      });
      if (title) title.textContent = layer.label;
      if (text) text.textContent = layer.text;
      if (indexEl) {
        indexEl.textContent = String(layers.length - (idx >= 0 ? idx : 0)).padStart(2, "0");
      }
      const p = palette[idx >= 0 ? idx : 0] || palette[0];
      const panel = $("#matryoshka-panel");
      if (panel) {
        panel.style.setProperty("--layer-accent", p.active || p.stroke);
        panel.classList.add("is-lit");
      }
      if (accent) {
        accent.style.setProperty("--layer-accent", p.active || p.stroke);
      }
    };

    const bindLayer = (el, layer, i) => {
      if (!el || !layer) return;
      el.addEventListener("mouseenter", () => show(layer, i));
      el.addEventListener("focus", () => show(layer, i));
      el.addEventListener("click", (e) => {
        e.preventDefault();
        show(layer, i);
      });
      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          show(layer, i);
        }
      });
    };

    layers.forEach((layer, i) => {
      const hit = host.querySelector(`.mx-ring-hit[data-layer="${layer.id}"]`);
      bindLayer(hit, layer, i);
      // also allow clicking the label / node via group hit on label text
      const group = host.querySelector(`.mx-ring-group[data-layer="${layer.id}"]`);
      if (group) {
        const labelEl = group.querySelector(".mx-node-label");
        const nodeEl = group.querySelector(".mx-node");
        bindLayer(labelEl, layer, i);
        bindLayer(nodeEl, layer, i);
      }
    });

    const coreIdx = layers.length - 1;
    show(layers[coreIdx] || layers[0], coreIdx);
  }

  function tariffCtaMeta(tier) {
    const cta = tier.cta || "request";
    if (cta === "generate") {
      return {
        mode: "generate",
        label: t("tariff_cta_generate") || t("cta_generate"),
        active: true,
      };
    }
    if (cta === "promo") {
      return {
        mode: "promo",
        label: t("tariff_cta_promo") || t("nav_promo"),
        active: true,
      };
    }
    if (cta === "later" || cta === "none") {
      return {
        mode: "",
        label: t("tariff_cta_later") || t("after_one_step"),
        active: false,
      };
    }
    if (cta === "partner") {
      return {
        mode: "",
        label: tier.price || t("tariff_cta_later"),
        active: false,
      };
    }
    return {
      mode: "request",
      label: t("tariff_cta_consult") || t("cta_consult") || t("tariff_cta"),
      active: true,
    };
  }

  function renderPricing() {
    const grid = $("#pricing-grid");
    if (!grid || !D.getPricingTiers) return;
    const tiers = D.getPricingTiers();
    grid.innerHTML = tiers
      .map((tier) => {
        const items = (tier.includes || [])
          .map((x) => `<li>${escapeHtml(x)}</li>`)
          .join("");
        const badge = tier.popular
          ? `<span class="tariff-badge">${escapeHtml(t("tariff_popular"))}</span>`
          : "";
        const meta = tariffCtaMeta(tier);
        const priceClass =
          tier.priceStyle === "soft" ? "tariff-price tariff-price-soft" : "tariff-price";
        const ctaHtml = meta.active
          ? `<button type="button" class="btn ${
              tier.popular ? "btn-primary" : "btn-ghost"
            } tariff-cta" data-mode-jump="${escapeHtml(meta.mode)}">${escapeHtml(meta.label)}</button>`
          : `<span class="tariff-cta tariff-cta-later" aria-disabled="true">${escapeHtml(
              meta.label
            )}</span>`;
        return `
      <article class="tariff-card${tier.popular ? " tariff-popular" : ""}" data-tariff="${escapeHtml(
          tier.id
        )}">
        ${badge}
        <div class="tariff-head">
          <div class="eyebrow">${escapeHtml(tier.id)}</div>
          <h3>${escapeHtml(tier.name)}</h3>
          <div class="${priceClass}">${escapeHtml(tier.price)}</div>
          <p class="tariff-period">${escapeHtml(tier.period || "")}</p>
          <p class="tariff-tagline">${escapeHtml(tier.tagline || "")}</p>
        </div>
        <ul class="tariff-list">${items}</ul>
        ${ctaHtml}
      </article>`;
      })
      .join("");
  }

  function renderHowItWorks() {
    const root = $("#how-it-works-body");
    if (!root) return;
    const steps = D.getHowSteps();
    root.innerHTML = steps
      .map(
        (s) => `
      <div class="how-card" style="--flag-accent:var(--accent)">
        <div class="step-num">${escapeHtml(s.n)}</div>
        <h3>${escapeHtml(s.title)}</h3>
        <p>${escapeHtml(s.text)}</p>
      </div>`
      )
      .join("");
  }

  function renderAudienceSplit() {
    const root = $("#audience-split");
    if (!root) return;
    root.innerHTML = `
      <div class="audience-split-inner">
        <div class="section-head" style="margin-bottom:1rem;margin-top:2rem">
          <div>
            <div class="eyebrow">${escapeHtml(t("for_whom"))}</div>
            <h2>${escapeHtml(t("audience_title"))}</h2>
            <p class="how-lead">${escapeHtml(t("audience_lead"))}</p>
          </div>
        </div>
        <div class="audience-grid">
          <article class="audience-card">
            <div class="eyebrow">${escapeHtml(t("workers_title"))}</div>
            <p>${escapeHtml(t("workers_text"))}</p>
          </article>
          <article class="audience-card">
            <div class="eyebrow">${escapeHtml(t("clients_title"))}</div>
            <p>${escapeHtml(t("clients_text"))}</p>
          </article>
        </div>
      </div>`;
  }

  function bindForm() {
    const form = $("#request-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const business = ($("#req-business")?.value || "").trim();
      const industry = $("#req-industry")?.value || "";
      // Consult + Tech-TZ: default product track so tech-write path is included
      let track = $("#req-track")?.value || "product";
      if (!track) track = "product";
      const err = $("#form-error");
      const ok = $("#form-success");
      if (err) err.textContent = "";
      if (ok) ok.textContent = "";
      if (!industry || business.length < 20) {
        if (err) err.textContent = t("form_err");
        return;
      }
      try {
        const res = await fetch(`${apiBase()}${D.api.processPath || "/api/v1/process"}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            industry,
            business,
            track,
            lang: lang(),
            name: "",
            contact: [$("#req-x")?.value, $("#req-telegram")?.value].filter(Boolean).join(" · "),
          }),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        state.lastProcess = data;
        paintConsult(data);
        if (ok) ok.textContent = t("form_ok");
      } catch (ex) {
        if (err) err.textContent = ex.message;
      }
    });

    $("#btn-new-consult")?.addEventListener("click", () => {
      if ($("#consult-result")) $("#consult-result").hidden = true;
      if ($("#free-work-panel")) $("#free-work-panel").hidden = true;
    });
  }

  /** Open consult+tech form, optionally prefilled from a Business Task card */
  function openConsultFromTask(svc) {
    setMode("request");
    const tr = $("#req-track");
    if (tr) tr.value = "product";
    const L = lang();
    const ta = $("#req-business");
    if (ta && !ta.value.trim() && svc) {
      const name = svc.name || svc.id || "";
      const benefit = svc.benefit || svc.tagline || "";
      const ex =
        Array.isArray(svc.examples) && svc.examples[0]
          ? svc.examples[0].text || svc.examples[0]
          : "";
      ta.value =
        L === "ru"
          ? `Нужна услуга «${name}». Польза: ${benefit}. ${ex ? "Пример из ниши: " + ex + ". " : ""}Опишите контур, дайте консультацию и tech-write.`
          : `I need «${name}». Benefit: ${benefit}. ${ex ? "Niche example: " + ex + ". " : ""}Give consult + tech write for my business.`;
    }
  }

  function paintConsult(data) {
    const box = $("#consult-result");
    if (!box) return;
    box.hidden = false;
    const idea = data.product?.demo_idea || data.demo_idea || {};
    $("#cr-headline").textContent = idea.title || data.orientation?.operating_mode || "Result";
    $("#cr-meta").textContent = `${data.industry || ""} · ${data.request_id || ""}`;
    $("#cr-blurb").textContent = idea.summary || data.summary || data.message || "";
    if ($("#cr-niche-answer")) $("#cr-niche-answer").textContent = "";
    if ($("#cr-links")) $("#cr-links").innerHTML = "";
  }

  function bindFreeWork() {
    $("#btn-start-free-work")?.addEventListener("click", async () => {
      const business = ($("#req-business")?.value || "").trim();
      const industry = $("#req-industry")?.value || "ai-agencies";
      try {
        const res = await fetch(`${apiBase()}${D.api.freeWorkStartPath}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            business:
              business ||
              (lang() === "ru"
                ? "Бесплатная работа после консультации: операционный контур и следующие шаги."
                : "Free work after consult for operational contour and next steps."),
            industry,
            track: $("#req-track")?.value || "all",
            lang: lang(),
          }),
        });
        const data = await res.json();
        state.freeWork = data;
        state.freeWorkId = data.work_id || data.id;
        paintFreeWork(data);
      } catch (ex) {
        alert(ex.message);
      }
    });
    $("#btn-advance-phase")?.addEventListener("click", async () => {
      if (!state.freeWorkId) return;
      const res = await fetch(
        `${apiBase()}${D.api.freeWorkAdvancePath}?work_id=${encodeURIComponent(state.freeWorkId)}`,
        { method: "POST" }
      );
      paintFreeWork(await res.json());
    });
    $("#btn-submit-clarify")?.addEventListener("click", async () => {
      if (!state.freeWorkId) return;
      const res = await fetch(`${apiBase()}${D.api.freeWorkClarifyPath}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ work_id: state.freeWorkId, answers: {}, lang: lang() }),
      });
      paintFreeWork(await res.json());
    });
  }

  function paintFreeWork(data) {
    const panel = $("#free-work-panel");
    if (!panel) return;
    panel.hidden = false;
    $("#fw-title").textContent = data.title || t("fw_title_default");
    $("#fw-quality").textContent = data.quality_note || data.summary || "";
    const phases = data.phases || data.phase_list || [];
    $("#fw-phases").innerHTML = Array.isArray(phases)
      ? phases
          .map(
            (p) =>
              `<span class="tag">${escapeHtml(typeof p === "string" ? p : p.name || p.id)}</span>`
          )
          .join(" ")
      : "";
    const cl = data.checklist || [];
    $("#fw-checklist").innerHTML = (Array.isArray(cl) ? cl : [])
      .map(
        (c) =>
          `<li>${escapeHtml(typeof c === "string" ? c : c.text || JSON.stringify(c))}</li>`
      )
      .join("");
    $("#fw-success-metric").textContent = data.success_metric || "";
    $("#fw-tech-md").textContent =
      data.tech_write || data.tech_md || JSON.stringify(data, null, 2).slice(0, 2000);
  }

  // ── Promotion mode (third tariff) ─────────────────────────────────────────
  function bindPromo() {
    const form = $("#promo-form");
    if (!form || form.dataset.bound === "1") return;
    form.dataset.bound = "1";
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const headline = ($("#promo-headline")?.value || "").trim();
      const body = ($("#promo-body")?.value || "").trim();
      const err = $("#promo-error");
      if (err) err.textContent = "";
      if (headline.length < 3 || body.length < 20) {
        if (err) err.textContent = t("gen_min_chars") || "Min 20 characters";
        return;
      }
      const btn = $("#promo-submit");
      if (btn) {
        btn.disabled = true;
        btn.textContent = "…";
      }
      try {
        const res = await fetch(`${apiBase()}/api/v1/analytics/promotion-pack`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            business: [headline, body].join(". "),
            project_name: headline,
            lang: lang(),
          }),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        paintPromo(data);
      } catch (ex) {
        if (err) err.textContent = String(ex.message || ex);
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.textContent = lang() === "en" ? "Build promo plan" : "Собрать план продвижения";
        }
      }
    });
  }

  function paintPromo(data) {
    const root = $("#promo-result");
    if (!root) return;
    root.hidden = false;
    const p = data.output || data;
    $("#promo-msg").textContent = data.message || p.summary || "—";
    const roads = p.roads || [];
    $("#promo-roads").innerHTML = roads
      .map(
        (r) => `<div class="gen-block-card promo-road">
          <h4>${escapeHtml(r.title || "")}</h4>
          <p class="how-lead">${escapeHtml(r.promise || "")}</p>
          <ol class="clean-list">${(r.steps || []).map((s) => `<li>${escapeHtml(s)}</li>`).join("")}</ol>
          <p class="how-lead"><strong>KPI:</strong> ${escapeHtml(r.kpi || "")}</p>
          <p class="how-lead"><strong>Kill:</strong> ${escapeHtml(r.kill || "")}</p>
        </div>`
      )
      .join("");
    $("#promo-dms").innerHTML = (p.dm_scripts || [])
      .map(
        (d) =>
          `<div class="hook-item"><div class="k">${escapeHtml(d.name || d.id)}</div><div>${escapeHtml(
            d.script || ""
          )}</div></div>`
      )
      .join("");
    const tips = (p.general_tips || []).map((t) => `<li>${escapeHtml(t)}</li>`).join("");
    const ideas = (p.sales_ideas || []).map((t) => `<li>${escapeHtml(t)}</li>`).join("");
    const ans = (p.analytics_answers || [])
      .map((a) => `<li><strong>${escapeHtml(a.signal)}</strong> — ${escapeHtml(a.answer)}</li>`)
      .join("");
    $("#promo-extra").innerHTML = `
      <div class="eyebrow">Советы</div><ul class="clean-list">${tips}</ul>
      <div class="eyebrow">Идеи продаж</div><ul class="clean-list">${ideas}</ul>
      <div class="eyebrow">Аналитика</div><ul class="clean-list">${ans || "<li>—</li>"}</ul>`;
    root.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // ── Generate business ─────────────────────────────────────────────────────
  function bindGenerate() {
    const form = $("#gen-form");
    if (!form) {
      console.warn("[metrix] #gen-form missing — generate mode markup not found");
      return;
    }
    if (form.dataset.bound === "1") return;
    form.dataset.bound = "1";
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const headline = ($("#gen-headline")?.value || "").trim();
      const body = ($("#gen-business")?.value || "").trim();
      // No niche picker — orchestrator ranks all 10 niches from free text
      const business = [headline, body].filter(Boolean).join(". ").trim();
      const err = $("#gen-error");
      if (err) err.textContent = "";
      if (headline.length < 3 || body.length < 20) {
        if (err) err.textContent = t("gen_min_chars");
        return;
      }
      const btn = $("#gen-submit");
      if (btn) {
        btn.disabled = true;
        btn.textContent = t("gen_loading");
      }
      try {
        const res = await fetch(
          `${apiBase()}${D.api.businessGeneratePath || "/api/v1/analytics/business-generate"}`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              business,
              industry: "generic",
              project_name: headline,
              lang: lang(),
              channel: ($("#gen-channel")?.value || "auto"),
              multi_pass: true,
              passes: 7,
              choices: state.genChoices,
              numbers: {
                cash_ceiling: Number($("#gen-cash")?.value || 1500),
                days: Number($("#gen-days")?.value || 21),
              },
            }),
          }
        );
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        state.lastGenerate = data;
        try {
          localStorage.setItem("metrix_last_generate", JSON.stringify(data));
        } catch (_) {}
        paintGenerate(data);
        paintChoices((data.output && data.output.plan) || {});
      } catch (ex) {
        if (err) err.textContent = `${t("gen_error")}: ${ex.message}`;
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.textContent = t("gen_run");
        }
      }
    });
  }

  function paintChoices(plan) {
    const wrap = $("#gen-choices");
    const host = $("#gen-choice-cards");
    if (!wrap || !host) return;
    const steps = (plan.steps || []).filter((s) => s.needs_human);
    if (!steps.length) {
      wrap.hidden = true;
      return;
    }
    wrap.hidden = false;
    host.innerHTML = steps
      .map((s) => {
        const opts = (s.options || [])
          .map((o) => {
            const checked =
              (state.genChoices[s.id] || s.default_option) === o.id ? "checked" : "";
            return `<label><input type="radio" name="${escapeHtml(s.id)}" value="${escapeHtml(o.id)}" ${checked}/> ${escapeHtml(o.label)}</label>`;
          })
          .join("");
        return `<div class="choice-block"><h4>${escapeHtml(s.title)}</h4><div class="choice-opts">${opts}</div></div>`;
      })
      .join("");
    host.onchange = (e) => {
      const input = e.target;
      if (input && input.name) state.genChoices[input.name] = input.value;
    };
  }

  function paintGenerate(data) {
    const root = $("#gen-result");
    if (!root) return;
    root.hidden = false;
    const out = data.output || {};
    const report = out.core_report || {};
    const isEn = lang() === "en";
    const msgEl = $("#gen-msg");
    if (msgEl) {
      msgEl.textContent =
        data.message ||
        (isEn
          ? "Consultation ready: filling, analytical report, main PDF."
          : "Консультация готова: наполнение, аналитический отчёт, основной PDF.");
    }
    // Hide valuation / route noise
    ["gen-gate", "gen-value-band", "gen-route-chip"].forEach((id) => {
      const el = $("#" + id);
      if (el) {
        el.hidden = true;
        el.textContent = "";
      }
    });

    const rd = out.rd_reader || {};
    const html =
      data.consultation_html ||
      data.rd_html ||
      (out.analytical_report && out.analytical_report.html) ||
      (out.exports && out.exports.consultation_html) ||
      (out.exports && out.exports.rd_html) ||
      (out.exports && out.exports.print_html) ||
      rd.html ||
      "";
    const md =
      data.rd_markdown ||
      data.core_markdown ||
      (out.analytical_report && out.analytical_report.markdown) ||
      report.markdown ||
      rd.markdown ||
      "";

    // 00 Live log
    paintLiveLog(out.live_log || {}, isEn);
    state.liveLogId = (out.live_log && out.live_log.id) || null;
    state.lastIdentityPack = out.identity_pack || data.identity_pack || null;

    // 01 Наполнение
    paintFill(out, report, isEn);

    // 02 Аналитический отчёт (no empty iframe)
    const reportBody = $("#gen-report-body");
    if (reportBody) {
      if (html) {
        reportBody.innerHTML = `<div class="report-frame-wrap"><iframe class="rd-frame" title="report" sandbox="allow-same-origin"></iframe></div>`;
        const fr = reportBody.querySelector("iframe");
        if (fr) fr.srcdoc = html;
      } else if (md) {
        reportBody.innerHTML = `<pre class="report-pre">${escapeHtml(md)}</pre>`;
      } else {
        reportBody.innerHTML = `<p class="how-lead">${isEn ? "Report loading…" : "Отчёт загружается…"}</p>`;
      }
    }

    // 03 Hook cards (designed)
    paintHook(out.hook_plan || data.hook_plan || {}, isEn);

    // Downloads
    bindExportButtons(data, report, { html, markdown: md });

    // Post-pay locked by default
    const postPay = $("#gen-post-pay");
    if (postPay) postPay.hidden = true;
    wirePostPay(out, data, isEn);

    // Identity questions only (unique per request) — shown after pay
    const iq = (out.identity_pack && out.identity_pack.identity_questions) || out.plan?.identity_questions || [];
    state.pendingQuestions = iq.length
      ? iq
      : (out.plan?.open_questions || []).map((t) => ({ text: t, id: "" }));

    paintForecast(out);

    // Orchestration: 10 niches + service stack
    const orch = out.orchestration || {};
    const noteEl = $("#gen-orch-note");
    if (noteEl) noteEl.textContent = orch.note || "";
    const rankHost = $("#gen-niche-rank");
    if (rankHost) {
      const ranks = (orch.niche_ranking || []).slice(0, 10);
      rankHost.innerHTML = ranks
        .map(
          (r, i) =>
            `<span class="niche-rank-chip${i === 0 ? " top" : ""}" title="${escapeHtml(String(r.score))}">${escapeHtml(
              r.label || r.id
            )} <em>${escapeHtml(String(Math.round((r.score || 0) * 100)))}%</em></span>`
        )
        .join("");
    }
    const stackHost = $("#gen-service-stack");
    if (stackHost) {
      const stack = orch.service_stack || [];
      stackHost.innerHTML = stack
        .map(
          (s) =>
            `<span class="svc-stack-chip${s.role === "primary_run" ? " primary" : ""}">${escapeHtml(
              s.order + ". " + (s.name || s.service_id)
            )}</span>`
        )
        .join("");
    }

    const plan = out.plan || {};
    const planEl = $("#gen-plan");
    if (planEl) {
      planEl.innerHTML = (plan.steps || [])
        .map(
          (s) =>
            `<div class="tz-step"><span class="tz-id">${escapeHtml(s.id || "")}</span><div><strong>${escapeHtml(
              s.title || ""
            )}</strong><div class="how-lead">${escapeHtml(s.default_option || "—")}</div></div></div>`
        )
        .join("");
    }

    const panel = out.control_panel || {};
    const panelEl = $("#gen-panel");
    if (panelEl) {
      panelEl.innerHTML = (panel.columns || [])
        .map((col) => {
          const cards = (col.cards || [])
            .slice(0, 4)
            .map((c) => {
              let v = c.v;
              if (v == null) v = "—";
              else if (Array.isArray(v))
                v = v
                  .map((x) => (typeof x === "object" ? x.title || x.id || "" : x))
                  .filter(Boolean)
                  .join("; ");
              else if (typeof v === "object")
                v = Object.entries(v)
                  .map(([k, val]) => `${k}: ${val}`)
                  .join(", ");
              v = String(v).slice(0, 220);
              return `<div class="human-card"><div class="k">${escapeHtml(c.k)}</div><div>${escapeHtml(v)}</div></div>`;
            })
            .join("");
          return `<div class="panel-col-inner"><div class="col-title">${escapeHtml(col.title)}</div>${cards}</div>`;
        })
        .join("");
    }

    const q = out.quality || {};
    const st = out.self_test || {};
    const qEl = $("#gen-quality");
    if (qEl) {
      const conf = q.confidence != null ? Math.round(Number(q.confidence) * 100) + "%" : "—";
      qEl.textContent = isEn
        ? `Confidence ${conf} · checks ${st.passed ?? "?"}/${st.total ?? "?"} · ${st.verdict || "ok"} · ${out.primary_industry || "—"}`
        : `Уверенность ${conf} · проверки ${st.passed ?? "?"}/${st.total ?? "?"} · ${st.verdict || "ok"} · ${out.primary_industry || "—"}`;
    }
    const eb = out.expert_base || {};
    const eEl = $("#gen-expert");
    if (eEl) {
      const moves = (eb.original_moves || report.original_moves || []).slice(0, 2);
      eEl.innerHTML = `<strong>${escapeHtml(eb.name || report.title || "—")}</strong><div class="how-lead">${escapeHtml(
        (eb.layers || []).join(" · ") || "—"
      )}</div>${moves.length ? `<div class="how-lead">${escapeHtml(moves.join(" · "))}</div>` : ""}`;
    }
    const pack = out.autonomous_code_pack || {};
    const cEl = $("#gen-code");
    if (cEl) {
      const rich = pack.components_rich || [];
      if (rich.length) {
        cEl.innerHTML = rich
          .slice(0, 6)
          .map(
            (c) =>
              `<div class="code-row"><span class="tz-id">${escapeHtml(c.status || "")}</span> ${escapeHtml(
                c.file || ""
              )} — ${escapeHtml(c.role || "")}</div>`
          )
          .join("");
      } else {
        const comps = (pack.components || []).slice(0, 5);
        cEl.innerHTML = comps.map((x) => `<div class="code-row">${escapeHtml(x)}</div>`).join("");
      }
      if (pack.next_build && pack.next_build.length) {
        cEl.innerHTML +=
          `<div class="eyebrow" style="margin-top:0.6rem">${isEn ? "Next build" : "Дальше в сборке"}</div>` +
          pack.next_build.map((x) => `<div class="how-lead">· ${escapeHtml(x)}</div>`).join("");
      }
    }
    root.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function paintLiveLog(log, isEn) {
    const host = $("#gen-live-log");
    const meta = $("#gen-live-log-meta");
    if (!host) return;
    if (!log || !log.days || !log.days.length) {
      host.innerHTML = `<p class="how-lead">${isEn ? "Live log will appear after generate." : "Живой лог появится после generate."}</p>`;
      return;
    }
    if (meta) {
      const art = log.artifact || {};
      meta.textContent = isEn
        ? `Target ${log.touch_target || "—"} touches · ${log.start_date} → ${log.end_date} · artifact: ${art.name || "—"} · id ${log.id || ""}`
        : `Цель ${log.touch_target || "—"} касаний · ${log.start_date} → ${log.end_date} · artifact: ${art.name || "—"} · id ${log.id || ""}`;
    }
    host.innerHTML = (log.days || [])
      .map((d, i) => {
        const done = d.done ? "done" : "";
        return `<div class="live-log-row ${done}" data-offset="${escapeHtml(String(d.day_offset != null ? d.day_offset : i))}">
          <button type="button" class="live-check" title="done">✓</button>
          <div>
            <strong>${escapeHtml(d.day || "")}</strong> · ${escapeHtml(d.label || "")}
            <div class="how-lead">${escapeHtml(d.action || "")}</div>
          </div>
        </div>`;
      })
      .join("");
    host.onclick = async (e) => {
      const row = e.target.closest(".live-log-row");
      if (!row || !state.liveLogId) return;
      const off = Number(row.dataset.offset);
      try {
        const res = await fetch(`${apiBase()}/api/v1/analytics/live-log/tick`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: state.liveLogId, day_offset: off, note: "ui" }),
        });
        if (!res.ok) throw new Error("tick");
        const data = await res.json();
        if (data.session) paintLiveLog(data.session, isEn);
      } catch (_) {
        row.classList.add("done");
      }
    };
    const artBtn = $("#gen-live-artifact");
    if (artBtn && artBtn.dataset.bound !== "1") {
      artBtn.dataset.bound = "1";
      artBtn.addEventListener("click", async () => {
        if (!state.liveLogId) return;
        try {
          const res = await fetch(`${apiBase()}/api/v1/analytics/live-log/tick`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: state.liveLogId, mark_artifact: true }),
          });
          if (res.ok) {
            const data = await res.json();
            if (data.session) paintLiveLog(data.session, lang() === "en");
            artBtn.textContent = lang() === "en" ? "Artifact marked" : "Artifact отмечен";
          }
        } catch (_) {
          artBtn.textContent = "…";
        }
      });
    }
  }

  function paintFill(out, report, isEn) {
    const host = $("#gen-fill-body");
    if (!host) return;
    const arch = report.architecture_cards || out.core_report?.architecture_cards || [];
    const counts = report.counts || {};
    const top = arch.slice(0, 12);
    host.innerHTML = `
      <p class="how-lead">${
        isEn
          ? "Path steps A01–A12 (architecture path — not content dump)"
          : "Шаги пути A01–A12 (архитектурный маршрут — не «наполнение»)"
      }: ${counts.architecture_cards || arch.length}</p>
      <div class="fill-grid">
        ${top
          .map(
            (c, i) =>
              `<div class="fill-card"><div class="tz-id">${escapeHtml(c.id || "A" + String(i + 1).padStart(2, "0"))}</div><strong>${escapeHtml(
                c.title || ""
              )}</strong><div class="how-lead">${escapeHtml(c.niche || "")}</div><div class="how-lead">${escapeHtml(
                (c.blocks || c.context || "").slice(0, 100)
              )}</div></div>`
          )
          .join("")}
      </div>`;
    // GenCore strip
    const gc = out.gencore || {};
    const chip = $("#chip-gencore");
    if (chip && gc.version) {
      chip.textContent = `GenCore ${gc.generation || "v1"} · ${(gc.skills_in_context != null ? gc.skills_in_context : 0)} skills`;
      chip.classList.add("ok");
      chip.classList.remove("later");
    }
  }

  function paintHook(hook, isEn) {
    const title = $("#gen-hook-title");
    const pitch = $("#gen-hook-pitch");
    const grid = $("#gen-hook-cards");
    if (title) title.textContent = hook.headline || (isEn ? "What is ready" : "Что готово");
    if (pitch) pitch.textContent = hook.pitch || "";
    if (grid) {
      const cards = hook.cards || [];
      grid.innerHTML = cards
        .map(
          (c) =>
            `<div class="hook-item"><div class="k">${escapeHtml(c.k)}</div><div>${escapeHtml(c.v)}</div></div>`
        )
        .join("");
    }
  }

  function wirePostPay(out, data, isEn) {
    const btn = $("#gen-approve-core");
    if (!btn) return;
    btn.disabled = false;
    btn.textContent = isEn ? "I paid · open identity & agent" : "Я оплатил · открыть идентичность и агент";
    if (btn.dataset.boundPay === "1") return;
    btn.dataset.boundPay = "1";
    btn.addEventListener("click", async () => {
      const isEn2 = lang() === "en";
      const last = state.lastGenerate || {};
      const out2 = last.output || out || {};
      const post = $("#gen-post-pay");
      if (post) post.hidden = false;

      const pack = out2.identity_pack || state.lastIdentityPack || data.identity_pack || {};
      const fc = pack.forecast || {};
      const fcEl = $("#gen-identity-forecast");
      if (fcEl) {
        const likes = (fc.why_you_will_like_this || [])
          .map((x) => `<li>${escapeHtml(x)}</li>`)
          .join("");
        fcEl.innerHTML = `
          <h4 style="margin:0 0 0.35rem">${escapeHtml(fc.headline || "")}</h4>
          <p class="how-lead">${escapeHtml(fc.delight_note || "")}</p>
          <ul class="clean-list">${likes}</ul>
          <p class="how-lead">${isEn2 ? "Delight score" : "Насколько «ваше»"}: ${fc.delight_score != null ? Math.round(fc.delight_score * 100) + "%" : "—"}</p>
        `;
      }
      paintPersonality(out2.author_personality || data.author_personality, isEn2);

      const qs = pack.identity_questions || state.pendingQuestions || [];
      const qEl = $("#gen-questions");
      if (qEl) {
        qEl.innerHTML = qs.length
          ? qs
              .map((q) => {
                const text = typeof q === "string" ? q : q.text || "";
                const key = typeof q === "object" ? q.unique_key || q.id || "" : "";
                return `<li><span class="tz-id">${escapeHtml(key)}</span> ${escapeHtml(text)}</li>`;
              })
              .join("")
          : `<li>${isEn2 ? "Write your angle in DM" : "Напишите свой угол в DM"}</li>`;
      }
      const regen = $("#gen-regen-slots");
      if (regen) {
        const gens = (fc.next_generations || []).map((g) => `<li>${escapeHtml(g)}</li>`).join("");
        regen.innerHTML = gens
          ? `<div class="eyebrow">${isEn2 ? "Open generation slots" : "Открытые слоты генераций"}</div><ul class="clean-list">${gens}</ul>`
          : "";
      }

      const teaser = out2.assist_agent || {};
      try {
        const res = await fetch(`${apiBase()}/api/v1/analytics/assist-agent/approve`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ assist_agent: teaser, lang: lang() }),
        });
        if (res.ok) {
          const payload = await res.json();
          const session = payload.session || {};
          state.assistSessionId = session.session_id;
          renderAssistSession(session, isEn2);
          const adv = $("#gen-assist-advance");
          if (adv) {
            adv.hidden = false;
            adv.onclick = () => advanceAssistAgent(isEn2);
          }
        } else throw new Error("api");
      } catch (_) {
        renderAssistSession(
          {
            ...teaser,
            approved: true,
            queue: (teaser.queue || []).map((s) => ({ ...s, status: "ready" })),
          },
          isEn2
        );
      }
      btn.textContent = isEn2 ? "Opened" : "Открыто";
      btn.disabled = true;
      post?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  function downloadBlob(filename, content, mime) {
    const blob = new Blob([content], { type: mime || "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1500);
  }

  function bindExportButtons(data, report, rd) {
    const exports = data.exports || report.exports || {};
    const names = exports.filenames || {};
    const pdfHtml =
      (rd && rd.html) ||
      data.consultation_html ||
      data.rd_html ||
      exports.consultation_html ||
      exports.rd_html ||
      exports.print_html ||
      "";
    const pdfMd =
      (rd && rd.markdown) ||
      data.rd_markdown ||
      data.core_markdown ||
      exports.consultation_md ||
      exports.rd_markdown ||
      "";
    const map = {
      "gen-dl-rd": () => {
        if (!pdfHtml && !pdfMd) {
          alert(lang() === "en" ? "PDF not ready — run generate again" : "PDF ещё не готов — запустите генерацию снова");
          return;
        }
        downloadBlob(
          names.pdf_html || names.html || "metrix-consultation.pdf.html",
          pdfHtml || `<pre>${pdfMd.replace(/</g, "&lt;")}</pre>`,
          "text/html;charset=utf-8"
        );
      },
      "gen-dl-md": () =>
        downloadBlob(names.md || "metrix-consultation.md", pdfMd || "", "text/markdown;charset=utf-8"),
      "gen-dl-csv": () =>
        downloadBlob(names.csv || "metrix-cards.csv", exports.cards_csv || "", "text/csv;charset=utf-8"),
    };
    Object.keys(map).forEach((id) => {
      const el = $("#" + id);
      if (!el) return;
      el.onclick = map[id];
    });
  }

  function paintPersonality(p, isEn) {
    const host = $("#gen-personality");
    if (!host) return;
    if (!p || !p.primary_label) {
      host.innerHTML = `<p class="how-lead">${isEn ? "Author pack after payment." : "Пак автора — после оплаты."}</p>`;
      return;
    }
    host.innerHTML = `
      <div class="eyebrow">${isEn ? "Author uniqueness" : "Авторская уникальность"}</div>
      <strong>${escapeHtml(p.primary_label)} · ${escapeHtml(p.secondary_label || "")}</strong>
      <p class="how-lead">${escapeHtml(p.intent || "")}</p>
      <ul class="clean-list">${(p.success_criteria || []).map((g) => `<li>${escapeHtml(g)}</li>`).join("")}</ul>
    `;
  }

  function renderAssistSession(session, isEn) {
    const assistEl = $("#gen-assist-path");
    if (!assistEl) return;
    const queue = session.queue || [];
    const prog = session.progress || {};
    assistEl.innerHTML = `
      <div class="eyebrow">${isEn ? "Deploy agent" : "Агент деплоя"}</div>
      <p class="how-lead">session ${escapeHtml(session.session_id || "local")} · ${prog.done || 0}/${prog.total || queue.length}</p>
      ${queue
        .map(
          (s) =>
            `<div class="assist-step ${escapeHtml(s.status || "")}"><strong>${escapeHtml(s.id)}</strong> ${escapeHtml(
              s.title || ""
            )}<div class="how-lead">${escapeHtml(s.action || "")}</div></div>`
        )
        .join("")}
    `;
  }

  async function advanceAssistAgent(isEn) {
    const sid = state.assistSessionId;
    if (!sid) return;
    try {
      const res = await fetch(`${apiBase()}/api/v1/analytics/assist-agent/advance`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sid, note: "ui_advance" }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const payload = await res.json();
      if (payload.session) renderAssistSession(payload.session, isEn);
    } catch (ex) {
      const el = $("#gen-assist-path");
      if (el) {
        el.insertAdjacentHTML(
          "beforeend",
          `<p class="how-lead" style="color:var(--danger)">${isEn ? "Advance failed" : "Advance не удался"}: ${escapeHtml(ex.message)}</p>`
        );
      }
    }
  }

  function paintForecast(out) {
    const host = $("#gen-forecast");
    if (!host) return;
    const fc = out.implementation_forecast || {};
    const L = lang();
    const isEn = L === "en";
    // Graceful fallback if API not yet upgraded
    const passes = fc.passes || 7;
    const scores = Array.isArray(fc.pass_scores) ? fc.pass_scores : [];
    const readiness =
      fc.readiness_if_approved != null
        ? fc.readiness_if_approved
        : Math.min(
            0.97,
            0.55 +
              (Number((out.quality || {}).anti_template_score) || 0.5) * 0.35 +
              (out.final_gate?.go_prod ? 0.08 : 0)
          );
    const channel = (out.channel && out.channel.mode) || fc.channel || "hybrid";
    const band =
      fc.quality_band ||
      (readiness >= 0.82 ? "ultra" : readiness >= 0.7 ? "strong" : readiness >= 0.55 ? "solid" : "refine");
    const summary =
      fc.summary ||
      (isEn
        ? `After ${passes} generation passes, estimated implementation quality if you approve real rollout (${channel}): ${(
            readiness * 100
          ).toFixed(0)}% — band ${band}.`
        : `После ${passes} прогонов генерации оценка качества реального внедрения при утверждении (${channel}): ${(
            readiness * 100
          ).toFixed(0)}% — полоса ${band}.`);
    const cards = [
      {
        k: isEn ? "Passes" : "Прогоны",
        v: String(passes),
      },
      {
        k: isEn ? "Channel" : "Канал",
        v: String(channel),
      },
      {
        k: isEn ? "If approved" : "Если утвердить",
        v: `${Math.round(readiness * 100)}% · ${band}`,
      },
      {
        k: isEn ? "Assist" : "Ассист",
        v: isEn
          ? "Implementation assistant + tester-strategist"
          : "Ассистент внедрения + тестировщик-стратег",
      },
    ];
    const scoreStrip =
      scores.length > 0
        ? `<div class="forecast-scores">${scores
            .map(
              (s, i) =>
                `<span class="forecast-score-chip" title="pass ${i + 1}">${escapeHtml(
                  String(Math.round(Number(s) * 100))
                )}%</span>`
            )
            .join("")}</div>`
        : "";
    host.innerHTML =
      `<p class="forecast-summary">${escapeHtml(summary)}</p>` +
      scoreStrip +
      `<div class="forecast-cards">${cards
        .map(
          (c) =>
            `<div class="forecast-card"><div class="eyebrow">${escapeHtml(
              c.k
            )}</div><strong>${escapeHtml(c.v)}</strong></div>`
        )
        .join("")}</div>`;
  }

  // ── Business Tasks ────────────────────────────────────────────────────────
  async function loadServices() {
    const grid = $("#svc-grid");
    if (!grid) return;
    const L = lang();
    try {
      const res = await fetch(
        `${apiBase()}${D.api.businessServicesPath || "/api/v1/analytics/business-services"}?lang=${encodeURIComponent(L)}`
      );
      if (!res.ok) throw new Error("services");
      const data = await res.json();
      paintServices(data.services || []);
    } catch (_) {
      paintServices(fallbackServices(L));
    }
  }

  function fallbackServices(L) {
    const isEn = L === "en";
    return [
      {
        id: "ops_reframe",
        name: isEn ? "Ops Contour" : "Операционный контур",
        tagline: isEn ? "One metric, leaks, scoreboard" : "Одна метрика, утечки, табло",
        benefit: isEn
          ? "Less rework · clear weekly gate · more margin from same hours"
          : "Меньше переделок · ясный weekly gate · маржа из тех же часов",
        examples: [
          {
            niche: "ai-agencies",
            text: isEn
              ? "AI studio: −15% rework via handoff scoreboard"
              : "AI-студия: −15% rework через scoreboard handoff",
          },
        ],
        cta_mode: "consult",
      },
      {
        id: "offer_pack",
        name: isEn ? "Offer Packaging" : "Упаковка предложения",
        tagline: isEn ? "Promise · boundaries · pack" : "Обещание · границы · пакет",
        benefit: isEn
          ? "Client sees what they pay for · easier close"
          : "Клиент сразу видит «за что платит» · проще закрыть сделку",
        examples: [
          {
            niche: "expert-services",
            text: isEn
              ? "Expert: 90-day pack instead of hourly"
              : "Эксперт: пакет 90 дней вместо «почасовки»",
          },
        ],
        cta_mode: "consult",
      },
      {
        id: "tech_tz",
        name: isEn ? "Implementation Spec" : "Тех-ТЗ под внедрение",
        tagline: isEn ? "Scope · acceptance · out of scope" : "Объём · приёмка · вне рамок",
        benefit: isEn
          ? "A document you can hand to an executor today"
          : "Документ, который можно отдать исполнителю сегодня",
        examples: [
          {
            niche: "api-for-devs",
            text: isEn
              ? "Integrations: scope + non-goals + 3 accept scenarios"
              : "Интеграции: scope + non-goals + приёмка 3 сценария",
          },
        ],
        cta_mode: "consult",
      },
      {
        id: "ai_agent_desk",
        name: isEn ? "Task AI Agent" : "ИИ-агент под задачу",
        tagline: isEn ? "Doc → agent on accepted scope" : "Документ → агент по принятому объёму",
        benefit: isEn
          ? "Not chat for chat’s sake — executable loop with stops"
          : "Не чат ради чата — исполнимый контур с стоп-правилами",
        examples: [
          {
            niche: "freelace-d2c",
            text: isEn
              ? "Freelance: agent for match + delivery checklist"
              : "Фриланс: агент по match + delivery checklist",
          },
        ],
        cta_mode: "consult",
      },
      {
        id: "distribution_engine",
        name: isEn ? "3D Distribution" : "Дистрибуция 3D",
        tagline: isEn ? "Brand · platforms · networking" : "Бренд · площадки · связи",
        benefit: isEn
          ? "7 days: 1 move per channel · no bloated retainers"
          : "7 дней: 1 ход в каждом канале · без раздутых подписок",
        examples: [
          {
            niche: "education",
            text: isEn
              ? "Education: brand + platform + 3 warm intros"
              : "Обучение: бренд + площадка + 3 тёплых intro",
          },
        ],
        cta_mode: "consult",
      },
      {
        id: "expert_base_gen",
        name: isEn ? "Project Expert Base" : "Экспертная база проекта",
        tagline: isEn ? "Unique knowledge layers per brief" : "Уникальные слои знаний под ТЗ",
        benefit: isEn
          ? "A base for your loop — not a wiki for bulk"
          : "База под ваш контур, не «википедия ради объёма»",
        examples: [
          {
            niche: "cost-ops",
            text: isEn
              ? "Unit-econ: leak ontology + kill-switches"
              : "Unit-экон.: ontology утечек + kill-switches",
          },
        ],
        cta_mode: "consult",
      },
      {
        id: "control_panel",
        name: isEn ? "Control Panel" : "Панель управления",
        tagline: isEn ? "Metrics · tasks · risks" : "Метрики · задачи · риски",
        benefit: isEn ? "Sense · Decide · Act — no UI noise" : "Sense · Decide · Act — без UI-шума",
        examples: [
          {
            niche: "automation-builders",
            text: isEn
              ? "Auto: 3 pilot widgets, not 40 metrics"
              : "Авто: 3 виджета на пилот, не 40 метрик",
          },
        ],
        cta_mode: "consult",
      },
      {
        id: "full_business_gen",
        name: isEn ? "Generate Business 🔥" : "Сгенерировать бизнес 🔥",
        tagline: isEn
          ? "Orchestrate 10 niches → system + base + panel"
          : "Оркестрация 10 ниш → система + база + панель",
        benefit: isEn
          ? "Planning brain: ranks niches, service stack, compute"
          : "Мозг планирования: ранжирует ниши, стек услуг, расчёты",
        examples: [
          {
            niche: "all",
            text: isEn
              ? "In: essence · Out: plan + base + panel across 10 niches"
              : "Вход: суть · Выход: план + база + панель по 10 нишам",
          },
        ],
        cta_mode: "generate",
      },
    ];
  }

  function paintServices(list) {
    const grid = $("#svc-grid");
    if (!grid) return;
    state._svcList = list;
    grid.innerHTML = list
      .map((s) => {
        const examples = (s.examples || [])
          .slice(0, 2)
          .map((ex) => {
            const text = typeof ex === "string" ? ex : ex.text || "";
            return text
              ? `<li>${escapeHtml(text)}</li>`
              : "";
          })
          .join("");
        const isGen = s.cta_mode === "generate" || s.id === "full_business_gen";
        return `
      <article class="svc-card svc-card-rich" data-svc="${escapeHtml(s.id)}" tabindex="0" role="button">
        <div class="svc-card-top">
          <h3>${escapeHtml(s.name)}</h3>
          <p class="svc-tagline">${escapeHtml(s.tagline || "")}</p>
        </div>
        <p class="svc-benefit">${escapeHtml(s.benefit || s.wow || "")}</p>
        ${
          examples
            ? `<div class="svc-examples"><div class="eyebrow">${escapeHtml(
                t("tasks_example_label")
              )}</div><ul>${examples}</ul></div>`
            : ""
        }
        <div class="svc-card-cta">${escapeHtml(
          isGen ? t("cta_generate") : t("cta_card_consult")
        )}</div>
      </article>`;
      })
      .join("");
    grid.onclick = (e) => {
      const card = e.target.closest("[data-svc]");
      if (!card) return;
      const id = card.dataset.svc;
      const svc = (state._svcList || []).find((x) => x.id === id) || { id };
      if (svc.cta_mode === "generate" || id === "full_business_gen") {
        setMode("generate");
        return;
      }
      openConsultFromTask(svc);
    };
  }

  init();
})();
