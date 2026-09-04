"""Stop-on-shift card.

Separate from strategy cards. Asks: does the live market contradict
the agreed strategy thesis? If yes — stop spending, then generate ideas
for the new regime. If no — do not rebuild. Not a signal. Not a new entry.

Live check does not debit Access (feature = watch).
"""

from __future__ import annotations

from typing import Any

from backend.core.resonance import new_id
from backend.core.strategies import STRATEGIES, resolve_strategy, run_strategy
from backend.core.voice import DISCLAIMER, clip, first_sentence


def _has(text: str, *words: str) -> bool:
    low = (text or "").lower()
    return any(w.lower() in low for w in words)


def _contradictions(sid: str, brief: str) -> list[str]:
    hits: list[str] = []
    if sid == "target_place":
        if _has(brief, "догон", "фомо", "опоздал", "уже ушло", "вслед", "середине"):
            hits.append("Цена не в заранее отмеченном месте — тезис мест мёртв, вход между местами сливает бюджет.")
        if _has(brief, "усредн", "добавл объём", "усреднить"):
            hits.append("Усреднение без нового места противоречит Target Place.")
    elif sid == "demand":
        if _has(brief, "держу", "инвест", "экосистем", "навсегда", "холд"):
            hits.append("Имя без окна / холд после катализатора — окно Demand мертво.")
        if _has(brief, "уже выросло", "x2", "x3", "после листинга"):
            hits.append("Спрос внутри окна уже снят. Новый вход в том же окне противоречит модели.")
        if _has(brief, "коин", "токен", "мем") and not _has(brief, "окно", "час", "листинг", "анлок"):
            hits.append("Имя названо, окно не названо — тезис Demand не собран.")
    elif sid == "ampli":
        if _has(brief, "будет расти", "будет падать", "лонг на завтра", "шорт на завтра", "таргет", "целью"):
            hits.append("Прогноз направления противоречит Ampli: модель собирает амплитуду, не мнение.")
        if _has(brief, "додержать", "до цели", "после выстрела"):
            hits.append("Амплитуда снята, удержание до таргета — слив на перемене режима.")
    elif sid == "two_leg_tape":
        if _has(brief, "плеч", "x10", "x20", "маржин", "фьюч"):
            hits.append("Плечо вместо двух ног. Tape Land без подтверждения деньгами противоречит модели.")
        if _has(brief, "хайп", "вирал", "лента") and not _has(brief, "объём", "деньг", "касс", "ликвидност"):
            hits.append("Только нога внимания. Без ноги денег тезис двух ног мёртв.")
    if _has(brief, "окно закрыл", "катализатор прошёл", "режим сменился", "уже не работает", "сломалось"):
        hits.append("Прямой факт смены режима в контуре — стоп расхода до новой карты идей.")
    return hits


def _ideas_for_new_regime(sid: str, brief: str) -> list[str]:
    """Ideas after contradiction. Not a new entry. Not a signal."""
    stem = first_sentence(brief, "новый режим")
    common = [
        f"Зафиксировать, что именно умерло в «{clip(stem, 72)}» — место, окно, амплитуда или нога денег.",
        "Не входить, пока новый тезис не назван. Скука дешевле слива.",
        "Собрать 3 идеи под новый режим: что считать входом факта, что инвалидацией, что запретом.",
    ]
    extra = {
        "target_place": "Новые места отметить до сессии. Старые магниты не переносить «потому что привыкли».",
        "demand": "Новое окно записать часами. Имя монеты подождать.",
        "ampli": "Ждать новое сжатие. Старый выстрел не дожимать.",
        "two_leg_tape": "Внимание без денег — серый список. Ждать вторую ногу.",
    }
    out = common + [extra.get(sid, "Пересобрать тезис модели, не размер.")]
    return out[:5]


def check_stop(brief: str = "", strategy: str | None = None) -> dict[str, Any]:
    text = (brief or "").strip() or "рынок как есть, без новой посадки"
    sid = resolve_strategy(strategy, text)
    hits = _contradictions(sid, text)
    contradicted = bool(hits)
    name = (STRATEGIES.get(sid) or {}).get("name") or sid
    if contradicted:
        ideas = _ideas_for_new_regime(sid, text)
        title = f"Стоп на перемене · {name}"
        one = "Режим противоречит стратегии. Бюджет не сливать. Сначала идеи под новый режим."
        move = " ".join(hits[:2])
        steps = ["Стоп расхода.", *ideas]
        status = "dead"
    else:
        ideas = []
        title = f"Стоп на перемене · {name} жива"
        one = "Противоречия тезису стратегии нет. Не пересобирать. Не входить «на всякий»."
        move = (
            "Карточка смотрит на факт против тезиса модели, не на настроение. "
            "Живой снимок рынка эту проверку не заменяет — снимок показывает картину, эта карта отвечает: тезис жив или мёртв."
        )
        steps = [
            "Оставить модель как есть.",
            "Не генерировать вход.",
            "Повторить проверку, когда рынок обновится.",
        ]
        status = "alive"
    art = run_strategy(sid, text)
    thesis = {
        "entry": (art.get("meta") or {}).get("entry") or art.get("entry"),
        "exit": (art.get("meta") or {}).get("exit") or art.get("exit"),
        "invalidation": (art.get("meta") or {}).get("invalidation") or art.get("invalidation"),
    }
    return {
        "id": new_id(),
        "kind": "chain.stop_on_shift",
        "lane": "chain",
        "strategy_id": sid,
        "title": title,
        "one_liner": one,
        "break": hits[0] if hits else "Тезис стратегии пока не опровергнут фактом из контура.",
        "move": move,
        "steps": steps,
        "artifact_week": (
            "Одна карточка: жив/мёртв + (если мёртв) три идеи под новый режим. Без нового входа."
        ),
        "anti": [
            "Не читать это как сигнал на вход.",
            "Не сливать остаток бюджета «дожать старый тезис».",
            "Не путать живой снимок с проверкой противоречия.",
        ],
        "ideas": ideas,
        "contradictions": hits,
        "status": status,
        "meta": {
            "legal": "код согласованной модели: тезис ↔ факты рынка ↔ жив/мёртв",
            "debited": False,
            "feature": "watch",
            "thesis": thesis,
        },
        "disclaimer": DISCLAIMER,
        "brief": clip(text, 400),
    }
