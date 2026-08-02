"""Tests: knowledge synthesis, business gen, distribution, worker escrow."""

from __future__ import annotations

from backend.core.business_gen import BusinessGenerator, BUSINESS_SERVICES, service_demo
from backend.core.business_gen.services_catalog import list_services
from backend.core.knowledge_synthesis import run_knowledge_synthesis
from backend.core.workers import PayoutTrustLayer
from backend.monetization.distribution import DistributionEngine
from backend.monetization.promo import PromoAutomation


RESOURCE_BRIEF = (
    "Автономный бизнес: переработка вторичных ресурсов (пластик/металл) "
    "плюс логистика фракций до B2B buyer. Нужна система с метрикой маржи на тонну, "
    "согласованиями направлений на каждом этапе и панелью управления."
)

NICHES_LIVE = [
    (
        "ai-agencies",
        "AI-студия тонет в переделках: 30% часов rework, нет scoreboard handoff, клиенты ждут сроки.",
    ),
    (
        "freelace-d2c",
        "Фрилансер ищет заказы вручную, нет документа под match, хочет автоматизировать outreach и delivery.",
    ),
    (
        "content-monetize",
        "Автор с аудиторией 12к, монетизация размыта, нужен один платный шаг без инфоцыганства.",
    ),
    (
        "cost-ops",
        "Себестоимость плывёт: unit economics не сведены, leak map отсутствует, маржа падает.",
    ),
    (
        "expert-services",
        "Эксперт продаёт часы, хочет упаковать оффер и стратегию на 90 дней с границами.",
    ),
]


def test_knowledge_synthesis_resource():
    r = run_knowledge_synthesis(RESOURCE_BRIEF, industry_id="cost-ops", lang="ru")
    assert r["domain"] == "resource_logistics"
    assert r["self_test"]["score"] >= 0.6
    assert len(r["synthesis"]["original_moves"]) >= 3
    assert r["expert_base"]["id"]
    assert r["side_compute"]["flow_balance"]["bottleneck"]
    assert r["plan"]["steps"]


def test_business_generate_go():
    b = BusinessGenerator().generate(RESOURCE_BRIEF, industry_id="cost-ops", lang="ru")
    out = b["output"]
    assert out["autonomous_code_pack"]["components"]
    assert out["control_panel"]["columns"]
    assert out["expert_base"]["name"]
    assert out["final_gate"]["verdict"] in ("GO", "CONDITIONAL_GO")


def test_services_catalog_10():
    assert len(BUSINESS_SERVICES) == 10
    assert len(list_services("ru")) == 10
    d = service_demo("resource_loop", lang="ru")
    assert "demo" in d
    assert d["service"]["id"] == "resource_loop"


def test_live_niches_batch():
    """Arbitrary tests on live niches (как это по-русски)."""
    results = []
    for ind, brief in NICHES_LIVE:
        r = run_knowledge_synthesis(brief, industry_id=ind, lang="ru")
        results.append(
            {
                "industry": ind,
                "domain": r["domain"],
                "score": r["self_test"]["score"],
                "anti_template": r["synthesis"]["anti_template_score"],
                "prod_hint": r["self_test"]["prod_ready_hint"],
            }
        )
        assert r["self_test"]["score"] >= 0.4
        assert r["synthesis"]["anti_template_score"] >= 0.55
    # majority should be prod candidates
    goods = sum(1 for x in results if x["prod_hint"])
    assert goods >= 3


def test_distribution_3d():
    plan = DistributionEngine().build(
        industry_id="ai-agencies",
        industry_name="AI-агентства",
        idea_title="Scoreboard rework pilot",
        promo_fit=0.7,
        lang="ru",
    )
    d = plan.to_dict()
    assert d["brand"]["promise"]
    assert len(d["platforms"]) >= 3
    assert len(d["networks"]) >= 2
    assert len(d["week_plan"]) == 7


def test_promo_includes_distribution():
    p = PromoAutomation().build(
        "Pilot pack",
        "content-monetize",
        "Контент",
        0.6,
        domain="content_monetize",
    )
    assert p.distribution
    assert p.distribution.get("week_plan")


def test_worker_escrow_flow():
    layer = PayoutTrustLayer()
    created = layer.create_task(
        title="Demo task",
        niche="ai-agencies",
        worker_id="test_worker",
        purse_units=100,
    )
    tid = created["task"]["task_id"]
    mid = created["task"]["milestones"][0]["id"]
    pr = layer.submit_proof(tid, mid, {"items": [True, True]})
    assert pr.get("ok")
    rel = layer.release_milestone(tid, mid)
    assert rel.get("ok")
    assert rel["paid_units"] > 0
    dash = layer.worker_dashboard("test_worker")
    assert "reputation" in dash
