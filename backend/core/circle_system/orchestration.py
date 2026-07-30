"""
Dynamic orchestration — configurable circle-system autopilot plan.

Plan is knowledge-based: complex deals + stimulation (incentive) design.
"""

from __future__ import annotations

from typing import Any


DEFAULT_PHASES = (
    {
        "id": "P0_intake",
        "name": "Intake & certainty pass",
        "actions": ("complex_text_ingest", "param_dev", "indirect_certainty"),
        "days": (1, 2),
    },
    {
        "id": "P1_tests",
        "name": "Super-speed uncertainty tests",
        "actions": ("isolate_uncertainties", "quiz_questions", "assembly_check"),
        "days": (2, 4),
    },
    {
        "id": "P2_super",
        "name": "Super program match + layers",
        "actions": ("super_program", "circle_layers", "consistency"),
        "days": (3, 5),
    },
    {
        "id": "P3_techwrite",
        "name": "Tech write terminal specs",
        "actions": ("terminal_specs", "ops_rules_phased", "integration_lib"),
        "days": (4, 10),
    },
    {
        "id": "P4_pilot",
        "name": "Pilot execution",
        "actions": ("pilot_charter", "deploy_slice", "metric_firmware", "support_watch"),
        "days": (8, 28),
    },
    {
        "id": "P5_predict",
        "name": "Pilot accuracy prediction & rework",
        "actions": ("pilot_predictor", "rework_loop", "main_package_gate"),
        "days": (21, 35),
    },
)

# Complex-deal knowledge (stimuli that move stakeholders)
STIMULATION_PATTERNS = (
    {
        "id": "risk_reduction",
        "stimulus": "Show certain_no early to cut wasted scope",
        "deal_effect": "shortens sales cycle",
    },
    {
        "id": "proof_metric",
        "stimulus": "One composite metric both parties sign",
        "deal_effect": "unlocks pilot payment",
    },
    {
        "id": "partial_win",
        "stimulus": "Ship tech-write free before pilot invoice",
        "deal_effect": "trust + conversion",
    },
    {
        "id": "rework_buffer",
        "stimulus": "Pre-book 20–30% calendar for retests",
        "deal_effect": "protects NPS on pilot",
    },
)


class DynamicOrchestrator:
    """Build / tune autopilot plan; allows runtime config overrides."""

    name = "Dynamic Orchestrator"

    def run(
        self,
        layers_result: dict[str, Any],
        assembly: dict[str, Any] | None = None,
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        cfg = config or {}
        skip = set(cfg.get("skip_phases") or [])
        compress = bool(cfg.get("compress_timeline"))
        phases = []
        for ph in DEFAULT_PHASES:
            if ph["id"] in skip:
                continue
            d0, d1 = ph["days"]
            if compress:
                d0 = max(1, int(d0 * 0.75))
                d1 = max(d0 + 1, int(d1 * 0.75))
            # gate pilot if not autopilot ready
            if ph["id"] == "P4_pilot" and not layers_result.get("autopilot_ready"):
                phases.append(
                    {
                        **ph,
                        "days": (d0, d1),
                        "gate": "blocked_until_consistency",
                        "required": ["metrics", "product", "layers.consistency>=0.62"],
                    }
                )
            else:
                phases.append({**ph, "days": (d0, d1), "gate": "open"})

        assembly_score = float((assembly or {}).get("assembly_score") or 0.4)
        return {
            "module": self.name,
            "configurable": True,
            "config_applied": cfg,
            "phases": phases,
            "stimulation": list(STIMULATION_PATTERNS),
            "deal_knowledge": {
                "principle": "Complex deals move on proof + risk cut + partial win, not on pitch length.",
                "assembly_score": assembly_score,
            },
            "total_calendar_days_estimate": [
                phases[0]["days"][0] if phases else 1,
                phases[-1]["days"][1] if phases else 30,
            ],
            "rule": "Dynamic orchestration = ordered phases + skip/compress config without code rewrite.",
        }
