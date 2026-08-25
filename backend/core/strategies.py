"""Three named trading models. Models, not signals.

1. Target Place — gold: entry/exit as places
2. Demand — crypto: local names that fire inside a time window
3. Ampli — US: collect amplitude, do not predict direction
"""

from __future__ import annotations

import re
from typing import Any

from backend.core.resonance import new_id
from backend.core.voice import DISCLAIMER, clip, first_sentence


STRATEGIES: dict[str, dict[str, Any]] = {
    "target_place": {
        "id": "target_place",
        "name": "Target Place",
        "market": "золото",
        "market_en": "XAU",
        "accent": "#fbbf24",
        "one_liner": "Вход и выход — это места, не ощущения.",
        "for_whom": "Кто торгует золото и устал входить «потому что пошло».",
        "image": "/assets/x-posts/target-place-gold.jpg",
    },
    "demand": {
        "id": "demand",
        "name": "Demand",
        "market": "крипта",
        "market_en": "crypto",
        "accent": "#c4b5fd",
        "one_liner": "Сначала окно спроса, потом имя. Не наоборот.",
        "for_whom": "Кто смотрит местные истории, которые стреляют коротко.",
        "image": "/assets/x-posts/demand-crypto.jpg",
    },
    "ampli": {
        "id": "ampli",
        "name": "Ampli",
        "market": "Америка",
        "market_en": "US",
        "accent": "#38bdf8",
        "one_liner": "Собирает амплитуду. Направление не угадывает.",
        "for_whom": "Кто торгует американскую сессию и путает мнение с расширением диапазона.",
        "image": "/assets/x-posts/ampli-us.jpg",
    },
}


def list_strategies() -> list[dict[str, Any]]:
    return [dict(STRATEGIES[k]) for k in ("target_place", "demand", "ampli")]


def _has(text: str, *words: str) -> bool:
    low = (text or "").lower()
    return any(w.lower() in low for w in words)


def _places_from_brief(brief: str) -> list[str]:
    found: list[str] = []
    low = (brief or "").lower()
    catalog = [
        (r"pdh|вчерашн(ий|его) максимум|high дня", "вчерашний максимум — магнит, пока его не сняли"),
        (r"pdl|вчерашн(ий|его) минимум|low дня", "вчерашний минимум — зеркало магнита"),
        (r"недел|weekly", "недельный уровень — место, которое цена обязана навестить или отвергнуть"),
        (r"кругл|2000|2500|round", "круглая цифра — место толпы, не святое"),
        (r"asia|ази", "азиатский диапазон — происхождение европейского хода"),
        (r"london|лондон", "лондонский край — часто origin американского импульса"),
    ]
    for pat, line in catalog:
        if re.search(pat, low):
            found.append(line)
    if not found:
        found = [
            "магнит — куда цена хочет дойти (вчерашний край, равные максимумы, круглая)",
            "origin — откуда начался ход (край азии / лондона, зона дисбаланса)",
            "инвалидация — закрытие за местом, после которого тезис мёртв",
        ]
    return found[:3]


def _target_place(brief: str) -> dict[str, Any]:
    places = _places_from_brief(brief)
    chase = _has(brief, "догон", "фомо", "опоздал", "уже ушло", "вслед")
    title = "Target Place · карта мест"
    if chase:
        title = "Target Place · вы не в воздухе"
    return {
        "kind": "strategy.target_place",
        "title": title,
        "one_liner": "Золото работает местами. Между местами — воздух, там я не торгую.",
        "break": (
            "Вход «потому что пошло» — это не стратегия. "
            "Это реакция на чужой импульс. Target Place сначала отмечает места, потом ждёт цену."
        ),
        "move": (
            "Три типа мест: магнит (куда хотят дойти), origin (откуда ход), инвалидация (где тезис умирает). "
            "Вход только когда цена пришла в заранее отмеченное место и отвергла его — тень, вынос ликвидности, возврат. "
            "Выход: противоположный магнит, либо конец NY, если место не уважили."
        ),
        "steps": [
            "До сессии отметить 2–3 места. Не шесть. Не «посмотрим по рынку».",
            "Ждать прихода цены. Нет прихода — нет сделки. Скука разрешена.",
            "Факт отклонения от места. Без факта — нет входа, даже если «идеально выглядит».",
            "Размер от инвалидации, не от желания. Выход — место или время, не настроение.",
        ],
        "artifact_week": (
            "Лист на неделю: три места на золото с ролью (магнит / origin / инвалидация) "
            "и запрет входа между ними."
        ),
        "anti": [
            "Не входить в середине диапазона.",
            "Не усредняться без нового места.",
            "Не догонять импульс, который уже ушёл от места.",
        ],
        "places": places,
        "entry": "Цена в заранее отмеченном месте + факт отклонения.",
        "exit": "Противоположный магнит, либо time-stop на закрытии NY.",
        "invalidation": "Закрытие за местом, которое держало тезис.",
    }


def _demand(brief: str) -> dict[str, Any]:
    named = first_sentence(brief, "местный проект")
    has_name = _has(brief, "коин", "токен", "мем", "listing", "листинг", "unlock", "аирдроп")
    title = "Demand · окно, не монета"
    if has_name:
        title = "Demand · сначала окно"
    return {
        "kind": "strategy.demand",
        "title": title,
        "one_liner": "Местные истории стреляют во времени. Имя без окна — лотерея.",
        "break": (
            f"«{clip(named, 80)}» как ставка навсегда — плохая модель. "
            "Demand спрашивает: в каком окне здесь вообще есть спрос, который можно снять."
        ),
        "move": (
            "Собрать окно 24–72 часа вокруг катализатора: листинг, анлок, нарратив, тонкий стакан. "
            "Вход — когда спрос показывается внутри окна (держит уровень, есть объём, можно выйти). "
            "Выход — конец окна. Даже если «могло ещё». Идентичность к монете дороже волатильности."
        ),
        "steps": [
            "Записать окно до имени: с какого часа по какой, какой катализатор.",
            "Проверить, можно ли физически выйти: ликвидность, не свой же выход.",
            "Входить только если спрос уже виден в окне — не «накануне, вдруг стрельнет».",
            "На закрытии окна — выход по правилам, не по привязанности.",
        ],
        "artifact_week": (
            "Карточка окна: катализатор, часы, что считать появлением спроса, что считать смертью окна."
        ),
        "anti": [
            "Не держать через анлок «потому что сообщество верит».",
            "Не входить после 2–3x внутри того же окна — спрос уже снят.",
            "Не путать местный выстрел с «инвестицией в экосистему».",
        ],
        "window": "24–72 часа вокруг катализатора",
        "entry": "Спрос виден внутри окна (уровень + объём + возможность выхода).",
        "exit": "Конец окна или слом тезиса окна.",
        "invalidation": "Катализатор прошёл, спроса нет — окно мертво, имя неважно.",
    }


def _ampli(brief: str) -> dict[str, Any]:
    pred = _has(brief, "лонг", "шорт", "будет расти", "будет падать", "целью", "таргет")
    title = "Ampli · сборщик амплитуды"
    if pred:
        title = "Ampli · не направление"
    return {
        "kind": "strategy.ampli",
        "title": title,
        "one_liner": "Американская сессия платит за расширение диапазона. Не за мнение, куда пойдёт индекс.",
        "break": (
            "Люди торгуют Америку как прогноз. Ampli торгует как сбор амплитуды: "
            "сначала сжатие, потом выстрел диапазона, потом тишина — и я уже не здесь."
        ),
        "move": (
            "Сжатие: узкий opening range, inside, низкий ATR к своей норме. "
            "Зажигание: цена выходит из сжатия в кэш-сессию. Беру ту сторону, которая реально вышла. "
            "Съём: нет нового экстремума N минут, тянет к VWAP, амплитуда сдохла — плоско."
        ),
        "steps": [
            "Первые 30–45 минут: только метить сжатие. Не торговать мнение.",
            "Выход диапазона за край сжатия — это вход в сторону факта.",
            "Тянуть, пока амплитуда жива (новые края). Стоп — обратно внутрь сжатия.",
            "Смерть амплитуды = выход. Не «додержать до таргета из Твиттера».",
        ],
        "artifact_week": (
            "Журнал трёх сессий: было ли сжатие, куда расширились, когда амплитуда умерла, R."
        ),
        "anti": [
            "Не угадывать сторону сжатия заранее.",
            "Не сидеть через ланч, если диапазон уже умер.",
            "Не превращать сбор амплитуды в позиционный лонг/шорт на неделю.",
        ],
        "entry": "Факт расширения за край сжатия в US cash.",
        "exit": "Амплитуда не делает новый край / возврат в середину.",
        "invalidation": "Обратный заход внутрь сжатия — это не «ещё подождём».",
    }


_BUILDERS = {
    "target_place": _target_place,
    "demand": _demand,
    "ampli": _ampli,
}


def resolve_strategy(name: str | None, brief: str = "") -> str:
    key = (name or "").strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "gold": "target_place",
        "xau": "target_place",
        "золото": "target_place",
        "target": "target_place",
        "place": "target_place",
        "crypto": "demand",
        "крипта": "demand",
        "крипто": "demand",
        "us": "ampli",
        "america": "ampli",
        "америка": "ampli",
        "spy": "ampli",
        "nasdaq": "ampli",
    }
    if key in STRATEGIES:
        return key
    if key in aliases:
        return aliases[key]
    if _has(brief, "золот", "xau", "gold"):
        return "target_place"
    if _has(brief, "крипт", "мем", "токен", "listing", "анлок"):
        return "demand"
    if _has(brief, "америк", "nasdaq", "spy", "us500", "es "):
        return "ampli"
    return key if key in STRATEGIES else "target_place"


def run_strategy(name: str | None = None, brief: str = "") -> dict[str, Any]:
    sid = resolve_strategy(name, brief)
    meta = STRATEGIES[sid]
    body = _BUILDERS[sid](brief or "")
    art = {
        "id": new_id(),
        "kind": body["kind"],
        "lane": "strategy",
        "strategy_id": sid,
        "title": body["title"],
        "one_liner": body["one_liner"],
        "break": body["break"],
        "move": body["move"],
        "steps": body["steps"],
        "artifact_week": body["artifact_week"],
        "anti": body["anti"],
        "meta": {
            "name": meta["name"],
            "market": meta["market"],
            "accent": meta["accent"],
            "entry": body.get("entry"),
            "exit": body.get("exit"),
            "invalidation": body.get("invalidation"),
            "places": body.get("places"),
            "window": body.get("window"),
        },
        "disclaimer": DISCLAIMER,
        "highway": {
            "free": "эта карта как демо",
            "paid": "посадка модели в ваш журнал и правила на 14 дней",
            "sku": "request_deep",
        },
        "brief": clip(brief, 400),
    }
    return art
