"""Demo as the paid highway.

User situation → one named artifact → resonance (зашло / почти / мимо)
→ if hit, that artifact IS the SKU.

This is the general version of Metrix: not a catalog, not a chatbot.
"""

from __future__ import annotations

import re
from typing import Any

from backend.core.agent_studio import NICHES, build_agent, resolve_niche
from backend.core.resonance import remember
from backend.core.strategies import run_strategy, resolve_strategy
from backend.core.voice import DISCLAIMER, PAID_BRIDGE, clip, first_sentence


def _has(text: str, *words: str) -> bool:
    low = (text or "").lower()
    return any(w in low for w in words)


def detect_lane(brief: str, hint: str = "") -> str:
    h = (hint or "").strip().lower()
    if h in ("strategy", "agent", "model", "landing", "engine", "making", "chain", "teammates", "artefacts"):
        return {"landing": "chain", "engine": "teammates", "making": "artefacts"}.get(h, h)
    if h in ("target_place", "demand", "ampli", "two_leg_tape", "gold", "crypto", "us", "tape", "risk"):
        return "strategy"
    if h in ("saas", "agency", "edu", "ecom"):
        return "agent"
    b = brief or ""
    if _has(b, "золот", "xau", "крипт", "мемкоин", "nasdaq", "spy", "америк", "target place", "ampli", "demand"):
        return "strategy"
    if _has(b, "агент", "saas", "школ", "агентств", "e-com", "ecom", "средний чек", "performance"):
        return "agent"
    return "model"


def _industry_for(brief: str, lane: str) -> str:
    if lane == "agent":
        return NICHES[resolve_niche(None, brief)]["industry"]
    if _has(brief, "фриланс", "соло"):
        return "freelace-d2c"
    if _has(brief, "курс", "школ"):
        return "education"
    if _has(brief, "магазин", "чек", "ecom"):
        return "ecommerce"
    if _has(brief, "saas", "софт"):
        return "saas-founders"
    return "expert-services"


def _harvest_pipeline(brief: str, industry: str) -> dict[str, Any]:
    if len((brief or "").strip()) < 20:
        return {}
    try:
        from backend.core.request_pipeline import process_client_request

        out = process_client_request(
            {
                "industry": industry,
                "business": brief,
                "track": "all",
                "lang": "ru",
            }
        )
        if not isinstance(out, dict):
            return {}
        idea = out.get("demo_idea") or {}
        return {
            "idea_title": idea.get("title") or "",
            "idea_blurb": idea.get("summary") or idea.get("blurb") or idea.get("description") or "",
            "next": (out.get("next_steps") or [])[:4],
            "ok": out.get("ok", True),
        }
    except Exception:  # noqa: BLE001
        return {}


def _model_artifact(brief: str, harvested: dict[str, Any]) -> dict[str, Any]:
    from backend.core.resonance import new_id

    sit = first_sentence(brief, "живая задача без упаковки")
    idea = harvested.get("idea_title") or ""
    title = idea or "Модель посадки"
    if idea:
        title = f"Модель · {clip(idea, 48)}"

    money = _has(brief, "марж", "юнит", "ltv", "чек", "окуп", "касса", "revenue")
    people = _has(brief, "команд", "сотруд", "менедж", "отдел")
    time = _has(brief, "срок", "недел", "месяц", "пилот", "14")

    break_line = (
        f"Сейчас «{clip(sit, 90)}» живёт как разговор. "
        "Нет места входа, нет места выхода, нет единицы, за которую стыдно, если сломается."
    )
    if money:
        break_line = (
            "Цифры есть, посадки нет: юнит считают отдельно от того, как люди нажимают кнопки. "
            "Модель без контура — это отчёт."
        )
    if people and not money:
        break_line = (
            "Людей много, модели нет. Решение плавает между людьми и нигде не становится артефактом."
        )

    move = (
        "Нестандартный ход — не «давайте AI». "
        "Ход: собрать именную финмодель под этот контур (единица, стоп, кто нажимает) "
        "и отдать её человеком читаемым артефактом. Потом агент, если артефакт зашёл."
    )
    steps = harvested.get("next") or [
        "Описать контур: кто принимает, где умирает, что считается деньгами.",
        "Собрать черновую модель на одну страницу. Без слайдов.",
        "Прогнать на одном живом случае на этой неделе.",
        "Оставить только то, что срезонировало. Остальное вырезать.",
    ]
    if time:
        steps = [
            "Пилот режется 14 днями. После — либо посадка, либо стоп.",
            *steps[:3],
        ]

    return {
        "id": new_id(),
        "kind": "model.implement",
        "lane": "model",
        "title": title,
        "one_liner": "Финансовая модель как посадка в проект, не как файл.",
        "break": break_line,
        "move": move,
        "steps": [str(s) for s in steps][:5],
        "artifact_week": (
            "Одна страница: вход, выход, единица денег, инвалидация, кто нажимает. "
            "Если страница не читается за 90 секунд — это ещё слайд."
        ),
        "anti": [
            "Не начинать с архитектуры и нейросетей.",
            "Не продавать внедрение до того, как артефакт зашёл.",
            "Не плодить метрики, которые никто не откроет второй раз.",
        ],
        "meta": {"harvested": bool(idea)},
        "highway": {
            "free": "этот артефакт",
            "paid": "посадка модели в ваш проект за 14 дней",
            "sku": "pilot_14",
        },
        "brief": clip(brief, 400),
        "disclaimer": DISCLAIMER,
    }


def _attach_closer(art: dict[str, Any], closer: dict[str, Any] | None) -> dict[str, Any]:
    """First voice is abstraction; cards and rewritten prompt ride with the artifact."""
    if not closer:
        return art
    essay = closer.get("abstraction") or {}
    cards = closer.get("cards") or {}
    event = closer.get("event") or {}
    art["abstraction"] = essay
    art["cards"] = cards
    art["prompt"] = closer.get("prompt")
    art["event"] = event
    art["trends"] = closer.get("trends")
    art["comfort"] = closer.get("comfort")
    art["engine_brief"] = closer.get("engine_brief")
    art["audit"] = closer.get("audit")
    art["closer_id"] = closer.get("id")
    art["layers"] = closer.get("layers")
    meta = dict(art.get("meta") or {})
    if event.get("invitation"):
        meta.setdefault("entry", event.get("invitation"))
    if essay.get("archetype"):
        meta["archetype"] = essay.get("archetype")
    codes = cards.get("codes") or []
    if codes:
        meta["cards"] = codes
    art["meta"] = meta
    return art


def build_demo(
    brief: str,
    *,
    hint: str = "",
    strategy: str | None = None,
    niche: str | None = None,
) -> dict[str, Any]:
    text = (brief or "").strip()
    if len(text) < 8:
        raise ValueError("Напишите ситуацию чуть живее — хотя бы одно предложение.")

    closer = None
    closer_as_artifact = None  # type: ignore[assignment]
    try:
        from backend.core.content_closer import closer_as_artifact as _caa
        from backend.core.content_closer import run_closer

        closer_as_artifact = _caa
        want_making = (hint or "").strip().lower() in ("making", "мейкинг", "artefacts")
        closer = run_closer(
            text,
            lang="ru",
            with_comfort=True,
            with_making=want_making,
        )
    except Exception:  # noqa: BLE001
        closer = None

    lane = detect_lane(text, hint)
    if strategy:
        lane = "strategy"
    if niche and not strategy:
        lane = "agent"

    if lane in ("landing", "chain"):
        art = (
            closer_as_artifact(closer)
            if closer and closer_as_artifact
            else _model_artifact(text, {})
        )
    elif lane in ("making", "artefacts"):
        from backend.core.theses import order_theses

        art = order_theses(text, lang="ru")
    elif lane == "strategy":
        art = run_strategy(strategy or hint, text)
    elif lane in ("agent", "teammates"):
        from backend.core.teammates import build_teammate

        art = build_teammate(niche or hint, text)
    else:
        harvested = _harvest_pipeline(text, _industry_for(text, lane))
        art = _model_artifact(text, harvested)
        if closer and lane in ("model", "engine", "teammates"):
            # engine answers lead with the figure, then the model
            arch = (closer.get("abstraction") or {}).get("archetype")
            if arch and not str(art.get("title") or "").startswith(arch):
                art["title"] = f"{arch} · {art.get('title')}"
            if closer.get("abstraction", {}).get("essay"):
                art["move"] = closer["abstraction"]["essay"]

    art = _attach_closer(art, closer)
    art["disclaimer"] = art.get("disclaimer") or DISCLAIMER
    art["bridge"] = PAID_BRIDGE
    remember(art)
    return art


def format_telegram(art: dict[str, Any]) -> str:
    def esc(s: Any) -> str:
        return (
            str(s or "")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    theses = art.get("theses") or []
    if theses:
        steps = "\n".join(
            f"{i}. {'мёртв' if (row or {}).get('status') == 'dead' else 'жив'}. {esc((row or {}).get('text'))}"
            for i, row in enumerate(theses, 1)
        )
    else:
        steps = "\n".join(f"{i}. {esc(s)}" for i, s in enumerate(art.get("steps") or [], 1))
    anti = "\n".join(f"— {esc(s)}" for s in (art.get("anti") or [])[:3])
    meta_bits = []
    m = art.get("meta") or {}
    if m.get("entry"):
        meta_bits.append(f"<b>Вход.</b> {esc(m['entry'])}")
    if m.get("exit"):
        meta_bits.append(f"<b>Выход.</b> {esc(m['exit'])}")
    if m.get("invalidation"):
        meta_bits.append(f"<b>Смерть тезиса.</b> {esc(m['invalidation'])}")
    if m.get("window"):
        meta_bits.append(f"<b>Окно.</b> {esc(m['window'])}")
    extra = ("\n\n" + "\n".join(meta_bits)) if meta_bits else ""
    codes = (art.get("cards") or {}).get("codes") or (m.get("cards") if isinstance(m.get("cards"), list) else [])
    cards_bit = ""
    if codes:
        cards_bit = "\n\n<b>Карточки</b>\n" + " · ".join(esc(c) for c in codes)
    lead = ""
    arch = (art.get("abstraction") or {}).get("lead") or m.get("archetype")
    if arch and arch not in str(art.get("title") or ""):
        lead = f"<b>{esc(arch)}</b>\n"

    return (
        f"{lead}"
        f"<b>{esc(art.get('title'))}</b>\n"
        f"{esc(art.get('one_liner'))}\n\n"
        f"<b>Где ломается</b>\n{esc(art.get('break'))}\n\n"
        f"<b>Нестандартный ход</b>\n{esc(art.get('move'))}\n\n"
        f"<b>Как садится</b>\n{steps}\n\n"
        f"<b>Артефакт на неделю</b>\n{esc(art.get('artifact_week'))}"
        f"{extra}{cards_bit}\n\n"
        f"<b>Не делать</b>\n{anti}\n\n"
        f"<i>{esc(art.get('disclaimer'))}</i>\n\n"
        "Зашло / почти / мимо — от этого зависит, есть ли товар."
    )


def format_almost_prompt() -> str:
    return "Ок, почти. Напишите одной фразой, чего не хватает или что режет глаз — соберу вторую версию."


def format_miss() -> str:
    return (
        "Мимо — нормально. Ценность я майню из того, что заходит, остальное не тяну.\n\n"
        "Можно взять другую дверь: стратегию, агента, или просто переписать задачу другими словами."
    )


def format_hit(art: dict[str, Any]) -> str:
    title = art.get("title") or "артефакт"
    return (
        f"Зашло. Тогда это и есть товар — «{title}».\n\n"
        f"{PAID_BRIDGE}\n\n"
        "Напишите, куда прислать пилот (Telegram / почта), "
        "или откройте билдер и продолжим там. "
        "Можно просто написать контакт следующей строкой."
    )
