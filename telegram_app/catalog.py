"""Four bot rooms and three Tribute categories. Prices are the public board."""

from __future__ import annotations

import html
import os
from typing import Any


def _esc(text: Any) -> str:
    return html.escape(str(text or ""), quote=False)


# Democratic board. Not the old $100 / $490 / $1 000 / $10 000 line.
OFFERS: dict[str, dict[str, Any]] = {
    "dev": {
        "id": "dev",
        "rub": 3490,
        "usd": 39,
        "name": "Покупка разраба",
        "env": "TRIBUTE_DEV_URL",
        "blurb": (
            "Один разработчик на одну задачу. "
            "Большой бот держит весь путь: заказ, молчание, kill. "
            "Мелкое ядро делает один шаг: читает бриф, сажает слот или пишет спеку."
        ),
    },
    "private": {
        "id": "private",
        "rub": 990,
        "usd": 12,
        "name": "Подписка на приватку",
        "env": "TRIBUTE_PRIVATE_URL",
        "blurb": (
            "Месяц тихой комнаты. Деньги, рынки и новые штуки без витрины. "
            "Без сигналов, без чужих депозитов, без обещания дохода."
        ),
    },
    "files": {
        "id": "files",
        "rub": 1490,
        "usd": 19,
        "name": "Готовые файлы роя",
        "env": "TRIBUTE_FILES_URL",
        "blurb": (
            "Файл, который уже собрали рой движков или бот: "
            "рекурсивная методика и надстройка того же контура. "
            "Не подписка и не живой разработчик."
        ),
    },
}


def price_line(offer_id: str) -> str:
    row = OFFERS[offer_id]
    return f"{row['rub']} ₽ · ${row['usd']} · {row['name']}"


def pay_url(offer_id: str) -> str:
    row = OFFERS.get(offer_id) or {}
    raw = (os.getenv(row.get("env") or "") or "").strip()
    if raw:
        return raw
    from backend.config import TRIBUTE_ACCESS_URL

    return TRIBUTE_ACCESS_URL or "https://t.me/tribute"


def pay_button(offer_id: str) -> dict[str, str]:
    row = OFFERS[offer_id]
    return {"text": f"{row['name']} · {row['rub']} ₽", "url": pay_url(offer_id)}


def tribute_board() -> str:
    lines = ["<b>Три категории на Tribute</b>", ""]
    for key in ("dev", "private", "files"):
        row = OFFERS[key]
        lines.append(f"<b>{_esc(row['name'])}</b> · {row['rub']} ₽")
        lines.append(_esc(row["blurb"]))
        lines.append("")
    return "\n".join(lines).strip()


def consult_intro() -> str:
    return (
        "<b>Консультации</b>\n"
        "Два режима отдельно. В каждом — суть, решение и несколько вариантов, как в разборе жертвенности.\n\n"
        "<b>1 · Под капотом</b>\n"
        "Видно, что делает движок: раздел цикла, уровень вопросов, рамка своего контура, "
        "из чего режутся варианты.\n"
        "В результате — суть, решение и список мелких задач. Файл рекурсии здесь не собирается.\n\n"
        "<b>2 · Рекурсивка</b>\n"
        "Под капотом четыре шага одного слота: bound, kill, библиотека, понедельник.\n"
        "В результате — файл этой рекурсии.\n"
        f"{price_line('files')}\n\n"
        "Напишите двумя строками, что ломается и куда это должно сесть. Сначала выберите режим.\n\n"
        + after_pay_block()
    )


def private_intro() -> str:
    return (
        "<b>Приватка</b>\n"
        "Два режима сразу. Подписка одна.\n"
        f"{price_line('private')}\n\n"
        "Выберите режим."
    )


def private_mode(mode: str) -> str:
    if mode == "hood":
        return (
            "<b>Приватка · под капотом</b>\n"
            "Комната не публикует цепочку на витрину. "
            "Движок держит бриф, тикер и файл у подписчика.\n"
            "Сюда не входят сигналы, чужие депозиты и обещание дохода.\n\n"
            f"{_esc(OFFERS['private']['blurb'])}"
        )
    return (
        "<b>Приватка · в результате</b>\n"
        "Раз в неделю одна посадка: суть, одно решение, один файл, если рой уже отработал.\n"
        "Можно принести свой бриф. Ответ остаётся в комнате.\n\n"
        f"{price_line('private')}"
    )


def work_intro() -> str:
    return (
        "<b>Боты и ядра</b>\n"
        "Большой бот ведёт задачу целиком. Мелкое ядро закрывает один шаг.\n"
        f"Покупка разраба: {price_line('dev')}\n"
        f"Готовый файл без живого запуска: {price_line('files')}"
    )


def work_mode(mode: str) -> str:
    if mode == "bot":
        return (
            "<b>Большой бот</b>\n"
            "Под капотом: один путь денег. Кто платит, когда бот молчит, какой факт его выключает.\n"
            "В результате: бот под вашу задачу, не витрина из четырёх чужих стратегий.\n\n"
            f"{price_line('dev')}"
        )
    return (
        "<b>Мелкое ядро</b>\n"
        "Под капотом: одна функция. Читатель брифа, спека или один шаг рекурсии.\n"
        "В результате: ядро, которое можно поставить в уже существующего бота.\n\n"
        f"{price_line('dev')}\n"
        "Если нужен только файл, без запуска — категория «Готовые файлы роя»."
    )


def after_pay_block(pack: dict[str, Any] | None = None) -> str:
    """Old flagship turnaround, unchanged, under one heading."""
    _ = pack
    from backend.core.workflow_turnaround import format_telegram, turnaround

    body = format_telegram(turnaround(lang="ru"))
    ask = (
        "<b>Флагман.</b> Бесплатный слой. Две строки, не эссе.\n"
        "Выдаёт суть твоего вопроса и решение одной фразой.\n"
        "Потом несколько вопросов — сводка векторов результата."
    )
    return "<b>После оплаты вы получите</b>\n\n" + body + "\n\n" + ask


def format_consult(pack: dict[str, Any], mode: str) -> str:
    variants = pack.get("variants") or []
    lines = [
        f"<b>{_esc(pack.get('ticker'))}</b>",
        f"Суть: {_esc(pack.get('problem'))}",
        f"Решение: {_esc(pack.get('solution'))}",
        "",
        "<b>Варианты</b>",
    ]
    for v in variants[:5]:
        lines.append(f"· <b>{_esc(v.get('title'))}</b> — {_esc(v.get('task'))}")
        if v.get("done"):
            lines.append(f"  готово, когда {_esc(v.get('done'))}")
    lines.append("")
    sit = pack.get("sit") or {}
    if mode == "recurse":
        lines.append("<b>Под капотом</b>")
        lines.append("Один слот режется на четыре шага. Глубина небольшая. Новая линейка не открывается.")
        lines.append(f"· bound — {_esc(sit.get('give') or pack.get('problem'))}")
        lines.append(f"· kill — {_esc(sit.get('kill') or 'ход, который закрываем')}")
        lines.append(f"· библиотека — {_esc(sit.get('library') or 'карточка границы')}")
        lines.append(f"· понедельник — {_esc(sit.get('monday') or 'цифра недели')}")
        lines.append("")
        lines.append("<b>В результате · рекурсивка</b>")
        lines.append("Файл: эти четыре шага плюс кодовая надстройка того же движка.")
        lines.append(price_line("files"))
    else:
        lines.append("<b>Под капотом</b>")
        lines.append(
            f"Раздел: {_esc(pack.get('cycle_section') or 'flagship')}. "
            f"Вопросы: {_esc(pack.get('question_level') or 'normal')}."
        )
        lines.append(
            f"Рамка: {_esc(pack.get('frame') or 'own_contour')}. "
            f"Чужой бизнес как основной ход: {'да' if pack.get('eternal_b2b') else 'нет'}."
        )
        lines.append("Движок называет суть, сажает решение и режет его на мелкие задачи.")
        if pack.get("section_fix"):
            lines.append(_esc(pack.get("section_fix")))
        lines.append("")
        lines.append("<b>В результате</b>")
        lines.append("Суть, решение и варианты выше.")
    lines.append("")
    lines.append(after_pay_block(pack))
    return "\n".join(lines)


def format_profile(session: dict[str, Any], entitled: dict[str, Any]) -> str:
    door = session.get("door") or "ещё нет"
    ticker = session.get("ticker") or "ещё нет"
    mode = session.get("consult_mode") or "не выбран"
    sku = entitled.get("sku") or "нет"
    tier = entitled.get("tier") or "free"
    ok = "есть" if entitled.get("ok") else "нет"
    return (
        "<b>Профиль</b>\n"
        f"Дверь: <code>{_esc(door)}</code>\n"
        f"Последний тикер: <code>{_esc(ticker)}</code>\n"
        f"Режим консультации: {_esc(mode)}\n"
        f"Доступ: {_esc(tier)} · {ok}\n"
        f"Тариф в записи: {_esc(sku)}\n\n"
        "Оплата — три категории Tribute: разраб, приватка, готовые файлы."
    )
