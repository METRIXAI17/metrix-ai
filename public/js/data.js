/**
 * Global Ru Workers · Metrix AI — public surface
 * Modes: Workers · Business Tasks · Generate 🔥 · Consult
 * Parent layer: i18n RU/EN (see i18n.js)
 */
window.METRIX_DATA = {
  brand: {
    name: "Global Ru Workers",
    tagline: "Workers · Business Tasks · Generate",
    focus: "Metrix AI decision + assembly system",
    x: "https://x.com/karimmetrix",
  },

  masterOffer: {
    headline: "Global Ru Workers",
    sub: "",
    sub2:
      "Моментальные экспертные идеи — сразу. Оплата после вашего успешного получения оплаты. Экспериментировать можно не боясь. Прайс адекватный.",
    pillars: [],
    disclaimers: [],
  },

  /**
   * 10 ниш клиентов (без SaaS и e-com).
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
      name: "Интеграции и фичи",
      short: "Интеграции",
      blurb: "Настройка интеграций и фичи",
      icon: "⚡",
      accent: "#7dd3fc",
    },
    {
      id: "freelace-d2c",
      name: "Фриланс",
      short: "Фриланс",
      blurb: "Автоматизация поиска и выполнения",
      icon: "↗",
      accent: "#67e8f9",
    },
    {
      id: "expert-services",
      name: "Экспертные услуги",
      short: "Эксперты",
      blurb: "Упаковка ценности и стратегия",
      icon: "✦",
      accent: "#c4b5fd",
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
      name: "Обучение",
      short: "Обучение",
      blurb: "Упаковка идеи и оформление",
      icon: "◫",
      accent: "#fda4af",
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
      accent: "#e9d5ff",
    },
  ],

  /** Короткий список = 10 ниш (без длинного дубля) */
  clientNicheList: [],

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
      text: "Решение = документ консультации и следующие шаги, которые можно внедрить.",
    },
    {
      key: "promotion",
      title: "Продвижение",
      text: "Угол продажи из фактов пилота, не из пустого контента.",
    },
    {
      key: "income",
      title: "Доход",
      text: "Поддержка решений укорачивает путь от идеи к оплачиваемому шагу.",
    },
  ],

  /** Проблемы — только данные для промо (на сайт не выводим) */
  problemSlides: [],

  howItWorks: {
    title: "Путь",
    lead:
      "Один путь подходит и воркерам (кто собирает и продаёт решения внутри 10 ниш), и клиентам этих ниш, которые приходят на сайт за результатом.",
    steps: [
      {
        n: "01",
        title: "Проблема",
        text: "Воркер или клиент ниши описывает бизнес своими словами — где болит и чего хочет.",
      },
      {
        n: "02",
        title: "Решение",
        text: "Моментальные экспертные идеи: направление, что делать первым, что не трогать.",
      },
      {
        n: "03",
        title: "Документ консультации",
        text: "Осязаемый выход: можно внедрять, отдавать команде или использовать как ТЗ.",
      },
      {
        n: "04",
        title: "Оплата после оплаты",
        text: "Вы сначала получаете ценность и свой результат; оплата внедрения — после вашего успешного получения оплаты. Экспериментировать можно не боясь.",
      },
    ],
  },

  /**
   * Для кого путь (воркеры + клиенты 10 ниш) — блок на сайте после «Путь».
   */
  audienceSplit: {
    title: "Для воркеров и для клиентов ниш",
    lead:
      "Один интерфейс. Два входа: вы делаете работу в нише — или вы клиент этой ниши и хотите ясный следующий шаг.",
    workers: {
      title: "Воркеры",
      text:
        "Те, кто ведёт проекты, фриланс, студию, интеграции, контент, обучение, автоматизацию, unit-экон., устройства или решения по активам. Нужен воркфлоу: от сырой задачи к документу и выполнению — без хаоса и без «кот в мешке».",
    },
    clients: {
      title: "Клиенты 10 ниш",
      text:
        "Те, кто приходит как заказчик AI-студии, интеграций, фриланса, эксперта, контента, обучения, автоматизации, cost-ops, устройств или asset-решений. Получают документ консультации и понятный путь к результату — можно экспериментировать не боясь.",
    },
  },

  /**
   * Подробные флагманы (после «Не кот в мешке»).
   * Без отдельных «фриланс» и «активы» как флагманов.
   */
  flagshipDetails: [
    {
      id: "decision-support",
      title: "Система поддержки решений",
      text:
        "Ядро продукта. На входе — проблема и описание бизнеса своими словами. На выходе — документ консультации: направление, шаги, что не делать. Это не чат ради чата, а осязаемый артефакт для внедрения.",
    },
    {
      id: "consult",
      title: "Моментальная консультация",
      text:
        "Короткий бриф → моментальные экспертные идеи сразу. Без ожидания «менеджера» и без подписки. Можно пробовать смело: оплата за внедрение — после вашего успешного получения оплаты.",
    },
    {
      id: "tech-tz",
      title: "Tech-TZ / документ работ",
      text:
        "Когда идея ясна — оформляем объём, приёмку и границы. Документ, с которым можно идти к исполнителю, команде или дальше в пилот.",
    },
    {
      id: "pilot",
      title: "Пилот",
      text:
        "Один трек, одна метрика, ограниченное окно. Живое общение после подтверждения. Полный пакет — только если пилот показал путь.",
    },
    {
      id: "teammate",
      title: "Terminal Teammate",
      text:
        "Доступ к базовому слою: библиотеки, закупки-промпты, живой спрос, свой стек. Не «ещё бот», а инструмент для разворачивания воркфлоу и оригинальных проектов.",
    },
    {
      id: "integrations",
      title: "Интеграции и фичи",
      text:
        "Настройка интеграций и фич под реальные клиентские штуки: что подключить, что урезать, какой пол качества. Для разработчиков и тех, кто собирает продукты клиентам.",
    },
  ],

  flagships: [
    {
      id: "decision-support",
      title: "Поддержка решений",
      essence: "Проблема и бизнес своими словами → документ консультации.",
      detail:
        "Система поддержки решений: моментальные экспертные идеи, осязаемый документ, путь к доходу. Оплата после вашего успешного получения оплаты.",
      track: "product",
      accent: "#5eead4",
      sticker: "Ядро",
      cta: "request",
    },
    {
      id: "consult",
      title: "Моментальная консультация",
      essence: "Бриф → экспертные идеи сразу.",
      detail:
        "5–20 предложений. Моментальные экспертные идеи. Экспериментировать можно не боясь.",
      track: "ops",
      accent: "#5eead4",
      sticker: "Сразу",
      cta: "request",
    },
    {
      id: "tech-journalism",
      title: "Tech-TZ",
      essence: "Документ работ: scope, приёмка, границы.",
      detail: "После ориентации — техническое письмо для внедрения или handoff.",
      track: "product",
      accent: "#38bdf8",
      sticker: "Документ",
      cta: "techwrite",
    },
    {
      id: "pilot",
      title: "Пилот",
      essence: "Один трек, одна метрика, живое общение после подтверждения.",
      detail: "Цены в блоке Pricing. Не подписка.",
      track: "product",
      accent: "#fbbf24",
      sticker: "Pilot",
      cta: "pricing",
    },
    {
      id: "teammate",
      title: "Terminal Teammate",
      essence: "Базовый слой: воркфлоу, библиотеки, живой спрос.",
      detail:
        "Разворачивание воркфлоу и оригинальных проектов. Шаги после пилота.",
      track: "models",
      accent: "#c4b5fd",
      sticker: "Flagship",
      cta: "request",
    },
    {
      id: "api-lane",
      title: "Интеграции и фичи",
      essence: "Настройка интеграций и фич без лишнего burn.",
      detail: "Карта подключений, cost, quality floor для клиентских продуктов.",
      track: "product",
      accent: "#7dd3fc",
      sticker: "Интеграции",
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
    freeTechWriteNote: "Моментальные экспертные идеи сразу.",
    pilotOpsUsd: 690,
    pilotProductUsd: 790,
    pilotPromotionUsd: 490,
    mainPackageUsd: 2490,
    volumeNote:
      "Оплата после вашего успешного получения оплаты. Внедрение с живым общением после подтверждения. Экспериментировать можно не боясь. Без подписок.",
    transactionNote: "",
  },

  fullPackage: {
    name: "Цены",
    why: "Моментальные идеи сразу. Оплата после вашей успешной оплаты. Без подписок.",
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
    businessGeneratePath: "/api/v1/analytics/business-generate",
    knowledgeSynthPath: "/api/v1/analytics/knowledge-synthesis",
    businessServicesPath: "/api/v1/analytics/business-services",
    workersTasksPath: "/api/v1/analytics/workers/tasks",
    workersDashboardPath: "/api/v1/analytics/workers/dashboard",
    distributionPath: "/api/v1/analytics/distribution",
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
