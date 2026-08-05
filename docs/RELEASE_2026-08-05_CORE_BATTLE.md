# Release 2026-08-05 · Core deliverable battle-ready

## Scope

Market Units improvements on **business-generate / Core $790** surface for the architecture library product and general generate path.

## Market Units checklist

| # | Gap | Fix |
|---|-----|-----|
| 1 | Numbers from signer → answers | `merge_signer_numbers`: cash_ceiling + days → `constraint_cash` / `constraint_time`; UI fields + API `numbers` |
| 2 | Live 7-day channel log | `channel_log_7d`: 12–15 touch plan + 1 artifact (not the word “network”) |
| 3 | Calendar kill T1–T3 | ISO `start_date` / `kill_date` / `go_date` on concept tests + dated pilot plan |
| 4 | Deep A01–A12 | Niche designs: SaaS billing, agent ops, API cost, marketplace, … (not library meta-templates) |
| 5 | PDF/export + CSV | `exports.cards_csv` + `print_html` (browser print→PDF) + MD; download buttons in UI |
| 6 | Implementation assistant | 5-step path after **Approve Core** (not CTA-only) |
| 7 | EN parity | Full EN markdown when `lang=en` |

## New modules

- `backend/core/business_gen/core_deliverable.py` v2.0 battle
- `backend/core/business_gen/hook_plan.py` — short buy-ready custom plan

## Hook plan (conversion)

One-screen pitch: payer · unit · cash/window · 7-day proof · calendar kill · assist after approval · value mid vs $790.

## Tests

- `tests/test_knowledge_and_business_gen.py` — library RU + EN parity + all 7 gaps
- Full suite: **105 passed**

## Deploy

- Push `main` → Vercel `public/` + Railway API (auto)
- Live generate: `POST /api/v1/analytics/business-generate` with `numbers.cash_ceiling`, `numbers.days`
