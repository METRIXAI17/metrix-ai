"""Contour APIs — Eval, Flight, Process, Broker, On-prem, Cold chain, Cross."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.contours import CONTOUR_MAP, NAV_DEFAULT, flags
from backend.contours import cold_chain, compute_broker, eval_protocol, flight_recorder
from backend.contours import heavy_launch, onprem, outcome_filter, partners, process_os
from backend.contours import spiritual, store
from backend.security.hardening import sanitize_text

router = APIRouter(prefix="/contours", tags=["contours"])


def _tenant(x_metrix_tenant: str | None) -> str:
    t = (x_metrix_tenant or "public").strip()[:64]
    return t or "public"


class TextBody(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)


class EvalRunBody(BaseModel):
    dataset_id: str = "ds_access_v1"
    engine_version: str = "orient-v1"
    param_snapshot: dict[str, Any] = Field(default_factory=dict)
    baseline_id: str | None = None


class FlightBody(BaseModel):
    agent_id: str
    trace_id: str | None = None
    step_type: str = "tool"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0
    cost_usd: float = 0
    payload_json: dict[str, Any] = Field(default_factory=dict)


class OutcomeBody(BaseModel):
    project_id: str
    named_observable: str
    baseline: str
    target: str
    measurement: str
    exclusions: str = ""
    acceptance_test: str


class LeadBody(BaseModel):
    source: str = "webhook"
    text: str
    owner: str | None = None
    sla_minutes: int = 30
    project_id: str = "default"


class StageBody(BaseModel):
    stage: str


class PartnerBody(BaseModel):
    name: str
    type: str
    contact: str = ""


class DeviceBody(BaseModel):
    device_id: str
    firmware_version: str = "cots-0.1"


class TelemetryBody(BaseModel):
    device_id: str
    temperature: float
    shock: float = 0
    battery: float = 100
    ts: str | None = None


class ChatBody(BaseModel):
    messages: list[dict[str, Any]]
    stream: bool = False


class PipelineBody(BaseModel):
    project_id: str
    stage: str


@router.get("/map")
def contour_map() -> dict[str, Any]:
    return {
        "contours": CONTOUR_MAP,
        "nav_default": NAV_DEFAULT,
        "flags": flags.snapshot(),
        "heavy_launch": heavy_launch.assembly(),
    }


@router.get("/skus")
def skus() -> dict[str, Any]:
    return {"skus": list(heavy_launch.SKUS.values())}


@router.post("/cross")
def cross(body: TextBody) -> dict[str, Any]:
    return heavy_launch.cross_search(sanitize_text(body.text))


@router.get("/spiritual")
def spiritual_lib(q: str = "") -> dict[str, Any]:
    if q:
        return spiritual.search(q)
    return spiritual.catalog()


# ── Eval ──────────────────────────────────────────────────────────────────────
@router.post("/eval/seed")
def eval_seed(x_metrix_tenant: str | None = Header(default=None)) -> dict[str, Any]:
    return eval_protocol.seed_dataset(_tenant(x_metrix_tenant))


@router.post("/eval/orient")
def eval_orient(body: TextBody) -> dict[str, Any]:
    return eval_protocol.orient(sanitize_text(body.text))


@router.post("/eval/access")
def eval_access(
    body: TextBody,
    x_metrix_tenant: str | None = Header(default=None),
) -> dict[str, Any]:
    return eval_protocol.access_eval(sanitize_text(body.text), tenant_id=_tenant(x_metrix_tenant))


@router.post("/eval/runs")
def eval_runs(
    body: EvalRunBody,
    x_metrix_tenant: str | None = Header(default=None),
) -> dict[str, Any]:
    extra = [k for k in (body.param_snapshot or {}) if k != "engine"]
    if body.baseline_id and len(body.param_snapshot or {}) > 1:
        # validation warning is also inside runner
        pass
    if len(extra) > 1:
        store.audit(_tenant(x_metrix_tenant), "eval.knob_warning", {"knobs": extra})
    return eval_protocol.run(
        tenant_id=_tenant(x_metrix_tenant),
        dataset_id=body.dataset_id,
        engine_version=body.engine_version,
        param_snapshot=body.param_snapshot,
        baseline_id=body.baseline_id,
    )


@router.get("/eval/runs/{run_id}/compare")
def eval_compare(
    run_id: str,
    baseline_id: str,
    x_metrix_tenant: str | None = Header(default=None),
) -> dict[str, Any]:
    return eval_protocol.compare(_tenant(x_metrix_tenant), run_id, baseline_id)


# ── Flight ────────────────────────────────────────────────────────────────────
@router.post("/telemetry/log")
def telemetry_log(
    body: FlightBody,
    x_metrix_tenant: str | None = Header(default=None),
) -> dict[str, Any]:
    return flight_recorder.log_event(
        tenant_id=_tenant(x_metrix_tenant),
        agent_id=body.agent_id,
        trace_id=body.trace_id,
        step_type=body.step_type,
        prompt_tokens=body.prompt_tokens,
        completion_tokens=body.completion_tokens,
        latency_ms=body.latency_ms,
        cost_usd=body.cost_usd,
        payload_json=body.payload_json,
    )


@router.post("/telemetry/kill-switch")
def kill_switch(
    threshold_usd: float = 25.0,
    x_metrix_tenant: str | None = Header(default=None),
) -> dict[str, Any]:
    return flight_recorder.kill_switch(_tenant(x_metrix_tenant), threshold_usd=threshold_usd)


@router.post("/telemetry/validate")
def validate_out(body: dict[str, Any]) -> dict[str, Any]:
    return flight_recorder.validate_output(
        body.get("output") if isinstance(body.get("output"), dict) else body,
        schema_keys=body.get("schema_keys"),
        rag_ids=body.get("rag_ids"),
    )


@router.get("/telemetry/export")
def export_pack(
    trace_id: str | None = None,
    x_metrix_tenant: str | None = Header(default=None),
) -> dict[str, Any]:
    return flight_recorder.export_pack(_tenant(x_metrix_tenant), trace_id)


# ── Process OS ────────────────────────────────────────────────────────────────
@router.post("/process/outcome")
def process_outcome(
    body: OutcomeBody,
    x_metrix_tenant: str | None = Header(default=None),
) -> dict[str, Any]:
    return process_os.bind_outcome(
        tenant_id=_tenant(x_metrix_tenant),
        project_id=body.project_id,
        named_observable=body.named_observable,
        baseline=body.baseline,
        target=body.target,
        measurement=body.measurement,
        exclusions=body.exclusions,
        acceptance_test=body.acceptance_test,
    )


@router.post("/process/leads")
def process_leads(
    body: LeadBody,
    x_metrix_tenant: str | None = Header(default=None),
) -> dict[str, Any]:
    return process_os.ingest_lead(
        tenant_id=_tenant(x_metrix_tenant),
        source=body.source,
        text=sanitize_text(body.text),
        owner=body.owner,
        sla_minutes=body.sla_minutes,
        project_id=body.project_id,
    )


@router.post("/process/webhook")
def process_webhook(
    body: dict[str, Any],
    x_metrix_tenant: str | None = Header(default=None),
) -> dict[str, Any]:
    text = sanitize_text(str(body.get("text") or body.get("message") or body.get("brief") or ""))
    if not text:
        raise HTTPException(400, "text required")
    return process_os.ingest_lead(
        tenant_id=_tenant(x_metrix_tenant),
        source=str(body.get("source") or "webhook"),
        text=text,
        owner=body.get("owner"),
        project_id=str(body.get("project_id") or "default"),
    )


@router.post("/process/leads/{lead_id}/stage")
def process_stage(
    lead_id: str,
    body: StageBody,
    x_metrix_tenant: str | None = Header(default=None),
) -> dict[str, Any]:
    return process_os.set_stage(_tenant(x_metrix_tenant), lead_id, body.stage)


@router.get("/process/monday")
def process_monday(
    project_id: str = "default",
    x_metrix_tenant: str | None = Header(default=None),
) -> dict[str, Any]:
    return process_os.monday_report(_tenant(x_metrix_tenant), project_id)


# ── Outcome filter ────────────────────────────────────────────────────────────
@router.post("/filter")
def filter_outcome(body: TextBody) -> dict[str, Any]:
    return outcome_filter.run(sanitize_text(body.text))


# ── Compute broker ────────────────────────────────────────────────────────────
@router.get("/broker/spots")
def broker_spots(x_metrix_tenant: str | None = Header(default=None)) -> dict[str, Any]:
    return compute_broker.scan_spots(_tenant(x_metrix_tenant))


@router.post("/v1/chat/completions")
def broker_chat(
    body: ChatBody,
    x_metrix_tenant: str | None = Header(default=None),
):
    out = compute_broker.chat_completions(
        _tenant(x_metrix_tenant),
        body.messages,
        stream=body.stream,
    )
    if isinstance(out, dict) and out.get("status") == 503:
        raise HTTPException(503, out.get("error") or "broker unavailable")
    if body.stream:
        return StreamingResponse(out, media_type="text/event-stream")
    return out


# ── On-prem ───────────────────────────────────────────────────────────────────
@router.get("/onprem/catalog")
def onprem_catalog() -> dict[str, Any]:
    return onprem.catalog()


@router.post("/onprem/infer")
def onprem_infer(body: dict[str, Any]) -> dict[str, Any]:
    return onprem.inference(
        sanitize_text(str(body.get("prompt") or "")),
        vram_pressure=float(body.get("vram_pressure") or 0.2),
        fail_primary=bool(body.get("fail_primary")),
    )


@router.post("/onprem/rag/ingest")
def onprem_ingest(
    body: dict[str, Any],
    x_metrix_tenant: str | None = Header(default=None),
) -> dict[str, Any]:
    return onprem.rag_ingest(_tenant(x_metrix_tenant), str(body.get("doc") or ""))


@router.post("/onprem/rag/query")
def onprem_query(
    body: TextBody,
    x_metrix_tenant: str | None = Header(default=None),
) -> dict[str, Any]:
    return onprem.rag_query(_tenant(x_metrix_tenant), sanitize_text(body.text))


@router.post("/onprem/pipeline")
def onprem_pipeline(
    body: PipelineBody,
    x_metrix_tenant: str | None = Header(default=None),
) -> dict[str, Any]:
    return onprem.pipeline_state(_tenant(x_metrix_tenant), body.project_id, body.stage)


# ── Cold chain ────────────────────────────────────────────────────────────────
@router.post("/devices")
def devices_reg(
    body: DeviceBody,
    x_metrix_tenant: str | None = Header(default=None),
) -> dict[str, Any]:
    return cold_chain.register_device(
        _tenant(x_metrix_tenant), body.device_id, body.firmware_version
    )


@router.post("/devices/telemetry")
def devices_tm(
    body: TelemetryBody,
    x_metrix_tenant: str | None = Header(default=None),
) -> dict[str, Any]:
    return cold_chain.ingest(
        _tenant(x_metrix_tenant),
        body.device_id,
        temperature=body.temperature,
        shock=body.shock,
        battery=body.battery,
        ts=body.ts,
    )


@router.get("/devices/{device_id}/proof")
def devices_proof(
    device_id: str,
    x_metrix_tenant: str | None = Header(default=None),
) -> dict[str, Any]:
    return cold_chain.proof_of_condition(_tenant(x_metrix_tenant), device_id)


# ── Partners ──────────────────────────────────────────────────────────────────
@router.post("/partners")
def partners_add(
    body: PartnerBody,
    x_metrix_tenant: str | None = Header(default=None),
) -> dict[str, Any]:
    return partners.upsert_partner(
        _tenant(x_metrix_tenant), name=body.name, ptype=body.type, contact=body.contact
    )


@router.get("/partners/templates")
def partners_tpl() -> dict[str, Any]:
    return {"templates": partners.templates()}


@router.get("/client-view")
def client_view(x_metrix_tenant: str | None = Header(default=None)) -> dict[str, Any]:
    tid = _tenant(x_metrix_tenant)
    report = process_os.monday_report(tid)
    demo = report.get("metrics", {}).get("leads", 0) == 0
    return {
        "outcome": "named Monday leak number",
        "sla": report.get("metrics"),
        "saved_capital": None if demo else report.get("metrics"),
        "compliance_pdf": "/api/v1/contours/telemetry/export",
        "demo_data": demo,
        "banner": "DEMO DATA" if demo else None,
        "skus": list(heavy_launch.SKUS.values()),
    }


@router.get("/operator-view")
def operator_view(x_metrix_tenant: str | None = Header(default=None)) -> dict[str, Any]:
    tid = _tenant(x_metrix_tenant)
    return {
        "nodes": compute_broker.scan_spots(tid),
        "spread": store.load_all(tid, "spread_ledger")[-12:],
        "flight": store.load_all(tid, "flight_logs")[-20:],
        "kill": store.get(tid, "kill_switch", "ks_current"),
        "flags": flags.snapshot(),
    }
