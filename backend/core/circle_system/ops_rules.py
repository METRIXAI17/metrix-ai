"""
Operational rules computer — phased tech-write insertion into the live system.
Splits the analyzed system into analysis segments.
"""

from __future__ import annotations

from typing import Any


class OperationalRulesEngine:
    name = "Operational Rules Engine"

    def run(
        self,
        terminal_specs: dict[str, Any],
        layers_result: dict[str, Any] | None = None,
        artefacts: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        specs = terminal_specs.get("terminal_functions") or []
        segments: list[dict[str, Any]] = []
        phases: list[dict[str, Any]] = []

        # Split system into analysis segments by layer
        for s in specs:
            segments.append(
                {
                    "segment_id": f"seg_{s['id']}",
                    "spec_id": s["id"],
                    "layer": s.get("layer"),
                    "analysis_focus": s.get("sections", [])[:3],
                    "status": s.get("status"),
                }
            )

        # Phased tech-write insertion rules
        insert_order = [
            "orientation_brief",
            "tech_write_core",
            "metric_firmware_spec",
            "ops_rules_slice",
            "integration_contract",
            "pilot_charter",
            "ledger_hooks",
            "arch_prompt_pack",
        ]
        step = 1
        for sid in insert_order:
            spec = next((x for x in specs if x["id"] == sid), None)
            if not spec:
                continue
            phases.append(
                {
                    "phase": step,
                    "rule_id": f"tw_insert_{step}",
                    "spec_id": sid,
                    "action": "insert_tech_write_slice",
                    "precondition": "previous_phase_accepted" if step > 1 else "intake_complete",
                    "validation": [
                        "sections_non_empty",
                        "no_contradiction_with_certain_no",
                        "metrics_hook_present" if "metric" in sid or sid == "pilot_charter" else "structure_ok",
                    ],
                    "rollback": f"revert_slice_{sid}",
                }
            )
            step += 1

        rules = [
            {
                "id": "R1_no_fake_certainty",
                "if": "status==uncertain",
                "then": "route_to_super_speed_tests",
            },
            {
                "id": "R2_certain_no_scope_cut",
                "if": "status==certain_no",
                "then": "exclude_from_pilot_scope",
            },
            {
                "id": "R3_assembly_gate",
                "if": "assembly_score<0.45",
                "then": "block_pilot_deploy",
            },
            {
                "id": "R4_phased_techwrite",
                "if": "tech_write_pending",
                "then": "insert_next_phase_only",
            },
            {
                "id": "R5_support_on_anomaly",
                "if": "metric_firmware.anomaly",
                "then": "open_support_ticket",
            },
            {
                "id": "R6_main_package_gate",
                "if": "pilot_predictor.accuracy>=0.7 AND pilot_success",
                "then": "offer_main_package",
            },
            {
                "id": "R7_artefact_informed_ticket",
                "if": "anomaly AND traditional_artefact.affects_slot",
                "then": "open_ticket_with_artefact_hook_human_owner_stays",
            },
        ]
        artefact_hooks = [
            {
                "artefact_id": a.get("id"),
                "sigil": a.get("sigil"),
                "hooks": a.get("chain_hooks") or [],
                "risk_delta": a.get("risk_delta"),
            }
            for a in (artefacts or [])
        ]

        return {
            "module": self.name,
            "segments": segments,
            "tech_write_phases": phases,
            "rules": rules,
            "artefact_hooks": artefact_hooks,
            "segment_count": len(segments),
            "rule": "Tech write is inserted phase-by-phase; system is split into analysis segments.",
        }
