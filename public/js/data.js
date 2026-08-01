/**
 * Metrix AI — public surface (unified offer · niches · problems · pricing)
 * Horizontal axis: liquidity (decision-making ↔ D2C offramp ↔ autoliquidity)
 */
window.METRIX_DATA = {
  brand: {
    name: "Metrix AI",
    tagline: "Orient · Decide · Liquidate",
    focus: "Operational success with a liquidity path",
    x: "https://x.com/karimmetrix",
  },

  /** One surface — three product lines (not three separate businesses) */
  masterOffer: {
    headline: "AI that turns intent into liquidity",
    sub:
      "One workspace for online business: orient the problem, structure the decision, " +
      "ship a document the market can buy — or a terminal agent can execute. " +
      "Expert ideas free. Transactions paid. No salary-style retainers, no % of placements.",
    pillars: [
      {
        id: "shift",
        name: "Metrix AI Shift",
        line: "Close the three hard gaps: organization · product · promotion.",
        detail:
          "Pilot-first path for online business. Scale key problems on a volume tariff. " +
          "Prompt builder as the gate to any IT-reachable fix. Ops libraries + expert system under the hood.",
      },
      {
        id: "assistant",
        name: "Metrix AI Assistant",
        line: "Global decision layer — metrics, structure, market pulse.",
        detail:
          "Dynamic market data, key-metric detector, change model, structured user intents. " +
          "Terminal agents for execution when you authorize them. Concierge-grade clarity without a human payroll.",
      },
      {
        id: "interface",
        name: "Metrix AI Interface",
        line: "The surface: workspace, D2C offramp, asset decisions.",
        detail:
          "Write an idea → get a freelace-ready / builder-ready document → optional agent run. " +
          "Asset lane: cognition · monitoring · strategy generation — trade management stays with you.",
      },
    ],
    disclaimers: [
      "Work is delivered against a clear TZ (spec). No guarantees of profit, yield, or deal success.",
      "Asset / market tools are decision support — not investment advice and not auto-trading custody.",
    ],
  },

  /**
   * Niches (8). Last two are autoliquidity lanes: decision-making + D2C share one liquidity surface.
   */
  industries: [
    {
      id: "ai-agencies",
      name: "AI Agencies",
      short: "Agencies",
      blurb: "Ops efficiency · delivery without agent chaos.",
      icon: "◇",
      accent: "#5eead4",
      description:
        "Agencies that sell AI delivery: fix intake, rework, handoff. Terminal Teammate as base-layer access — not another chatbot. Promo = buyer fin models.",
      problems: ["rework eats margin", "agents without scoreboard", "sales without unit economics"],
      liquidity: "ops",
    },
    {
      id: "cloud-economy",
      name: "Cloud / API cost",
      short: "Cloud",
      blurb: "Cut third-party API spend, keep quality.",
      icon: "☁",
      accent: "#7dd3fc",
      description:
        "For founders burning tokens and vendor APIs. Unit-cost map, quality band, Expert path vs pure LLM bill. Event promo that reviews what already ships.",
      problems: ["API bill grows faster than revenue", "quality vs cost fog", "no Expert vs LLM comparison"],
      liquidity: "ops",
    },
    {
      id: "cost-engineering",
      name: "Cost Engineering",
      short: "Cost",
      blurb: "Cut waste parameters, keep capability.",
      icon: "▣",
      accent: "#fbbf24",
      description:
        "Simple waste map + resellable Void Scanner. One-page ops offer + broad product pack for people who hire cost engineers.",
      problems: ["fat specs nobody uses", "capability cut with the waste", "no resellable SKU"],
      liquidity: "ops",
    },
    {
      id: "chipmaking",
      name: "Chipmaking",
      short: "Chips",
      blurb: "Design-loop clarity before tapeout.",
      icon: "▦",
      accent: "#c4b5fd",
      description:
        "Conceptual yield twin and design-loop voids — ops / product / promo as three simple offers. Clarity without hype fog.",
      problems: ["design-loop voids", "late yield surprises", "buzzword promo"],
      liquidity: "ops",
    },
    {
      id: "telecom",
      name: "Telecom",
      short: "Telecom",
      blurb: "ARPU, churn, SLA-native SKUs.",
      icon: "◈",
      accent: "#86efac",
      description:
        "Carrier-grade product language: SLA, ARPU, MOS. Ops levers for churn; promo as intent-signal care weave.",
      problems: ["spreadsheet SLA fog", "SKU ≠ QoS", "churn without lever board"],
      liquidity: "ops",
    },
    {
      id: "device-assembly",
      name: "Device assembly",
      short: "Devices",
      blurb: "Stations & config that scale — hands + online.",
      icon: "⬡",
      accent: "#fda4af",
      description:
        "Assembly → setup → guided config as a product. Online business paired with physical periphery when you want to build with your hands.",
      problems: ["station rework time", "config matrix chaos", "demo that does not scale"],
      liquidity: "ops",
    },
    {
      id: "asset-decisions",
      name: "Asset decisions",
      short: "Assets",
      blurb: "AI for asset management decisions.",
      icon: "◎",
      accent: "#f0abfc",
      badge: "Автоликвидность",
      description:
        "Decision support for people who already have capital (or want a private room): key metric, risk model, what not to do. " +
        "Cognition · monitoring · strategy generation — deal management stays yours. Presented as work by TZ, no yield guarantees. " +
        "Not “trading bots hype”: base mechanisms that Claude/API stacks already use to draft strategies.",
      problems: [
        "capital parked in banks / signals with no model",
        "no key metric or change model",
        "bot scripts without risk language",
      ],
      liquidity: "autoliquidity",
      fork: "assistant",
    },
    {
      id: "d2c-offramp",
      name: "D2C · freelace offramp",
      short: "D2C",
      blurb: "Idea → document → exchange → agent.",
      icon: "↗",
      accent: "#67e8f9",
      badge: "Автоликвидность",
      description:
        "Direct D2C offramp: you drop an idea you cannot finish; the system returns a workspace document that matches freelace / market demand. " +
        "Basic order search can be automated; creative multi-variant work is what clients pay for — then a terminal agent executes the accepted doc. " +
        "Liquidity = decision-making with a path to cash, not another 30-minute YouTube vinaigrette.",
      problems: [
        "idea with no freelace-ready pack",
        "outreach without a document",
        "creative work lost before terminal agent",
      ],
      liquidity: "autoliquidity",
      fork: "interface",
    },
  ],

  tracks: [
    { id: "product", name: "Product", label: "Product", color: "#5eead4", salesGuide: true },
    { id: "models", name: "Teammate", label: "Teammate", color: "#fbbf24", salesGuide: true },
    { id: "promotion", name: "Promotion", label: "Promotion", color: "#c4b5fd", salesGuide: false },
  ],

  /** Why-us marquee (ops · product · promotion · liquidity) */
  whyUsSlides: [
    {
      key: "ops",
      title: "Operations",
      text:
        "Same product. Better ops analytics → different money. Orient the geometry of the business, kill free-discovery waste, lock a scoreboard — without a token-swarm of agents.",
    },
    {
      key: "product",
      title: "Product",
      text:
        "The product is access to the base layer — not “another AI tool”. Libraries → procurement as self-generation → live demand → own stack. Capture liquidity where others rent infrastructure.",
    },
    {
      key: "promotion",
      title: "Promotion",
      text:
        "Promotion is the angle, not a separate product. When ops and product are locked, the story sells: proof posts, reverse outreach, events that review what already ships.",
    },
    {
      key: "liquidity",
      title: "Liquidity",
      text:
        "D2C and decision-making sit on one surface: structure the request → ship a document or metric model → optional agent. Autoliquidity niches: assets + freelace offramp.",
    },
  ],

  /**
   * Frequent problems → top solution the system proposes (rotating slides).
   * Filled from real sequence + process dry-runs (2026-08-02).
   */
  problemSlides: [
    {
      problem: "Online business stuck: org · product · promo all half-done",
      solution:
        "Metrix AI Shift: free orient → one primary track → pilot on that track only. Volume tariff if you scale all three later. Main package only after pilot proof.",
      niche: "shift",
    },
    {
      problem: "Capital idle or trust in crypto signals — no decision model",
      solution:
        "Asset decisions lane: key metric + risk model + “what not to do”. Cognition / monitoring / strategy drafts. Management of deals stays with client. Work by TZ, no yield promise.",
      niche: "asset-decisions",
    },
    {
      problem: "Idea exists; freelace gigs look the same; nothing to send",
      solution:
        "D2C workspace: structured brief → freelace-ready document → optional order match → terminal agent on accepted scope. You sell the multi-variant creative layer; agent executes the fixed doc.",
      niche: "d2c-offramp",
    },
    {
      problem: "API / token burn without quality floor",
      solution:
        "Expert path: unit-cost map, hot-path calls, quality band. Compare pure LLM multi-agent vs Metrix hybrid. Event promo that reviews current spend before selling the fix.",
      niche: "cloud-economy",
    },
    {
      problem: "Agency delivery rework >20%",
      solution:
        "Ops map: intake · rework · handoff. Lower VVI on agent specs. 14-day scoreboard + one Terminal Teammate lane — not a full rewrite.",
      niche: "ai-agencies",
    },
    {
      problem: "YouTube “AI freelace bots” — no clear value",
      solution:
        "Horizontal surface: decision document first, automation second. Value = pack the client can buy on the exchange; change = digital product + optional agent, not a 30-minute salad of buzzwords.",
      niche: "d2c-offramp",
    },
    {
      problem: "Want hands-on + online income",
      solution:
        "Device / periphery lane: one station end-to-end, config SKU matrix, then online offer. Project for people who already have something — not for “wage slavery” scripts.",
      niche: "device-assembly",
    },
    {
      problem: "Trading bot curiosity without risk language",
      solution:
        "Only base mechanisms: market models under a situation, logical + risk analysis, explicit “do not do X”. Subscription or one-shot program for info + abstract support — not unmanaged auto-trading.",
      niche: "asset-decisions",
    },
  ],

  howItWorks: {
    title: "How Metrix AI works",
    lead:
      "One horizontal surface: free expert orientation → structured document / metric model → pilot or autoliquidity lane. " +
      "Transactions when you execute. Volume discount when you scale multiple problem packs.",
    steps: [
      {
        n: "01",
        title: "Orient",
        text: "Industry + your words + numbers. Diagnosis, mechanism, product fork (Shift / Assistant / Interface) — without a catalog tour.",
      },
      {
        n: "02",
        title: "Structure",
        text: "Free tech TZ / workspace doc: scope, packages, acceptance. SEQUENCE-style arch prompts when you build with agents.",
      },
      {
        n: "03",
        title: "Pick liquidity path",
        text: "Ops/product/promo pilot — or autoliquidity: asset decisions · D2C freelace offramp. One primary lane so energy does not leak.",
      },
      {
        n: "04",
        title: "Ship · optional agent",
        text: "Pilot proof → main package or volume tariff. Terminal agents only on accepted docs / authorized actions. You keep deal management.",
      },
    ],
  },

  flagships: [
    {
      id: "consult",
      title: "Free consultation",
      essence: "Short business brief → diagnosis, direction, next steps.",
      detail:
        "Describe your business in 5–20 sentences. Free orientation pack (EN/RU): diagnosis, change mechanism, product choice, short notes. Expert ideas free — transactions when you buy execution.",
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
        "Technical specification language: scope, work packages, acceptance, DoD — free tech write after orientation. Prompt builder for any IT-reachable problem.",
      track: "product",
      accent: "#38bdf8",
      sticker: "Free",
      cta: "techwrite",
    },
    {
      id: "pilot",
      title: "Pilot",
      essence: "One live lane — ops, product, or promotion — with proof metrics.",
      detail:
        "Paid pilot, clear scoreboard, go/no-go for main package. Volume tariff if you expand to multi-problem packs after pilot success.",
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
        "Step 1 — Company by niches: libraries, configs.\n" +
        "Step 2 — Procurement: prompts = self-generation of what you used to buy outside.\n" +
        "Step 3 — Sales: live demand, not a static catalog.\n" +
        "Step 4 — Own stack: engineering, materials, research, content — fewer rented costs.\n" +
        "Step 5 — Corporate network that multiplies the first four.\n\n" +
        "This is not a chatbot. It is base-layer access.",
      track: "models",
      accent: "#c4b5fd",
      sticker: "Flagship",
      cta: "request",
    },
    {
      id: "asset-lane",
      title: "Asset decisions",
      essence: "AI for asset management decisions — cognition, monitor, strategies.",
      detail:
        "Autoliquidity niche. Private-room friendly: key metric, risk model, market situation packs. " +
        "You keep deal management. No base fee as “AMC % of AUM” — paid work by TZ / subscription for intel + support. No guarantees.",
      track: "product",
      accent: "#f0abfc",
      sticker: "Автоликвидность",
      cta: "request",
      industryHint: "asset-decisions",
    },
    {
      id: "d2c-lane",
      title: "D2C freelace offramp",
      essence: "Idea → document → market → optional terminal agent.",
      detail:
        "Autoliquidity niche. Workspace for incomplete ideas. Output matches freelace exchange problems so you can sell the creative layer; agent runs the accepted document. Basic order search automatable.",
      track: "product",
      accent: "#67e8f9",
      sticker: "Автоликвидность",
      cta: "request",
      industryHint: "d2c-offramp",
    },
    {
      id: "expert",
      title: "API cost · Expert",
      essence: "Cut third-party API spend, keep quality.",
      detail:
        "For founders burning tokens and vendor APIs. Unit-cost map, quality band, Expert path vs pure LLM bill.",
      track: "product",
      accent: "#86efac",
      sticker: "Flagship",
      cta: "request",
    },
    {
      id: "metrix-ai",
      title: "Why Metrix AI",
      essence: "Dynamic story: ops · product · promotion · liquidity.",
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
    freeTechWriteNote: "Expert ideas + tech TZ after free consult are free.",
    pilotOpsUsd: 690,
    pilotProductUsd: 790,
    pilotPromotionUsd: 490,
    mainPackageUsd: 2490,
    volumeNote:
      "Volume tariff: multi-problem packs (org + product + promo) after pilot — discount vs three separate pilots. Ask in consult.",
    transactionNote: "Transactions / agent runs / private rooms: paid. No placement %, no “salary” retainer required to start.",
  },

  fullPackage: {
    name: "Pricing",
    why:
      "Expert ideas free. Tech TZ free. Pilot by track. Main / volume after proof. Transactions when you execute.",
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
