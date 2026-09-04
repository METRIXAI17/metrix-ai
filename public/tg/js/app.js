(function () {
  const tg = window.Telegram && window.Telegram.WebApp;
  if (tg) {
    tg.ready();
    tg.expand();
    try { tg.setHeaderColor("#070a0f"); } catch (e) {}
    try { tg.setBackgroundColor("#070a0f"); } catch (e2) {}
  }

  function apiBase() {
    const h = location.hostname;
    if (h === "localhost" || h === "127.0.0.1") return "http://127.0.0.1:8787";
    if (h.indexOf("vercel.app") !== -1) return "https://metrix-ai-production.up.railway.app";
    return "";
  }
  const API = apiBase();

  function headers() {
    const h = { "Content-Type": "application/json" };
    const init = tg && tg.initData;
    if (init) h["X-Telegram-Init-Data"] = init;
    return h;
  }

  async function get(path) {
    const r = await fetch(API + path, { headers: headers() });
    return r.json();
  }
  async function post(path, body) {
    const r = await fetch(API + path, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify(body || {}),
    });
    return r.json();
  }

  const VIEWS = ["chain", "teammates", "artefacts", "landing", "engine", "making", "home", "demo", "strategies", "agents", "posts"];
  const ALIAS = {
    home: "chain",
    demo: "chain",
    landing: "chain",
    strategies: "chain",
    engine: "teammates",
    agents: "teammates",
    posts: "artefacts",
    making: "artefacts",
  };
  const state = {
    view: (location.hash || "").replace("#", "") || "chain",
    catalog: null,
    last: null,
    closer: null,
    niche: "",
    strategy: "",
    comfort: [],
  };
  if (ALIAS[state.view]) state.view = ALIAS[state.view];
  if (VIEWS.indexOf(state.view) < 0) state.view = "landing";

  const viewEl = document.getElementById("view");

  function go(name) {
    name = ALIAS[name] || name;
    state.view = name;
    try {
      history.replaceState(null, "", "#" + name);
    } catch (e) {}
    document.querySelectorAll(".tabbar button").forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-go") === name);
    });
    render();
    window.scrollTo(0, 0);
  }
  window.addEventListener("hashchange", function () {
    var h = ALIAS[(location.hash || "").replace("#", "")] || (location.hash || "").replace("#", "") || "landing";
    if (h !== state.view) go(h);
  });

  document.addEventListener("click", function (ev) {
    var t = ev.target;
    if (!t || !t.closest) return;
    var goEl = t.closest("[data-go]");
    if (goEl) {
      ev.preventDefault();
      var name = goEl.getAttribute("data-go");
      if (name) go(name);
      return;
    }
    var st = t.closest("[data-st]");
    if (st) {
      ev.preventDefault();
      runStrategy(st.getAttribute("data-st"));
      return;
    }
    var ag = t.closest("[data-ag]");
    if (ag) {
      ev.preventDefault();
      runAgent(ag.getAttribute("data-ag"));
      return;
    }
    if (t.closest("#q-run")) {
      ev.preventDefault();
      runLanding();
    }
    if (t.closest("#c-run")) {
      ev.preventDefault();
      runComfort();
    }
    if (t.closest("#m-run")) {
      ev.preventDefault();
      runMaking();
    }
    if (t.closest("#p-run") || t.closest("#th-run")) {
      ev.preventDefault();
      runThesis();
    }
    if (t.closest("#o-run")) {
      ev.preventDefault();
      runThesis();
    }
    if (t.closest("[data-ss]")) {
      ev.preventDefault();
      runStop();
    }
    if (t.closest("[data-rk]")) {
      ev.preventDefault();
      runRisk();
    }
    if (t.closest("#wf-run")) {
      ev.preventDefault();
      runWorkflow();
    }
  });

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  var GEO = {
    chain: "/tg/assets/geo-chain.jpg",
    target_place: "/tg/assets/geo-gold.jpg",
    demand: "/tg/assets/geo-demand.jpg",
    ampli: "/tg/assets/geo-ampli.jpg",
    two_leg_tape: "/tg/assets/geo-tape.jpg",
    risk: "/tg/assets/geo-risk.jpg",
    saas: "/tg/assets/geo-saas.jpg",
    agency: "/tg/assets/geo-agency.jpg",
    edu: "/tg/assets/geo-edu.jpg",
    ecom: "/tg/assets/geo-ecom.jpg",
    artefacts: "/tg/assets/geo-artefacts.jpg",
  };

  function photoSrc(id, remote) {
    return GEO[id] || remote || "";
  }

  function photoHtml(src, alt, cls) {
    if (!src) return "";
    return (
      '<img class="' +
      (cls || "card-photo") +
      '" src="' +
      esc(src) +
      '" alt="' +
      esc(alt || "") +
      '" />'
    );
  }

  function cardsHtml(cards) {
    var items = (cards && cards.items) || [];
    if (!items.length) return "";
    return (
      '<div class="eyebrow section-label">Функциональные обозначения</div><div class="card-table">' +
      items
        .map(function (c) {
          return (
            '<article class="fn-card"><code>' +
            esc(c.code) +
            '</code><span class="des">' +
            esc(c.designation) +
            "</span><h4>" +
            esc(c.poetic_name) +
            "</h4><p>" +
            esc(c.action) +
            '</p><div class="fn-meta"><span><b>fn</b> ' +
            esc(c.function) +
            "</span><span><b>obj</b> " +
            esc(c.object) +
            "</span><span><b>unit</b> " +
            esc(c.unit) +
            "</span><span><b>kill</b> " +
            esc(c.kill) +
            "</span></div></article>"
          );
        })
        .join("") +
      "</div>"
    );
  }

  function eventHtml(ev) {
    if (!ev) return "";
    return (
      '<article class="event-vision">' +
      '<span class="tag">событие</span>' +
      "<h2>" +
      esc(ev.title) +
      "</h2>" +
      '<p class="atm">' +
      esc(ev.atmosphere) +
      "</p>" +
      "<p>" +
      esc(ev.who_enters) +
      "</p>" +
      "<h3>Что движется</h3><p>" +
      esc(ev.what_moves) +
      "</p>" +
      "<h3>Что стоит</h3><p>" +
      esc(ev.what_stays) +
      "</p>" +
      '<p class="lead">' +
      esc(ev.invitation) +
      "</p></article>"
    );
  }

  function essayHtml(abs) {
    if (!abs || !abs.essay) return "";
    return (
      '<div class="eyebrow">Абстракция</div><h2>' +
      esc(abs.lead || abs.archetype) +
      '</h2><div class="essay">' +
      esc(abs.essay) +
      "</div>"
    );
  }

  function thesesHtml(rows) {
    if (!rows || !rows.length) return "";
    return (
      '<ol class="theses">' +
      rows
        .map(function (row) {
          var dead = row.status === "dead";
          return (
            '<li class="thesis ' +
            (dead ? "dead" : "alive") +
            '"><b>' +
            (dead ? "мёртв" : "жив") +
            "</b> · " +
            esc(row.relation || "") +
            "<p>" +
            esc(row.text) +
            "</p></li>"
          );
        })
        .join("") +
      "</ol>"
    );
  }

  function artHtml(a) {
    if (!a) return "";
    var steps = (a.steps || [])
      .map(function (s) {
        return "<li>" + esc(s) + "</li>";
      })
      .join("");
    var anti = (a.anti || [])
      .map(function (s) {
        return "<li>" + esc(s) + "</li>";
      })
      .join("");
    var m = a.meta || {};
    var meta = "";
    if (m.entry) meta += '<p><span class="k">Вход</span> ' + esc(m.entry) + "</p>";
    if (m.exit) meta += '<p><span class="k">Выход</span> ' + esc(m.exit) + "</p>";
    if (m.invalidation) meta += '<p><span class="k">Смерть тезиса</span> ' + esc(m.invalidation) + "</p>";
    if (m.window) meta += '<p><span class="k">Окно</span> ' + esc(m.window) + "</p>";
    if (m.why_builder) meta += "<p>" + esc(m.why_builder) + "</p>";
    var cal = (m.calendar_7d || []).map(function (d) {
      return (
        '<div class="day"><div class="n">' +
        esc(d.day) +
        "</div><div><b>" +
        esc(d.title) +
        "</b><p>" +
        esc(d.do) +
        "</p></div></div>"
      );
    }).join("");
    var fin = m.fin_structure_shift || {};
    var fear = fin.fear_protocol || {};
    var fee = fin.success_fee || {};
    var extra = "";
    if (cal) extra += '<h3>Неделя</h3>' + cal;
    if (fear.say) {
      extra +=
        '<div class="fear"><h3>Протокол страха</h3><p>' +
        esc(fear.say) +
        "</p><p>" +
        esc(fear.inversion) +
        "</p></div>";
    }
    if (fee.on) {
      extra +=
        '<div class="fee"><h3>Share</h3><p>' +
        esc(fee.on) +
        "</p><p class='muted'>" +
        esc(fee.kill) +
        "</p></div>";
    }
    return (
      '<article class="artifact" data-aid="' +
      esc(a.id || "") +
      '">' +
      '<span class="tag">' +
      esc((a.lane || "demo") + (a.strategy_id ? " · " + a.strategy_id : a.niche_id ? " · " + a.niche_id : "")) +
      "</span>" +
      "<h2>" +
      esc(a.title) +
      "</h2>" +
      '<p class="lead">' +
      esc(a.one_liner) +
      "</p>" +
      thesesHtml(a.theses) +
      "<h3>Где ломается</h3><p>" +
      esc(a.break) +
      "</p>" +
      "<h3>Нестандартный ход</h3><p>" +
      esc(a.move) +
      "</p>" +
      "<h3>Как садится</h3><ol class='tickets'>" +
      steps +
      "</ol>" +
      "<h3>Артефакт на неделю</h3><p>" +
      esc(a.artifact_week) +
      "</p>" +
      meta +
      extra +
      (anti ? "<h3>Не делать</h3><ul class='tickets'>" + anti + "</ul>" : "") +
      '<p class="muted disc">' +
      esc(a.disclaimer || "") +
      "</p>" +
      '<div class="resonate">' +
      '<button class="btn btn-primary" data-rs="hit">Зашло</button>' +
      '<button class="btn" data-rs="almost">Почти</button>' +
      '<button class="btn" data-rs="miss">Мимо</button>' +
      "</div>" +
      '<div class="rs-out"></div>' +
      "</article>"
    );
  }

  function wallHtml(out) {
    if (!out || !out.wall) return "";
    var url = (state.catalog && state.catalog.tribute) || out.tribute || "https://t.me/tribute";
    var human = (state.catalog && state.catalog.human) || out.human || "https://x.com/karimmetrix";
    return (
      '<article class="wall">' +
      "<h3>" +
      (out.reason === "month_cap" ? "Лимит месяца (40 результатов)" : "Два бесплатных результата использованы") +
      "</h3>" +
      "<p>Бот — ленд-артефакт. Access — 3 290 ₽ / месяц, 40 результатов. " +
      "Metrix AI в боте уже работает (тезисы, конфиги, in-out). $2490 — посадка того же движка в физ. ecom.</p>" +
      '<div class="row"><a class="btn btn-primary" href="' +
      esc(url) +
      '" target="_blank" rel="noopener">Оплатить в Tribute</a>' +
      '<a class="btn btn-ghost" href="' +
      esc(human) +
      '" target="_blank" rel="noopener">Связаться с человеком</a></div></article>'
    );
  }

  function landingView() {
    return chainView(state.catalog || {});
  }

  function chainView(c) {
    var cards = (c.strategies || [])
      .map(function (s) {
        var img = photoHtml(photoSrc(s.id, s.image), s.name);
        return (
          '<article class="card card-flag" style="--flag-accent:' +
          esc(s.accent) +
          '" data-st="' +
          esc(s.id) +
          '">' +
          img +
          '<span class="tag">' +
          esc(s.market) +
          "</span><h3>" +
          esc(s.name) +
          "</h3><p>" +
          esc(s.one_liner) +
          "</p></article>"
        );
      })
      .join("");
    var acc = (c.access || {}).remaining;
    var accNote =
      acc == null
        ? "Access открыт"
        : "Бесплатно осталось " + acc + " результат(а)";
    return (
      '<section class="room">' +
      '<div class="geo-hero">' +
      photoHtml(GEO.chain, "In-Out Chain", "geo-hero-img") +
      "</div>" +
      '<div class="room-head"><span class="room-pulse" aria-hidden="true"></span>' +
      '<div class="eyebrow">Флагман</div></div>' +
      "<h1>In-Out <em>Chain</em></h1>" +
      "<p class='lead'>In-out эксперимент гоняет основной движок. " +
      "Снимает рутину, закрывает решённое и нерешённое, режет стоимость in и out.</p>" +
      '<p class="muted">' +
      esc(accNote) +
      "</p>" +
      '<label>Что стоит дорого на in или на out</label>' +
      '<textarea id="q-brief" placeholder="SaaS 80 человек, фичи пилим, никто не знает, что считается победой…"></textarea>' +
      '<div class="row"><button type="button" class="btn btn-primary" id="q-run">Собрать цепочку</button></div>' +
      '<div id="q-out"></div>' +
      '<div class="eyebrow section-label">Четыре модели · код, не сигналы</div>' +
      '<div class="grid grid-cards">' +
      cards +
      "</div>" +
      '<article class="card card-flag" style="--flag-accent:#fb7185" data-ss="now">' +
      photoHtml(GEO.risk, "Стоп на перемене") +
      '<span class="tag">не списывает</span><h3>Стоп на перемене</h3>' +
      "<p>Факт против тезиса стратегии. Бюджет не сливать. Если тезис мёртв — идеи под новый режим, не новый вход.</p></article>" +
      '<article class="card card-flag" style="--flag-accent:#fb7185" data-rk="engine">' +
      '<span class="tag">отдельно</span><h3>Risk Engine</h3>' +
      "<p>R — мера исхода. Плечо — размер. Движок их не путает.</p></article>" +
      '<div id="st-out"></div></section>'
    );
  }

  function engineView(c) {
    return teammatesView(c);
  }

  function teammatesView(c) {
    var teammates = (c.teammates || c.niches || [])
      .map(function (n) {
        return (
          '<article class="card card-flag" style="--flag-accent:' +
          esc(n.accent) +
          '" data-ag="' +
          esc(n.id) +
          '">' +
          photoHtml(photoSrc(n.id, n.image), n.codename || n.title) +
          '<span class="tag">' +
          esc(n.codename || n.size || "") +
          "</span><h3>" +
          esc(n.title) +
          "</h3><p>" +
          esc(n.user_facing || n.pain || "") +
          "</p></article>"
        );
      })
      .join("");
    var steps = ((c.workflow || {}).steps || [])
      .map(function (s, i) {
        return "<li><b>" + (i + 1) + ". " + esc(s.title) + "</b> — " + esc(s.do) + "</li>";
      })
      .join("");
    var human = (c.human || "https://x.com/karimmetrix");
    var custom = c.tribute_custom || human;
    return (
      '<section class="comfort">' +
      '<div class="geo-hero">' +
      photoHtml(GEO.saas, "AI Teammates", "geo-hero-img") +
      "</div>" +
      '<div class="eyebrow">AI Teammates</div>' +
      "<h1>Два тимейта. <em>Конфиг</em> на заказ.</h1>" +
      "<p class='lead'>Движок собирает конфиг: IT-внедрение и продакшн. Файл подрядчику. Edu и ecom — не этот контур.</p>" +
      '<div class="grid">' +
      teammates +
      "</div>" +
      '<div class="eyebrow section-label">Воркфлоу конфига</div>' +
      "<ol class='tickets'>" +
      steps +
      "</ol>" +
      '<label>Контур для конфига</label>' +
      '<textarea id="c-brief" placeholder="агентство, онбординг сжигает маржу, метод в головах…"></textarea>' +
      '<div class="row"><button type="button" class="btn btn-primary" id="wf-run">Собрать конфиг</button>' +
      '<a class="btn" href="' +
      esc(human) +
      '" target="_blank" rel="noopener">Связаться с человеком</a>' +
      '<a class="btn btn-ghost" href="' +
      esc(custom) +
      '" target="_blank" rel="noopener">Custom · $500</a></div>' +
      '<div id="c-out"></div><div id="ag-out"></div></section>'
    );
  }

  function makingView() {
    return artefactsView();
  }

  function artefactsView() {
    return (
      '<section class="chamber">' +
      '<div class="chamber-hero">' +
      photoHtml(GEO.artefacts, "Artefacts", "chamber-photo") +
      '<div class="eyebrow">Artefacts</div>' +
      "<h1>Тезисы <em>на заказ</em>.</h1>" +
      "<p class='lead'>Продаём только тезисы. Их собирает основной движок. " +
      "Короткое утверждение про процесс, которое можно убить фактом.</p></div>" +
      '<label>Контур своими словами</label>' +
      '<textarea id="m-brief" placeholder="касса как туман, поставщик снял отсрочку, онбординг жрёт маржу…"></textarea>' +
      '<div class="row">' +
      '<button type="button" class="btn btn-primary" id="th-run">Заказать тезисы</button>' +
      "</div>" +
      '<div id="m-out"></div></section>'
    );
  }

  async function render() {
    if (!state.catalog) {
      viewEl.innerHTML = "<p class='muted'>Загрузка…</p>";
      try {
        state.catalog = await get("/api/v1/miniapp/catalog?lang=ru");
      } catch (e) {
        viewEl.innerHTML = "<p>Нет связи с API. Локально поднимите backend на :8787.</p>";
        return;
      }
    }
    var c = state.catalog;
    var html = "";
    if (state.view === "teammates" || state.view === "engine") html = teammatesView(c);
    else if (state.view === "artefacts" || state.view === "making") html = artefactsView();
    else html = chainView(c);
    viewEl.innerHTML = html;
    bind();
  }

  function bindResonate(root) {
    if (!root) return;
    root.querySelectorAll("[data-rs]").forEach(function (b) {
      b.onclick = async function () {
        var artEl = root.querySelector(".artifact");
        var aid = artEl && artEl.getAttribute("data-aid");
        var outEl = root.querySelector(".rs-out");
        if (!aid) return;
        var out = await post("/api/v1/miniapp/resonate", {
          artifact_id: aid,
          verdict: b.getAttribute("data-rs"),
        });
        var p = out.paid_path || {};
        var msg =
          out.verdict === "hit"
            ? "Зашло. Это и есть товар. Пилот сажает именно этот артефакт в ваш контур на share."
            : out.verdict === "almost"
            ? "Почти. Допишите, чего не хватает — соберу вторую версию."
            : "Мимо. Нормально. Возьмите другую дверь — или посидите.";
        if (outEl) {
          outEl.innerHTML =
            '<article class="card"><h3>' +
            esc(p.title || "") +
            "</h3><p>" +
            esc(msg) +
            "</p><p class='muted'>" +
            esc(p.why || "") +
            "</p></article>";
        }
      };
    });
  }

  function paintCloser(box, pack, art) {
    var abs = (pack && pack.abstraction) || (art && art.abstraction) || {};
    var ev = (pack && pack.event) || (art && art.event) || {};
    var cards = (pack && pack.cards) || (art && art.cards) || {};
    var prompt = (pack && pack.prompt) || {};
    var audit = (pack && pack.audit) || {};
    box.innerHTML =
      eventHtml(ev) +
      essayHtml(abs) +
      cardsHtml(cards) +
      (prompt.engine_brief
        ? '<div class="eyebrow section-label">Промпт для основного движка</div><pre class="pre">' +
          esc(prompt.engine_brief) +
          "</pre>"
        : "") +
      (audit.ratio
        ? '<p class="muted">Аудит гипотез: ' + audit.held + "/" + audit.total + "</p>"
        : "") +
      artHtml(art);
    bindResonate(box);
  }

  async function runLanding() {
    var briefEl = document.getElementById("q-brief");
    var box = document.getElementById("q-out");
    if (!box) return;
    var brief = briefEl ? briefEl.value : "";
    box.innerHTML = "<p class='status'>Собираю комнату…</p>";
    try {
      var out = await post("/api/v1/miniapp/landing", { brief: brief, lang: "ru" });
      if (out.wall) {
        box.innerHTML = wallHtml(out);
        return;
      }
      if (!out.ok) {
        box.innerHTML = "<p class='muted'>" + esc(out.detail || out.error || "Не собралось") + "</p>";
        return;
      }
      state.last = out.artifact;
      state.closer = out.closer;
      paintCloser(box, out.closer, out.artifact);
    } catch (e) {
      box.innerHTML = "<p>Сеть. Попробуйте ещё раз.</p>";
    }
  }

  async function runComfort() {
    var briefEl = document.getElementById("c-brief");
    var box = document.getElementById("c-out");
    var log = document.getElementById("c-log");
    if (!briefEl) return;
    var msg = briefEl.value || "";
    if (msg.length < 2) return;
    state.comfort.push({ role: "you", text: msg });
    if (log) {
      log.innerHTML += '<div class="bubble you">' + esc(msg) + "</div>";
    }
    if (box) box.innerHTML = "<p class='status'>Сидим…</p>";
    try {
      var out = await post("/api/v1/miniapp/comfort", {
        message: msg,
        brief: (state.closer && state.closer.brief) || msg,
        history: state.comfort.slice(-8),
        lang: "ru",
      });
      state.comfort.push({ role: "quiet", text: out.reply || "" });
      if (log) log.innerHTML += '<div class="bubble quiet">' + esc(out.reply || "") + "</div>";
      var objs = (out.objects || [])
        .map(function (o) {
          return (
            '<div class="obj"><span class="k">' +
            esc(o.title) +
            "</span><p>" +
            esc(o.text) +
            "</p></div>"
          );
        })
        .join("");
      if (box) box.innerHTML = '<div class="objects">' + objs + "</div>";
      briefEl.value = "";
    } catch (e) {
      if (box) box.innerHTML = "<p>Сеть.</p>";
    }
  }

  async function runMaking() {
    var extraEl = document.getElementById("m-brief");
    var box = document.getElementById("m-out");
    if (!box) return;
    box.innerHTML = "<p class='status'>Камера ткёт неделю…</p>";
    var extra = extraEl ? extraEl.value : "";
    var brief =
      extra ||
      (state.closer && state.closer.brief) ||
      "собери неделю из того, что уже движется в комнате";
    try {
      var out = await post("/api/v1/miniapp/making", {
        brief: brief,
        extra: extra,
        lang: "ru",
        closer: state.closer,
      });
      if (!out.ok) {
        box.innerHTML =
          "<p class='muted'>" +
          esc(out.error || out.detail || "Камера пуста. Сначала войдите на лендинге.") +
          "</p>";
        return;
      }
      state.last = out.artifact || out.making;
      box.innerHTML = artHtml(out.artifact || out.making);
      bindResonate(box);
    } catch (e) {
      box.innerHTML = "<p>Сеть.</p>";
    }
  }

  async function runStrategy(id) {
    var extra = (document.getElementById("q-brief") || document.getElementById("c-brief") || {}).value || id;
    var box = document.getElementById("st-out") || document.getElementById("m-out") || document.getElementById("c-out");
    if (!box) return;
    box.innerHTML = "<p class='status'>Собираю код модели…</p>";
    var out = await post("/api/v1/miniapp/strategy", { brief: extra, strategy: id });
    if (out.wall) {
      box.innerHTML = wallHtml(out);
      return;
    }
    box.innerHTML = artHtml(out.artifact);
    bindResonate(box);
  }

  async function runAgent(id) {
    var extra = (document.getElementById("c-brief") || {}).value || "";
    if (extra.length < 8) extra = "Собрать тимейта для ниши " + id;
    var box = document.getElementById("ag-out") || document.getElementById("c-out");
    if (!box) return;
    box.innerHTML = "<p class='status'>Собираю спеку…</p>";
    var out = await post("/api/v1/miniapp/teammate", { brief: extra, niche: id });
    if (out.wall) {
      box.innerHTML = wallHtml(out);
      return;
    }
    box.innerHTML = artHtml(out.artifact);
    bindResonate(box);
  }

  async function runRisk() {
    var extra = (document.getElementById("q-brief") || {}).value || "риск без путаницы R и плеча";
    var box = document.getElementById("st-out") || document.getElementById("q-out");
    if (!box) return;
    box.innerHTML = "<p class='status'>Риск-движок…</p>";
    var out = await post("/api/v1/miniapp/risk", { brief: extra });
    if (out.wall) {
      box.innerHTML = wallHtml(out);
      return;
    }
    box.innerHTML = artHtml(out.artifact);
    bindResonate(box);
  }

  async function runThesis() {
    var extra = (document.getElementById("m-brief") || {}).value || "контур без описания";
    var box = document.getElementById("m-out");
    if (!box) return;
    box.innerHTML = "<p class='status'>Собираю тезисы…</p>";
    var out = await post("/api/v1/miniapp/thesis", { brief: extra });
    if (out.wall) {
      box.innerHTML = wallHtml(out);
      return;
    }
    box.innerHTML = artHtml(out.artifact);
    bindResonate(box);
  }

  async function runStop() {
    var extra = (document.getElementById("q-brief") || {}).value || "рынок как есть";
    var box = document.getElementById("st-out") || document.getElementById("q-out");
    if (!box) return;
    box.innerHTML = "<p class='status'>Проверяю противоречие…</p>";
    var out = await post("/api/v1/miniapp/stop-on-shift", { brief: extra, watch: true });
    if (out.wall) {
      box.innerHTML = wallHtml(out);
      return;
    }
    box.innerHTML = artHtml(out.artifact);
    bindResonate(box);
  }

  async function runWorkflow() {
    var extra = (document.getElementById("c-brief") || {}).value || "";
    if (extra.length < 8) extra = "собрать нового тимейта под живой контур";
    var box = document.getElementById("c-out");
    if (!box) return;
    box.innerHTML = "<p class='status'>Воркфлоу…</p>";
    var out = await post("/api/v1/miniapp/teammate", { brief: extra });
    if (out.wall) {
      box.innerHTML = wallHtml(out);
      return;
    }
    box.innerHTML = artHtml(out.artifact);
    bindResonate(box);
  }

  function bind() {
    bindResonate(viewEl);
  }

  render();
})();
