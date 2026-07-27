"""
Virtual Chips — core component 2 of the Paid Product.

Modular parametric libraries that act as virtual “hardware” inside agents
and between simulated distributors.

They are not ordinary code libraries: one template (chip) is invented once;
afterwards the graph of variants is cheaper and more scalable than adapting
rules case-by-case.

Virtual Chips carry:
  - purpose
  - zone influence
  - causal chains
  - reverse influence on the model itself

Dependency shifts onto base virtual converters:
  environment · narrative_economy · parametric_contours

Used as standardized reusable parametric modules enabling Terminal Agency
overlays and multi-agent scaling.
"""

from __future__ import annotations

import hashlib
from typing import Any

from backend.paid.types import VirtualAsset, VirtualChip, clamp01, safe_float

# ── Base chip templates (invented once) ──────────────────────────────────────

CHIP_TEMPLATES: dict[str, dict[str, Any]] = {
    "chip_orientation_core": {
        "purpose": "Anchor dynamic orientation axes and operating mode",
        "zone": "orientation",
        "params": {
            "place_mass": 0.55,
            "mine_depth": 0.5,
            "calculate_precision": 0.55,
            "mode_stability": 0.5,
        },
        "causal_chain": [
            "client_tokens",
            "axes_frame",
            "operating_mode",
            "downstream_scoring",
        ],
        "converters": ["environment", "parametric_contours"],
        "reverse_influence": {
            "value_density": 0.12,
            "readiness": 0.1,
            "clarity": 0.08,
        },
        "tags": ["orientation", "terminal_agency", "multi_agent"],
    },
    "chip_void_membrane": {
        "purpose": "Turn voids into constructor forms (not deletions)",
        "zone": "infa_sol",
        "params": {
            "void_pressure": 0.4,
            "membrane_thickness": 0.55,
            "constructor_mass": 0.5,
        },
        "causal_chain": ["missing_params", "constructor_slots", "embedding_energy"],
        "converters": ["environment", "parametric_contours"],
        "reverse_influence": {"vvi_pull": -0.1, "rrc_pull": 0.08},
        "tags": ["void", "oae", "constructor"],
    },
    "chip_mode_switch": {
        "purpose": "Gate scoring → generative → recursive → paid handoff",
        "zone": "structure_fi",
        "params": {
            "awareness_gate": 0.5,
            "generative_pull": 0.35,
            "paid_pull": 0.4,
        },
        "causal_chain": ["geometry", "decision_mode", "handoff_flags"],
        "converters": ["parametric_contours"],
        "reverse_influence": {"decision_confidence": 0.1},
        "tags": ["decision", "handoff"],
    },
    "chip_product_spine": {
        "purpose": "Hold product seed spine and implement hinge",
        "zone": "product_sol",
        "params": {
            "spine_coherence": 0.55,
            "pilot_speed": 0.5,
            "specs_lock": 0.45,
        },
        "causal_chain": ["demo_idea", "specs_gate", "paid_implement"],
        "converters": ["narrative_economy", "parametric_contours"],
        "reverse_influence": {"product_fit": 0.12, "impact": 0.1},
        "tags": ["product", "terminal_agency"],
    },
    "chip_pilot_hinge": {
        "purpose": "Day-1 payback pilot conversion surface",
        "zone": "product_sol",
        "params": {
            "payback_clarity": 0.55,
            "risk_cap": 0.4,
            "unit_economics": 0.5,
        },
        "causal_chain": ["demo_free", "pilot_offer", "implement_paid"],
        "converters": ["narrative_economy"],
        "reverse_influence": {"iroi": 0.15, "order_readiness": 0.1},
        "tags": ["pilot", "monetization"],
    },
    "chip_param_contour": {
        "purpose": "Parametric contour map for model / cost surfaces",
        "zone": "structure_fi",
        "params": {
            "contour_resolution": 0.55,
            "coverage": 0.5,
            "smoothness": 0.45,
        },
        "causal_chain": ["raw_params", "contour_field", "sensitivity_plane"],
        "converters": ["parametric_contours", "environment"],
        "reverse_influence": {"model_fit": 0.12, "param_coverage": 0.1},
        "tags": ["params", "multi_agent"],
    },
    "chip_fin_stage": {
        "purpose": "Drive fin-model three-stage paid packaging",
        "zone": "structure_fi",
        "params": {
            "definition_mass": 0.5,
            "general_paid_mass": 0.55,
            "custom_paid_mass": 0.45,
        },
        "causal_chain": ["definition", "general_paid", "custom_paid", "quote"],
        "converters": ["narrative_economy", "parametric_contours"],
        "reverse_influence": {"monetization_fit": 0.1},
        "tags": ["fin_model", "paid"],
    },
    "chip_sensitivity": {
        "purpose": "Expose derivative sensitivity across output plane",
        "zone": "market_units",
        "params": {
            "delta_step": 0.05,
            "elasticity_floor": 0.2,
            "rank_cutoff": 0.5,
        },
        "causal_chain": ["base_fn", "partial_derivatives", "ranked_levers"],
        "converters": ["parametric_contours"],
        "reverse_influence": {"function_engine_gain": 0.12},
        "tags": ["function", "sensitivity"],
    },
    "chip_narrative_economy": {
        "purpose": "Narrative economy converter between agents/distributors",
        "zone": "cloud_sol",
        "params": {
            "story_tension": 0.5,
            "token_efficiency": 0.55,
            "distributor_coupling": 0.45,
        },
        "causal_chain": [
            "message_units",
            "narrative_flow",
            "distributor_graph",
            "promo_spine",
        ],
        "converters": ["narrative_economy", "environment"],
        "reverse_influence": {"promo_fit": 0.12, "narrative_coherence": 0.1},
        "tags": ["narrative", "multi_agent", "distributor"],
    },
    "chip_promo_spine": {
        "purpose": "Promo sequence and market-making two-sided offer",
        "zone": "cloud_sol",
        "params": {
            "sequence_strength": 0.5,
            "two_sided_balance": 0.55,
            "cta_pressure": 0.45,
        },
        "causal_chain": ["promo_days", "market_make", "auto_order_gate"],
        "converters": ["narrative_economy"],
        "reverse_influence": {"liquidity": 0.1, "order_readiness": 0.08},
        "tags": ["promo", "market_making"],
    },
    "chip_liquidity": {
        "purpose": "Liquidity / market-unit energy between simulated parties",
        "zone": "market_units",
        "params": {
            "bid_depth": 0.5,
            "ask_depth": 0.5,
            "spread": 0.35,
        },
        "causal_chain": ["offer", "counteroffer", "clearing", "order"],
        "converters": ["environment", "narrative_economy"],
        "reverse_influence": {"liquidity": 0.15},
        "tags": ["market_units", "distributor"],
    },
    "chip_energy_flow": {
        "purpose": "Detect incorrect entanglement and redistribute energy",
        "zone": "market_units",
        "params": {
            "entanglement_threshold": 0.45,
            "redistribution_rate": 0.5,
            "amplitude_cap": 0.85,
        },
        "causal_chain": [
            "raw_flows",
            "entanglement_graph",
            "corrected_flows",
            "zone_balance",
        ],
        "converters": ["environment", "parametric_contours"],
        "reverse_influence": {"entanglement": -0.12, "amplitude_spread": -0.08},
        "tags": ["energy", "disentangler"],
    },
    "chip_calm_seed": {
        "purpose": "Low-entropy calm point seed for image / form generation",
        "zone": "calm_point",
        "params": {
            "entropy_floor": 0.15,
            "noise_floor": 0.12,
            "seed_coherence": 0.7,
        },
        "causal_chain": ["noise_field", "calm_point", "form_nucleation", "assembly"],
        "converters": ["environment", "parametric_contours"],
        "reverse_influence": {"entropy": -0.1, "noise": -0.08},
        "tags": ["calm_point", "physics", "image"],
    },
    "chip_map_anchor": {
        "purpose": "Anchor hypotheses on Mega Map with uncertainty radii",
        "zone": "mega_map",
        "params": {
            "coord_scale": 0.55,
            "uncertainty_base": 0.35,
            "root_gravity": 0.6,
        },
        "causal_chain": ["hypotheses", "coords", "uncertainty", "root_distance"],
        "converters": ["parametric_contours"],
        "reverse_influence": {"coordinate_uncertainty": -0.1},
        "tags": ["mega_map", "hypothesis"],
    },
    # Phenomenon → Notation → Object → Virtual Asset (Blue Ocean native)
    "chip_phenomenon_bridge": {
        "purpose": "Carry raw phenomena into notation boundaries for Reader stage 1–2",
        "zone": "orientation",
        "params": {
            "perception_gain": 0.55,
            "boundary_sharpness": 0.5,
            "naming_stability": 0.55,
        },
        "causal_chain": [
            "raw_phenomenon",
            "notation",
            "object",
            "virtual_asset",
        ],
        "converters": ["environment", "parametric_contours"],
        "reverse_influence": {"clarity": 0.1, "value_density": 0.08},
        "tags": ["phenomenon", "reader", "blue_ocean", "multi_agent"],
    },
    "chip_virtual_asset": {
        "purpose": "Brand and price-signal objectified units between agents",
        "zone": "product_sol",
        "params": {
            "weight_floor": 0.35,
            "brand_coherence": 0.55,
            "owner_clarity": 0.5,
            "price_signal_gain": 0.5,
        },
        "causal_chain": [
            "object",
            "weight_price_owner",
            "branding",
            "agent_handoff",
        ],
        "converters": ["narrative_economy", "parametric_contours"],
        "reverse_influence": {"product_fit": 0.1, "monetization_fit": 0.1},
        "tags": ["virtual_asset", "branding", "terminal_agency", "multi_agent"],
    },
    "chip_supply_contour": {
        "purpose": "Parametric contour for outgoing supply-chain vision handoff",
        "zone": "structure_fi",
        "params": {
            "stage_resolution": 0.5,
            "narrowing_alpha": 0.22,
            "horizon_depth": 0.45,
        },
        "causal_chain": [
            "statistics",
            "narrowing_model",
            "stage_amplitudes",
            "vision_open",
        ],
        "converters": ["parametric_contours", "environment"],
        "reverse_influence": {"model_fit": 0.08, "time_pressure": -0.05},
        "tags": ["conceptual_engine", "supply_chain", "open_final"],
    },
}


def _stable_noise(key: str, salt: str = "") -> float:
    """Deterministic 0..1 noise from string key (no RNG drift)."""
    h = hashlib.sha256(f"{key}:{salt}".encode("utf-8")).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


class VirtualChipLibrary:
    """
    Factory for Virtual Chips and their cheap parametric variants.

    Multi-agent / Terminal Agency overlays compose chips rather than
    rewriting per-case rules.
    """

    name = "Virtual Chips"

    def __init__(self) -> None:
        self._templates = dict(CHIP_TEMPLATES)

    def list_templates(self) -> list[dict[str, Any]]:
        out = []
        for tid, spec in self._templates.items():
            out.append(
                {
                    "id": tid,
                    "purpose": spec["purpose"],
                    "zone": spec["zone"],
                    "converters": list(spec["converters"]),
                    "tags": list(spec.get("tags") or []),
                }
            )
        return out

    def instantiate(
        self,
        template_id: str,
        *,
        params_override: dict[str, float] | None = None,
        context: dict[str, Any] | None = None,
        variant_label: str | None = None,
    ) -> VirtualChip | None:
        spec = self._templates.get(template_id)
        if not spec:
            return None
        context = context or {}
        params = {k: float(v) for k, v in (spec["params"] or {}).items()}
        if params_override:
            for k, v in params_override.items():
                params[k] = clamp01(safe_float(v, params.get(k, 0.5)))

        # Context-driven parametric modulation (cheap variant graph)
        scores = context.get("scores") or {}
        axes = context.get("axes") or {}
        for k in list(params.keys()):
            if k in scores:
                params[k] = clamp01(0.6 * params[k] + 0.4 * safe_float(scores[k]))
            elif k in axes:
                params[k] = clamp01(0.6 * params[k] + 0.4 * safe_float(axes[k]))

        amp = clamp01(
            sum(params.values()) / max(1, len(params))
            + 0.05 * _stable_noise(template_id, str(context.get("request_id", "")))
        )
        # energy_direction: source if high pilot/paid pull, sink if high void/risk
        direction = 0.0
        direction += 0.3 * params.get("paid_pull", 0.0)
        direction += 0.2 * params.get("pilot_speed", 0.0)
        direction += 0.2 * params.get("liquidity", safe_float(scores.get("promo_fit"), 0.0))
        direction -= 0.25 * params.get("void_pressure", 0.0)
        direction -= 0.2 * safe_float(axes.get("risk"), 0.3)
        direction = max(-1.0, min(1.0, direction))

        chip_id = template_id
        if variant_label:
            chip_id = f"{template_id}__{variant_label}"

        return VirtualChip(
            id=chip_id,
            template_id=template_id,
            purpose=str(spec["purpose"]),
            zone=str(spec["zone"]),
            params=params,
            causal_chain=list(spec["causal_chain"]),
            converters=list(spec["converters"]),
            reverse_influence={
                k: float(v) for k, v in (spec["reverse_influence"] or {}).items()
            },
            amplitude=amp,
            energy_direction=direction,
            variant_of=template_id if variant_label else None,
            tags=list(spec.get("tags") or []),
        )

    def build_graph(
        self,
        chip_refs: list[str],
        *,
        context: dict[str, Any] | None = None,
        library_params: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        """
        Instantiate a graph of chips from design-library refs.
        Missing refs are skipped; known templates always win over ad-hoc rules.
        """
        context = dict(context or {})
        library_params = library_params or {}
        chips: list[VirtualChip] = []
        for ref in chip_refs:
            # Soft map library params onto chip params by name intersection
            override = {
                k: v
                for k, v in library_params.items()
                if k in (self._templates.get(ref) or {}).get("params", {})
            }
            chip = self.instantiate(ref, params_override=override or None, context=context)
            if chip:
                chips.append(chip)

        # Variant expansion: one cheap variant per high-amplitude chip (scalability)
        variants: list[VirtualChip] = []
        for chip in chips:
            if chip.amplitude >= 0.55:
                v = self.instantiate(
                    chip.template_id,
                    params_override={
                        k: clamp01(v * 1.08) for k, v in chip.params.items()
                    },
                    context=context,
                    variant_label="hi_amp",
                )
                if v:
                    variants.append(v)

        # Aggregate reverse influence on model
        reverse: dict[str, float] = {}
        for chip in chips + variants:
            for k, w in chip.reverse_influence.items():
                reverse[k] = reverse.get(k, 0.0) + w * chip.amplitude
        reverse = {k: round(max(-0.5, min(0.5, v)), 4) for k, v in reverse.items()}

        # Converter dependency map
        converter_load: dict[str, int] = {}
        for chip in chips:
            for c in chip.converters:
                converter_load[c] = converter_load.get(c, 0) + 1

        zone_influence: dict[str, float] = {}
        for chip in chips:
            zone_influence[chip.zone] = round(
                zone_influence.get(chip.zone, 0.0) + chip.amplitude, 4
            )

        # Phenomenon → Virtual Asset branding surface (for Reader + Blue Ocean)
        virtual_assets = self._chips_to_virtual_assets(chips, context)

        # Causal mesh: edges between chips that share converters or chain steps
        mesh = self._causal_mesh(chips)

        return {
            "module": self.name,
            "chips": [c.to_dict() for c in chips],
            "variants": [v.to_dict() for v in variants],
            "chip_count": len(chips),
            "variant_count": len(variants),
            "reverse_influence": reverse,
            "converter_load": converter_load,
            "zone_influence": zone_influence,
            "virtual_assets": virtual_assets,
            "causal_mesh": mesh,
            "phenomenon_chain_ready": any(
                "phenomenon" in (c.tags or []) or "virtual_asset" in (c.tags or [])
                for c in chips
            )
            or len(virtual_assets) > 0,
            "terminal_agency_ready": len(chips) >= 3,
            "multi_agent_scalable": any(
                "multi_agent" in (c.tags or []) for c in chips
            ),
            "base_converters": ["environment", "narrative_economy", "parametric_contours"],
            "summary": (
                f"Instantiated {len(chips)} chips + {len(variants)} variants; "
                f"virtual_assets={len(virtual_assets)}; "
                f"converters={list(converter_load.keys())}; "
                f"zones={list(zone_influence.keys())}."
            ),
            "open_point": (
                "OPEN: cross-agent chip market (Terminal Agency bid rail) "
                "attaches via Engagement Protocol."
            ),
        }

    def _chips_to_virtual_assets(
        self,
        chips: list[VirtualChip],
        context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Each chip can surface as a branded Virtual Asset.
        Invent template once → asset graph is cheap parametric variants.
        """
        context = context or {}
        scores = context.get("scores") or {}
        assets: list[dict[str, Any]] = []
        for chip in chips:
            weight = clamp01(
                0.5 * chip.amplitude
                + 0.25 * safe_float(scores.get("product_fit"), 0.5)
                + 0.25 * abs(chip.energy_direction)
            )
            price = clamp01(weight * (0.65 + 0.35 * chip.amplitude)) * 1.15
            owner = "platform"
            if "pilot" in chip.tags or "product" in chip.tags:
                owner = "founder"
            elif "market" in chip.tags or chip.zone == "market_units":
                owner = "market"
            brand = f"MX-CHIP-{chip.template_id.replace('chip_', '').upper()[:10]}"
            va = VirtualAsset(
                id=f"va_from_{chip.id}",
                name=chip.purpose[:60],
                weight=weight,
                price_signal=price,
                owner=owner,
                branding=brand,
                zone=chip.zone,
                notation_id=f"nt_{chip.template_id}",
                chip_id=chip.id,
                tags=list(chip.tags) + ["from_chip"],
            )
            assets.append(va.to_dict())
        return assets

    def _causal_mesh(self, chips: list[VirtualChip]) -> dict[str, Any]:
        """Lightweight between-chip causal edges (no heavy graph cycles)."""
        edges: list[dict[str, str]] = []
        for i, a in enumerate(chips):
            for b in chips[i + 1 :]:
                shared_conv = set(a.converters) & set(b.converters)
                shared_chain = set(a.causal_chain) & set(b.causal_chain)
                if shared_conv or shared_chain:
                    edges.append(
                        {
                            "from": a.id,
                            "to": b.id,
                            "via": ",".join(sorted(shared_conv | shared_chain))[:80],
                        }
                    )
        return {
            "edge_count": len(edges),
            "edges": edges[:24],
            "note": "Mesh for multi-agent overlays; not a full message bus.",
        }


_vchip_lib: VirtualChipLibrary | None = None


def get_virtual_chip_library() -> VirtualChipLibrary:
    global _vchip_lib
    if _vchip_lib is None:
        _vchip_lib = VirtualChipLibrary()
    return _vchip_lib
