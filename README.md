# Metrix AI (KARIM METRIX)

**v2.8.0 · дверь ALLO 2.1.0 · контур 2.7 NPODP · 2026-11-23**

Один код. Дверь и комнаты одного потока. Не чат, не каталог идей.

Публичный голос: [@karimmetrix](https://x.com/karimmetrix) · бот [@karimmetrixbot](https://t.me/karimmetrixbot)

| | |
|---|---|
| Сайт | https://metrix-ai.vercel.app |
| API + Mini App | https://metrix-ai-production.up.railway.app |
| Health | https://metrix-ai-production.up.railway.app/api/v1/health |
| Контуры | https://metrix-ai-production.up.railway.app/app/contours/ |

---

## Языки

Сайт открывается по-русски. Кнопки EN и RU переключают весь видимый текст. Внутренние имена функций и команды на страницу не выводятся.

## Вес

Исходник в Git — около 21 МБ, 562 файла, около 94 тысяч строк. Папка на машине больше, потому что в `backend/data/requests` лежат локальные прогоны. Это не клиенты: 16 ноября 2026 тесты и скрипты (`Anna Kovaleva`, `Dmitry Orlov`, `PaidTest`, `Portfolio Test`, `Test`). В GitHub эти файлы не входят.

Уникальные визиты сайта отсюда не видны: счётчика на странице нет, доступа к аналитике Vercel нет. Цифру не выдумываю.


Из ситуации собирается объект (демо, контур, ключ). Если зашло — это товар. Если нет — не продаём «ещё чат».

Три проекта одной сборки, не семь продуктов:

| Проект | Работа |
|---|---|
| **Финансы** | Рисуем показатели. Касса, понедельник, дыра. |
| **Диптех** | Eval, полёт агента, рекурсивная спека. Контур работает. |
| **Бренд** | Мир, в который хотят зайти. Дверь и комнаты. |

Слои того же потока: чипы (роботизация) · маркеты (воронка) · продажи (лёгкое «купить») · ценность.

Демо — платёжная дорога, не брошюра.

---

## Что продаём

Одна цена двери: **$50 Allo** / месяц. Directing — отдельно, один ход уже открытого контура. Хиты и Store бесплатно. Верхние комнаты остаются для рекурсии и спек. Доходность не обещаем. Ордеров на биржу из ядра нет.

| SKU | Цена | Что входит | Что не входит |
|---|---|---|---|
| **Allo** | **$50 / мес** | Дверь, чтение семи операций, грант запросов | Directing, файл рекурсии, сигналы, Main $2490 |
| **Directing** | отдельно, разово | Один ход из двенадцати следствий | Не директолог и не рекламный кабинет |
| **$100 / $490 / $1000 / $10 000** | верхние комнаты | Кастом спека, рекурсия, стандарт, автономный контур | Не базовая подписка |
| **Metrix Access** | **3 290 ₽ / мес** | Прежняя рублёвая дверь | Сигналы |
| **Custom spec pilot** | **45 000 ₽** | Именованная дыра, gate | Сигналы, доходность |
| **Cross assist** | **80 000 ₽** | Поиск среди предложенных | Седьмой продукт |
| **Main** | **$2490** | После названного пилота | Не входит в Allo |

Оплата — Tribute. Имя и телефон не храним. Игровой пакет изолирован и не открывает дверь Allo.

---

## Поверхности

| Поверхность | Где | Стек |
|---|---|---|
| Сайт | Vercel `public/` | статика HTML/CSS/JS |
| API | Railway | Python 3.12 · FastAPI |
| Бот + Mini App `/tg/` | Railway, если задан `TELEGRAM_BOT_TOKEN` | long poll рядом с API |
| Контуры (Client / Operator / Eval / Process / Cross) | `/app/contours/` и `/api/v1/contours/*` | JSON store в проде |

Режимы сайта: Продукты · Консультация · **Слоты** (третий режим: именованный объект, не to-do) · Сборка заказа · Разговор продажи · Фандинг.

Бот: Разговор · Стор · CraftShift · Хит · Дверь · `/cross`.

---

## Пять контуров

| ID | Контур | В проде |
|---|---|---|
| C1 | Process OS — заявка → хозяин → SLA → понедельник. OutcomeContract до Stage 1 | да |
| C2 | Eval Protocol (error / latency / cost / escalation) + Flight Recorder + kill-switch | да, eval на Access |
| C3 | On-prem pipeline (audit → air-gap/RAG → resilience → ERP → handover) | да |
| C4 | Compute broker (OpenAI-compatible proxy, маржа 40–60%) | флаг `ENABLE_COMPUTE_BROKER` (иначе 503) |
| C5 | Cold chain / telemetry, proof-of-condition | флаг `ENABLE_COLD_CHAIN` |

Локально: `docker-compose.local.yml` (API + Postgres + Redis + nginx). Прод Railway читает только `Dockerfile` + `railway.toml`.

---

## Quick start

```powershell
cd $env:USERPROFILE\Desktop\metrix-ai
pip install -r requirements.txt
python -m backend.main
```

- API: http://127.0.0.1:8787/
- Docs: http://127.0.0.1:8787/docs
- Health: http://127.0.0.1:8787/api/v1/health
- Сайт: http://127.0.0.1:8787/app/
- Mini App: http://127.0.0.1:8787/tg/

```text
POST /api/v1/process
{ "industry": "ai-agencies", "business": "что ломается, своими словами…", "track": "all" }

POST /api/v1/contours/cross
{ "text": "касса eval дверь" }

POST /api/v1/contours/eval/runs
{ "dataset_id": "ds_access_v1", "param_snapshot": { "engine": "orient-v1" } }
```

Бот локально: `TELEGRAM_BOT_TOKEN=… python -m telegram_app.bot`

Тесты: `pytest tests -q`

Деплой: push в `main`. Railway — API и бот. Vercel — `public/`. Автор коммита должен мапиться на GitHub-аккаунт `METRIXAI17` (noreply `297400418+METRIXAI17@users.noreply.github.com`), иначе Vercel на private-репо блокирует сборку. Подробности: `DEPLOY.md`.

---

## Каркас репозитория

```
metrix-ai/
├── public/                 # Vercel: сайт, /tg Mini App, /store, /craft, /contours
├── backend/
│   ├── main.py
│   ├── contours/           # C1–C5, Cross, Heavy Launch, spiritual library
│   ├── core/
│   │   ├── pure_vehicle/   # IN → OUT → REALIZE, OPS-7, FREE-12, Allo
│   │   └── …               # ориентация, store, door, Access
│   ├── paid/
│   ├── api/routes/
│   └── data/               # JSON store — секреты не коммитить
├── telegram_app/           # бот
├── robots/                 # paper по умолчанию: py -3 -m robots scan all
├── tests/
├── docs/
├── Dockerfile · railway.toml · vercel.json
└── docker-compose.local.yml
```

Ядро детерминированное: ориентация → зоны → финмодели → paid-core. LLM не обязателен. Не обещаем доходность и не шлём ордера на биржу.

Ценз продукта (тот же метод, что в `scripts/_count_ideas.py`): **922** дискретных юнита · **269** py-файлов бэкенда · **~63k** строк ядра.

---

## License

Personal-use, non-commercial — см. `LICENSE`. Коммерция только по отдельной лицензии у Karim Metrix.
