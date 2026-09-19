"""Paid file: recursive methodology + specs + same-engine overlay.

$100 does not get a file. 490 / 1000 / 10000 do.
"""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.core.code_overlay import build_overlay, inspect_overlay
from backend.core.circle_system.chain_store import load_chain, save_chain
from backend.core.pricing_lanes import sku_of
from backend.core.ticker_registry import bind_ticker, load_ticker


NO_FILE_SKUS = frozenset({"sku_100", "free_life"})


def _dir() -> Path:
    from backend.config import DATA_DIR

    p = DATA_DIR / "product_files"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _methodology(pack: dict[str, Any], lang: str) -> str:
    ru = not (lang or "ru").lower().startswith("en")
    tick = pack.get("ticker") or "MX"
    problem = pack.get("problem") or ""
    solution = pack.get("solution") or ""
    if ru:
        return (
            f"# {tick} · рекурсивная методика\n\n"
            f"Плотнее спеки, тот же контур. Комнаты, не новая линейка.\n\n"
            f"## Суть\n{problem}\n\n"
            f"## Решение\n{solution}\n\n"
            "## Рекурсия\n"
            "1. Bound — именованная поломка.\n"
            "2. Kill / slot / library — границы, посадка, конкретная библиотека.\n"
            "3. In / out / owner — где горят часы, кто нажимает.\n"
            "4. Monday / escalate — цифра и N минут.\n"
            "Глубина ≤ 4. Лист — когда узел больше не делится без новой линейки.\n\n"
            "## Kill\n"
            "Не авто-доход. Не эссе. Не вторая линейка продуктов.\n"
        )
    return (
        f"# {tick} · recursive methodology\n\n"
        f"Denser specs, same contour. Rooms, not a new product line.\n\n"
        f"## Problem\n{problem}\n\n"
        f"## Solution\n{solution}\n\n"
        "## Recursion\n"
        "1. Bound — named leak.\n"
        "2. Kill / slot / library.\n"
        "3. In / out / owner.\n"
        "4. Monday / escalate.\n"
        "Depth ≤ 4. A leaf is a node that would otherwise open a new product line.\n"
    )


def _html(pack: dict[str, Any], overlay_src: str, method: str, sku: dict[str, Any]) -> str:
    tick = html.escape(str(pack.get("ticker") or ""))
    problem = html.escape(str(pack.get("problem") or ""))
    solution = html.escape(str(pack.get("solution") or ""))
    method_h = html.escape(method)
    src_h = html.escape(overlay_src)
    sku_name = html.escape(str(sku.get("name_ru") or sku.get("id") or ""))
    return f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"/>
<title>{tick} · Metrix overlay</title>
<style>
body{{margin:0;background:#070a0f;color:#e8eef7;font:16px/1.55 system-ui,sans-serif}}
main{{max-width:720px;margin:0 auto;padding:2rem 1.2rem 4rem}}
h1{{font-size:1.8rem;letter-spacing:-.03em}}
.chip{{display:inline-block;border:1px solid rgba(94,234,212,.4);color:#5eead4;
padding:.2rem .6rem;border-radius:999px;font:700 12px/1.4 ui-monospace,monospace}}
.pair{{display:grid;gap:.8rem;grid-template-columns:1fr 1fr;margin:1.2rem 0}}
.card{{background:#111822;border:1px solid rgba(148,163,184,.16);border-radius:14px;padding:1rem}}
pre{{white-space:pre-wrap;background:#0b1118;border:1px solid rgba(94,234,212,.18);
padding:1rem;border-radius:12px;overflow:auto;font-size:.82rem}}
.muted{{color:#94a3b8}}
</style></head><body><main>
<span class="chip">{tick}</span>
<p class="muted">{sku_name}</p>
<h1>Плотнее спеки. Тот же контур.</h1>
<div class="pair">
<article class="card"><p class="muted">Суть</p><p>{problem}</p></article>
<article class="card"><p class="muted">Решение</p><p>{solution}</p></article>
</div>
<h2>Методика</h2>
<pre>{method_h}</pre>
<h2>Кодовая надстройка</h2>
<pre>{src_h}</pre>
<p class="muted">Не обещание доходности. Overlay того же движка.</p>
</main></body></html>"""


def generate_paid_file(
    ticker: str,
    *,
    sku_id: str = "sku_490",
    lang: str = "ru",
) -> dict[str, Any]:
    if sku_id in NO_FILE_SKUS:
        return {
            "ok": False,
            "file": False,
            "sku": sku_id,
            "reason": "sku_100_no_file",
            "note": "После $100 файл не отдаётся. 120 запросов — и всё.",
        }
    chain = load_chain(ticker) or load_ticker(ticker) or {}
    if not chain.get("ticker"):
        chain["ticker"] = ticker
    problem = chain.get("problem") or ""
    solution = chain.get("solution") or ""
    answers = chain.get("answers") or {}
    overlay = build_overlay(
        ticker=ticker,
        problem=problem,
        solution=solution,
        specs={
            "bound": problem,
            "slot": solution,
            "kill": "новая линейка / авто-доход / эссе",
            "library": (answers.get("library") or "concrete library"),
            "monday": answers.get("monday") or "Monday number",
            "owner": answers.get("who") or answers.get("owner") or "named owner",
        },
        answers=answers,
        lang=lang,
    )
    q = overlay.get("quality") or inspect_overlay(overlay.get("source") or "", ticker=ticker)
    if not q.get("go"):
        # Do not bounce: repair once by rebuilding. If still weak, ship with CONDITIONAL and the source.
        overlay = build_overlay(
            ticker=ticker,
            problem=problem or "named leak in the contour",
            solution=solution or "sit the object in a named slot",
            specs=None,
            answers=answers,
            lang=lang,
        )
        q = overlay.get("quality") or inspect_overlay(overlay.get("source") or "", ticker=ticker)
    method = _methodology(chain, lang)
    sku = sku_of(sku_id)
    html_doc = _html(chain, overlay.get("source") or "", method, sku)
    folder = _dir() / ticker
    folder.mkdir(parents=True, exist_ok=True)
    py_path = folder / overlay["filename"]
    md_path = folder / f"{ticker}.md"
    html_path = folder / f"{ticker}.html"
    json_path = folder / f"{ticker}.json"
    py_path.write_text(overlay["source"], encoding="utf-8")
    md_path.write_text(method + "\n\n```python\n" + overlay["source"] + "\n```\n", encoding="utf-8")
    html_path.write_text(html_doc, encoding="utf-8")
    payload = {
        "ticker": ticker,
        "sku": sku_id,
        "created": _now(),
        "problem": problem,
        "solution": solution,
        "eval": chain.get("eval") or {},
        "overlay_quality": q,
        "paths": {
            "py": str(py_path),
            "md": str(md_path),
            "html": str(html_path),
            "json": str(json_path),
        },
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    save_chain({**chain, "chain_id": ticker, "paid_file": payload, "sku": sku_id})
    bind_ticker(ticker, sku=sku_id, file=True, quality=q)
    return {
        "ok": True,
        "file": True,
        "ticker": ticker,
        "sku": sku_id,
        "quality": q,
        "source": overlay["source"],
        "methodology": method,
        "paths": payload["paths"],
        "py_path": str(py_path),
        "html_path": str(html_path),
        "filename": overlay["filename"],
    }
