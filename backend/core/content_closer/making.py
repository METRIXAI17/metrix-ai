"""Making chamber — last of three bot sections. New Metrix function.

Not a plan. Not a Gantt. A week that can be lived.

Invented function: weave abstraction + function cards + rewritten prompt
+ screened trend into a material week:

  day 1  enter the event (landing published as a living post, not a website)
  day 2–3  warm founders on X and Telegram (inversion, no CTA)
  day 4  fear protocol — 20 min, no pitch
  day 5  show the card table, not the deck
  day 6  close into integration on success-fee geometry
  day 7  satellite starts traffic toward the event, not the brand

Gates: cannot make without cards, event, and a rewritten prompt.
Day 1 must be event entry — never «research».
"""

from __future__ import annotations

from typing import Any

from backend.core.resonance import new_id
from backend.core.voice import DISCLAIMER


class MakingRefused(ValueError):
    """Chamber is empty — the landing has not been entered."""


def _codes(cards: dict[str, Any] | list | None) -> set[str]:
    if isinstance(cards, dict):
        items = cards.get("items") or []
    else:
        items = cards or []
    return {c.get("code") for c in items if isinstance(c, dict)}


def _card(cards: dict[str, Any], code: str) -> dict[str, Any]:
    for c in cards.get("items") or []:
        if c.get("code") == code:
            return c
    return {}


def run_making_chamber(
    closer: dict[str, Any],
    *,
    extra: str = "",
    lang: str = "ru",
) -> dict[str, Any]:
    ru = not (lang or "").lower().startswith("en")
    if not closer:
        raise MakingRefused(
            "Камера пуста. Сначала войдите в событие на лендинге."
            if ru
            else "Chamber is empty. Enter the event on the landing first."
        )
    cards = closer.get("cards") or {}
    event = closer.get("event") or {}
    prompt = closer.get("prompt") or {}
    essay = closer.get("abstraction") or {}
    trends = closer.get("trends") or {}
    codes = _codes(cards)

    missing = [k for k in ("FN-MAKE", "FN-LAND", "FN-UNIT") if k not in codes]
    if len(cards.get("items") or []) < 4:
        raise MakingRefused(
            "Мало карточек для сборки. Вернитесь на лендинг и войдите ещё раз."
            if ru
            else "Not enough cards. Enter the landing again."
        )
    if not event.get("title"):
        raise MakingRefused(
            "Нет видения события. Лендинг ещё не собрал комнату."
            if ru
            else "No event vision. The landing has not built the room."
        )
    if not prompt.get("master") and not prompt.get("engine_brief"):
        raise MakingRefused(
            "Нет промпта для основного движка. Карточки ещё не переписаны."
            if ru
            else "No engine prompt. Cards have not been rewritten."
        )

    trend = trends.get("primary") or {}
    arch = essay.get("archetype") or event.get("archetype") or ""
    title = event.get("title")
    unit_card = _card(cards, "FN-UNIT")
    fee_card = _card(cards, "FN-FEE")
    fear_card = _card(cards, "FN-FEAR")
    sat_card = _card(cards, "FN-SAT")
    warm_card = _card(cards, "FN-WARM")

    extra_note = " ".join((extra or "").split())[:240]

    calendar = [
        {
            "day": 1,
            "id": "D1_ENTER",
            "title": "Вход в событие" if ru else "Enter the event",
            "do": (
                f"Опубликовать видение «{title}» как живой пост (Telegram + X), не как сайт. "
                f"Приглашение: {event.get('invitation')}"
            ),
            "kill": "если день 1 = исследование / бриф / созвон — камера пуста",
        },
        {
            "day": 2,
            "id": "D2_WARM_X",
            "title": "Прогрев X",
            "do": (
                (warm_card.get("action") or "Касание-инверсия на X без CTA.")
                + " Черновик 1: инверсия состояний. Черновик 2: узкий круг действий."
            ),
            "kill": "ROI, гарантия, «успех» в черновике — сжечь",
        },
        {
            "day": 3,
            "id": "D3_WARM_TG",
            "title": "Прогрев Telegram",
            "do": (
                "Три сообщения в узкий круг: (1) фигура, (2) что движется, (3) что стоит. "
                "Без кнопки оплаты."
            ),
            "kill": "если появляется каталог услуг — это реклама",
        },
        {
            "day": 4,
            "id": "D4_FEAR",
            "title": "Протокол страха",
            "do": fear_card.get("action")
            or (
                "20 минут. Назвать страх смены финструктуры. Инверсия вслух. Без питча."
            ),
            "kill": "оргсхема, 40 страниц, «давайте сначала стратегию» — стоп",
        },
        {
            "day": 5,
            "id": "D5_TABLE",
            "title": "Стол с карточками",
            "do": (
                f"Показать стол: {', '.join(sorted(codes))}. "
                "Не колоду слайдов. Каждая карта — функция, не мнение."
            ),
            "kill": "если показывают презентацию вместо стола — вернуть в комнату",
        },
        {
            "day": 6,
            "id": "D6_CLOSE",
            "title": "Закрытие на интеграцию",
            "do": (
                (fee_card.get("action") or "success fee / share с изменённой структуры.")
                + " Посадка в контур клиента на 14 дней того артефакта, который уже зашёл."
            ),
            "kill": "fee до сдвига структуры = аренда тревоги",
        },
        {
            "day": 7,
            "id": "D7_SAT",
            "title": "Сателлит",
            "do": sat_card.get("action")
            or (
                f"Сателлит несёт внимание к событию «{title}», не к бренду. "
                f"Тренд: {trend.get('name_ru') or ''}."
            ),
            "kill": "если ведёт на каталог — выключить сателлит",
        },
    ]
    if extra_note:
        calendar[4]["do"] += f" Учесть: {extra_note}"

    warm_x = [
        {
            "n": 1,
            "channel": "x",
            "line": f"{arch}. Стремиться к состоянию — значит стремиться к смерти.",
        },
        {
            "n": 2,
            "channel": "x",
            "line": "Тебе плохо тогда, когда ты думаешь, что тебе хорошо. И наоборот. Не мотивация — геометрия.",
        },
        {
            "n": 3,
            "channel": "x",
            "line": f"Событие: {title}. Не кнопка. Комната.",
        },
        {
            "n": 4,
            "channel": "x",
            "line": f"Тренд, который сажаем в проект: {trend.get('name_ru')}. Не сигнал.",
        },
        {
            "n": 5,
            "channel": "x",
            "line": "Образы не имеют смысла. Ты всё равно продолжаешь играть. Узкий круг — или ничего.",
        },
    ]
    warm_tg = [
        {
            "n": 1,
            "channel": "telegram",
            "line": f"Фигура в комнате — {arch}. Можно сесть.",
        },
        {
            "n": 2,
            "channel": "telegram",
            "line": event.get("what_moves") or "Движется только то, что уже может.",
        },
        {
            "n": 3,
            "channel": "telegram",
            "line": event.get("what_stays") or "Стоит узкий круг. Стоит kill.",
        },
        {
            "n": 4,
            "channel": "telegram",
            "line": "Если страшно менять финструктуру — так и есть. Текущая уже состояние, значит уже немного мертва.",
        },
        {
            "n": 5,
            "channel": "telegram",
            "line": "Закрытие не «доступ». Закрытие — посадка в контур на share.",
        },
    ]

    fin = {
        "before": "выручка как туман: часы, подписка, «за присутствие», без жеста, который стыдно сломать",
        "after": unit_card.get("action")
        or "один жест выручки = единица share; остальная структура движется как шла",
        "fear_protocol": {
            "name": "страх смерти старой кассы",
            "say": fear_card.get("action")
            or "если поменять структуру, умрёт то, что кормит сейчас",
            "inversion": "текущая структура уже состояние, значит уже стремится к смерти",
            "gesture": "сменить одну единицу, не всё сразу",
            "minutes": 20,
            "no_pitch": True,
        },
        "success_fee": {
            "model": "success_fee_share",
            "on": "изменённая структура выручки (жест, который случился)",
            "not_on": "часы, доступ, подписка «на всякий случай»",
            "gate": "fee только после дня 6, если структура сдвинулась",
            "kill": fee_card.get("kill") or "fee до сдвига = аренда тревоги",
        },
    }

    derivative = {
        "name": f"Производная · {trend.get('name_ru') or title}",
        "from_trend": trend.get("id"),
        "adapted_to": closer.get("brief") or extra_note or event.get("title"),
        "what": trend.get("adapt")
        or "надстройка над движением клиента, не новый бренд",
        "object": _card(cards, "FN-IDEA").get("action")
        or "один объект на столе, который можно взять",
    }

    satellite = {
        "name": "бот-сателлит",
        "carries": "внимание → событие",
        "not": "внимание → бренд / каталог",
        "trend": trend.get("id"),
        "brief": sat_card.get("action")
        or f"Арбитраж внимания к «{title}». Спред между касанием и входом.",
        "kill": "каталог услуг на выходе",
    }

    close_script = {
        "say": (
            f"Артефакт «{title}» уже в комнате. Если зашёл — сажаем его в ваш контур на 14 дней. "
            "Оплата: доля с жеста выручки, который сдвинется. Не ретейнер."
        ),
        "if_almost": "одной фразой, чего не хватает — камера собирает вторую неделю, не новый продукт",
        "if_miss": "не тянуть. Другая дверь: лендинг ещё раз, или тишина.",
        "integration": "верхний модуль движка (Тихий) остаётся сидеть в контуре как точка роста, не как чат",
    }

    making_id = new_id()
    pack = {
        "id": making_id,
        "kind": "making.chamber",
        "lane": "making",
        "function": "making_chamber",
        "title": f"Мейкинг · {title}",
        "one_liner": "Неделя, которую можно прожить. Не план.",
        "break": (
            "Обычно после идеи начинают исследовать, собирать слайды и нанимать. "
            "Это стремление к состоянию. Камера так не собирает."
        ),
        "move": (
            "Нестандартный ход: день 1 = вход в событие. "
            "Карточки уже есть. Промпт уже переписан под тренд. "
            "Мейкинг только ткёт неделю."
        ),
        "steps": [f"День {d['day']}: {d['title']} — {d['do']}" for d in calendar],
        "artifact_week": (
            f"Семь дней вокруг «{title}». "
            "Прогрев X/TG, протокол страха, стол карточек, close на share, сателлит."
        ),
        "anti": [
            "Не начинать с исследования.",
            "Не брать fee до сдвига структуры.",
            "Не вести сателлит на каталог.",
            "Не обещать новую жизнь.",
        ],
        "meta": {
            "calendar_7d": calendar,
            "fin_structure_shift": fin,
            "warm_x": warm_x,
            "warm_tg": warm_tg,
            "close_script": close_script,
            "satellite": satellite,
            "derivative_product": derivative,
            "trend_id": trend.get("id"),
            "archetype": arch,
            "missing_optional": missing,
            "engine_brief": prompt.get("engine_brief"),
            "gates_ok": True,
        },
        "highway": {
            "free": "камера сборки как демо-неделя",
            "paid": "посадка недели в контур клиента на share",
            "sku": "pilot_14",
        },
        "disclaimer": DISCLAIMER,
        "module": "MakingChamber",
        "version": "1.0.0",
        "section": "making",
        "message": f"Камера сборки · {title}",
    }
    return pack


def format_making_telegram(pack: dict[str, Any]) -> str:
    def esc(s: Any) -> str:
        return (
            str(s or "")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    cal = (pack.get("meta") or {}).get("calendar_7d") or []
    days = "\n".join(f"{d.get('day')}. <b>{esc(d.get('title'))}</b> — {esc(d.get('do'))}" for d in cal)
    fin = (pack.get("meta") or {}).get("fin_structure_shift") or {}
    fee = fin.get("success_fee") or {}
    return (
        f"<b>{esc(pack.get('title'))}</b>\n"
        f"{esc(pack.get('one_liner'))}\n\n"
        f"<b>Неделя</b>\n{days}\n\n"
        f"<b>Share</b>\n{esc(fee.get('on'))}\n"
        f"<i>{esc(fee.get('kill'))}</i>\n\n"
        f"<i>{esc(pack.get('disclaimer'))}</i>"
    )
