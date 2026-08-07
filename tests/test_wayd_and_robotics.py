"""wayD spine · originality · acceptance · robotics · implement model."""

from __future__ import annotations

from backend.core.wayd import stamp_labels, compute_terminal, compose_edges, unique_functions
from backend.core.business_gen.client_segmentation import segment_client
from backend.core.business_gen.expert_base_directions import match_expert_directions
from backend.core.business_gen.user_paths import select_user_path
from backend.core.business_gen.originality_inject import inject_three_directions
from backend.core.business_gen.acceptance_forecast import forecast_acceptance
from backend.core.business_gen.implement_model import build_implement_model, redact_paid_surface
from backend.core.business_gen.robotics_harness import RoboticsHarness
from backend.core.business_gen.gencore import run_gencore


BRIEF = (
    "Online architecture design library for IT product builders with niche cards, "
    "concept tests and unit packs for B2B studios."
)


def test_wayd_labels_and_terminal():
    labels = stamp_labels(
        direction_ids=["product_pack", "unit_pack", "ch_network"],
        segment_id="b2b_knowledge",
        path_id="library_ship",
    )
    assert "L.direction.product_pack" in labels["ids"]
    assert "L.rail.hide_paid_surface" in labels["ids"]
    mesh = compose_edges(
        ["gencore", "live_log", "robotics_harness", "implement_model", "wayd", "acceptance_forecast"],
        segment_fit=0.8,
        path_fit=0.8,
    )
    d = mesh.to_dict()
    assert d["edge_count"] >= 1
    assert unique_functions(d)
    term = compute_terminal(
        acceptance_p=0.7,
        originality=0.65,
        edge_count=d["edge_count"],
        edge_strength=d["edge_strength"],
        segment_fit=0.8,
        path_fit=0.8,
    )
    assert term.ship_gate in ("hold", "near_core", "ship")
    assert 0 <= term.acceptance_p <= 1


def test_segment_path_expert():
    seg = segment_client(BRIEF, industry_id="expert-services", lang="ru")
    assert seg["primary"]["id"] in (
        "b2b_knowledge",
        "b2b_product",
        "founder_solo",
        "agency",
        "platform",
        "b2b_ops",
    )
    path = select_user_path(BRIEF, segment_id=seg["primary"]["id"], lang="ru")
    assert path["path"]["id"]
    assert path["path"]["premium_artifacts"]
    exp = match_expert_directions(BRIEF, lang="ru")
    assert len(exp["top"]) >= 1


def test_originality_and_acceptance():
    o = inject_three_directions(
        {
            "product_pack": "Готовое решение и уникальный масштабируемый продукт для рынка.",
            "unit_pack": "Монетизация через KPI и ценностное предложение.",
            "ch_network": "Сетевой эффект и маркетинг на большую аудиторию.",
        },
        lang="ru",
        seed="test",
    )
    assert o["originality"] >= 0.4
    acc = forecast_acceptance(
        originality=o["originality"],
        segment_fit=0.7,
        path_fit=0.75,
        core_report={"markdown": "Single stop-rule · A01 cards", "counts": {"total_cards": 10}},
        live_log={"id": "log_x", "days": [{"done": True}] * 3},
        gencore={"slots": {"v1_consult": {"status": "ready"}, "v2_uniqueness_pager": {"status": "ready"}}},
        lang="ru",
    )
    assert acc["acceptance_p"] > 0.4
    assert acc["band"] in ("low", "medium", "high")


def test_implement_hidden_and_robotics():
    im = build_implement_model(lang="ru", expose_price=False)
    assert im["direction_count"] == 3
    assert im["ops_commercial"] is None
    assert im["price_redacted"] is True
    im2 = build_implement_model(lang="ru", expose_price=True)
    assert im2["ops_commercial"] and im2["ops_commercial"]["price_usd"] == 790

    payload = redact_paid_surface(
        {
            "hook_plan": {"price_usd": 790, "cta": "x"},
            "core_report": {"value_vs_core": {"tariff_price_usd": 790, "gap_usd": 10}},
            "implement_model": im2,
        }
    )
    assert "price_usd" not in (payload["hook_plan"] or {})
    assert payload["implement_model"]["ops_commercial"] is None

    plan = RoboticsHarness().build_plan(implement_model=im, lang="ru", approved=False)
    assert len(plan["queue"]) == 7
    session = RoboticsHarness().start(plan, lang="ru")
    sid = session["session_id"]
    r = RoboticsHarness().advance(sid, note="test")
    assert r["ok"] is True
    assert r["session"]["cursor"] == 1


def test_gencore_v6_slots():
    out = run_gencore(
        business_text=BRIEF,
        project_name="Lib",
        generation="v6",
        lang="ru",
        segment={"primary": {"id": "b2b_knowledge", "name": "Knowledge"}},
        user_path={"path": {"id": "library_ship", "name": "Lib path", "sophistication": 0.9, "result_sections": ["a"]}},
        originality={"originality": 0.7, "total_replacements": 3},
        acceptance={"acceptance_p": 0.72, "band": "high", "actions": []},
        wayd={"terminal": {"ship_gate": "ship", "density": 0.7, "signal": 0.7, "mesh_score": 0.6}},
        edge_mesh={"edge_count": 3, "unique_functions": [{"id": "E1", "function": "x", "function_ru": "y", "strength": 0.7}]},
        implement_model={"sku_id": "implement_three_directions", "spine_order": ["product_pack", "unit_pack", "ch_network"]},
    )
    assert out["version"].startswith("0.2")
    assert out["slots"]["v6_compound_edges"]["status"] == "ready"
    assert out["slots"]["v5_result_pack_template"]["status"] == "ready"
    assert "hide_paid_implement_surface" in out["hard_rails"]
