"""
System Design Library — core component 1 of the Paid Product.

Structured library of system-design templates, patterns and base architectures
for each industry direction and each request category.

The system loads the relevant library subset based on request type
(industry + track/category).
"""

from __future__ import annotations

from typing import Any

from backend.config import INDUSTRIES
from backend.paid.types import DesignTemplate, RequestKind, clamp01, safe_float

# ── Category patterns (shared across industries) ─────────────────────────────

_CATEGORY_PATTERNS: dict[str, dict[str, Any]] = {
    "product": {
        "pattern": "seed-spine → specs gate → demo surface → implement hinge",
        "architecture": [
            "Orientation frame",
            "Product Sol overlay",
            "SpecsForge tree",
            "Day-1 payback pilot",
        ],
        "default_params": {
            "clarity": 0.55,
            "impact": 0.5,
            "time_to_value": 0.45,
            "specs_density": 0.4,
        },
        "chip_refs": [
            "chip_orientation_core",
            "chip_product_spine",
            "chip_pilot_hinge",
            "chip_phenomenon_bridge",
            "chip_virtual_asset",
        ],
        "zone_focus": ["product_sol", "infa_sol", "orientation"],
    },
    "model": {
        "pattern": "parameter map → fin-model stages → sensitivity plane → priced pack",
        "architecture": [
            "Fin Model 3-stage template",
            "Function Calculation Engine",
            "Virtual Chip converters",
            "IROI gate",
        ],
        "default_params": {
            "model_fit": 0.55,
            "param_coverage": 0.5,
            "sensitivity_depth": 0.45,
            "monetization_fit": 0.5,
        },
        "chip_refs": ["chip_param_contour", "chip_fin_stage", "chip_sensitivity"],
        "zone_focus": ["structure_fi", "product_sol", "market_units"],
    },
    "promo": {
        "pattern": "narrative economy → promo spine → market-make → auto-order gate",
        "architecture": [
            "Cloud Sol linguistic layer",
            "Promo Automation",
            "Market Making two-sided offer",
            "Auto Orders approval gate",
        ],
        "default_params": {
            "promo_fit": 0.55,
            "liquidity": 0.45,
            "narrative_coherence": 0.5,
            "order_readiness": 0.4,
        },
        "chip_refs": ["chip_narrative_economy", "chip_promo_spine", "chip_liquidity"],
        "zone_focus": ["cloud_sol", "market_units", "product_sol"],
    },
    "orientation": {
        "pattern": "place → mine → calculate → operating mode",
        "architecture": [
            "OrientationForge axes",
            "Dynamic mode switch",
            "Void constructors",
            "Meaning vectors (paid)",
        ],
        "default_params": {
            "value_density": 0.5,
            "complexity": 0.45,
            "risk": 0.35,
            "readiness": 0.5,
        },
        "chip_refs": ["chip_orientation_core", "chip_void_membrane", "chip_mode_switch"],
        "zone_focus": ["orientation", "infa_sol", "structure_fi"],
    },
    "analysis": {
        "pattern": "energy audit → disentangle → calm point → mega map compare",
        "architecture": [
            "Energy Flow Disentangler",
            "Critical Thinking Layer",
            "Mega Map Builder",
            "Reader explanations",
        ],
        "default_params": {
            "entanglement": 0.5,
            "amplitude_spread": 0.45,
            "coordinate_uncertainty": 0.4,
            "discrepancy_pressure": 0.35,
        },
        "chip_refs": ["chip_energy_flow", "chip_calm_seed", "chip_map_anchor"],
        "zone_focus": ["market_units", "calm_point", "mega_map"],
    },
    "full_package": {
        "pattern": "orientation → product → models → promo → paid core loop",
        "architecture": [
            "Full Superstructure Overlay",
            "Decision Core + OAE",
            "Six paid components",
            "Hypothesis → Mega Map close",
        ],
        "default_params": {
            "package_coherence": 0.5,
            "handoff_readiness": 0.45,
            "iroi_pull": 0.5,
            "awareness": 0.5,
        },
        "chip_refs": [
            "chip_orientation_core",
            "chip_product_spine",
            "chip_fin_stage",
            "chip_promo_spine",
            "chip_energy_flow",
            "chip_map_anchor",
            "chip_phenomenon_bridge",
            "chip_virtual_asset",
            "chip_supply_contour",
        ],
        "zone_focus": [
            "orientation",
            "product_sol",
            "structure_fi",
            "cloud_sol",
            "market_units",
            "mega_map",
        ],
    },
    # Product building library — concrete build patterns (showcase-ready)
    "product_building": {
        "pattern": "job map → spine → parameter surface → pilot scaffold → standards TZ",
        "architecture": [
            "Job-to-be-done canvas",
            "Product spine + demo surface",
            "Parameter / lever map",
            "14–30d pilot scaffold",
            "Integration standards block",
            "Paid portal commercial surface",
        ],
        "default_params": {
            "job_clarity": 0.5,
            "spine_coherence": 0.55,
            "param_surface": 0.5,
            "pilot_readiness": 0.45,
            "standards_coverage": 0.5,
        },
        "chip_refs": [
            "chip_product_spine",
            "chip_pilot_hinge",
            "chip_param_contour",
            "chip_fin_stage",
            "chip_map_anchor",
        ],
        "zone_focus": ["product_sol", "infa_sol", "structure_fi", "mega_map"],
    },
}

# Industry-specific architectural accents
_INDUSTRY_ACCENTS: dict[str, dict[str, Any]] = {
    "ai-agencies": {
        "accent": "agent stack delivery + parameter-map pricing",
        "extra_arch": ["Agent delivery system", "Retainer → pilot conversion"],
        "param_boost": {"impact": 0.08, "promo_fit": 0.05},
    },
    "cloud-economy": {
        "accent": "unit economics + edge placement intelligence",
        "extra_arch": ["Spend intelligence layer", "Edge placement map"],
        "param_boost": {"model_fit": 0.08, "param_coverage": 0.05},
    },
    "cost-engineering": {
        "accent": "waste cut without capability cut",
        "extra_arch": ["Cost parameter map", "Capability floor guard"],
        "param_boost": {"clarity": 0.08, "sensitivity_depth": 0.06},
    },
    "chipmaking": {
        "accent": "design loop + yield + vulnerability voids",
        "extra_arch": ["Yield geometry twin", "DFT insertion gates"],
        "param_boost": {"complexity": 0.1, "specs_density": 0.06},
    },
    "telecom": {
        "accent": "network zones + linguistic ops cooperation",
        "extra_arch": ["QoS zone map", "Care ↔ core linguistic bridge"],
        "param_boost": {"narrative_coherence": 0.08, "liquidity": 0.04},
    },
    "device-assembly": {
        "accent": "assembly line params + defect energy flow",
        "extra_arch": ["Line bottleneck map", "Defect energy disentangle"],
        "param_boost": {"time_to_value": 0.06, "entanglement": 0.05},
    },
}

# Extra product-building architecture bullets per industry (library fill)
_PRODUCT_BUILDING_EXTRA: dict[str, list[str]] = {
    "ai-agencies": [
        "Agent delivery kit",
        "Orientation-first pricing page",
        "Client geometry → pilot metric",
    ],
    "cloud-economy": [
        "Margin bands UI (reserved / on-demand / edge)",
        "FinOps signal board + owners",
        "Utilization → bill bridge",
        "Specialty cloud premium tier card",
    ],
    "cost-engineering": [
        "Waste vs capability floor dashboard",
        "Parameter cut list with rollback",
    ],
    "chipmaking": [
        "Yield twin pilot board",
        "NRE stage-gate checklist",
    ],
    "telecom": [
        "QoS zone × care linguistic bridge",
        "ARPU / churn lever panel",
    ],
    "device-assembly": [
        "Bottleneck Kanban + defect energy",
        "Config SKU → margin map",
    ],
}


def _infer_category(track: str | None, request_kind: str | None) -> str:
    if request_kind and request_kind in _CATEGORY_PATTERNS:
        return request_kind
    t = (track or "all").lower().strip()
    mapping = {
        "product": "product",
        "model": "model",
        "promo": "promo",
        "orientation": "orientation",
        "analysis": "analysis",
        "product_building": "product_building",
        "build": "product_building",
        "all": "full_package",
        "full": "full_package",
        "package": "full_package",
    }
    return mapping.get(t, "full_package")


class SystemDesignLibrary:
    """
    Loads structured design templates by industry direction + category.

    Templates are invented as library entries once; the paid orchestrator
    selects the active subset per request instead of hand-writing rules.
    """

    name = "System Design Library"

    def __init__(self) -> None:
        self._templates: list[DesignTemplate] = self._build_catalog()

    def _build_catalog(self) -> list[DesignTemplate]:
        catalog: list[DesignTemplate] = []
        for industry_id, ind in INDUSTRIES.items():
            accent = _INDUSTRY_ACCENTS.get(industry_id, {})
            for cat, base in _CATEGORY_PATTERNS.items():
                params = dict(base["default_params"])
                for k, boost in (accent.get("param_boost") or {}).items():
                    if k in params:
                        params[k] = clamp01(params[k] + float(boost))
                    else:
                        params[k] = clamp01(0.5 + float(boost))

                arch = list(base["architecture"]) + list(accent.get("extra_arch") or [])
                if cat == "product_building":
                    arch = arch + list(_PRODUCT_BUILDING_EXTRA.get(industry_id, []))
                tid = f"sdl_{industry_id}_{cat}"
                catalog.append(
                    DesignTemplate(
                        id=tid,
                        name=f"{ind.get('name', industry_id)} · {cat.replace('_', ' ').title()}",
                        direction=industry_id,
                        category=cat,
                        pattern=str(base["pattern"]),
                        base_architecture=arch,
                        default_params=params,
                        chip_refs=list(base["chip_refs"]),
                        zone_focus=list(base["zone_focus"]),
                        notes=str(accent.get("accent") or ind.get("blurb") or ""),
                    )
                )
        return catalog

    def product_building_pack(self, industry_id: str) -> dict[str, Any]:
        """Dedicated pack for product-building library consumers."""
        loaded = self.load_for_request(
            industry_id, track="product_building", request_kind="product_building"
        )
        t = self.get(f"sdl_{industry_id}_product_building")
        return {
            "module": "Product Building Design Library",
            "industry_id": industry_id,
            "template": t.to_dict() if t else None,
            "architecture": loaded.get("base_architecture"),
            "pattern": loaded.get("pattern"),
            "chip_refs": loaded.get("chip_refs"),
            "params": loaded.get("merged_params"),
            "summary": (
                f"Product-building pack for {industry_id}: "
                f"{len(loaded.get('base_architecture') or [])} architecture layers."
            ),
        }

    def list_all(self) -> list[dict[str, Any]]:
        return [t.to_dict() for t in self._templates]

    def list_directions(self) -> list[str]:
        return sorted({t.direction for t in self._templates})

    def list_categories(self) -> list[str]:
        return sorted({t.category for t in self._templates})

    def get(self, template_id: str) -> DesignTemplate | None:
        for t in self._templates:
            if t.id == template_id:
                return t
        return None

    def load_for_request(
        self,
        industry_id: str,
        track: str | None = None,
        request_kind: RequestKind | str | None = None,
        *,
        include_analysis: bool = True,
    ) -> dict[str, Any]:
        """
        Primary API: load the relevant library subset for this request type.
        """
        category = _infer_category(track, request_kind if isinstance(request_kind, str) else None)
        industry_id = industry_id if industry_id in INDUSTRIES else "ai-agencies"

        primary = [
            t
            for t in self._templates
            if t.direction == industry_id and t.category == category
        ]
        # Always attach orientation backbone for the same industry
        orientation = [
            t
            for t in self._templates
            if t.direction == industry_id and t.category == "orientation"
        ]
        analysis = []
        if include_analysis and category != "analysis":
            analysis = [
                t
                for t in self._templates
                if t.direction == industry_id and t.category == "analysis"
            ]

        # Sibling categories for full package context
        siblings = [
            t
            for t in self._templates
            if t.direction == industry_id
            and t.category not in {category, "orientation", "analysis"}
        ]

        selected = primary or orientation
        merged_params: dict[str, float] = {}
        chip_refs: list[str] = []
        zone_focus: list[str] = []
        architecture: list[str] = []
        for t in selected + orientation[:1]:
            for k, v in t.default_params.items():
                merged_params[k] = max(merged_params.get(k, 0.0), float(v))
            for c in t.chip_refs:
                if c not in chip_refs:
                    chip_refs.append(c)
            for z in t.zone_focus:
                if z not in zone_focus:
                    zone_focus.append(z)
            for a in t.base_architecture:
                if a not in architecture:
                    architecture.append(a)

        return {
            "module": self.name,
            "industry_id": industry_id,
            "category": category,
            "primary": [t.to_dict() for t in selected],
            "orientation_backbone": [t.to_dict() for t in orientation[:1]],
            "analysis_layer": [t.to_dict() for t in analysis[:1]],
            "siblings": [t.to_dict() for t in siblings],
            "merged_params": {k: round(float(v), 4) for k, v in merged_params.items()},
            "chip_refs": chip_refs,
            "zone_focus": zone_focus,
            "base_architecture": architecture,
            "pattern": (selected[0].pattern if selected else "place → mine → calculate"),
            "catalog_size": len(self._templates),
            "summary": (
                f"Loaded {len(selected)} primary template(s) for {industry_id}/{category}; "
                f"chips={len(chip_refs)}, zones={len(zone_focus)}."
            ),
        }

    def blend_with_context(
        self,
        loaded: dict[str, Any],
        axes: dict[str, Any] | None = None,
        scores: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Shift library default params toward live orientation axes/scores."""
        params = dict(loaded.get("merged_params") or {})
        axes = axes or {}
        scores = scores or {}
        # Map known orientation axes into design params
        bridges = {
            "value_density": "clarity",
            "complexity": "complexity",
            "risk": "risk",
            "monetization_fit": "monetization_fit",
            "time_pressure": "time_to_value",
        }
        for axis, param in bridges.items():
            if axis in axes:
                av = safe_float(axes[axis], 0.5)
                if param in params:
                    params[param] = clamp01(0.55 * params[param] + 0.45 * av)
                else:
                    params[param] = clamp01(av)
        for sk in ("product_fit", "model_fit", "promo_fit", "readiness"):
            if sk in scores:
                key = sk if sk in params else sk
                params[key] = clamp01(
                    0.5 * params.get(key, 0.5) + 0.5 * safe_float(scores[sk], 0.5)
                )
        out = dict(loaded)
        out["merged_params"] = {k: round(float(v), 4) for k, v in params.items()}
        out["blended"] = True
        return out


# Singleton for import convenience
_library: SystemDesignLibrary | None = None


def get_system_design_library() -> SystemDesignLibrary:
    global _library
    if _library is None:
        _library = SystemDesignLibrary()
    return _library
