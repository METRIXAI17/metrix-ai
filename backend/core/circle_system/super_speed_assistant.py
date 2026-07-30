"""
Global step 3 (part A): Super-speed assistant — isolate each uncertainty
and convert it into concrete test-style questions.

Analyzes *assembly* of uncertain values (what must click together),
not linguistic heat. Warmth is applied only to answer rendering later.
"""

from __future__ import annotations

from typing import Any

from backend.core.circle_system.lexicon import (
    TEST_QUESTION_SHELLS_EN,
    TEST_QUESTION_SHELLS_RU,
)


ASSEMBLY_PRESETS: dict[str, list[str]] = {
    "goal": ["measurable outcome", "owner", "deadline"],
    "client_segment": ["who pays", "who uses", "decision cycle"],
    "offer": ["deliverable artifact", "price band", "acceptance criteria"],
    "constraint": ["hard limit", "soft preference", "violation cost"],
    "resource": ["available now", "gap", "procurement path"],
    "metric": ["baseline", "target", "measurement source"],
    "timeline": ["start gate", "end gate", "buffer for rework"],
    "integration": ["system A", "system B", "auth + data map"],
    "pilot_scope": ["in scope", "out of scope", "success metric"],
    "success_criterion": ["pass threshold", "fail action", "owner sign-off"],
}


class SuperSpeedAssistant:
    """Separate each uncertainty → concrete test questions + assembly map."""

    name = "Super Speed Assistant (uncertainty → tests)"

    def run(
        self,
        certainty_result: dict[str, Any],
        *,
        lang: str = "ru",
        max_questions_per_slot: int = 3,
    ) -> dict[str, Any]:
        shells = TEST_QUESTION_SHELLS_RU if lang.startswith("ru") else TEST_QUESTION_SHELLS_EN
        uncertain = [
            p
            for p in (certainty_result.get("parameters") or [])
            if p.get("status") == "uncertain"
        ]

        items: list[dict[str, Any]] = []
        all_questions: list[dict[str, Any]] = []

        for p in uncertain:
            slot = str(p.get("slot") or "goal")
            pid = str(p.get("id"))
            assembly_parts = ASSEMBLY_PRESETS.get(slot, ["condition_a", "condition_b", "condition_c"])
            questions: list[dict[str, Any]] = []

            # Binary polarity test
            q1 = {
                "qid": f"{pid}_bin",
                "param_id": pid,
                "slot": slot,
                "kind": "binary",
                "text": shells["binary"].format(slot=slot),
                "analyzes": "polarity",
                "not": "heat",
            }
            questions.append(q1)

            # Assembly test — what must click together
            q2 = {
                "qid": f"{pid}_asm",
                "param_id": pid,
                "slot": slot,
                "kind": "assembly",
                "text": shells["assembly"].format(slot=slot),
                "assembly_parts": assembly_parts,
                "analyzes": "value_assembly",
                "not": "linguistic_heat",
            }
            questions.append(q2)

            # Scale readiness
            q3 = {
                "qid": f"{pid}_scl",
                "param_id": pid,
                "slot": slot,
                "kind": "scale",
                "text": shells["scale"].format(slot=slot),
                "analyzes": "readiness",
            }
            questions.append(q3)

            # Slot-specific numeric when metric/timeline/resource
            if slot in ("metric", "timeline", "resource"):
                unit = {"metric": "ratio or %", "timeline": "days", "resource": "USD or FTE"}[slot]
                qn = {
                    "qid": f"{pid}_num",
                    "param_id": pid,
                    "slot": slot,
                    "kind": "numeric",
                    "text": shells["numeric"].format(slot=slot, unit=unit),
                    "unit": unit,
                    "analyzes": "magnitude",
                }
                questions.append(qn)

            questions = questions[: max(1, max_questions_per_slot + (1 if slot in ("metric", "timeline") else 0))]
            all_questions.extend(questions)

            items.append(
                {
                    "param_id": pid,
                    "slot": slot,
                    "snippet": p.get("snippet"),
                    "prior_scores": p.get("scores"),
                    "assembly": {
                        "parts": assembly_parts,
                        "rule": "A parameter becomes CERTAIN YES only when all assembly parts are filled and non-contradictory.",
                        "heat_forbidden": True,
                    },
                    "questions": questions,
                }
            )

        return {
            "module": self.name,
            "global_step": "3_super_speed_uncertainty_tests",
            "ref": "ref_4:points_5_6",
            "uncertain_count": len(uncertain),
            "items": items,
            "test_battery": all_questions,
            "mode": "quiz_style",
            "principle": (
                "Analyze assembly of uncertain values — not linguistic heat. "
                "Warmth applies only when rendering answers."
            ),
        }
