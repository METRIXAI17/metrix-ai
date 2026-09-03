"""Resource Assembly — first act of chain.

Chain does not start from client text. Chain starts when resources bind to
empty constructor-form slots. Without bind there is no chain_id.

Compatibility formula (feeds pilot k, y0 and L=0.92):
  compat = 0.45·(critical_bound / critical_n)
         + 0.25·mean(primary confidence)
         + 0.15·(1 − deadlock_risk)
         + 0.15·load_balance
Deadlock/load come from Market Units coordination — not a second matrix.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from backend.core.circle_system.chain_store import load_chain, save_chain
from backend.core.circle_system.knowledge_libs import get_traditional_artefact
from backend.core.circle_system.resource_match import ResourceMatchEngine
from backend.core.market_units_v2.coordination import CoordinationLayer
from backend.core.naming_canon import chain_sigil
from backend.core.superstructure import OverlayPassage
from backend.paid.types import clamp01

CRITICAL_SLOTS = ("outcome_frame", "void_membrane", "revenue_hinge", "product_sol")
ZONE_SLOTS = ("infra_sol", "cloud_sol", "structure_fi", "product_sol")
FORM_SLOTS = (
    "outcome_frame",
    "role_lattice",
    "signal_port",
    "value_pipeline",
    "bound_shell",
    "success_gauge",
    "void_membrane",
    "revenue_hinge",
    "open_manifold",
    *ZONE_SLOTS,
)

PARAM_TO_FORM = {
    "goal": "outcome_frame",
    "actors": "role_lattice",
    "client_segment": "role_lattice",
    "inputs": "signal_port",
    "process": "value_pipeline",
    "offer": "value_pipeline",
    "constraints": "bound_shell",
    "constraint": "bound_shell",
    "metrics": "success_gauge",
    "metric": "success_gauge",
    "success_criterion": "success_gauge",
    "risks": "void_membrane",
    "resource": "infra_sol",
    "integration": "cloud_sol",
    "timeline": "structure_fi",
    "pilot_scope": "product_sol",
    "monetization": "revenue_hinge",
}

KIND_TO_SLOTS = {
    "url": ("signal_port", "cloud_sol"),
    "file": ("bound_shell", "infra_sol"),
    "file_meta": ("bound_shell", "infra_sol"),
    "knowledge_id": ("success_gauge", "open_manifold"),
    "market_unit_id": ("product_sol", "revenue_hinge", "role_lattice"),
    "artefact_id": (),  # filled from artefact.affects
    "human_note": ("outcome_frame",),
    "data": ("signal_port", "success_gauge"),
    "compute": ("cloud_sol", "infra_sol"),
    "human": ("role_lattice", "product_sol"),
    "capital": ("revenue_hinge", "structure_fi"),
    "channel": ("signal_port", "product_sol"),
    "ip": ("value_pipeline", "product_sol"),
}


def _rid(raw: dict[str, Any]) -> str:
    for k in ("id", "resource_id", "artefact_id", "knowledge_id", "market_unit_id"):
        if raw.get(k):
            return str(raw[k])
    blob = json.dumps(raw, sort_keys=True, ensure_ascii=False, default=str)
    return "res_" + hashlib.sha1(blob.encode("utf-8")).hexdigest()[:10]


def _kind(raw: dict[str, Any]) -> str:
    if raw.get("artefact_id"):
        return "artefact_id"
    if raw.get("knowledge_id"):
        return "knowledge_id"
    if raw.get("market_unit_id"):
        return "market_unit_id"
    if raw.get("url"):
        return "url"
    if raw.get("file") or raw.get("file_meta"):
        return "file"
    if raw.get("human_note") or raw.get("note"):
        return "human_note"
    return str(raw.get("type") or raw.get("kind") or "human_note")


def _slots_for(raw: dict[str, Any]) -> list[str]:
    kind = _kind(raw)
    slots: list[str] = []
    if kind == "artefact_id":
        art = get_traditional_artefact(str(raw.get("artefact_id") or raw.get("id") or ""))
        if art:
            slots.extend(art.get("affects") or [])
    slots.extend(KIND_TO_SLOTS.get(kind, ()))
    extra = raw.get("slots") or raw.get("affects") or []
    if isinstance(extra, (list, tuple)):
        slots.extend(str(s) for s in extra)
    out = []
    for s in slots:
        if s in FORM_SLOTS and s not in out:
            out.append(s)
    return out or ["open_manifold"]


def _confidence(raw: dict[str, Any], slot: str) -> float:
    base = float(raw.get("confidence") or raw.get("strength") or 0.55)
    if _kind(raw) == "artefact_id":
        art = get_traditional_artefact(str(raw.get("artefact_id") or raw.get("id") or ""))
        if art:
            if art.get("evidence_grade") == "contested":
                return 0.0  # contested never raises assembly
            if art.get("evidence_grade") == "codified":
                base = max(base, 0.7)
            if slot not in (art.get("affects") or []):
                return min(base, 0.25)
    return clamp01(base)


def chain_seed_of(*, resource_ids: list[str], industry_id: str, bound_slots: list[str]) -> str:
    raw = "|".join(
        [
            industry_id or "-",
            ",".join(sorted(resource_ids)),
            ",".join(sorted(bound_slots)),
        ]
    )
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


class ResourceAssemblyEngine:
    """Bind resources to constructor-form slots. First act of chain."""

    name = "Resource Assembly Engine"
    version = "1.8.1"

    def __init__(self) -> None:
        self.match = ResourceMatchEngine()
        self.coord = CoordinationLayer()

    def bind(
        self,
        resources: list[dict[str, Any]] | None,
        *,
        request_payload: dict[str, Any] | None = None,
        voids: dict[str, Any] | None = None,
        persist: bool = True,
    ) -> dict[str, Any]:
        payload = dict(request_payload or {})
        industry_id = str(payload.get("industry") or payload.get("industry_id") or "ai-agencies")
        text = str(payload.get("business") or payload.get("text") or "")
        raw_list = [dict(r) for r in (resources or []) if isinstance(r, dict)]

        # Text-detected inventory can join as resources, still a bind.
        detected = self.match.run(text, certainty_result=payload.get("certainty"))
        for item in detected.get("inventory") or []:
            if not any(_rid(r) == item.get("resource_id") for r in raw_list):
                raw_list.append(
                    {
                        "id": item.get("resource_id"),
                        "type": item.get("type"),
                        "confidence": float(item.get("strength") or 0.4),
                    }
                )

        vvi = float((voids or {}).get("vvi") or payload.get("vvi") or 0.4)
        bound: dict[str, dict[str, Any]] = {}
        secondaries: dict[str, list[str]] = {}
        owners: dict[str, str] = {}

        ranked: list[tuple[float, str, str, dict[str, Any]]] = []
        for raw in raw_list:
            rid = _rid(raw)
            for slot in _slots_for(raw):
                ranked.append((_confidence(raw, slot), slot, rid, raw))
        ranked.sort(key=lambda x: (-x[0], x[1], x[2]))

        for conf, slot, rid, raw in ranked:
            zone = slot if slot in ZONE_SLOTS else _zone_for(slot)
            if slot not in bound:
                bound[slot] = {
                    "slot": slot,
                    "resource_id": rid,
                    "confidence": round(conf, 4),
                    "zone": zone,
                    "kind": _kind(raw),
                    "primary": True,
                }
                owners[slot] = rid
            else:
                secondaries.setdefault(slot, []).append(rid)

        unbound_critical = [s for s in CRITICAL_SLOTS if s not in bound or float(bound[s]["confidence"]) <= 0]
        n_crit = len(CRITICAL_SLOTS)
        n_bound = n_crit - len(unbound_critical)
        mean_conf = (
            sum(float(bound[s]["confidence"]) for s in bound) / max(1, len(bound)) if bound else 0.0
        )

        coord = self.coord.compute(
            density=clamp01(len(bound) / max(1, len(FORM_SLOTS))),
            readiness_band="orientation_needed" if unbound_critical else "ready",
            teammate_coverage=mean_conf,
            ontology_fit=0.55 if bound else 0.3,
            health=clamp01(1.0 - vvi),
        )
        deadlock = float(coord.deadlock_risk)
        load_b = float(coord.load_balance)
        compat = clamp01(
            0.45 * (n_bound / n_crit)
            + 0.25 * mean_conf
            + 0.15 * (1.0 - deadlock)
            + 0.15 * load_b
        )
        if unbound_critical:
            void_delta = round(-0.04 * len(unbound_critical), 4)  # VVI rises when critical slots stay empty
        else:
            void_delta = round(min(vvi, 0.08 * n_bound + 0.03 * max(0, len(bound) - n_bound)), 4)

        resource_ids = sorted({_rid(r) for r in raw_list})
        bound_slot_ids = sorted(bound.keys())
        seed = chain_seed_of(
            resource_ids=resource_ids,
            industry_id=industry_id,
            bound_slots=bound_slot_ids,
        )
        chain_id = f"CH-{seed}"
        fragments = bound_slot_ids + resource_ids[:8]
        sigil = chain_sigil(seed, fragments)

        passages = [
            OverlayPassage(
                from_zone="orientation",
                to_zone="infa_sol",
                reason="resource bind → infra slot",
                artifact_keys=[bound[s]["resource_id"] for s in bound if bound[s]["zone"] == "infra_sol"],
            ).to_dict(),
            OverlayPassage(
                from_zone="infa_sol",
                to_zone="cloud_sol",
                reason="resource bind → cloud slot",
                artifact_keys=[bound[s]["resource_id"] for s in bound if bound[s]["zone"] == "cloud_sol"],
            ).to_dict(),
            OverlayPassage(
                from_zone="cloud_sol",
                to_zone="structure_fi",
                reason="resource bind → structure slot",
                artifact_keys=[bound[s]["resource_id"] for s in bound if bound[s]["zone"] == "structure_fi"],
            ).to_dict(),
            OverlayPassage(
                from_zone="structure_fi",
                to_zone="product_sol",
                reason="resource bind → product slot",
                artifact_keys=[bound[s]["resource_id"] for s in bound if bound[s]["zone"] == "product_sol"],
            ).to_dict(),
        ]

        assembly = {
            "module": self.name,
            "version": self.version,
            "bound_slots": bound,
            "unbound_critical": unbound_critical,
            "compatibility": round(compat, 4),
            "compatibility_score": round(compat, 4),  # pilot_predictor contract
            "void_delta": void_delta,
            "vvi_after_bind": round(clamp01(vvi - void_delta), 4),
            "chain_seed": seed,
            "chain_id": chain_id,
            "public_sigil": sigil,
            "passages": passages,
            "secondaries": secondaries,
            "primary_owners": owners,
            "coordination": {
                "deadlock_risk": round(deadlock, 4),
                "load_balance": round(load_b, 4),
                "sync_score": round(float(coord.sync_score), 4),
            },
            "formula": (
                "compat = 0.45·(critical_bound/4) + 0.25·mean(primary) "
                "+ 0.15·(1-deadlock) + 0.15·load_balance; L=0.92 via pilot k,y0"
            ),
            "rule": "no bind → no chain_id; contested artefacts do not raise assembly",
            "detected_inventory": detected.get("inventory") or [],
        }

        if persist:
            save_chain(
                {
                    "chain_id": chain_id,
                    "chain_seed": seed,
                    "public_sigil": sigil,
                    "industry_id": industry_id,
                    "topology": payload.get("topology") or "unset",
                    "resource_assembly": assembly,
                    "request_excerpt": text[:240],
                    "vvi": vvi,
                }
            )
        return assembly

    def get(self, chain_id: str) -> dict[str, Any] | None:
        return load_chain(chain_id)


def _zone_for(slot: str) -> str:
    if slot in ZONE_SLOTS:
        return slot
    if slot in ("outcome_frame", "value_pipeline", "success_gauge"):
        return "product_sol"
    if slot in ("revenue_hinge", "bound_shell"):
        return "structure_fi"
    if slot in ("signal_port", "open_manifold"):
        return "cloud_sol"
    return "infra_sol"


def bind_resources(
    resources: list[dict[str, Any]] | None,
    **kwargs: Any,
) -> dict[str, Any]:
    return ResourceAssemblyEngine().bind(resources, **kwargs)
