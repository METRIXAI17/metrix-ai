"""Engine D — Compute broker & spot arbitrage (C4). Feature-flagged."""

from __future__ import annotations

from typing import Any, Iterator

from backend.contours import flags, store

MARGIN = 0.5  # 50% inside 40–60%
PROVIDERS = ("mock", "vast.ai", "runpod")


def _tid(t: str | None) -> str:
    return (t or "public").strip() or "public"


def _mock_nodes() -> list[dict[str, Any]]:
    return [
        {"id": "mock-a", "provider": "mock", "spot_usd": 0.42, "healthy": True, "gpu": "4090"},
        {"id": "mock-b", "provider": "mock", "spot_usd": 0.51, "healthy": True, "gpu": "A6000"},
        {"id": "mock-c", "provider": "mock", "spot_usd": 0.38, "healthy": False, "gpu": "3090"},
    ]


def scan_spots(tenant_id: str = "public") -> dict[str, Any]:
    if not flags.compute_broker_enabled():
        return {
            "ok": False,
            "flag": "ENABLE_COMPUTE_BROKER",
            "nodes": [],
            "note": "flag off — structured empty state",
        }
    nodes = _mock_nodes()
    healthy = [n for n in nodes if n["healthy"]]
    store.upsert(tenant_id, "spot_cache", {"id": "latest", "nodes": nodes, "scanned": store.now_iso()})
    return {"ok": True, "nodes": nodes, "healthy": len(healthy)}


def pick_node() -> dict[str, Any] | None:
    healthy = [n for n in _mock_nodes() if n["healthy"]]
    if not healthy:
        return None
    return min(healthy, key=lambda n: n["spot_usd"])


def quote(spot_usd: float) -> dict[str, Any]:
    client = round(spot_usd * (1 + MARGIN), 4)
    return {
        "spot_cost": spot_usd,
        "client_rate": client,
        "delta": round(client - spot_usd, 4),
        "margin": MARGIN,
    }


def ledger_write(tenant_id: str, q: dict[str, Any], node_id: str) -> dict[str, Any]:
    return store.upsert(
        tenant_id,
        "spread_ledger",
        {
            "id": store.new_id("sp_"),
            "node_id": node_id,
            "client_rate": q["client_rate"],
            "spot_cost": q["spot_cost"],
            "delta": q["delta"],
            "timestamp": store.now_iso(),
        },
    )


def chat_completions(
    tenant_id: str,
    messages: list[dict[str, Any]],
    *,
    stream: bool = False,
) -> dict[str, Any] | Iterator[str]:
    if not flags.compute_broker_enabled():
        return {
            "error": {
                "message": "compute broker disabled",
                "type": "flag_off",
                "code": "ENABLE_COMPUTE_BROKER",
            },
            "status": 503,
        }
    node = pick_node()
    if not node:
        return {
            "error": {"message": "no healthy node", "type": "provider_down", "code": "503"},
            "status": 503,
        }
    q = quote(float(node["spot_usd"]))
    ledger_write(tenant_id, q, node["id"])
    last = ""
    for m in messages or []:
        if m.get("role") == "user":
            last = str(m.get("content") or "")
    text = f"[broker {node['id']}] {last[:400] or 'ok'}"
    if stream:

        def gen() -> Iterator[str]:
            import json as _json

            for ch in text:
                payload = {"choices": [{"delta": {"content": ch}}]}
                yield "data: " + _json.dumps(payload) + "\n\n"
            yield "data: [DONE]\n\n"

        return gen()
    return {
        "id": store.new_id("chat_"),
        "object": "chat.completion",
        "model": f"metrix-broker/{node['id']}",
        "choices": [{"message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 8, "completion_tokens": max(1, len(text) // 4)},
        "metrix_spread": q,
        "node": node["id"],
    }
