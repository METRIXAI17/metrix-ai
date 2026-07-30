# Действия сейчас + оценка стартапа Metrix AI (Deep Tech ready, branding in progress)

**Дата оценки:** 2026-07-30  
**Источники:** `metrix-ai` codebase · `4 Бизнеса.xlsx` · X @karimmetrix (190342) · Market Units notes · branding/VA: @andrewsmm1  

---

## 1. Что уже есть (факт)

| Актив | Статус | Доказательство |
|-------|--------|----------------|
| Deep Tech runtime (OAE, decision, paid core, memo convert, pilot_private) | **Готов / working** | `Desktop/metrix-ai`, tests, pilot portals |
| Circle-System 3 global steps | **Готов (2026-07-30)** | `backend/core/circle_system/*` |
| Free consult → free tech write → paid pilot → main $2490 | **Заложено** | pilot_private + market_units |
| Публичный бренд X | **В процессе** | KARIM METRIX @karimmetrix, 6 posts, bio science/tech |
| Branding & Virtual Assets | **Человек назначен** | @andrewsmm1; Excel row Branding&VA |
| Ниши | **Заданы** | AI Agencies, Cost Eng, Cloud Economic & Marketing (+ chip/telecom/device) |
| Excel карта 4 бизнесов | **Есть** | Deep Tech 750k ₽ design; Branding&VA chain; каналы x.com/upwork |

**Скрин 190342:** профиль позиционирует recursive schemas / open opportunist / custom specs для AI Agencies, Cost Eng, Cloud & Marketing. Это согласуется с market units, но **ещё не конвертирует** (мало постов, early stage presence).

---

## 2. Что можно сделать **прямо сейчас** (приоритет)

### A. Deep Tech / продукт (владелец: @karimmetrix)

1. **Прогнать** `POST /api/v1/analytics/deep-tech` на 3 реальных brief из целевых ниш → сохранить JSON как case studies.  
2. **Выложить** 1 public free-consult demo (без выноса private pilot_private).  
3. **Зафиксировать** pilot charter template (из terminal_specs) как PDF/Notion one-pager.  
4. **Прогнать тесты:** `py -3 -m pytest tests/test_circle_system.py -q`.  
5. **Снять 1 Loom** 3–5 мин: «как brief → CY/CN/U → tech write → pilot gate» (sales asset).  
6. **Не продавать main** до первого успешного пилота (правило системы).

### B. Branding & VA (владелец: @andrewsmm1)

1. **Phenomenon → Notation → Object** (Excel):  
   - Phenomenon: «детерминированный deep-tech consult без LLM-чека»  
   - Notation: имя/линейка (KARIM METRIX / Metrix Circle / Terminal Teammate)  
   - Object: 1 VA-артефакт (logo lockup + 1 visual system token)  
2. **Согласовать** bio + pinned post с product surfaces (free TZ → pilot → main).  
3. **Visual pack** под 3 карточки: Auto-consult / Tech write / Pilot (в стиле crystal banner профиля).  
4. **Не** раздувать 4 бизнеса сразу — **сфокусировать Deep Tech + Branding** как пару, Virtual Chips/IT later.

### C. Go-to-market (совместно)

| Канал (Excel) | Действие now | KPI 14 дней |
|---------------|--------------|-------------|
| x.com @karimmetrix | 3 поста: problem / method / pilot offer | 1 DM → brief |
| upwork.com | 1 gig: «Tech TZ + ops map for AI agency» | 2 proposals |
| Подписчики / warm | 5 личных outreach с free consult | 2 consults |
| Telegram/Market Units | Короткий оффер «free TZ за brief» | 1 pilot intent |

### D. Операционка

1. Назначить **client signer checklist** в каждом pilot.  
2. Включить support health в weekly review (SFI/ASM).  
3. Ledger seed: кто владеет compute/data/human/channel (resource_match).  
4. White-label arch prompts — готовить как **upsell** «поставь runtime под своего клиента без внешней LLM», не как day-1 offer.

---

## 3. Чего **не** делать сейчас

- Не обещать «полноценный LLM-product» — сила в **детерминированном** deep tech + tech write.  
- Не параллелить все 4 Excel-бизнеса (Financial Eng / Deep Tech / Branding / Virtual Chips) до PMF в Deep Tech.  
- Не поднимать цену main ($2490) в рекламе без 1 case pilot success.  
- Не отдавать private `pilot_private` в public GitHub (уже gitignored — держать).

---

## 4. Оценка стартапа (порядок величины, не formal valuation)

### Стадия

**Pre-revenue / early prototype-to-pilot**  
Deep tech code maturity: **выше среднего** для solo/deep-tech founder.  
Go-to-market & brand: **ранние** (X joined Apr 2026, мало постов, branding in process).

### Скоринг активов (0–10)

| Фактор | Балл | Комментарий |
|--------|------|-------------|
| Техническая глубина / IP-like structure | **8** | OAE, paid core, circle-system, pilot DE model |
| Дифференциация vs pure LLM agencies | **8** | Hybrid/deterministic + capital efficiency story |
| Product packaging (free→pilot→main) | **7** | Воронка ясна |
| Brand / distribution | **3** | Ранний X, branding в процессе |
| Team completeness | **4** | Founder deep tech + branding contractor; нет sales full-time |
| Traction / revenue proof | **2** | Нужны pilot case + $ |
| Defensibility of data loop | **5** | System log + firmware; ещё мало live data |
| **Итого взвешенно** | **~5.2 / 10** | Strong tech, weak GTM |

### Денежные ориентиры (сценарно)

| Сценарий | 6 мес | Условие |
|----------|-------|---------|
| **Conservative** | $0–8k revenue | 0–2 pilots, brand still building |
| **Base** | **$15–40k** | 4–8 pilots (~$500–800) + 1–2 main ($2490) |
| **Upside** | $60–120k | 15+ pilots, 4+ main, 1 white-label runtime license |

**Excel Deep Tech design 750k ₽** (~$8–9k) — ориентир **project-style** solution design, не SaaS ARR.  
SaaS-like valuation сейчас **не применима** без recurring; ближе к **services+IP hybrid**.

### «Стоимость» на сегодня (качественно)

| Подход | Диапазон | Почему |
|--------|----------|--------|
| Asset / rebuild cost | **$40–120k** | Сколько стоило бы воссоздать runtime + docs |
| Pre-seed story (if raising) | **$0.4–1.2M post** только при narrative + 1 pilot LOI | Иначе early friends/family |
| Strategic (agency/tool buyer) | **$80–250k** asset deal | Если tech + brand pack + niches clean |

**Честная формула сейчас:**

> **Сильный deep-tech asset + слабый distribution.**  
> Ценность растёт **не** новым кодом, а **1–3 платными пилотами + case + brand lockup**.

С готовым deep tech и брендингом «в процессе» стартап оценивается как **технически готовый к пилотам, коммерчески pre-traction**. Ускоритель — закрыть 1 пилот end-to-end и закрепить VA/naming.

---

## 5. 30-дневный план (конкретные deliverables)

| Неделя | Deep Tech | Branding (@andrewsmm1) | GTM |
|--------|-----------|------------------------|-----|
| 1 | 3 deep-tech JSON cases; pytest green | Notation shortlist 3 names; moodboard | 2 X posts + 5 outreach |
| 2 | Pilot one-pager + client guide published | Logo lockup draft + VA object v0 | Upwork gig live |
| 3 | 1 live free consult → TZ delivered | Profile banner/visual align | 1 pilot proposal sent |
| 4 | Support weekly review + predictor on real pilot | Final naming pick | Close or iterate pilot |

---

## 6. Связь с Excel «4 бизнеса»

| Строка Excel | Роль now |
|--------------|----------|
| **Deep Tech** | **Core product** — circle-system, 750k design / $60 param как B2B offer ladder |
| **Branding&Virtual Assets** | **Параллельный слой** — @andrewsmm1; не блокирует pilot, блокирует scale brand |
| Financial Engineering | Later / adjacent (tokens, fin models already partial in code) |
| Virtual Chips | Later (paid virtual_chips already in block 18) |
| IT Services&Consulting | Delivery wrapper around pilot |
| Value Augmentation / Asset Genesis / Terminal Agency | Narrative/future SKUs |

**Фокус:** Deep Tech product × Branding surface × 1–2 канала (X + upwork/warm).

---

## 7. Итог одной фразой

**Сейчас:** продавать free consult + free tech write, готовить paid pilot; брендинг доводит identity; оценка = сильный IP-runtime при раннем GTM; цель 30 дней — **первый платный пилот и case**, не «ещё модули».
