"""Engine E — On-prem / resilience stack (C3)."""

from __future__ import annotations

import hashlib
from typing import Any

from backend.contours import store

STAGES = (
    ("stage0", "Audit/NDA", 1, 7),
    ("stage1", "Air-gap + RAG", 8, 20),
    ("stage2", "Resilience + guardrails", 21, 40),
    ("stage3", "ERP/CRM + security tests", 41, 55),
    ("stage4", "Handover + SLA retainer", 56, 60),
)

PRICE_BANDS = {
    "pilot": {"min_rub": 800_000, "max_rub": 1_500_000, "label": "PoC"},
    "production": {"min_rub": 2_500_000, "max_rub": 4_500_000, "label": "MVP"},
    "hardened": {"min_rub": 5_500_000, "max_rub": 7_500_000, "label": "Hardened"},
}

PRIMARY_TIMEOUT_MS = 1500


def catalog() -> dict[str, Any]:
    return {
        "stages": [
            {"id": s[0], "name": s[1], "day_from": s[2], "day_to": s[3]} for s in STAGES
        ],
        "price_bands": PRICE_BANDS,
        "note": "bands are configurable constants, not a quote",
    }


def inference(prompt: str, *, vram_pressure: float = 0.2, fail_primary: bool = False) -> dict[str, Any]:
    """Primary heavy + secondary light. 1500ms switch is a contract, emulated here."""
    used = "secondary_light" if fail_primary or vram_pressure > 0.85 else "primary_heavy"
    text = (prompt or "")[:240]
    return {
        "used": used,
        "timeout_ms": PRIMARY_TIMEOUT_MS,
        "switched": used != "primary_heavy",
        "output": f"[{used}] {text}",
        "vram_pressure": vram_pressure,
        "circuit": "open" if vram_pressure > 0.95 else "closed",
    }


def rag_ingest(tenant_id: str, doc: str, doc_id: str | None = None) -> dict[str, Any]:
    did = doc_id or store.new_id("doc_")
    chunks = []
    raw = doc or ""
    for i in range(0, max(1, len(raw)), 280):
        piece = raw[i : i + 280]
        chunks.append(
            {
                "id": f"{did}_{i}",
                "text": piece,
                "embed": hashlib.sha256(piece.encode()).hexdigest()[:16],
            }
        )
    row = store.upsert(tenant_id, "rag_docs", {"id": did, "chunks": chunks, "n": len(chunks)})
    return row


def rag_query(tenant_id: str, query: str) -> dict[str, Any]:
    q = (query or "").lower()
    hits = []
    for doc in store.load_all(tenant_id, "rag_docs"):
        for ch in doc.get("chunks") or []:
            blob = str(ch.get("text") or "").lower()
            score = sum(1 for w in q.split() if w and w in blob)
            if score:
                hits.append({"doc_id": doc["id"], "chunk_id": ch["id"], "score": score, "text": ch.get("text")})
    hits.sort(key=lambda x: x["score"], reverse=True)
    citations = [h["chunk_id"] for h in hits[:3]]
    return {
        "query": query,
        "hits": hits[:5],
        "citations": citations,
        "citations_required": True,
        "answer": hits[0]["text"] if hits else "",
        "ok": bool(citations) or not q,
    }


def guardrail(output: str) -> dict[str, Any]:
    low = (output or "").lower()
    banned = ("гарантируем", "guarantee", "risk-free", "без риска")
    hits = [b for b in banned if b in low]
    return {"ok": not hits, "blocked": hits, "structured": True}


def pipeline_state(tenant_id: str, project_id: str, stage_id: str) -> dict[str, Any]:
    allowed = {s[0] for s in STAGES}
    if stage_id not in allowed:
        return {"ok": False, "error": "bad_stage", "allowed": sorted(allowed)}
    row = store.upsert(
        tenant_id,
        "onprem_projects",
        {"id": project_id, "stage": stage_id, "catalog": catalog()},
    )
    return {"ok": True, "project": row}
