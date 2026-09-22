"""Owner view of custom specs and recursive files.

Open when METRIX_OWNER_OPEN=1 or backend/data/owner_open.json exists.
The public page for a ticker is written under public/owner-specs/.
"""

from __future__ import annotations

import html
import json
import os
from pathlib import Path
from typing import Any

from backend.config import DATA_DIR


def owner_specs_open() -> bool:
    if (os.getenv("METRIX_OWNER_OPEN") or "").strip() in ("1", "true", "yes"):
        return True
    return (DATA_DIR / "owner_open.json").is_file()


def grant_owner() -> dict[str, Any]:
    path = DATA_DIR / "owner_open.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = {"open": True, "scope": "specs", "who": "owner"}
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    return rec


def publish_page(
    pack: dict[str, Any],
    custom: dict[str, Any],
    recursive: dict[str, Any] | None = None,
    before: dict[str, Any] | None = None,
) -> str:
    """Write a readable spec page into the public tree."""
    root = Path(__file__).resolve().parents[2] / "public" / "owner-specs"
    root.mkdir(parents=True, exist_ok=True)
    tick = str(pack.get("ticker") or "MX")
    problem = str(pack.get("problem") or "")
    solution = str(pack.get("solution") or "")
    variants = pack.get("variants") or custom.get("variants") or []
    specs = custom.get("specs") or []
    v_html = "".join(
        f"<li><b>{v.get('title')}</b> — {v.get('task')} <span class='muted'>{v.get('sku')}</span></li>"
        for v in variants
    )
    s_html = "".join(
        f"<article class='card'><p class='muted'>{s.get('title')}</p><p>{s.get('text')}</p></article>"
        for s in specs
    )
    rec_note = "Рекурсивный файл собран." if (recursive or {}).get("file") else "Рекурсия ещё не собрана."
    before = before or {}
    diff_rows = ""
    if before:
        pairs = (
            ("Суть", before.get("problem"), problem),
            ("Решение", before.get("solution"), solution),
            ("Вариант 1", before.get("variant"), (variants[0].get("task") if variants else "")),
            ("Библиотека", before.get("library"), (pack.get("sit") or {}).get("library")),
            ("Понедельник", before.get("monday"), (pack.get("sit") or {}).get("monday")),
        )
        diff_rows = "".join(
            f"<tr><th>{html.escape(name)}</th><td>{html.escape(str(old or ''))}</td><td>{html.escape(str(new or ''))}</td></tr>"
            for name, old, new in pairs
        )
    diff_block = (
        f"<h2>Разница: было и стало</h2><table><tr><th></th><th>Было</th><th>Стало</th></tr>{diff_rows}</table>"
        if diff_rows
        else ""
    )
    html_doc = f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"/>
<title>{tick} · спеки</title>
<style>
body{{margin:0;background:#070a0f;color:#e8eef7;font:16px/1.55 system-ui,sans-serif}}
main{{max-width:760px;margin:0 auto;padding:2rem 1.2rem 4rem}}
h1{{font-size:1.8rem;letter-spacing:-.03em}}
.chip{{display:inline-block;border:1px solid rgba(94,234,212,.4);color:#5eead4;
padding:.2rem .6rem;border-radius:999px;font:700 12px/1.4 ui-monospace,monospace}}
.pair{{display:grid;gap:.8rem;grid-template-columns:1fr 1fr;margin:1.2rem 0}}
.grid{{display:grid;gap:.8rem}}
.card{{background:#111822;border:1px solid rgba(148,163,184,.16);border-radius:14px;padding:1rem}}
.muted{{color:#94a3b8}}
a{{color:#5eead4}}
table{{width:100%;border-collapse:collapse;margin:1rem 0}}
th,td{{border:1px solid rgba(148,163,184,.2);padding:.55rem .7rem;vertical-align:top;text-align:left}}
th{{color:#94a3b8;font-weight:600}}
</style></head><body><main>
<span class="chip">{tick}</span>
<p class="muted">Web3 Store · $100 кастом спека · $490 рекурсия</p>
<h1>{problem}</h1>
{diff_block}
<div class="pair">
<article class="card"><p class="muted">Суть</p><p>{problem}</p></article>
<article class="card"><p class="muted">Решение</p><p>{solution}</p></article>
</div>
<h2>Варианты · мелкие задачи</h2>
<ul>{v_html}</ul>
<h2>Кастом спека · $100</h2>
<div class="grid">{s_html}</div>
<h2>Рекурсия · $490</h2>
<p>{rec_note}</p>
<p class="muted">Вопросы идут на уровне normal, не на максимальном абстрактном.</p>
<p class="muted">Свой контур. Вечный B2B снят.</p>
</main></body></html>"""
    page = root / f"{tick}.html"
    page.write_text(html_doc, encoding="utf-8")
    index = root / "index.html"
    index.write_text(
        f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"/><title>Спеки · Metrix</title>
<style>
body{{margin:0;background:#070a0f;color:#e8eef7;font:16px/1.55 system-ui,sans-serif}}
main{{max-width:720px;margin:0 auto;padding:2rem 1.2rem}}
a{{color:#5eead4}}
</style></head><body><main>
<h1>Спеки владельца</h1>
<p><a href="{tick}.html">{tick}</a> — {problem}</p>
</main></body></html>""",
        encoding="utf-8",
    )
    return str(page)
