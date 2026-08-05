"""
Skill memory — harness-style memory management.

Each successful Generate run can be distilled into a specialized skill:
  - conceptual algorithm (what / why / warrants)
  - executive algorithm (how / steps / kill / proof)

Memory is file-backed under backend/data/skill_memory/ (ephemeral on Railway
unless volume mounted — still works for local + in-response distill).
"""

from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path
from typing import Any

try:
    from backend.config import DATA_DIR as _DATA
except Exception:  # pragma: no cover
    _DATA = Path(__file__).resolve().parents[2] / "data"

MEMORY_DIR = Path(_DATA) / "skill_memory"
MAX_SKILLS = 80
MAX_LOAD = 8


def _ensure_dir() -> Path:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    return MEMORY_DIR


def _slug(text: str, n: int = 40) -> str:
    s = re.sub(r"[^a-zA-Z0-9а-яА-Я_-]+", "-", (text or "").strip().lower())
    s = re.sub(r"-+", "-", s).strip("-")
    return (s or "skill")[:n]


def list_skills(limit: int = MAX_LOAD) -> list[dict[str, Any]]:
    d = _ensure_dir()
    files = sorted(d.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    out: list[dict[str, Any]] = []
    for f in files[: max(limit, MAX_LOAD)]:
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            continue
    return out[:limit]


def distill_skill_from_run(
    *,
    business_text: str,
    core_report: dict[str, Any],
    routing: dict[str, Any] | None = None,
    personality: dict[str, Any] | None = None,
    quality: dict[str, Any] | None = None,
    project_name: str = "",
    lang: str = "ru",
    persist: bool = True,
) -> dict[str, Any]:
    """
    Convert a successful run into conceptual + executive algorithms.
    Persist when quality/commit warrants it.
    """
    cr = core_report or {}
    route = routing or {}
    pers = personality or {}
    q = quality or {}
    conf = float(q.get("confidence") or 0.0)
    commit = bool(q.get("commit_ready"))
    band = (cr.get("value_vs_core") or {}).get("band") or ""
    success = commit or conf >= 0.55 or band in ("near_core", "orientation_plus")

    domain = route.get("domain") or (cr.get("profile") or {}).get("profile") or "generic"
    title = project_name or cr.get("title") or "Untitled skill"
    skill_id = f"sk_{_slug(title)}_{uuid.uuid4().hex[:6]}"

    # Conceptual algorithm
    conceptual = {
        "problem": (business_text or "")[:280],
        "intent": pers.get("intent") or "Ship a provable core unit",
        "unit": (cr.get("profile") or {}).get("unit"),
        "warrants": [
            {
                "id": d.get("id"),
                "chosen": d.get("chosen"),
                "why": d.get("resolved_as"),
            }
            for d in (cr.get("decision_cards") or [])[:4]
        ],
        "design_claims": [
            {"id": c.get("id"), "niche": c.get("niche"), "title": c.get("title")}
            for c in (cr.get("architecture_cards") or [])[:6]
        ],
        "success_criteria": pers.get("success_criteria")
        or [(cr.get("profile") or {}).get("metric")],
        "anti_patterns": [
            "auto-yield promises",
            "5 channels at once",
            "open retainer without unit",
        ],
    }

    # Executive algorithm
    pilot = cr.get("pilot_21d") or []
    assist = (cr.get("implementation_assistant") or {}).get("steps") or []
    executive = {
        "preconditions": {
            "cash_ceiling": (cr.get("signer_numbers") or {}).get("cash_ceiling"),
            "days": (cr.get("signer_numbers") or {}).get("days"),
            "channel": (cr.get("profile") or {}).get("channel"),
        },
        "steps": [
            {
                "phase": p.get("days"),
                "dates": p.get("dates"),
                "focus": p.get("focus"),
                "exit": p.get("exit"),
            }
            for p in pilot
        ],
        "assist_steps": [
            {"id": s.get("id"), "action": s.get("action"), "exit": s.get("exit")}
            for s in assist
        ],
        "experiments": [
            {
                "id": t.get("id"),
                "hypothesis": t.get("hypothesis"),
                "kill_date": t.get("kill_date"),
                "stop": t.get("stop"),
            }
            for t in (cr.get("concept_tests") or [])
        ],
        "proof_artifacts": [
            "rd_memo_html",
            "cards_csv",
            "channel_log",
            "assist_run_log",
        ],
    }

    tags = list(
        {
            domain,
            pers.get("primary_axis") or "builder",
            route.get("surface") or "online",
            "universal",
        }
    )

    skill = {
        "id": skill_id,
        "name": title[:80],
        "domain": domain,
        "tags": tags,
        "success": success,
        "confidence": conf,
        "band": band,
        "conceptual_algorithm": conceptual,
        "executive_algorithm": executive,
        "source_fingerprint": pers.get("fingerprint"),
        "created_at": time.time(),
        "lang": "en" if (lang or "").lower().startswith("en") else "ru",
        "version": "1.0",
    }

    if persist and success:
        _persist(skill)
        _prune()

    return skill


def _persist(skill: dict[str, Any]) -> None:
    d = _ensure_dir()
    path = d / f"{skill['id']}.json"
    path.write_text(json.dumps(skill, ensure_ascii=False, indent=2), encoding="utf-8")


def _prune() -> None:
    d = _ensure_dir()
    files = sorted(d.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for f in files[MAX_SKILLS:]:
        try:
            f.unlink()
        except OSError:
            pass


def memory_status() -> dict[str, Any]:
    d = _ensure_dir()
    files = list(d.glob("*.json"))
    return {
        "module": "SkillMemory",
        "count": len(files),
        "max": MAX_SKILLS,
        "dir": str(d),
        "latest": [f.stem for f in sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:5]],
    }
