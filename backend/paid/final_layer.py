"""
Final Product Layer — wires 21 principles, assembler, anti-down,
Objectly, OpeningEdge, NFT Create-Building, Harness, capital efficiency.

Runs once after PaidProductCore + before/inside commercial packaging.
"""

from __future__ import annotations

from typing import Any

from backend.paid.anti_down_sorter import AntiDownSorter
from backend.paid.capital_efficiency import CapitalEfficiencyEngine
from backend.paid.harness_showcase import HarnessShowcase
from backend.paid.narrative.semantic_engine import NarrativeSemanticEngine
from backend.paid.nft_create_building import NFTCreateBuilding
from backend.paid.objectly import ObjectlyEngine
from backend.paid.opening_edge import OpeningEdgeEngine
from backend.paid.principles_engine import get_principles_engine
from backend.paid.sequence_assembler import SequenceAssembler
from backend.paid.types import safe_float


class FinalProductLayer:
    name = "Final Product Layer"
    version = "final-2.0-narrative"

    def __init__(self) -> None:
        self.principles = get_principles_engine()
        self.assembler = SequenceAssembler()
        self.anti_down = AntiDownSorter()
        self.objectly = ObjectlyEngine()
        self.opening_edge = OpeningEdgeEngine()
        self.nft = NFTCreateBuilding()
        self.harness = HarnessShowcase()
        self.capital = CapitalEfficiencyEngine()
        self.narrative = NarrativeSemanticEngine()

    def run(
        self,
        *,
        industry_id: str = "",
        business: str = "",
        idea_title: str = "",
        request_id: str = "",
        paid: dict[str, Any] | None = None,
        scores: dict[str, Any] | None = None,
        scenario_key: str = "traction_200",
        extra_params: dict[str, Any] | None = None,
        must_ask_open: int = 0,
    ) -> dict[str, Any]:
        paid = paid or {}
        scores = scores or {}
        residual = safe_float(
            (paid.get("conceptual_trajectory") or {}).get("residual_uncertainty"),
            0.35,
        )
        top_lever = str(
            (paid.get("package") or {}).get("top_lever")
            or (paid.get("function_engine") or {}).get("top_lever")
            or ""
        )

        principles_report = self.principles.run(
            industry_id=industry_id,
            scores=scores,
            top_lever=top_lever,
            residual_uncertainty=residual,
        )
        sequence = self.assembler.assemble(
            industry_id=industry_id,
            top_lever=top_lever,
            residual_uncertainty=residual,
            paid_score=safe_float(paid.get("paid_score"), 0.5),
            principles_report=principles_report,
        )
        anti = self.anti_down.sort(
            paid=paid,
            sequence=sequence,
            principles=principles_report,
            situation_metrics=paid.get("situation_metrics")
            or paid.get("business_metrics"),
        )
        objectly = self.objectly.materialize(
            industry_id=industry_id,
            business=business,
            idea_title=idea_title,
            paid=paid,
            reader=paid.get("reader"),
            principles=principles_report,
        )
        edge = self.opening_edge.run(
            industry_id=industry_id,
            paid=paid,
            scores=scores,
            residual_uncertainty=residual,
            principles=principles_report,
        )
        nft = self.nft.build(
            industry_id=industry_id,
            business=business,
            idea_title=idea_title,
            paid=paid,
            principles=principles_report,
            objectly=objectly,
        )
        harness = self.harness.run(
            industry_id=industry_id,
            paid=paid,
            sequence=sequence,
            principles=principles_report,
            anti_down=anti,
            nft=nft,
            objectly=objectly,
            opening_edge=edge,
            request_id=request_id,
        )
        capital = self.capital.run(
            scenario_key=scenario_key,
            industry_id=industry_id,
            include_optional_llm=True,
        )

        narrative = self.narrative.run(
            industry_id=industry_id,
            business=business,
            idea_title=idea_title,
            paid=paid,
            scores=scores,
            extra_params=extra_params or {},
            principles_report=principles_report,
            anti_down=anti,
            must_ask_open=must_ask_open,
        )

        # Status honesty for UI — hard gate on open must-ask
        ui_status = self._ui_status(paid, anti, must_ask_open=must_ask_open)

        return {
            "module": self.name,
            "version": self.version,
            "principles_engine": principles_report,
            "sequence_assembler": sequence,
            "anti_down_sorter": anti,
            "objectly": objectly,
            "opening_edge": edge,
            "nft_create_building": nft,
            "harness_showcase": harness,
            "narrative_engine": narrative,
            "client_memo": narrative.get("memo"),
            "capital_efficiency": {
                "scenario_key": capital["scenario_key"],
                "per_orientation_usd": {
                    k: v["total_usd"]
                    for k, v in capital["per_orientation_usd"].items()
                },
                "monthly_ops_usd": {
                    k: v["total_ops_usd"] for k, v in capital["monthly"].items()
                },
                "comparisons": capital["comparisons"],
                "output_per_dollar": capital["output_per_dollar"],
                "gross_revenue_model": capital["revenue_model_usd"]["gross_revenue"],
                "charts": capital["charts"],
                "assumptions_as_of": capital["assumptions"]["as_of"],
                "honesty": capital["honesty"],
                "full_report_path": "/app/capital-efficiency.html",
                "api": "/api/v1/analytics/capital-efficiency",
            },
            "ui_status": ui_status,
            "live_mode": harness.get("live_mode", True),
            "roadmap_scaffold": {
                "1_accounting": "workspace JSON + learning_state",
                "2_assistant": "niche principles / meta-reality framing",
                "3_execution_nftt": nft.get("token_draft"),
                "4_offer_capability_card": "commercial_layer tariffs",
                "next": ["Objectly", "OpeningEdge", "Data Market"],
            },
            "summary": (
                f"Final layer: meanings={principles_report.get('meanings_count')}, "
                f"plan={sequence.get('plan_key')}, "
                f"anti_down={anti.get('gate')}, "
                f"narrative_q={ (narrative.get('quality') or {}).get('consistency_score') }, "
                f"ops_save_vs_llm={capital['comparisons'].get('savings_C_vs_A_pct')}%."
            ),
        }

    def _ui_status(
        self,
        paid: dict[str, Any],
        anti: dict[str, Any],
        must_ask_open: int = 0,
    ) -> dict[str, Any]:
        raw = str(paid.get("status") or "candidate_preview")
        gate = anti.get("gate") or "pass_with_warnings"
        if must_ask_open > 0:
            return {
                "code": "preview",
                "label": "PREVIEW — MUST-ASK OPEN",
                "color": "#fbbf24",
                "sellable": False,
                "note": f"{must_ask_open} must-ask items open — not packageable.",
            }
        if gate == "block_down" or raw in ("blocked", "down"):
            return {
                "code": "blocked_down",
                "label": "BLOCKED / DOWN",
                "color": "#f87171",
                "sellable": False,
                "note": "Do not sell. Fix metrics / honesty first.",
            }
        if raw in ("candidate_preview", "preview", "open_scaffold"):
            return {
                "code": "preview",
                "label": "PREVIEW ONLY",
                "color": "#fbbf24",
                "sellable": False,
                "note": "Orientation-grade. Not packageable.",
            }
        if raw in ("ready", "packageable", "paid_ready") and gate in (
            "pass",
            "strong_pass",
        ):
            return {
                "code": "packageable",
                "label": "PACKAGEABLE",
                "color": "#34d399",
                "sellable": True,
                "note": "Metric-grounded path may be offered as pilot/package.",
            }
        return {
            "code": "candidate",
            "label": "CANDIDATE",
            "color": "#38bdf8",
            "sellable": False,
            "note": "Needs must-ask answers + client numbers.",
        }
