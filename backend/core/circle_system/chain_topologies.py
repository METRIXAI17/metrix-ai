"""B2C chain and A2A chain. Different constructors. Mixed → Dual path."""

from __future__ import annotations

from typing import Any

from backend.core.circle_system.chain_store import load_chain, save_chain
from backend.core.circle_system.copy_firmware import CopyFirmware
from backend.core.circle_system.free_work_flow import FreeWorkFlow
from backend.core.circle_system.resource_chain import ResourceAssemblyEngine
from backend.paid.types import clamp01

B2C_PHASES = (
    {"id": "D0-1", "title_en": "Start", "title_ru": "Старт", "days": "0–1"},
    {"id": "D1-4", "title_en": "Tests / assembly", "title_ru": "Тесты / сборка", "days": "1–4"},
    {"id": "D3-10", "title_en": "Tech write spine", "title_ru": "Стержень тех-ТЗ", "days": "3–10"},
)


def detect_topology(text: str, *, track: str = "", contact_type: str = "") -> str:
    low = (text or "").lower()
    a2a_hits = any(
        w in low
        for w in ("агентств", "agencies", "handoff", "market unit", "a2a", "teammate mesh")
    )
    b2c_hits = any(
        w in low
        for w in ("мне нужен", "i need a free consult", "my small online shop", "хочу пилот", "b2c")
    )
    if contact_type in ("agency", "a2a"):
        a2a_hits = True
    if contact_type in ("person", "b2c"):
        b2c_hits = True
    if track in ("ops", "product", "promotion") and not a2a_hits:
        b2c_hits = True
    if a2a_hits and b2c_hits:
        return "dual"
    if a2a_hits:
        return "a2a"
    return "b2c"


class B2CChain:
    name = "B2C Chain"

    def start(
        self,
        *,
        business: str,
        industry_id: str,
        lang: str = "ru",
        resources: list[dict[str, Any]] | None = None,
        name: str = "",
        contact: str = "",
        track: str = "all",
        vvi: float = 0.4,
    ) -> dict[str, Any]:
        ra = ResourceAssemblyEngine().bind(
            resources,
            request_payload={
                "industry_id": industry_id,
                "business": business,
                "topology": "b2c",
            },
            voids={"vvi": vvi},
        )
        fw = FreeWorkFlow().start(
            business=business,
            industry_id=industry_id,
            track=track,
            name=name,
            contact=contact,
            lang=lang,
            resources=resources,
        )
        copy = CopyFirmware().offer_block(
            who=name or ("клиент" if lang.startswith("ru") else "the client"),
            void="несобранный слот консультации",
            gate="assembly≥0.45",
            price="free consult",
            not_included="Main $2490",
            voice="b2c",
            lang=lang,
        )
        rec = load_chain(ra["chain_id"]) or {}
        rec.update(
            {
                "topology": "b2c",
                "phase_index": 0,
                "phases": [dict(p) for p in B2C_PHASES],
                "work_id": fw.get("work_id"),
                "assembly_score": (fw.get("circle_summary") or {}).get("assembly_score")
                or ra.get("compatibility"),
                "copy": copy,
            }
        )
        save_chain(rec)
        return {
            "ok": True,
            "topology": "b2c",
            "chain_id": ra["chain_id"],
            "chain_seed": ra["chain_seed"],
            "public_sigil": ra["public_sigil"],
            "resource_assembly": ra,
            "phases": rec["phases"],
            "current_phase": rec["phases"][0],
            "free_work": {
                "work_id": fw.get("work_id"),
                "cta": fw.get("cta"),
                "self_clarifications": fw.get("self_clarifications"),
            },
            "copy": copy,
            "cta": fw.get("cta"),
        }

    def advance(self, chain_id: str, *, answers: dict[str, Any] | None = None) -> dict[str, Any]:
        rec = load_chain(chain_id)
        if not rec or rec.get("topology") not in ("b2c", "dual"):
            return {"ok": False, "error": "not_a_b2c_chain"}
        idx = int(rec.get("phase_index") or 0) + 1
        phases = rec.get("phases") or [dict(p) for p in B2C_PHASES]
        idx = min(idx, len(phases) - 1)
        rec["phase_index"] = idx
        rec["answers"] = {**(rec.get("answers") or {}), **(answers or {})}
        asm = float(rec.get("assembly_score") or 0)
        pred_end = float((rec.get("gates") or {}).get("predicted_end") or asm)
        risk = (rec.get("gates") or {}).get("risk") or ("high" if asm < 0.45 else "medium")
        main_open = pred_end >= 0.7 and risk != "high" and asm >= 0.45
        rec["main_open"] = main_open
        save_chain(rec)
        return {
            "ok": True,
            "chain_id": chain_id,
            "current_phase": phases[idx],
            "phase_index": idx,
            "main_open": main_open,
            "gate": "predicted_end≥0.7 and risk≠high",
        }


def build_a2a_chain(
    mu: dict[str, Any],
    *,
    chain_id: str | None = None,
    resource_assembly: dict[str, Any] | None = None,
) -> dict[str, Any]:
    coord = mu.get("coordination") or {}
    team = mu.get("teammate_network") or {}
    onto = mu.get("ontology") or {}
    loads = coord.get("node_loads") or {}
    if isinstance(loads, dict):
        nodes = list(loads.keys())
    elif isinstance(loads, list):
        nodes = [str(x) for x in loads]
    else:
        nodes = []
    nodes = nodes or [
        "system_reader",
        "problem_lattice",
        "metric_composer",
        "ontology",
        "teammate_network",
        "offer_surface",
    ]
    edges = coord.get("edges") or []
    handoffs = []
    matrix = coord.get("handoff_matrix") or {}
    for src, row in matrix.items():
        for dst, w in (row or {}).items():
            if float(w or 0) >= 0.35:
                handoffs.append(
                    {
                        "from": src,
                        "to": dst,
                        "weight": round(float(w), 4),
                        "artefact": f"handoff:{src}->{dst}",
                    }
                )
    return {
        "topology": "a2a",
        "chain_id": chain_id,
        "nodes": nodes,
        "edges": edges,
        "sync_score": coord.get("sync_score"),
        "deadlock_risk": coord.get("deadlock_risk"),
        "load_balance": coord.get("load_balance"),
        "artefact_handoffs": handoffs,
        "lead": team.get("lead_id"),
        "ontology_fit": onto.get("ontology_fit"),
        "resource_assembly": resource_assembly,
        "constructors": "a2a_handoff",  # not B2C consult slots
    }


def dual_bundle(b2c: dict[str, Any], a2a: dict[str, Any]) -> dict[str, Any]:
    parent = f"BD-{(b2c.get('chain_id') or 'x')[-8:]}-{(a2a.get('chain_id') or 'y')[-8:]}"
    return {
        "parent_bundle": parent,
        "mode": "dual_ricochet",
        "b2c_chain_id": b2c.get("chain_id"),
        "a2a_chain_id": a2a.get("chain_id"),
        "note": "Two constructors. Do not open B2C stepper on A2A slots.",
    }
