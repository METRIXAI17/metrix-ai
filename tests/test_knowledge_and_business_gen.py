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
    assert b.get("role") == "orchestrator"
    assert out["autonomous_code_pack"]["components"]
    assert out["control_panel"]["columns"]
    assert out["expert_base"]["name"]
    assert out["final_gate"]["verdict"] in ("GO", "CONDITIONAL_GO")
    orch = out["orchestration"]
    assert orch["mode"] == "multi_niche_orchestrator"
    assert orch["niches_total"] == 10
    assert len(orch["niche_ranking"]) == 10
    assert orch["service_stack"]
    assert orch["run_plan"]
    # Human Core report (no JSON-only surface)
    cr = out["core_report"]
    assert cr["markdown"] and "# " in cr["markdown"]
    assert cr["counts"]["architecture_cards"] >= 8
    assert b.get("core_markdown")
    assert "realized_mid_usd" in (b.get("value_vs_core") or cr["value_vs_core"])


def test_business_generate_library_core():
    brief = (
        "Онлайн бизнес с карточками архитектуры, предложениями и работой с нишами, "
        "принятия решений на пути создания и концептов тестирования. "
        "Библиотека с архитектурными дизайнами для билдеров ай-ти продуктов."
    )
    b = BusinessGenerator().generate(
        brief,
        industry_id="generic",
        lang="ru",
        project_name="Библиотека архитектурных дизайнов",
        channel="online",
        numbers={"cash_ceiling": 1500, "days": 21},
    )
    out = b["output"]
    cr = out["core_report"]
    assert cr["profile"]["is_library"] is True
    assert cr["profile"]["profile"] == "knowledge_library"
    assert cr["counts"]["total_cards"] >= 15
    assert "Ядро:" in cr["markdown"]
    assert "unit" in cr["markdown"].lower()

    # 1) Signer numbers → answers (constraint_cash, days) — not 2 open money Q
    ans = cr["inferred_answers"]
    assert "constraint_cash" in ans and "1500" in ans["constraint_cash"]
    assert "constraint_time" in ans and "21" in ans["constraint_time"]
    money_q = [
        q
        for q in (cr.get("open_questions") or out["plan"].get("open_questions") or [])
        if any(t in q.lower() for t in ("бюджет", "cash", "потол", "окно", "дней", "срок"))
    ]
    assert len(money_q) == 0, money_q

    # 2) Live 7-day channel log: 10–15 touches + 1 artifact
    clog = cr["channel_log_7d"]
    assert clog["touch_target"] >= 10
    assert clog["artifact"]["name"]
    assert "network" not in (clog["rule"] or "").lower() or "не" in (clog["rule"] or "").lower()
    assert len(clog["days"]) >= 6

    # 3) Calendar kill — T1–T3 with ISO dates
    tests = cr["concept_tests"]
    assert len(tests) >= 3
    for t in tests:
        assert t.get("start_date") and t.get("kill_date")
        assert "-" in t["kill_date"]  # ISO
    assert "kill `" in cr["markdown"] or "kill" in cr["markdown"].lower()

    # 4) Deep niche designs (not library meta only)
    titles = " ".join(c["title"] for c in cr["architecture_cards"])
    assert "Billing" in titles or "Agent" in titles or "API" in titles
    assert all(c.get("niche") for c in cr["architecture_cards"])

    # 5) File exports CSV + print HTML
    ex = cr["exports"]
    assert "architecture" in ex["cards_csv"] and "A01" in ex["cards_csv"]
    assert "<html" in ex["print_html"].lower()
    assert b.get("exports")

    # 6) Implementation assistant path (not CTA-only)
    assist = cr["implementation_assistant"]
    assert len(assist["steps"]) >= 5
    assert assist["trigger"] == "implementation_approval"

    # Hook plan for conversion
    hook = out["hook_plan"]
    assert hook["cta"] and hook["markdown"]
    assert b.get("hook_markdown")
    assert hook["price_usd"] == 790

    # Plan should lean product_pack / unit_pack for library
    steps = {s["id"]: s["default_option"] for s in (out["plan"]["steps"] or [])}
    assert steps.get("S1_direction") in ("product_pack", "full_stack", "ops_fix")
    assert steps.get("S2_unit") in ("unit_pack", "unit_order")
    val = cr["value_vs_core"]
    assert val["tariff_price_usd"] == 790
    assert val["realized_mid_usd"] >= 350
    assert val["realized_mid_usd"] <= 790
    assert val["gap_usd"] >= 0


def test_business_generate_library_en_parity():
    brief = (
        "Online business with architecture cards, offers, niche work, "
        "decision paths and concept testing. "
        "Library of architectural designs for IT product builders."
    )
    b = BusinessGenerator().generate(
        brief,
        industry_id="generic",
        lang="en",
        project_name="Architecture Design Library",
        channel="online",
        numbers={"cash_ceiling": 1200, "days": 21},
    )
    cr = b["output"]["core_report"]
    md = cr["markdown"]
    assert md.startswith("# Core:")
    assert "Deep architecture cards" in md or "architecture cards" in md.lower()
    assert "Implementation assistant" in md
    assert "Live 7-day channel log" in md
    assert "1200" in cr["inferred_answers"]["constraint_cash"]
    hook = b["output"]["hook_plan"]
    assert hook["lang"] == "en"
    assert "Approve" in hook["cta"] or "Core" in hook["cta"]


def test_services_catalog():
    """Public catalog is distribution-facing; non-distributive lanes stay off surface."""
    assert len(BUSINESS_SERVICES) == 8
    assert len(list_services("ru")) == 8
    ids = {s["id"] for s in BUSINESS_SERVICES}
    assert "worker_lane" not in ids
    assert "resource_loop" not in ids
    assert "distribution_engine" in ids
    d = service_demo("distribution_engine", lang="ru")
    assert "demo" in d
    assert d["service"]["id"] == "distribution_engine"


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
