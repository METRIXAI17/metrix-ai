/**
 * Global Ru Workers · Metrix AI — UI
 * Modes: workers | tasks | generate | consult
 * Parent: i18n RU/EN
 */
(function () {
  const D = window.METRIX_DATA;
  const I18N = window.METRIX_I18N;
  if (!D) {
    console.error("METRIX_DATA missing");
    return;
  }

  const state = {
    mode: "workers",
    industry: "all",
    lastGenerate: null,
    lastProcess: null,
    freeWorkId: null,
    freeWork: null,
    workerTask: null,
    genChoices: {},
  };

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  function apiBase() {
    const b = (D.api && D.api.baseUrl) || "";
    if (b) return b.replace(/\/$/, "");
    if (location.hostname === "localhost" || location.hostname === "127.0.0.1") {
      return "http://127.0.0.1:8787";
    }
    return "https://metrix-ai-production.up.railway.app";
  }

  function escapeHtml(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function t(k) {
    return I18N ? I18N.t(k) : k;
  }

  function applyI18n() {
    if (!I18N) return;
    $$("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (key) el.textContent = t(key);
    });
    $$("[data-i18n-ph]").forEach((el) => {
      const key = el.getAttribute("data-i18n-ph");
      if (key) el.placeholder = t(key);
    });
    $$(".lang-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.lang === I18N.lang);
    });
    document.documentElement.lang = I18N.lang || "ru";
  }

  function init() {
    applyI18n();
    fillSelects();
    renderNicheGrid();
    renderHowItWorks();
    bindModeSwitch();
    bindLang();
    bindGenerate();
    bindWorkers();
    bindTasks();
    bindForm();
    bindFreeWork();
    bindModal();

    const params = new URLSearchParams(location.search);
    if (params.get("mode")) setMode(params.get("mode"));
    if (params.get("industry")) {
      state.industry = params.get("industry");
      ["#req-industry", "#gen-industry"].forEach((sel) => {
        const el = $(sel);
        if (el) el.value = state.industry;
      });
    }

    document.addEventListener("metrix:lang", () => {
      applyI18n();
      renderNicheGrid();
      renderHowItWorks();
      loadServices();
    });

    loadServices();
    refreshWorkerDash();
  }

  function bindLang() {
    $$(".lang-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (I18N) I18N.setLang(btn.dataset.lang);
        applyI18n();
        loadServices();
      });
    });
  }

  function setMode(mode) {
    const allowed = ["workers", "tasks", "generate", "consult", "marketplace", "request"];
    if (mode === "marketplace") mode = "workers";
    if (mode === "request") mode = "consult";
    if (!allowed.includes(mode) && mode !== "workers") mode = "workers";
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
    const target = $(`#mode-${mode}`);
    if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
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
        setMode(m);
      });
    });
  }

  function fillSelects() {
    const opts =
      `<option value="">…</option>` +
      (D.industries || [])
        .map((i) => `<option value="${escapeHtml(i.id)}">${escapeHtml(i.name)}</option>`)
        .join("");
    ["#req-industry", "#gen-industry"].forEach((sel) => {
      const el = $(sel);
      if (el) el.innerHTML = opts;
    });
    const tr = $("#req-track");
    if (tr) {
      tr.innerHTML =
        `<option value="">All</option>` +
        (D.tracks || [])
          .map((t) => `<option value="${escapeHtml(t.id)}">${escapeHtml(t.label)}</option>`)
          .join("");
    }
  }

  function renderNicheGrid() {
    const root = $("#niche-grid");
    if (!root) return;
    root.innerHTML = (D.industries || [])
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
      ["#req-industry", "#gen-industry"].forEach((sel) => {
        const el = $(sel);
        if (el) el.value = state.industry;
      });
      setMode("generate");
    };
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
      <div class="how-card">
        <div class="step-num">${escapeHtml(s.n)}</div>
        <h3>${escapeHtml(s.title)}</h3>
        <p>${escapeHtml(s.text)}</p>
      </div>`
      )
      .join("");
  }

  // ── Generate business ──────────────────────────────────────────
  function bindGenerate() {
    const form = $("#gen-form");
    if (!form) return;
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const business = ($("#gen-business")?.value || "").trim();
      const industry = $("#gen-industry")?.value || "automation-builders";
      const err = $("#gen-error");
      if (err) err.textContent = "";
      if (business.length < 20) {
        if (err) err.textContent = "≥ 20 characters";
        return;
      }
      const btn = $("#gen-submit");
      if (btn) {
        btn.disabled = true;
        btn.textContent = t("loading");
      }
      try {
        const res = await fetch(`${apiBase()}/api/v1/analytics/business-generate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            business,
            industry,
            lang: I18N ? I18N.lang : "ru",
            choices: state.genChoices,
          }),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        state.lastGenerate = data;
        try {
          localStorage.setItem("metrix_last_generate", JSON.stringify(data));
        } catch (_) {}
        paintGenerate(data);
        // show choice cards from plan for next iteration
        paintChoices((data.output && data.output.plan) || {});
      } catch (ex) {
        if (err) err.textContent = `${t("error")}: ${ex.message}`;
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.textContent = t("run");
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
            const checked = (state.genChoices[s.id] || s.default_option) === o.id ? "checked" : "";
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
      gEl.textContent = gate.go_prod ? t("success_go") + " · " + (gate.verdict || "") : t("success_cond") + " · " + (gate.verdict || "");
      gEl.classList.toggle("warn", !gate.go_prod);
    }
    const plan = out.plan || {};
    $("#gen-plan").innerHTML = (plan.steps || [])
      .map(
        (s) =>
          `<div class="mp-card"><strong>${escapeHtml(s.id)}</strong> ${escapeHtml(s.title)} → <em>${escapeHtml(s.default_option || "—")}</em></div>`
      )
      .join("");
    $("#gen-questions").innerHTML = (plan.open_questions || out.interaction?.open_questions || [])
      .map((q) => `<li>${escapeHtml(q)}</li>`)
      .join("") || "<li>—</li>";

    const panel = out.control_panel || {};
    $("#gen-panel").innerHTML = (panel.columns || [])
      .map((col) => {
        const cards = (col.cards || [])
          .slice(0, 3)
          .map((c) => {
            let v = c.v;
            if (typeof v === "object") v = JSON.stringify(v).slice(0, 100);
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

  // ── Workers ────────────────────────────────────────────────────
  function bindWorkers() {
    $("#btn-create-sample-task")?.addEventListener("click", async () => {
      try {
        const res = await fetch(`${apiBase()}/api/v1/analytics/workers/tasks`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title: "Собрать демо-пакет для ниши + proof checklist",
            niche: state.industry !== "all" ? state.industry : "general",
            worker_id: "worker_demo",
            purse_units: 100,
          }),
        });
        const data = await res.json();
        state.workerTask = data;
        paintTaskDetail(data);
        refreshWorkerDash();
      } catch (ex) {
        alert(ex.message);
      }
    });
  }

  async function refreshWorkerDash() {
    const host = $("#worker-tasks");
    if (!host) return;
    try {
      const res = await fetch(`${apiBase()}/api/v1/analytics/workers/dashboard?worker_id=worker_demo`);
      if (!res.ok) throw new Error("dashboard");
      const data = await res.json();
      const rep = data.reputation || {};
      const rEl = $("#worker-rep");
      if (rEl) rEl.textContent = `rep · ${rep.score ?? 0.5} · done ${rep.completed ?? 0}`;
      const tasks = data.open_tasks || [];
      if (!tasks.length) {
        host.innerHTML = `<p class="muted-sm">No open tasks — create one.</p>`;
        return;
      }
      host.innerHTML = tasks
        .map(
          (t) => `
        <button type="button" class="task-card" data-task="${escapeHtml(t.task_id)}">
          <strong>${escapeHtml(t.title)}</strong>
          <span>${escapeHtml(t.niche)} · ${escapeHtml(t.status)} · net ${escapeHtml(t.net_units)}</span>
        </button>`
        )
        .join("");
      host.onclick = async (e) => {
        const card = e.target.closest("[data-task]");
        if (!card) return;
        // show local detail if we have it
        if (state.workerTask?.task?.task_id === card.dataset.task) {
          paintTaskDetail(state.workerTask);
        } else {
          paintTaskDetail({
            task: { task_id: card.dataset.task, title: card.querySelector("strong")?.textContent, milestones: [] },
            worker_net_units: "—",
          });
        }
      };
    } catch (_) {
      host.innerHTML = `<p class="muted-sm">API offline — start backend for live tasks.</p>`;
    }
  }

  function paintTaskDetail(data) {
    const el = $("#worker-task-detail");
    if (!el) return;
    el.hidden = false;
    const task = data.task || {};
    const miles = (task.milestones || [])
      .map(
        (m) =>
          `<li><strong>${escapeHtml(m.id)}</strong> ${escapeHtml(m.title)} · ${escapeHtml(m.proof_type)} · ${escapeHtml(m.status)} · share ${escapeHtml(m.amount_share)}</li>`
      )
      .join("");
    el.innerHTML = `
      <div><strong>${escapeHtml(task.title || "Task")}</strong></div>
      <div>id: ${escapeHtml(task.task_id)} · net units: ${escapeHtml(data.worker_net_units)}</div>
      <ul class="clean-list">${miles || "<li>milestones on create</li>"}</ul>
      <button type="button" class="btn btn-primary" id="btn-proof-m1">Submit proof m1</button>
      <button type="button" class="btn btn-ghost" id="btn-release-m1">Release m1</button>
    `;
    $("#btn-proof-m1")?.addEventListener("click", async () => {
      await fetch(`${apiBase()}/api/v1/analytics/workers/proof`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          task_id: task.task_id,
          milestone_id: "m1",
          proof: { items: [true, true, true] },
        }),
      });
      alert("Proof submitted");
    });
    $("#btn-release-m1")?.addEventListener("click", async () => {
      const r = await fetch(`${apiBase()}/api/v1/analytics/workers/release`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task_id: task.task_id, milestone_id: "m1" }),
      });
      const j = await r.json();
      alert("Released: " + JSON.stringify(j.paid_units || j));
      refreshWorkerDash();
    });
  }

  // ── Business Tasks ─────────────────────────────────────────────
  async function loadServices() {
    const grid = $("#svc-grid");
    if (!grid) return;
    const lang = I18N ? I18N.lang : "ru";
    try {
      const res = await fetch(`${apiBase()}/api/v1/analytics/business-services?lang=${lang}`);
      if (!res.ok) throw new Error("services");
      const data = await res.json();
      paintServices(data.services || []);
    } catch (_) {
      // offline fallback from static list
      paintServices(fallbackServices(lang));
    }
  }

  function fallbackServices(lang) {
    return [
      { id: "ops_reframe", name: lang === "en" ? "Ops Contour" : "Операционный контур", tagline: "One metric", price_note: t("fair_price"), wow: "leak-map" },
      { id: "offer_pack", name: lang === "en" ? "Offer Packaging" : "Упаковка оффера", tagline: "Promise · pack", price_note: t("fair_price"), wow: "offer" },
      { id: "tech_tz", name: "Tech-TZ", tagline: "Scope", price_note: t("fair_price"), wow: "tz" },
      { id: "ai_agent_desk", name: "AI Agent", tagline: "Doc → agent", price_note: t("fair_price"), wow: "agent" },
      { id: "distribution_engine", name: "3D Distribution", tagline: "Brand·Platforms·Net", price_note: t("fair_price"), wow: "7d" },
      { id: "worker_lane", name: "Worker Lane", tagline: "Task·proof·pay", price_note: t("fair_price"), wow: "escrow" },
      { id: "resource_loop", name: lang === "en" ? "Resource + Logistics" : "Ресурс + логистика", tagline: "Flow", price_note: t("fair_price"), wow: "flow" },
      { id: "expert_base_gen", name: lang === "en" ? "Expert Base" : "Экспертная база", tagline: "Layers", price_note: t("fair_price"), wow: "kb" },
      { id: "control_panel", name: "Control Panel", tagline: "Sense·Decide·Act", price_note: t("fair_price"), wow: "panel" },
      { id: "full_business_gen", name: "Generate 🔥", tagline: "Full system", price_note: t("fair_price"), wow: "full" },
    ];
  }

  function paintServices(list) {
    const grid = $("#svc-grid");
    if (!grid) return;
    grid.innerHTML = list
      .map(
        (s) => `
      <button type="button" class="svc-card" data-svc="${escapeHtml(s.id)}">
        <h3>${escapeHtml(s.name)}</h3>
        <p>${escapeHtml(s.tagline || "")}</p>
        <div class="price-note">${escapeHtml(s.price_note || t("fair_price"))}</div>
      </button>`
      )
      .join("");
    grid.onclick = async (e) => {
      const card = e.target.closest("[data-svc]");
      if (!card) return;
      const id = card.dataset.svc;
      if (id === "full_business_gen") {
        setMode("generate");
        return;
      }
      if (id === "worker_lane") {
        setMode("workers");
        return;
      }
      await showServiceDemo(id);
    };
  }

  async function showServiceDemo(id) {
    const box = $("#svc-demo");
    if (!box) return;
    const lang = I18N ? I18N.lang : "ru";
    let demo = null;
    let svc = null;
    try {
      const res = await fetch(`${apiBase()}/api/v1/analytics/business-services/${id}/demo?lang=${lang}`);
      if (res.ok) {
        const data = await res.json();
        demo = data.demo;
        svc = data.service;
      }
    } catch (_) {}
    if (!demo) {
      demo = { title: id, lines: ["Demo offline"], cta: t("continue") };
    }
    box.hidden = false;
    $("#svc-demo-title").textContent = demo.title || id;
    $("#svc-demo-lines").innerHTML = (demo.lines || []).map((l) => `<li>${escapeHtml(l)}</li>`).join("");
    $("#svc-demo-price").textContent =
      (svc && (lang === "ru" ? svc.price_note_ru : svc.price_note_en)) || t("fair_price");
    $("#svc-demo-close").onclick = () => {
      box.hidden = true;
    };
    $("#svc-demo-continue").onclick = () => {
      box.hidden = true;
      if (id === "control_panel") {
        location.href = "panel/index.html";
        return;
      }
      setMode("generate");
      const ta = $("#gen-business");
      if (ta && !ta.value) {
        ta.value =
          lang === "ru"
            ? `Хочу услугу «${svc?.name_ru || id}»: опишите контур под мой бизнес и соберите артефакты.`
            : `I want service «${svc?.name_en || id}»: build the contour and artifacts for my business.`;
      }
    };
    box.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function bindTasks() {
    /* grid bound in paintServices */
  }

  // ── Classic consult (kept) ─────────────────────────────────────
  function bindForm() {
    const form = $("#request-form");
    if (!form) return;
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
        if (err) err.textContent = "Industry + business (≥20 chars)";
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
      $("#consult-result").hidden = true;
      $("#free-work-panel").hidden = true;
    });
  }

  function paintConsult(data) {
    const box = $("#consult-result");
    if (!box) return;
    box.hidden = false;
    const idea = data.product?.demo_idea || data.demo_idea || {};
    $("#cr-headline").textContent = idea.title || data.orientation?.operating_mode || "Consult result";
    $("#cr-meta").textContent = `${data.industry || ""} · ${data.request_id || ""}`;
    $("#cr-blurb").textContent = idea.summary || data.summary || data.message || "";
    $("#cr-niche-answer").textContent = "";
    const links = $("#cr-links");
    if (links) links.innerHTML = "";
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
            business: business || "Free work after consult for operational contour and next steps.",
            industry,
            track: $("#req-track")?.value || "all",
            lang: I18N ? I18N.lang : "ru",
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
      ? phases.map((p) => `<span class="tag">${escapeHtml(typeof p === "string" ? p : p.name || p.id)}</span>`).join(" ")
      : "";
    const cl = data.checklist || [];
    $("#fw-checklist").innerHTML = (Array.isArray(cl) ? cl : [])
      .map((c) => `<li>${escapeHtml(typeof c === "string" ? c : c.text || JSON.stringify(c))}</li>`)
      .join("");
    $("#fw-success-metric").textContent = data.success_metric || "";
    $("#fw-tech-md").textContent = data.tech_write || data.tech_md || JSON.stringify(data, null, 2).slice(0, 2000);
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
  }

  // Update howItWorks for workers surface
  if (D.howItWorks) {
    D.howItWorks.lead =
      "Вход: суть бизнеса. Процесс: согласования + синтез. Выход: код, экспертная база, панель. Воркер: задача → proof → payout.";
    D.howItWorks.steps = [
      { n: "01", title: "Суть", text: "Описываете бизнес своими словами — система распознаёт домен." },
      { n: "02", title: "Согласования", text: "Короткие выборы направлений (как по ТЗ), не простыня вопросов." },
      { n: "03", title: "Сборка", text: "Экспертная база, код-пакет, панель Sense·Decide·Act." },
      { n: "04", title: "Воркер / клиент", text: "Escrow-задача или внедрение после подтверждённой ценности." },
    ];
  }

  init();
})();
