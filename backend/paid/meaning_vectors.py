"""
Applied meaning vector specifications for the paid part (standard).

Хранятся отдельно от free demo path.
Consumed by PaidProductCore (block 18) package output.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class MeaningVectorSpec:
    """Спецификация смыслового вектора для paid-слоя."""

    id: str
    label: str
    dims: list[str]
    weights: dict[str, float]
    stage: str  # definition | general_paid | custom_paid
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Standard library (applied meaning vectors) — paid part
STANDARD_PAID_VECTORS: list[MeaningVectorSpec] = [
    MeaningVectorSpec(
        id="mv_orientation_paid",
        label="Orientation as paid unit",
        dims=["clarity", "impact", "parameter_density"],
        weights={"clarity": 0.4, "impact": 0.35, "parameter_density": 0.25},
        stage="general_paid",
        notes="Billable orientation run — common to all clients",
    ),
    MeaningVectorSpec(
        id="mv_implement_spine",
        label="Implement spine",
        dims=["specs_ready", "iroi", "risk_inverse"],
        weights={"specs_ready": 0.35, "iroi": 0.4, "risk_inverse": 0.25},
        stage="general_paid",
        notes="Gate for full implementation offer",
    ),
    MeaningVectorSpec(
        id="mv_custom_geometry",
        label="Custom client geometry",
        dims=["client_tokens", "void_closure", "track_balance"],
        weights={"client_tokens": 0.4, "void_closure": 0.35, "track_balance": 0.25},
        stage="custom_paid",
        notes="Deep customization vector — block 18 expands delivery",
    ),
    MeaningVectorSpec(
        id="mv_monetization_stack",
        label="Promo / MM / Auto-orders stack",
        dims=["promo_fit", "liquidity", "order_readiness"],
        weights={"promo_fit": 0.35, "liquidity": 0.35, "order_readiness": 0.3},
        stage="general_paid",
        notes="Commercial layer attached to paid package",
    ),
]


class MeaningVectorStore:
    """Store / retrieve standard + future custom paid meaning vectors."""

    def __init__(self) -> None:
        self._standard = list(STANDARD_PAID_VECTORS)

    def list_standard(self) -> list[dict[str, Any]]:
        return [v.to_dict() for v in self._standard]

    def get(self, vector_id: str) -> dict[str, Any] | None:
        for v in self._standard:
            if v.id == vector_id:
                return v.to_dict()
        return None


def get_standard_paid_vectors() -> list[dict[str, Any]]:
    return MeaningVectorStore().list_standard()
