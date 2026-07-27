# Metrix AI (KARIM METRIX)

**Operational Analytical System** — store of ready-made solutions for idea generation, business consulting, and product optimization.

Public positioning: [@karimmetrix](https://x.com/karimmetrix)

- Dynamic **Orientation** (no massive training dump of the client’s business)
- Zones: **Infa Sol · Cloud Sol · Structure Fi · Product Sol**
- Connecting layer: **Superstructure / Product Overlay**
- **Enhanced Decision Making Core** — full project awareness + mode switch
- **Main Operational Analytics Engine (OAE)** — constructor form, embedding, ricochet
- **Custom Success Metrics Positioning** — unique TZ per request
- Monetization: **Promo · Market Making · Auto Orders**
- Core metrics everywhere: **VVI · ER · RRC** + informational ROI
- Roadmap slots: **block 18 paid core** · **block 19 generativity**

---

## Two surfaces

| Surface | What | Stack |
|---------|------|--------|
| **Frontend** | Marketplace + request form + Full Package tour | Static HTML/CSS/JS |
| **Backend** | Full request processing OAS | Python · FastAPI |

### Final layer (2026-07-21)

- **21-principle engine** (210 edges · 490 meanings) · Sequence Assembler · Anti-Down Sorter  
- Objectly · OpeningEdge · NFT Create-Building · Harness live mode  
- **Capital efficiency** (LLM vs Hybrid vs Metrix) + charts: `/app/capital-efficiency.html`  
- Report: `docs/CAPITAL_EFFICIENCY_PITCH_RU.md`  
- API: `GET /api/v1/analytics/capital-efficiency` · `/principles` · `POST /final-layer`

### v1.1 Memo Convert · Market Units (2026-07-26)

- **Memo Convert** — unique engine + reader-assembler (no idea-DB): system → coop open-opp → analog function → reverse categories → tech tasks  
- **Market Units** — application points + simple offers (agencies / API-cost Expert / cost-eng / chip / telecom)  
- **Consult + Tech Write package = $1290** (MetaReality $890 + SpecsForge $650 − $250)  
- API: `GET /api/v1/analytics/market-units` · `/package-costs` · `POST /memo-convert`  
- Release notes: `docs/RELEASE_1_1_MEMO_CONVERT_2026-07-26.md`

### Free consult → Pilot funnel (2026-07-27)

- **Public:** free orientation consult (EN+RU result pack), track ranking ops/product/promo, industry sanity packs  
- **Text usability suite** (dedupe / simplify / dry-math) · multi-industry originality bench  
- **Pricing:** free → pilot $490–790 → main $2490 only after pilot success  
- **Private pilot backend:** `pilot_private/` (gitignored) — client + executor portals on port 8790  
- Deploy / finance: `docs/PILOT_FINANCE_AND_DEPLOY.md` · License Apache-2.0 (`LICENSE`)

### Lean public frontend (2026-07-27)

- Flagship cards only (6) · no catalog bloat / architecture dump on home  
- Method: Get a consultation → Pick direction → Ship  
- Pricing strip: free → pilot → main  
- Deploy: **`DEPLOY.md`** (Vercel static + optional API)

---

## Quick start (backend)

```powershell
cd $env:USERPROFILE\Desktop\metrix-ai
pip install -r requirements.txt

# Smoke: all 6 industries (no HTTP needed)
python scripts/first_test_all_industries.py

# API server
python -m backend.main
```

- API root: http://127.0.0.1:8787/  
- Swagger: http://127.0.0.1:8787/docs  
- Health: http://127.0.0.1:8787/api/v1/health  
- **Process request:** `POST /api/v1/process`  
- Static site: http://127.0.0.1:8787/app/  

### Process a request

```json
POST /api/v1/process
{
  "industry": "ai-agencies",
  "business": "Your business description (20+ chars) and what makes it special…",
  "track": "all",
  "name": "Alex",
  "contact": "@handle",
  "success_metrics": {
    "weights": { "iroi": 0.35, "impact": 0.25, "clarity": 0.15 },
    "targets": { "iroi": 0.6 },
    "priority": ["iroi", "impact", "clarity"],
    "composite_target": 0.6
  }
}
```

Returns: orientation, demo idea, **decision_core**, **operational_analytics**, **success_metrics**, breakdown, fin models, monetization, next steps.

One interactive request (Windows): `run_one_request.bat` or `py -3 scripts\one_request.py`

Analytics preview: `POST /api/v1/analytics/oae-preview`

---

## Architecture (pipeline v2)

```
Request
  → OrientationForge (place / mine / calculate)
  → Superstructure Product Overlay
       Infa Sol · Cloud Sol · Structure Fi · Product Sol
  → Informational Profitability (IROI)
  → Custom Success Metrics TZ  ← influences scoring / decision / OAE
  → System Log Analyst         ← features from past requests
  → Enhanced Decision Making Core
       geometry awareness · thinking trace · mode switch
       scoring | generative_development | recursive_refinement | dual_ricochet
  → Main Operational Analytics Engine
       1. constructor of a certain form (undefined params)
       2. dynamic embedding assembly
       3. deep analysis on embedding
       4. reduce back to user request
       5. answer shift parameters
       6. abstract coordinates (double bottom fly-out)
       7. reverse void ricochet (RRC)
       8. Pragma Collection splitting → demo-fast path
  → Fin Models · IdeaStructure · Monetization · Self-improve
  → Response
       slots: backend/paid (18) · backend/generative (19)
```

### Main Operational Analytics Engine (how it works)

| Step | Meaning |
|------|---------|
| **Constructor of a certain form** | Vague/missing params are not dropped — they become *form slots* (outcome_frame, void_membrane, revenue_hinge…) that inject energy into the embedding |
| **Embedding assembly** | Deterministic 12-dim vector from axes + scores + constructors + success weights + system-log gravity (not a cloud LLM) |
| **Deep analysis** | Surface / track / latent energy, product–promo tension, top dimensions |
| **Reduce to request** | Deep layer compressed into client-facing bridge text |
| **Answer shift** | How far demo wording should move toward client lexicon vs keep seed spine |
| **Abstract coordinates** | Ready solutions that “fly out” as double-bottom latent offers |
| **Reverse void ricochet** | Voids bounce through reverse links into reassemblable fragments; raises RRC |
| **Pragma splits** | Metric firmware combinations (VVI×ER×RRC×success) become recursive generative split points when scoring fails |

### Enhanced Decision Making Core

- Builds **project geometry** (axes, tension, voids pressure, monetization pull)
- **Thinking process** (sense → structure → metrics firmware → pragma → system memory → commit)
- **Improving decisions** with owners (SpecsForge, OAE, human, paid/gen slots)
- **Mode switch**: when to leave pure scoring for generative / recursive / ricochet
- Handoff flags for **block 18** (paid) and **block 19** (generativity)

### Custom Success Metrics Positioning

Per-request TZ: weights, targets, priority order, composite target.  
Becomes part of unique technical specification and feeds Decision + OAE influence vectors.

### Six Fin Models

1. **ChipForge Metrics** — chip design, vulnerability, production  
2. **OrientationForge Engine** — dynamic orientation & parameter map  
3. **EdgeForge Calculator** — edge compute economics  
4. **MetaObject Simulator** — second-type virtual object simulation  
5. **PrologForge Logic Engine** — rule-based reasoning  
6. **MarketForge Optimizer** — promo, market making, auto orders  

Every new Fin Model must follow the **3-stage template**  
(`backend/fin_models/template.py`): Definition → General Paid → Custom Paid.

### Industry directions (mandatory on requests)

`ai-agencies` · `cloud-economy` · `cost-engineering` · `chipmaking` · `telecom` · `device-assembly`

---

## Project layout

```
metrix-ai/
├── index.html, css/, js/     # public marketplace (frontend)
├── backend/                  # OAS request backend
│   ├── main.py
│   ├── core/
│   │   ├── orientation_engine.py
│   │   ├── superstructure.py
│   │   ├── request_pipeline.py      # v2 orchestrator
│   │   ├── decision_core.py         # Enhanced Decision Making Core
│   │   ├── operational_analytics.py # Main OAE
│   │   ├── success_metrics.py       # Custom TZ positioning
│   │   ├── pragma_phenomena.py      # Pragma 2021 splits
│   │   ├── system_log.py
│   │   └── metrics.py
│   ├── paid/                 # BLOCK 18 — paid product core (slot + meaning vectors)
│   ├── generative/           # BLOCK 19 — generativity concept (stub)
│   ├── zones/ modules/ fin_models/ monetization/
│   ├── api/routes/           # + analytics.py
│   └── workspace/
├── tests/                    # test_core.py + test_oae_decision.py
├── scripts/
├── docs/
├── requirements.txt
└── DEPLOY.md
```

---

## Tests

```powershell
pytest tests/ -q
python scripts/first_test_all_industries.py
```

---

## Monetization paths

| Path | Role | Showcase base |
|------|------|----------------|
| **Promo** | Idea & offer automation | $490 |
| **Market Making** | Positioning + attention liquidity | $890 |
| **Auto Orders** | Decision → order loops | $1290 |
| **Consult + Tech Write** | MetaReality consult + SpecsForge tech writing | **$1290** |
| **Full Package** | Product + Models + Promotion tour → implement | $2490 |

Demo idea + breakdown stays free; full implement is quoted after the tour.

---

## Docs (Russian)

- [Отчёт о работе](docs/REPORT_RU.md)  
- [Инструкция: обработка запросов + first test × 6](docs/FIRST_TEST_GUIDE_RU.md)  
- [Deploy frontend](DEPLOY.md)  

---

## License

Private project content — © Metrix AI / Karim Metrix.
