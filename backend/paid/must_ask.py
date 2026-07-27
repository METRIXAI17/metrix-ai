"""
Must-Ask Loop — gate before any paid re-run.

Before re-process, the system must ask clarifying questions in the
modeling language:

  entities · flows · levers · jobs · metrics

Wraps ClarifyingQuestionEngine and hardens the "must" subset so
re-runs never silently invent missing structure.
"""

from __future__ import annotations

from typing import Any

from backend.paid.clarifying_questions import MODELING_AXES, ClarifyingQuestionEngine
from backend.paid.types import clamp01, safe_float


# Canonical must-ask language (user-facing)
MUST_AXES = ("entities", "flows", "levers", "jobs", "metrics")


class MustAskLoop:
    """
    Production gate: produce must-ask questions + re-run readiness.

    `ready_for_rerun` is True only when must-count is 0 or all must fields
    appear in modeling_answers.
    """

    name = "Must-Ask Loop"

    def __init__(self) -> None:
        self._engine = ClarifyingQuestionEngine()

    def run(
        self,
        *,
        business: str,
        industry_id: str,
        idea_title: str = "",
        paid: dict[str, Any] | None = None,
        metrics: dict[str, Any] | None = None,
        decision: dict[str, Any] | None = None,
        oae: dict[str, Any] | None = None,
        scores: dict[str, float] | None = None,
        modeling_answers: dict[str, Any] | None = None,
        reader_skeleton: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        paid = paid or {}
        metrics = metrics or {}
        ma = dict(modeling_answers or {})

        # Seed paid/metrics so question engine skips answered fields
        paid_for_q = {**paid, "_modeling_answers": ma}
        metrics_for_q = {**metrics, "_modeling_answers": ma}

        base = self._engine.build(
            business=business,
            industry_id=industry_id,
            idea_title=idea_title,
            paid=paid_for_q,
            metrics=metrics_for_q,
            decision=decision,
            oae=oae,
            scores=scores,
        )

        questions = list(base.get("questions") or [])
        # Prefer modeling axes in MUST_AXES; mark must
        must_ask: list[dict[str, Any]] = []
        optional: list[dict[str, Any]] = []
        for q in questions:
            axis = str(q.get("modeling_axis") or "")
            field = str(q.get("answer_field") or "")
            is_must = (
                axis in MUST_AXES
                or q.get("priority", 99) <= 2
                or str(q.get("required_for") or "") in ("re_run", "rerun", "paid_rerun")
            )
            # If reader already named this lever/entity, demote
            if reader_skeleton and field:
                covered = []
                for key in MUST_AXES:
                    covered.extend(reader_skeleton.get(key) or [])
                if any(field.lower() in str(c).lower() for c in covered):
                    is_must = False
            if field in ma and ma[field] not in (None, "", []):
                continue
            item = {**q, "must": is_must, "language": "entities·flows·levers·jobs·metrics"}
            if is_must:
                must_ask.append(item)
            else:
                optional.append(item)

        # Ensure at least structural coverage of empty axes when readiness low
        pr = safe_float(
            ((paid.get("function_engine") or {}).get("output_plane") or {}).get(
                "paid_readiness"
            )
            or (paid.get("package") or {}).get("paid_score"),
            0.4,
        )
        covered_axes = {str(q.get("modeling_axis")) for q in must_ask}
        if pr < 0.55:
            for axis in MUST_AXES:
                if axis in covered_axes:
                    continue
                if axis in ma:
                    continue
                must_ask.append(
                    {
                        "id": f"must_{axis}",
                        "modeling_axis": axis,
                        "question": _default_question(axis, industry_id),
                        "why": "Must-Ask Loop: incomplete modeling language before re-run.",
                        "answer_field": axis,
                        "priority": 1,
                        "required_for": "paid_rerun",
                        "must": True,
                        "language": "entities·flows·levers·jobs·metrics",
                    }
                )

        must_ask.sort(key=lambda x: int(x.get("priority") or 9))
        must_count = len(must_ask)
        ready = must_count == 0

        return {
            "module": self.name,
            "modeling_axes": list(MUST_AXES),
            "all_modeling_axes": list(MODELING_AXES),
            "must_ask": must_ask,
            "optional": optional[:12],
            "questions": must_ask + optional,  # backward compatible
            "must_count": must_count,
            "ready_for_rerun": ready,
            "block_rerun": not ready,
            "language": "entities · flows · levers · jobs · metrics",
            "re_run_checklist": base.get("re_run_checklist")
            or {
                "answer_must_ask": must_count > 0,
                "confirm_levers": True,
                "reprocess_endpoint": "POST /api/v1/process",
            },
            "honesty": (
                "System will not invent missing entities/flows/levers. "
                "Answer must-ask before re-run for stable paid packaging."
            ),
            "summary": (
                f"Must-Ask: {must_count} required, "
                f"{len(optional)} optional; ready_for_rerun={ready}."
            ),
            # pass-through useful base fields
            "focus": base.get("focus"),
            "gaps": base.get("gaps"),
        }


def _default_question(axis: str, industry_id: str) -> str:
    samples = {
        "entities": f"Who are the core entities in your {industry_id} value chain (client, builder, platform)?",
        "flows": "What are the main flows (money, compute, content, attention) between those entities?",
        "levers": "Which 1–3 levers can you actually turn this quarter (price, capacity, offer, process)?",
        "jobs": "What is the primary job-to-be-done you get paid for (one sentence)?",
        "metrics": "Which metrics prove control (revenue, margin, utilization, delivery time)?",
    }
    return samples.get(axis, f"Clarify {axis} for re-run.")
