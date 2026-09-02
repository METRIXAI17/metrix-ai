"""Artefacts tab: analytical panel + offer generator.

Panel comes from operational analytics (constructor slots, tensions, metrics).
Offers come from making chamber + promo-lite — one generator, not two menus.
Tape Land folder is the two-leg-tape model, not a separate app.
"""

from __future__ import annotations

from typing import Any

from backend.core.resonance import new_id
from backend.core.voice import DISCLAIMER, clip


def analytical_panel(brief: str = "", lang: str = "ru") -> dict[str, Any]:
    from backend.core.metrics import compute_core_metrics
    from backend.core.operational_analytics import OperationalAnalyticsEngine
    from backend.core.pragma_phenomena import evaluate_pragma_phenomena

    text = (brief or "").strip() or "контур без описания — конструктор пустой формы"
    words = len(text.split())
    known = min(10, max(2, words // 8))
    m = compute_core_metrics(
        known_params=known,
        required_params=10,
        ambiguity_score=0.38 if words < 40 else 0.14,
        missing_critical=1 if words < 20 else 0,
        notes=[clip(text, 120)],
    )
    pragma = evaluate_pragma_phenomena(
        vvi=m.vvi,
        er=m.er,
        rrc=m.rrc,
        health=m.health_score,
        readiness=m.health_score,
        overall=m.health_score,
        info_roi=1.2,
        success_composite=m.health_score,
        success_target=0.55,
        product_fit=0.5,
        promo_fit=0.4,
    )
    oae_dict: dict[str, Any] = {}
    try:
        oae = OperationalAnalyticsEngine().run(
            business_text=text,
            industry_id="expert-services",
            orientation={
                "scores": {"readiness": m.health_score},
                "frame": {"axes": {}},
                "parameter_map": {"params": {}, "missing": ["risks"]},
            },
            idea_title=clip(text, 72),
            vvi=m.vvi,
            er=m.er,
            rrc=m.rrc,
            health=m.health_score,
            info_roi=1.2,
            missing_params=["goal", "metrics", "risks"] if words < 40 else ["risks"],
        )
        oae_dict = oae.to_dict()
    except Exception as exc:  # noqa: BLE001
        oae_dict = {"error": str(exc)[:240]}

    constructors = oae_dict.get("constructors") or []
    readable = [
        f"VVI {m.vvi:.2f} — {m.labels['vvi']} (пустоты в спеке)",
        f"ER {m.er:.2f} — {m.labels['er']} (ошибки как топливо)",
        f"RRC {m.rrc:.2f} — {m.labels['rrc']} (можно разобрать и собрать лучше)",
        f"health {m.health_score:.2f} — {m.labels['health']}",
    ]
    return {
        "id": new_id(),
        "kind": "artefact.panel",
        "lane": "artefacts",
        "title": "Аналитическая панель",
        "one_liner": "Метрики как артефакт: просто прочитать, сложно подделать.",
        "break": "Дашборд без единицы и без kill — это обои. Панель показывает напряжение, пустоту и что считать победой.",
        "move": (
            "Неопределённые параметры не выкидываются — они становятся конструктором формы. "
            "Глубокий слой сжимается обратно в язык запроса. "
            "Это Tape Land в миниатюре: отношение параметров, не «ещё график»."
        ),
        "steps": [
            "Прочитать метрики как текст, не как KPI-театр.",
            "Отметить конструкторы пустоты — туда вливается геометрия.",
            "Снять напряжение pragma: где система сплитуется.",
            "Оставить одну цифру, которая значит, что контур живой.",
        ],
        "artifact_week": "Одна панель: 4 метрики, 1 конструктор пустоты, 1 условие kill.",
        "anti": [
            "Не добавлять метрики, которые нельзя прочитать вслух.",
            "Не называть панель торговым сигналом.",
        ],
        "readable": readable,
        "meta": {
            "metrics": m.to_dict(),
            "pragma": pragma.to_dict(),
            "constructors": constructors[:8] if isinstance(constructors, list) else [],
            "summary": oae_dict.get("summary") or "",
            "lang": lang,
        },
        "disclaimer": DISCLAIMER,
        "brief": clip(text, 400),
    }


def offer_generator(brief: str = "", lang: str = "ru") -> dict[str, Any]:
    from backend.core.functions.making_chamber import run_making_function
    from backend.core.promo_lite import run_promo_lite

    text = (brief or "").strip() or "собери предложение из того, что уже движется"
    making = run_making_function(text, lang=lang, extra="")
    if not making.get("ok"):
        from backend.core.content_closer import run_closer

        pack = run_closer(text, lang=lang, with_comfort=False, with_making=True)
        making = {"ok": True, "making": pack.get("making") or pack, "cards": (pack.get("cards") or {}).get("codes")}
    promo = run_promo_lite(text, kind="all", industry_id="expert-services", lang=lang)

    making_art = (making or {}).get("making") or {}
    cards = (making or {}).get("cards") or making_art.get("cards") or {}
    fee = ((making_art.get("meta") or {}).get("fin_structure_shift") or {}).get("success_fee") or {}

    return {
        "id": new_id(),
        "kind": "artefact.offer",
        "lane": "artefacts",
        "title": "Генератор предложений",
        "one_liner": "Неделя, которую можно прожить, плюс оффер, который можно положить на стол.",
        "break": "Два старых выхода (мейкинг и промо) жили отдельно. Здесь это одна папка.",
        "move": (
            "Камера сборки ткёт неделю. Промо-lite собирает карточки описания. "
            "Вместе это предложение: что входит, чего нет, share с изменённой структуры, kill."
        ),
        "steps": making_art.get("steps")
        or [
            "Событие, не исследование.",
            "Неделя из семи дней, которые можно прожить.",
            "Оффер с границей и kill.",
            "Share — если зашло, не ретейнер «на всякий».",
        ],
        "artifact_week": making_art.get("artifact_week")
        or "Пакет: неделя + 3 карточки оффера + условие share/kill.",
        "anti": making_art.get("anti") or ["Не продавать неделю как «контент-план»."],
        "meta": {
            "making_title": making_art.get("title"),
            "cards": cards,
            "promo": promo if isinstance(promo, dict) else {},
            "share": fee,
            "calendar": (making_art.get("meta") or {}).get("calendar_7d") or [],
        },
        "disclaimer": DISCLAIMER,
        "brief": clip(text, 400),
        "highway": {"free": "черновик предложения", "paid": "посадка пакета", "sku": "access_month"},
    }


def tape_folder() -> dict[str, Any]:
    return {
        "id": "two_leg_tape",
        "kind": "artefact.folder",
        "title": "Tape Land · two-leg-tape",
        "one_liner": "Две ноги: внимание обгоняет цену, деньги подтверждают. Без плеча.",
        "note": (
            "Папка, не отдельный Railway-сервис. Модель живёт в этом же движке. "
            "LIVE только когда обе ноги на месте. Пустой нарратив — серый список."
        ),
    }
