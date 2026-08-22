"""Digital mockup of the individual — fast unfold of solo work."""

from __future__ import annotations

import re
from typing import Any

from backend.core.task_reader import assemble_query


def _pick(text: str, pairs: list[tuple[str, str]], default: str) -> str:
    low = text.lower()
    for pat, val in pairs:
        if re.search(pat, low):
            return val
    return default


def run_digital_mockup(
    portrait: str,
    *,
    lang: str = "ru",
    offer: str = "",
) -> dict[str, Any]:
    """
    A working likeness: tempo, offer geometry, ops slots, so the individual
    can spin up work without rebuilding identity each time.
    """
    text = f"{portrait or ''} {offer or ''}".strip()
    packed = assemble_query(text, lang=lang, surface_hint="digital_mockup")
    tempo = _pick(
        text,
        [
            (r"быстр|спринт|daily|каждый день", "daily_sprint"),
            (r"медлен|исследов|r&d|лаборатор", "research_cycle"),
            (r"клиент|созвон|call|сесси", "session_based"),
        ],
        "batch_twice_week",
    )
    channel = _pick(
        text,
        [
            (r"telegram|телеграм|\bтг\b", "telegram"),
            (r"x\.com|twitter", "x"),
            (r"офлайн|студия|локац", "offline"),
        ],
        "hybrid",
    )
    offer_shape = _pick(
        text,
        [
            (r"подписк|retainer|абонемент", "retainer"),
            (r"пакет|pack|карточки", "pack_sku"),
            (r"пилот|pilot", "pilot"),
            (r"ордер|сделк", "order_ticket"),
        ],
        "one_off_pack",
    )
    slots = [
        {"id": "intake", "title": "Вход", "how": "20+ символов своими словами, без созвона"},
        {"id": "orient", "title": "Ориентация", "how": "Task reader → режим автоматически"},
        {"id": "pack", "title": "Пак", "how": "Один артефакт (карточка / журнал / макет / ТЗ)"},
        {"id": "offramp", "title": "Оффрамп", "how": "Оплата после утверждения или SKU Mini App"},
    ]
    likeness = {
        "tempo": tempo,
        "channel": channel,
        "offer_shape": offer_shape,
        "working_name": (portrait or "individual")[:48],
        "do_not_copy": "Не копия личности. Рабочая геометрия: темп, оффер, слоты.",
    }
    unfold = [
        "Открыть Mini App → функция «цифровой макет»",
        f"Темп {tempo}: слот intake каждый цикл, без ожидания вдохновения",
        f"Оффер {offer_shape} лежит как SKU, не как «давайте обсудим»",
        "Повторять pack → offramp, пока не появится свой флагман",
    ]
    return {
        "module": "Digital Mockup",
        "function": "digital_mockup",
        "likeness": likeness,
        "ops_slots": slots,
        "unfold_24h": unfold,
        "assembly": packed,
        "summary": f"tempo={tempo} channel={channel} offer={offer_shape}",
    }
