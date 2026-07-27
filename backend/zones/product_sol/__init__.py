"""
Product Sol zone — client-facing product geometry.

Modules:
- ClientGeometry Architecture Forge
- Idea Portfolio Engine (multi-idea operational success set)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.core.idea_portfolio import IdeaPortfolioEngine
from backend.core.metrics import CoreMetrics, compute_core_metrics


@dataclass
class ProductSolOutput:
    client_geometry: dict[str, Any]
    demo_idea: dict[str, Any]
    demo_ideas: list[dict[str, Any]]
    portfolio: dict[str, Any]
    metrics: CoreMetrics
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "zone": "Product Sol",
            "client_geometry": self.client_geometry,
            "demo_idea": self.demo_idea,
            "demo_ideas": self.demo_ideas,
            "portfolio": self.portfolio,
            "metrics": self.metrics.to_dict(),
            "summary": self.summary,
        }


# Шаблоны идей по индустриям × трекам (seed pool for portfolio)
IDEA_SEEDS: dict[str, dict[str, list[str]]] = {
    "ai-agencies": {
        "product": [
            "Terminal Teammate for agency ops efficiency (primary Market Unit product)",
            "Orientation-first delivery kit: map client geometry before any agent build",
            "MetaReality consult pack for agency ops geometry",
        ],
        "models": [
            "Buyer financial model that proves Terminal Teammate payback",
            "Parameter-map pricing instead of bloated retainers",
            "Day-1 payback pack: free demo idea → paid implement with unit economics",
        ],
        "promotion": [
            "Draw efficient fin models for the buying business (ops-efficiency angle)",
            "Full Package tour as the flagship lead magnet",
            "AnalogBridge post surface for agency proof stories",
        ],
    },
    "cloud-economy": {
        "product": [
            "Expert: cut third-party API spend while raising quality (creative founders)",
            "Custom expert environment vs pure LLM API (structural 12.5× unit)",
            "API burn board tied to decision owners (preserve unit-economics language)",
        ],
        "models": [
            "Third-party API cost collapse model (token + vendor APIs)",
            "Workload margin bands under expert-env path",
            "CloudForge precision under product context (kept as cost lever)",
        ],
        "promotion": [
            "Event that reviews what already ships → container + sales pointer to Expert",
            "Proof posts: before/after API unit economics for creative ops",
            "ZoneWeave post→lead for founders in productive creativity",
        ],
    },
    "cost-engineering": {
        "product": [
            "Simple product: resellable Parameter Void Scanner SKU pack",
            "SpecsForge loop for industrial cost briefs",
            "Margin-defense parameter map product",
        ],
        "models": [
            "Simple offer: 1-page parameter waste map ($290 entry)",
            "Dollar-return map per engineered parameter",
            "Rework cost refragmentation model",
        ],
        "promotion": [
            "Waste-killer case cards for ops buyers + cost-engineer clients",
            "Industrial DM funnel with free parameter map sample",
            "Linguistic Signal ads for broad audience of cost-eng referrals",
        ],
    },
    "chipmaking": {
        "product": [
            "Yield geometry twin before tapeout decisions (product offer)",
            "ChipVulnerability Void Oracle for design-loop gaps (ops offer)",
            "ClientGeometry for fab-side decision loops",
        ],
        "models": [
            "NRE vs iteration cost navigator",
            "Yield-risk informational ROI board",
            "VerdictLattice harness for design gates",
        ],
        "promotion": [
            "Semiconductor clarity event + sales pointer (promo offer)",
            "Design-team reverse outreach with void index demos",
            "Clarity posts — no buzzword fog",
        ],
    },
    "telecom": {
        "product": [
            "SLA-native product SKU builder (product offer)",
            "Linguistic Signal Weaver pack for intent↔QoS products",
            "OpticPrism care chatbot for SME plans",
        ],
        "models": [
            "ARPU / churn / capacity lever board (ops offer)",
            "Signal cooperation cost model",
            "Retention / ARPU lever pack for MVNO SME",
        ],
        "promotion": [
            "Intent-signal care weave + partner hunt (promo offer)",
            "Carrier-grade messaging: SLA, ARPU, MOS first",
            "ZoneWeave topology for tariff feature launches",
        ],
    },
    "device-assembly": {
        "product": [
            "Config product workflow: assembly → setup → guided config",
            "Station-level intellectual work instructions",
            "SpecsForge recursive instructions after station consult",
        ],
        "models": [
            "Labor / rework / throughput economics canvas",
            "SKU complexity vs margin model",
            "Terminal Teammate pre-dev for config promo kits",
        ],
        "promotion": [
            "Maker & integrator outreach with setup-that-scales stories",
            "Free demo: one station optimized end-to-end",
            "AnalogBridge posts for station before/after",
        ],
    },
}


class ProductSolZone:
    zone_id = "product_sol"
    name = "Product Sol"

    def __init__(self) -> None:
        self.portfolio_engine = IdeaPortfolioEngine(idea_seeds=IDEA_SEEDS)

    def run(
        self,
        business_text: str,
        industry_id: str,
        orientation: dict[str, Any],
        primary_track: str,
        specs_ready: bool,
    ) -> ProductSolOutput:
        scores = orientation.get("scores") or {}
        track = primary_track if primary_track in ("product", "models", "promotion") else "product"

        portfolio = self.portfolio_engine.build(
            business_text=business_text,
            industry_id=industry_id,
            orientation=orientation,
            primary_track=track,
            specs_ready=specs_ready,
        )
        demo_idea = dict(portfolio.primary)
        demo_ideas = list(portfolio.ideas)

        geometry = {
            "module": "ClientGeometry Architecture Forge",
            "advantage_brief": (
                "Architecture starts from the client's advantage — "
                "not from a preferred tech stack."
            ),
            "build_sequence": [
                "Orient industry",
                "Solution Bridge (pick from portfolio)",
                "SpecsForge recursive refine",
                "Product idea portfolio (ops success)",
                "Teammate attach",
                "Promotion angle",
                "Paid implement",
            ],
            "architecture_sketch": [
                "Infa Sol foundation",
                "Cloud Sol execution fabric",
                "Structure Fi decisions",
                "Product Sol client surface",
                "Superstructure product overlay",
            ],
            "portfolio_count": len(demo_ideas),
            "portfolio_roles": [i.get("role") for i in demo_ideas],
        }

        metrics = compute_core_metrics(
            known_params=6 if specs_ready else 4,
            required_params=8,
            ambiguity_score=0.2 if specs_ready else 0.4,
            conflict_score=0.05,
            missing_critical=0 if specs_ready else 1,
            detected_errors=1,
            actionable_errors=1,
            improvement_delta=float(scores.get("overall_orientation", 0.4)),
            fragments=max(4, len(demo_ideas)),
            successful_reassemblies=max(3, len(demo_ideas) - 1),
            structure_entropy=0.48,
            reverse_links=2,
            forward_links=max(4, len(demo_ideas)),
        )
        title = demo_idea.get("title") or "Metrix idea"
        summary = (
            f"Product Sol: portfolio n={len(demo_ideas)} · "
            f"primary «{str(title)[:50]}…» track={track}."
        )
        return ProductSolOutput(
            client_geometry=geometry,
            demo_idea=demo_idea,
            demo_ideas=demo_ideas,
            portfolio=portfolio.to_dict(),
            metrics=metrics,
            summary=summary,
        )
