from __future__ import annotations

from backend.contours import CONTOUR_MAP, cold_chain, compute_broker, eval_protocol
from backend.contours import flags, flight_recorder, heavy_launch, onprem, outcome_filter
from backend.contours import process_os, spiritual
from backend.contours.metrix_logger import track_agent


def test_contour_map_has_five():
    assert set(CONTOUR_MAP) == {"C1", "C2", "C3", "C4", "C5"}


def test_eval_seed_reproducible(tmp_path, monkeypatch):
    monkeypatch.setenv("ENABLE_LLM_ASSIST", "0")
    a = eval_protocol.seed_dataset("t_eval")
    b = eval_protocol.seed_dataset("t_eval")
    assert a["cases"] == b["cases"] == 5
    r1 = eval_protocol.run(tenant_id="t_eval", dataset_id="ds_access_v1")
    r2 = eval_protocol.run(tenant_id="t_eval", dataset_id="ds_access_v1")
    assert r1["axes"]["error_rate"] == r2["axes"]["error_rate"]
    assert set(r1["axes"]) >= {"error_rate", "latency_ms", "cost_usd", "escalation_rate"}


def test_eval_orient_and_access():
    o = eval_protocol.orient("заявки горят, нет хозяина")
    assert o["outcome_class"] == "process_qualify"
    assert o["escalate"] is False
    ae = eval_protocol.access_eval("нужен eval на access", tenant_id="t_acc")
    assert ae["eval"]["recommended_offer_sku"]
    assert ae["disclaimer"].startswith("measured")


def test_eval_knob_warning():
    eval_protocol.seed_dataset("t_knob")
    base = eval_protocol.run(
        tenant_id="t_knob",
        dataset_id="ds_access_v1",
        param_snapshot={"engine": "orient-v1", "a": 1},
    )
    nxt = eval_protocol.run(
        tenant_id="t_knob",
        dataset_id="ds_access_v1",
        param_snapshot={"engine": "orient-v1", "a": 2, "b": 3},
        baseline_id=base["id"],
    )
    assert nxt["warning"]
    cmp_ = eval_protocol.compare("t_knob", nxt["id"], base["id"])
    assert "delta" in cmp_


def test_flight_recorder_and_kill():
    e = flight_recorder.log_event(
        tenant_id="t_fl",
        agent_id="a1",
        step_type="llm",
        cost_usd=30,
        latency_ms=12,
    )
    assert e["id"]
    ks = flight_recorder.kill_switch("t_fl", threshold_usd=25)
    assert ks["state"] == "STATE_HALTED"
    v = flight_recorder.validate_output({"outcome_class": "x"}, schema_keys=["outcome_class"])
    assert v["ok"] is True
    pack = flight_recorder.export_pack("t_fl", e["trace_id"])
    assert pack["sha256"]


def test_track_agent_decorator():
    hits = {"n": 0}

    @track_agent("unit", tenant_id="t_dec")
    def ping():
        hits["n"] += 1
        return 7

    assert ping() == 7
    assert hits["n"] == 1


def test_process_os_requires_outcome():
    tid = "t_pr_" + __import__("uuid").uuid4().hex[:8]
    bad = process_os.ingest_lead(tenant_id=tid, source="site", text="hi")
    assert bad["ok"] is False
    process_os.bind_outcome(
        tenant_id=tid,
        project_id="default",
        named_observable="monday leak %",
        baseline="unknown",
        target="<10%",
        measurement="weekly report",
        exclusions="ads",
        acceptance_test="named owner + number",
    )
    ok = process_os.ingest_lead(tenant_id=tid, source="site", text="заявка с сайта")
    assert ok["ok"] is True
    st = process_os.set_stage(tid, ok["lead"]["id"], "qualified")
    assert st["ok"] is True
    rep = process_os.monday_report(tid)
    assert "ownerless" in rep["markdown"].lower() or "ownerless" in str(rep["metrics"])


def test_compute_broker_flag_off(monkeypatch):
    monkeypatch.delenv("ENABLE_COMPUTE_BROKER", raising=False)
    assert flags.compute_broker_enabled() is False
    s = compute_broker.scan_spots("t_br")
    assert s["ok"] is False
    chat = compute_broker.chat_completions("t_br", [{"role": "user", "content": "hi"}])
    assert chat["status"] == 503


def test_compute_broker_flag_on(monkeypatch):
    monkeypatch.setenv("ENABLE_COMPUTE_BROKER", "1")
    s = compute_broker.scan_spots("t_br2")
    assert s["ok"] is True
    chat = compute_broker.chat_completions("t_br2", [{"role": "user", "content": "hi"}])
    assert chat["choices"][0]["message"]["content"]
    assert 0.4 <= chat["metrix_spread"]["margin"] <= 0.6


def test_onprem_and_rag():
    inf = onprem.inference("hello", fail_primary=True)
    assert inf["used"] == "secondary_light"
    onprem.rag_ingest("t_op", "air-gap RAG for a plant floor")
    q = onprem.rag_query("t_op", "air-gap")
    assert q["citations_required"] is True
    g = onprem.guardrail("we guarantee results")
    assert g["ok"] is False
    cat = onprem.catalog()
    assert cat["price_bands"]["pilot"]["min_rub"] == 800_000


def test_cold_chain_flag(monkeypatch):
    monkeypatch.delenv("ENABLE_COLD_CHAIN", raising=False)
    assert cold_chain.register_device("t_cc", "d1")["ok"] is False
    monkeypatch.setenv("ENABLE_COLD_CHAIN", "1")
    assert cold_chain.register_device("t_cc", "d1")["ok"] is True
    tm = cold_chain.ingest("t_cc", "d1", temperature=22, shock=1, battery=80)
    assert tm["alerts"]
    proof = cold_chain.proof_of_condition("t_cc", "d1")
    assert proof["head"]


def test_outcome_filter_does_not_claim_100():
    out = outcome_filter.run("эскалируйте человеку непонятно")
    assert out["escalate"] is True
    assert "never" in out["language"]


def test_heavy_launch_skus_and_cross():
    a = heavy_launch.assembly()
    assert len(a["projects"]) == 3
    assert {s["sku"] for s in a["skus"]} == {
        "access_month",
        "custom_spec_pilot",
        "cross_assist",
    }
    assert heavy_launch.SKUS["access_month"]["price_rub"] == 3290
    assert heavy_launch.SKUS["custom_spec_pilot"]["price_rub"] == 45000
    assert heavy_launch.SKUS["cross_assist"]["price_rub"] == 80000
    x = heavy_launch.cross_search("касса понедельник eval дверь")
    assert x["packed"]["n"] >= 1
    assert x["assistant"]["pick"]
    sp = spiritual.catalog()
    assert sp["n"] >= 6
    assert "natal" in sp["disclaimer"]


def test_api_contours_map():
    from fastapi.testclient import TestClient

    from backend.main import app

    c = TestClient(app)
    h = c.get("/api/v1/health")
    assert h.status_code == 200
    assert h.json().get("heavy_launch") is True
    m = c.get("/api/v1/contours/map")
    assert m.status_code == 200
    body = m.json()
    assert "C1" in body["contours"]
    x = c.post("/api/v1/contours/cross", json={"text": "касса eval дверь"})
    assert x.status_code == 200
    assert x.json()["packed"]["n"] >= 1
    seed = c.post("/api/v1/contours/eval/seed")
    assert seed.status_code == 200
    run = c.post(
        "/api/v1/contours/eval/runs",
        json={"dataset_id": "ds_access_v1", "param_snapshot": {"engine": "orient-v1"}},
    )
    assert run.status_code == 200
    assert "error_rate" in (run.json().get("axes") or {})
