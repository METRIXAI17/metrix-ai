# Metrix Access · 3 290 ₽ — продажи

Движок на контуре KARIM METRIX (2026-09-03): compatibility 0.78, **void_membrane unbound**, circle assembly 0.44, **Main закрыт** (risk high). Две лестницы цен ломали revenue_hinge. Исправление: один публичный SKU.

## Что продаём сейчас

| SKU | Цена | Что |
|---|---|---|
| **Metrix Access** | **3 290 ₽ / мес** | Chain + Teammates + Artefacts, 4 модели, риск-движок |
| Access год | 32 900 ₽ | 10 месяцев |
| Custom Teammate | $500 | не Access |
| Tape Land / Full Package | от $2 490 | только после пилота, **не** эта подписка |

Не входит в Access: сигналы, Main без пилота, Custom, Tape Land.

Net Tribute 10% ≈ **2 961 ₽**. Два бесплатных прогона, потом стена.

## Готовность

| Слой | Статус |
|---|---|
| Код, бот, Mini App, `/chain/` | готов, цена 3290 |
| Копирайт who/void/gate/price/not | готов |
| HMAC, без анкеты | готов в коде |
| Tribute продукт 3290 + webhook | **не готов, пока не заведёте** |
| Main $2490 как массовый SKU | **закрыт движком** |

Копия продаётся. Живые платежи — после Tribute.

## Дальше, по порядку

1. Tribute → продукт **Metrix Access**, 3 290 ₽ / месяц (рекуррент). Год — 32 900 ₽, отдельно.
2. Railway Variables: `TRIBUTE_ACCESS_URL`, `TRIBUTE_API_KEY`, `METRIX_TOKEN_SECRET` (длинный random).
3. Webhook: `https://metrix-ai-production.up.railway.app/api/v1/miniapp/tribute/webhook`
4. Проверка: `/api/v1/analytics/sales-readiness` — `tribute_url` и `token_secret` должны стать true.
5. Два своих прогона в боте → на третьем стена 3 290 ₽.
6. Пост @karimmetrix: цена 3 290 ₽, не сигналы, ссылка `/chain/`.
7. Не продавать Main как Access. Custom — кнопка «человек».

Проверка готовности: `GET /api/v1/analytics/sales-readiness`
