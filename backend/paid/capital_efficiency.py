"""
Capital Efficiency Engine — concrete $ comparisons for the pitch.

Models (honest, documented assumptions):
  A) Pure Cloud LLM API (pay-per-token, multi-agent style)
  B) Hybrid: small local/deterministic core + selective LLM
  C) Metrix architecture: proprietary pipeline (OAE embedding, paid core)
     with minimal LLM calls (copy polish / optional vision only)

Numbers are order-of-magnitude realistic for 2025–2026 API list prices,
not audited finance. Used for investor/operator orientation.
"""

from __future__ import annotations

from typing import Any

from backend.paid.types import clamp01, safe_float


# ── Unit costs (USD) — documented assumptions ────────────────────────────────
ASSUMPTIONS = {
    "as_of": "2026-07",
    "llm_input_per_1m_tokens_usd": 2.50,   # mid-tier frontier blended
    "llm_output_per_1m_tokens_usd": 10.00,
    "llm_embed_per_1m_tokens_usd": 0.10,
    "cloud_vm_hour_usd": 0.12,             # small always-on API box
    "gpu_hour_a10_usd": 1.10,              # if self-host mid model
    "vercel_serverless_gb_sec_usd": 0.000018,
    "storage_gb_month_usd": 0.023,
    "egress_gb_usd": 0.09,
    "notes": [
        "Blended LLM rates approximate GPT-4o-class / Claude Sonnet mid-2025 list.",
        "Metrix core path is deterministic Python — no token bill per orientation.",
        "Optional LLM only for natural-language polish of portal copy.",
        "Not a promise of savings; depends on traffic and whether LLM is used.",
    ],
}

# Workload templates: one paid "Orientation Run" ($290) as multi-agent equivalent
# Honest: a deep multi-step consulting agent (8+ tools, large context) — not a one-shot chat.
ORIENTATION_WORKLOAD = {
    "name": "single_orientation_run",
    "client_input_tokens": 4_000,
    "internal_reasoning_tokens_if_llm": 48_000,  # multi-step agent reasoning chain
    "output_tokens_if_llm": 6_500,
    "agent_tool_calls_if_llm": 18,
    "extra_tokens_per_tool_call": 2_000,
    "agent_pass_multiplier": 2.8,  # planner + worker + critic style
    "metrix_cpu_seconds": 2.5,
    "metrix_optional_llm_polish_in": 1_200,
    "metrix_optional_llm_polish_out": 900,
    "cloud_llm_only_cpu_seconds": 0.5,
    # Free portal / marketing previews (no $290) — pure LLM still pays tokens
    "free_preview_token_factor": 0.55,  # 55% of paid run tokens
}

# Monthly operating scenarios
# free_previews: funnel traffic that never pays — LLM burns cash; Metrix almost free
MONTHLY_SCENARIOS = {
    "bootstrap_50": {
        "label": "Bootstrap · 50 paid + 400 free previews / mo",
        "orientations": 50,
        "free_previews": 400,
        "full_packages": 2,
        "pilots": 4,
        "smm_posts": 20,
        "always_on_hours": 720,
    },
    "traction_200": {
        "label": "Traction · 200 paid + 2 000 free previews / mo",
        "orientations": 200,
        "free_previews": 2_000,
        "full_packages": 8,
        "pilots": 15,
        "smm_posts": 40,
        "always_on_hours": 720,
    },
    "scale_1000": {
        "label": "Scale · 1000 paid + 12 000 free previews / mo",
        "orientations": 1000,
        "free_previews": 12_000,
        "full_packages": 40,
        "pilots": 60,
        "smm_posts": 80,
        "always_on_hours": 720,
    },
}

REVENUE_UNIT = {
    "orientation_usd": 290,
    "pilot_usd": 1490,
    "full_package_usd": 2490,
    "additional_cap_usd": 1790,
}


class CapitalEfficiencyEngine:
    name = "Capital Efficiency Engine"
    status = "live"

    def run(
        self,
        *,
        scenario_key: str = "traction_200",
        industry_id: str = "",
        include_optional_llm: bool = True,
    ) -> dict[str, Any]:
        scenario = MONTHLY_SCENARIOS.get(scenario_key, MONTHLY_SCENARIOS["traction_200"])
        unit_a = self._cost_per_orientation_llm_cloud()
        unit_b = self._cost_per_orientation_hybrid()
        unit_c = self._cost_per_orientation_metrix(include_optional_llm)

        n = scenario["orientations"]
        monthly = {
            "A_pure_llm_cloud": self._monthly_roll(unit_a, scenario, mode="llm"),
            "B_hybrid": self._monthly_roll(unit_b, scenario, mode="hybrid"),
            "C_metrix_architecture": self._monthly_roll(
                unit_c, scenario, mode="metrix"
            ),
        }

        rev = self._monthly_revenue(scenario)
        comparisons = self._comparisons(monthly, rev)
        charts = self._chart_payloads(monthly, unit_a, unit_b, unit_c, rev, scenario)

        return {
            "module": self.name,
            "status": self.status,
            "assumptions": ASSUMPTIONS,
            "scenario": scenario,
            "scenario_key": scenario_key,
            "per_orientation_usd": {
                "A_pure_llm_cloud": unit_a,
                "B_hybrid": unit_b,
                "C_metrix_architecture": unit_c,
            },
            "monthly": monthly,
            "revenue_model_usd": rev,
            "comparisons": comparisons,
            "charts": charts,
            "output_per_dollar": {
                "A": round(rev["gross_revenue"] / max(0.01, monthly["A_pure_llm_cloud"]["total_ops_usd"]), 2),
                "B": round(rev["gross_revenue"] / max(0.01, monthly["B_hybrid"]["total_ops_usd"]), 2),
                "C": round(
                    rev["gross_revenue"]
                    / max(0.01, monthly["C_metrix_architecture"]["total_ops_usd"]),
                    2,
                ),
            },
            "pitch_bridge": {
                "claim": (
                    "Proprietary architecture + internal coordination → "
                    "lower cloud/LLM variable cost, higher output per same finance."
                ),
                "supported_by": [
                    "Deterministic OAE embedding (no per-request frontier tokens)",
                    "Paid core 16-step local compute",
                    "Optional LLM only for copy polish",
                    "Same commercial surface ($290 / $1490 / $2490)",
                ],
                "not_claimed": [
                    "Guaranteed savings without measuring real traffic",
                    "Zero LLM forever (polish/support may use LLM)",
                    "That cloud infra is free (VM still runs)",
                ],
            },
            "industry_id": industry_id or None,
            "honesty": (
                "Figures are model-based orientation economics, not audited P&L. "
                "Use as decision map; replace rates with your invoices when available."
            ),
        }

    def _llm_token_cost(self, tin: float, tout: float) -> float:
        a = ASSUMPTIONS
        return (
            tin / 1_000_000 * a["llm_input_per_1m_tokens_usd"]
            + tout / 1_000_000 * a["llm_output_per_1m_tokens_usd"]
        )

    def _cost_per_orientation_llm_cloud(self) -> dict[str, float]:
        w = ORIENTATION_WORKLOAD
        tin = w["client_input_tokens"] + w["internal_reasoning_tokens_if_llm"]
        tin += w["agent_tool_calls_if_llm"] * w["extra_tokens_per_tool_call"]
        tout = w["output_tokens_if_llm"]
        mult = float(w.get("agent_pass_multiplier", 2.5))
        tokens = self._llm_token_cost(tin, tout) * mult
        infra = w["cloud_llm_only_cpu_seconds"] / 3600 * ASSUMPTIONS["cloud_vm_hour_usd"]
        other = 0.02  # tracing, retries, eval logs
        total = tokens + infra + other
        return {
            "llm_tokens_usd": round(tokens, 4),
            "infra_usd": round(infra, 4),
            "other_usd": round(other, 4),
            "total_usd": round(total, 4),
            "input_tokens": int(tin * mult),
            "output_tokens": int(tout * mult),
            "label": "Pure LLM multi-agent cloud",
        }

    def _cost_per_orientation_hybrid(self) -> dict[str, float]:
        pure = self._cost_per_orientation_llm_cloud()
        # Hybrid: ~35% of agent tokens (retrieval + one LLM pass)
        tokens = pure["llm_tokens_usd"] * 0.35
        infra = 4.0 / 3600 * ASSUMPTIONS["cloud_vm_hour_usd"]
        other = 0.012
        total = tokens + infra + other
        return {
            "llm_tokens_usd": round(tokens, 4),
            "infra_usd": round(infra, 4),
            "other_usd": round(other, 4),
            "total_usd": round(total, 4),
            "input_tokens": int(pure["input_tokens"] * 0.35),
            "output_tokens": int(pure["output_tokens"] * 0.35),
            "label": "Hybrid rules + selective LLM",
        }

    def _cost_per_orientation_metrix(self, include_optional_llm: bool) -> dict[str, float]:
        w = ORIENTATION_WORKLOAD
        if include_optional_llm:
            tokens = self._llm_token_cost(
                w["metrix_optional_llm_polish_in"],
                w["metrix_optional_llm_polish_out"],
            )
            tin, tout = w["metrix_optional_llm_polish_in"], w["metrix_optional_llm_polish_out"]
        else:
            tokens = 0.0
            tin = tout = 0
        # Deterministic pipeline on small VM / serverless
        infra = w["metrix_cpu_seconds"] / 3600 * ASSUMPTIONS["cloud_vm_hour_usd"]
        # workspace JSON write
        other = 0.004
        total = tokens + infra + other
        return {
            "llm_tokens_usd": round(tokens, 4),
            "infra_usd": round(infra, 4),
            "other_usd": round(other, 4),
            "total_usd": round(total, 4),
            "input_tokens": int(tin),
            "output_tokens": int(tout),
            "label": "Metrix proprietary pipeline (+ optional polish LLM)",
        }

    def _monthly_roll(
        self, unit: dict[str, float], scenario: dict[str, Any], mode: str
    ) -> dict[str, Any]:
        n = scenario["orientations"]
        free = int(scenario.get("free_previews") or 0)
        var = unit["total_usd"] * n
        # Free previews: LLM/hybrid pay a fraction of unit cost; Metrix ~CPU crumbs only
        preview_factor = float(ORIENTATION_WORKLOAD.get("free_preview_token_factor", 0.55))
        if mode == "metrix":
            free_cost = free * (unit["infra_usd"] + unit["other_usd"] + 0.001)
        elif mode == "hybrid":
            free_cost = free * unit["total_usd"] * preview_factor * 0.7
        else:
            free_cost = free * unit["total_usd"] * preview_factor

        always = scenario["always_on_hours"] * ASSUMPTIONS["cloud_vm_hour_usd"]
        if mode == "llm":
            always *= 1.25
            storage = 12 * ASSUMPTIONS["storage_gb_month_usd"]
            egress = 40 * ASSUMPTIONS["egress_gb_usd"]
        elif mode == "hybrid":
            storage = 7 * ASSUMPTIONS["storage_gb_month_usd"]
            egress = 18 * ASSUMPTIONS["egress_gb_usd"]
        else:
            always *= 0.85
            storage = 4 * ASSUMPTIONS["storage_gb_month_usd"]
            egress = 6 * ASSUMPTIONS["egress_gb_usd"]

        # Pilot/package delivery overhead (human-adjacent compute)
        pilot_compute = scenario["pilots"] * (0.25 if mode == "metrix" else 1.8)
        full_compute = scenario["full_packages"] * (0.6 if mode == "metrix" else 4.5)

        total = var + free_cost + always + storage + egress + pilot_compute + full_compute
        return {
            "variable_orientations_usd": round(var, 2),
            "free_previews_usd": round(free_cost, 2),
            "free_previews_count": free,
            "always_on_usd": round(always, 2),
            "storage_usd": round(storage, 2),
            "egress_usd": round(egress, 2),
            "pilot_compute_usd": round(pilot_compute, 2),
            "full_package_compute_usd": round(full_compute, 2),
            "total_ops_usd": round(total, 2),
            "unit_total_usd": unit["total_usd"],
            "mode": mode,
            "label": unit["label"],
        }

    def _monthly_revenue(self, scenario: dict[str, Any]) -> dict[str, Any]:
        r = REVENUE_UNIT
        orient = scenario["orientations"] * r["orientation_usd"]
        pilots = scenario["pilots"] * r["pilot_usd"]
        fulls = scenario["full_packages"] * r["full_package_usd"]
        # Assume 10% of pilots also buy additional capability
        caps = int(scenario["pilots"] * 0.1) * r["additional_cap_usd"]
        gross = orient + pilots + fulls + caps
        return {
            "orientation_revenue": orient,
            "pilot_revenue": pilots,
            "full_package_revenue": fulls,
            "additional_capability_revenue": caps,
            "gross_revenue": gross,
            "units": {
                "orientations": scenario["orientations"],
                "pilots": scenario["pilots"],
                "full_packages": scenario["full_packages"],
            },
            "prices": r,
        }

    def _comparisons(
        self, monthly: dict[str, Any], rev: dict[str, Any]
    ) -> dict[str, Any]:
        a = monthly["A_pure_llm_cloud"]["total_ops_usd"]
        b = monthly["B_hybrid"]["total_ops_usd"]
        c = monthly["C_metrix_architecture"]["total_ops_usd"]
        gross = rev["gross_revenue"]

        def margin(ops: float) -> float:
            return round((gross - ops) / max(1, gross) * 100, 2)

        return {
            "ops_cost_usd": {"A": a, "B": b, "C": c},
            "savings_C_vs_A_usd": round(a - c, 2),
            "savings_C_vs_A_pct": round((a - c) / max(0.01, a) * 100, 1),
            "savings_C_vs_B_usd": round(b - c, 2),
            "savings_C_vs_B_pct": round((b - c) / max(0.01, b) * 100, 1),
            "gross_margin_pct": {"A": margin(a), "B": margin(b), "C": margin(c)},
            "cost_share_of_revenue_pct": {
                "A": round(a / gross * 100, 2),
                "B": round(b / gross * 100, 2),
                "C": round(c / gross * 100, 2),
            },
            "break_even_orientations_approx": {
                "note": "At $290/unit, ops-only break-even is nearly immediate; "
                "real break-even includes founder salary / SMM (separate).",
                "A_ops_only": max(1, int(a / 290) + 1) if False else 1,
            },
            "payback_from_two_transactions": {
                "claim": "Product can amortize build effort from ~2 client checks ($1–3k).",
                "example_two_pilots_usd": 2 * REVENUE_UNIT["pilot_usd"],
                "example_one_full_one_orient_usd": (
                    REVENUE_UNIT["full_package_usd"] + REVENUE_UNIT["orientation_usd"]
                ),
            },
        }

    def _chart_payloads(
        self,
        monthly: dict[str, Any],
        unit_a: dict[str, float],
        unit_b: dict[str, float],
        unit_c: dict[str, float],
        rev: dict[str, Any],
        scenario: dict[str, Any],
    ) -> dict[str, Any]:
        """Data series for frontend charts (Chart.js friendly)."""
        labels_arch = ["A Pure LLM", "B Hybrid", "C Metrix"]
        return {
            "per_orientation_cost": {
                "type": "bar",
                "title": "Cost per Orientation Run (USD)",
                "labels": labels_arch,
                "datasets": [
                    {
                        "label": "LLM tokens",
                        "data": [
                            unit_a["llm_tokens_usd"],
                            unit_b["llm_tokens_usd"],
                            unit_c["llm_tokens_usd"],
                        ],
                    },
                    {
                        "label": "Infra",
                        "data": [
                            unit_a["infra_usd"],
                            unit_b["infra_usd"],
                            unit_c["infra_usd"],
                        ],
                    },
                    {
                        "label": "Other",
                        "data": [
                            unit_a["other_usd"],
                            unit_b["other_usd"],
                            unit_c["other_usd"],
                        ],
                    },
                ],
            },
            "monthly_ops": {
                "type": "bar",
                "title": f"Monthly ops cost — {scenario['label']}",
                "labels": labels_arch,
                "datasets": [
                    {
                        "label": "Total ops USD",
                        "data": [
                            monthly["A_pure_llm_cloud"]["total_ops_usd"],
                            monthly["B_hybrid"]["total_ops_usd"],
                            monthly["C_metrix_architecture"]["total_ops_usd"],
                        ],
                    }
                ],
            },
            "ops_breakdown_metrix": {
                "type": "doughnut",
                "title": "Metrix monthly ops breakdown",
                "labels": [
                    "Paid orientations",
                    "Free previews",
                    "Always-on",
                    "Storage+egress",
                    "Pilot+Full compute",
                ],
                "datasets": [
                    {
                        "data": [
                            monthly["C_metrix_architecture"]["variable_orientations_usd"],
                            monthly["C_metrix_architecture"].get("free_previews_usd", 0),
                            monthly["C_metrix_architecture"]["always_on_usd"],
                            monthly["C_metrix_architecture"]["storage_usd"]
                            + monthly["C_metrix_architecture"]["egress_usd"],
                            monthly["C_metrix_architecture"]["pilot_compute_usd"]
                            + monthly["C_metrix_architecture"]["full_package_compute_usd"],
                        ]
                    }
                ],
            },
            "free_preview_tax": {
                "type": "bar",
                "title": "Free-preview funnel tax (USD / mo) — where pure LLM bleeds",
                "labels": labels_arch,
                "datasets": [
                    {
                        "label": "Free previews ops USD",
                        "data": [
                            monthly["A_pure_llm_cloud"].get("free_previews_usd", 0),
                            monthly["B_hybrid"].get("free_previews_usd", 0),
                            monthly["C_metrix_architecture"].get("free_previews_usd", 0),
                        ],
                    }
                ],
            },
            "revenue_mix": {
                "type": "doughnut",
                "title": "Monthly revenue mix (model)",
                "labels": ["Orientation $290", "Pilot $1490", "Full $2490", "Add-on $1790"],
                "datasets": [
                    {
                        "data": [
                            rev["orientation_revenue"],
                            rev["pilot_revenue"],
                            rev["full_package_revenue"],
                            rev["additional_capability_revenue"],
                        ]
                    }
                ],
            },
            "margin_compare": {
                "type": "bar",
                "title": "Modeled gross margin % (ops only)",
                "labels": labels_arch,
                "datasets": [
                    {
                        "label": "Gross margin %",
                        "data": [
                            round(
                                (rev["gross_revenue"] - monthly["A_pure_llm_cloud"]["total_ops_usd"])
                                / rev["gross_revenue"]
                                * 100,
                                2,
                            ),
                            round(
                                (rev["gross_revenue"] - monthly["B_hybrid"]["total_ops_usd"])
                                / rev["gross_revenue"]
                                * 100,
                                2,
                            ),
                            round(
                                (
                                    rev["gross_revenue"]
                                    - monthly["C_metrix_architecture"]["total_ops_usd"]
                                )
                                / rev["gross_revenue"]
                                * 100,
                                2,
                            ),
                        ],
                    }
                ],
            },
            "output_per_dollar": {
                "type": "bar",
                "title": "Revenue $ per $1 ops spend",
                "labels": labels_arch,
                "datasets": [
                    {
                        "label": "$ revenue / $ ops",
                        "data": [
                            round(
                                rev["gross_revenue"]
                                / max(0.01, monthly["A_pure_llm_cloud"]["total_ops_usd"]),
                                1,
                            ),
                            round(
                                rev["gross_revenue"]
                                / max(0.01, monthly["B_hybrid"]["total_ops_usd"]),
                                1,
                            ),
                            round(
                                rev["gross_revenue"]
                                / max(
                                    0.01,
                                    monthly["C_metrix_architecture"]["total_ops_usd"],
                                ),
                                1,
                            ),
                        ],
                    }
                ],
            },
            "scale_curve": self._scale_curve(),
        }

    def _scale_curve(self) -> dict[str, Any]:
        """Ops cost vs orientations for three architectures."""
        xs = [25, 50, 100, 200, 500, 1000]
        series = {"A": [], "B": [], "C": []}
        for n in xs:
            sc = {
                "orientations": n,
                "free_previews": n * 10,
                "full_packages": max(1, n // 25),
                "pilots": max(1, n // 12),
                "smm_posts": 20,
                "always_on_hours": 720,
                "label": f"n={n}",
            }
            series["A"].append(
                self._monthly_roll(self._cost_per_orientation_llm_cloud(), sc, "llm")[
                    "total_ops_usd"
                ]
            )
            series["B"].append(
                self._monthly_roll(self._cost_per_orientation_hybrid(), sc, "hybrid")[
                    "total_ops_usd"
                ]
            )
            series["C"].append(
                self._monthly_roll(
                    self._cost_per_orientation_metrix(True), sc, "metrix"
                )["total_ops_usd"]
            )
        return {
            "type": "line",
            "title": "Monthly ops cost vs orientation volume",
            "labels": [str(x) for x in xs],
            "datasets": [
                {"label": "A Pure LLM", "data": series["A"]},
                {"label": "B Hybrid", "data": series["B"]},
                {"label": "C Metrix", "data": series["C"]},
            ],
        }

    def all_scenarios(self) -> dict[str, Any]:
        out = {}
        for key in MONTHLY_SCENARIOS:
            out[key] = self.run(scenario_key=key)
        return {
            "module": self.name,
            "scenarios": {k: self._thin(v) for k, v in out.items()},
            "full": out,
        }

    def _thin(self, report: dict[str, Any]) -> dict[str, Any]:
        return {
            "scenario_key": report["scenario_key"],
            "per_orientation_usd": {
                k: v["total_usd"] for k, v in report["per_orientation_usd"].items()
            },
            "monthly_ops_usd": {
                k: v["total_ops_usd"] for k, v in report["monthly"].items()
            },
            "comparisons": report["comparisons"],
            "output_per_dollar": report["output_per_dollar"],
            "gross_revenue": report["revenue_model_usd"]["gross_revenue"],
        }
