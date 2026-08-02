/**
 * Metrix AI — public UI
 * EN default · working RU/EN · Products + Consult only
 * Worker path: accept → pay → mass payout (simple copy)
 */
(function () {
  const D = window.METRIX_DATA;
  if (!D) {
    console.error("METRIX_DATA missing");
    return;
  }

  const state = {
    mode: "marketplace",
    industry: "all",
    selectedFlagship: null,
    marqueeTimer: null,
    marqueeIndex: 0,
    lastProcess: null,
    freeWorkId: null,
    freeWork: null,
  };

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  function t(key) {
    return D.t ? D.t(key) : key;
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
    // default EN (first visit) — only if unset
    try {
      if (!localStorage.getItem("metrix_lang")) {
        D.setLang("en");
      }
    } catch (e) {
      /* ignore */
    }
    applyLangChrome();
    renderAll();
    bindModeSwitch();
    bindLang();
    bindScrollJumps();
    bindModal();
    bindForm();
    bindFreeWork();
    startMarquee();

    const params = new URLSearchParams(location.search);
    if (params.get("mode") === "request") setMode("request");
    if (params.get("lang") === "ru" || params.get("lang") === "en") {
      D.setLang(params.get("lang"));
      applyLangChrome();
      renderAll();
    }
    if (params.get("industry")) {
      state.industry = params.get("industry");
      const ind = $("#req-industry");
      if (ind) ind.value = state.industry;
    }
  }

  function applyLangChrome() {
    const lang = D.getLang();
    document.documentElement.lang = lang;
    $$(".lang-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.lang === lang);
    });
    $$("[data-i18n]").forEach((el) => {
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
    }
    const pkg = $("#pkg-why");
    if (pkg) pkg.textContent = t("pricing_why");
    const lead = $("#how-it-works-lead");
    if (lead) lead.textContent = t("how_lead");
  }

  function renderAll() {
    fillRequestSelects();
    renderNicheGrid();
    renderFlagshipDetails();
    renderFlagships();
    renderHowItWorks();
    renderAudienceSplit();
    paintMarquee(state.marqueeIndex || 0);
  }

  function bindLang() {
    $$(".lang-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        const lang = btn.dataset.lang;
        if (!lang) return;
        D.setLang(lang);
        applyLangChrome();
        renderAll();
      });
    });
  }

  function setMode(mode) {
    if (mode !== "marketplace" && mode !== "request") mode = "marketplace";
    state.mode = mode;
    $$(".mode-switch button").forEach((btn) => {
      const on = btn.dataset.mode === mode;
      btn.classList.toggle("active", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });
    $$(".mode-panel").forEach((panel) => {
      const on = panel.dataset.panel === mode;
      panel.classList.toggle("active", on);
      if (on) panel.removeAttribute("hidden");
      else panel.setAttribute("hidden", "");
    });
    if (mode === "request") {
      $("#mode-request")?.scrollIntoView({ behavior: "smooth", block: "start" });
    } else {
      $("#mode-marketplace")?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  function bindModeSwitch() {
    $$(".mode-switch button").forEach((btn) => {
      btn.addEventListener("click", () => setMode(btn.dataset.mode));
    });
    $$("[data-mode-jump]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const m = btn.dataset.modeJump;
        if (m === "pricing") {
          $("#pricing")?.scrollIntoView({ behavior: "smooth" });
          return;
        }
        if (m === "techwrite") {
          setMode("request");
          const tr = $("#req-track");
          if (tr) tr.value = "product";
          return;
        }
        setMode(m === "consult" ? "request" : m);
      });
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
      if (f?.cta === "techwrite") {
        setMode("request");
        const tr = $("#req-track");
        if (tr) tr.value = "product";
        return;
      }
      setMode("request");
      if (f) {
        const tr = $("#req-track");
        if (tr && f.track) tr.value = f.track === "models" ? "models" : f.track;
        if (f.industryHint) {
          state.industry = f.industryHint;
          const ind = $("#req-industry");
          if (ind) ind.value = f.industryHint;
        }
      }
    });
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

    $("#btn-tech-write")?.addEventListener("click", () => {
      const tr = $("#req-track");
      if (tr) tr.value = "product";
      form.requestSubmit();
    });

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const business = ($("#req-business")?.value || "").trim();
      const industry = $("#req-industry")?.value || "";
      const track = $("#req-track")?.value || "";
      const err = $("#form-error");
      const ok = $("#form-success");
      if (err) err.textContent = "";
      if (ok) ok.textContent = "";
      if (!industry || business.length < 20) {
        if (err) err.textContent = D.getLang() === "ru"
          ? "Ниша + бизнес (≥20 символов)"
          : "Niche + business (≥20 characters)";
        return;
      }
      try {
        const res = await fetch(`${apiBase()}${D.api.processPath || "/api/v1/process"}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            industry,
            business,
            track: track || "all",
            name: "",
            contact: [$("#req-x")?.value, $("#req-telegram")?.value].filter(Boolean).join(" · "),
          }),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        state.lastProcess = data;
        paintConsult(data);
        if (ok) ok.textContent = "OK";
      } catch (ex) {
        if (err) err.textContent = ex.message;
      }
    });

    $("#btn-new-consult")?.addEventListener("click", () => {
      if ($("#consult-result")) $("#consult-result").hidden = true;
      if ($("#free-work-panel")) $("#free-work-panel").hidden = true;
    });
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
              "Free work after consult for operational contour and next steps.",
            industry,
            track: $("#req-track")?.value || "all",
            lang: D.getLang(),
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
        body: JSON.stringify({ work_id: state.freeWorkId, answers: {} }),
      });
      paintFreeWork(await res.json());
    });
  }

  function paintFreeWork(data) {
    const panel = $("#free-work-panel");
    if (!panel) return;
    panel.hidden = false;
    $("#fw-title").textContent = data.title || "Free work";
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

  init();
})();
