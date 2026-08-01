/**
 * Metrix AI — public surface
 * Workspace: problem → decision → sellable document (or agent-ready pack)
 */
window.METRIX_DATA = {
  brand: {
    name: "Metrix AI",
    tagline: "Проблема → решение → документ",
    focus: "Система поддержки решений на пути к доходу",
    x: "https://x.com/karimmetrix",
  },

  masterOffer: {
    headline: "Metrix AI",
    sub:
      "Единое рабочее пространство для онлайн-бизнеса: сформулируйте проблему, определите решение, отправьте документ, который рынок может купить, или который может выполнить конечный агент. Экспертные идеи бесплатно. Оплата за внедрение с живым общением после подтверждения.",
    sub2: "Не кот в мешке. Никаких подписок, никакого роялти.",
    pillars: [],
    disclaimers: [],
  },

  /**
   * Конкретные ниши клиентов (короткие карточки, без длинных описаний).
   * cloud → api-for-devs: API-интеграции под клиентские продукты.
   */
  industries: [
    {
      id: "ai-agencies",
      name: "AI-агентства и студии",
      short: "AI-студии",
      blurb: "Сдача проектов без хаоса",
      icon: "◇",
      accent: "#5eead4",
    },
    {
      id: "api-for-devs",
      name: "API для разработчиков",
      short: "API / dev",
      blurb: "Интеграции и клиентские штуки",
      icon: "⚡",
      accent: "#7dd3fc",
    },
    {
      id: "freelace-d2c",
      name: "Фриланс и D2C-офферы",
      short: "Фриланс",
      blurb: "Идея → документ → заказ",
      icon: "↗",
      accent: "#67e8f9",
      badge: "Автоликвидность",
    },
    {
      id: "expert-services",
      name: "Экспертные услуги",
      short: "Эксперты",
      blurb: "Упаковка оффера и ТЗ",
      icon: "✦",
      accent: "#c4b5fd",
    },
    {
      id: "ecommerce",
      name: "Онлайн-магазины",
      short: "E-com",
      blurb: "Оффер, воронка, unit-экон.",
      icon: "▣",
      accent: "#fbbf24",
    },
    {
      id: "content-monetize",
      name: "Контент и аудитория",
      short: "Контент",
      blurb: "Монетизация без размытия",
      icon: "◈",
      accent: "#86efac",
    },
    {
      id: "education",
      name: "Курсы и обучение",
      short: "Обучение",
      blurb: "Программа → продаваемый пакет",
      icon: "◫",
      accent: "#fda4af",
    },
    {
      id: "saas-founders",
      name: "SaaS и цифровые продукты",
      short: "SaaS",
      blurb: "Пилот, метрика, оффер",
      icon: "⬡",
      accent: "#a5b4fc",
    },
    {
      id: "automation-builders",
      name: "Автоматизация и no-code",
      short: "Авто",
      blurb: "Сценарии под доход",
      icon: "◎",
      accent: "#f9a8d4",
    },
    {
      id: "cost-ops",
      name: "Себестоимость и unit-economics",
      short: "Unit-экон.",
      blurb: "Где утекают деньги",
      icon: "▤",
      accent: "#fcd34d",
    },
    {
      id: "device-assembly",
      name: "Сборка и конфиг устройств",
      short: "Устройства",
      blurb: "Руками + онлайн-оффер",
      icon: "⬢",
      accent: "#fb7185",
    },
    {
      id: "asset-decisions",
      name: "Решения по активам",
      short: "Активы",
      blurb: "Метрика и риски, без обещаний",
      icon: "◎",
      accent: "#f0abfc",
      badge: "Автоликвидность",
    },
  ],

  /** Полный список ниш (для отчёта и select) — то же, что industries */
  clientNicheList: [
    "AI-агентства и студии",
    "API-интеграции для разработчиков клиентских продуктов",
    "Фриланс и D2C-офферы (документ под заказ)",
    "Экспертные услуги (коучинг, консалтинг, упаковка)",
    "Онлайн-магазины и товарный D2C",
    "Контент-креаторы и монетизация аудитории",
    "Онлайн-курсы и образовательные продукты",
    "SaaS и цифровые продукты на ранней стадии",
    "Автоматизация, no-code, агентные сценарии под доход",
    "Себестоимость, unit-economics, cost-ops",
    "Сборка, конфиг, периферия + онлайн-продажа",
    "Решения по активам и капиталу (decision support)",
    "Маркетинговые и performance-команды",
    "B2B-услуги и агентства (не только AI)",
    "Локальный сервис с онлайн-записью и оффером",
  ],

  tracks: [
    { id: "product", name: "Product", label: "Продукт", color: "#5eead4", salesGuide: true },
    { id: "models", name: "Teammate", label: "Teammate", color: "#fbbf24", salesGuide: true },
    { id: "promotion", name: "Promotion", label: "Продвижение", color: "#c4b5fd", salesGuide: false },
  ],

  whyUsSlides: [
    {
      key: "ops",
      title: "Операции",
      text: "Одна табло-метрика и карта утечек — те же люди, больше маржи.",
    },
    {
      key: "product",
      title: "Продукт",
      text: "Решение = документ и метрики, которые можно продать или отдать агенту.",
    },
    {
      key: "promotion",
      title: "Продвижение",
      text: "Угол продажи из фактов пилота, не из пустого контента.",
    },
    {
      key: "income",
      title: "Доход",
      text: "Поддержка решений, которая укорачивает путь от идеи к оплачиваемому шагу.",
    },
  ],

  /**
   * Проблемы + конкретный ответ (все карточки сразу, без слайдера).
   * Без «лучшее решение», без Metrix AI Shift.
   */
  problemSlides: [
    {
      problem: "Идея есть, продавать нечего",
      solution: "Пакет: 1-страничный оффер + ТЗ + чеклист приёмки — можно выложить или отдать исполнителю.",
      niche: "Фриланс / D2C",
    },
    {
      problem: "Три направления сразу, ничего не закрыто",
      solution: "Выбираем один трек (продукт, ops или промо), 14-дневный пилот с одной метрикой успеха.",
      niche: "Онлайн-бизнес",
    },
    {
      problem: "API и токены жрут бюджет",
      solution: "Карта вызовов API: что оставить, что урезать, что заменить — с полом качества.",
      niche: "API / dev",
    },
    {
      problem: "Капитал есть, модели нет",
      solution: "Карточка ключевой метрики, рамка рисков и список «чего не делать». Сделки — у вас.",
      niche: "Активы",
    },
    {
      problem: "Клиенты просят «ещё агентов», маржа падает",
      solution: "Три рычага: приёмка, переделки, handoff. Табло на 14 дней без переписывания стека.",
      niche: "AI-студии",
    },
    {
      problem: "Непонятно, за что платить",
      solution: "Бесплатно: диагноз и экспертные идеи. Платно: внедрение после вашего «да», с живым созвоном.",
      niche: "Все",
    },
    {
      problem: "Курс / экспертка не продаётся",
      solution: "Упаковка: обещание результата, 3 модуля, цена, возражения — один продаваемый пакет.",
      niche: "Обучение / эксперты",
    },
    {
      problem: "Хочу руками + онлайн",
      solution: "Одна станция или SKU конфига → оффер в сеть. Онлайн-продажа на базе осязаемого результата.",
      niche: "Устройства",
    },
  ],

  howItWorks: {
    title: "Как это работает",
    lead:
      "Сформулировали проблему → получили решение в виде документа и метрик → рынок купил или конечный агент выполнил. Идеи бесплатно, внедрение — после подтверждения.",
    steps: [
      {
        n: "01",
        title: "Проблема",
        text: "Коротко: кто вы, где деньги, где болит. Ниша из списка.",
      },
      {
        n: "02",
        title: "Решение",
        text: "Диагноз, направление, tech-TZ: объём, приёмка, что не делаем.",
      },
      {
        n: "03",
        title: "Документ",
        text: "Пакет, который можно продать, отдать подрядчику или агенту.",
      },
      {
        n: "04",
        title: "Внедрение",
        text: "После вашего подтверждения — живое общение и платная реализация. Без подписок и роялти.",
      },
    ],
  },

  flagships: [
    {
      id: "decision-support",
      title: "Поддержка решений → доход",
      essence:
        "Система, которая упрощает путь: проблема → ясное решение → документ, метрики и следующий оплачиваемый шаг.",
      detail:
        "Осязаемый продукт Metrix AI: не «ещё чат», а рабочее место, где каждый ответ сводится к решению и артефакту (оффер, ТЗ, метрика, чеклист). Экспертные идеи бесплатно. Внедрение — после подтверждения, с живым общением. Без подписок и роялти.",
      track: "product",
      accent: "#5eead4",
      sticker: "Ядро",
      cta: "request",
    },
    {
      id: "consult",
      title: "Бесплатная консультация",
      essence: "Краткий бриф → диагноз, направление, следующие шаги.",
      detail:
        "5–20 предложений о бизнесе. Пакет ориентации: что ломается, какой механизм, куда идти. Идеи бесплатно.",
      track: "ops",
      accent: "#5eead4",
      sticker: "Free",
      cta: "request",
    },
    {
      id: "tech-journalism",
      title: "Tech-TZ бесплатно",
      essence: "Читаемое ТЗ: scope, пакеты работ, приёмка.",
      detail: "После ориентации — техническое письмо, с которым можно идти к исполнителю или агенту.",
      track: "product",
      accent: "#38bdf8",
      sticker: "Free",
      cta: "techwrite",
    },
    {
      id: "pilot",
      title: "Пилот",
      essence: "Один трек, одна метрика, 14–30 дней — потом решение о полном пакете.",
      detail: "Цены в блоке Pricing. Не подписка: фиксированная работа после подтверждения.",
      track: "product",
      accent: "#fbbf24",
      sticker: "Pilot",
      cta: "pricing",
    },
    {
      id: "teammate",
      title: "Terminal Teammate",
      essence: "Доступ к базовому слою: библиотеки, закупки-промпты, живой спрос.",
      detail:
        "Не чатбот. Карта ниш → самогенерация того, что раньше покупали снаружи → продажи с рынка → свой стек. По шагам, после пилота.",
      track: "models",
      accent: "#c4b5fd",
      sticker: "Flagship",
      cta: "request",
    },
    {
      id: "asset-lane",
      title: "Решения по активам",
      essence: "Метрика, риски, сценарии. Управление сделками — у вас.",
      detail:
        "Поддержка решений, не обещание доходности. Работа по ТЗ после подтверждения. Без роялти с капитала.",
      track: "product",
      accent: "#f0abfc",
      sticker: "Автоликвидность",
      cta: "request",
      industryHint: "asset-decisions",
    },
    {
      id: "d2c-lane",
      title: "D2C и фриланс-пакет",
      essence: "Идея → документ под заказ → передача исполнителю или агенту.",
      detail:
        "Рынок платит за оформленное решение. Мы собираем документ, который совпадает с формой заказа.",
      track: "product",
      accent: "#67e8f9",
      sticker: "Автоликвидность",
      cta: "request",
      industryHint: "freelace-d2c",
    },
    {
      id: "api-lane",
      title: "API для разработчиков",
      essence: "Карта интеграций и клиентских API без лишнего burn.",
      detail:
        "Для тех, кто собирает штуки клиентам: что вызывать, где резать cost, какой пол качества.",
      track: "product",
      accent: "#7dd3fc",
      sticker: "Dev",
      cta: "request",
      industryHint: "api-for-devs",
    },
    {
      id: "metrix-ai",
      title: "Почему мы",
      essence: "Короткие факты: ops, продукт, промо, путь к доходу.",
      detail: "",
      track: "ops",
      accent: "#7dd3fc",
      sticker: "Why us",
      cta: "request",
      marquee: true,
    },
  ],

  packagePricing: {
    freeConsultUsd: 0,
    freeTechWriteUsd: 0,
    freeTechWriteNote: "Экспертные идеи и tech-TZ после консультации — бесплатно.",
    pilotOpsUsd: 690,
    pilotProductUsd: 790,
    pilotPromotionUsd: 490,
    mainPackageUsd: 2490,
    volumeNote:
      "Оплата за внедрение после подтверждения, с живым общением. Без подписок и роялти.",
    transactionNote: "",
  },

  fullPackage: {
    name: "Цены",
    why: "Идеи бесплатно. Внедрение — после вашего «да». Без подписок и роялти.",
  },

  api: {
    baseUrl: (function resolveApiBase() {
      if (typeof window !== "undefined" && window.METRIX_RUNTIME && window.METRIX_RUNTIME.apiBaseUrl != null) {
        return String(window.METRIX_RUNTIME.apiBaseUrl).replace(/\/$/, "");
      }
      var host = typeof location !== "undefined" ? location.hostname : "";
      if (host === "localhost" || host === "127.0.0.1") {
        return "http://127.0.0.1:8787";
      }
      var METRIX_API_BASE = "https://metrix-ai-production.up.railway.app";
      return String(METRIX_API_BASE || "").replace(/\/$/, "");
    })(),
    processPath: "/api/v1/process",
    freeWorkStartPath: "/api/v1/analytics/free-work/start",
    freeWorkClarifyPath: "/api/v1/analytics/free-work/clarify",
    freeWorkAdvancePath: "/api/v1/analytics/free-work/advance",
    enabled: true,
  },

  contact: {
    note: "",
    xDm: "https://x.com/messages/compose?recipient_id=2042689375742373888",
  },
};

window.METRIX_DATA.getPrograms = function (filters) {
  const data = window.METRIX_DATA;
  const out = [];
  const industries = filters?.industry
    ? data.industries.filter((i) => i.id === filters.industry)
    : data.industries;
  for (const ind of industries) {
    for (const f of data.flagships) {
      out.push({
        id: `${ind.id}__${f.id}`,
        industryId: ind.id,
        industryName: ind.name,
        trackId: f.track,
        trackName: f.track,
        slug: f.id,
        title: f.title,
        fullTitle: f.title,
        summary: f.essence,
        detail: f.detail,
        pillar: f.title,
        deliverables: [],
        status: "ready",
        popular: true,
        salesGuide: f.detail,
        industryNote: ind.blurb,
        hasSalesGuide: true,
        accent: ind.accent,
      });
    }
  }
  return out;
};

window.METRIX_DATA.getProgramById = function (id) {
  return window.METRIX_DATA.getPrograms().find((p) => p.id === id) || null;
};

window.METRIX_DATA.getPopularCount = function () {
  return window.METRIX_DATA.flagships.length;
};

window.METRIX_DATA.getFlagships = function () {
  return window.METRIX_DATA.flagships.slice();
};

window.METRIX_DATA.getIndustries = function () {
  return window.METRIX_DATA.industries.slice();
};

window.METRIX_DATA.getProblemSlides = function () {
  return (window.METRIX_DATA.problemSlides || []).slice();
};
