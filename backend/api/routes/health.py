"""Health & catalog endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from backend import __brand__, __codename__, __version__
from backend.config import INDUSTRIES, MONETIZATION, TRACKS, ZONES
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
        "service": "metrix-ai-backend",
    }


@router.get("/catalog")
def catalog() -> dict:
    zones = get_zone_registry().describe()
    fins = get_fin_model_registry().list_models()
    return {
        "industries": list(INDUSTRIES.values()),
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
