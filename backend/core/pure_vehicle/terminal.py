"""Terminal of any scheme: IN → OUT → REALIZE. Not a chat and not a new line."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from backend.core.pure_vehicle.catalog import (
    FREE12,
    KILL,
    ensure_stores,
    open_consequences,
    ops_by_n,
    recurse_status,
)
from backend.core.pure_vehicle.store import read_json, write_json
from backend.core.voice import clip

_OP_HINTS: tuple[tuple[int, tuple[str, ...]], ...] = (
    (2, ("чип", "rtl", "fpga", "прибор", "прошив")),
    (3, ("бренд", "кадр", "голос", "x.com")),
    (4, ("библиотек", "карточек пак", "library")),
    (5, ("кто платит", "рельс", "продаж")),
    (1, ("a2a", "скринер", "навод")),
    (7, ("поток", "касс", "посад", "актив")),
    (6, ("метрик", "качеств", "спек")),
)

_CONSEQUENCE_HINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("recurse_spec", ("рекурс", "recurse")),
    ("plant_cash", ("касс", "актив", "посад")),
    ("isolate_freelance", ("фриланс", "isolated")),
    ("one_robot_paper", ("робот", "paper", "scan all")),
    ("green", ("клише", "green", "короч")),
    ("contribute", ("шаблон", "в базу")),
    ("library_card", ("библиотек", "карточка")),
    ("owner_monday", ("понедельник", "хозяин")),
    ("cut_support", ("поддерж", "support")),
    ("individualize", ("тикер", "слот")),
    ("direct_next", ("следующий ход", "direct")),
    ("kill_branch", ("убить", "ветк", "kill")),
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _text(situation: dict[str, Any]) -> str:
    return str(situation.get("text") or situation.get("brief") or situation.get("situation") or "").strip()


def _sku(situation: dict[str, Any]) -> str:
    return str(situation.get("sku") or "allo_month").strip() or "allo_month"


def paying_asset(situation: dict[str, Any]) -> dict[str, Any] | None:
    raw = situation.get("base_asset")
    if isinstance(raw, dict) and raw.get("pays") is True and (raw.get("id") or raw.get("ticker")):
        return {"id": str(raw.get("id") or raw.get("ticker")), "ticker": str(raw.get("ticker") or raw.get("id"))}
    return None


def _pick_op(situation: dict[str, Any], text: str) -> dict[str, Any]:
    forced = situation.get("op") or situation.get("line")
    if forced is not None:
        try:
            return ops_by_n(int(forced))
        except (KeyError, TypeError, ValueError):
            pass
    low = text.lower()
    for n, hints in _OP_HINTS:
        if any(h in low for h in hints):
            return ops_by_n(n)
    return ops_by_n(6)


def _pick_consequence(situation: dict[str, Any], text: str, sku: str) -> dict[str, Any]:
    opened = open_consequences(sku)
    asked = str(situation.get("consequence") or "").strip()
    if not asked:
        low = text.lower()
        for cid, hints in _CONSEQUENCE_HINTS:
            if any(h in low for h in hints):
                asked = cid
                break
    if asked == "recurse_spec" and asked not in opened:
        return {
            "id": "kill_branch",
            "open": True,
            "asked": "recurse_spec",
            "closed": recurse_status(sku),
            "line": KILL["kill_branch"],
        }
    if asked not in FREE12:
        asked = "kill_branch"
    if asked not in opened:
        return {
            "id": "kill_branch",
            "open": True,
            "asked": asked,
            "closed": recurse_status(sku) if asked == "recurse_spec" else {"id": asked, "open": False},
            "line": KILL["kill_branch"],
        }
    return {"id": asked, "open": True, "line": KILL[asked], "closed": None}


def _door_in(situation: dict[str, Any], text: str) -> dict[str, Any]:
    from backend.core.life_intake import problem_phrase, solution_phrase

    code = str(situation.get("door") or "").strip()
    bound = ""
    if code:
        from backend.core.door import bind, load

        rec = load(code)
        if rec:
            bind(rec["code"], brief=clip(text, 400), room="pure_vehicle")
            bound = rec["code"]
    return {
        "via": "door" if bound else "life_intake",
        "door": bound,
        "situation": clip(text, 240),
        "problem": problem_phrase(text or "пустой вход", "ru"),
        "solution": solution_phrase(text or "пустой вход", "ru"),
    }


def _realize(situation: dict[str, Any], text: str, op: dict[str, Any], consequence: str) -> dict[str, Any]:
    asset = paying_asset(situation)
    if asset is None:
        return {
            "ok": False,
            "landed": False,
            "stub": bool(op.get("stub")),
            "sell_as_ready": False,
            "refusal": "no_base_asset",
            "chat": False,
            "new_product": False,
            "line": "Базового актива, который уже платит, нет. Посадки нет.",
        }
    if op.get("stub"):
        return {
            "ok": False,
            "landed": False,
            "stub": True,
            "sell_as_ready": False,
            "chat": False,
            "new_product": False,
            "asset": asset["id"],
            "line": f"Линия {op['n']} — stub. Готовой посадкой не продаётся.",
        }
    seat: dict[str, Any] = {}
    try:
        from backend.core.terminal_ai import place

        placed = place(text or asset["id"])
        seat = {
            "where": (placed.get("seat") or {}).get("where"),
            "kill": (placed.get("seat") or {}).get("kill"),
        }
    except Exception as exc:  # noqa: BLE001
        seat = {"error": str(exc)[:120]}
    fin_id = "orientationforge"
    fin_ok = False
    try:
        from backend.fin_models.registry import get_fin_model_registry

        reg = get_fin_model_registry()
        known = {row["id"] for row in reg.list_models()}
        fin_id = asset["id"] if asset["id"] in known else "orientationforge"
        reg.run(fin_id, {"business": clip(text, 280), "ticker": asset["ticker"]})
        fin_ok = True
    except Exception as exc:  # noqa: BLE001
        fin_ok = False
        seat["fin_error"] = str(exc)[:120]
    return {
        "ok": True,
        "landed": True,
        "stub": False,
        "chat": False,
        "new_product": False,
        "asset": asset["id"],
        "fin_model": fin_id,
        "fin_ok": fin_ok,
        "seat": seat,
        "consequence": consequence,
        "line": f"Актив {asset['id']} уже платит. Стул линии 7. Новый продукт не открыт.",
    }


def constructor(situation: dict[str, Any] | str) -> dict[str, Any]:
    """One operation of seven, one open consequence of twelve. Writes the terminal."""
    if isinstance(situation, str):
        situation = {"text": situation, "sku": "allo_month"}
    situation = dict(situation or {})
    ensure_stores()
    text = _text(situation)
    sku = _sku(situation)
    op = _pick_op(situation, text)
    consequence = _pick_consequence(situation, text, sku)
    entered = _door_in(situation, text)
    out = {"kill": consequence["line"], "consequence": consequence["id"]}
    realized = _realize(situation, text, op, consequence["id"])
    if consequence.get("closed") and consequence["closed"].get("id") == "recurse_spec":
        realized = {
            **realized,
            "recurse_spec": False,
            "recurse_why": consequence["closed"].get("why"),
        }
    record = {
        "version": "2.1.0",
        "codename": "PURE VEHICLE",
        "at": _now(),
        "sku": sku,
        "ok": bool(realized.get("ok")),
        "in": entered,
        "out": out,
        "realize": realized,
        "op": op,
        "consequence": consequence,
        "recurse_spec": recurse_status(sku),
        "financial_landing": realized,
        "new_product": False,
        "eighth_operation": False,
    }
    book = read_json("terminals.json", {"version": "2.1.0", "rows": []})
    rows = list(book.get("rows") or [])
    rows.append(
        {
            "at": record["at"],
            "sku": sku,
            "op": op["n"],
            "consequence": consequence["id"],
            "ok": record["ok"],
            "refusal": realized.get("refusal"),
        }
    )
    book["rows"] = rows[-200:]
    book["version"] = "2.1.0"
    write_json("terminals.json", book)
    return record
