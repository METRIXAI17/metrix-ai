"""Health & catalog endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from backend import __brand__, __codename__, __version__
from backend.config import (
    CLIENT_NICHE_LIST_RU,
    DECISION_SUPPORT_PRODUCT,
    ENV_NAME,
    INDUSTRIES,
    MONETIZATION,
    PUBLIC_INDUSTRY_IDS,
    TRACKS,
    ZONES,
)
from backend.fin_models.registry import get_fin_model_registry
from backend.zones.registry import get_zone_registry

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "brand": __brand__,
        "codename": __codename__,
        "version": __version__,
        "env": ENV_NAME,
        "service": "metrix-ai-backend",
        "public_niches": PUBLIC_INDUSTRY_IDS,
        "decision_support": DECISION_SUPPORT_PRODUCT.get("id"),
    }


@router.get("/catalog")
def catalog() -> dict:
    zones = get_zone_registry().describe()
    fins = get_fin_model_registry().list_models()
    public = [INDUSTRIES[i] for i in PUBLIC_INDUSTRY_IDS if i in INDUSTRIES]
    return {
        "industries": public,
        "all_industries": list(INDUSTRIES.values()),
        "client_niche_list_ru": CLIENT_NICHE_LIST_RU,
        "decision_support_product": DECISION_SUPPORT_PRODUCT,
        "tracks": list(TRACKS),
        "zones": zones + [{"id": "superstructure", "name": ZONES["superstructure"], "modules": ["Product Overlay"]}],
        "fin_models": fins,
        "monetization": MONETIZATION,
        "module_names": {
            "specs": "SpecsForge Recursive Oracle",
            "meta_reality": "MetaReality Synthesizer",
            "analog": "AnalogBridge Operator Surface",
            "cloud": "CloudForge Precision Optimizer",
            "pragma": "PragmaVault Pattern Lattice",
            "linguistic": "Linguistic Signal Weaver (Telecom)",
            "verdict": "VerdictLattice Decision Core",
            "decision_core": "Enhanced Decision Making Core",
            "oae": "Main Operational Analytics Engine",
            "success_metrics": "Custom Success Metrics Positioning",
            "optic": "OpticPrism Insight Lens",
            "zone_weave": "ZoneWeave Topology Engine",
            "client": "ClientGeometry Architecture Forge",
            "orientation": "OrientationForge Dynamic Compass",
            "profit": "Informational Profitability Oracle",
            "structure": "IdeaStructure Synthesizer",
        },
        "roadmap_slots": {
            "18": "backend/paid — Paid Product Core",
            "19": "backend/generative — Generativity Concept",
        },
    }
