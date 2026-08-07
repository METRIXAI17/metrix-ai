"""
Autonomous Robotics Executor Harness — for three-direction implementations.

Not a chat agent. A state machine that:
  R0  Sense wayD terminal + labels
  R1  Lock implement model (3 directions)
  R2  Materialize product_pack artifacts
  R3  Materialize unit_pack artifacts
  R4  Drive ch_network / live_log ticks
  R5  Run acceptance forecast gate
  R6  Emit ship / hold decision + next ops actions

Sessions persist under data/robotics_sessions/
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

try:
    from backend.config import DATA_DIR as _DATA
except Exception:  # pragma: no cover
    _DATA = Path(__file__).resolve().parents[2] / "data"

SESSIONS = Path(_DATA) / "robotics_sessions"


def _lang(lang: str) -> str:
    return "en" if (lang or "").lower().startswith("en") else "ru"


def _d(lang: str, ru: str, en: str) -> str:
    return en if _lang(lang) == "en" else ru


def _ensure() -> Path:
    SESSIONS.mkdir(parents=True, exist_ok=True)
    return SESSIONS


PHASES = [
    ("R0", "sense", "Sense wayD terminal"),
    ("R1", "lock_model", "Lock three-direction implement model"),
    ("R2", "product_pack", "Materialize product_pack"),
    ("R3", "unit_pack", "Materialize unit_pack"),
    ("R4", "ch_network", "Drive channel network / live log"),
    ("R5", "acceptance_gate", "Acceptance forecast gate"),
    ("R6", "ship_decision", "Ship / hold + next actions"),
]


class RoboticsHarness:
    """Autonomous robotics executor for implementations."""

    name = "RoboticsHarness"
    version = "1.0.0"

    def build_plan(
        self,
        *,
        implement_model: dict[str, Any] | None = None,
        wayd: dict[str, Any] | None = None,
        segment: dict[str, Any] | None = None,
        path: dict[str, Any] | None = None,
        live_log: dict[str, Any] | None = None,
        acceptance: dict[str, Any] | None = None,
        gencore: dict[str, Any] | None = None,
        lang: str = "ru",
        approved: bool = False,
    ) -> dict[str, Any]:
        L = _lang(lang)
        im = implement_model or {}
        directions = im.get("directions") or [
            {"id": "product_pack"},
            {"id": "unit_pack"},
            {"id": "ch_network"},
        ]
        queue = []
        for pid, kind, title_en in PHASES:
            status = "ready" if approved else "locked"
            if not approved and pid == "R0":
                status = "preview"
            action = self._action_for(pid, directions, live_log, acceptance, lang=L)
            queue.append(
                {
                    "id": pid,
                    "kind": kind,
                    "title": title_en if L == "en" else _ru_title(pid),
                    "status": status,
                    "action": action,
                    "exit": _d(L, f"Фаза {pid} закрыта", f"Phase {pid} closed"),
                }
            )

        return {
            "module": self.name,
            "version": self.version,
            "status": "executive" if approved else "teaser",
            "approved": approved,
            "queue": queue,
            "queue_len": len(queue),
            "linked": {
                "implement_sku": im.get("sku_id") or "implement_three_directions",
                "live_log_id": (live_log or {}).get("id"),
                "segment_id": ((segment or {}).get("primary") or segment or {}).get("id"),
                "path_id": ((path or {}).get("path") or path or {}).get("id"),
                "acceptance_p": (acceptance or {}).get("acceptance_p"),
                "ship_gate": ((wayd or {}).get("terminal") or wayd or {}).get("ship_gate"),
                "gencore_gen": (gencore or {}).get("generation"),
            },
            "how_it_works": {
                "mode": "state_machine",
                "steps": [
                    _d(
                        L,
                        "Харнес читает wayD-метки и terminal metrics (density·signal·acceptance·mesh).",
                        "Harness reads wayD labels and terminal metrics (density·signal·acceptance·mesh).",
                    ),
                    _d(
                        L,
                        "Фиксирует модель внедрения трёх направлений (единственный платный SKU, скрыт с public).",
                        "Locks three-direction implement model (sole paid SKU, hidden from public).",
                    ),
                    _d(
                        L,
                        "Последовательно материализует product_pack → unit_pack → ch_network.",
                        "Sequentially materializes product_pack → unit_pack → ch_network.",
                    ),
                    _d(
                        L,
                        "Гоняет live log ticks и пишет proof в ledger.",
                        "Runs live log ticks and writes proof into ledger.",
                    ),
                    _d(
                        L,
                        "На R5 считает P(приёмки); на R6 — ship/hold без чат-цикла.",
                        "At R5 computes acceptance P; at R6 ship/hold without chat loop.",
                    ),
                ],
                "ops_hint": _d(
                    L,
                    "Управление: POST /analytics/robotics/start → /advance. Панель: /app/ops-panel.html",
                    "Control: POST /analytics/robotics/start → /advance. Panel: /app/ops-panel.html",
                ),
            },
            "offer": {
                "id": "robotics_harness",
                "separate_from_core": True,
                "public_price": None,
                "unlock": "implementation_approval",
                "tagline": _d(
                    L,
                    "Автономный роботикс-исполнитель внедрений",
                    "Autonomous robotics implementation executor",
                ),
            },
            "wayd_label": "L.edge.robotics_x_implement",
            "message": _d(
                L,
                "Robotics harness: 7 фаз · teaser до approval",
                "Robotics harness: 7 phases · teaser until approval",
            ),
        }

    def _action_for(
        self,
        phase: str,
        directions: list[dict[str, Any]],
        live_log: dict[str, Any] | None,
        acceptance: dict[str, Any] | None,
        *,
        lang: str,
    ) -> str:
        L = lang
        if phase == "R0":
            return _d(L, "Снять terminal metrics + label bus", "Snapshot terminal metrics + label bus")
        if phase == "R1":
            ids = ", ".join(d.get("id", "?") for d in directions)
            return _d(L, f"Lock implement model: {ids}", f"Lock implement model: {ids}")
        if phase == "R2":
            return _d(L, "Собрать product_pack артефакты + originality", "Assemble product_pack artifacts + originality")
        if phase == "R3":
            return _d(L, "Собрать unit_pack + pilot metric", "Assemble unit_pack + pilot metric")
        if phase == "R4":
            lid = (live_log or {}).get("id") or "log_?"
            return _d(L, f"Live log {lid}: tick days + artifact", f"Live log {lid}: tick days + artifact")
        if phase == "R5":
            p = (acceptance or {}).get("acceptance_p")
            return _d(
                L,
                f"Acceptance gate P={p if p is not None else '—'}",
                f"Acceptance gate P={p if p is not None else '—'}",
            )
        if phase == "R6":
            return _d(L, "Ship/hold + next ops actions", "Ship/hold + next ops actions")
        return phase

    def start(self, plan: dict[str, Any], *, lang: str = "ru") -> dict[str, Any]:
        """Approve and persist executive session."""
        sid = f"rob_{uuid.uuid4().hex[:12]}"
        session = {
            "session_id": sid,
            "module": self.name,
            "version": self.version,
            "created_at": time.time(),
            "status": "executive",
            "approved": True,
            "cursor": 0,
            "plan": plan,
            "queue": [],
            "run_log": [],
            "lang": _lang(lang),
        }
        # unlock queue
        q = []
        for step in plan.get("queue") or []:
            s = dict(step)
            s["status"] = "ready" if s.get("id") == "R0" else "queued"
            q.append(s)
        if q:
            q[0]["status"] = "active"
        session["queue"] = q
        session["run_log"].append({"ts": time.time(), "event": "start", "session_id": sid})
        self._save(session)
        return session

    def advance(self, session_id: str, *, note: str = "") -> dict[str, Any]:
        path = _ensure() / f"{session_id}.json"
        if not path.exists():
            return {"ok": False, "error": "not_found"}
        session = json.loads(path.read_text(encoding="utf-8"))
        q = session.get("queue") or []
        cur = int(session.get("cursor") or 0)
        if cur >= len(q):
            session["status"] = "complete"
            self._save(session)
            return {"ok": True, "done": True, "session": session}

        step = q[cur]
        step["status"] = "done"
        step["done_at"] = time.time()
        if note:
            step["note"] = note
        session["run_log"].append(
            {"ts": time.time(), "event": "advance", "phase": step.get("id"), "note": note}
        )
        cur += 1
        session["cursor"] = cur
        if cur < len(q):
            q[cur]["status"] = "active"
            session["status"] = "executive"
        else:
            session["status"] = "complete"
            # ship decision summary
            acc = ((session.get("plan") or {}).get("linked") or {}).get("acceptance_p")
            session["ship_decision"] = {
                "gate": "ship" if (acc or 0) >= 0.62 else "hold",
                "acceptance_p": acc,
                "completed_phases": len(q),
            }
        session["queue"] = q
        self._save(session)
        return {"ok": True, "done": session["status"] == "complete", "session": session, "advanced": step}

    def get(self, session_id: str) -> dict[str, Any]:
        path = _ensure() / f"{session_id}.json"
        if not path.exists():
            return {"ok": False, "error": "not_found"}
        return {"ok": True, "session": json.loads(path.read_text(encoding="utf-8"))}

    def _save(self, session: dict[str, Any]) -> None:
        sid = session.get("session_id") or f"rob_{uuid.uuid4().hex[:12]}"
        session["session_id"] = sid
        path = _ensure() / f"{sid}.json"
        path.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")


def _ru_title(pid: str) -> str:
    return {
        "R0": "Sense wayD terminal",
        "R1": "Lock модели внедрения",
        "R2": "Materialize product_pack",
        "R3": "Materialize unit_pack",
        "R4": "Channel network / live log",
        "R5": "Acceptance gate",
        "R6": "Ship / hold",
    }.get(pid, pid)
