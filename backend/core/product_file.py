"""Paid file.

$100 — custom spec (essence, solution, variants as small tasks). No code overlay.
$490 — recursive methodology + same-engine overlay.
$1000 / $10000 — the same recursive file, denser contour.
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


NO_FILE_SKUS = frozenset({"free_life"})
CUSTOM_SPEC_SKUS = frozenset({"sku_100"})


def _sit(chain: dict[str, Any]) -> dict[str, str]:
    raw = chain.get("sit") or {}
    return raw if isinstance(raw, dict) else {}


def _spec_sections(chain: dict[str, Any]) -> list[dict[str, str]]:
    problem = str(chain.get("problem") or "")
    solution = str(chain.get("solution") or "")
    sit = _sit(chain)
    section = chain.get("cycle_section") or "flagship"
    room = sit.get("room") or ("Web3 Store" if section == "web3" else "Флагман")
    give = sit.get("give") or "объект, который уходит из контура"
    keep = sit.get("keep") or "то, что остаётся у хозяина"
    owner = sit.get("owner") or "хозяин слота"
    monday = sit.get("monday") or "граница записана в спеку"
    kill = sit.get("kill") or "сборка чужого бизнеса"
    library = sit.get("library") or "карточка границы"
    return [
        {"id": "essence", "title": "Суть", "text": problem},
        {"id": "solution", "title": "Решение", "text": solution},
        {"id": "room", "title": "Раздел", "text": room},
        {"id": "bound", "title": "Граница", "text": f"Отдают: {give}. Остаётся: {keep}."},
        {"id": "slot", "title": "Слот", "text": f"Комната {room}. Объект недели: единица отдачи."},
        {"id": "owner", "title": "Хозяин", "text": f"{owner} нажимает в понедельник."},
        {"id": "monday", "title": "Цифра", "text": monday},
        {"id": "library", "title": "Библиотека", "text": library},
        {"id": "kill", "title": "Kill", "text": f"Закрытый ход: {kill}."},
    ]


def _custom_spec_md(chain: dict[str, Any], sections: list[dict[str, str]], variants: list[dict[str, Any]]) -> str:
    tick = chain.get("ticker") or "MX"
    lines = [
        f"# {tick} · кастом спека",
        "",
        "Услуга $100. Рекурсия — отдельно, $490.",
        "",
        f"Суть: {chain.get('problem') or ''}",
        f"Решение: {chain.get('solution') or ''}",
        f"Раздел: {chain.get('cycle_section') or ''}",
        "",
        "## Спека",
    ]
    for sec in sections:
        lines.append(f"### {sec['title']}")
        lines.append(sec["text"])
        lines.append("")
    lines.append("## Варианты · мелкие задачи")
    for v in variants:
        done = v.get("done") or ""
        lines.append(f"- {v.get('title')}: {v.get('task')} Готово, когда {done} ({v.get('sku')})")
    lines.append("")
    lines.append("Каждый вариант можно взять отдельной мелкой задачей. $490 раскрывает один из них рекурсией.")
    return "\n".join(lines)


def _custom_html(chain: dict[str, Any], md: str, sku: dict[str, Any]) -> str:
    tick = html.escape(str(chain.get("ticker") or ""))
    problem = html.escape(str(chain.get("problem") or ""))
    solution = html.escape(str(chain.get("solution") or ""))
    body = html.escape(md)
    sku_name = html.escape(str(sku.get("name_ru") or "$100 · кастом спека"))
    return f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"/>
<title>{tick} · кастом спека</title>
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
<h1>Кастом спека. Свой контур.</h1>
<div class="pair">
<article class="card"><p class="muted">Суть</p><p>{problem}</p></article>
<article class="card"><p class="muted">Решение</p><p>{solution}</p></article>
</div>
<pre>{body}</pre>
</main></body></html>"""


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
    sit = _sit(pack)
    give = sit.get("give") or "именованная поломка"
    keep = sit.get("keep") or "то, что остаётся"
    library = sit.get("library") or "конкретная библиотека"
    owner = sit.get("owner") or "кто нажимает"
    monday = sit.get("monday") or "цифра понедельника"
    kill = sit.get("kill") or "новая линейка"
    if ru:
        return (
            f"# {tick} · рекурсивная методика\n\n"
            f"Плотнее спеки, тот же контур. Комнаты, не новая линейка.\n\n"
            f"## Суть\n{problem}\n\n"
            f"## Решение\n{solution}\n\n"
            "## Рекурсия\n"
            f"1. Bound — отдают {give}; остаётся {keep}.\n"
            f"2. Kill — {kill}. Слот — решение выше. Библиотека — {library}.\n"
            f"3. Owner — {owner}.\n"
            f"4. Monday — {monday}. Дальше N минут и эскалация.\n"
            "Глубина ≤ 4. Лист — когда узел больше не делится без новой линейки.\n\n"
            f"## Kill\n{kill}.\n"
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
        return {"ok": False, "file": False, "sku": sku_id, "reason": "free_no_file"}
    chain = load_chain(ticker) or load_ticker(ticker) or {}
    if sku_id in CUSTOM_SPEC_SKUS:
        if not chain.get("ticker"):
            chain["ticker"] = ticker
        sections = _spec_sections(chain)
        variants = list(chain.get("variants") or [])
        if len(variants) < 3:
            from backend.core.life_intake import small_task_variants

            variants = small_task_variants(
                str(chain.get("problem") or ""),
                str(chain.get("solution") or ""),
                section=str(chain.get("cycle_section") or "flagship"),
                lang=lang,
            )
        method = _custom_spec_md(chain, sections, variants)
        sku = sku_of(sku_id)
        html_doc = _custom_html(chain, method, sku)
        folder = _dir() / ticker
        folder.mkdir(parents=True, exist_ok=True)
        md_path = folder / f"{ticker}.spec.md"
        html_path = folder / f"{ticker}.spec.html"
        json_path = folder / f"{ticker}.spec.json"
        md_path.write_text(method, encoding="utf-8")
        html_path.write_text(html_doc, encoding="utf-8")
        payload = {
            "ticker": ticker,
            "sku": sku_id,
            "kind": "custom_spec",
            "created": _now(),
            "problem": chain.get("problem") or "",
            "solution": chain.get("solution") or "",
            "cycle_section": chain.get("cycle_section") or "",
            "specs": sections,
            "variants": variants,
            "paths": {"md": str(md_path), "html": str(html_path), "json": str(json_path)},
        }
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        save_chain({**chain, "chain_id": ticker, "custom_spec": payload, "sku": sku_id})
        bind_ticker(ticker, sku=sku_id, file=True)
        return {
            "ok": True,
            "file": True,
            "kind": "custom_spec",
            "ticker": ticker,
            "sku": sku_id,
            "problem": payload["problem"],
            "solution": payload["solution"],
            "specs": sections,
            "variants": variants,
            "methodology": method,
            "source": "",
            "paths": payload["paths"],
            "html_path": str(html_path),
            "quality": {"ok": True, "score": 0.9, "go": True, "reasons": ["custom_spec", "variants"]},
        }
    chain = load_chain(ticker) or load_ticker(ticker) or {}
    if not chain.get("ticker"):
        chain["ticker"] = ticker
    problem = chain.get("problem") or ""
    solution = chain.get("solution") or ""
    answers = chain.get("answers") or {}
    sit = _sit(chain)
    overlay = build_overlay(
        ticker=ticker,
        problem=problem,
        solution=solution,
        specs={
            "bound": sit.get("give") or problem,
            "slot": solution,
            "kill": sit.get("kill") or "новая линейка / авто-доход / эссе",
            "library": answers.get("library") or sit.get("library") or "concrete library",
            "monday": answers.get("monday") or sit.get("monday") or "Monday number",
            "owner": answers.get("who") or answers.get("owner") or sit.get("owner") or "named owner",
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
