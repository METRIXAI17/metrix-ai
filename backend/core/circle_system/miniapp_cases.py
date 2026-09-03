"""Mini-app case packer. Only if assembly and consistency gates pass."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.config import PROJECT_ROOT
from backend.core.circle_system.chain_store import load_chain, save_chain
from backend.core.naming_canon import case_sigil, public_gloss

CASES_DIR = PROJECT_ROOT / "public" / "cases"

GATES = {
    "assembly": 0.45,
    "consistency": 0.62,
    "predicted_end": 0.7,
}


def _gates_ok(g: dict[str, Any]) -> bool:
    if float(g.get("assembly") or g.get("assembly_score") or 0) < GATES["assembly"]:
        return False
    if float(g.get("consistency") or g.get("consistency_score") or 0) < GATES["consistency"]:
        return False
    if str(g.get("risk") or "") == "high":
        return False
    return True


def pack_miniapp_case(chain_id: str, *, lang: str = "en") -> dict[str, Any]:
    rec = load_chain(chain_id)
    if not rec:
        return {"ok": False, "error": "unknown_chain"}
    ra = rec.get("resource_assembly") or {}
    gates = rec.get("gates") or {
        "assembly": rec.get("assembly_score") or ra.get("compatibility") or 0,
        "consistency": rec.get("consistency") or 0,
        "risk": rec.get("risk") or "medium",
        "predicted_end": rec.get("predicted_end") or 0,
    }
    if not _gates_ok(gates):
        return {"ok": False, "error": "gates_closed", "gates": gates}

    closed = sorted((ra.get("bound_slots") or {}).keys())
    sig = case_sigil(str(rec.get("chain_seed") or chain_id), closed)
    artefacts = rec.get("artefacts_applied") or []
    ru = lang.startswith("ru")
    scenario = {
        "sigil": sig,
        "screen": (
            "Один экран: какие слоты закрыты, какой gate открыл Main."
            if ru
            else "One screen: which slots closed, which gate opened Main."
        ),
        "closed_slots": closed,
        "artefacts_in": [a.get("id") or a.get("sigil") for a in artefacts][:8],
        "main_gate": "predicted_end≥0.7 and risk≠high and assembly≥0.45",
        "extends": [
            "ChipForge",
            "OrientationForge",
            "EdgeForge",
            "MetaObject",
            "PrologForge",
            "MarketForge",
            "Circle Runtime",
        ],
        "tooltip": public_gloss(sig, lang=lang),
    }
    html = _html(scenario, lang=lang)
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    path = CASES_DIR / f"{sig}.html"
    path.write_text(html, encoding="utf-8")
    rec["miniapp_case"] = {"sigil": sig, "path": f"/cases/{sig}.html"}
    save_chain(rec)
    return {
        "ok": True,
        "sigil": sig,
        "url": f"/app/cases/{sig}.html",
        "case": scenario,
        "gates": gates,
    }


def _html(scenario: dict[str, Any], *, lang: str) -> str:
    slots = "".join(f"<li>{s}</li>" for s in scenario["closed_slots"])
    arts = "".join(f"<li>{s}</li>" for s in scenario["artefacts_in"])
    return f"""<!DOCTYPE html>
<html lang="{lang[:2]}">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{scenario['sigil']} · Metrix case</title>
<style>body{{font-family:Segoe UI,system-ui,sans-serif;background:#070a0f;color:#e8eef7;max-width:640px;margin:2rem auto;padding:0 1rem}}
.sigil{{color:#5eead4;letter-spacing:.08em}} a{{color:#67e8f9}}</style></head>
<body>
<p class="sigil">{scenario['sigil']}</p>
<h1>Mini-app case</h1>
<p>{scenario['screen']}</p>
<p>{scenario['tooltip']}</p>
<h2>Closed slots</h2><ul>{slots}</ul>
<h2>Artefacts in</h2><ul>{arts}</ul>
<p>Gate: {scenario['main_gate']}</p>
<p>Extends original projects, not a seventh business.</p>
<p><a href="/">Metrix AI</a></p>
</body></html>"""
