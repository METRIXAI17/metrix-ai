"""Registry of zones — single access point for Superstructure."""

from __future__ import annotations

from typing import Any

from backend.zones.cloud_sol import CloudSolZone
from backend.zones.infa_sol import InfaSolZone
from backend.zones.product_sol import ProductSolZone
from backend.zones.structure_fi import StructureFiZone


class ZoneRegistry:
    def __init__(self) -> None:
        self.infa = InfaSolZone()
        self.cloud = CloudSolZone()
        self.structure = StructureFiZone()
        self.product = ProductSolZone()

    def describe(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "infa_sol",
                "name": "Infa Sol",
                "modules": [
                    "SpecsForge Recursive Oracle",
                    "MetaReality Synthesizer",
                    "AnalogBridge Operator Surface",
                ],
            },
            {
                "id": "cloud_sol",
                "name": "Cloud Sol",
                "modules": [
                    "CloudForge Precision Optimizer",
                    "PragmaVault Pattern Lattice",
                    "Linguistic Signal Weaver (Telecom)",
                ],
            },
            {
                "id": "structure_fi",
                "name": "Structure Fi",
                "modules": [
                    "VerdictLattice Decision Core",
                    "OpticPrism Insight Lens",
                    "ZoneWeave Topology Engine",
                ],
            },
            {
                "id": "product_sol",
                "name": "Product Sol",
                "modules": ["ClientGeometry Architecture Forge"],
            },
        ]


_registry: ZoneRegistry | None = None


def get_zone_registry() -> ZoneRegistry:
    global _registry
    if _registry is None:
        _registry = ZoneRegistry()
    return _registry
