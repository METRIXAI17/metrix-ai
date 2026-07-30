# Deep Tech Metrix AI — Circle-System

**Дата:** 2026-07-30  
**Кодовое имя:** circle-system  
**Продукт:** metrix-ai  
**Отсылки:** ref_3 → 1 2 3 4 · ref_4 → 5 6 7 · models: open  
**Excel:** `Documents/4 Бизнеса.xlsx` (Deep Tech + Branding&VA)  
**Публичный профиль:** @karimmetrix / KARIM METRIX (снимок 190342)

---

## Три глобальных шага

| Шаг | Содержание | Модули |
|-----|------------|--------|
| **A** | Сложный текст → параметры; косвенный проход **ТОЧНО ДА / ТОЧНО НЕТ / НЕОПРЕДЕЛЕНО** | `certainty_analyzer` |
| **B** | Неопределённости → супер-скоростной ассистент (тесты) → **сборка** параметров (не «тепло») → Super Program → ответы с **лингвистическим теплом** | `super_speed_assistant`, `parameter_assembly`, `super_program`, `linguistic_warmth` |
| **C** | Autopilot circle: слои-потребности, терминальные спеки, оркестрация, ресурсы+ledger, ops-rules tech write, integration lib, pilot predictor, metric firmware, **support**, expert libs, **arch prompts без внешней LLM** | остальные модули `circle_system` |

### Правило истины vs тона

- **Сборка (assembly)** — анализирует, сходятся ли условия параметра.  
- **Тепло (warmth)** — только язык ответа. Никогда не меняет CY/CN/U.

---

## Super Program (Excel Deep Tech)

Из строки Deep Tech (`4 Бизнеса.xlsx`):

1. SYNTHESIS CORE  
2. REALITY LAYER INTERFACE  
3. SYMMETRY BRIDGE  
4. VALUE PROPOSITION ENGINE  
5. ENGAGEMENT & TRANSACTION PROTOCOL  
6. METRIX LEDGER & OPERATIONAL CORE  

Ценовой ориентир Excel: **750 000 ₽** solution design + **$60** параметризация сделок.

---

## Продуктовые поверхности (готовые утверждения)

| Поверхность | Утверждение | Gate |
|-------------|-------------|------|
| **Auto-consult** | Детерминированный consult из текста → CY/CN/U + warmth-ответы + test battery | всегда |
| **Tech write** | Terminal specs + phased insert (ops rules) | всегда draft |
| **Pilot** | Charter + prediction (логистическое ДУ с L=0.92) | assembly≥0.45 · consistency≥0.62 |
| **Main product** | $2490 после успеха пилота | predicted_end≥0.7 · risk≠high · autopilot_ready |
| **White-label arch prompts** | Промпты для размещения программ клиентам **без внешней LLM** | всегда |

---

## API

```
GET  /api/v1/analytics/circle-system
GET  /api/v1/analytics/lexicon
GET  /api/v1/analytics/support-system
GET  /api/v1/analytics/knowledge?q=...
POST /api/v1/analytics/deep-tech
```

Тело `POST /deep-tech`:

```json
{
  "business": "описание ≥20 символов…",
  "industry": "ai-agencies",
  "lang": "ru",
  "test_answers": {},
  "product_name": "Metrix Circle Runtime",
  "client_label": "client",
  "pilot_horizon_days": 21
}
```

Полный `POST /api/v1/process` кладёт результат в `meta.circle_system` и `meta.deep_tech_product_surfaces`.

---

## Код

```
backend/core/circle_system/
  lexicon.py
  certainty_analyzer.py
  super_speed_assistant.py
  parameter_assembly.py
  super_program.py
  linguistic_warmth.py
  layers.py
  terminal_specs.py
  orchestration.py
  resource_match.py
  ops_rules.py
  integration_lib.py
  pilot_predictor.py
  metric_firmware.py
  support_system.py
  arch_prompt_gen.py
  knowledge_libs.py
  deep_tech_pipeline.py
```

Тесты: `tests/test_circle_system.py`

---

## Пилот-модель

Дискретная логистика (предопределённый показатель **L = 0.92**):

```
y_{t+1} = y_t + k · y_t · (1 − y_t / L)
```

`k` и `y0` из assembly / consistency / resource compatibility.

---

## Support System (отсылка)

См. `docs/SUPPORT_SYSTEM_RU.md` и `GET /analytics/support-system`.  
Цепочка: Metric Firmware → anomalies → tickets → human-authorized owners → residual watch pilot predictor.  
Refs: ref_3, ref_4, Excel Deep Tech, Excel Branding&VA, @karimmetrix, ops R5.
