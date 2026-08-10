# Системные ворота Metrix AI v2

**Дата:** 2026-08-10  
**Триггер:** 3 нарекания на CraftShift (анализ / executive / promo+fund в situation)

## Ворота (hard fail если < 0.6)

| # | Metric | Смысл |
|---|--------|--------|
| 1 | `analysis_completeness` | diagnosis + friction/leak + evidence + entities + gaps |
| 2 | `executive_clarity` | S0–S10 steps + plain_how + approve gate + progress |
| 3 | `situation_promo_funding` | promo+funding **вшиты** в situation, не сиротские вкладки |

## Доп. метрики сборки

- `path_fidelity` · `essence_clarity` · `prompt_strength`  
- `meaning_density` · `code_build_readiness`  
- `originality` · `acceptance_p` (как раньше)

Модуль: `backend/core/business_gen/assembly_metrics.py`  
В generate: `output.assembly_metrics` + `final_gate.systemic_three_ok`

## Усиления

| Модуль | Роль |
|--------|------|
| `build_prompt_engine.py` | Master prompt с hard rails → сильнее Grok Build |
| `meaning_engine.py` | Block 19 live — плотность смыслов |
| `user_paths.py` v1.2 | +creator_shift · hobby_lattice · api_surface + scenarios |
| `generative/stub.py` | MeaningEngine expand |

## Re-run CraftShift brief

`assembly.band = ideal` · overall ≈ 0.85 · systemic_three.ok = true  
(см. `backend/workspace/_four_tariff_run/05_assembly_v2.json`)

## Правило на следующие проекты

Любой generate / build prompt **обязан** закрывать systemic 3.  
Repair list в `assembly_metrics.repairs` — что дописать.
