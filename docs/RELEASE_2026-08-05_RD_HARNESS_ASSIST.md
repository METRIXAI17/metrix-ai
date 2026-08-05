# Release 2026-08-05b · R&D Reader · Harness · Assist Agent

## Why (user signal)

Previous Core battle pack was mostly **file-side** (CSV/MD). On-screen almost unchanged.  
This release makes surfaces **visually obvious** and adds harness-class architecture.

## Video concepts used

Source: [Новые правила контекстной инженерии…](https://youtu.be/wT0LOkQVgNc) (Yersham)

| Concept | Product mapping |
|---------|-----------------|
| Intent / goals / success criteria over long prompts | Author personality product |
| Harness (memory + tools) | Skill memory + assist agent tools |
| Dynamic skill load | Smart router loads prior distilled skills |
| Autonomy band | R&D S6 + personality.autonomy_band |
| High-level oversight | Agent advances by criteria/kills, not micro-text |
| Golden examples | personality.golden_examples |

## Visible UI

1. **FREE banner** + 3 download buttons (R&D HTML→PDF, CSV, MD)  
2. **Author personality** card with axes bars  
3. **R&D Reader iframe** (beautiful HTML, not plain pre-MD)  
4. **Separate Assist Agent product** + Approve unlock + Advance step  
5. **Route chip** (domain / depth / skills)

## New modules

| Module | Path |
|--------|------|
| R&D reader-converter | `backend/core/business_gen/rd_reader.py` |
| Author personality | `backend/core/business_gen/author_personality.py` |
| Smart router | `backend/core/business_gen/smart_router.py` |
| Skill memory | `backend/core/business_gen/skill_memory.py` |
| Assist agent | `backend/core/business_gen/assist_agent.py` |

## API

- `POST /api/v1/analytics/business-generate` → adds `rd_reader`, `author_personality`, `smart_routing`, `skill_*`, `assist_agent`, free `exports`
- `POST /api/v1/analytics/assist-agent/approve`
- `POST /api/v1/analytics/assist-agent/advance`
- `GET  /api/v1/analytics/assist-agent/{session_id}`
- `GET  /api/v1/analytics/skill-memory`

## Classification of system (current state)

| Layer | Class | Notes |
|-------|-------|-------|
| Public UI | Static SPA (HTML/CSS/JS) | Vercel |
| API | FastAPI monolith | Railway |
| Generate pipeline | Deterministic multi-module orchestrator | No external LLM required |
| Knowledge synth | Rule + structure engines | Human-light planner |
| Core cards | Generative templates + niche deep designs | Design-card generative core |
| R&D reader | Symbolic converter | Evidence grades A/B/C |
| Personality | Feature scoring / archetypes | Not ML embedding (v1) |
| Smart router | Multi-label heuristic router | Domain · surface · depth · products · skills |
| Skill memory | File-backed episodic store | Conceptual + executive algorithms |
| Assist agent | Stateful session automaton | Approve → queue → advance |
| AI label | **Hybrid decision system / agentic shell** | Appropriate: not pure LLM app; harness + rules + optional future LLM |

## Technical evaluation after generative card core

| Dimension | Score (1–10) | Comment |
|-----------|--------------|---------|
| Product clarity (visible) | 8 | FREE + R&D frame + personality + separate assist |
| Decision justification | 8 | Warrants + falsifiers + grades |
| Architecture depth of cards | 8 | 12 niche deep designs |
| Memory / learning loop | 7 | Distill on success; load on route |
| Autonomy / agent | 7.5 | Runnable queue, not only CTA |
| EN/RU parity | 7.5 | R&D + personality bilingual |
| True ML / LLM core | 4 | Deliberately symbolic; LLM optional later |
| Deployability | 9 | Static + FastAPI, no new deps |
| **Overall (technical)** | **7.6 / 10** | Strong productized decision OS; not foundation-model lab |

## Plan (implemented this release)

1. Free downloads always on  
2. Replace primary MD with R&D reader  
3. Split assist as separate product + autonomous agent  
4. Author personality product  
5. Smart routers  
6. Skill distill conceptual+executive  
7. Memory management (file harness)  
8. Module interaction: generate → personality → route → distill → R&D → assist teaser  

## Deploy

Push `main` → Vercel public + Railway API.
