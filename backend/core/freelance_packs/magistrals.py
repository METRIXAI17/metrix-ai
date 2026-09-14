"""Only three magistrals. No M4–M20."""

from __future__ import annotations

MAGISTRALS = {
    "M1": {
        "id": "M1",
        "path": "Consult-Diagnose → Pack-Select → Artifact → Retainer-Offer",
        "for": "TYPE_A",
    },
    "M2": {
        "id": "M2",
        "path": "Vague-Brief → Assumptions → Style-Lock → Series-Artifact",
        "for": "TYPE_B",
    },
    "M3": {
        "id": "M3",
        "path": "Sales-Pointer",
        "for": "sale talk",
    },
}


def pick_magistral(order_type: str, *, sales: bool = False) -> dict:
    if sales:
        return MAGISTRALS["M3"]
    if order_type == "TYPE_B":
        return MAGISTRALS["M2"]
    return MAGISTRALS["M1"]
