/**
 * Metrix AI — public UI (flagships, marquee why-us, how-it-works, pricing)
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
  };

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  function init() {
    renderIndustryStrip();
    fillRequestSelects();
    renderFlagships();
    renderHowItWorks();
    renderPackageBanner();
    bindModeSwitch();
    bindModal();
    bindForm();
    startMarquee();

    const note = $("#contact-note");
    if (note) {
      note.textContent = "";
      note.hidden = true;
    }

    const params = new URLSearchParams(location.search);
    if (params.get("mode") === "request") setMode("request");
    if (params.get("industry")) {
      state.industry = params.get("industry");
      $$(".industry-tile").forEach((t) =>
        t.classList.toggle("active", t.dataset.industry === state.industry)
      );
    }
  }

  function setMode(mode) {
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
        setMode(m);
      });
    });
  }

  function renderIndustryStrip() {
    const root = $("#industry-strip");
    if (!root) return;
    root.innerHTML = D.industries
      .map(
        (ind) => `
      <button type="button" class="industry-tile" data-industry="${ind.id}"
        style="--tile-accent:${ind.accent}">
        <div class="icon">${ind.icon}</div>
        <strong>${escapeHtml(ind.short || ind.name)}</strong>
        <span>${escapeHtml(ind.blurb)}</span>
      </button>`
      )
      .join("");

    root.addEventListener("click", (e) => {
      const tile = e.target.closest("[data-industry]");
      if (!tile) return;
      state.industry = tile.dataset.industry;
      $$(".industry-tile").forEach((t) =>
        t.classList.toggle("active", t.dataset.industry === state.industry)
      );
      const ind = $("#req-industry");
      if (ind) ind.value = state.industry;
    });
  }

  function renderFlagships() {
    const grid = $("#program-grid");
    if (!grid) return;
    const list = D.getFlagships ? D.getFlagships() : D.flagships || [];
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
          <span class="linkish">Details →</span>
        </div>
      </button>`;
      })
      .join("");

    grid.onclick = (e) => {
      const card = e.target.closest("[data-flag]");
      if (!card) return;
      openFlagship(card.dataset.flag);
    };

    paintMarquee(0);
  }

  function startMarquee() {
    if (state.marqueeTimer) clearInterval(state.marqueeTimer);
    const slides = D.whyUsSlides || [];
    if (!slides.length) return;
    state.marqueeTimer = setInterval(() => {
      state.marqueeIndex = (state.marqueeIndex + 1) % slides.length;
      paintMarquee(state.marqueeIndex);
    }, 4200);
  }

  function paintMarquee(idx) {
    const slides = D.whyUsSlides || [];
    if (!slides.length) return;
    const s = slides[idx % slides.length];
    $$("[data-marquee-host]").forEach((host) => {
      const label = host.querySelector("[data-marquee-label]");
      const text = host.querySelector("[data-marquee-text]");
      const dots = host.querySelector("[data-marquee-dots]");
      if (label) label.textContent = s.title;
      if (text) {
        text.classList.remove("marquee-in");
        void text.offsetWidth;
        text.textContent = s.text;
        text.classList.add("marquee-in");
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
    const f = (D.flagships || []).find((x) => x.id === id);
    if (!f) return;
    state.selectedFlagship = id;
    $("#modal-title").textContent = f.title;
    const stick = f.sticker
      ? `<span class="tag accent">${escapeHtml(f.sticker)}</span>`
      : "";
    $("#modal-tags").innerHTML =
      `${stick}<span class="tag">${escapeHtml(f.track)}</span>`;

    let body = "";
    if (f.marquee) {
      const slides = D.whyUsSlides || [];
      body = slides
        .map(
          (s) => `
        <div class="detail-block">
          <h4>${escapeHtml(s.title)}</h4>
          <p style="color:var(--text-muted);font-size:0.95rem;line-height:1.65">${escapeHtml(s.text)}</p>
        </div>`
        )
        .join("");
    } else {
      const detail = (f.detail || f.essence || "").replace(/\n/g, "<br/>");
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
      const f = (D.flagships || []).find((x) => x.id === state.selectedFlagship);
      if (f?.cta === "pricing") {
        $("#pricing")?.scrollIntoView({ behavior: "smooth" });
        return;
      }
      if (f?.cta === "techwrite") {
        setMode("request");
        const tr = $("#req-track");
        if (tr) tr.value = "product";
        const biz = $("#req-business");
        if (biz && !biz.value.trim()) {
          biz.placeholder = "Free tech write: describe the business and what must be specified…";
        }
        return;
      }
      setMode("request");
      if (f) {
        const tr = $("#req-track");
        if (tr && f.track) tr.value = f.track === "models" ? "models" : f.track;
      }
    });
  }

  function renderHowItWorks() {
    const root = $("#how-it-works-body");
    const how = D.howItWorks;
    if (!root || !how) return;
    const lead = $("#how-it-works-lead");
    if (lead) lead.textContent = how.lead || "";
    root.innerHTML = (how.steps || [])
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

  function fillRequestSelects() {
    const ind = $("#req-industry");
    const tr = $("#req-track");
    if (ind) {
      ind.innerHTML =
        `<option value="">Select…</option>` +
        D.industries.map((i) => `<option value="${i.id}">${escapeHtml(i.name)}</option>`).join("");
    }
    if (tr) {
      tr.innerHTML =
        `<option value="">All three</option>` +
        D.tracks.map((t) => `<option value="${t.id}">${escapeHtml(t.label)}</option>`).join("");
    }
  }

  function bindForm() {
    const form = $("#request-form");
    if (!form) return;

    $("#btn-tech-write")?.addEventListener("click", () => {
      const tr = $("#req-track");
      if (tr) tr.value = "product";
      const biz = $("#req-business");
      if (biz) {
        biz.focus();
        if (!biz.value.trim()) {
          biz.placeholder =
            "Free tech write: describe the business and what must be specified…";
        }
      }
      form.requestSubmit?.() || form.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
    });

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const err = $("#form-error");
      const ok = $("#form-success");
      err.classList.remove("show");
      ok.classList.remove("show");

      const industry = $("#req-industry").value;
      const business = $("#req-business").value.trim();
      const name = $("#req-name").value.trim();
      const contact = $("#req-email").value.trim();
      const track = $("#req-track").value;

      if (!industry) {
        err.textContent = "Select an industry.";
        err.classList.add("show");
        return;
      }
      if (!business || business.length < 20) {
        err.textContent = "Describe your business (at least a few sentences).";
        err.classList.add("show");
        return;
      }

      const payload = {
        industry,
        industryName: D.industries.find((i) => i.id === industry)?.name,
        track: track || "all",
        name,
        contact,
        business,
        createdAt: new Date().toISOString(),
      };

      const key = "metrix_ai_requests";
      const prev = JSON.parse(localStorage.getItem(key) || "[]");
      prev.push(payload);
      localStorage.setItem(key, JSON.stringify(prev));

      const api = D.api || {};
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;

      // baseUrl may be "" (same-origin via Vercel rewrite) — do not treat as falsy disable
      if (api.enabled) {
        try {
          const base = (api.baseUrl == null ? "" : String(api.baseUrl)).replace(/\/$/, "");
          const res = await fetch(`${base}${api.processPath || "/api/v1/process"}`, {
            method: "POST",
            headers: { "Content-Type": "application/json", Accept: "application/json" },
            body: JSON.stringify({
              industry: payload.industry,
              business: payload.business,
              track: payload.track,
              name: payload.name,
              contact: payload.contact,
            }),
          });
          if (!res.ok) throw new Error(`API ${res.status}`);
          const data = await res.json();
          if (!data.ok) throw new Error((data.errors || []).join("; ") || "failed");

          const idea = data.demo_idea || {};
          const cat = (data.meta && data.meta.category_router) || {};
          const primary = cat.primary || "—";
          const packUrl =
            (data.meta &&
              data.meta.paid_product_core &&
              data.meta.paid_product_core.package_deliverable &&
              data.meta.paid_product_core.package_deliverable.url) ||
            "";

          ok.innerHTML = `
            <strong>Consultation + free tech path ready</strong> · ${escapeHtml(payload.industryName)}<br/>
            Direction: <strong>${escapeHtml(String(primary))}</strong><br/>
            ${escapeHtml((idea.title || "—").slice(0, 120))}<br/>
            ${packUrl ? `<a href="${escapeHtml(packUrl)}" target="_blank" rel="noopener">Open result pack (tech write) →</a><br/>` : ""}
            <a href="https://x.com/karimmetrix" target="_blank" rel="noopener">Message @karimmetrix →</a>`;
          ok.classList.add("show");
          form.reset();
          if (submitBtn) submitBtn.disabled = false;
          return;
        } catch (apiErr) {
          console.warn("API unavailable:", apiErr);
        }
      }

      ok.innerHTML = `
        Request saved. Message
        <a href="https://x.com/karimmetrix" target="_blank" rel="noopener">@karimmetrix</a>
        for free consult + free tech write.`;
      ok.classList.add("show");
      form.reset();
      if (submitBtn) submitBtn.disabled = false;
    });
  }

  function renderPackageBanner() {
    const title = $("#pkg-title");
    const why = $("#pkg-why");
    const p = D.packagePricing || {};
    if (title) title.textContent = "Pricing";
    if (why) {
      why.innerHTML = `
        <strong>Consult — free.</strong> <strong>Tech TZ / technical writing — free.</strong><br/>
        Pilot: ops $${p.pilotOpsUsd || 690} · product $${p.pilotProductUsd || 790} · promotion $${p.pilotPromotionUsd || 490}.
        Main package $${p.mainPackageUsd || 2490} after pilot success.`;
    }
  }

  function escapeHtml(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
