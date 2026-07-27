"""
Blue Ocean Identifier bridge — compatibility layer for Meta-Reality Engine.

Architecture blocks (exact names):
  1. Synthesis Core
  2. Reality Layer Interface
  3. Symmetry Bridge
  4. Value Proposition Engine
  5. Engagement & Transaction Protocol
  6. Metrix Ledger & Operational Core

This module does NOT fake live blockchain / bidding markets.
It builds deterministic structural maps from paid-core outputs and leaves
honest OPEN points where external feeds or contracts attach later.
"""

from __future__ import annotations

from typing import Any

from backend.paid.types import clamp01, safe_float


class BlueOceanBridge:
    """
    Synthesize Blue Ocean Identifier surfaces from a finished (or partial)
    paid-core bundle + orientation/OAE parallel context.
    """

    name = "Blue Ocean Identifier Bridge"

    def synthesize(
        self,
        *,
        paid: dict[str, Any],
        industry_id: str,
        business: str = "",
        oae: dict[str, Any] | None = None,
        decision: dict[str, Any] | None = None,
        scores: dict[str, float] | None = None,
        axes: dict[str, float] | None = None,
        virtual_assets: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        paid = paid or {}
        oae = oae or {}
        decision = decision or {}
        scores = {k: safe_float(v) for k, v in (scores or {}).items()}
        axes = {k: safe_float(v) for k, v in (axes or {}).items()}
        virtual_assets = virtual_assets or []

        plane = (paid.get("function_engine") or {}).get("output_plane") or {}
        energy = paid.get("energy_flow") or {}
        mega = paid.get("mega_map") or {}
        comparison = mega.get("comparison") or {}
        chips = paid.get("virtual_chips") or {}
        hyp = paid.get("hypotheses") or {}
        metrics = paid.get("business_metrics") or paid.get("situation_metrics") or {}
        package = paid.get("package") or {}
        reader = paid.get("reader") or {}

        # ── 1. Synthesis Core ────────────────────────────────────────────
        # G-AI analog: deterministic synthesis from chips + hypotheses + OAE
        s1 = (reader.get("stages") or {}).get("1_perception") or {}
        phenomena = list(s1.get("phenomena") or []) if isinstance(s1, dict) else []
        if not phenomena:
            # Fallback phenomena from root + energy
            phenomena = [
                {
                    "id": "ph_root",
                    "raw": paid.get("root_task") or business[:80],
                    "source": "business",
                    "amplitude": 0.6,
                },
                {
                    "id": "ph_energy",
                    "raw": f"entanglement={energy.get('total_entanglement')}",
                    "source": "energy",
                    "amplitude": safe_float(energy.get("total_entanglement"), 0.4),
                },
            ]
        graph_nodes = []
        for c in chips.get("chips") or []:
            graph_nodes.append(
                {
                    "id": c.get("id"),
                    "kind": "chip",
                    "zone": c.get("zone"),
                    "amp": c.get("amplitude"),
                }
            )
        for h in (hyp.get("hypotheses") or hyp.get("scored_hypotheses") or [])[:8]:
            graph_nodes.append(
                {
                    "id": h.get("id"),
                    "kind": "hypothesis",
                    "claim": (h.get("claim") or "")[:80],
                    "conf": h.get("confidence") or h.get("navigator_score"),
                }
            )
        synthesis_core = {
            "block": "Synthesis Core",
            "g_ai_mode": "deterministic_parametric_synthesis",
            "phenomenon_graph": {
                "nodes": graph_nodes,
                "node_count": len(graph_nodes),
                "phenomena_count": len(phenomena),
            },
            "potential_phenomenon_space": {
                "axes": {
                    "product": safe_float(plane.get("product_axis"), scores.get("product_fit", 0.5)),
                    "model": safe_float(plane.get("model_axis"), scores.get("model_fit", 0.5)),
                    "promo": safe_float(plane.get("promo_axis"), scores.get("promo_fit", 0.5)),
                    "risk": axes.get("risk", 0.35),
                },
                "open_volume": round(
                    clamp01(1.0 - safe_float(comparison.get("root_alignment_score"), 0.5)),
                    4,
                ),
                "note": "Space of still-unclaimed combinations near root task",
            },
            "summary": (
                f"Synthesis Core: {len(graph_nodes)} graph nodes, "
                f"{len(phenomena)} phenomena, open_volume="
                f"{clamp01(1.0 - safe_float(comparison.get('root_alignment_score'), 0.5)):.2f}."
            ),
        }

        # ── 2. Reality Layer Interface ───────────────────────────────────
        embedding = oae.get("embedding") or {}
        reality_layer = {
            "block": "Reality Layer Interface",
            "real_time_streamers": {
                "status": "stub_ready",
                "active_feeds": [],
                "open_point": "OPEN: attach live market / usage streamers per client.",
            },
            "nlp_feature_extractor": {
                "business_excerpt": (business or "")[:160],
                "token_signals": _soft_tokens(business),
                "mode": "deterministic_lexicon",  # not cloud LLM dump
            },
            "current_innovation_landscape": {
                "industry_id": industry_id,
                "decision_mode": decision.get("active_mode") or decision.get("mode"),
                "oae_dims": list((embedding.get("dimensions") or embedding.get("vector") or [])[:12])
                if isinstance(embedding, dict)
                else [],
                "scores": scores,
            },
            "summary": "Reality Layer: lexicon + OAE landscape; live streamers OPEN.",
        }

        # ── 3. Symmetry Bridge ───────────────────────────────────────────
        best_id = comparison.get("best_hypothesis_id")
        blue_ocean_ids = []
        for h in (hyp.get("hypotheses") or [])[:5]:
            conf = safe_float(h.get("navigator_score", h.get("confidence")), 0.5)
            dist = 0.5
            for p in mega.get("points") or []:
                if p.get("hypothesis_id") == h.get("id"):
                    dist = safe_float(p.get("distance_to_root"), 0.5)
                    break
            # Blue ocean-ish: high novelty (distance) but usable confidence
            novelty = clamp01(dist)
            usability = conf
            blue_score = clamp01(0.55 * usability + 0.45 * novelty * (1.0 - 0.3 * novelty))
            blue_ocean_ids.append(
                {
                    "hypothesis_id": h.get("id"),
                    "claim": (h.get("claim") or "")[:100],
                    "novelty": round(novelty, 4),
                    "usability": round(usability, 4),
                    "blue_ocean_score": round(blue_score, 4),
                    "is_bifurcation_candidate": blue_score >= 0.55 and novelty >= 0.25,
                }
            )
        blue_ocean_ids.sort(key=lambda x: -x["blue_ocean_score"])
        bifurcation_targets = [
            b for b in blue_ocean_ids if b.get("is_bifurcation_candidate")
        ][:3]
        symmetry_bridge = {
            "block": "Symmetry Bridge",
            "quantum_similarity_engine": {
                "mode": "cosine_coord_proximity",
                "root_alignment": comparison.get("root_alignment_score"),
                "competing_pairs": comparison.get("competing_pairs"),
                "best_hypothesis_id": best_id,
            },
            "bifurcation_point_detector": {
                "targets": bifurcation_targets,
                "count": len(bifurcation_targets),
                "method": "novelty×usability with soft mid-novelty peak",
            },
            "blue_ocean_identifiers": blue_ocean_ids[:5],
            "summary": (
                f"Symmetry Bridge: {len(blue_ocean_ids)} identifiers, "
                f"{len(bifurcation_targets)} bifurcation targets."
            ),
        }

        # ── 4. Value Proposition Engine ──────────────────────────────────
        situation = metrics.get("situation_score")
        top_leak = metrics.get("top_leak") or {}
        value_prop = {
            "block": "Value Proposition Engine",
            "solution_design_framework": {
                "pattern": (paid.get("system_design_library") or {}).get("pattern"),
                "architecture": (paid.get("system_design_library") or {}).get(
                    "base_architecture"
                ),
                "product_building_pack": bool(
                    paid.get("product_building_library")
                ),
            },
            "roi_predictor": {
                "paid_score": package.get("paid_score") or paid.get("paid_score"),
                "iroi_plane": plane.get("abstract_value"),
                "situation_score": situation,
                "top_lever": (paid.get("function_engine") or {}).get("top_lever"),
                "top_leak": top_leak.get("id") or top_leak.get("name"),
                "confidence": clamp01(
                    0.5 * safe_float(package.get("paid_score"), 0.5)
                    + 0.3 * safe_float(situation, 0.5)
                    + 0.2 * (1.0 - safe_float(energy.get("total_entanglement"), 0.4))
                ),
                "honesty": "Not a financial guarantee — parametric readiness signal.",
            },
            "capital_1_1_protocol": {
                "status": "structural_ready",
                "virtual_assets": len(virtual_assets),
                "open_point": (
                    "OPEN: 1:1 capital integration attaches after founder review "
                    "and pilot TZ acceptance."
                ),
            },
            "summary": (
                f"Value Prop: readiness={package.get('paid_score')}, "
                f"ROI conf={(0.5 * safe_float(package.get('paid_score'), 0.5)):.2f}+, "
                f"assets={len(virtual_assets)}."
            ),
        }

        # ── 5. Engagement & Transaction Protocol ─────────────────────────
        cq = paid.get("clarifying_questions") or paid.get("must_ask") or {}
        engagement = {
            "block": "Engagement & Transaction Protocol",
            "owner_engagement_interface": {
                "must_ask_count": cq.get("must_count") or len(cq.get("must_ask") or []),
                "portal_url": (paid.get("portal") or {}).get("url"),
                "status": package.get("status") or paid.get("status"),
            },
            "ai_agent_bidding_system": {
                "status": "structural_stub",
                "chip_agents": [
                    c.get("id") for c in (chips.get("chips") or []) if "multi_agent" in (c.get("tags") or [])
                ],
                "open_point": "OPEN: multi-agent bid market uses Virtual Chip overlays.",
            },
            "smart_contract_execution": {
                "status": "not_executed",
                "pilot_tz": bool(paid.get("pilot_tz_draft")),
                "open_point": "OPEN: legal/smart-contract rail per jurisdiction.",
            },
            "summary": "Engagement: portal + must-ask; bidding/contracts OPEN.",
        }

        # ── 6. Metrix Ledger & Operational Core ──────────────────────────
        ledger = {
            "block": "Metrix Ledger & Operational Core",
            "multi_currency_crypto_accounting": {
                "status": "structural_stub",
                "open_point": "OPEN: multi-currency ledger adapter.",
            },
            "speech_to_text_billing": {
                "status": "structural_stub",
                "open_point": "OPEN: STT → billing processor.",
            },
            "data_value_accretion": {
                "learning_iteration": (paid.get("hypothesis_library") or {}).get(
                    "iteration", 1
                ),
                "trajectory_steps": len(
                    (paid.get("conceptual_trajectory") or {}).get("steps") or []
                ),
                "virtual_assets": len(virtual_assets),
            },
            "compliance_logger": {
                "founder_error_logged": bool(
                    (paid.get("critical_thinking") or {}).get("founder_error", {}).get(
                        "suspected"
                    )
                ),
                "overclaim_guard": True,
            },
            "ai_business_assistant_interface": {
                "reader_summary": (reader.get("plain_summary") or "")[:200],
                "action_bullets": list(reader.get("action_bullets") or [])[:5],
            },
            "summary": "Ledger/Ops: accretion + compliance hooks; crypto/STT OPEN.",
        }

        # Aggregate blue-ocean score for packaging honesty
        top_bo = blue_ocean_ids[0]["blue_ocean_score"] if blue_ocean_ids else 0.0
        aggregate = clamp01(
            0.35 * safe_float(package.get("paid_score"), 0.5)
            + 0.25 * top_bo
            + 0.20 * safe_float(comparison.get("root_alignment_score"), 0.5)
            + 0.20 * safe_float(value_prop["roi_predictor"]["confidence"], 0.5)
        )

        return {
            "module": self.name,
            "architecture": {
                "synthesis_core": synthesis_core,
                "reality_layer_interface": reality_layer,
                "symmetry_bridge": symmetry_bridge,
                "value_proposition_engine": value_prop,
                "engagement_transaction_protocol": engagement,
                "metrix_ledger_operational_core": ledger,
            },
            "flow_native": {
                "phenomenon_to_virtual_asset": True,
                "reader_stages": True,
                "virtual_chips": True,
            },
            "blue_ocean_top": blue_ocean_ids[:3],
            "bifurcation_targets": bifurcation_targets,
            "aggregate_readiness": round(aggregate, 4),
            "open_points": [
                "OPEN: live Reality Layer streamers",
                "OPEN: agent bidding market execution",
                "OPEN: smart-contract rail",
                "OPEN: multi-currency crypto accounting",
                "OPEN: STT billing processor",
                "OPEN: Conceptual Engine supply-chain vision (last planning step)",
            ],
            "summary": (
                f"Blue Ocean bridge: readiness={aggregate:.2f}, "
                f"identifiers={len(blue_ocean_ids)}, "
                f"bifurcations={len(bifurcation_targets)}."
            ),
        }


def _soft_tokens(text: str) -> list[str]:
    t = (text or "").lower()
    keys = (
        "рычаг", "lever", "margin", "марж", "cloud", "облак", "agent", "агент",
        "delivery", "достав", "unit", "churn", "отток", "gpu", "pilot", "пилот",
        "supply", "цепоч", "vision", "вижн",
    )
    return [k for k in keys if k in t]
