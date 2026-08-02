"""
Worker payout trust layer — solves under-declaration without hostile surveillance.

Psycho-socio design:
- People under-report when: (1) tax fear, (2) platform feels extractive,
  (3) proof of work is subjective, (4) payment is delayed/uncertain.
- Safe solution: milestone escrow + objective proof + transparent cut +
  reputation that unlocks better tasks — not invasive monitoring.

Legal note: we do NOT help evade taxes. We make on-platform verification
the path of least resistance so "honest on platform" is the default.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.config import DATA_DIR


@dataclass
class Milestone:
    id: str
    title: str
    amount_share: float  # 0..1 of task purse
    proof_type: str  # checklist | file_hash | client_accept | metric
    status: str = "open"  # open | submitted | released | disputed
    proof_payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EscrowTask:
    task_id: str
    title: str
    niche: str
    worker_id: str
    client_ref: str
    purse_units: float  # abstract units (not tax advice)
    platform_cut: float  # 0..1 transparent
    milestones: list[Milestone]
    status: str
    created_at: str
    reputation_delta_on_success: float
    rules: list[str]

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["milestones"] = [m.to_dict() if hasattr(m, "to_dict") else m for m in self.milestones]
        return d


class PayoutTrustLayer:
    """
    Escrow-style task purse:
      1) Client funds purse (or platform holds intent)
      2) Worker sees net = purse * (1 - platform_cut) split by milestones
      3) Release only on proof (checklist / file hash / accept)
      4) Reputation unlocks higher purse tasks
      5) No need to "declare income" off-platform for platform settlement —
         settlement IS the record (worker still responsible for local law)

    This reduces incentive to hide volume: unpaid off-book work has no escrow protection.
    """

    name = "PayoutTrustLayer"
    STORE = DATA_DIR / "workers"
    DEFAULT_CUT = 0.12  # transparent, not predatory

    def __init__(self) -> None:
        self.STORE.mkdir(parents=True, exist_ok=True)
        (self.STORE / "tasks").mkdir(exist_ok=True)
        (self.STORE / "reputations").mkdir(exist_ok=True)

    def create_task(
        self,
        *,
        title: str,
        niche: str,
        worker_id: str = "open",
        client_ref: str = "",
        purse_units: float = 100.0,
        platform_cut: float | None = None,
        milestone_titles: list[str] | None = None,
    ) -> dict[str, Any]:
        cut = self.DEFAULT_CUT if platform_cut is None else max(0.05, min(0.25, platform_cut))
        titles = milestone_titles or [
            "Brief confirmed + plan",
            "Draft deliverable",
            "Client accept / metric gate",
        ]
        shares = self._split_shares(len(titles))
        proof_cycle = ["checklist", "file_hash", "client_accept"]
        miles = []
        for i, (t, sh) in enumerate(zip(titles, shares)):
            miles.append(
                Milestone(
                    id=f"m{i+1}",
                    title=t,
                    amount_share=sh,
                    proof_type=proof_cycle[i % len(proof_cycle)],
                )
            )
        task = EscrowTask(
            task_id=uuid.uuid4().hex[:12],
            title=title,
            niche=niche,
            worker_id=worker_id,
            client_ref=client_ref or "self",
            purse_units=float(purse_units),
            platform_cut=cut,
            milestones=miles,
            status="funded_open",
            created_at=datetime.now(timezone.utc).isoformat(),
            reputation_delta_on_success=0.05,
            rules=[
                "Выплата только за verified milestone — не за обещание.",
                "Platform cut прозрачен до старта.",
                "Off-platform «серые» договорённости не защищены escrow.",
                "Репутация растёт только с released milestones.",
                "Налоги/декларации — ответственность сторон по местному праву; "
                "платформа даёт ledger фактов, не налоговую схему.",
            ],
        )
        self._save(task)
        return {
            "module": self.name,
            "task": task.to_dict(),
            "worker_net_units": round(purse_units * (1 - cut), 2),
            "platform_units": round(purse_units * cut, 2),
            "why_honest_default": self.rationale(),
        }

    def submit_proof(
        self,
        task_id: str,
        milestone_id: str,
        proof: dict[str, Any],
    ) -> dict[str, Any]:
        task = self._load(task_id)
        if not task:
            return {"error": "task_not_found"}
        for m in task["milestones"]:
            if m["id"] == milestone_id:
                ok, reason = self._validate_proof(m["proof_type"], proof)
                if not ok:
                    return {"error": "proof_rejected", "reason": reason}
                m["status"] = "submitted"
                m["proof_payload"] = {
                    **proof,
                    "submitted_at": datetime.now(timezone.utc).isoformat(),
                    "proof_fingerprint": hashlib.sha256(
                        json.dumps(proof, sort_keys=True, default=str).encode()
                    ).hexdigest()[:16],
                }
                self._write_raw(task)
                return {"ok": True, "milestone": m, "next": "await_release_or_auto"}
        return {"error": "milestone_not_found"}

    def release_milestone(self, task_id: str, milestone_id: str) -> dict[str, Any]:
        task = self._load(task_id)
        if not task:
            return {"error": "task_not_found"}
        released_pay = 0.0
        for m in task["milestones"]:
            if m["id"] == milestone_id and m["status"] in ("submitted", "open"):
                m["status"] = "released"
                net = task["purse_units"] * (1 - task["platform_cut"])
                released_pay = round(net * m["amount_share"], 2)
                break
        else:
            return {"error": "cannot_release"}
        if all(m["status"] == "released" for m in task["milestones"]):
            task["status"] = "completed"
            self._bump_reputation(task["worker_id"], task["reputation_delta_on_success"])
        self._write_raw(task)
        return {
            "ok": True,
            "paid_units": released_pay,
            "task_status": task["status"],
            "ledger_entry": {
                "task_id": task_id,
                "milestone_id": milestone_id,
                "units": released_pay,
                "ts": datetime.now(timezone.utc).isoformat(),
            },
        }

    def worker_dashboard(self, worker_id: str = "open") -> dict[str, Any]:
        tasks = []
        for p in (self.STORE / "tasks").glob("*.json"):
            t = json.loads(p.read_text(encoding="utf-8"))
            if t.get("worker_id") in (worker_id, "open"):
                tasks.append(
                    {
                        "task_id": t["task_id"],
                        "title": t["title"],
                        "status": t["status"],
                        "niche": t["niche"],
                        "net_units": round(t["purse_units"] * (1 - t["platform_cut"]), 2),
                    }
                )
        rep = self._rep(worker_id)
        return {
            "worker_id": worker_id,
            "reputation": rep,
            "open_tasks": tasks,
            "path": "зайти → взять задачу → proof → release → результат",
            "incentives": self.rationale()["incentives"],
        }

    def rationale(self) -> dict[str, Any]:
        return {
            "problem": (
                "Воркеры могут не декларировать доход, если (а) боятся налогов/фиска, "
                "(б) платформа кажется жадной, (в) нет proof, (г) платят «когда-нибудь»."
            ),
            "unsafe_bad_ideas": [
                "Скрытые трекеры и слежка — ломают trust, legal risk",
                "Заставлять занижать cut «в чёрную» — legal/ethical no",
                "Штрафы без due process",
            ],
            "safe_solution": "Milestone escrow + objective proof + transparent cut + reputation",
            "incentives": [
                "Off-book = без защиты escrow → worker loses security",
                "On-platform completion = reputation → better tasks",
                "Cut known upfront → no surprise extraction",
                "Fast release on proof → less need to game system",
                "Client funds purse first → less non-payment drama",
            ],
            "socio_read": (
                "Люди честнее, когда система делает честность самым выгодным и простым путём, "
                "а не когда их «ловят». Уважение + ясность > контроль."
            ),
        }

    def _validate_proof(self, proof_type: str, proof: dict[str, Any]) -> tuple[bool, str]:
        if proof_type == "checklist":
            items = proof.get("items") or []
            if not items or not all(items):
                return False, "checklist incomplete"
            return True, "ok"
        if proof_type == "file_hash":
            if not proof.get("sha256") and not proof.get("url"):
                return False, "need sha256 or url"
            return True, "ok"
        if proof_type == "client_accept":
            if not proof.get("accepted"):
                return False, "client not accepted"
            return True, "ok"
        if proof_type == "metric":
            if proof.get("value") is None:
                return False, "metric value missing"
            return True, "ok"
        return True, "ok"

    def _split_shares(self, n: int) -> list[float]:
        if n <= 0:
            return []
        if n == 1:
            return [1.0]
        if n == 2:
            return [0.4, 0.6]
        # front-load a bit less, final accept more
        base = [0.25] * (n - 1)
        base.append(round(1.0 - 0.25 * (n - 1), 2))
        if abs(sum(base) - 1.0) > 0.01:
            base[-1] = round(1.0 - sum(base[:-1]), 2)
        return base

    def _save(self, task: EscrowTask) -> None:
        self._write_raw(task.to_dict())

    def _write_raw(self, task: dict) -> None:
        path = self.STORE / "tasks" / f"{task['task_id']}.json"
        path.write_text(json.dumps(task, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load(self, task_id: str) -> dict | None:
        path = self.STORE / "tasks" / f"{task_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def _rep(self, worker_id: str) -> dict[str, Any]:
        path = self.STORE / "reputations" / f"{worker_id}.json"
        if not path.exists():
            return {"score": 0.5, "completed": 0}
        return json.loads(path.read_text(encoding="utf-8"))

    def _bump_reputation(self, worker_id: str, delta: float) -> None:
        if worker_id == "open":
            return
        rep = self._rep(worker_id)
        rep["score"] = round(min(0.99, float(rep.get("score", 0.5)) + delta), 3)
        rep["completed"] = int(rep.get("completed", 0)) + 1
        path = self.STORE / "reputations" / f"{worker_id}.json"
        path.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")


def create_task_escrow(**kwargs: Any) -> dict[str, Any]:
    return PayoutTrustLayer().create_task(**kwargs)
