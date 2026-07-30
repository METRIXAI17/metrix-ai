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
    lastPayload: null,
    lastProcess: null,
    freeWorkId: null,
    freeWork: null,
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
    bindFreeWork();
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
          const meta = data.meta || {};
          const card = meta.free_consult_card || {};
          const cat = meta.category_router || {};
          const dirLabel =
            card.direction_label ||
            cat.primary_label ||
            cat.primary ||
            "—";
          const natural =
            card.natural_label &&
            card.natural_direction &&
            card.natural_direction !== (card.direction || cat.primary)
              ? card.natural_label
              : "";
          const headline = (card.headline || idea.label || idea.title || "Orientation ready").slice(0, 120);
          const blurb = (card.blurb || idea.summary || "").slice(0, 280);
          const reason = (card.reason || "").slice(0, 160);

          const abs = (u) => {
            if (!u) return "";
            if (/^https?:\/\//i.test(u)) return u;
            return `${base}${u.startsWith("/") ? u : `/${u}`}`;
          };
          const packUrl = abs(
            card.pack_url ||
              (meta.paid_product_core &&
                meta.paid_product_core.package_deliverable &&
                meta.paid_product_core.package_deliverable.url) ||
              ""
          );
          const consultUrl = abs(card.consult_url || "");

          state.lastPayload = payload;
          state.lastProcess = data;

          ok.innerHTML = `
            <strong>Consultation ready</strong> · ${escapeHtml(payload.industryName)} ·
            Direction: <strong>${escapeHtml(String(dirLabel))}</strong>${
              natural ? ` <span style="opacity:.75">(also ${escapeHtml(natural)})</span>` : ""
            }`;
          ok.classList.add("show");

          showConsultResult({
            headline,
            blurb,
            reason,
            dirLabel,
            natural,
            industryName: payload.industryName,
            packUrl,
            consultUrl,
            niche: meta.niche_answer || {},
            cta: meta.free_work_cta || {},
          });

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
      // Offline fallback: still show free-work steps from static data
      state.lastPayload = payload;
      showConsultResult({
        headline: "Brief saved (offline)",
        blurb: "API offline — steps below still guide free work. Message @karimmetrix to process live.",
        reason: "",
        dirLabel: payload.track || "all",
        natural: "",
        industryName: payload.industryName,
        packUrl: "",
        consultUrl: "",
        niche: {},
        cta: { label: "Начать работу бесплатно" },
      });
      if (submitBtn) submitBtn.disabled = false;
    });
  }

  function showConsultResult(view) {
    const box = $("#consult-result");
    const fw = $("#free-work-panel");
    if (!box) return;
    box.hidden = false;
    if (fw) fw.hidden = true;

    $("#cr-headline").textContent = view.headline || "Orientation ready";
    $("#cr-meta").textContent = [
      view.industryName,
      view.dirLabel ? `→ ${view.dirLabel}` : "",
      view.natural ? `(also ${view.natural})` : "",
    ]
      .filter(Boolean)
      .join(" ");
    $("#cr-blurb").textContent = [view.blurb, view.reason].filter(Boolean).join(" · ");

    const nicheEl = $("#cr-niche-answer");
    const n = view.niche || {};
    if (nicheEl) {
      if (n.answer) {
        nicheEl.innerHTML = `<strong>${escapeHtml(n.title || "Direction answer")}</strong>${escapeHtml(n.answer)}`;
      } else {
        nicheEl.innerHTML = `<strong>Next</strong>Start free work to unlock niche answer, quizzes, and tech-write draft.`;
      }
    }

    const links = $("#cr-links");
    if (links) {
      const parts = [];
      if (view.packUrl) {
        parts.push(
          `<a href="${escapeHtml(view.packUrl)}" target="_blank" rel="noopener">Full result pack →</a>`
        );
      }
      if (view.consultUrl && view.consultUrl !== view.packUrl) {
        parts.push(
          `<a href="${escapeHtml(view.consultUrl)}" target="_blank" rel="noopener">Consult only →</a>`
        );
      }
      parts.push(
        `<a href="https://x.com/karimmetrix" target="_blank" rel="noopener">@karimmetrix →</a>`
      );
      links.innerHTML = parts.join("");
    }

    const btn = $("#btn-start-free-work");
    if (btn) {
      btn.textContent =
        (view.cta && (view.cta.label || view.cta.label_ru)) || "Начать работу бесплатно";
    }

    box.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function apiBase() {
    const api = D.api || {};
    return (api.baseUrl == null ? "" : String(api.baseUrl)).replace(/\/$/, "");
  }

  function bindFreeWork() {
    $("#btn-start-free-work")?.addEventListener("click", startFreeWork);
    $("#btn-submit-clarify")?.addEventListener("click", submitClarifications);
    $("#btn-advance-phase")?.addEventListener("click", advancePhase);
    $("#btn-new-consult")?.addEventListener("click", () => {
      $("#consult-result").hidden = true;
      $("#free-work-panel").hidden = true;
      $("#form-success")?.classList.remove("show");
      $("#request-form")?.scrollIntoView({ behavior: "smooth" });
    });
  }

  async function startFreeWork() {
    const btn = $("#btn-start-free-work");
    const p = state.lastPayload;
    if (!p) {
      alert("Сначала получите консультацию.");
      return;
    }
    if (btn) btn.disabled = true;
    const base = apiBase();
    const path = (D.api && D.api.freeWorkStartPath) || "/api/v1/analytics/free-work/start";
    const lang =
      /[а-яА-ЯёЁ]/.test((p.business || "").slice(0, 80)) ? "ru" : "en";
    const meta = (state.lastProcess && state.lastProcess.meta) || {};
    const cat = meta.category_router || {};
    const body = {
      business: p.business,
      industry: p.industry,
      track: p.track || "all",
      name: p.name || "",
      contact: p.contact || "",
      lang,
      natural_direction: cat.primary || null,
      request_id: (state.lastProcess && state.lastProcess.request_id) || null,
      include_founders_lane: true,
    };

    try {
      if (D.api && D.api.enabled) {
        const res = await fetch(`${base}${path}`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error(`API ${res.status}`);
        const data = await res.json();
        if (!data.ok && data.error) throw new Error(data.error);
        state.freeWorkId = data.work_id;
        state.freeWork = data;
        renderFreeWork(data);
      } else {
        throw new Error("API disabled");
      }
    } catch (err) {
      console.warn("free-work start failed", err);
      // Client-side skeleton so UX still works
      renderFreeWork(offlineFreeWorkSkeleton(p, lang));
    }
    if (btn) btn.disabled = false;
  }

  function offlineFreeWorkSkeleton(p, lang) {
    const phases = [
      {
        id: "D0_1_start",
        days: "0–1",
        title: lang === "ru" ? "Старт" : "Start",
        system: "Step A",
        actions: [
          { n: 1, action: "Brief", result: "≥20 chars" },
          { n: 2, action: "Industry", result: "market unit" },
          { n: 3, action: "Numbers", result: "less UNDEFINED" },
          { n: 4, action: "Signer", result: "acceptance" },
          { n: 5, action: "Change-prep", result: "constraints" },
        ],
      },
      {
        id: "D1_4_tests",
        days: "1–4",
        title: lang === "ru" ? "Тесты неопределённостей" : "Uncertainty tests",
        system: "Step B",
        actions: [
          { n: 6, action: "Quiz UNDEFINED", result: "assembly ↑" },
          { n: 7, action: "ТОЧНО ДА / НЕТ / НЕ ЗНАЮ", result: "clean status" },
          { n: 8, action: "Numbers for metric/timeline", result: "magnitude" },
          { n: 9, action: "Assembly conditions", result: "map" },
        ],
      },
      {
        id: "D3_10_techwrite",
        days: "3–10",
        title: "Tech write",
        system: "R4",
        actions: [
          { n: 10, action: "Read TZ / charter", result: "scope" },
          { n: 11, action: "Notes on sections", result: "rework" },
          { n: 12, action: "Out of scope", result: "protect pilot" },
          { n: 13, action: "Success metric + signer", result: "gate" },
        ],
      },
    ];
    return {
      work_id: "offline",
      quality_answer: {
        title: "Offline mode",
        answer:
          lang === "ru"
            ? "API недоступен. Пройдите фазы вручную и напишите @karimmetrix."
            : "API offline. Follow phases manually and DM @karimmetrix.",
        free_work_checklist: ["Complete brief numbers", "Name signer", "List out-of-scope"],
        success_metric: "Signed success metric for pilot gate",
        clarification_questions: [
          {
            id: "clr_signer",
            field: "signer",
            question: lang === "ru" ? "Кто signer (ТОЧНО ДА/НЕТ)?" : "Who is the signer?",
          },
        ],
      },
      self_clarifications: [
        {
          id: "clr_signer",
          field: "signer",
          question: lang === "ru" ? "Кто signer?" : "Who is the signer?",
        },
      ],
      phases,
      current_phase: phases[0],
      free_work_checklist: ["Brief", "Signer", "One success metric"],
      tech_write_preview: "# Tech write\n\n(connect API for full draft)",
      founders_lane: {
        title: "Deep Tech × Branding&VA",
        display_hook:
          "Karim — TZ/assembly; Andryusha — Phenomenon→Notation→Object. Один free stream.",
        joint_deliverables_free: [
          { title: "VA name seed", owner: "@andrewsmm1", desc: "3 name candidates" },
          { title: "Tech TZ spine", owner: "@karimmetrix", desc: "scope + acceptance" },
          { title: "Object lockup v0", owner: "@andrewsmm1", desc: "visual token" },
          { title: "Pilot charter dual", owner: "both", desc: "metric + brand constraint" },
        ],
        tasty_moments: [
          "Имя + объект раньше paid pilot",
          "X-ready: crystal visual + mechanism line",
        ],
      },
    };
  }

  function renderFreeWork(data) {
    const panel = $("#free-work-panel");
    if (!panel) return;
    panel.hidden = false;
    state.freeWork = data;

    const qa = data.quality_answer || {};
    const rendered = (qa.rendered && qa.rendered.text) || qa.answer || "";
    $("#fw-title").textContent =
      qa.title || (data.current_phase && data.current_phase.title) || "Free work";
    $("#fw-quality").textContent = rendered;

    // Phases
    const phases = data.phases || [];
    const curId = (data.current_phase && data.current_phase.id) || (phases[0] && phases[0].id);
    const host = $("#fw-phases");
    if (host) {
      host.innerHTML = phases
        .map((ph) => {
          const active = ph.id === curId ? " active" : "";
          const actions = (ph.actions || [])
            .map(
              (a) =>
                `<li><strong>${a.n}.</strong> ${escapeHtml(a.action)} <span class="result-tag">→ ${escapeHtml(
                  a.result || ""
                )}</span></li>`
            )
            .join("");
          return `<div class="fw-phase${active}" data-phase="${escapeHtml(ph.id)}">
            <div class="days">Дни ${escapeHtml(ph.days || "")}</div>
            <h5>${escapeHtml(ph.title || ph.id)}</h5>
            <ol>${actions}</ol>
            <p class="hint" style="margin-top:.4rem">${escapeHtml(ph.system || "")}</p>
          </div>`;
        })
        .join("");
    }

    // Clarifications
    const qs = data.self_clarifications || qa.clarification_questions || [];
    const form = $("#fw-clarify-form");
    if (form) {
      if (!qs.length) {
        form.innerHTML = `<p class="hint">Уточнений нет — можно идти по чеклисту и tech write.</p>`;
      } else {
        form.innerHTML = qs
          .map((q) => {
            const id = escapeHtml(q.id || q.field || "q");
            const label = escapeHtml(q.question || q.question_ru || q.field || id);
            const kind = q.kind || "";
            if (kind === "binary") {
              return `<div class="fw-clarify-item">
                <label for="fw-${id}">${label}</label>
                <select id="fw-${id}" data-field="${id}">
                  <option value="">—</option>
                  <option value="certain_yes">ТОЧНО ДА</option>
                  <option value="certain_no">ТОЧНО НЕТ</option>
                  <option value="unknown">НЕ ЗНАЮ</option>
                </select>
              </div>`;
            }
            return `<div class="fw-clarify-item">
              <label for="fw-${id}">${label}</label>
              <input id="fw-${id}" data-field="${id}" type="text" placeholder="число / факт / не знаю" />
            </div>`;
          })
          .join("");
      }
    }

    // Checklist
    const cl = data.free_work_checklist || qa.free_work_checklist || [];
    const ul = $("#fw-checklist");
    if (ul) {
      ul.innerHTML = cl.map((x) => `<li>${escapeHtml(x)}</li>`).join("") || "<li>—</li>";
    }
    const sm = $("#fw-success-metric");
    if (sm) {
      sm.textContent = data.success_metric || qa.success_metric
        ? `Success metric: ${data.success_metric || qa.success_metric}`
        : "";
    }

    // Tech write
    const pre = $("#fw-tech-md");
    if (pre) pre.textContent = data.tech_write_preview || "(нет preview — уточните поля)";

    // Founders lane
    const fl = data.founders_lane;
    const fcard = $("#fw-founders-card");
    if (fcard && fl) {
      fcard.hidden = false;
      $("#fw-founders-title").textContent = fl.title || "Deep Tech × Branding&VA";
      $("#fw-founders-hook").textContent = fl.display_hook || fl.hook || "";
      const list = $("#fw-founders-list");
      if (list) {
        list.innerHTML = (fl.joint_deliverables_free || [])
          .map(
            (d) =>
              `<li><strong>${escapeHtml(d.title)}</strong> · ${escapeHtml(d.owner || "")} — ${escapeHtml(
                d.desc || ""
              )}</li>`
          )
          .join("");
      }
      const tasty = $("#fw-tasty");
      if (tasty) {
        tasty.innerHTML = (fl.tasty_moments || [])
          .map((t) => `<div class="t-item">✦ ${escapeHtml(t)}</div>`)
          .join("");
      }
    } else if (fcard) {
      fcard.hidden = true;
    }

    panel.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  async function submitClarifications() {
    const form = $("#fw-clarify-form");
    if (!form) return;
    const answers = {};
    form.querySelectorAll("[data-field]").forEach((el) => {
      const v = (el.value || "").trim();
      if (v) answers[el.dataset.field] = v;
    });
    if (!Object.keys(answers).length) {
      alert("Заполните хотя бы одно уточнение.");
      return;
    }

    const base = apiBase();
    const path = (D.api && D.api.freeWorkClarifyPath) || "/api/v1/analytics/free-work/clarify";
    const workId = state.freeWorkId;

    if (!workId || workId === "offline" || !(D.api && D.api.enabled)) {
      // local merge into quality text
      const fw = state.freeWork || {};
      fw.quality_answer = fw.quality_answer || {};
      fw.quality_answer.answer =
        (fw.quality_answer.answer || "") +
        "\n\n[уточнения] " +
        Object.entries(answers)
          .map(([k, v]) => `${k}=${v}`)
          .join(", ");
      fw.self_clarifications = [];
      renderFreeWork(fw);
      return;
    }

    try {
      const res = await fetch(`${base}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ work_id: workId, answers }),
      });
      if (!res.ok) throw new Error(`API ${res.status}`);
      const data = await res.json();
      if (data.ok === false) throw new Error(data.error || "clarify failed");
      // keep phases from previous if missing
      data.phases = data.phases || (state.freeWork && state.freeWork.phases);
      data.founders_lane = data.founders_lane || (state.freeWork && state.freeWork.founders_lane);
      data.self_clarifications = data.open_clarifications || [];
      data.free_work_checklist =
        (data.quality_answer && data.quality_answer.free_work_checklist) ||
        (state.freeWork && state.freeWork.free_work_checklist);
      data.success_metric =
        (data.quality_answer && data.quality_answer.success_metric) ||
        (state.freeWork && state.freeWork.success_metric);
      state.freeWork = { ...(state.freeWork || {}), ...data };
      renderFreeWork(state.freeWork);
    } catch (e) {
      console.warn(e);
      alert("Не удалось отправить уточнения. Проверьте API.");
    }
  }

  async function advancePhase() {
    const workId = state.freeWorkId;
    const base = apiBase();
    if (!workId || workId === "offline" || !(D.api && D.api.enabled)) {
      const fw = state.freeWork || {};
      const phases = fw.phases || [];
      if (!phases.length) return;
      const cur = fw.current_phase || phases[0];
      const idx = Math.min(
        phases.findIndex((p) => p.id === cur.id) + 1,
        phases.length - 1
      );
      fw.current_phase = phases[idx];
      renderFreeWork(fw);
      return;
    }
    try {
      const res = await fetch(
        `${base}${(D.api && D.api.freeWorkAdvancePath) || "/api/v1/analytics/free-work/advance"}?work_id=${encodeURIComponent(
          workId
        )}`,
        { method: "POST", headers: { Accept: "application/json" } }
      );
      if (!res.ok) throw new Error(`API ${res.status}`);
      const data = await res.json();
      state.freeWork = {
        ...(state.freeWork || {}),
        ...data,
        quality_answer: (state.freeWork || {}).quality_answer,
        self_clarifications: (state.freeWork || {}).self_clarifications || [],
        free_work_checklist: (state.freeWork || {}).free_work_checklist,
        tech_write_preview: (state.freeWork || {}).tech_write_preview,
        founders_lane: (state.freeWork || {}).founders_lane,
      };
      renderFreeWork(state.freeWork);
    } catch (e) {
      console.warn(e);
      alert("Не удалось сменить фазу.");
    }
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
