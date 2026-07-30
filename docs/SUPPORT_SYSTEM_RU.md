# Support System — как работает (с отсылками)

## Назначение

Ловить сбои внедрения пилота и product-runtime **до** того, как клиент «теряет» trust.  
Не чат-бот поддержки, а **метрический контур**: firmware → anomalies → tickets → owners → retest.

## Цепочка

```
Metric Firmware (base + auto-composed)
        ↓ anomalies (ASM, CNS, SFI, PAP, …)
Support System
        ↓ tickets (severity, SLA, owner)
Human-authorized / tech adapters
        ↓ close condition
Assembly retest OR certain_yes on linked param
        ↓
Pilot predictor residual watch
```

## Пороги (по умолчанию)

| Метрика | Warn / Critical | Смысл |
|---------|-----------------|--------|
| ASM | < 0.35 warn | Сборка параметров слабая |
| CNS | < 0.5 warn | Слои circle не согласованы |
| SFI | ≥ 0.55 critical | Индекс риска сбоя support |
| PAP | < 0.55 warn | Прогноз точности пилота низкий |

## SLA

- critical → 4 часа  
- warn → 24 часа  
- info → 72 часа  

## Owners (human-authorized)

| Owner | Handle / id | Когда |
|-------|-------------|--------|
| Deep Tech | @karimmetrix / hum_deep_tech_owner | ASM/CNS/PAP/SFI tech |
| Branding & VA | @andrewsmm1 / hum_branding_va | identity / VA |
| Client signer | client_designee | RCM, acceptance |

## Отсылки (дописано)

| Ref | Значение |
|-----|----------|
| **ref_3: 1 2 3 4** | Цепочка разработки параметров + косвенной достоверности |
| **ref_4: 5 6 7** | Super-speed → Super Program → компоновка метрик |
| **models: open** | Открытые модели матчинга Super Program |
| **pilot DE** | `y' = k y (1−y/L)`, L=0.92 предопределён |
| **Excel Deep Tech** | 6 компонентов SYNTHESIS…LEDGER (`4 Бизнеса.xlsx`) |
| **Excel Branding&VA** | Phenomenon → Notation → Object → branding reverse |
| **screenshot 190342** | Публичный профиль KARIM METRIX @karimmetrix |
| **ops R5** | `metric_firmware.anomaly → open_support_ticket` |
| **ops R6** | main package только при pilot accuracy gate |

## API

`GET /api/v1/analytics/support-system` — структура + demo ticket.  
Полный feed: `POST /api/v1/analytics/deep-tech` → `support` + `metric_firmware.support_feed`.

## Код

- `backend/core/circle_system/metric_firmware.py`  
- `backend/core/circle_system/support_system.py`  
- `backend/core/circle_system/ops_rules.py` (R5, R6)
