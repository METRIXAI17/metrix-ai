"""Engine F — Cold chain / chip telemetry bridge (C5). Feature-flagged."""

from __future__ import annotations

import hashlib
from typing import Any

from backend.contours import flags, store


def _tid(t: str | None) -> str:
    return (t or "public").strip() or "public"


def _guard() -> dict[str, Any] | None:
    if flags.cold_chain_enabled():
        return None
    return {
        "ok": False,
        "flag": "ENABLE_COLD_CHAIN",
        "note": "flag off — structured empty state",
        "devices": [],
    }


def register_device(
    tenant_id: str,
    device_id: str,
    firmware_version: str = "cots-0.1",
) -> dict[str, Any]:
    g = _guard()
    if g:
        return g
    row = store.upsert(
        tenant_id,
        "devices",
        {
            "id": device_id,
            "firmware_version": firmware_version,
            "last_seen": store.now_iso(),
            "generation": "COTS",
            "path_note": "COTS (ESP32/STM32) → FPGA → MPW; telemetry is generation-agnostic",
        },
    )
    return {"ok": True, "device": row}


def ingest(
    tenant_id: str,
    device_id: str,
    *,
    temperature: float,
    shock: float,
    battery: float,
    ts: str | None = None,
) -> dict[str, Any]:
    g = _guard()
    if g:
        return g
    ev = store.upsert(
        tenant_id,
        "telemetry",
        {
            "id": store.new_id("tm_"),
            "device_id": device_id,
            "temperature": float(temperature),
            "shock": float(shock),
            "battery": float(battery),
            "ts": ts or store.now_iso(),
        },
    )
    dev = store.get(tenant_id, "devices", device_id) or {"id": device_id}
    dev["last_seen"] = ev["ts"]
    store.upsert(tenant_id, "devices", dev)
    alerts = []
    if temperature > 8 or temperature < -25:
        alerts.append({"rule": "temp_breach", "value": temperature})
    if shock > 12:
        alerts.append({"rule": "shock_breach", "value": shock})
    if battery < 15:
        alerts.append({"rule": "battery_low", "value": battery})
    for a in alerts:
        store.upsert(
            tenant_id,
            "alerts",
            {"id": store.new_id("al_"), "device_id": device_id, **a, "notify": "stub"},
        )
    return {"ok": True, "event": ev, "alerts": alerts}


def proof_of_condition(tenant_id: str, device_id: str) -> dict[str, Any]:
    g = _guard()
    if g:
        return g
    events = [e for e in store.load_all(tenant_id, "telemetry") if e.get("device_id") == device_id]
    events.sort(key=lambda e: e.get("ts") or "")
    chain = []
    prev = "0" * 64
    for e in events:
        payload = f"{prev}|{e.get('id')}|{e.get('ts')}|{e.get('temperature')}|{e.get('shock')}"
        digest = hashlib.sha256(payload.encode()).hexdigest()
        chain.append({"event_id": e.get("id"), "hash": digest, "prev": prev})
        prev = digest
    return {
        "ok": True,
        "device_id": device_id,
        "n": len(chain),
        "head": prev,
        "chain": chain,
        "zk_onchain": False,
        "note": "software hash chain; ZK/on-chain behind a later flag",
    }


def pilot_workflow(tenant_id: str, partner: str, n_devices: int = 50) -> dict[str, Any]:
    g = _guard()
    if g:
        return g
    n = min(100, max(50, int(n_devices)))
    return store.upsert(
        tenant_id,
        "cold_pilots",
        {
            "id": store.new_id("cp_"),
            "partner": partner,
            "devices_target": n,
            "status": "open",
        },
    )
