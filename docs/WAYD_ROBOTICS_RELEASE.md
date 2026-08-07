# wayD + Robotics + GenCore 0.2 — release notes

**Date:** 2026-08-07  
**Version:** BusinessGenerator `2.3.0-wayd` · GenCore `0.2.0-wayd`

## What landed

| # | Item | Where |
|---|------|--------|
| 1 | Live log UI | `public/ops-panel.html` — day grid, tick, ledger, list |
| 2 | Implement model · 3 directions (only paid SKU, **hidden**) | `implement_model.py` + redact on generate |
| 3 | GenCore rework | `gencore.py` v1–v6 slots, wayD context |
| 4 | Originality injections (probabilistic) | `originality_inject.py` × 3 directions |
| 5 | Acceptance forecast | `acceptance_forecast.py` · P(final accept) |
| 6 | Expert base popular directions | `expert_base_directions.py` |
| 7 | Sophisticated user paths | `user_paths.py` |
| 8 | B2B client segmentation | `client_segmentation.py` |
| — | wayD labels + terminal + edges | `backend/core/wayd/*` |
| — | Robotics harness R0–R6 | `robotics_harness.py` |
| — | License personal-only / commercial forbidden | `LICENSE` |
| — | Appsmith short guide | `docs/APPSMITH_SETUP.md` |

## wayD concept

Labels (`L.direction.*`, `L.segment.*`, `L.path.*`, `L.metric.*`, `L.edge.*`, `L.rail.*`) are system edges.  
**Unique functions** appear only at module intersections (edge mesh), e.g.:

- GenCore × LiveLog → live uniqueness trail  
- Segment × Path → segment-locked sophisticated pack  
- Acceptance × Originality → raise unique phrasing when reject risk  
- Robotics × Implement → autonomous three-direction rollout  

Terminal metrics: **density · signal · acceptance_p · mesh · ship_gate**.

## Paid surface (hidden)

Single paid service = **implementation of three directions**:

1. `product_pack`  
2. `unit_pack`  
3. `ch_network`  

Public generate redacts prices (`price_redacted`, `commercial_hidden`).  
Ops may call `POST /api/v1/analytics/implement-model` with `expose_price: true` internally.

## Robotics how it works

1. **R0** Sense wayD terminal + labels  
2. **R1** Lock implement model (3 directions)  
3. **R2** Materialize product_pack + originality  
4. **R3** Materialize unit_pack  
5. **R4** Drive live log ticks / artifact  
6. **R5** Acceptance gate P(accept)  
7. **R6** Ship / hold + next actions  

Control: `POST /analytics/robotics/plan` → `/start` → `/advance`.  
UI: `/app/ops-panel.html` section 4.

## API additions

- `POST /analytics/wayd/terminal`  
- `POST /analytics/segment`  
- `GET  /analytics/expert-directions`  
- `POST /analytics/expert-directions/match`  
- `POST /analytics/user-path`  
- `POST /analytics/implement-model`  
- `POST /analytics/robotics/plan|start|advance`  
- `GET  /analytics/robotics/{id}`  
- `GET  /analytics/live-log` (list sessions)  

## Next actions

1. Set Railway `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` for durable live_log  
2. Wire Appsmith queries from `APPSMITH_SETUP.md`  
3. Run multi-pass eval on top 5 popular paths  
4. Optional: skill_memory → Supabase table  
5. Keep public homepage free of implement pricing  
