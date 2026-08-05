"""
Autonomous Implementation Assistant Agent — executor for post-approval rollout.

Not a CTA label: a runnable agent that:
  1. Locks scope from Core decisions
  2. Drafts desk assignments from architecture cards
  3. Schedules T1/T2/T3 gates from calendar kills
  4. Builds channel-log checklist
  5. Produces next-action queue + run log
  6. Can advance step-by-step (stateful session)

Separate product surface from Core free pack:
  - Free: see offer + teaser steps
  - After Approve Core: agent unlocks and executes drafts
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

SESSIONS_DIR = Path(_DATA) / "assist_sessions"


def _lang(lang: str) -> str:
    return "en" if (lang or "").lower().startswith("en") else "ru"


def _d(lang: str, ru: str, en: str) -> str:
    return en if _lang(lang) == "en" else ru


def _ensure() -> Path:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    return SESSIONS_DIR


class ImplementationAssistAgent:
    """Autonomous executor agent for implementation path."""

    name = "ImplementationAssistAgent"
    version = "1.0"

    def offer(self, *, lang: str = "ru", assist_ready: bool = True) -> dict[str, Any]:
        """Separate commercial / product offer for the assist agent."""
        L = _lang(lang)
        return {
            "id": "assist_agent",
            "sku": "implementation_assist_agent",
            "name": _d(L, "Ассистент-исполнитель внедрения", "Implementation executor assistant"),
            "tagline": _d(
                L,
                "Автономный агент: scope → desk → T-gates → channel log → tune",
                "Autonomous agent: scope → desk → T-gates → channel log → tune",
            ),
            "what_it_does": [
                _d(L, "Фиксирует scope из S1–S4", "Locks scope from S1–S4"),
                _d(L, "Назначает WIP=3 по A01–A12", "Assigns WIP=3 from A01–A12"),
                _d(L, "Ставит calendar gates T1–T3", "Schedules calendar gates T1–T3"),
                _d(L, "Ведёт checklist 7-day log", "Runs 7-day log checklist"),
                _d(L, "Пишет run log и next actions", "Writes run log and next actions"),
            ],
            "separate_from_core": True,
            "free_teaser": True,
            "unlock": "implementation_approval",
            "price_note": _d(
                L,
                "Отдельное предложение: открывается после утверждения Ядра · оплата внедрения опциональна",
                "Separate offer: unlocks after Core approval · implementation pay optional",
            ),
            "ready": assist_ready,
            "cta_teaser": _d(
                L,
                "Отдельный продукт: подключить Assist Agent после Approve",
                "Separate product: connect Assist Agent after Approve",
            ),
            "cta_unlock": _d(
                L,
                "Запустить ассистента-исполнителя",
                "Start implementation executor agent",
            ),
        }

    def build_from_core(
        self,
        core_report: dict[str, Any],
        *,
        personality: dict[str, Any] | None = None,
        routing: dict[str, Any] | None = None,
        lang: str = "ru",
        approved: bool = False,
    ) -> dict[str, Any]:
        """Draft full agent plan from Core deliverable (teaser or unlocked)."""
        L = _lang(lang)
        cr = core_report or {}
        pers = personality or {}
        route = routing or {}
        arch = cr.get("architecture_cards") or []
        tests = cr.get("concept_tests") or []
        decisions = cr.get("decision_cards") or []
        clog = cr.get("channel_log_7d") or {}
        assist = cr.get("implementation_assistant") or {}

        # Queue of autonomous actions
        queue: list[dict[str, Any]] = []

        # Step 0 — scope lock
        queue.append(
            {
                "id": "AG0",
                "kind": "scope_lock",
                "status": "ready" if approved else "locked",
                "title": _d(L, "Scope lock", "Scope lock"),
                "action": _d(
                    L,
                    "Зафиксировать S1–S4 + cash ceiling + anti-scope; выдать accept note.",
                    "Lock S1–S4 + cash ceiling + anti-scope; issue accept note.",
                ),
                "inputs": {
                    "decisions": [
                        {"id": d.get("id"), "chosen": d.get("chosen")} for d in decisions
                    ],
                    "cash": (cr.get("signer_numbers") or {}).get("cash_ceiling"),
                    "days": (cr.get("signer_numbers") or {}).get("days"),
                },
                "exit": _d(L, "Scope accepted", "Scope accepted"),
            }
        )

        # Step 1 — desk assignments from cards
        assignments = []
        for i, c in enumerate(arch[:3]):
            assignments.append(
                {
                    "wip_slot": i + 1,
                    "card_id": c.get("id"),
                    "title": c.get("title"),
                    "niche": c.get("niche"),
                    "proof": c.get("proof"),
                    "deadline_hint": "≤7d",
                }
            )
        queue.append(
            {
                "id": "AG1",
                "kind": "desk_assign",
                "status": "ready" if approved else "locked",
                "title": _d(L, "Editorial desk WIP=3", "Editorial desk WIP=3"),
                "action": _d(
                    L,
                    "Назначить 3 активные deep-карточки; остальное backlog.",
                    "Assign 3 active deep cards; rest stays backlog.",
                ),
                "inputs": {"assignments": assignments, "backlog": [c.get("id") for c in arch[3:]]},
                "exit": _d(L, "Board live", "Board live"),
            }
        )

        # Step 2 — calendar gates
        gates = [
            {
                "test_id": t.get("id"),
                "kill_date": t.get("kill_date"),
                "hypothesis": t.get("hypothesis"),
                "stop": t.get("stop"),
                "go": t.get("go"),
            }
            for t in tests
        ]
        queue.append(
            {
                "id": "AG2",
                "kind": "calendar_gates",
                "status": "ready" if approved else "locked",
                "title": _d(L, "Calendar gates T1–T3", "Calendar gates T1–T3"),
                "action": _d(
                    L,
                    "Поставить kill/go dates в календарь; без даты — нет теста.",
                    "Place kill/go dates on calendar; no date = no test.",
                ),
                "inputs": {"gates": gates},
                "exit": _d(L, "Gates scheduled", "Gates scheduled"),
            }
        )

        # Step 3 — channel log execution checklist
        days = clog.get("days") or []
        queue.append(
            {
                "id": "AG3",
                "kind": "channel_log",
                "status": "ready" if approved else "locked",
                "title": _d(L, "Execute 7-day channel log", "Execute 7-day channel log"),
                "action": _d(
                    L,
                    f"Пройти {clog.get('touch_target', 12)} касаний + 1 artifact; вести ledger.",
                    f"Run {clog.get('touch_target', 12)} touches + 1 artifact; keep ledger.",
                ),
                "inputs": {
                    "days": days,
                    "artifact": clog.get("artifact"),
                    "touch_target": clog.get("touch_target"),
                },
                "exit": _d(L, "Log complete or channel kill", "Log complete or channel kill"),
            }
        )

        # Step 4 — final tune
        queue.append(
            {
                "id": "AG4",
                "kind": "final_tune",
                "status": "ready" if approved else "locked",
                "title": _d(L, "Final client tune", "Final client tune"),
                "action": _d(
                    L,
                    "Под автора: pricing pack, niche #2, stop/go Core close.",
                    "Per author: pack pricing, niche #2, stop/go Core close.",
                ),
                "inputs": {
                    "author": pers.get("primary_label"),
                    "intent": pers.get("intent"),
                    "assist_template": assist.get("steps") or [],
                },
                "exit": _d(L, "Tune notes + next package", "Tune notes + next package"),
            }
        )

        next_actions = []
        for q in queue:
            if q["status"] == "ready":
                next_actions.append(
                    {
                        "step_id": q["id"],
                        "do": q["action"],
                        "exit": q["exit"],
                    }
                )

        session_id = f"ia_{uuid.uuid4().hex[:10]}"
        payload = {
            "module": self.name,
            "version": self.version,
            "session_id": session_id,
            "approved": approved,
            "status": "running" if approved else "teaser",
            "offer": self.offer(lang=lang, assist_ready=bool(route.get("assist_ready", True))),
            "author_axis": pers.get("primary_axis"),
            "domain": route.get("domain"),
            "queue": queue,
            "next_actions": next_actions[:3],
            "progress": {
                "total": len(queue),
                "ready": sum(1 for q in queue if q["status"] == "ready"),
                "done": 0,
                "cursor": queue[0]["id"] if approved and queue else None,
            },
            "run_log": [
                {
                    "ts": time.time(),
                    "event": "session_created",
                    "approved": approved,
                    "note": _d(
                        L,
                        "Агент создан. Teaser до approval; после — executive mode.",
                        "Agent created. Teaser until approval; then executive mode.",
                    ),
                }
            ],
            "harness": {
                "memory": "skill_memory + session log",
                "tools": ["scope_lock", "desk_assign", "calendar_gates", "channel_log", "tune"],
                "oversight": _d(
                    L,
                    "Высокоуровневый надзор: критерии успеха и kill dates, не микро-менеджмент текста.",
                    "High-level oversight: success criteria and kill dates, not text micromanagement.",
                ),
            },
            "lang": L,
        }
        if approved:
            self._save_session(payload)
        return payload

    def advance(self, session_id: str, *, note: str = "") -> dict[str, Any]:
        """Mark current cursor step done and move to next."""
        path = _ensure() / f"{session_id}.json"
        if not path.exists():
            return {"ok": False, "error": "session_not_found", "session_id": session_id}
        data = json.loads(path.read_text(encoding="utf-8"))
        if not data.get("approved"):
            return {"ok": False, "error": "not_approved", "session_id": session_id}
        cursor = (data.get("progress") or {}).get("cursor")
        queue = data.get("queue") or []
        found = False
        next_id = None
        for i, step in enumerate(queue):
            if step.get("id") == cursor:
                step["status"] = "done"
                found = True
                if i + 1 < len(queue):
                    queue[i + 1]["status"] = "ready"
                    next_id = queue[i + 1]["id"]
                break
        if not found and queue:
            # start first ready
            for step in queue:
                if step.get("status") in ("ready", "locked"):
                    step["status"] = "done"
                    break
            for step in queue:
                if step.get("status") != "done":
                    step["status"] = "ready"
                    next_id = step["id"]
                    break
        done = sum(1 for s in queue if s.get("status") == "done")
        data["progress"] = {
            "total": len(queue),
            "ready": sum(1 for s in queue if s.get("status") == "ready"),
            "done": done,
            "cursor": next_id,
        }
        data["queue"] = queue
        data["next_actions"] = [
            {"step_id": s["id"], "do": s["action"], "exit": s["exit"]}
            for s in queue
            if s.get("status") == "ready"
        ][:3]
        data["run_log"] = list(data.get("run_log") or []) + [
            {
                "ts": time.time(),
                "event": "advance",
                "from": cursor,
                "to": next_id,
                "note": note or "",
            }
        ]
        if done >= len(queue):
            data["status"] = "completed"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "session": data}

    def get_session(self, session_id: str) -> dict[str, Any]:
        path = _ensure() / f"{session_id}.json"
        if not path.exists():
            return {"ok": False, "error": "session_not_found"}
        return {"ok": True, "session": json.loads(path.read_text(encoding="utf-8"))}

    def approve_and_start(
        self,
        teaser_payload: dict[str, Any],
        *,
        lang: str = "ru",
    ) -> dict[str, Any]:
        """Flip teaser agent to approved executive mode and persist."""
        data = dict(teaser_payload or {})
        data["approved"] = True
        data["status"] = "running"
        for step in data.get("queue") or []:
            if step.get("status") == "locked":
                step["status"] = "ready"
        queue = data.get("queue") or []
        data["progress"] = {
            "total": len(queue),
            "ready": sum(1 for s in queue if s.get("status") == "ready"),
            "done": 0,
            "cursor": queue[0]["id"] if queue else None,
        }
        data["next_actions"] = [
            {"step_id": s["id"], "do": s["action"], "exit": s["exit"]}
            for s in queue
            if s.get("status") == "ready"
        ][:3]
        data["run_log"] = list(data.get("run_log") or []) + [
            {
                "ts": time.time(),
                "event": "approved",
                "note": _d(lang, "Implementation approved · agent unlocked", "Implementation approved · agent unlocked"),
            }
        ]
        if not data.get("session_id"):
            data["session_id"] = f"ia_{uuid.uuid4().hex[:10]}"
        self._save_session(data)
        return data

    def _save_session(self, data: dict[str, Any]) -> None:
        sid = data.get("session_id") or f"ia_{uuid.uuid4().hex[:10]}"
        data["session_id"] = sid
        path = _ensure() / f"{sid}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def build_assist_agent(
    core_report: dict[str, Any],
    **kwargs: Any,
) -> dict[str, Any]:
    return ImplementationAssistAgent().build_from_core(core_report, **kwargs)
