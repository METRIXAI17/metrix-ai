# ТЗ для тестировщика · Metrix AI (специализированное + общее)

**Продукт:** Metrix AI — public surface + API  
**Дата:** 2026-08-04  
**Live:** frontend `https://metrix-ai.vercel.app` · API `https://metrix-ai-production.up.railway.app`  
**Локально:** `public/` + `python -m backend.main` (порт 8787)

---

## 1. Цель

Проверить, что публичный продукт ведёт себя предсказуемо по трём **критическим контурам** и по **полному матричному прогону** ролей × режимов × направлений.

Результат работы тестировщика — **отчёт-артефакт** (не «зелёный/красный» в голове):

1. Скопированные **запрос → ответ** (или скрин + текст) на каждом шаге  
2. Что было видно в UI на каждом шаге  
3. **Развёрнутая рефлексия** (где путаница, где сила, где обман ожиданий)  
4. Рекомендация: **ship / conditional / hold** + список блокеров

---

## 2. Роли (кто «играет» пользователь)

| ID | Роль | Цель в тесте |
|----|------|----------------|
| R1 | **Владелец бизнеса (offline)** | Бриф → ядро → понять панель и утверждение |
| R2 | **Владелец / бренд (online)** | Generate online + consult |
| R3 | **Growth-специалист** | Client packs, coop, scoreboard logic |
| R4 | **System & Yield Engineer** | Identity panel, assets (без auto-yield), multi-pass forecast |
| R5 | **Воркер / исполнитель** | Business Tasks → consult path, payout narrative |
| R6 | **Скептик / buyer** | Pricing, approve-gate, скидка 20%, EN/RU |

Каждая роль должна пройти **свой сценарий минимум 1×** внутри общего матричного прогона (см. §4).

---

## 3. Специализированное тестирование (P0)

### 3.1 Identity panel

**Где:** Generate 🔥 → результат → блок **Control panel** + `growth_yield_core` / Sense cards (`identity`, `assets`).

**Проверить:**

| # | Критерий | Pass |
|---|----------|------|
| IP-1 | После generate в панели есть **identity** (channel / standout / industry) | ☐ |
| IP-2 | **Assets** явно: structure + **auto_yield = false** / текст «без авто-доходности» | ☐ |
| IP-3 | Есть **connect_or_diy** (что подключить vs сделать самому) | ☐ |
| IP-4 | EN и RU: смысл панели не ломается, нет смеси языков в chrome | ☐ |
| IP-5 | Offline brief → channel offline/hybrid; online brief → online/hybrid | ☐ |

**Мини-брифы (по 1× EN + 1× RU минимум):**

```
A) Offline cafe on main street + delivery. Need unique identity and asset structure in control panel. No yield promises.
B) SaaS analytics for small shops online. Need identity map and what to connect first vs DIY.
```

**В отчёте на каждый прогон:**

- Текст запроса (headline + body + channel)  
- JSON/фрагмент `output.control_panel` + `output.growth_yield_core` (или скрин)  
- Вердикт: identity читается за ≤30 сек? да/нет + комментарий  

---

### 3.2 Client packs

**Где:** Generate / Consult → coop narrative; flagship **Client packs**; matryoshka layer **Coop**; тариф **Client cooperation**.

**Проверить:**

| # | Критерий | Pass |
|---|----------|------|
| CP-1 | В copy / panel / growth_core есть **client pack** (похожие запросы) | ☐ |
| CP-2 | Matryoshka layer «Кооперация / Coop» hover: текст про packs + handoff | ☐ |
| CP-3 | Карточка flagship Client packs открывается, CTA ведёт в consult/generate | ☐ |
| CP-4 | Brief «у меня 8 клиентов с одним типом handoff» → в ответе есть coop/pack сигнал | ☐ |
| CP-5 | Тариф Coop $1,190 + пункт про скидку 20% на повтор в категории | ☐ |

**Бриф:**

```
Agency with 6–8 retainers: same rework on handoffs. Need client pack config for similar requests, shared scoreboard, coordinated handoffs.
```

---

### 3.3 Approve-gate (оплата только после утверждения внедрения)

**Где:** Hero badge/sub, Path step 04, form_lead, pricing, forecast block, footer.

**Проверить:**

| # | Критерий | Pass |
|---|----------|------|
| AG-1 | **Нет** формулировок «оплата после вашей оплаты» / «pay after your pay» | ☐ |
| AG-2 | Есть **опциональная оплата при утверждении внедрения** (EN+RU) | ☐ |
| AG-3 | Path 01 = «Опишите бизнес и запрос своими словами» | ☐ |
| AG-4 | Generate forecast говорит про качество **если утвердить** real implementation | ☐ |
| AG-5 | Pricing: **убран** длинный абзац про бэкенды партнёра; есть **скидка 20%** на повтор в категории | ☐ |
| AG-6 | Hero H1 = прежние строки: «Единое окно… / воркфлоу…» (EN: One window… / workflows…) | ☐ |
| AG-7 | Hero sub = **2 предложения**, визуально тонкий **blue→teal shimmer** | ☐ |

**Регресс-копирайт (grep mental checklist):**  
`pay after your pay` · `после вашего успешного получения оплаты` · `Ideas free. Four clear tariffs` — **не должны** появляться на главной.

---

## 4. Общее тестирование (матрица × 3)

### 4.1 Режимы (mode)

| Mode | UI entry | API / действие |
|------|----------|----------------|
| M1 marketplace | Products / home cards | Без API — клики, modal, niches |
| M2 request | Consult + Tech-TZ | `POST /api/v1/process` + free-work |
| M3 tasks | Business Tasks | `GET business-services` + demo → consult |
| M4 generate | Generate 🔥 | `POST /api/v1/analytics/business-generate` |

### 4.2 Направления (tracks / channels / tariffs)

**Tracks (consult):** product · models (teammate/yield) · promotion  
**Channels (generate):** auto · online · offline · hybrid  
**Tariffs (pricing):** core · coop · marketing · capital  
**Lang:** EN · RU  
**Niches:** 10 client directions (минимум 3 разных + 1 «Assets»)

### 4.3 Правило «3 раза»

Для **каждой ячейки** ниже выполнить **3 независимых прогона** (разный brief или слегка изменённый):

| Ячейка | Что крутить 3× |
|--------|----------------|
| M1 × EN | 3 разных flagship card → modal → CTA |
| M1 × RU | то же |
| M2 × track product | 3 brief + niche |
| M2 × track models | 3 brief |
| M2 × track promotion | 3 brief |
| M3 × services | 3 разных task card → demo → consult |
| M4 × channel auto | 3 brief |
| M4 × channel online | 3 brief |
| M4 × channel offline | 3 brief |
| M4 × channel hybrid | 3 brief |
| Pricing × 4 tariffs | UI: клик CTA каждого тарифа 1× + проверка 20% (копирайт) 3× lang switch |
| System map | hover каждого из 5 слоёв EN + RU |

**Минимум прогонов (оценка объёма):**  
~ (2 lang × 4 modes × 3) + specialized + pricing ≈ **30–40 осмысленных сессий**.  
Не нужно 10 ниш × 3 blindly — **выборочно 3 ниши × 3** + 1 assets.

### 4.4 Шаблон шага (копировать в отчёт)

```markdown
### Run ID: M4-offline-02 · Role R1 · 2026-08-04
**Lang:** ru  
**Mode:** generate  
**Channel:** offline  
**Request:**
> headline: ...
> body: ...

**Steps UI:**
1. Open Generate → filled form → submit
2. Saw: forecast / niche rank / panel / ...

**Response (paste key fields):**
- message: ...
- channel.mode: ...
- implementation_forecast: passes / band / readiness
- control_panel cards: identity / assets / client_pack
- final_gate: ...

**Pass/Fail notes:** ...
```

---

## 5. Чеклист UX / i18n / brand (общее)

| # | Проверка |
|---|----------|
| U1 | Favicon + logo в шапке = brand M (`metrix-brand-m.jpg`) |
| U2 | EN/RU переключатель: весь chrome на одном языке (не mix) |
| U3 | Matryoshka: hover подсветка + текст панели |
| U4 | Mobile ~375px: pricing 1 col, matryoshka stack, nav usable |
| U5 | API down: generate/consult показывают ошибку, не silent blank |
| U6 | Assets niche blurb: no auto-yield promise |
| U7 | Auto niche: generate без ручного picker niche |

---

## 6. API smoke (для тестировщика с curl/Postman)

```http
GET  /api/v1/health
POST /api/v1/process
POST /api/v1/analytics/business-generate
GET  /api/v1/analytics/business-services?lang=ru
```

**business-generate body:**

```json
{
  "business": "Offline cafe + delivery. Identity panel and client packs.",
  "lang": "ru",
  "channel": "offline",
  "multi_pass": true,
  "passes": 7,
  "project_name": "Cafe test"
}
```

**Ожидать в output:** `channel`, `implementation_forecast`, `growth_yield_core`, `control_panel` с identity/assets.

---

## 7. Deliverable: структура отчёта

Файл: `docs/reports/TEST_REPORT_YYYY-MM-DD.md` (или Google Doc + link)

1. **Summary** — ship / conditional / hold  
2. **Specialized results** — Identity · Client packs · Approve-gate (таблица pass/fail)  
3. **Matrix log** — все run ID со вставками request/response  
4. **Bugs** — severity S0–S3, repro  
5. **Развёрнутая рефлексия** (обязательно):
   - Где продукт «чувствуется» как Metrix, а где как generic AI form  
   - Понятен ли approve-gate за 5 секунд  
   - Доверие к forecast (не overpromise?)  
   - EN vs RU качество  
   - Что бы поправил тестировщик в copy/UX за 1 день  
6. **Рекомендации** — top 5 fixes before next push  

---

## 8. Рекомендуемая цена работы тестировщика

Оценка объёма по этому ТЗ:

| Пакет | Scope | Часы (оценка) | **Рекомендуемая цена** |
|-------|--------|---------------|-------------------------|
| **A. Smoke** | Только §3 specialized + health + 6 generate/consult | 3–4 ч | **$90–120** / 8–12k ₽ |
| **B. Full (это ТЗ)** | §3 + §4 матрица ×3 + отчёт + рефлексия | **10–14 ч** | **$280–380** / **25–35k ₽** |
| **C. Full + regression pack** | B + 2nd pass после фиксов + чеклист retest | 16–20 ч | **$420–520** / 38–48k ₽ |

**Базовая рекомендация для этого ТЗ: пакет B — $320 / ~28–30k ₽**  
(mid market freelance QA specialist, bilingual RU/EN, отчёт с артефактами, не «просто кликнул»).

Доплаты:

- +$40–60 если нужен Loom 10–15 мин walkthrough  
- +$50–80 если нужен авто-smoke script (Playwright) сверх ручного  

Критерий оплаты тестировщику: **сдан отчёт §7**, а не «время в кресле».

---

## 9. Definition of Done (для приёмки ТЗ)

- [ ] §3 Identity / Packs / Approve-gate закрыты таблицами  
- [ ] ≥ 24 matrix runs с request/response  
- [ ] Нет regression: pay-after-pay / длинный pricing_why / wrong H1  
- [ ] Forecast + channel на live API  
- [ ] Рефлексия ≥ 1 страница  
- [ ] Вердикт ship/conditional/hold  

---

## 10. Контакты / артефакты продукта

- X: [@karimmetrix](https://x.com/karimmetrix)  
- Repo: `METRIXAI17/metrix-ai`  
- Copy source: `public/js/data.js`  
- Generate logic: `backend/core/business_gen/generator.py`  
- Release notes: `docs/RELEASE_2026-08-04_MARKET_UNITS_ULTRA.md`  

**Не в scope тестирования:** backend маркетинга, backend внешнего финансирования, private `pilot_private/`.
