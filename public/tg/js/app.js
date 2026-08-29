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

  const VIEWS = ["landing", "engine", "making", "home", "demo", "strategies", "agents", "posts"];
  const ALIAS = { home: "landing", demo: "landing", strategies: "engine", agents: "engine", posts: "making" };
  const state = {
    view: (location.hash || "").replace("#", "") || "landing",
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
  });

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
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

  function landingView() {
    return (
      '<section class="room">' +
      '<div class="room-head"><span class="room-pulse" aria-hidden="true"></span>' +
      '<div class="eyebrow">Видение события</div></div>' +
      "<h1>Не кнопка. <em>Комната.</em></h1>" +
      "<p class='lead'>Работа и отдых здесь не противоположности. " +
      "Стремиться к состоянию — значит стремиться к смерти. " +
      "Событие уже идёт — ты входишь в него, или нет.</p>" +
      '<label>Что сейчас движется</label>' +
      '<textarea id="q-brief" placeholder="SaaS 80 человек, фичи пилим, никто не знает, что считается победой…"></textarea>' +
      '<div class="row"><button type="button" class="btn btn-primary" id="q-run">Войти</button></div>' +
      '<div id="q-out"></div></section>'
    );
  }

  function engineView(c) {
    var log = state.comfort
      .map(function (m) {
        return '<div class="bubble ' + (m.role === "you" ? "you" : "quiet") + '">' + esc(m.text) + "</div>";
      })
      .join("");
    var cards = (c.strategies || [])
      .map(function (s) {
        var img = s.image
          ? '<img class="card-photo" src="' + esc(s.image) + '" alt="' + esc(s.name) + '" />'
          : "";
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
    var niches = (c.niches || [])
      .map(function (n) {
        return (
          '<article class="card card-flag" style="--flag-accent:' +
          esc(n.accent) +
          '" data-ag="' +
          esc(n.id) +
          '"><span class="tag">' +
          esc(n.size) +
          "</span><h3>" +
          esc(n.title) +
          "</h3><p>" +
          esc(n.pain) +
          "</p></article>"
        );
      })
      .join("");
    return (
      '<section class="comfort">' +
      '<div class="eyebrow">Верхний модуль движка</div>' +
      " <h1>Тихий <em>ассистент</em></h1>" +
      "<p class='lead'>Идеи и точки роста. Без подъёма пульса. Можно сесть.</p>" +
      '<div class="comfort-log" id="c-log">' +
      (log || '<div class="bubble quiet">Тихо. Напишите, что уже движется — или что бесит.</div>') +
      "</div>" +
      '<textarea id="c-brief" placeholder="слишком много людей, слишком много фич, касса как туман…"></textarea>' +
      '<div class="row"><button type="button" class="btn btn-primary" id="c-run">Сказать</button></div>' +
      '<div id="c-out"></div></section>' +
      '<div class="eyebrow section-label">Модели внутри движка</div><div class="grid grid-cards">' +
      cards +
      "</div>" +
      '<div class="eyebrow section-label">Агенты</div><div class="grid">' +
      niches +
      "</div>" +
      '<div id="st-out"></div><div id="ag-out"></div>'
    );
  }

  function makingView() {
    var ready = state.closer && state.closer.cards;
    return (
      '<section class="chamber">' +
      '<div class="chamber-hero">' +
      '<div class="eyebrow">Камера сборки</div>' +
      "<h1>Мейкинг. <em>Неделя,</em> не план.</h1>" +
      "<p class='lead'>Ткёт абстракцию, карточки, промпт и наскриненный тренд в семь дней, которые можно прожить. " +
      "День 1 — вход в событие. Никогда «исследование».</p></div>" +
      (ready
        ? "<p class='muted'>Карточки уже на столе. Можно собрать неделю.</p>"
        : "<p class='muted'>Если ещё не входили — камера соберёт событие из фразы. Лучше сначала лендинг.</p>") +
      '<label>Уточнение к сборке (необязательно)</label>' +
      '<textarea id="m-brief" placeholder="соберите неделю под мой контур… / боюсь менять кассу…"></textarea>' +
      '<div class="row"><button type="button" class="btn btn-primary" id="m-run">Собрать неделю</button>' +
      '<button type="button" class="btn btn-ghost" data-go="landing">В комнату</button></div>' +
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
    if (state.view === "engine") html = engineView(c);
    else if (state.view === "making") html = makingView();
    else html = landingView();
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
    var extra = (document.getElementById("c-brief") || {}).value || id;
    var box = document.getElementById("st-out") || document.getElementById("c-out");
    if (!box) return;
    box.innerHTML = "<p class='status'>Собираю карту…</p>";
    var out = await post("/api/v1/miniapp/strategy", { brief: extra, strategy: id });
    box.innerHTML = artHtml(out.artifact);
    bindResonate(box);
  }

  async function runAgent(id) {
    var extra = (document.getElementById("c-brief") || {}).value || "";
    if (extra.length < 8) extra = "Собрать агента для ниши " + id;
    var box = document.getElementById("ag-out") || document.getElementById("c-out");
    if (!box) return;
    box.innerHTML = "<p class='status'>Собираю спеку…</p>";
    var out = await post("/api/v1/miniapp/agent", { brief: extra, niche: id });
    box.innerHTML = artHtml(out.artifact);
    bindResonate(box);
  }

  function bind() {
    bindResonate(viewEl);
  }

  render();
})();
