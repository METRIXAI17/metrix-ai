/**
 * Metrix AI — public site data (flagships + how-it-works + pricing)
 */
window.METRIX_DATA = {
  brand: {
    name: "Metrix AI",
    tagline: "Orient · Pick · Ship",
    focus: "Operational success",
    x: "https://x.com/karimmetrix",
  },

  industries: [
    { id: "ai-agencies", name: "AI Agencies", short: "Agencies", blurb: "Ops efficiency & delivery.", icon: "◇", accent: "#5eead4" },
    { id: "cloud-economy", name: "Cloud / API cost", short: "Cloud", blurb: "Cut third-party API spend.", icon: "☁", accent: "#7dd3fc" },
    { id: "cost-engineering", name: "Cost Engineering", short: "Cost", blurb: "Cut waste, keep capability.", icon: "▣", accent: "#fbbf24" },
    { id: "chipmaking", name: "Chipmaking", short: "Chips", blurb: "Design-loop clarity.", icon: "▦", accent: "#c4b5fd" },
    { id: "telecom", name: "Telecom", short: "Telecom", blurb: "ARPU, churn, SLA SKUs.", icon: "◈", accent: "#86efac" },
    { id: "device-assembly", name: "Device assembly", short: "Devices", blurb: "Stations & config that scale.", icon: "⬡", accent: "#fda4af" },
  ],

  tracks: [
    { id: "product", name: "Product", label: "Product", color: "#5eead4", salesGuide: true },
    { id: "models", name: "Teammate", label: "Teammate", color: "#fbbf24", salesGuide: true },
    { id: "promotion", name: "Promotion", label: "Promotion", color: "#c4b5fd", salesGuide: false },
  ],

  /**
   * Why-us marquee slides (ops · product · promotion)
   * Card scrolls these dynamically.
   */
  whyUsSlides: [
    {
      key: "ops",
      title: "Operations",
      text:
        "Same product. Better ops analytics → different money. Orient the geometry of the business, kill free-discovery waste, lock a scoreboard. Ops alone changes cash — without a token-swarm of agents.",
    },
    {
      key: "product",
      title: "Product",
      text:
        "The product is access to the base layer — not “another AI tool”. Terminal Teammate opens the descent: niches & libraries → procurement as self-generation → live market sales → own engineering, materials tech, thinking research, content gen with fewer external bills → corporate network. Capture liquidity where others rent infrastructure.",
    },
    {
      key: "promotion",
      title: "Promotion",
      text:
        "Promotion is the angle, not a separate product. When ops and product are locked, the story sells itself: proof posts, reverse outreach, events that review what already ships — then point to Teammate, Expert, or the pilot lane. Angle follows structure.",
    },
  ],

  /** How the whole product works — excited plain language */
  howItWorks: {
    title: "How Metrix AI works",
    lead:
      "You drop a short business story. The system orients it, ranks ops · product · promotion, and hands you a free tech-writing path plus a pilot when you are ready to move.",
    steps: [
      {
        n: "01",
        title: "Orient",
        text: "Industry + your words + numbers. Diagnosis, mechanism, product choice — without a catalog tour.",
      },
      {
        n: "02",
        title: "Write it down",
        text: "Free technical writing (tech TZ / SpecsForge style): scope, packages, acceptance — something implementers can open.",
      },
      {
        n: "03",
        title: "Pick one lane",
        text: "Ops, product, or promotion. One primary track so energy does not leak between three half-done projects.",
      },
      {
        n: "04",
        title: "Pilot · then ship",
        text: "A paid pilot on that lane. Main package only if the pilot proves the path. Terminal Teammate is the base-layer access when you are ready to descend.",
      },
    ],
  },

  /** Flagships */
  flagships: [
    {
      id: "consult",
      title: "Free consultation",
      essence: "Short business brief → diagnosis, direction, next steps.",
      detail:
        "Describe your business in 5–20 sentences. Free orientation pack (EN/RU): diagnosis, change mechanism, product choice, short notes.",
      track: "ops",
      accent: "#5eead4",
      sticker: "Free",
      cta: "request",
    },
    {
      id: "tech-journalism",
      title: "Technical journalism",
      essence: "Free tech TZ: consult → readable, build-ready writing.",
      detail:
        "Technical specification language: scope, work packages, acceptance, DoD — free tech write after orientation. Not a jargon dump.",
      track: "product",
      accent: "#38bdf8",
      sticker: "Free",
      cta: "techwrite",
    },
    {
      id: "pilot",
      title: "Pilot",
      essence: "A focused live lane: ops, product, or promotion — with proof metrics.",
      detail:
        "One paid pilot lane, clear scoreboard, go/no-go for the main package. Prices live in the Pricing block below — not on this card.",
      track: "product",
      accent: "#fbbf24",
      sticker: "Pilot",
      cta: "pricing",
    },
    {
      id: "teammate",
      title: "Terminal Teammate",
      essence: "Access to the base layer — not “an AI product”.",
      detail:
        "Terminal Teammate is permission to descend under the surface of the market.\n\n" +
        "Step 1 — Company by niches: libraries, configs, chip-configuration sales as the entry map.\n" +
        "Step 2 — Procurement: prompts = self-generation of what you used to buy outside.\n" +
        "Step 3 — Sales: life market — live demand, not a static catalog.\n" +
        "Step 4 — Own stack: engineering in equipment, tech in materials, research for thinking, content generation — fewer rented costs, liquidity capture.\n" +
        "Step 5 — Corporate network: the layer that multiplies the first four.\n\n" +
        "This is not a chatbot. It is base-layer access.",
      track: "models",
      accent: "#c4b5fd",
      sticker: "Flagship",
      cta: "request",
    },
    {
      id: "expert",
      title: "API cost · Expert",
      essence: "Cut third-party API spend, keep quality.",
      detail:
        "For founders burning tokens and vendor APIs. Unit-cost map, quality band, Expert path vs pure LLM bill. Flagship for creative and custom ops.",
      track: "product",
      accent: "#86efac",
      sticker: "Flagship",
      cta: "request",
    },
    {
      id: "metrix-ai",
      title: "Why Metrix AI",
      essence: "Dynamic story: ops · product · promotion — scroll the layers.",
      detail: "", // filled by marquee in UI
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
    freeTechWriteNote: "Tech TZ / technical writing after free consult is free.",
    pilotOpsUsd: 690,
    pilotProductUsd: 790,
    pilotPromotionUsd: 490,
    mainPackageUsd: 2490,
  },

  fullPackage: {
    name: "Pricing",
    why:
      "Consult free. Tech TZ free. Pilot priced by track. Main package only after pilot success.",
  },

  /**
   * API base URL resolution:
   * 1) window.METRIX_RUNTIME.apiBaseUrl (set in index.html or by deploy)
   * 2) local host → http://127.0.0.1:8787
   * 3) production → set METRIX_API_BASE below after Railway public URL is known
   *
   * Empty string "" = same-origin (use with Vercel rewrites proxy to Railway).
   */
  api: {
    baseUrl: (function resolveApiBase() {
      if (typeof window !== "undefined" && window.METRIX_RUNTIME && window.METRIX_RUNTIME.apiBaseUrl != null) {
        return String(window.METRIX_RUNTIME.apiBaseUrl).replace(/\/$/, "");
      }
      var host = typeof location !== "undefined" ? location.hostname : "";
      if (host === "localhost" || host === "127.0.0.1") {
        return "http://127.0.0.1:8787";
      }
      // Production Railway public URL (fallback if METRIX_RUNTIME not set)
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
