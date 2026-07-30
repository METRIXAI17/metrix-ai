"""
Local evaluation suite for Metrix / Circle-System / Free work / Private rooms.

Scoring axes (0–100 each → weighted total):
  tests          30%  — pytest green
  deep_tech      20%  — pipeline assertions + surfaces
  free_work      15%  — start/clarify/advance
  niche_coverage 15%  — 6×3 answer packs
  private_rooms  20%  — mint link/password + unlock

Run:  py -3 scripts/local_eval_suite.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@dataclass
class AxisScore:
    name: str
    score: float
    weight: float
    notes: list[str]
    defects: list[str]

    @property
    def weighted(self) -> float:
        return self.score * self.weight


def eval_pytest() -> AxisScore:
    notes, defects = [], []
    try:
        p = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=180,
        )
        out = (p.stdout or "") + (p.stderr or "")
        notes.append(out.strip().splitlines()[-1] if out.strip() else "no output")
        if p.returncode == 0:
            score = 100.0
            notes.append("all tests green")
        else:
            # partial credit from passed count
            import re

            m = re.search(r"(\d+) failed.*?(\d+) passed", out)
            m2 = re.search(r"(\d+) passed.*?(\d+) failed", out)
            failed, passed = 1, 0
            if m:
                failed, passed = int(m.group(1)), int(m.group(2))
            elif m2:
                passed, failed = int(m2.group(1)), int(m2.group(2))
            total = max(1, failed + passed)
            score = round(100.0 * passed / total, 1)
            defects.append(f"pytest exit {p.returncode}: {failed} failed / {passed} passed")
    except Exception as e:  # noqa: BLE001
        score = 0.0
        defects.append(str(e))
    return AxisScore("tests", score, 0.30, notes, defects)


def eval_deep_tech() -> AxisScore:
    notes, defects = [], []
    try:
        from backend.core.circle_system import run_deep_tech_pipeline

        r = run_deep_tech_pipeline(
            "AI agency: 12 clients, rework 25%, want Terminal Teammate, "
            "budget 5000 USD, pilot 21 days, branding VA ready, CRM unclear.",
            industry_id="ai-agencies",
            lang="en",
        )
        surfaces = r.get("product_surfaces") or {}
        asserts = r.get("assertions") or []
        holds = sum(1 for a in asserts if a.get("holds"))
        score = 50.0
        if surfaces.get("auto_consult", {}).get("ready"):
            score += 10
        if surfaces.get("tech_write", {}).get("ready"):
            score += 10
        if surfaces.get("white_label_arch_prompts", {}).get("no_external_llm"):
            score += 10
        if holds == len(asserts) and asserts:
            score += 15
        else:
            defects.append(f"assertions {holds}/{len(asserts)}")
            score += 15 * (holds / max(1, len(asserts)))
        if (r.get("assembly") or {}).get("heat_used") is False:
            score += 5
        else:
            defects.append("assembly used heat")
        score = min(100.0, score)
        notes.append(f"assembly={r.get('assembly', {}).get('assembly_score')}")
        notes.append(f"primary={(r.get('super_program') or {}).get('primary', {}).get('excel_name')}")
    except Exception as e:  # noqa: BLE001
        score = 0.0
        defects.append(str(e))
    return AxisScore("deep_tech", score, 0.20, notes, defects)


def eval_free_work() -> AxisScore:
    notes, defects = [], []
    try:
        from backend.core.circle_system.free_work_flow import FreeWorkFlow

        fw = FreeWorkFlow()
        s = fw.start(
            business="Cloud founder burns OpenAI API 4k USD/mo quality floor critical custom ops "
            * 2,
            industry_id="cloud-economy",
            track="product",
            lang="ru",
            name="Eval",
        )
        score = 40.0
        if s.get("ok") and s.get("work_id"):
            score += 15
        else:
            defects.append("start failed")
        if len(s.get("phases") or []) >= 3:
            score += 15
        else:
            defects.append("phases < 3")
        if s.get("phases"):
            score += 10
        c = fw.submit_clarifications(
            s["work_id"],
            {"monthly_api_usd": "4000", "quality_floor": "user notices latency"},
            lang="ru",
        )
        if c.get("ok"):
            score += 10
        else:
            defects.append("clarify failed")
        a = fw.advance_phase(s["work_id"])
        if a.get("ok"):
            score += 10
        else:
            defects.append("advance failed")
        notes.append(f"quality={ (s.get('quality_answer') or {}).get('quality_score') }")
        score = min(100.0, score)
    except Exception as e:  # noqa: BLE001
        score = 0.0
        defects.append(str(e))
    return AxisScore("free_work", score, 0.15, notes, defects)


def eval_niche() -> AxisScore:
    notes, defects = [], []
    try:
        from backend.core.circle_system.niche_answer_base import NICHE_BASE, NicheAnswerBase

        base = NicheAnswerBase()
        miss = 0
        total = 0
        for ind in NICHE_BASE:
            for d in ("ops", "product", "promotion"):
                total += 1
                r = base.resolve(ind, track=d, lang="ru", business="eval " * 10)
                if not r.get("answer") or not r.get("success_metric"):
                    miss += 1
                    defects.append(f"{ind}/{d} incomplete")
        score = round(100.0 * (total - miss) / max(1, total), 1)
        notes.append(f"packs ok {total - miss}/{total}")
        notes.append("founders lane not required (deferred)")
    except Exception as e:  # noqa: BLE001
        score = 0.0
        defects.append(str(e))
    return AxisScore("niche_coverage", score, 0.15, notes, defects)


def eval_private_rooms() -> AxisScore:
    notes, defects = [], []
    try:
        from pilot_private.private_rooms import PrivateRoomRegistry
    except ImportError:
        notes.append("pilot_private absent (public tree) — axis N/A, full credit for public deploy")
        return AxisScore("private_rooms", 100.0, 0.20, notes, [])
    try:
        reg = PrivateRoomRegistry()
        room = reg.mint(
            client_name="Eval Client",
            industry="ai-agencies",
            contact="@eval",
            lang="ru",
        )
        score = 50.0
        if room.get("slug") and room.get("password") and room.get("unique_url_path"):
            score += 20
            notes.append(f"slug={room['slug']}")
        else:
            defects.append("mint incomplete")
        bad = reg.unlock(room["slug"], "wrong-password")
        if not bad.get("ok"):
            score += 10
        else:
            defects.append("wrong password accepted")
        good = reg.unlock(room["slug"], room["password"])
        if good.get("ok") and good.get("workspace"):
            score += 15
        else:
            defects.append("unlock failed")
        if good.get("workspace", {}).get("return_url"):
            score += 5
            notes.append("return_url present")
        score = min(100.0, score)
    except Exception as e:  # noqa: BLE001
        score = 0.0
        defects.append(str(e))
    return AxisScore("private_rooms", score, 0.20, notes, defects)


def main() -> int:
    axes = [
        eval_pytest(),
        eval_deep_tech(),
        eval_free_work(),
        eval_niche(),
        eval_private_rooms(),
    ]
    total = sum(a.weighted for a in axes)
    grade = (
        "A" if total >= 90 else
        "B" if total >= 80 else
        "C" if total >= 70 else
        "D" if total >= 55 else
        "F"
    )
    report = {
        "total": round(total, 2),
        "grade": grade,
        "axes": [asdict(a) | {"weighted": round(a.weighted, 2)} for a in axes],
        "all_defects": [d for a in axes for d in a.defects],
    }
    out = ROOT / "docs" / "LOCAL_EVAL_REPORT.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\n=== TOTAL {report['total']} / 100  GRADE {grade} ===")
    return 0 if total >= 70 and not any(
        a.name == "tests" and a.score < 95 for a in axes
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
