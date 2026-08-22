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

  const state = {
    view: (location.hash || "").replace("#", "") || "home",
    catalog: null,
    last: null,
  };
  if (
    [
      "home",
      "request",
      "flagships",
      "promo",
      "terminal",
      "fn-creative",
      "fn-logger",
      "fn-mockup",
      "scheme",
    ].indexOf(state.view) < 0
  ) {
    state.view = "home";
  }

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

  function price(p) {
    if (!p) return "";
    if (p.rub === 0) return "бесплатно";
    var s = "";
    if (p.rub != null) s += p.rub + " ₽";
    if (p.stars) s += (s ? " · " : "") + p.stars + " ★";
    return s;
  }

  function fmtReadings(list) {
    if (!list || !list.length) return "";
    return list
      .map(function (e) {
        return (
          '<article class="card card-flag reading"><span class="tag">' +
          esc(e.label || e.id) +
          "</span><h3>" +
          esc(e.reading) +
          "</h3><p class='muted'>" +
          esc(e.deliverable) +
          " · " +
          Math.round((e.confidence || 0) * 100) +
          "%</p></article>"
        );
      })
      .join("");
  }

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  var PAYMENTS = false; // старт без оплаты; Tribute/ЮKassa позже

  function buyRow(sku, title) {
    if (!PAYMENTS) {
      return '<p class="sku-buy">Бесплатно на старте</p>';
    }
    return (
      '<div class="row sku-buy">' +
      '<button type="button" class="btn btn-primary" data-buy="' +
      esc(sku) +
      '" data-pay="yookassa">Карта РФ</button>' +
      '<button type="button" class="btn" data-buy="' +
      esc(sku) +
      '" data-pay="stars">Stars</button>' +
      "</div>"
    );
  }

  async function buy(sku, pay) {
    const out = await post("/api/v1/miniapp/invoice", { sku: sku, pay_in: pay });
    if (out.invoice_url && tg && tg.openInvoice) {
      tg.openInvoice(out.invoice_url, function () {});
      return;
    }
    alert(
      (out.hint || out.error || "Счёт не выставлен") +
        "\nSKU " +
        sku +
        (out.price ? " · " + JSON.stringify(out.price) : "")
    );
  }

  viewEl.addEventListener("click", function (ev) {
    var t = ev.target;
    if (!t || !t.closest) return;
    var buyBtn = t.closest("[data-buy]");
    if (buyBtn) {
      buy(buyBtn.getAttribute("data-buy"), buyBtn.getAttribute("data-pay") || "yookassa");
      return;
    }
    var goEl = t.closest("[data-go]");
    if (goEl) go(goEl.getAttribute("data-go"));
  });

  var HIT_NAMES = {
    request_work: "Работа по запросу",
    creative_assistant: "Творческий ассистент",
    promo_cards: "Промо · карточки",
    solution_logger: "Solution logger",
    digital_mockup: "Цифровой макет",
    flagship_metric: "Metric engine",
    terminal_mine: "Терминал ордеров",
    promo_reels: "Промо · ролики",
    promo_prompts: "Промо · промпты",
  };

  function home(c) {
    var accents = ["#5eead4", "#38bdf8", "#c4b5fd"];
    var fns = (c.functions || [])
      .map(function (f, i) {
        var view =
          f.id === "creative_assistant"
            ? "fn-creative"
            : f.id === "solution_logger"
            ? "fn-logger"
            : "fn-mockup";
        return (
          '<article class="card card-flag" style="--flag-accent:' +
          accents[i % 3] +
          '" data-go="' +
          view +
          '"><span class="tag">функция</span><h3>' +
          esc(f.title) +
          "</h3><p>" +
          esc(f.blurb) +
          "</p><p class='price'>хиты " +
          (f.hits || 0) +
          "</p></article>"
        );
      })
      .join("");
    var hits = (c.hits || [])
      .map(function (h) {
        return (
          '<div class="card hit"><b>' +
          esc(HIT_NAMES[h.id] || h.id) +
          "</b><span class='price'>" +
          h.hits +
          "</span></div>"
        );
      })
      .join("");
    return (
      '<section class="hero">' +
      '<div class="hero-badge">Instant ideas · без оплаты</div>' +
      "<h1>Одно окно для <em>workflows</em> и оригинальных проектов.</h1>" +
      "<p class='lead'>Читалка задания держит несколько концов считывания и сама выбирает режим. Идеи сразу. Внедрение — когда утвердите.</p>" +
      '<div class="hero-actions">' +
      '<button class="btn btn-primary" data-go="request">Работа по запросу</button>' +
      '<button class="btn btn-ghost" data-go="flagships">Флагманские карточки</button>' +
      "</div></section>" +
      '<div class="eyebrow section-label">Функции</div><div class="grid">' +
      fns +
      "</div>" +
      '<div class="eyebrow section-label">Хиты</div>' +
      '<div class="grid">' +
      hits +
      "</div>"
    );
  }

  function requestView() {
    return (
      '<div class="eyebrow">Работа по запросу</div>' +
      "<h1>Сложный запрос → <em>несколько считываний</em></h1>" +
      "<p class='lead'>Не один «правильный» ответ. Читалка держит варианты и умолчания, режим выбирается сборкой.</p>" +
      '<label>Бриф (своими словами)</label>' +
      '<textarea id="q-brief" placeholder="Опишите задачу, бизнес, что скрыто или неясно…"></textarea>' +
      '<div class="row"><button class="btn btn-primary" id="q-run">Собрать запрос</button></div>' +
      '<div id="q-out"></div>'
    );
  }

  function flagships(c) {
    var cards = (c.flagships || [])
      .map(function (f) {
        return (
          '<article class="card card-flag" style="--flag-accent:' +
          esc(f.accent || "#5eead4") +
          '"><span class="tag">' +
          esc(f.sticker) +
          "</span><h3>" +
          esc(f.title) +
          "</h3><p>" +
          esc(f.essence_ru) +
          "</p><p class='price'>" +
          price(f.price) +
          "</p>" +
          buyRow(f.sku, f.title) +
          "</article>"
        );
      })
      .join("");
    return (
      '<div class="eyebrow">Флагманы</div><h1>Карточки <em>как на сайте</em></h1>' +
      '<p class="lead">Именные слои Metrix — не свалка каталога.</p>' +
      '<div class="grid grid-cards">' +
      cards +
      "</div>"
    );
  }

  function promoView() {
    return (
      '<div class="eyebrow">Промо</div>' +
      "<h1>Массовый бизнес-билдер</h1>" +
      "<p class='muted'>Облегчённая версия: карточки описаний, идеи роликов, промпты для консалтинга.</p>" +
      '<textarea id="p-brief" placeholder="Оффер / продукт / ниша…"></textarea>' +
      '<div class="row">' +
      '<button class="btn btn-primary" data-pk="cards">Карточки</button>' +
      '<button class="btn" data-pk="reels">Ролики</button>' +
      '<button class="btn" data-pk="prompts">Промпты</button>' +
      "</div><div id='p-out'></div>" +
      buyRow("promo_pack", "Промо-пак")
    );
  }

  function terminalView() {
    return (
      '<div class="eyebrow">Терминал</div>' +
      "<h1>Путь к ордерам / майнинг</h1>" +
      "<p class='muted'>Не брокер. Неформальные цепочки решений → ожидающие ордера Metrix. Ликвидность = внимание + оплачиваемый SKU.</p>" +
      '<textarea id="t-brief" placeholder="Тезис, след, журнал, что должно стать ордером…"></textarea>' +
      '<button class="btn btn-primary" id="t-run">Майнить ордера</button>' +
      '<div id="t-out"></div>'
    );
  }

  function fnCreative() {
    return (
      '<div class="eyebrow">Функция</div><h1>Творческий ассистент</h1>' +
      '<textarea id="c-brief" placeholder="Задача / ограничение / материал…"></textarea>' +
      '<button class="btn btn-primary" id="c-run">Собрать идеи</button><div id="c-out"></div>' +
      buyRow("fn_creative", "Creative")
    );
  }

  function fnLogger() {
    return (
      '<div class="eyebrow">Функция</div><h1>Solution logger</h1>' +
      "<p class='muted'>Полезный анализ своего трейдинга. Не сигналы.</p>" +
      '<label>Тезис входа</label><textarea id="l-thesis" placeholder="Почему вход, где инвалидация, горизонт…"></textarea>' +
      '<div class="row"><input id="l-market" placeholder="рынок" /><input id="l-side" placeholder="long/short" /><input id="l-result" placeholder="win/loss" /></div>' +
      '<button class="btn btn-primary" id="l-run">Разобрать</button><div id="l-out"></div>' +
      buyRow("fn_logger", "Logger")
    );
  }

  function fnMockup() {
    return (
      '<div class="eyebrow">Функция</div><h1>Цифровой макет</h1>' +
      "<p class='muted'>Подобие индивидуала: темп, оффер, слоты — быстрый разворот соло-работы.</p>" +
      '<textarea id="m-port" placeholder="Кто вы, как работаете, что продаёте…"></textarea>' +
      '<input id="m-offer" placeholder="оффер (необязательно)" />' +
      '<button class="btn btn-primary" id="m-run">Собрать макет</button><div id="m-out"></div>' +
      buyRow("fn_mockup", "Mockup")
    );
  }

  function schemeView(s) {
    if (!s) return "<p>Загрузка схемы…</p>";
    var u = s.unit_90d_conservative || {};
    var rails = (s.rails && s.rails.rf_cards) || {};
    return (
      '<div class="eyebrow">Монетизация</div><h1>Карточки · запрос · earning</h1>' +
      '<article class="card"><h3>90 дней, нижняя планка</h3>' +
      "<p>MAU " +
      u.mau +
      " · платящих " +
      u.payers +
      "</p>" +
      "<p class='price'>GMV " +
      u.gmv_rub +
      " ₽ · net ЮKassa " +
      u.net_yookassa_rub +
      " ₽</p>" +
      "<p class='muted'>" +
      esc(u.note) +
      "</p></article>" +
      '<article class="card"><h3>Карты РФ → Telegram</h3><p>' +
      esc(rails.how) +
      "</p><p class='muted'>" +
      esc(rails.not) +
      "</p></article>" +
      '<article class="card"><h3>Market making (формально)</h3><p>' +
      esc((s.market_making || {}).formal) +
      "</p></article>"
    );
  }

  async function render() {
    if (!state.catalog) {
      viewEl.innerHTML = "<p class='muted'>Загрузка каталога…</p>";
      try {
        state.catalog = await get("/api/v1/miniapp/catalog?lang=ru");
      } catch (e) {
        viewEl.innerHTML = "<p>Нет связи с API. Запустите backend на :8787.</p>";
        return;
      }
    }
    var c = state.catalog;
    var html = "";
    if (state.view === "home") html = home(c);
    else if (state.view === "request") html = requestView();
    else if (state.view === "flagships") html = flagships(c);
    else if (state.view === "promo") html = promoView();
    else if (state.view === "terminal") html = terminalView();
    else if (state.view === "fn-creative") html = fnCreative();
    else if (state.view === "fn-logger") html = fnLogger();
    else if (state.view === "fn-mockup") html = fnMockup();
    else if (state.view === "scheme") html = schemeView(c.scheme);
    else html = home(c);
    viewEl.innerHTML = html;
    bind();
  }

  function bind() {
    var run = document.getElementById("q-run");
    if (run) {
      run.onclick = async function () {
        var brief = document.getElementById("q-brief").value;
        document.getElementById("q-out").innerHTML = "<p class='status'>Сборка…</p>";
        var out = await post("/api/v1/miniapp/request", { brief: brief, lang: "ru" });
        var mode = (out.mode || {}).surface_mode || "—";
        var readings = fmtReadings(out.end_readings);
        var idea =
          (((out.process || {}).demo_idea) || {}).title ||
          (out.assembly && out.assembly.summary) ||
          "";
        document.getElementById("q-out").innerHTML =
          '<article class="card card-flag"><span class="tag">режим ' +
          esc(mode) +
          "</span><h3>Сборка</h3><p class='muted'>" +
          esc((out.assembly || {}).summary || "") +
          "</p></article>" +
          readings +
          (idea ? "<p class='muted'>Демо: " + esc(idea) + "</p>" : "") +
          buyRow("request_deep", "Deep request");
      };
    }
    document.querySelectorAll("[data-pk]").forEach(function (b) {
      b.onclick = async function () {
        var kind = b.getAttribute("data-pk");
        var brief = (document.getElementById("p-brief") || {}).value || "оффер";
        var out = await post("/api/v1/miniapp/promo", { brief: brief, kind: kind, lang: "ru" });
        document.getElementById("p-out").innerHTML =
          '<pre class="pre">' + esc(JSON.stringify(out.items || out, null, 2)) + "</pre>";
      };
    });
    var tr = document.getElementById("t-run");
    if (tr) {
      tr.onclick = async function () {
        var brief = document.getElementById("t-brief").value;
        var out = await post("/api/v1/miniapp/terminal", { brief: brief, lang: "ru" });
        var tickets = (out.tickets || [])
          .map(function (t) {
            return "<li><b>" + esc(t.status) + "</b> — " + esc(t.title) + ". " + esc(t.why) + "</li>";
          })
          .join("");
        var chain = (out.chain || [])
          .map(function (s) {
            return "<li>" + esc(s.move) + "</li>";
          })
          .join("");
        document.getElementById("t-out").innerHTML =
          '<article class="card"><h3>Цепочка (не формальная)</h3><ol class="tickets">' +
          chain +
          "</ol></article>" +
          '<article class="card"><h3>Ордера</h3><ul class="tickets">' +
          tickets +
          "</ul><p class='muted'>" +
          esc((out.viability || {}).verdict || "") +
          "</p></article>" +
          buyRow("terminal_mine", "Mine");
      };
    }
    var cr = document.getElementById("c-run");
    if (cr) {
      cr.onclick = async function () {
        var out = await post("/api/v1/miniapp/creative", {
          brief: document.getElementById("c-brief").value,
          lang: "ru",
        });
        document.getElementById("c-out").innerHTML =
          '<pre class="pre">' +
          esc((out.ideas || []).map(function (i) { return i.line; }).join("\n")) +
          "\n\n" +
          esc((out.prompts || []).join("\n")) +
          "</pre>";
      };
    }
    var lr = document.getElementById("l-run");
    if (lr) {
      lr.onclick = async function () {
        var out = await post("/api/v1/miniapp/logger", {
          thesis: document.getElementById("l-thesis").value,
          market: document.getElementById("l-market").value,
          side: document.getElementById("l-side").value,
          result: document.getElementById("l-result").value,
          lang: "ru",
        });
        document.getElementById("l-out").innerHTML =
          '<article class="card"><h3>Полезность ' +
          ((out.stats || {}).usefulness || 0) +
          "</h3><p>" +
          esc((out.error_families || []).join(", ")) +
          "</p><p class='muted'>" +
          esc(((out.path_to_orders || {}).note) || "") +
          "</p></article>";
      };
    }
    var mr = document.getElementById("m-run");
    if (mr) {
      mr.onclick = async function () {
        var out = await post("/api/v1/miniapp/mockup", {
          portrait: document.getElementById("m-port").value,
          offer: document.getElementById("m-offer").value,
          lang: "ru",
        });
        var L = out.likeness || {};
        document.getElementById("m-out").innerHTML =
          '<article class="card"><h3>' +
          esc(L.working_name) +
          "</h3><p>темп " +
          esc(L.tempo) +
          " · канал " +
          esc(L.channel) +
          " · оффер " +
          esc(L.offer_shape) +
          "</p><ol>" +
          (out.unfold_24h || []).map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") +
          "</ol></article>";
      };
    }
  }

  render();
})();
