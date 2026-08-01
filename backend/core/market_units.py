"""
Market Units — application points, simple offers, package pricing.

Update 2026-07-26:
  · AI agencies → ops efficiency; promo = buyer fin models; product = Terminal Teammate
  · Cloud / creative founders → cut third-party API costs; Expert product; event promo
  · Cost engineering → 1 simple offer + 1 broad product offer
  · Chipmaking → 3 simple offers (ops / product / promotion)
  · Telecom → simple offers (ops / product / promotion)
  · Full package pricing: consultation + tech write
"""

from __future__ import annotations

from typing import Any

from backend.config import MONETIZATION


# ── Client-facing package ladder (showcase) ────────────────────────────────

PACKAGE_PRICING: dict[str, dict[str, Any]] = {
    "orientation_run": {
        "sku": "orientation_run",
        "name": "Orientation Run",
        "price_usd": 290,
        "includes": ["short brief analysis", "demo idea", "must-ask list"],
    },
    "metareality_consult": {
        "sku": "metareality_consult",
        "name": "MetaReality Consultation",
        "price_usd": 890,
        "includes": [
            "operational geometry consult",
            "constraint map",
            "SKU recommendation (Teammate / Expert / simple offer)",
        ],
        "ops_variable_usd": 1.0,
        "llm_path_ops_usd": 12.5,
    },
    "specsforge_tech_write": {
        "sku": "specsforge_tech_write",
        "name": "SpecsForge Tech Writing",
        "price_usd": 650,
        "includes": [
            "recursive specs after consult",
            "acceptance criteria",
            "VVI/ER/RRC improvement log",
        ],
        "gate": "metareality_consult complete",
        "ops_variable_usd": 2.0,
        "llm_path_ops_usd": 25.0,
    },
    "consult_techwrite_bundle": {
        "sku": "consult_techwrite_bundle",
        "name": "Full Consult + Tech Write Package",
        "price_usd": 1290,
        "includes": [
            "MetaReality consultation",
            "SpecsForge tech writing",
            "Memo Convert technical tasks",
            "handoff to Terminal Teammate / Expert",
        ],
        "components": ["metareality_consult", "specsforge_tech_write"],
        "separate_sum_usd": 890 + 650,  # 1540
        "bundle_discount_usd": 250,
        "ops_variable_usd": 3.0,
        "llm_path_ops_usd": 37.5,
        "structural_savings_x": 12.5,
    },
    "paid_pilot": {
        "sku": "paid_pilot",
        "name": "Paid Pilot 14–30d",
        "price_usd": 1490,
    },
    "full_orientation_package": {
        "sku": "full_orientation_package",
        "name": MONETIZATION["full_package"]["name"],
        "price_usd": MONETIZATION["full_package"]["base_price_usd"],
        "includes": [
            "orient → bridge → product → teammate → angle",
            "implement path quote",
        ],
    },
    "terminal_teammate_predev": {
        "sku": "terminal_teammate_predev",
        "name": "Terminal Teammate · Pre-dev day",
        "price_usd": 990,
        "ops_variable_usd": 4.0,
    },
    "expert_api_collapse": {
        "sku": "expert_api_collapse",
        "name": "Expert · API cost collapse (quality up)",
        "price_usd": 1190,
        "ops_variable_usd": 2.5,
    },
}


# ── Industry application points ────────────────────────────────────────────

MARKET_UNITS: dict[str, dict[str, Any]] = {
    "ai-agencies": {
        "application_point": "operational_efficiency",
        "application_ru": "Операционная эффективность",
        "product": {
            "sku": "terminal_teammate",
            "name": "Terminal Teammate",
            "one_liner": "Teammate console that raises ops efficiency without agent chaos.",
        },
        "promotion": {
            "angle": "buyer_financial_models",
            "angle_ru": "Рисовать покупающему бизнесу эффективные финансовые модели",
            "one_liner": "Show the buying business a clean fin model why Terminal Teammate pays.",
        },
        "offers": [
            {
                "track": "ops",
                "title": "Ops efficiency map → Teammate attach",
                "price_usd": 890,
                "simple": True,
            },
            {
                "track": "product",
                "title": "Terminal Teammate pre-dev kit",
                "price_usd": 990,
                "simple": True,
            },
            {
                "track": "promotion",
                "title": "Buyer fin-model pack for Teammate sale",
                "price_usd": 490,
                "simple": True,
            },
        ],
    },
    "cloud-economy": {
        "application_point": "third_party_api_cost_cut",
        "application_ru": (
            "Фаундеры продуктивного творчества и кастомных операций — "
            "сократить расходы на сторонние API"
        ),
        "redirect_from": "generic_cloud_finops",
        "product": {
            "sku": "expert",
            "name": "Expert",
            "one_liner": "Cut third-party API spend while strengthening quality (expert env vs pure LLM).",
        },
        "promotion": {
            "angle": "event_review_container",
            "angle_ru": "Эвент с пересмотром того, что уже делается — контейнер + отсылка на продажу",
            "one_liner": "Event that reviews what already ships → container + sales pointer to Expert.",
        },
        "preserved_valuable": [
            "unit economics language",
            "12.5× structural savings vs pure LLM multi-agent",
            "CloudForge precision under product context",
            "edge vs core placement as cost lever",
        ],
        "offers": [
            {
                "track": "ops",
                "title": "API burn audit → Expert path",
                "price_usd": 890,
                "simple": True,
            },
            {
                "track": "product",
                "title": "Expert env install (quality↑ cost↓)",
                "price_usd": 1190,
                "simple": True,
            },
            {
                "track": "promotion",
                "title": "Review event container + sales pointer",
                "price_usd": 490,
                "simple": True,
            },
        ],
    },
    "cost-engineering": {
        "application_point": "ops_for_cost_engineers",
        "application_ru": "Операционка для кост-инженеров",
        "product": {
            "sku": "parameter_void_scanner",
            "name": "Parameter Void Scanner",
            "one_liner": "Cut waste parameters without cutting capability.",
        },
        "promotion": {
            "angle": "waste_killer_cards",
            "one_liner": "Waste-killer case cards for ops buyers who hate fat specs.",
        },
        "offers": [
            {
                "track": "ops",
                "title": "Simple offer: 1-page parameter waste map",
                "price_usd": 290,
                "simple": True,
                "audience": "cost engineers + anyone who hires them",
            },
            {
                "track": "product",
                "title": "Simple product: resellable Void Scanner SKU pack",
                "price_usd": 990,
                "simple": True,
                "audience": "broad audience that comes to cost engineers",
            },
        ],
    },
    "chipmaking": {
        "application_point": "design_loop_clarity",
        "application_ru": "Ясность design-loop / yield без hype",
        "product": {
            "sku": "yield_geometry_twin",
            "name": "Yield Geometry Twin",
            "one_liner": "Conceptual twin before tapeout decisions.",
        },
        "promotion": {
            "angle": "semiconductor_clarity",
            "one_liner": "Clarity posts and reverse outreach — no buzzword fog.",
        },
        "offers": [
            {
                "track": "ops",
                "title": "Design-loop void pack (ops)",
                "price_usd": 890,
                "simple": True,
            },
            {
                "track": "product",
                "title": "Yield geometry twin session (product)",
                "price_usd": 1290,
                "simple": True,
            },
            {
                "track": "promotion",
                "title": "Semiconductor clarity event + sales pointer",
                "price_usd": 490,
                "simple": True,
            },
        ],
    },
    "telecom": {
        "application_point": "sla_arpu_signal",
        "application_ru": "SLA / ARPU / intent-signal без spreadsheet fog",
        "product": {
            "sku": "sla_native_sku_builder",
            "name": "SLA-native SKU Builder",
            "one_liner": "Product SKUs that speak carrier SLA and QoS.",
        },
        "promotion": {
            "angle": "carrier_grade_messaging",
            "one_liner": "Carrier-grade messages: SLA, ARPU, MOS first.",
        },
        "offers": [
            {
                "track": "ops",
                "title": "Churn/ARPU lever board (ops)",
                "price_usd": 890,
                "simple": True,
            },
            {
                "track": "product",
                "title": "SLA-native SKU pack for SME/MVNO (product)",
                "price_usd": 1190,
                "simple": True,
            },
            {
                "track": "promotion",
                "title": "Intent-signal care weave + partner hunt (promo)",
                "price_usd": 490,
                "simple": True,
            },
        ],
    },
    "device-assembly": {
        "application_point": "station_scale",
        "application_ru": "Station setup that scales",
        "product": {
            "sku": "config_workflow",
            "name": "Config product workflow",
            "one_liner": "Assembly → setup → guided config as a product.",
        },
        "promotion": {
            "angle": "one_station_demo",
            "one_liner": "Free demo: one station optimized end-to-end.",
        },
        "offers": [
            {
                "track": "ops",
                "title": "Station rework timer pack",
                "price_usd": 490,
                "simple": True,
            },
            {
                "track": "product",
                "title": "Config SKU matrix product",
                "price_usd": 990,
                "simple": True,
            },
            {
                "track": "promotion",
                "title": "Maker/integrator before-after posts",
                "price_usd": 290,
                "simple": True,
            },
        ],
    },
    "asset-decisions": {
        "application_point": "decision_support_liquidity",
        "application_ru": "Поддержка решений по активам · автоликвидность",
        "badge": "Автоликвидность",
        "liquidity_surface": "decision_making",
        "product": {
            "sku": "decision_support_desk",
            "name": "Decision Support Desk",
            "one_liner": (
                "Key metric · risk model · situation packs — cognition, monitoring, "
                "strategy generation. Deal management stays with the client."
            ),
        },
        "promotion": {
            "angle": "private_room_proof",
            "angle_ru": "Приватка после теста модели, без гарантий доходности",
            "one_liner": "Private room after model test — work by TZ, no yield guarantees.",
        },
        "offers": [
            {
                "track": "ops",
                "title": "Key-metric + risk map (ops)",
                "price_usd": 690,
                "simple": True,
            },
            {
                "track": "product",
                "title": "Situation strategy pack (product)",
                "price_usd": 990,
                "simple": True,
            },
            {
                "track": "promotion",
                "title": "Private-room narrative + disclaimers",
                "price_usd": 490,
                "simple": True,
            },
        ],
        "disclaimers": [
            "Not investment advice",
            "Not auto-trading custody",
            "No profit guarantees",
        ],
    },
    "d2c-offramp": {
        "application_point": "d2c_document_liquidity",
        "application_ru": "D2C: идея → документ → биржа → агент · автоликвидность",
        "badge": "Автоликвидность",
        "liquidity_surface": "d2c",
        "product": {
            "sku": "workspace_offramp",
            "name": "Workspace Offramp",
            "one_liner": (
                "Incomplete idea → freelace-ready document → optional order match → "
                "terminal agent on accepted scope."
            ),
        },
        "promotion": {
            "angle": "document_not_vinaigrette",
            "angle_ru": "Ценность = документ на бирже, не 30-минутный винегрет",
            "one_liner": "Sell the creative multi-variant layer; agent executes the fixed doc.",
        },
        "offers": [
            {
                "track": "ops",
                "title": "Idea → brief → freelace match (ops)",
                "price_usd": 490,
                "simple": True,
            },
            {
                "track": "product",
                "title": "Workspace + agent handoff kit",
                "price_usd": 890,
                "simple": True,
            },
            {
                "track": "promotion",
                "title": "Proof: document sold / accepted once",
                "price_usd": 390,
                "simple": True,
            },
        ],
    },
}


def package_cost_report() -> dict[str, Any]:
    """Current cost of 1 full consult + tech-write package."""
    bundle = PACKAGE_PRICING["consult_techwrite_bundle"]
    consult = PACKAGE_PRICING["metareality_consult"]
    tech = PACKAGE_PRICING["specsforge_tech_write"]
    full = PACKAGE_PRICING["full_orientation_package"]
    return {
        "as_of": "2026-07-26",
        "primary_package": {
            "name": bundle["name"],
            "client_price_usd": bundle["price_usd"],
            "if_bought_separate_usd": bundle["separate_sum_usd"],
            "bundle_discount_usd": bundle["bundle_discount_usd"],
            "components": [
                {
                    "name": consult["name"],
                    "price_usd": consult["price_usd"],
                    "ops_variable_usd": consult["ops_variable_usd"],
                },
                {
                    "name": tech["name"],
                    "price_usd": tech["price_usd"],
                    "ops_variable_usd": tech["ops_variable_usd"],
                    "gate": tech["gate"],
                },
            ],
            "ops_variable_total_usd": bundle["ops_variable_usd"],
            "llm_path_ops_usd": bundle["llm_path_ops_usd"],
            "structural_savings_x": bundle["structural_savings_x"],
            "margin_note": (
                "Client $1290; variable intelligence ops ~$3 Metrix vs ~$37.5 pure LLM path. "
                "Human delivery time is the real capacity limit, not token bill."
            ),
        },
        "related_ladder": {
            "orientation_usd": PACKAGE_PRICING["orientation_run"]["price_usd"],
            "consult_techwrite_usd": bundle["price_usd"],
            "pilot_usd": PACKAGE_PRICING["paid_pilot"]["price_usd"],
            "full_orientation_usd": full["price_usd"],
        },
        "note": (
            "«Полный пакет (консультация + тех райт)» = consult_techwrite_bundle $1290. "
            "Full Orientation Package $2490 = tour product+teammate+angle+implement path — шире."
        ),
    }


def market_unit_for(industry_id: str) -> dict[str, Any]:
    unit = MARKET_UNITS.get(industry_id) or MARKET_UNITS["ai-agencies"]
    return {
        "industry_id": industry_id,
        **unit,
        "package_pricing_ref": "consult_techwrite_bundle",
    }


def simple_offers(industry_id: str) -> list[dict[str, Any]]:
    unit = MARKET_UNITS.get(industry_id) or {}
    return list(unit.get("offers") or [])


def all_market_units_payload() -> dict[str, Any]:
    return {
        "module": "Market Units",
        "version": "2026-07-26",
        "package_pricing": PACKAGE_PRICING,
        "package_cost_report": package_cost_report(),
        "units": {k: market_unit_for(k) for k in MARKET_UNITS},
    }

