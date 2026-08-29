"""Translate abstraction into cards with functional designations.

The essay is the first language. The card is the second: a function
with a code, an object, an action, a money unit and a kill.

This is the «усовершенствованный перевод» — not a summary of the essay,
a designation of what the engine is allowed to do.
"""

from __future__ import annotations

from typing import Any


CARD_SPECS: list[dict[str, Any]] = [
    {
        "code": "FN-ARCH",
        "designation": "archetype_lock",
        "layer": "closer",
        "need": lambda v, _t: True,
    },
    {
        "code": "FN-MOVE",
        "designation": "movement_unit",
        "layer": "closer",
        "need": lambda v, _t: True,
    },
    {
        "code": "FN-BIN",
        "designation": "binary_dissolve",
        "layer": "closer",
        "need": lambda v, _t: v.get("binary_trap", 0) >= 0.2 or v.get("state_seeking", 0) >= 0.3,
    },
    {
        "code": "FN-LAND",
        "designation": "event_entry",
        "layer": "closer",
        "need": lambda _v, _t: True,
    },
    {
        "code": "FN-GROW",
        "designation": "growth_point",
        "layer": "growth",
        "need": lambda _v, _t: True,
    },
    {
        "code": "FN-IDEA",
        "designation": "idea_object",
        "layer": "trade",
        "need": lambda _v, _t: True,
    },
    {
        "code": "FN-WARM",
        "designation": "founder_warm",
        "layer": "closer",
        "need": lambda v, t: v.get("resistance", 0) >= 0.2 or any(
            k in t for k in ("страх", "фаундер", "прогрев", "twitter", "телег")
        ),
    },
    {
        "code": "FN-FEAR",
        "designation": "structure_fear_kill",
        "layer": "closer",
        "need": lambda v, t: v.get("money_structure", 0) >= 0.2 or v.get("resistance", 0) >= 0.35 or any(
            k in t for k in ("страх", "фин", "выруч", "структур", "касс")
        ),
    },
    {
        "code": "FN-UNIT",
        "designation": "money_unit",
        "layer": "growth",
        "need": lambda _v, _t: True,
    },
    {
        "code": "FN-FEE",
        "designation": "success_share",
        "layer": "growth",
        "need": lambda v, t: v.get("money_structure", 0) >= 0.15 or True,
    },
    {
        "code": "FN-TREND",
        "designation": "screened_trend_adapt",
        "layer": "growth",
        "need": lambda _v, _t: True,
    },
    {
        "code": "FN-SAT",
        "designation": "satellite_arb",
        "layer": "trade",
        "need": lambda v, t: v.get("crowd_noise", 0) >= 0.2 or any(
            k in t for k in ("трафик", "лид", "арбитраж", "реклам", "телег", "twitter")
        ),
    },
    {
        "code": "FN-CLOSE",
        "designation": "integration_close",
        "layer": "closer",
        "need": lambda _v, _t: True,
    },
    {
        "code": "FN-MAKE",
        "designation": "making_gate",
        "layer": "trade",
        "need": lambda _v, _t: True,
    },
    {
        "code": "FN-KILL",
        "designation": "invalidation",
        "layer": "closer",
        "need": lambda _v, _t: True,
    },
]


def _quote(essay: str, *needles: str) -> str:
    if not essay:
        return ""
    low = essay.lower()
    for n in needles:
        i = low.find(n.lower())
        if i >= 0:
            start = max(0, essay.rfind(".", 0, i) + 1)
            end = essay.find(".", i)
            if end < 0:
                end = min(len(essay), i + 140)
            return " ".join(essay[start:end].strip().split())
    # fallback: first sentence
    end = essay.find(".")
    return " ".join((essay[: end if end > 20 else 160]).split())


def _fill(
    spec: dict[str, Any],
    *,
    brief: str,
    essay: dict[str, Any],
    event: dict[str, Any],
    trends: dict[str, Any],
    vectors: dict[str, float],
    lang: str,
) -> dict[str, Any]:
    ru = not (lang or "").startswith("en")
    code = spec["code"]
    arch = essay.get("archetype") or "Живое движение"
    sit = essay.get("situation_object") or "ситуация"
    binaries = essay.get("binaries") or []
    bin_txt = ", ".join(f"{b.get('a')} / {b.get('b')}" for b in binaries[:3]) or "работа / отдых"
    ev_title = (event or {}).get("title") or "вход в комнату"
    trend = (trends or {}).get("primary") or {}
    trend_name = trend.get("name_ru") or trend.get("name_en") or "движение"
    trend_adapt = trend.get("adapt") or ""
    text_essay = essay.get("essay") or ""

    table: dict[str, dict[str, str]] = {
        "FN-ARCH": {
            "poetic": arch,
            "function": "lock_figure",
            "object": "founder_as_figure",
            "action": (
                f"зафиксировать фигуру «{arch}» как вход в комнату, не как диагноз личности"
                if ru
                else f"lock figure «{arch}» as room entry, not a personality diagnosis"
            ),
            "unit": "одна фигура на событие",
            "kill": "если фигура становится ролью в оргсхеме — карта умирает",
            "money": "фигура не продаётся; продаётся движение, которое она выдерживает",
            "source": _quote(text_essay, arch.split()[0], "Деятель", "Менеджер"),
        },
        "FN-MOVE": {
            "poetic": "Движение без состояния",
            "function": "kill_state_seeking",
            "object": "goal_as_place",
            "action": (
                f"заменить стремление «закрыть: {sit}» на единицу движения, которую можно повторить на этой неделе"
                if ru
                else f"replace arriving at «{sit}» with a repeatable movement unit"
            ),
            "unit": "один повторённый жест, не одно достигнутое настроение",
            "kill": "если артефакт обещает новую жизнь / новый я — вырезать",
            "money": "платить за жест, который случился, не за состояние, в которое верят",
            "source": _quote(text_essay, "состояни", "смерти", "движение разрушает"),
        },
        "FN-BIN": {
            "poetic": f"Снятие антагонистов · {bin_txt}",
            "function": "dissolve_binary",
            "object": "false_antagonists",
            "action": (
                f"разрушить пару {bin_txt} в тексте события — оставить только как двигалось"
                if ru
                else f"dissolve {bin_txt}; keep only how it moved"
            ),
            "unit": "одна разрушенная пара понятий за событие",
            "kill": "если лендинг снова ставит «успех vs провал» — переписать",
            "money": "антагонисты не монетизируются; монетизируется выход из них",
            "source": _quote(text_essay, "антагонист", "понятие", "работа"),
        },
        "FN-LAND": {
            "poetic": ev_title,
            "function": "enter_event",
            "object": "landing_as_room",
            "action": (
                "собрать лендинг как видение события: кто входит, что движется, что стоит. Не кнопка «студия»."
                if ru
                else "compose landing as event vision: who enters, what moves, what stays. Not a studio button."
            ),
            "unit": "один вход в комнату",
            "kill": "если есть hero-CTA «начать» / «купить» / «запустить ROI» — это страница, не событие",
            "money": "вход бесплатен; share начинается после изменения структуры",
            "source": _quote(text_essay, "Комната", "играть", "узкому кругу"),
        },
        "FN-GROW": {
            "poetic": "Точка роста без масштаба",
            "function": "name_growth_point",
            "object": "narrow_circle",
            "action": (
                f"назвать одну точку, где «{sit}» уже движется — не ту, где хочется, чтобы двигалось"
                if ru
                else f"name one point where «{sit}» already moves"
            ),
            "unit": "одна точка на неделю",
            "kill": "если точек больше трёх — это backlog, не рост",
            "money": "рост = изменение единицы выручки на этой точке, не headcount",
            "source": _quote(text_essay, "узком", "кругу", "обстоятельства"),
        },
        "FN-IDEA": {
            "poetic": "Идея как объект на столе",
            "function": "materialize_idea",
            "object": "derivative_product",
            "action": (
                f"положить на стол производный продукт под тренд «{trend_name}», адаптированный под проект клиента"
                if ru
                else f"put a derivative product for trend «{trend_name}» on the table"
            ),
            "unit": "один объект, который можно взять в мейкинг",
            "kill": "если идея требует «ещё подумать» — это не объект",
            "money": "идея бесплатна; мейкинг объекта — share",
            "source": _quote(text_essay, "образы", "сделать ровно"),
        },
        "FN-WARM": {
            "poetic": "Прогрев без воронки",
            "function": "warm_founder",
            "object": "trust_mindset",
            "action": (
                "X + Telegram: 5 касаний инверсией, не аргументом. Сначала trust, потом структура."
                if ru
                else "X + Telegram: 5 inversion touches, not arguments."
            ),
            "unit": "одно касание = одна инверсия, без CTA",
            "kill": "если в касании есть «ROI / гарантия / успех» — сжечь черновик",
            "money": "прогрев не продаёт; он снимает необходимость сопротивляться",
            "source": _quote(text_essay, "плохо тогда", "мешают", "Нечему"),
        },
        "FN-FEAR": {
            "poetic": "Страх перед сменой финструктуры",
            "function": "dissolve_structure_fear",
            "object": "old_revenue_shape",
            "action": (
                "назвать страх: если поменять структуру, умрёт то, что кормит сейчас. "
                "Инверсия: текущая структура уже состояние, значит уже немного мертва."
                if ru
                else "name the fear: changing structure kills what feeds you now. Inversion: the current structure is already a state, hence already dying."
            ),
            "unit": "один названный страх + один жест, который остаётся живым",
            "kill": "если в ответ просят оргсхему на 40 страниц — стоп",
            "money": "менять одну денежную единицу, остальное пусть движется",
            "source": _quote(text_essay, "стремиться к смерти", "состояни"),
        },
        "FN-UNIT": {
            "poetic": "Единица, за которую стыдно, если сломается",
            "function": "name_money_unit",
            "object": "revenue_gesture",
            "action": (
                f"вынуть из «{sit}» один жест, который уже приносит деньги — и сделать его единицей share"
                if ru
                else f"extract one money gesture from «{sit}» and make it the share unit"
            ),
            "unit": "один жест выручки",
            "kill": "если единица = «час» или «подписка на доступ» — пересобрать",
            "money": "единица делима; час — нет",
            "source": _quote(text_essay, "значение", "бессмысленно"),
        },
        "FN-FEE": {
            "poetic": "Комиссия за рост",
            "function": "success_fee_geometry",
            "object": "share_of_movement",
            "action": (
                "success fee / share model: доля с изменённой структуры выручки, не ретейнер за присутствие"
                if ru
                else "success fee / share of changed revenue structure, not a retainer"
            ),
            "unit": "доля с движения, которое случилось",
            "kill": "если fee берётся до изменения структуры — это аренда тревоги",
            "money": trend_adapt or "share after structure_first",
            "source": _quote(text_essay, "Нечему сопротивляться", "обстоятельства"),
        },
        "FN-TREND": {
            "poetic": trend_name,
            "function": "adapt_screened_trend",
            "object": "client_project",
            "action": (
                f"адаптировать наскриненный тренд «{trend_name}» под проект клиента: {trend_adapt}"
                if ru
                else f"adapt screened trend «{trend_name}» to the client project"
            ),
            "unit": "один тренд → один производный объект",
            "kill": "если тренд читается как торговый сигнал — вырезать",
            "money": trend.get("crypto_rhyme") or "движение, не ставка",
            "source": trend.get("why") or "",
        },
        "FN-SAT": {
            "poetic": "Бот-сателлит",
            "function": "arbitrate_attention",
            "object": "traffic_to_event",
            "action": (
                "сателлит носит внимание к событию, не к бренду. Спред между вниманием и входом."
                if ru
                else "satellite carries attention to the event, not the brand"
            ),
            "unit": "один канал → одно событие",
            "kill": "если сателлит ведёт на каталог услуг — это реклама, не арбитраж",
            "money": "платить за вход в событие, который состоялся",
            "source": _quote(text_essay, "самолёт", "полный"),
        },
        "FN-CLOSE": {
            "poetic": "Закрытие на интеграцию",
            "function": "close_into_integration",
            "object": "client_contour",
            "action": (
                "автозакрытие проекта на интеграцию через верхний модуль движка: "
                "не «купить доступ», а сесть в контур на share"
                if ru
                else "auto-close into integration: sit in the contour on share, don't sell access"
            ),
            "unit": "одна посадка, один share",
            "kill": "если close = подписка «на всякий случай» — мимо",
            "money": "пилот 14 дней сажает уже зашедший артефакт",
            "source": _quote(text_essay, "играть", "не надо"),
        },
        "FN-MAKE": {
            "poetic": "Камера сборки",
            "function": "weave_week",
            "object": "making_chamber",
            "action": (
                "мейкинг ткёт абстракцию + карточки + промпт + тренд в неделю, которую можно прожить. Не план."
                if ru
                else "making weaves abstraction + cards + prompt + trend into a week you can live. Not a plan."
            ),
            "unit": "7 дней, день 1 = вход в событие",
            "kill": "если день 1 = «исследование» — камера пуста",
            "money": "сборка оплачивается share после дня 6, если структура сдвинулась",
            "source": _quote(text_essay, "обстоятельства меняются", "И всё"),
        },
        "FN-KILL": {
            "poetic": "Смерть тезиса",
            "function": "invalidate",
            "object": "this_pack",
            "action": (
                "пакет умирает, если: обещает состояние, продаёт сигналы, плодит объекты, "
                "или просит влезть в невозможное"
                if ru
                else "pack dies if it promises a state, sells signals, spawns objects, or climbs the impossible"
            ),
            "unit": "одно явное условие смерти",
            "kill": "карта, которая не умеет умереть, не является функцией",
            "money": "нет денег за мёртвый пакет",
            "source": _quote(text_essay, "невозможн", "личную силу", "смерти"),
        },
    }
    body = table[code]
    return {
        "code": code,
        "designation": spec["designation"],
        "layer": spec["layer"],
        "poetic_name": body["poetic"],
        "function": body["function"],
        "object": body["object"],
        "action": body["action"],
        "unit": body["unit"],
        "kill": body["kill"],
        "money": body["money"],
        "source_span": body["source"],
        "task": f"[{code} · {spec['designation']}] {body['action']}",
    }


def translate_cards(
    *,
    brief: str,
    essay: dict[str, Any],
    event: dict[str, Any],
    trends: dict[str, Any],
    vectors: dict[str, float],
    lang: str = "ru",
) -> dict[str, Any]:
    t = (brief or "").lower()
    cards: list[dict[str, Any]] = []
    skipped: list[str] = []
    for spec in CARD_SPECS:
        if spec["need"](vectors, t):
            cards.append(
                _fill(
                    spec,
                    brief=brief,
                    essay=essay,
                    event=event,
                    trends=trends,
                    vectors=vectors,
                    lang=lang,
                )
            )
        else:
            skipped.append(spec["code"])

    codes = {c["code"] for c in cards}
    # hard rails: some cards must exist even if need() was shy
    required = {"FN-ARCH", "FN-MOVE", "FN-LAND", "FN-UNIT", "FN-KILL", "FN-MAKE", "FN-TREND"}
    missing_required = sorted(required - codes)

    conflicts: list[dict[str, str]] = []
    actions = [c["action"].lower() for c in cards]
    if any("новую жизнь" in a or "new identity" in a for a in actions):
        conflicts.append({"a": "FN-MOVE", "b": "copy", "why": "state-seeking leaked into action"})
    if any("сигнал" in (c.get("money") or "").lower() and c["code"] == "FN-TREND" for c in cards):
        conflicts.append({"a": "FN-TREND", "b": "FN-KILL", "why": "trend reads as a signal"})

    return {
        "module": "FunctionCards",
        "version": "1.0.0",
        "count": len(cards),
        "items": cards,
        "codes": [c["code"] for c in cards],
        "skipped": skipped,
        "missing_required": missing_required,
        "conflicts": conflicts,
        "task_block": "\n".join(c["task"] for c in cards),
        "message": f"Карточки · {len(cards)} функций",
    }


def cards_as_table(cards: list[dict[str, Any]]) -> str:
    lines = []
    for c in cards:
        lines.append(
            f"{c['code']}  {c['designation']}\n"
            f"  {c['poetic_name']}\n"
            f"  fn={c['function']}  obj={c['object']}\n"
            f"  {c['action']}\n"
            f"  unit: {c['unit']}\n"
            f"  kill: {c['kill']}"
        )
    return "\n\n".join(lines)
