"""
Implementation model for THREE directions — the only paid service.

Public surface: free consult (ideas, cards, resume).
Paid (hidden from marketing surface): single SKU = implement three directions.

Directions:
  1. product_pack  — product / offer / architecture pack
  2. unit_pack     — unit economics / paid unit
  3. ch_network    — channel network / live 7-day log

Pricing and pay CTAs are INTERNAL (ops / founder pad only) — not client homepage.
"""

from __future__ import annotations

from typing import Any

# Internal only — never render on public homepage pricing strip
_INTERNAL_SKU = {
    "id": "implement_three_directions",
    "sku": "IMPL-3D",
    "surface": "internal_ops_only",
    "public_visible": False,
    "name_ru": "Внедрение · три направления",
    "name_en": "Implementation · three directions",
    "directions": ["product_pack", "unit_pack", "ch_network"],
    # price kept for ops accounting; UI must not show on public site
    "ops_price_usd": 790,
    "note": "Single paid service. Free = consult pack. Paid = implement rollout.",
}


DIRECTIONS: list[dict[str, Any]] = [
    {
        "id": "product_pack",
        "label": "L.direction.product_pack",
        "name_ru": "Product pack",
        "name_en": "Product pack",
        "deliverables": [
            "architecture_cards_A01_A12",
            "decision_S1_S4",
            "identity_uniqueness",
            "result_pack_template",
        ],
        "acceptance": [
            "Cards are path steps, not filler",
            "Boundaries / non-goals locked",
        ],
    },
    {
        "id": "unit_pack",
        "label": "L.direction.unit_pack",
        "name_ru": "Unit pack",
        "name_en": "Unit pack",
        "deliverables": [
            "unit_definition",
            "margin_or_paid_units_metric",
            "value_vs_core_gap",
            "concept_tests_T1_T3",
        ],
        "acceptance": [
            "One pilot metric",
            "Cash ceiling + days window",
        ],
    },
    {
        "id": "ch_network",
        "label": "L.direction.ch_network",
        "name_ru": "Channel network",
        "name_en": "Channel network",
        "deliverables": [
            "live_log_7d",
            "touch_target_10_15",
            "one_proof_artifact",
            "warm_list_or_referral",
        ],
        "acceptance": [
            "Not multi-channel spam",
            "Artifact shipped or scheduled",
        ],
    },
]


def build_implement_model(
    *,
    segment: dict[str, Any] | None = None,
    path: dict[str, Any] | None = None,
    expert: dict[str, Any] | None = None,
    lang: str = "ru",
    expose_price: bool = False,
) -> dict[str, Any]:
    """
    Build the three-direction implement model.

    expose_price=False (default) — hide commercial fields (public / generate).
    expose_price=True — ops panel / founder only.
    """
    L = "en" if (lang or "").lower().startswith("en") else "ru"
    seg = (segment or {}).get("primary") or segment or {}
    fit_map = seg.get("implement_fit") or {
        "product_pack": 0.65,
        "unit_pack": 0.65,
        "ch_network": 0.65,
    }
    path_obj = (path or {}).get("path") or path or {}
    spine = path_obj.get("spine") or ["product_pack", "unit_pack", "ch_network"]

    directions_out = []
    for d in DIRECTIONS:
        fit = float(fit_map.get(d["id"], 0.6))
        priority = spine.index(d["id"]) + 1 if d["id"] in spine else 9
        directions_out.append(
            {
                "id": d["id"],
                "label": d["label"],
                "name": d["name_en"] if L == "en" else d["name_ru"],
                "deliverables": d["deliverables"],
                "acceptance": d["acceptance"],
                "segment_fit": round(fit, 4),
                "priority": priority,
                "status": "model_ready",
            }
        )
    directions_out.sort(key=lambda x: x["priority"])

    expert_top = ((expert or {}).get("top") or [])[:3]
    model = {
        "module": "ImplementModel",
        "version": "1.0.0",
        "sku_id": _INTERNAL_SKU["id"],
        "only_paid_service": True,
        "public_visible_price": False,
        "directions": directions_out,
        "direction_count": 3,
        "spine_order": [d["id"] for d in directions_out],
        "linked_expert_directions": [e.get("id") for e in expert_top],
        "path_id": path_obj.get("id"),
        "segment_id": seg.get("id"),
        "unlock": "implementation_approval",
        "hidden_commercial": True,
        "public_message": (
            "Free consult pack ready. Implementation is a separate technical rollout of three directions — configured in ops."
            if L == "en"
            else "Бесплатный consult pack готов. Внедрение — отдельная техническая раскатка трёх направлений, настраивается в ops."
        ),
        "wayd_labels": [d["label"] for d in DIRECTIONS] + ["L.rail.hide_paid_surface"],
    }

    if expose_price:
        model["ops_commercial"] = {
            "sku": _INTERNAL_SKU["sku"],
            "name": _INTERNAL_SKU["name_en"] if L == "en" else _INTERNAL_SKU["name_ru"],
            "price_usd": _INTERNAL_SKU["ops_price_usd"],
            "surface": "internal_ops_only",
            "warning": "Do not render on public homepage",
        }
    else:
        # Explicit redaction
        model["ops_commercial"] = None
        model["price_redacted"] = True

    return model


def redact_paid_surface(payload: dict[str, Any]) -> dict[str, Any]:
    """Strip commercial price fields from a generate payload for public API responses."""
    if not isinstance(payload, dict):
        return payload
    out = dict(payload)
    # Hook plan price — keep structure but mark hidden
    hook = out.get("hook_plan")
    if isinstance(hook, dict):
        h = dict(hook)
        if "price_usd" in h:
            h["price_usd_hidden"] = True
            h.pop("price_usd", None)
        if "price" in h:
            h.pop("price", None)
        h["commercial_hidden"] = True
        out["hook_plan"] = h
    # core value_vs_core tariff noise
    cr = out.get("core_report")
    if isinstance(cr, dict):
        cr2 = dict(cr)
        vvc = cr2.get("value_vs_core")
        if isinstance(vvc, dict):
            v2 = dict(vvc)
            for k in ("tariff_price_usd", "price_usd", "gap_usd", "realized_mid_usd"):
                if k in v2:
                    v2[f"{k}_redacted"] = True
                    v2.pop(k, None)
            v2["commercial_hidden"] = True
            cr2["value_vs_core"] = v2
        out["core_report"] = cr2
    # implement model ensure hidden
    im = out.get("implement_model")
    if isinstance(im, dict):
        im2 = dict(im)
        im2["ops_commercial"] = None
        im2["price_redacted"] = True
        im2["public_visible_price"] = False
        out["implement_model"] = im2
    # assist offer soft language
    aa = out.get("assist_agent")
    if isinstance(aa, dict):
        offer = dict(aa.get("offer") or {})
        offer["price_note"] = offer.get("price_note") or "internal"
        offer["public_price"] = None
        aa2 = dict(aa)
        aa2["offer"] = offer
        out["assist_agent"] = aa2
    return out
