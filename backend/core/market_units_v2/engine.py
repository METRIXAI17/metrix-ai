"""
Market Units Engine v2 — full orchestration + recursive operational core boost.

Pipeline:
  SystemReader → ProblemRecognition → MetricComposer (pre)
  → TeammateNetwork → CoordinationLayer → OntologyEngine
  → MetricComposer (post, with CI) → quality forecast + offer routing
"""

from __future__ import annotations

from typing import Any

from backend.core.market_units import market_unit_for, package_cost_report, simple_offers
from backend.core.market_units_v2.coordination import CoordinationLayer
from backend.core.market_units_v2.metric_composer import MetricComposer
from backend.core.market_units_v2.ontology import OntologyEngine
from backend.core.market_units_v2.problem_recognition import ProblemRecognition
from backend.core.market_units_v2.system_reader import SystemReader
from backend.core.market_units_v2.teammate_network import TeammateNetwork

VERSION = "2026-08-02-mu-v2"


class MarketUnitsEngine:
    """Orchestrates Market Units v2 layers and returns a single payload."""

    name = "Market Units Engine v2"
    version = VERSION

    def __init__(self) -> None:
        self.reader = SystemReader()
        self.problems = ProblemRecognition()
        self.metrics = MetricComposer()
        self.coordination = CoordinationLayer()
        self.ontology = OntologyEngine()
        self.teammates = TeammateNetwork()

    def run(
        self,
        *,
        industry_id: str,
        business_text: str = "",
        orientation: dict[str, Any] | None = None,
        scores: dict[str, float] | None = None,
        vvi: float = 0.4,
        er: float = 0.5,
        rrc: float = 0.5,
        health: float | None = None,
        success_composite: float = 0.5,
        situation_score: float | None = None,
        decision_mode: str = "scoring",
        oae: dict[str, Any] | None = None,
        memo_convert: dict[str, Any] | None = None,
        paid: dict[str, Any] | None = None,
        chain_mode: str | None = None,
        chain_id: str | None = None,
    ) -> dict[str, Any]:
        orientation = orientation or {}
        scores = scores or dict(orientation.get("scores") or {})
        unit = market_unit_for(industry_id)
        product = dict(unit.get("product") or {})
        product_sku = str(product.get("sku") or "")

        # 1. System reader
        read = self.reader.read(
            business_text=business_text,
            industry_id=industry_id,
            orientation=orientation,
            scores=scores,
        )
        read_d = read.to_dict()

        # 2. Problem recognition
        lattice = self.problems.recognize(
            industry_id=industry_id,
            signals=read.signals,
            voids=read.voids,
            readiness_band=read.readiness_band,
            scores=scores,
        )
        lattice_d = lattice.to_dict()
        primary = lattice.primary
        primary_d = primary.to_dict() if primary else {}
        primary_lev = float(primary.leverage) if primary else 0.0

        # 3. Teammate network (pre-coord for coverage)
        team = self.teammates.build(
            industry_id=industry_id,
            problems=[p.to_dict() for p in lattice.problems],
            family_pressure=lattice.family_pressure,
            product_sku=product_sku,
            coordination_index=0.5,
            readiness_band=read.readiness_band,
        )
        team_d = team.to_dict()

        # 4. Coordination layer
        coord = self.coordination.compute(
            density=read.density,
            readiness_band=read.readiness_band,
            family_pressure=lattice.family_pressure,
            primary_leverage=primary_lev,
            signals=read.signals,
            teammate_coverage=team.coverage,
            ontology_fit=0.55,
            decision_mode=decision_mode,
            health=float(health if health is not None else 0.5),
        )
        coord_d = coord.to_dict()

        # 5. Ontology + algorithms
        onto = self.ontology.generate(
            industry_id=industry_id,
            primary_problem=primary_d,
            family_pressure=lattice.family_pressure,
            signals=read.signals,
            coordination_index=coord.coordination_index,
            originality_pressure=0.45,
            readiness_band=read.readiness_band,
            product_sku=product_sku,
        )
        onto_d = onto.to_dict()

        # rebuild teammates with real CI
        team2 = self.teammates.build(
            industry_id=industry_id,
            problems=[p.to_dict() for p in lattice.problems],
            family_pressure=lattice.family_pressure,
            product_sku=product_sku,
            coordination_index=coord.coordination_index,
            readiness_band=read.readiness_band,
        )
        team_d = team2.to_dict()

        # re-coord lightly with ontology_fit
        coord2 = self.coordination.compute(
            density=read.density,
            readiness_band=read.readiness_band,
            family_pressure=lattice.family_pressure,
            primary_leverage=primary_lev,
            signals=read.signals,
            teammate_coverage=team2.coverage,
            ontology_fit=onto.ontology_fit,
            decision_mode=decision_mode,
            health=float(health if health is not None else 0.5),
        )
        coord_d = coord2.to_dict()

        # situation from paid/commercial if present
        sit = situation_score
        if sit is None and paid:
            sit = (paid.get("business_metrics") or {}).get("situation_score")
            if sit is None:
                sit = (paid.get("situation_metrics") or {}).get("situation_score")

        # 6. Metric composition (final)
        composed = self.metrics.compose(
            vvi=vvi,
            er=er,
            rrc=rrc,
            health=health,
            scores=scores,
            signals=read.signals,
            family_pressure=lattice.family_pressure,
            density=read.density,
            success_composite=success_composite,
            situation_score=float(sit) if sit is not None else None,
            coordination_index=coord2.coordination_index,
            primary_problem_leverage=primary_lev,
        )
        composed_d = composed.to_dict()

        # Offer routing: rank unit offers by track fit to primary family
        family = str((primary_d or {}).get("family") or "ops")
        track_map = {
            "ops": "ops",
            "cost": "ops",
            "metrics": "ops",
            "product": "product",
            "liquidity": "product",
            "promo": "promotion",
        }
        preferred_track = track_map.get(family, "product")
        offers = list(unit.get("offers") or simple_offers(industry_id))
        ranked_offers: list[dict[str, Any]] = []
        for o in offers:
            o2 = dict(o)
            track = str(o2.get("track") or "")
            boost = 0.15 if track == preferred_track else 0.0
            if primary and primary.product_hook and primary.product_hook in str(
                o2.get("title", "")
            ).lower().replace(" ", "_"):
                boost += 0.1
            o2["route_score"] = round(0.5 + boost + composed.product_quality_index * 0.2, 4)
            o2["preferred"] = track == preferred_track
            ranked_offers.append(o2)
        ranked_offers.sort(key=lambda x: -float(x.get("route_score") or 0))

        # Recursive operational core boost (forecast + concrete boosts)
        core_boost = self._recursive_core_boost(
            composed=composed_d,
            coord=coord_d,
            onto=onto_d,
            team=team_d,
            lattice=lattice_d,
            unit=unit,
        )

        # Quality of main products forecast
        product_quality = self._product_quality_forecast(
            unit=unit,
            composed=composed_d,
            onto=onto_d,
            team=team_d,
            primary=primary_d,
        )

        # Interaction rewrite spine (how pipeline should treat interactions)
        interaction_logic = {
            "version": VERSION,
            "flow": [
                "read_system",
                "recognize_problems",
                "compose_metrics",
                "coordinate",
                "ontologize",
                "attach_teammates",
                "route_offers",
                "memo_and_tech_write",
            ],
            "if_something_goes_wrong": {
                "degrade_to": "static_market_unit_catalog",
                "preserve": ["application_point", "product", "offers", "package_pricing"],
                "block_pipeline": False,
                "log_key": "market_units_v2_error",
            },
            "preferred_track": preferred_track,
            "lead_teammate": team_d.get("lead_id"),
            "primary_problem": primary_d.get("id"),
            "selected_function_hint": (
                ((memo_convert or {}).get("analog_engine") or {}).get("selected_function")
            ),
        }

        # Semantic enrichment of the static unit
        enriched_unit = {
            **unit,
            "semantics": {
                "readiness_band": read.readiness_band,
                "density": read.density,
                "primary_problem": primary_d.get("id"),
                "primary_family": family,
                "application_point": unit.get("application_point"),
                "application_logic": (
                    f"{unit.get('application_point')} ← problem:{primary_d.get('id')} "
                    f"via {preferred_track} track"
                ),
                "ontology_combo": (onto_d.get("primary_combo") or {}).get("id"),
                "figurative": (onto_d.get("figurative_awareness") or {}).get("metaphor"),
            },
            "offers_ranked": ranked_offers,
            "coordination_index": coord2.coordination_index,
            "product_quality_index": composed.product_quality_index,
        }

        summary = (
            f"{self.name} [{industry_id}]: PQI={composed.product_quality_index:.3f} "
            f"CI={coord2.coordination_index:.3f} problem={primary_d.get('id')} "
            f"lead={team_d.get('lead_id')} boost={core_boost.get('boost_score')}"
        )

        out = {
            "module": self.name,
            "version": VERSION,
            "industry_id": industry_id,
            "unit": enriched_unit,
            "system_reader": read_d,
            "problem_recognition": lattice_d,
            "metric_composer": composed_d,
            "coordination": coord_d,
            "ontology": onto_d,
            "teammate_network": team_d,
            "offers_ranked": ranked_offers,
            "interaction_logic": interaction_logic,
            "core_boost": core_boost,
            "product_quality": product_quality,
            "package_costs": package_cost_report().get("primary_package"),
            "summary": summary,
            "ok": True,
        }
        if (chain_mode or "").lower() == "a2a":
            from backend.core.circle_system.chain_topologies import build_a2a_chain

            try:
                out["chain_mode"] = "a2a"
                out["a2a_chain"] = build_a2a_chain(out, chain_id=chain_id)
                out["b2c_stepper"] = False
            except Exception as exc:  # noqa: BLE001
                out["chain_mode"] = "a2a"
                out["a2a_chain"] = {"topology": "a2a", "error": str(exc)[:200], "artefact_handoffs": []}
                out["b2c_stepper"] = False
        return out

    def _recursive_core_boost(
        self,
        *,
        composed: dict[str, Any],
        coord: dict[str, Any],
        onto: dict[str, Any],
        team: dict[str, Any],
        lattice: dict[str, Any],
        unit: dict[str, Any],
    ) -> dict[str, Any]:
        """How v2 recursively strengthens the operational core."""
        pqi = float(composed.get("product_quality_index") or 0.5)
        ci = float(coord.get("coordination_index") or 0.5)
        ofit = float(onto.get("ontology_fit") or 0.5)
        nscore = float(team.get("network_score") or 0.5)
        boost_score = round(
            min(1.0, pqi * 0.3 + ci * 0.3 + ofit * 0.2 + nscore * 0.2), 4
        )
        return {
            "boost_score": boost_score,
            "mechanisms": [
                {
                    "id": "reader_to_decision",
                    "effect": "SystemReader signals feed Decision Core mode confidence",
                    "delta": round(ci * 0.08, 4),
                },
                {
                    "id": "problem_to_oae",
                    "effect": "Primary problem family biases OAE constructor slots",
                    "delta": round(float((lattice.get("primary") or {}).get("leverage") or 0) * 0.1, 4),
                },
                {
                    "id": "metrics_to_success_tz",
                    "effect": "PQI levers refine Success Metrics TZ weights",
                    "delta": round((1.0 - pqi) * 0.06 + 0.04, 4),
                },
                {
                    "id": "teammate_to_paid",
                    "effect": "Teammate mesh raises paid core handoff readiness",
                    "delta": round(nscore * 0.09, 4),
                },
                {
                    "id": "ontology_to_memo",
                    "effect": "Task algorithms seed Memo Convert technical language",
                    "delta": round(ofit * 0.08, 4),
                },
            ],
            "product_hooks": {
                "sku": (unit.get("product") or {}).get("sku"),
                "name": (unit.get("product") or {}).get("name"),
                "strengthened_by": [
                    "coordination_index",
                    "ontology_algorithms",
                    "teammate_coverage",
                ],
            },
            "recursive_note": (
                "Each request re-runs reader→problems→metrics→coord→ontology→teammates; "
                "outputs re-enter OAE/Decision/Paid as richer context without external LLM."
            ),
        }

    def _product_quality_forecast(
        self,
        *,
        unit: dict[str, Any],
        composed: dict[str, Any],
        onto: dict[str, Any],
        team: dict[str, Any],
        primary: dict[str, Any],
    ) -> dict[str, Any]:
        """Forecast how to strengthen quality of main outbound products."""
        forecast = dict(composed.get("forecast") or {})
        product = unit.get("product") or {}
        return {
            "main_product": product,
            "baseline_pqi": forecast.get("pqi_now"),
            "after_v2": forecast.get("pqi_after_full_v2"),
            "lift": round(
                float(forecast.get("pqi_after_full_v2") or 0)
                - float(forecast.get("pqi_now") or 0),
                4,
            ),
            "quality_levers": [
                {
                    "lever": "semantic_density",
                    "how": "SystemReader voids + density → less vague packs",
                    "expected": forecast.get("clarity_lift"),
                },
                {
                    "lever": "problem_aligned_offers",
                    "how": f"Route offers to family={(primary or {}).get('family')} / {primary.get('id')}",
                    "expected": 0.06,
                },
                {
                    "lever": "ontological_algorithms",
                    "how": "Task algorithms make tech-write and teammate attach repeatable",
                    "expected": float(onto.get("ontology_fit") or 0) * 0.08,
                },
                {
                    "lever": "teammate_coverage",
                    "how": f"Lead {team.get('lead_id')} owns primary until severity drops",
                    "expected": float(team.get("coverage") or 0) * 0.07,
                },
                {
                    "lever": "figurative_alignment",
                    "how": (onto.get("figurative_awareness") or {}).get("metaphor"),
                    "expected": float(
                        (onto.get("figurative_awareness") or {}).get("awareness_score") or 0
                    )
                    * 0.05,
                },
            ],
            "before_after": {
                "before": {
                    "market_units": "static application_point + offers list",
                    "interaction": "catalog lookup after memo convert",
                    "metrics": "VVI/ER/RRC only at core",
                    "teammates": "SKU name only (Terminal Teammate)",
                },
                "after": {
                    "market_units": "semantic graph + ranked offers + PQI",
                    "interaction": "reader→problem→coord→ontology→mesh→route",
                    "metrics": "composed PQI + forecast + levers",
                    "teammates": "role mesh + attach plan + coverage",
                },
            },
        }


def run_market_units_v2(**kwargs: Any) -> dict[str, Any]:
    """Module-level convenience wrapper with safe degrade."""
    try:
        return MarketUnitsEngine().run(**kwargs)
    except Exception as exc:  # noqa: BLE001 — never block pipeline
        industry_id = str(kwargs.get("industry_id") or "ai-agencies")
        unit = market_unit_for(industry_id)
        return {
            "module": "Market Units Engine v2",
            "version": VERSION,
            "ok": False,
            "error": str(exc)[:240],
            "unit": unit,
            "degraded": True,
            "summary": f"degraded to static unit: {exc}",
        }
