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

  const VIEWS = ["home", "demo", "strategies", "agents", "posts"];
  const state = {
    view: (location.hash || "").replace("#", "") || "home",
    catalog: null,
    last: null,
    niche: "",
    strategy: "",
  };
  if (VIEWS.indexOf(state.view) < 0) state.view = "home";

  const viewEl = document.getElementById("view");

  function go(name) {
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
    var h = (location.hash || "").replace("#", "") || "home";
    if (h !== state.view) go(h);
  });

  document.querySelectorAll(".tabbar button").forEach(function (b) {
    b.addEventListener("click", function () {
      go(b.getAttribute("data-go"));
    });
  });
  document.querySelectorAll(".logo[data-go]").forEach(function (b) {
    b.addEventListener("click", function (ev) {
      ev.preventDefault();
      go(b.getAttribute("data-go"));
    });
  });

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function artHtml(a) {
    if (!a) return "";
    var steps = (a.steps || [])
      .map(function (s, i) {
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

  function home(c) {
    var flags = (c.flagships || [])
      .map(function (f) {
        return (
          '<article class="card card-flag" style="--flag-accent:' +
          esc(f.accent || "#5eead4") +
          '" data-go="' +
          esc(f.cta || "demo") +
          '"><span class="tag">' +
          esc(f.sticker) +
          "</span><h3>" +
          esc(f.title) +
          "</h3><p>" +
          esc(f.essence_ru) +
          "</p></article>"
        );
      })
      .join("");
    return (
      '<section class="hero">' +
      '<div class="hero-badge">Карим · не сигналы</div>' +
      "<h1>Демо. Если артефакт <em>зашёл</em> — это товар.</h1>" +
      "<p class='lead'>Торговал. Собрал нишу: уникальные финансовые модели, которые садятся в чужой проект. " +
      "Посты на X иногда залетают. Фрилансю, когда есть окно. Когда нет — залипаю.</p>" +
      '<div class="hero-actions">' +
      '<button class="btn btn-primary" data-go="demo">Собрать демо</button>' +
      '<button class="btn btn-ghost" data-go="strategies">Стратегии</button>' +
      '<button class="btn btn-ghost" data-go="agents">Агенты</button>' +
      "</div></section>" +
      '<div class="eyebrow section-label">Двери</div><div class="grid grid-cards">' +
      flags +
      "</div>" +
      '<p class="muted foot-note">Билдер на столе для SaaS 50–500, агентств, школ и e-com с высоким чеком. ' +
      "Агент держит финмодель, не болтает.</p>"
    );
  }

  function demoView() {
    return (
      '<div class="eyebrow">Магистраль</div>' +
      "<h1>Ситуация → <em>артефакт</em></h1>" +
      "<p class='lead'>Своими словами. Можно криво. Один выход, не отчёт. Если зайдёт — пилот сажает именно это.</p>" +
      '<label>Что у вас за задача</label>' +
      '<textarea id="q-brief" placeholder="SaaS 80 человек, фичи пилим, никто не знает, что считается победой. Или: золото, вхожу когда уже ушло…"></textarea>' +
      '<div class="row"><button class="btn btn-primary" id="q-run">Собрать</button></div>' +
      '<div id="q-out"></div>'
    );
  }

  function strategiesView(c) {
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
          "</p><p class='muted'>" +
          esc(s.for_whom) +
          "</p></article>"
        );
      })
      .join("");
    return (
      '<div class="eyebrow">Три модели</div>' +
      "<h1>Места. Окно. <em>Амплитуда.</em></h1>" +
      "<p class='lead'>Не стрелочки на сегодня. Модели, которые можно посадить в свой журнал.</p>" +
      '<div class="grid grid-cards">' +
      cards +
      "</div>" +
      '<label>Если хотите — одна фраза про ваш стиль входа</label>' +
      '<textarea id="st-brief" placeholder="золото, ловлю догон… / местный листинг на этой неделе… / Америка, угадываю сторону…"></textarea>' +
      '<div id="st-out"></div>'
    );
  }

  function agentsView(c) {
    var cards = (c.niches || [])
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
      '<div class="eyebrow">Билдер агентов</div>' +
      "<h1>Агент с <em>финмоделью</em></h1>" +
      "<p class='lead'>Не чат, который отвечает на всё. Агент знает, что считать деньгами, когда молчать, какой артефакт отдать человеку.</p>" +
      '<div class="grid">' +
      cards +
      "</div>" +
      '<label>Кто вы и что бесит</label>' +
      '<textarea id="ag-brief" placeholder="агентство 12 человек, онбординг съедает маржу…"></textarea>' +
      '<div id="ag-out"></div>'
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
    if (state.view === "home") html = home(c);
    else if (state.view === "demo") html = demoView();
    else if (state.view === "strategies") html = strategiesView(c);
    else if (state.view === "agents") html = agentsView(c);
    else html = home(c);
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
            ? "Зашло. Это и есть товар. Пилот сажает именно этот артефакт в ваш контур."
            : out.verdict === "almost"
            ? "Почти. Допишите в поле выше, чего не хватает — соберу вторую версию."
            : "Мимо. Нормально. Возьмите другую дверь.";
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

  function bind() {
    var run = document.getElementById("q-run");
    if (run) {
      run.onclick = async function () {
        var brief = document.getElementById("q-brief").value;
        var box = document.getElementById("q-out");
        box.innerHTML = "<p class='status'>Собираю…</p>";
        try {
          var out = await post("/api/v1/miniapp/demo", { brief: brief, lang: "ru" });
          if (!out.ok) {
            box.innerHTML = "<p class='muted'>" + esc(out.detail || out.error || "Не собралось") + "</p>";
            return;
          }
          state.last = out.artifact;
          box.innerHTML = artHtml(out.artifact);
          bindResonate(box);
        } catch (e) {
          box.innerHTML = "<p>Сеть. Попробуйте ещё раз.</p>";
        }
      };
    }
    document.querySelectorAll("[data-st]").forEach(function (card) {
      card.onclick = async function () {
        var id = card.getAttribute("data-st");
        var extra = (document.getElementById("st-brief") || {}).value || id;
        var box = document.getElementById("st-out");
        box.innerHTML = "<p class='status'>Собираю карту…</p>";
        var out = await post("/api/v1/miniapp/strategy", { brief: extra, strategy: id });
        box.innerHTML = artHtml(out.artifact);
        bindResonate(box);
      };
    });
    document.querySelectorAll("[data-ag]").forEach(function (card) {
      card.onclick = async function () {
        var id = card.getAttribute("data-ag");
        var extra = (document.getElementById("ag-brief") || {}).value || "";
        if (extra.length < 8) extra = "Собрать агента для ниши " + id;
        var box = document.getElementById("ag-out");
        box.innerHTML = "<p class='status'>Собираю спеку…</p>";
        var out = await post("/api/v1/miniapp/agent", { brief: extra, niche: id });
        box.innerHTML = artHtml(out.artifact);
        bindResonate(box);
      };
    });
  }

  render();
})();
