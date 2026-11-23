"""Traction for the 2.9 engine. Not a 3.0, and not a rewrite of contour 2.7.

Pull is how far a named aim moves through real numbers into a build.
Six stations. A later station cannot hold if an earlier one slipped.
The words of the table stay: what came in, what is due, what can be paid.
Yield is not the pull. An exchange order is not placed.
Eval floor is imported and never lowered.
"""

from __future__ import annotations

import re
from typing import Any, Callable

from backend.core.product_eval import THRESHOLD

VERSION = "2.9.0"
LAYER = "traction"
DOES_NOT_REWRITE = "2.7"

ORDER = (
    "aim",
    "volume",
    "table",
    "bridge",
    "engineering",
    "ideas",
)

# A station may open only after these have held.
REQUIRES = {
    "aim": (),
    "volume": ("aim",),
    "table": ("aim", "volume"),
    "bridge": ("aim", "volume", "table"),
    "engineering": ("aim", "volume", "table", "bridge"),
    "ideas": ("aim", "volume", "table", "bridge", "engineering"),
}

STATION_LINE = {
    "aim": "Цель — объёмная закупка.",
    "volume": "Объём назван числом, которое существует.",
    "table": "Что пришло, что должно, что можно заплатить.",
    "bridge": "Мост переносит эти три числа, не обещание дохода.",
    "engineering": "Инженерия открывается лишь на числах, которые существуют.",
    "ideas": "Идеи идут после инженерии, не вместо неё.",
}

REFUSED_PATHS = frozenset(
    {"envelope", "cash_envelope", "no_docs", "mixer", "off_book", "obnal"}
)

YIELD_WORDS = (
    "доходность",
    "гарантир",
    "иксы",
    "пассивный доход",
    "yield",
    "roi ",
    "памп",
)

FOG_WORDS = (
    "кажется",
    "примерно",
    "как-нибудь",
    "потом разбер",
    "в целом",
    "синерг",
    "под ключ",
)

VOLUME_WORDS = (
    "объём",
    "объем",
    "закуп",
    "парти",
    "штук",
    "единиц",
    "пачк",
    "лот",
    "volume",
    "units",
)


def _text(value: Any, limit: int = 240) -> str:
    return str(value or "").strip()[:limit]


def _rows(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [row for row in value if isinstance(row, dict)]


def _num(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"-?\d+(?:[.,]\d+)?", str(value))
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", "."))
    except ValueError:
        return None


def _has_any(text: str, words: tuple[str, ...]) -> bool:
    low = text.lower()
    return any(word in low for word in words)


class _Ctx:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.raw = payload
        self.concept = _text(payload.get("concept") or payload.get("aim") or payload.get("brief"))
        self.solution = _text(payload.get("solution"))
        self.ideas = _text(payload.get("ideas"))
        self.data = _rows(payload.get("data"))
        self.table = _rows(payload.get("table"))
        self.bridge = payload.get("bridge") if isinstance(payload.get("bridge"), dict) else {}
        self.purchase = payload.get("purchase") if isinstance(payload.get("purchase"), dict) else {}
        self.real = [
            row
            for row in self.data
            if row.get("real") is True and _text(row.get("name")) and _text(row.get("value"))
        ]
        self.held: set[str] = set()


Check = Callable[[_Ctx], str | None]


def aim_present(ctx: _Ctx) -> str | None:
    if len(ctx.concept) < 8:
        return "aim_missing"
    return None


def aim_names_volume(ctx: _Ctx) -> str | None:
    blob = f"{ctx.concept} {ctx.solution}"
    if not _has_any(blob, VOLUME_WORDS) and _num(blob) is None:
        return "aim_has_no_volume"
    return None


def aim_is_not_a_yield(ctx: _Ctx) -> str | None:
    if _has_any(ctx.concept, YIELD_WORDS):
        return "aim_is_a_yield"
    return None


def aim_is_not_fog(ctx: _Ctx) -> str | None:
    if _has_any(ctx.concept, FOG_WORDS) and _num(ctx.concept) is None:
        return "aim_is_fog"
    return None


def aim_not_a_door_price(ctx: _Ctx) -> str | None:
    low = ctx.concept.lower()
    if "$50" in low or "дверь за" in low:
        return "aim_is_a_retired_door"
    return None


def volume_has_a_real_row(ctx: _Ctx) -> str | None:
    if not ctx.real:
        return "volume_not_real"
    return None


def volume_row_has_a_number(ctx: _Ctx) -> str | None:
    if not any(_num(row.get("value")) is not None for row in ctx.real):
        return "volume_without_a_number"
    return None


def volume_name_is_a_thing(ctx: _Ctx) -> str | None:
    for row in ctx.real:
        name = _text(row.get("name"))
        if len(name) < 2:
            return "volume_name_empty"
        if _has_any(name, YIELD_WORDS):
            return "volume_name_is_a_yield"
    return None


def volume_drops_unreal(ctx: _Ctx) -> str | None:
    unreal = [row for row in ctx.data if row.get("real") is not True]
    if unreal and not ctx.real:
        return "volume_only_rumor"
    return None


def volume_matches_the_aim(ctx: _Ctx) -> str | None:
    if not ctx.real:
        return None
    aim_num = _num(ctx.concept) or _num(ctx.solution)
    if aim_num is None:
        return None
    values = [_num(row.get("value")) for row in ctx.real]
    values = [n for n in values if n is not None]
    if values and aim_num not in values and min(abs(n - aim_num) for n in values) > 0:
        # The aim may name a total while a row names a part. A part is allowed.
        if all(n > aim_num * 4 for n in values):
            return "volume_far_from_the_aim"
    return None


def table_has_a_line(ctx: _Ctx) -> str | None:
    if not ctx.table:
        return "table_missing"
    return None


def table_has_three_numbers(ctx: _Ctx) -> str | None:
    for row in ctx.table:
        if _num(row.get("in")) is None or _num(row.get("due")) is None or _num(row.get("payable")) is None:
            return "table_missing_a_column"
    return None


def table_words_stay(ctx: _Ctx) -> str | None:
    # The three columns are the pull. A fourth yield column is a slip.
    for row in ctx.table:
        if "yield" in row or "доходность" in row:
            return "table_has_a_yield_column"
    return None


def table_payable_is_possible(ctx: _Ctx) -> str | None:
    for row in ctx.table:
        came = _num(row.get("in"))
        due = _num(row.get("due"))
        payable = _num(row.get("payable"))
        if came is None or due is None or payable is None:
            continue
        if payable < 0 or came < 0 or due < 0:
            return "table_negative"
        if payable > came + 1e-9:
            return "table_pays_more_than_came_in"
        if abs((came - due) - payable) > 0.02 and payable > came - due + 0.02:
            return "table_does_not_meet"
    return None


def table_names_a_person(ctx: _Ctx) -> str | None:
    for row in ctx.table:
        if not _text(row.get("label")):
            return "table_has_no_name"
    return None


def bridge_present(ctx: _Ctx) -> str | None:
    if not ctx.bridge:
        return "bridge_missing"
    return None


def bridge_not_refused(ctx: _Ctx) -> str | None:
    path = _text(ctx.bridge.get("path")).lower()
    if path in REFUSED_PATHS or bool(ctx.bridge.get("off_book")):
        return "bridge_refused"
    return None


def bridge_names_three(ctx: _Ctx) -> str | None:
    giver = _text(ctx.bridge.get("from") or ctx.bridge.get("giver"))
    taker = _text(ctx.bridge.get("to") or ctx.bridge.get("taker"))
    amount = _text(ctx.bridge.get("amount"))
    if not giver or not taker or not amount:
        return "bridge_incomplete"
    if _num(amount) is None:
        return "bridge_amount_not_a_number"
    return None


def bridge_amount_is_on_the_table(ctx: _Ctx) -> str | None:
    amount = _num(ctx.bridge.get("amount"))
    if amount is None:
        return None
    numbers: list[float] = []
    for row in ctx.table:
        for key in ("in", "due", "payable"):
            n = _num(row.get(key))
            if n is not None:
                numbers.append(n)
    for row in ctx.real:
        n = _num(row.get("value"))
        if n is not None:
            numbers.append(n)
    if numbers and not any(abs(n - amount) < 0.02 for n in numbers):
        return "bridge_amount_not_on_the_table"
    return None


def bridge_is_not_a_yield(ctx: _Ctx) -> str | None:
    blob = " ".join(_text(ctx.bridge.get(key)) for key in ("from", "to", "amount", "path"))
    if _has_any(blob, YIELD_WORDS):
        return "bridge_is_a_yield"
    return None


def engineering_waits_for_numbers(ctx: _Ctx) -> str | None:
    if "volume" not in ctx.held or "table" not in ctx.held:
        return "engineering_before_numbers"
    return None


def engineering_has_a_solution(ctx: _Ctx) -> str | None:
    if not ctx.solution and not ctx.concept:
        return "engineering_empty"
    return None


def engineering_closed_on_real_rows(ctx: _Ctx) -> str | None:
    if not ctx.real:
        return "engineering_not_closed"
    return None


def engineering_does_not_invent_a_station(ctx: _Ctx) -> str | None:
    if _has_any(ctx.solution, YIELD_WORDS):
        return "engineering_invents_a_yield"
    return None


def ideas_wait(ctx: _Ctx) -> str | None:
    if "engineering" not in ctx.held:
        return "ideas_before_engineering"
    return None


def ideas_exist(ctx: _Ctx) -> str | None:
    if "engineering" not in ctx.held:
        return None
    if len(ctx.ideas) < 4:
        return "ideas_missing"
    return None


def ideas_do_not_replace_the_build(ctx: _Ctx) -> str | None:
    if ctx.ideas and "engineering" not in ctx.held:
        return "ideas_replace_the_build"
    return None


def ideas_are_not_a_yield(ctx: _Ctx) -> str | None:
    if _has_any(ctx.ideas, YIELD_WORDS):
        return "ideas_are_a_yield"
    return None


def purchase_names_parties(ctx: _Ctx) -> str | None:
    if not ctx.purchase:
        return None
    if not _text(ctx.purchase.get("parties")) or not _text(ctx.purchase.get("scope")):
        return "purchase_unnamed"
    return None


def purchase_not_hidden(ctx: _Ctx) -> str | None:
    if bool(ctx.purchase.get("hidden")) or bool(ctx.purchase.get("off_book")):
        return "purchase_hidden"
    return None


# The order inside a station is the order of the pull.
STATION_CHECKS: dict[str, tuple[Check, ...]] = {
    "aim": (
        aim_present,
        aim_names_volume,
        aim_is_not_a_yield,
        aim_is_not_fog,
        aim_not_a_door_price,
    ),
    "volume": (
        volume_has_a_real_row,
        volume_row_has_a_number,
        volume_name_is_a_thing,
        volume_drops_unreal,
        volume_matches_the_aim,
    ),
    "table": (
        table_has_a_line,
        table_has_three_numbers,
        table_words_stay,
        table_payable_is_possible,
        table_names_a_person,
    ),
    "bridge": (
        bridge_present,
        bridge_not_refused,
        bridge_names_three,
        bridge_amount_is_on_the_table,
        bridge_is_not_a_yield,
    ),
    "engineering": (
        engineering_waits_for_numbers,
        engineering_has_a_solution,
        engineering_closed_on_real_rows,
        engineering_does_not_invent_a_station,
        purchase_names_parties,
        purchase_not_hidden,
    ),
    "ideas": (
        ideas_wait,
        ideas_exist,
        ideas_do_not_replace_the_build,
        ideas_are_not_a_yield,
    ),
}


def _run_station(name: str, ctx: _Ctx) -> dict[str, Any]:
    slips: list[str] = []
    missing = [need for need in REQUIRES[name] if need not in ctx.held]
    if missing:
        slips.append("needs:" + ",".join(missing))
    else:
        for check in STATION_CHECKS[name]:
            reason = check(ctx)
            if reason:
                slips.append(reason)
    held = not slips
    if held:
        ctx.held.add(name)
    return {
        "station": name,
        "line": STATION_LINE[name],
        "held": held,
        "slips": slips,
    }


def pull(payload: dict[str, Any] | None) -> dict[str, Any]:
    """One pass of traction. Later stations do not open over a slip."""
    ctx = _Ctx(payload or {})
    stations = [_run_station(name, ctx) for name in ORDER]
    held = [row["station"] for row in stations if row["held"]]
    slipped = [row["station"] for row in stations if not row["held"]]
    asked = (payload or {}).get("eval_floor")
    ignored = False
    if asked is not None:
        try:
            ignored = float(asked) < THRESHOLD
        except (TypeError, ValueError):
            ignored = True
    return {
        "ok": True,
        "version": VERSION,
        "layer": LAYER,
        "does_not_rewrite": DOES_NOT_REWRITE,
        "eval_floor": THRESHOLD,
        "floor_lowered": False,
        "floor_request_ignored": ignored,
        "yield_promised": False,
        "exchange_orders": False,
        "orders_placed": 0,
        "order": list(ORDER),
        "held": held,
        "slipped": slipped,
        "traction": round(len(held) / len(ORDER), 4),
        "stations": stations,
        "table_words": ["пришло", "должно", "можно заплатить"],
    }


def pull_brief(brief: str) -> dict[str, Any]:
    """Read a loose brief into the same six stations. Does not invent numbers."""
    text = _text(brief, 800)
    numbers = re.findall(r"\d+(?:[.,]\d+)?", text)
    rows: list[dict[str, Any]] = []
    if numbers:
        rows.append({"name": "из текста", "value": numbers[0], "real": True})
    table: list[dict[str, Any]] = []
    if len(numbers) >= 3:
        table.append(
            {
                "label": "из текста",
                "in": numbers[0],
                "due": numbers[1],
                "payable": numbers[2],
            }
        )
    return pull(
        {
            "concept": text,
            "solution": text if rows else "",
            "ideas": "",
            "data": rows,
            "table": table,
            "bridge": {},
            "purchase": {},
        }
    )
