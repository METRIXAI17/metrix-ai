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

  const MODES = ["marketplace", "request", "tasks", "generate"];

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
        return `
      <button type="button" class="card card-flag${f.marquee ? " card-flag-marquee" : ""}" data-flag="${f.id}"
        style="--flag-accent:${accent}">
        ${sticker}
        <h3>${escapeHtml(f.title)}</h3>
        ${marquee}
        <div class="card-foot">
          <span class="tag accent">${escapeHtml(f.track)}</span>
          <span class="linkish">${escapeHtml(t("details"))}</span>
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
      close();
      const f = D.getFlagships().find((x) => x.id === state.selectedFlagship);
      if (f?.cta === "pricing") {
        $("#pricing")?.scrollIntoView({ behavior: "smooth" });
        return;
      }
      if (f?.cta === "generate") {
        setMode("generate");
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
    const legend = $("#matryoshka-legend");
    const title = $("#matryoshka-title");
    const text = $("#matryoshka-text");
    const indexEl = $("#matryoshka-index");
    const accent = $("#matryoshka-accent");
    if (!host || !D.getSystemLayers) return;

    const layers = D.getSystemLayers();
    // Designer palette: outer → core (violet → cyan → teal)
    const palette = [
      { stroke: "#a78bfa", glow: "rgba(167, 139, 250, 0.55)" }, // capital
      { stroke: "#c4b5fd", glow: "rgba(196, 181, 253, 0.5)" }, // marketing
      { stroke: "#38bdf8", glow: "rgba(56, 189, 248, 0.55)" }, // coop
      { stroke: "#5eead4", glow: "rgba(94, 234, 212, 0.55)" }, // assist
      { stroke: "#2dd4bf", glow: "rgba(45, 212, 191, 0.7)" }, // core
    ];
    // Radii for concentric rings (viewBox 0 0 400 400, center 200,200)
    const radii = [172, 138, 104, 72, 42];
    const strokeW = [22, 20, 18, 16, 28];
    const cx = 200;
    const cy = 200;

    // SVG rings: pointer-events: stroke so outer disks don't block inner rings
    const ringEls = layers
      .map((layer, i) => {
        const p = palette[i] || palette[0];
        const r = radii[i] != null ? radii[i] : 160 - i * 30;
        const sw = strokeW[i] != null ? strokeW[i] : 18;
        const isCore = layer.id === "core" || i === layers.length - 1;
        if (isCore) {
          return `
            <g class="mx-ring-group" data-layer="${escapeHtml(layer.id)}" data-i="${i}">
              <circle class="mx-core-disc" cx="${cx}" cy="${cy}" r="${r - 2}"
                fill="url(#mxCoreFill)" stroke="${p.stroke}" stroke-width="2.5" />
              <circle class="mx-core-pulse" cx="${cx}" cy="${cy}" r="${Math.max(18, r - 14)}"
                fill="url(#mxCoreGlow)" />
              <text class="mx-core-letter" x="${cx}" y="${cy + 8}" text-anchor="middle">M</text>
              <circle class="mx-ring-hit mx-ring-hit-core" cx="${cx}" cy="${cy}" r="${r + 6}"
                fill="transparent" stroke="transparent" stroke-width="1"
                data-layer="${escapeHtml(layer.id)}" tabindex="0" role="button"
                aria-label="${escapeHtml(layer.label)}" />
            </g>`;
        }
        return `
          <g class="mx-ring-group" data-layer="${escapeHtml(layer.id)}" data-i="${i}" style="--mx-glow:${p.glow}; --mx-stroke:${p.stroke}">
            <circle class="mx-ring-track" cx="${cx}" cy="${cy}" r="${r}"
              fill="none" stroke="rgba(148,163,184,0.12)" stroke-width="${sw}" />
            <circle class="mx-ring-arc" cx="${cx}" cy="${cy}" r="${r}"
              fill="none" stroke="${p.stroke}" stroke-width="${sw}"
              stroke-linecap="round" />
            <text class="mx-ring-label" x="${cx}" y="${cy - r}" text-anchor="middle"
              dy="-0.35em">${escapeHtml(layer.short || layer.label)}</text>
            <circle class="mx-ring-hit" cx="${cx}" cy="${cy}" r="${r}"
              fill="none" stroke="transparent" stroke-width="${sw + 14}"
              data-layer="${escapeHtml(layer.id)}" tabindex="0" role="button"
              aria-label="${escapeHtml(layer.label)}" />
          </g>`;
      })
      .join("");

    host.innerHTML = `
      <svg class="matryoshka-svg" viewBox="0 0 400 400" role="img" aria-label="Metrix layers">
        <defs>
          <radialGradient id="mxCoreFill" cx="40%" cy="35%" r="70%">
            <stop offset="0%" stop-color="#134e4a"/>
            <stop offset="55%" stop-color="#0c1a22"/>
            <stop offset="100%" stop-color="#070a0f"/>
          </radialGradient>
          <radialGradient id="mxCoreGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="rgba(94,234,212,0.55)"/>
            <stop offset="100%" stop-color="rgba(94,234,212,0)"/>
          </radialGradient>
          <filter id="mxSoftGlow" x="-40%" y="-40%" width="180%" height="180%">
            <feGaussianBlur stdDeviation="4" result="b"/>
            <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
          <radialGradient id="mxStageFade" cx="50%" cy="50%" r="50%">
            <stop offset="60%" stop-color="rgba(7,10,15,0)"/>
            <stop offset="100%" stop-color="rgba(7,10,15,0.55)"/>
          </radialGradient>
        </defs>
        <circle cx="200" cy="200" r="196" fill="rgba(12,18,28,0.55)" stroke="rgba(94,234,212,0.12)" stroke-width="1"/>
        <circle cx="200" cy="200" r="196" fill="url(#mxStageFade)"/>
        ${ringEls}
      </svg>`;

    if (legend) {
      legend.innerHTML = layers
        .map((layer, i) => {
          const p = palette[i] || palette[0];
          const num = String(layers.length - i).padStart(2, "0");
          return `<button type="button" class="matryoshka-chip" data-layer="${escapeHtml(
            layer.id
          )}" style="--chip:${p.stroke}" role="tab" aria-selected="false">
            <span class="matryoshka-chip-dot"></span>
            <span class="matryoshka-chip-n">${num}</span>
            <span class="matryoshka-chip-t">${escapeHtml(layer.short || layer.label)}</span>
          </button>`;
        })
        .join("");
    }

    const show = (layer, i) => {
      if (!layer) return;
      const idx = i != null ? i : layers.findIndex((l) => l.id === layer.id);
      host.querySelectorAll(".mx-ring-group").forEach((g) => {
        g.classList.toggle("is-active", g.dataset.layer === layer.id);
      });
      host.querySelectorAll(".mx-ring-hit").forEach((el) => {
        el.setAttribute("aria-pressed", el.dataset.layer === layer.id ? "true" : "false");
      });
      if (legend) {
        legend.querySelectorAll(".matryoshka-chip").forEach((chip) => {
          const on = chip.dataset.layer === layer.id;
          chip.classList.toggle("is-active", on);
          chip.setAttribute("aria-selected", on ? "true" : "false");
        });
      }
      if (title) title.textContent = layer.label;
      if (text) text.textContent = layer.text;
      if (indexEl) {
        indexEl.textContent = String(layers.length - (idx >= 0 ? idx : 0)).padStart(2, "0");
      }
      if (accent) {
        const p = palette[idx >= 0 ? idx : 0] || palette[0];
        accent.style.setProperty("--layer-accent", p.stroke);
      }
      const panel = $("#matryoshka-panel");
      if (panel) {
        const p = palette[idx >= 0 ? idx : 0] || palette[0];
        panel.style.setProperty("--layer-accent", p.stroke);
        panel.classList.add("is-lit");
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
      if (legend) {
        const chip = legend.querySelector(`.matryoshka-chip[data-layer="${layer.id}"]`);
        bindLayer(chip, layer, i);
      }
    });

    // Default: core (innermost)
    const coreIdx = layers.length - 1;
    show(layers[coreIdx] || layers[0], coreIdx);
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
        return `
      <article class="tariff-card${tier.popular ? " tariff-popular" : ""}" data-tariff="${escapeHtml(
          tier.id
        )}">
        ${badge}
        <div class="tariff-head">
          <div class="eyebrow">${escapeHtml(tier.id)}</div>
          <h3>${escapeHtml(tier.name)}</h3>
          <div class="tariff-price">${escapeHtml(tier.price)}</div>
          <p class="tariff-period">${escapeHtml(tier.period || "")}</p>
          <p class="tariff-tagline">${escapeHtml(tier.tagline || "")}</p>
        </div>
        <ul class="tariff-list">${items}</ul>
        <button type="button" class="btn ${
          tier.popular ? "btn-primary" : "btn-ghost"
        } tariff-cta" data-mode-jump="request">${escapeHtml(t("tariff_cta"))}</button>
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
    $("#gen-msg").textContent = data.message || out.pre_corrected?.opening_line || "—";
    const gate = out.final_gate || {};
    const gEl = $("#gen-gate");
    if (gEl) {
      gEl.textContent =
        (gate.go_prod ? t("success_go") : t("success_cond")) +
        (gate.verdict ? " · " + gate.verdict : "");
      gEl.classList.toggle("warn", !gate.go_prod);
    }

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
    $("#gen-plan").innerHTML = (plan.steps || [])
      .map(
        (s) =>
          `<div class="mp-card"><strong>${escapeHtml(s.id)}</strong> ${escapeHtml(s.title)} → <em>${escapeHtml(s.default_option || "—")}</em></div>`
      )
      .join("");
    const qs = plan.open_questions || out.interaction?.open_questions || [];
    $("#gen-questions").innerHTML = qs.length
      ? qs.map((q) => `<li>${escapeHtml(q)}</li>`).join("")
      : "<li>—</li>";

    const panel = out.control_panel || {};
    $("#gen-panel").innerHTML = (panel.columns || [])
      .map((col) => {
        const cards = (col.cards || [])
          .slice(0, 4)
          .map((c) => {
            let v = c.v;
            if (typeof v === "object") v = JSON.stringify(v).slice(0, 120);
            return `<div class="mp-card">${escapeHtml(c.k)}: ${escapeHtml(v)}</div>`;
          })
          .join("");
        return `<div><strong>${escapeHtml(col.title)}</strong>${cards}</div>`;
      })
      .join("");

    $("#gen-quality").textContent = JSON.stringify(
      {
        quality: out.quality,
        self_test: out.self_test,
        synthesis: out.synthesis_highlights,
        primary_industry: out.primary_industry,
        channel: out.channel,
        implementation_forecast: out.implementation_forecast,
      },
      null,
      2
    );
    const eb = out.expert_base || {};
    $("#gen-expert").textContent = JSON.stringify(
      {
        id: eb.id,
        name: eb.name,
        summary: eb.summary,
        layers: eb.layers,
        original_moves: eb.original_moves,
      },
      null,
      2
    );
    $("#gen-code").textContent = JSON.stringify(out.autonomous_code_pack || {}, null, 2);
    root.scrollIntoView({ behavior: "smooth", block: "start" });
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
