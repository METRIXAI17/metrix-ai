# План-задание · Описание: скачать PDF + подключить Assist path

**Продукт:** Metrix AI · Generate 🔥 · Core / Ядро ($790)  
**Дата:** 2026-08-05  
**Статус runtime:** уже в коде (`core_deliverable_2.0_battle`) — задача = **описать, упаковать copy, проверить UX**, не изобретать с нуля  
**Поверхности:** UI Generate · hook plan · API `POST /api/v1/analytics/business-generate` · EN/RU

---

## 1. Цель задания

Сделать так, чтобы пользователь **за 30 секунд** понял:

1. **Можно скачать результат как файл** (в т.ч. PDF-путь), а не только смотреть на экране.  
2. **После утверждения внедрения** открывается **Assist path** — пошаговый ассистент, а не одна кнопка «Consult».

Результат работы по этому ТЗ — **артефакты описания** (copy + чеклист + 1 мини-гайд), а не новый backend.

---

## 2. Что уже есть в системе (факт для автора)

### 2.1 Скачивание / PDF

| Элемент UI | ID | Что отдаёт |
|------------|-----|------------|
| ↓ Markdown | `#gen-dl-md` | `exports.markdown` / `core_markdown` → файл `.md` |
| ↓ Cards CSV | `#gen-dl-csv` | `exports.cards_csv` → `.csv` (A01–A12, offers, T1–T3) |
| ↓ HTML→PDF | `#gen-dl-html` | `exports.print_html` → `.html` print-ready |

**PDF-путь (текущий, честный):**  
скачать HTML → открыть в браузере → **Print → Save as PDF**.  
Отдельного server-side PDF binary (reportlab и т.п.) **нет** — в copy **не обещать** «магическую кнопку PDF без print», пока не сделают v2.

**API-поля:**

```text
response.exports.cards_csv
response.exports.print_html
response.exports.markdown
response.exports.filenames  → csv / html / md
response.core_report.exports  (зеркало)
```

**Где в UI:** блок Hook plan, сразу после generate result (`#gen-hook-block`).

### 2.2 Assist path

| Элемент | ID / ключ | Поведение |
|---------|-----------|-----------|
| CTA утверждения | `#gen-approve-core` | «Approve Core · $790» |
| Панель пути | `#gen-assist-path` | **hidden** до клика Approve |
| Данные | `core_report.implementation_assistant` | 5 шагов IA1–IA5 |

**Триггер:** `implementation_approval` (опциональная оплата **после** утверждения — не «pay after your pay»).

**Шаги (смысл):**

| ID | Суть |
|----|------|
| IA1 | Scope lock после approval (S1–S4, cash, anti-scope) |
| IA2 | Assist: desk + schema A01–A12 |
| IA3 | Tester-strategist: T1 gate |
| IA4 | Channel log mid-check (≥10 touches + artifact) |
| IA5 | Final client tune + stop/go |

**Pay model string:** `optional_on_implementation_approval`

---

## 3. Задачи исполнителю (описание / copy / UX-текст)

### Задача A — Copy «Скачать как файл»

**Сделать:**

1. **RU + EN** короткие подписи кнопок (не жаргон «blob»):  
   - MD: «Скачать отчёт (.md)» / «Download report (.md)»  
   - CSV: «Карточки CSV» / «Cards CSV»  
   - HTML→PDF: «HTML для PDF» / «HTML for PDF» + tooltip: «Откройте файл → Печать → Сохранить как PDF»
2. **Один абзац** (≤40 слов) под кнопками:  
   *«Deliverable — файлы, не только экран. PDF: HTML → печать в браузере.»*
3. **Один bullet** в hook plan / pricing strip, если есть место:  
   *«CSV + MD + print→PDF в комплекте Core-draft»*
4. **i18n-ключи** (предложение имён):  
   `gen_dl_md` · `gen_dl_csv` · `gen_dl_html` · `gen_dl_pdf_hint` · `gen_export_note`

**Не делать:** обещать native PDF API, email-delivery, watermark, invoice PDF.

**Критерий done:**

- [ ] Пользователь без подсказки понимает, **как получить PDF**  
- [ ] EN и RU без смеси в одном chrome  
- [ ] Copy согласован с approve-gate (оплата после approval)

---

### Задача B — Copy «Подключить Assist path»

**Сделать:**

1. Переименовать/усилить primary CTA:  
   - RU: **«Утвердить Ядро · открыть Assist»**  
   - EN: **«Approve Core · unlock Assist»**  
   (цена $790 может остаться secondary chip)
2. **До Approve** — 1 строка-тизер:  
   *«После GO: 5 шагов assistant + tester-strategist (scope → desk → T1 → channel log → tune).»*
3. **После Approve** — заголовок блока + шаги в человеческом виде (не raw JSON):  
   `IA1 · дата · название · действие · exit`
4. Явно связать: **Approve ≠ автоматическое списание**.  
   Формула: *«Утверждение внедрения открывает Assist path; оплата — опционально после GO.»*
5. **i18n-ключи:**  
   `gen_approve_core` · `gen_assist_teaser` · `gen_assist_unlocked` · `gen_assist_pay_note`

**Не делать:** обещать live human manager 24/7; auto-yield; «оплата после вашей оплаты».

**Критерий done:**

- [ ] До клика ясно, **что откроется**  
- [ ] После клика path **виден**, CTA disabled («Утверждено · assist открыт»)  
- [ ] 5 шагов читаются за ≤20 сек

---

### Задача C — Мини-гайд «1 экран» (для docs / pilot client)

Написать **1 страницу** (RU + EN) со структурой:

```text
1. Generate → hook plan
2. Скачать: MD / CSV / HTML→PDF (как)
3. Утвердить Core → Assist path
4. Что делает каждый шаг IA1–IA5
5. Что не входит (anti-scope)
```

Файл-цель (создать/дополнить):  
`docs/GUIDE_PDF_AND_ASSIST_PATH_RU.md` (+ EN section или twin)

**Критерий done:** пилот-клиент проходит сценарий без созвона.

---

### Задача D — Визуальные / product notes (если есть designer)

1. Группа кнопок: **primary = Approve**, secondary = downloads в одном `cr-cta-row`.  
2. После unlock — soft highlight `#gen-assist-path` (border / eyebrow «Assist unlocked»).  
3. Не прятать downloads за Approve (файлы доступны **до** оплаты).  
4. Mobile: кнопки wrap, не обрезать «HTML→PDF».

---

## 4. Сценарий приёмки (тест-кейс для описания)

### TC-PDF-1 · Скачать HTML→PDF

| Шаг | Действие | Ожидание |
|-----|----------|----------|
| 1 | Generate 🔥, brief ≥20 символов | Появился `#gen-hook-block` |
| 2 | Клик «↓ HTML→PDF» | Файл `metrix-core-report.html` скачался |
| 3 | Открыть HTML | Виден title + pre с Core report |
| 4 | Print → Save as PDF | PDF читаем, без raw JSON |

### TC-CSV-1 · Карточки

| Шаг | Ожидание |
|-----|----------|
| Клик CSV | Есть строки `architecture,A01,...` и `concept_test,T1,...` |

### TC-ASSIST-1 · Подключить path

| Шаг | Действие | Ожидание |
|-----|----------|----------|
| 1 | До Approve | `#gen-assist-path` hidden |
| 2 | Approve Core | Path visible, ≥5 строк IA* |
| 3 | Повторный клик | Кнопка disabled / «Утверждено» |
| 4 | Copy | Нет «pay after your pay»; есть optional on approval |

### TC-LANG-1

| Lang | Ожидание |
|------|----------|
| RU | Подписи и assist summary на RU (или dual-safe) |
| EN | Core markdown `# Core:`, assist EN, chrome EN |

---

## 5. Формулировки «можно / нельзя» (для любого описания)

| Можно говорить | Нельзя |
|----------------|--------|
| Скачать отчёт MD, карточки CSV, HTML для печати в PDF | «Мгновенный PDF с сервера» (пока нет) |
| После утверждения внедрения открывается Assist path | «Оплата после вашей оплаты» |
| 5 шагов: scope → desk → test → channel → tune | «Гарантия revenue / auto-yield» |
| Оплата внедрения опциональна после GO | Assist = бесплатный forever unlimited |

---

## 6. Связь с тарифом Core ($790)

| Слой | Доступность (текущая логика) | Как описывать |
|------|------------------------------|---------------|
| Hook plan + screen report | После generate | «Черновик Ядра на экране» |
| Downloads MD/CSV/HTML | После generate | «Файловый deliverable draft» |
| Assist path unlock | После **Approve Core** | «Путь внедрения после утверждения» |
| Full $790 close | Живой channel log execution + approval | Gap-copy уже в `value_vs_core` |

*Freemium-разрез demo/paid — отдельное решение; в этом задании только **описать** текущее поведение.*

---

## 7. Deliverables исполнителя (чеклист сдачи)

1. [ ] Таблица copy RU/EN для 3 download + 1 approve + 1 assist teaser/unlocked  
2. [ ] Tooltip/hint для PDF-пути (HTML → Print → PDF)  
3. [ ] Текст блока Assist path (шаблон 5 шагов, human-readable)  
4. [ ] Мини-гайд 1 страница (`docs/GUIDE_…`)  
5. [ ] Прогон TC-PDF-1 · TC-CSV-1 · TC-ASSIST-1 · TC-LANG-1 (скрин или notes)  
6. [ ] Список «не обещаем» согласован с Market Units / approve-gate  

**Формат сдачи:** один PR или один doc + комментарий в чат: «copy ready / TC pass».

---

## 8. Оценка объёма

| Роль | Часы (оценка) |
|------|----------------|
| Copy / product writer | 1.5–3 ч |
| Frontend i18n wiring (если внедрять тексты в `data.js`) | 0.5–1 ч |
| QA по TC | 0.5–1 ч |
| **Итого** | **~3–5 ч** |

---

## 9. Definition of Done (общий)

Описание готово, если:

- в UI/доке **явно** видны два пути: **Download files** и **Unlock Assist**;  
- PDF объясняется **честно** (HTML→print);  
- Assist path = **5 шагов после approval**, не пустой CTA;  
- EN/RU parity copy;  
- приёмка по §4 без блокеров P0.

---

## 10. Опциональный next (вне scope описания)

Только если после copy решат допилить продукт:

1. Server-side PDF (`reportlab` / weasy) — endpoint `GET/POST …/export.pdf`  
2. Persist approval state (localStorage + server flag)  
3. Deep-link «Assist room» в private pilot  
4. Email deliverable pack  

---

**Владелец продукта:** @karimmetrix / Metrix Core  
**Связанный release:** `docs/RELEASE_2026-08-05_CORE_BATTLE.md`  
**Код-якоря:** `public/js/app.js` (`bindExportButtons`, approve handler) · `core_deliverable.exports` · `implementation_assistant`
