"""GROWTH AI — trend screener (business-crypto), not signals.

A trend here is a movement that can be productized into a client's
derivative — not a ticker, not a call. The closer adapts the screened
trend to the task-card that came from the abstract idea.
"""

from __future__ import annotations

import hashlib
from typing import Any


def _seed(text: str) -> int:
    return int(hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:10], 16)


TRENDS: list[dict[str, Any]] = [
    {
        "id": "share_over_retainer",
        "layer": "growth",
        "name_ru": "Доля с движения вместо ретейнера",
        "name_en": "Share of movement instead of retainer",
        "family": "success_fee",
        "why": "фаундер платит за изменённую финструктуру, не за часы присутствия",
        "adapt": "success fee / share model на единицу изменённой выручки",
        "crypto_rhyme": "не ставка на монету — доля с потока, который уже пошёл",
        "keys": ("комисс", "ретейнер", "подписк", "fee", "долю", "оплат", "касса", "марж"),
    },
    {
        "id": "local_demand_window",
        "layer": "trade",
        "name_ru": "Короткое окно местного спроса",
        "name_en": "Short local demand window",
        "family": "demand",
        "why": "сначала окно, потом имя. Местная история, короткий выстрел.",
        "adapt": "производный оффер живёт 3–9 дней, потом умирает сам",
        "crypto_rhyme": "Demand: местный листинг как культурное окно, не как сигнал",
        "keys": ("крипт", "мем", "листин", "окно", "спрос", "demand", "local"),
    },
    {
        "id": "derivative_of_client",
        "layer": "trade",
        "name_ru": "Производный продукт чужого проекта",
        "name_en": "Derivative of a client's project",
        "family": "derivative",
        "why": "не новый бренд — надстройка над тем, что у клиента уже движется",
        "adapt": "генератор продуктов под найденный тренд, адаптированный под проект клиента",
        "crypto_rhyme": "дериватив не торгует базу — он торгует форму базы",
        "keys": ("клиент", "проект", "агентств", "white-label", "под ключ", "интеграц"),
    },
    {
        "id": "satellite_arb",
        "layer": "trade",
        "name_ru": "Сателлит трафика и арбитража",
        "name_en": "Traffic-arbitrage satellite",
        "family": "satellite",
        "why": "бот-сателлит носит трафик к событию, не к «бренду»",
        "adapt": "арбитраж внимания: дешёвый вход в событие, не в лендинг-каталог",
        "crypto_rhyme": "спред между вниманием и событием, не между двумя биржами",
        "keys": ("трафик", "арбитраж", "лид", "telegram", "twitter", "x.com", "реклам"),
    },
    {
        "id": "event_not_page",
        "layer": "closer",
        "name_ru": "Лендинг как видение события",
        "name_en": "Landing as event vision",
        "family": "landing",
        "why": "страница больше не продаёт. Продаёт вход в комнату, где уже идёт событие.",
        "adapt": "landing studio вместо кнопки «студия»: событие, не сайт",
        "crypto_rhyme": "listing event > listing page",
        "keys": ("лендинг", "запуск", "ивент", "событ", "вебинар", "комнат", "вход"),
    },
    {
        "id": "founder_warmth",
        "layer": "closer",
        "name_ru": "Прогрев фаундера как trust, не как воронка",
        "name_en": "Founder warmth as trust, not funnel",
        "family": "warm",
        "why": "страх перед сменой финструктуры снимается инверсией, не аргументом ROI",
        "adapt": "X + Telegram: прогрев mindset, затем close на интеграцию",
        "crypto_rhyme": "холд через доверие к движению, не через обещание лампы",
        "keys": ("страх", "фаундер", "довер", "прогрев", "twitter", "телеграм", "mindset"),
    },
    {
        "id": "structure_first_capital",
        "layer": "growth",
        "name_ru": "Сначала структура выручки, потом капитал",
        "name_en": "Revenue structure first, capital second",
        "family": "fin_eng",
        "why": "фин. инженерия читает, из каких жестов состоит выручка — и только потом share",
        "adapt": "разбор структуры выручки → одна единица, которую можно делить",
        "crypto_rhyme": "TVL без структуры — пустой бассейн",
        "keys": ("выручк", "структур", "фин", "unit", "юнит", "капитал", "инвест"),
    },
    {
        "id": "attention_as_working_capital",
        "layer": "growth",
        "name_ru": "Внимание как оборотный капитал",
        "name_en": "Attention as working capital",
        "family": "attention",
        "why": "не аудитория. Оборот: внимание входит, событие происходит, остаток уходит в share",
        "adapt": "контент-стратегия как касса внимания, не как блог",
        "crypto_rhyme": "liquidity of attention, not followers",
        "keys": ("аудитор", "подпис", "контент", "пост", "х", "twitter", "вниман"),
    },
    {
        "id": "auto_close_integration",
        "layer": "closer",
        "name_ru": "Автозакрытие на интеграцию",
        "name_en": "Auto-close into integration",
        "family": "close",
        "why": "close — не «купить доступ». Close — сесть в контур клиента на share",
        "adapt": "верхний модуль движка: студия точек роста → интеграция без театра внедрения",
        "crypto_rhyme": "listing is the close; the token is the integration",
        "keys": ("интеграц", "внедр", "пилот", "посадк", "close", "сделк"),
    },
]


def screen_trends(
    brief: str,
    vectors: dict[str, float] | None = None,
    *,
    limit: int = 3,
) -> dict[str, Any]:
    """Screen 1–3 live movements that can be implemented for this brief."""
    t = (brief or "").lower()
    vec = vectors or {}
    ranked: list[tuple[float, dict[str, Any]]] = []
    for tr in TRENDS:
        score = 0.18
        score += 0.22 * sum(1 for k in tr["keys"] if k in t)
        # vector boosts
        if tr["family"] == "success_fee":
            score += 0.35 * vec.get("money_structure", 0)
        if tr["family"] == "warm":
            score += 0.3 * vec.get("resistance", 0)
        if tr["family"] == "landing":
            score += 0.2
        if tr["family"] == "derivative":
            score += 0.25 * vec.get("object_glut", 0)
        if tr["family"] == "satellite":
            score += 0.2 * vec.get("crowd_noise", 0)
        if tr["family"] == "fin_eng":
            score += 0.33 * vec.get("money_structure", 0)
        if tr["family"] == "demand":
            score += 0.2 * (1.0 if any(k in t for k in ("крипт", "мем", "золот", "окно")) else 0.0)
        score += (_seed(t + tr["id"]) % 9) / 80.0
        ranked.append((score, tr))
    ranked.sort(key=lambda x: -x[0])
    picked = []
    for sc, tr in ranked[: max(1, limit)]:
        picked.append({**tr, "score": round(sc, 3), "screened": True})
    primary = picked[0]
    return {
        "module": "TrendScreener",
        "version": "1.0.0",
        "layer": "GROWTH AI",
        "disclaimer": "Тренд как культурное движение, не торговый сигнал.",
        "primary": primary,
        "items": picked,
        "board": [
            {"id": tr["id"], "name_ru": tr["name_ru"], "score": round(sc, 3)}
            for sc, tr in ranked
        ],
        "message": f"Скринер · {primary['name_ru']}",
    }
