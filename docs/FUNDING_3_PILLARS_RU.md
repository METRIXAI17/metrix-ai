# Фандинг Metrix AI · 3 столпа

**Дата:** 2026-08-08  
**Поверхность:** `?mode=funding` · тариф *Funding · 3 pillars* · `POST /api/v1/analytics/funding-pack`

---

## Расшифровка плана

### 1. Структурный авто-доход

Не «пассивный yield по активам».  
**Авто** = после настройки OUTPUT (Generate / Consult / Promo / free-work → paid gate)  
деньги появляются, когда кто-то касается **уже работающей** поверхности.

Мгновенные рычаги (seed):

| Lever | Surface | $ seed |
|-------|---------|--------|
| orient_run | paid orientation | 290 |
| consult_tech | free Consult + Tech-TZ | 0 → pilot |
| promo_pack | mode Promo | 690 |
| pilot_14 | ops pilot | 1490 |
| full_package | stack | 2490 |

Модуль: `backend/monetization/structural_income.py`

### 2. Активы 1:1

Допродажи к **уже настроенным** продажам (не «актив сам зарабатывает»):

- **Аренда** 1–4 недели (compute slot, VA pack, channel seat, ops board, pilot capacity)
- **%** 7–15% от outcome после signed scope

Правило: один attach ↔ один sale/pilot. Idle >40% → cut.

Модуль: `backend/monetization/asset_attach.py`

### 3. Кооперация с размещённым капиталом

Капитал кладётся в **именованные слоты** (ops / distribution / buffer),  
партнёры работают по shared scoreboard (паки Metrix).  
Evidence first → narrative second. Gate:

- `structure_first` → сначала pillar 1 + 1 free run  
- `build_evidence` → orientation / numbers  
- `partner_ready` → partner pack

Модуль: `backend/monetization/capital_coop.py`  
Сборка: `backend/core/business_gen/funding_pack.py`

---

## Как работать с платной частью (просто)

```
01 FREE  Funding form        → 3 столпа + launch path
02 FREE  Generate / Consult  → ideas + tech-TZ
03 PAID  Orientation $290    → axes + commercial card  (после go-ahead)
04 PAID  Pilot $1490         → 14–30d + assist         (numbers locked)
05      Attach + capital     → rental/% + partner pack (после 1 proof)
```

1. Открой сайт → **Funding** в шапке (или тариф).  
2. Заполни оффер + контекст (≥20 символов), опционально capital USD.  
3. **Собрать план** — читай `pillars`, `levers`, `launch_path`, `paid_quickstart`.  
4. Primary lever = CTA в DM/сайте.  
5. Когда готов внедрять — DM [@karimmetrix](https://x.com/karimmetrix) на orientation/pilot.  
6. Attach и partner capital — только после 1 proof cycle.

### API

```bash
curl -sS -X POST https://metrix-ai-production.up.railway.app/api/v1/analytics/funding-pack \
  -H "Content-Type: application/json" \
  -d "{\"business\":\"AI agency pilots and unit margin, 10k capital\",\"project_name\":\"Ops\",\"lang\":\"ru\"}"
```

Локально:

```bash
python -m backend.main
# POST http://127.0.0.1:8787/api/v1/analytics/funding-pack
```

### Как читать результат

| Поле | Зачем |
|------|--------|
| `pillars[].steps` | Чеклист на неделю |
| `instant_levers` / `role=primary` | Что ставить в CTA |
| `readiness.gate` | Можно ли звать партнёра |
| `launch_path` | Порядок без догадок |
| `paid_quickstart` | Free → paid ступени |

---

## Честность продукта

- Нет auto-yield promises по активам (как в остальных слоях Metrix).  
- Цены seed / showcase — финальный quote в ops.  
- Capital narrative без unit/pilot proof = `structure_first` / `build_evidence`.
)
