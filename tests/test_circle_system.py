"""Circle-System / Deep Tech Metrix tests."""

from __future__ import annotations

from backend.core.circle_system import (
    DeepTechMetrixPipeline,
    circle_system_overview,
    lexicon_catalog,
    run_deep_tech_pipeline,
)
from backend.core.circle_system.certainty_analyzer import CertaintyAnalyzer
from backend.core.circle_system.pilot_predictor import PilotAccuracyPredictor
from backend.core.circle_system.support_system import SupportSystem


SAMPLE = (
    "Нужен deep tech пилот для AI-агентства: цель — сократить ops-хаос, "
    "клиенты B2B SaaS, оффер Terminal Teammate, бюджет 5000 USD, срок 21 день, "
    "метрика — конверсия free consult → pilot. Точно да: уже есть branding VA. "
    "Интеграция с CRM неясна, возможно webhook. Пилот scope: tech write + ops slice."
)


def test_lexicon_catalog():
    cat = lexicon_catalog()
    assert "read" in cat and "write" in cat
    assert "certain_yes" in cat["read"]
    assert "warmth_bands" in cat["write"]
    assert len(cat["super_program_families"]) == 6


def test_certainty_buckets():
    r = CertaintyAnalyzer().run(SAMPLE, industry_id="ai-agencies", lang="ru")
    assert r["counts"]["certain_yes"] + r["counts"]["certain_no"] + r["counts"]["uncertain"] >= 1
    assert r["parameters"]
    assert "uncertain_ids" in r


def test_deep_tech_pipeline_surfaces():
    out = run_deep_tech_pipeline(SAMPLE, industry_id="ai-agencies", lang="ru")
    assert out["system"] == "circle-system"
    surfaces = out["product_surfaces"]
    assert surfaces["auto_consult"]["ready"] is True
    assert surfaces["tech_write"]["ready"] is True
    assert surfaces["white_label_arch_prompts"]["no_external_llm"] is True
    assert out["assembly"]["heat_used"] is False
    assert out["super_speed"]["test_battery"]
    assert out["support"]["how_it_works"]
    assert out["arch_prompts"]["system_prompt"]
    assert all(a.get("holds") for a in out["assertions"] if a["id"] != "A3")


def test_pilot_predictor_logistic():
    pred = PilotAccuracyPredictor().run(
        assembly={"assembly_score": 0.7, "joint_score": 0.6, "composed_metrics": {"open_uncertainty": 0.2}},
        layers_result={"consistency_score": 0.75},
        resource_match={"compatibility_score": 0.6},
        pilot_horizon_days=14,
    )
    assert pred["predetermined_indicator_L"] == 0.92
    assert pred["predicted_end"] >= pred["y0"]
    assert pred["risk"] in ("low", "medium", "high")


def test_support_system_tickets():
    fw = {
        "anomalies": [{"metric": "SFI", "level": "critical", "msg": "high failure risk"}],
        "values": {"SFI": 0.7},
    }
    s = SupportSystem().run(fw)
    assert s["ticket_count"] == 1
    assert s["health"] == "red"
    assert "references" in s
    assert "ref_3" in s["references"] or "models" in s["references"]


def test_overview_modules():
    ov = circle_system_overview()
    assert ov["global_steps"] == 3
    assert "certainty_analyzer" in ov["modules"]
    assert "support_system" in ov["modules"]


def test_pipeline_class_version():
    p = DeepTechMetrixPipeline()
    assert p.version.startswith("2026")
