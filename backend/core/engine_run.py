"""Metrix AI engine adapter for the bot.

The main engine powers three bot surfaces:
  1. theses on order
  2. config generation (teammates)
  3. In-Out experiments (chain)

$2490 is the same engine as a paid SKU (physical-goods ecom), not a second brain.
No invented external LLM calls — process_client_request only.
"""

from __future__ import annotations

from typing import Any

from backend.core.voice import clip, first_sentence


def industry_for(brief: str, hint: str = "") -> str:
    low = f"{hint} {brief}".lower()
    if any(w in low for w in ("агентств", "продакш", "performance", "онбординг")):
        return "ai-agencies"
    if any(w in low for w in ("saas", "jira", "фич", "внедр", "айти", "it ")):
        return "saas-founders"
    if any(w in low for w in ("магазин", "sku", "товар", "склад", "фулфил", "физическ", "ecom")):
        return "ecommerce"
    if any(w in low for w in ("золот", "крипт", "nasdaq", "tape", "лента")):
        return "expert-services"
    return "expert-services"


def run_engine(brief: str, *, industry: str | None = None, lang: str = "ru") -> dict[str, Any]:
    text = (brief or "").strip()
    if len(text) < 16:
        return {"ok": False, "reason": "brief_short"}
    ind = industry or industry_for(text)
    try:
        from backend.core.request_pipeline import process_client_request

        out = process_client_request(
            {
                "industry": ind,
                "business": text,
                "track": "all",
                "lang": lang if lang in ("ru", "en") else "ru",
            }
        )
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "reason": str(exc)[:240]}
    if not isinstance(out, dict):
        return {"ok": False, "reason": "bad_engine"}
    meta = out.get("meta") or {}
    oae = out.get("operational_analytics") or {}
    constructors = oae.get("constructors") if isinstance(oae, dict) else []
    if not isinstance(constructors, list):
        constructors = []
    pack = (meta.get("memo_convert_v2") or meta.get("chain_pack") or {}) if isinstance(meta, dict) else {}
    bound = pack.get("bound_slots") if isinstance(pack, dict) else {}
    if not isinstance(bound, dict):
        bound = {}
    circle = meta.get("circle_system") if isinstance(meta, dict) else {}
    assertions = []
    if isinstance(circle, dict):
        assertions = list(circle.get("assertions") or [])[:8]
    reduced = oae.get("reduced_to_request") if isinstance(oae, dict) else {}
    idea = out.get("demo_idea") or {}
    metrics = out.get("metrics") or {}
    return {
        "ok": bool(out.get("ok", True)),
        "request_id": out.get("request_id") or "",
        "industry": out.get("industry") or ind,
        "idea_title": (idea.get("title") if isinstance(idea, dict) else "") or "",
        "idea_blurb": (idea.get("summary") or idea.get("blurb") or "") if isinstance(idea, dict) else "",
        "next_steps": list(out.get("next_steps") or [])[:5],
        "constructors": constructors[:10],
        "bound_slots": bound,
        "assertions": assertions,
        "reduced": reduced if isinstance(reduced, dict) else {},
        "metrics": metrics if isinstance(metrics, dict) else {},
        "chain": meta.get("chain") if isinstance(meta, dict) else {},
        "engine": "metrix_ai",
    }


def _slot_name(row: Any) -> str:
    if isinstance(row, dict):
        return str(row.get("param_name") or row.get("form_type") or row.get("form") or "slot")
    return str(row)


def theses_from_engine(pack: dict[str, Any], brief: str) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if not pack.get("ok"):
        return out
    sit = first_sentence(brief, "контур")
    for row in pack.get("constructors") or []:
        if not isinstance(row, dict):
            continue
        form = str(row.get("form_type") or row.get("form") or "open_manifold")
        param = str(row.get("param_name") or "param")
        note = str(row.get("note") or "")
        out.append(
            {
                "text": clip(
                    note
                    or f"Слот «{param}» открыт как {form}. Тезис контура мёртв, пока слот не связан.",
                    220,
                ),
                "status": "dead",
                "relation": f"{param}→{form}",
            }
        )
    for a in pack.get("assertions") or []:
        if not isinstance(a, dict):
            continue
        claim = str(a.get("claim") or a.get("text") or a.get("assertion") or "").strip()
        if not claim:
            continue
        grade = str(a.get("grade") or a.get("certainty") or "U").upper()
        out.append(
            {
                "text": clip(claim, 220),
                "status": "alive" if grade.startswith("CY") else "dead",
                "relation": str(a.get("slot") or a.get("relation") or "круг"),
            }
        )
    red = pack.get("reduced") or {}
    bridge = str(red.get("client_facing_bridge") or red.get("reduced") or "").strip()
    if bridge:
        out.append(
            {
                "text": clip(bridge, 220),
                "status": "alive",
                "relation": "запрос→сжатие",
            }
        )
    bound = pack.get("bound_slots") or {}
    if isinstance(bound, dict):
        empty = [k for k, v in bound.items() if not v]
        for k in empty[:4]:
            out.append(
                {
                    "text": f"Слот «{k}» не связан — in-out эксперимент без этого входа не закрывается.",
                    "status": "dead",
                    "relation": f"{k}→bind",
                }
            )
    if pack.get("idea_title"):
        out.append(
            {
                "text": f"Эксперимент движка назвал «{clip(pack['idea_title'], 80)}» — тезис жив, пока его можно убить фактом на этой неделе.",
                "status": "alive",
                "relation": "движок→идея",
            }
        )
    if not out:
        out.append(
            {
                "text": f"Движок прогнал «{clip(sit, 72)}», но не сплёвывает убиваемый тезис — заказ ещё пустой.",
                "status": "dead",
                "relation": "движок→тезис",
            }
        )
    seen: set[str] = set()
    uniq: list[dict[str, str]] = []
    for row in out:
        key = row["text"]
        if key in seen:
            continue
        seen.add(key)
        uniq.append(row)
    return uniq[:7]


def config_from_engine(pack: dict[str, Any], *, niche: str) -> dict[str, Any]:
    if not pack.get("ok"):
        return {"ok": False, "slots": {}, "steps": []}
    bound = pack.get("bound_slots") if isinstance(pack.get("bound_slots"), dict) else {}
    steps = list(pack.get("next_steps") or [])
    constructors = [
        _slot_name(r) for r in (pack.get("constructors") or [])[:6]
    ]
    return {
        "ok": True,
        "engine": "metrix_ai",
        "request_id": pack.get("request_id") or "",
        "job": pack.get("idea_title") or "",
        "slots": bound,
        "open_constructors": constructors,
        "handoff": (
            "Конфиг для IT-подрядчика"
            if niche == "saas"
            else "Конфиг для продакшн-агентства / робота"
        ),
        "steps": steps[:5],
        "blurb": clip(str(pack.get("idea_blurb") or ""), 280),
    }


def in_out_from_engine(pack: dict[str, Any], brief: str) -> dict[str, Any]:
    """In-Out experiment: what is expensive in, what is expensive out, what closed."""
    from backend.core.resonance import new_id
    from backend.core.voice import DISCLAIMER

    sit = first_sentence(brief, "эксперимент без имени")
    constructors = pack.get("constructors") or []
    ins = []
    for row in constructors[:4]:
        if isinstance(row, dict):
            ins.append(_slot_name(row))
    idea = pack.get("idea_title") or ""
    nxt = pack.get("next_steps") or []
    closed = idea or (nxt[0] if nxt else "")
    ok = bool(pack.get("ok"))
    steps = nxt[:5] or [
        "Назвать, что дорого на входе.",
        "Назвать, что дорого на выходе.",
        "Закрыть решённое триггером, нерешённое — в параметр.",
    ]
    return {
        "id": new_id(),
        "kind": "chain.experiment",
        "lane": "chain",
        "title": f"In-Out эксперимент · {clip(idea or sit, 48)}",
        "one_liner": (
            "Движок режет стоимость на in и на out. Это эксперимент, не сигнал."
        ),
        "break": (
            f"На входе открыты слоты: {', '.join(ins) or 'не названы'}. "
            "Пока слот пуст — вход дорогой."
        ),
        "move": (
            closed
            or "Решённое закрывается триггером. Нерешённое ставится в параметр, не в новый чат."
        ),
        "steps": [str(s) for s in steps],
        "artifact_week": "Один прогон движка: in-слоты, out-закрытие, что осталось параметром.",
        "anti": [
            "Не читать эксперимент как торговый сигнал.",
            "Не сливать бюджет, пока «Стоп на перемене» не сказал, что тезис жив.",
        ],
        "meta": {
            "engine": "metrix_ai",
            "engine_ok": ok,
            "request_id": pack.get("request_id") or "",
            "in_slots": ins,
            "out_closed": closed,
            "legal": "код согласованной модели, не сигнал",
        },
        "disclaimer": DISCLAIMER,
        "brief": clip(brief, 400),
        "highway": {
            "free": "этот эксперимент",
            "paid": "посадка in-out в контур · Access",
            "sku": "access_month",
        },
    }
