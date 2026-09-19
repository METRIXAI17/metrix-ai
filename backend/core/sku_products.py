"""$100 / $490 / $1000 — automated products baked into every Flagship output."""

from __future__ import annotations

from typing import Any

from backend.core.pricing_lanes import sku_of


def bake_into_output(
    brief: str = "",
    *,
    recommended: str = "sku_490",
    lang: str = "ru",
    ticker: str = "",
) -> dict[str, Any]:
    ru = (lang or "ru").startswith("ru")
    t = (brief or "").lower()
    cards = []
    for sid, move_ru, move_en in (
        (
            "sku_100",
            "120 коротких посадок. Без файла. Когда задача мелкая и не просит контур.",
            "120 short sits. No file. When the task is small and does not ask for a contour.",
        ),
        (
            "sku_490",
            "Две строки, не эссе. Нестандартный ход, конкретная библиотека, до слота.",
            "Two lines, not an essay. Unusual move, concrete library, delivered to the slot.",
        ),
        (
            "sku_1000",
            "Стандарт: рекурсивная методика + спеки, переведённые в надстройку того же движка.",
            "Standard: recursive methodology + specs, translated into the same-engine overlay.",
        ),
    ):
        row = sku_of(sid)
        row["move"] = move_ru if ru else move_en
        row["recommended"] = sid == recommended
        row["ticker"] = ticker
        cards.append(row)
    if any(w in t for w in ("10k", "10000", "контур", "contour", "автоном")):
        rec = sku_of("sku_10000")
        rec["move"] = (
            "Дизайн автономного контура в ваш проект. Плотнее спеки, тот же поток."
            if ru
            else "Autonomous contour designed into your project. Denser specs, same stream."
        )
        rec["recommended"] = recommended == "sku_10000"
        rec["ticker"] = ticker
        rec["automated"] = False
        cards.append(rec)
    return {
        "module": "AutomatedSkus",
        "baked": True,
        "recommended": recommended,
        "cards": cards,
        "note": (
            "100, 490, 1000 заложены в выдачу. Файл — после оплаты, кроме $100."
            if ru
            else "100, 490, 1000 are baked into the output. File after pay, except $100."
        ),
    }
