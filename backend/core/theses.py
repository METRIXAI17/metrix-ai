"""Sellable artefact: theses on order.

The conveyor niche. Customer pays for theses only — short killable claims
about a process / a market relation. Analyzer of relation-shifts is internal.
Project generator is not sold.

Propeller Ads creative = one thesis about a process. Not signals. Not «our AI».
"""

from __future__ import annotations

from typing import Any

from backend.core.resonance import new_id
from backend.core.voice import DISCLAIMER, clip, first_sentence


def _has(text: str, *words: str) -> bool:
    low = (text or "").lower()
    return any(w.lower() in low for w in words)


def _relation_theses(brief: str) -> list[dict[str, str]]:
    """Internal analyzer. Public output is theses only."""
    t = brief or ""
    sit = first_sentence(t, "контур без имени")
    out: list[dict[str, str]] = []

    def add(text: str, status: str, relation: str) -> None:
        out.append({"text": text, "status": status, "relation": relation})

    if _has(t, "отсрочк", "предоплат", "реализац", "консигнац"):
        if _has(t, "предоплат") or _has(t, "снял отсроч"):
            add(
                "Отсрочка как вход мертва: поставщик взял предоплату или реализацию.",
                "dead",
                "поставщик→касса",
            )
            add(
                "Живое отношение: кто платит за лежание товара, пока касса не закрыла закупку.",
                "alive",
                "товар→время денег",
            )
        else:
            add(
                "Отсрочка ещё названа — тезис «вход в товар без своей кассы» жив, пока поставщик не снял окно.",
                "alive",
                "поставщик→касса",
            )
    if _has(t, "онбординг", "бриф", "аккаунт", "агентств", "продакш"):
        add(
            "Онбординг без границы пакета сжигает маржу на нулевой неделе — пакета нет, есть геройство.",
            "dead" if _has(t, "сжиг", "жрёт", "съед") else "alive",
            "клиент→агентство",
        )
        add(
            "Метод, который нельзя посадить в конфиг подрядчику, не является методом.",
            "alive",
            "метод→конфиг",
        )
    if _has(t, "фич", "jira", "slack", "внедр", "it ", "айти", "saas"):
        add(
            "Фича без того, кто платит за 90 дней, не фича — статус в трекере.",
            "dead" if _has(t, "вроде", "пилим", "без экономи") else "alive",
            "команда→деньги фичи",
        )
        add(
            "Конфиг внедрения жив, только если названы слоты: вход, выход, молчание, kill.",
            "alive",
            "IT→подрядчик",
        )
    if _has(t, "склад", "фулфил", "отгруз", "физическ", "товар", "sku", "магазин"):
        add(
            "Витрина без цикла кассы физического SKU — обои. Тезис магазина мёртв, пока не названо, кто оплачивает лежание.",
            "dead" if _has(t, "туман", "не знаю", "касса") else "alive",
            "SKU→касса",
        )
    if _has(t, "реклам", "трафик", "propeller", "залив", "клик"):
        add(
            "Трафик на процесс без тезиса, который можно убить фактом, сливает бюджет на чужой нарратив.",
            "dead",
            "клик→процесс",
        )
        add(
            "Один тезис = один креатив. Два обещания в одном объявлении — не тезис.",
            "alive",
            "креатив→заказ",
        )
    if _has(t, "курс", "школ", "урок", "когорт"):
        add(
            "Образование не в этом контуре. Тезис «ещё контент продаст» здесь не продаём.",
            "dead",
            "контент→офер",
        )
    if not out:
        add(
            f"Отношение в «{clip(sit, 80)}» не названо: кто кому платит, кто молчит, что умерло.",
            "dead",
            "контур→имя отношения",
        )
        add(
            "Заказ тезисов жив, когда можно убить хотя бы одно утверждение фактом на этой неделе.",
            "alive",
            "тезис→факт",
        )
        add(
            "Пока отношение не названо — не собирать проект и не лить трафик.",
            "alive",
            "заказ→стоп",
        )
    # Always close with a kill thesis.
    add(
        "Если за 14 дней ни один тезис не убит фактом — заказ конвейера выключить, не «докрутить формулировку».",
        "alive",
        "заказ→kill",
    )
    # Dedup by text
    seen: set[str] = set()
    uniq: list[dict[str, str]] = []
    for row in out:
        key = row["text"]
        if key in seen:
            continue
        seen.add(key)
        uniq.append(row)
    return uniq[:7]


def order_theses(brief: str = "", lang: str = "ru") -> dict[str, Any]:
    text = (brief or "").strip() or "контур без описания"
    engine_pack: dict[str, Any] = {}
    engine_theses: list[dict[str, str]] = []
    try:
        from backend.core.engine_run import run_engine, theses_from_engine

        engine_pack = run_engine(text, lang=lang)
        engine_theses = theses_from_engine(engine_pack, text)
    except Exception:  # noqa: BLE001
        engine_pack = {"ok": False}
    local = _relation_theses(text)
    theses: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in engine_theses + local:
        key = (row or {}).get("text") or ""
        if not key or key in seen:
            continue
        seen.add(key)
        theses.append(row)
    theses = theses[:7]
    alive = sum(1 for x in theses if x["status"] == "alive")
    dead = sum(1 for x in theses if x["status"] == "dead")
    ru = (lang or "ru").startswith("ru")
    lines = [f"{'мёртв' if x['status'] == 'dead' else 'жив'}. {x['text']}" for x in theses]
    return {
        "id": new_id(),
        "kind": "artefact.thesis",
        "lane": "artefacts",
        "title": "Тезисы на заказ" if ru else "Theses on order",
        "one_liner": (
            "Продаём только тезисы. Короткое утверждение про процесс, которое можно убить фактом."
            if ru
            else "We sell theses only. A short process claim you can kill with a fact."
        ),
        "break": (
            "Отчёт, дашборд и «проект в подарок» размывают товар. Товар — тезис."
            if ru
            else "A report, a dashboard, or a free project is not the SKU. The SKU is the thesis."
        ),
        "move": "\n".join(lines),
        "steps": lines,
        "artifact_week": f"{len(theses)} тезисов · живых {alive} · мёртвых {dead}.",
        "anti": [
            "Не продавать проект вместо тезиса.",
            "Не писать тезис, который нельзя убить фактом.",
            "Не лить Propeller в сигналы и не в «наш ИИ».",
        ],
        "theses": theses,
        "meta": {
            "sold": "theses_only",
            "analyzer": "metrix_ai_engine",
            "engine": "metrix_ai",
            "engine_ok": bool(engine_pack.get("ok")),
            "request_id": engine_pack.get("request_id") or "",
            "project_generator": "not_sold",
            "count": len(theses),
            "alive": alive,
            "dead": dead,
            "lang": lang,
        },
        "disclaimer": DISCLAIMER,
        "brief": clip(text, 400),
        "highway": {
            "free": "черновик тезисов",
            "paid": "заказ тезисов · Access",
            "sku": "access_month",
        },
    }


def propeller_pack() -> list[dict[str, str]]:
    """Creatives: one process thesis per ad. No signals. No yield promise."""
    return [
        {
            "id": "ad_prepay",
            "thesis": "Отсрочка как вход мертва — поставщик взял предоплату.",
            "landing": "/tg/#artefacts",
            "ban": "не доходность, не сигналы",
        },
        {
            "id": "ad_onboard",
            "thesis": "Онбординг жрёт маржу на нулевой неделе — пакета нет, есть геройство.",
            "landing": "/tg/#artefacts",
            "ban": "не «наш ИИ»",
        },
        {
            "id": "ad_feature",
            "thesis": "Фича без того, кто платит за 90 дней — не фича.",
            "landing": "/tg/#artefacts",
            "ban": "не SaaS-хайп",
        },
        {
            "id": "ad_sku",
            "thesis": "Витрина без цикла кассы физического SKU — обои.",
            "landing": "/ai/",
            "ban": "не инфопродукт",
        },
        {
            "id": "ad_traffic",
            "thesis": "Трафик на процесс без убиваемого тезиса сливает бюджет.",
            "landing": "/tg/#artefacts",
            "ban": "не гарантия ROAS",
        },
    ]
