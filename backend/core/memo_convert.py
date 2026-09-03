"""
Memo Convert — unique engine + reader-assembler (instead of a static DB).

Architecture (Market Units 2026-07-26):
  1. System intake → open-opportunity analysis (cooperation theory)
  2. Ideas / solutions → categorical system data (reverse context; informatics law)
  3. Analog engine: drop raw values → model properties → select *function*, not method
  4. Reader-assembler → technical-task language (SpecsForge / tech writing handoff)
  5. Personalize answers from system context + interaction history (process tasks)
  6. Complexity-boundary cognitive gates (from @karimmetrix principles)

No durable idea-DB lookup. Meaning is rebuilt on the fly from system state + brief.
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import asdict, dataclass, field
from typing import Any

from backend.paid.types import clamp01, safe_float


# ── Cognitive complexity principles (operable subset from public posts) ─────

COMPLEXITY_PRINCIPLES: list[dict[str, Any]] = [
    {
        "id": "void_plasticity",
        "title": "Voids between systems are generative",
        "rule": "Prefer interstitial function pick over linear method polish inside a closed frame.",
        "boundary": "If residual uncertainty is structural, do not force method iteration — reselect function.",
        "source": "karimmetrix structural-hole / interstitial",
    },
    {
        "id": "error_as_signal",
        "title": "Error as primary probe",
        "rule": "Treat ER/VVI rises as signal for function re-pick, not only as defect to suppress.",
        "boundary": "Complexity ceiling: stop method recursion when improvement_delta < SPECS floor.",
        "source": "karimmetrix error-as-phase-transition",
    },
    {
        "id": "attribute_substitution",
        "title": "Avoid easy-frame substitution",
        "rule": "Do not replace causal architecture with a convenient formal frame.",
        "boundary": "If diagnosis is only JTBD-generic, raise reverse-context pressure.",
        "source": "karimmetrix Kahneman attribute substitution",
    },
    {
        "id": "dimensionality",
        "title": "Refuse single-axis flattening",
        "rule": "Model properties on multiple planes; drop scalar 'success' as sole objective.",
        "boundary": "Max simultaneous planes before reassembly: 5 (cognitive load gate).",
        "source": "karimmetrix dimensionality distortion",
    },
    {
        "id": "cooperation_open_opp",
        "title": "Open opportunity via cooperation calculus",
        "rule": "Score open opportunities by joint surplus (buyer+seller+system), not solo extraction.",
        "boundary": "Coop score < 0.35 → do not package as sellable without bridge.",
        "source": "cooperation theory / Market Units",
    },
]


# ── Industry system categories (lightweight, not a solution DB) ─────────────

SYSTEM_CATEGORIES: dict[str, list[str]] = {
    "ai-agencies": [
        "ops_efficiency",
        "delivery_geometry",
        "margin_defense",
        "scope_gates",
        "teammate_attach",
    ],
    "cloud-economy": [
        "third_party_api_spend",
        "token_unit_economics",
        "expert_env_vs_llm",
        "reply_quality_band",
        "creative_ops_cost",
    ],
    "cost-engineering": [
        "parameter_waste",
        "capability_preserve",
        "rework_cost",
        "tolerance_price",
        "simple_offer_surface",
    ],
    "chipmaking": [
        "design_loop_voids",
        "yield_geometry",
        "nre_iteration",
        "gate_decisions",
        "clarity_over_hype",
    ],
    "telecom": [
        "sla_qos",
        "arpu_churn",
        "intent_signal",
        "capacity_investment",
        "mvno_partner",
    ],
    "device-assembly": [
        "station_instructions",
        "config_sku",
        "labor_rework",
        "setup_scale",
        "predev_promo",
    ],
}


@dataclass
class OpenOpportunity:
    id: str
    title: str
    coop_score: float
    joint_surplus: float
    buyer_gain: float
    seller_gain: float
    system_category: str
    abstraction_point: str
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TechnicalTask:
    id: str
    title: str
    language: str  # tech-writing ready
    acceptance: list[str]
    function_selected: str
    complexity_gate: str
    specsforge_ready: bool
    reverse_context: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MemoConvertResult:
    module: str
    version: str
    system_state: dict[str, Any]
    open_opportunities: list[dict[str, Any]]
    categorical_data: dict[str, Any]
    analog_engine: dict[str, Any]
    technical_tasks: list[dict[str, Any]]
    personalization: dict[str, Any]
    complexity_gates: list[dict[str, Any]]
    engine_on_same_arch: dict[str, Any]
    summary: str
    chain_pack: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "version": self.version,
            "system_state": self.system_state,
            "open_opportunities": self.open_opportunities,
            "categorical_data": self.categorical_data,
            "analog_engine": self.analog_engine,
            "technical_tasks": self.technical_tasks,
            "personalization": self.personalization,
            "complexity_gates": self.complexity_gates,
            "engine_on_same_arch": self.engine_on_same_arch,
            "summary": self.summary,
            "chain_pack": self.chain_pack,
            "convert_v2": True,
        }


def _sid(prefix: str, *parts: str) -> str:
    raw = "|".join(parts)
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}_{h}"


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Zа-яА-Я0-9]{3,}", (text or "").lower())}


class MemoConvertEngine:
    """
    Unique engine: system data ↔ ideas ↔ tech tasks.
    Reader-assembler role is embedded (no separate DB of memos).
    """

    name = "Memo Convert Engine"
    version = "1.2.0"

    # Function library (selectable abstractions — not execution methods)
    FUNCTIONS: dict[str, dict[str, Any]] = {
        "ops_efficiency_map": {
            "title": "Operational efficiency map",
            "plane": "ops",
            "when": "agency or delivery margin pressure",
            "out": "terminal_teammate_attach",
        },
        "api_cost_collapse": {
            "title": "Third-party API cost collapse",
            "plane": "spend",
            "when": "creative / founder token burn",
            "out": "expert_env_quality_up_cost_down",
        },
        "parameter_void_cut": {
            "title": "Parameter void cut (capability preserved)",
            "plane": "cost",
            "when": "cost engineering / waste",
            "out": "simple_offer_surface",
        },
        "yield_gate_function": {
            "title": "Yield / gate decision function",
            "plane": "chip",
            "when": "design loop or fab gate",
            "out": "clarity_pack",
        },
        "signal_qos_bridge": {
            "title": "Intent signal ↔ QoS bridge",
            "plane": "telecom",
            "when": "ARPU/churn/capacity",
            "out": "sla_native_sku",
        },
        "fin_model_buyer_proof": {
            "title": "Buyer financial-model proof",
            "plane": "promo",
            "when": "selling teammate to buying business",
            "out": "terminal_teammate_sale",
        },
        "event_review_container": {
            "title": "Event review container + sales pointer",
            "plane": "promo",
            "when": "founders already shipping creative ops",
            "out": "expert_product_upsell",
        },
    }

    def convert(
        self,
        *,
        business_text: str,
        industry_id: str,
        orientation: dict[str, Any] | None = None,
        oae: dict[str, Any] | None = None,
        decision: dict[str, Any] | None = None,
        product: dict[str, Any] | None = None,
        paid: dict[str, Any] | None = None,
        system_features: dict[str, Any] | None = None,
        success: dict[str, Any] | None = None,
        ideas: list[dict[str, Any]] | None = None,
        chain_id: str | None = None,
    ) -> MemoConvertResult:
        orientation = orientation or {}
        oae = oae or {}
        decision = decision or {}
        product = product or {}
        paid = paid or {}
        system_features = system_features or {}
        success = success or {}
        ideas = ideas or list(product.get("demo_ideas") or [])

        # 1. System intake
        system_state = self._system_intake(
            business_text=business_text,
            industry_id=industry_id,
            orientation=orientation,
            oae=oae,
            decision=decision,
            system_features=system_features,
            success=success,
        )

        # 2. Open opportunities (cooperation calculus)
        opps = self._open_opportunities(system_state, business_text, industry_id)

        # 3. Analog engine → function selection
        analog = self._analog_engine(system_state, opps, industry_id)

        # 4. Ideas → categorical system data (reverse context)
        categorical = self._ideas_to_categories(
            ideas=ideas,
            system_state=system_state,
            industry_id=industry_id,
            function_key=analog.get("selected_function") or "",
        )

        # 5. Reader-assembler → technical tasks
        tech_tasks = self._reader_assemble_tasks(
            system_state=system_state,
            analog=analog,
            categorical=categorical,
            opps=opps,
            business_text=business_text,
            industry_id=industry_id,
        )

        # 6. Personalization for process tasks
        personalization = self._personalize(
            system_state=system_state,
            categorical=categorical,
            tech_tasks=tech_tasks,
            business_text=business_text,
        )

        # Complexity gates applied
        gates = self._apply_complexity_gates(system_state, analog, opps)

        # Can we build an engine on the same architecture from last improved version?
        same_arch = self._engine_architecture_answer(analog, tech_tasks, system_state)

        best_coop = max((o.coop_score for o in opps), default=0.0)
        summary = (
            f"{self.name} v{self.version}: categories={len(categorical.get('mapped') or [])}, "
            f"open_opp={len(opps)}, best_coop={best_coop:.2f}, "
            f"function={analog.get('selected_function')}, "
            f"tech_tasks={len(tech_tasks)}, "
            f"same_arch_engine={'yes' if same_arch.get('feasible') else 'partial'}."
        )

        chain_pack = self._chain_pack(
            chain_id=chain_id,
            system_state=system_state,
            analog=analog,
            tech_tasks=tech_tasks,
            industry_id=industry_id,
        )
        if chain_pack.get("unbound_critical"):
            system_state = {**system_state, "unbound_critical": chain_pack["unbound_critical"]}
        summary = f"{summary} convert_v2 chain_pack={'yes' if chain_pack else 'empty'}."

        return MemoConvertResult(
            module=self.name,
            version=self.version,
            system_state=system_state,
            open_opportunities=[o.to_dict() for o in opps],
            categorical_data=categorical,
            analog_engine=analog,
            technical_tasks=[t.to_dict() for t in tech_tasks],
            personalization=personalization,
            complexity_gates=gates,
            engine_on_same_arch=same_arch,
            summary=summary,
            chain_pack=chain_pack,
        )

    def _chain_pack(
        self,
        *,
        chain_id: str | None,
        system_state: dict[str, Any],
        analog: dict[str, Any],
        tech_tasks: list[Any],
        industry_id: str,
    ) -> dict[str, Any]:
        """Relays what is already assembled. Does not invent missing slots."""
        from backend.core.circle_system.copy_firmware import CopyFirmware
        from backend.core.circle_system.chain_store import load_chain

        rec = load_chain(chain_id) if chain_id else None
        ra = (rec or {}).get("resource_assembly") or {}
        topology = (rec or {}).get("topology") or "b2c"
        unbound = list(ra.get("unbound_critical") or [])
        fw = CopyFirmware()
        copy_blocks = {
            "b2c": fw.offer_block(
                who="client",
                void="unbound: " + ",".join(unbound) if unbound else "consult void",
                gate="assembly≥0.45",
                price="free → pilot → main $2490",
                not_included="Main before gates",
                voice="b2c",
                lang="en",
            ),
            "a2a": fw.offer_block(
                who="slot owner",
                void="handoff artefact",
                gate="sync_score",
                price="coordination",
                not_included="B2C stepper",
                voice="a2a",
                lang="en",
            ),
            "tech_write": fw.offer_block(
                who="spec",
                void="terminal",
                gate="ASM",
                price="n/a",
                not_included="warmth in facts",
                voice="tech_write",
                lang="en",
            ),
        }
        pack = {
            "b2c_path": topology in ("b2c", "dual"),
            "a2a_path": topology in ("a2a", "dual"),
            "bound_resources": ra.get("bound_slots") or {},
            "artefacts": (rec or {}).get("artefacts_applied") or [],
            "naming_sigils": {
                "chain": ra.get("public_sigil") or (rec or {}).get("public_sigil"),
                "internal_id": chain_id or ra.get("chain_id"),
            },
            "gates_snapshot": {
                "vvi": (system_state.get("metrics") or {}).get("vvi"),
                "er": (system_state.get("metrics") or {}).get("er"),
                "rrc": (system_state.get("metrics") or {}).get("rrc"),
                "assembly": ra.get("compatibility"),
                "consistency": (rec or {}).get("consistency"),
            },
            "copy_blocks": copy_blocks,
            "miniapp_case_stub": {
                "ready": not unbound and float(ra.get("compatibility") or 0) >= 0.45,
                "sigil": (rec or {}).get("public_sigil"),
            },
            "unbound_critical": unbound,
            "invented_slots": False,
            "function": analog.get("selected_function"),
            "tech_task_0": (tech_tasks[0].to_dict() if tech_tasks and hasattr(tech_tasks[0], "to_dict") else (tech_tasks[0] if tech_tasks else None)),
        }
        return pack

    # ── 1. System intake ───────────────────────────────────────────────────

    def _system_intake(
        self,
        *,
        business_text: str,
        industry_id: str,
        orientation: dict[str, Any],
        oae: dict[str, Any],
        decision: dict[str, Any],
        system_features: dict[str, Any],
        success: dict[str, Any],
    ) -> dict[str, Any]:
        scores = orientation.get("scores") or {}
        axes = (orientation.get("frame") or {}).get("axes") or {}
        delta = oae.get("metrics_delta") or {}
        cats = SYSTEM_CATEGORIES.get(industry_id, SYSTEM_CATEGORIES["ai-agencies"])

        vvi = safe_float(delta.get("vvi_after"), safe_float(scores.get("vvi"), 0.35))
        er = safe_float(delta.get("er_after"), 0.55)
        rrc = safe_float(delta.get("rrc_after"), safe_float(scores.get("rrc"), 0.5))
        health = safe_float(delta.get("health_after"), safe_float(scores.get("overall_orientation"), 0.5))

        tokens = _tokens(business_text)
        api_signal = bool(
            tokens
            & {
                "api",
                "token",
                "llm",
                "openai",
                "anthropic",
                "gemini",
                "cloud",
                "cost",
                "spend",
                "creative",
                "founder",
                "агент",
                "токен",
                "апи",
            }
        )
        ops_signal = bool(
            tokens
            & {
                "ops",
                "margin",
                "rework",
                "delivery",
                "utilization",
                "agency",
                "операц",
                "маржа",
                "агентств",
            }
        )

        return {
            "industry_id": industry_id,
            "categories_available": cats,
            "scores": {k: round(safe_float(v), 4) for k, v in scores.items()},
            "axes": {k: round(safe_float(v), 4) for k, v in axes.items()},
            "metrics": {
                "vvi": round(vvi, 4),
                "er": round(er, 4),
                "rrc": round(rrc, 4),
                "health": round(health, 4),
            },
            "decision_mode": decision.get("active_mode") or "scoring",
            "system_log_gravity": round(
                safe_float(
                    (system_features or {}).get("gravity")
                    or (system_features or {}).get("request_count", 0) / 100.0
                ),
                4,
            ),
            "success_composite": round(
                safe_float(
                    success.get("weighted_composite")
                    or (success.get("card") or {}).get("weighted_composite"),
                    0.5,
                ),
                4,
            ),
            "signals": {
                "api_cost_pressure": api_signal,
                "ops_efficiency_pressure": ops_signal,
            },
            "brief_token_count": len(tokens),
            "abstraction_target": self._pick_abstraction_target(
                industry_id, vvi, rrc, api_signal, ops_signal
            ),
        }

    def _pick_abstraction_target(
        self,
        industry_id: str,
        vvi: float,
        rrc: float,
        api_signal: bool,
        ops_signal: bool,
    ) -> str:
        if industry_id == "cloud-economy" or api_signal:
            return "function_select:api_cost_collapse"
        if industry_id == "ai-agencies" or ops_signal:
            return "function_select:ops_efficiency_map"
        if industry_id == "cost-engineering":
            return "function_select:parameter_void_cut"
        if industry_id == "chipmaking":
            return "function_select:yield_gate_function"
        if industry_id == "telecom":
            return "function_select:signal_qos_bridge"
        if vvi > 0.55 and rrc < 0.5:
            return "function_select:void_reassembly"
        return "function_select:fin_model_buyer_proof"

    # ── 2. Open opportunities (cooperation theory) ─────────────────────────

    def _open_opportunities(
        self,
        system_state: dict[str, Any],
        business_text: str,
        industry_id: str,
    ) -> list[OpenOpportunity]:
        m = system_state["metrics"]
        health = m["health"]
        rrc = m["rrc"]
        er = m["er"]
        success = system_state["success_composite"]
        cats = system_state["categories_available"]
        signals = system_state["signals"]

        # Joint surplus ≈ buyer clarity gain + seller packageability + system health
        buyer_gain = clamp01(0.35 + 0.4 * success + 0.15 * er)
        seller_gain = clamp01(0.3 + 0.35 * health + 0.2 * rrc)
        joint = round(0.55 * buyer_gain + 0.45 * seller_gain, 4)
        coop = clamp01(joint * (0.85 + 0.15 * er) - 0.1 * m["vvi"])

        seeds: list[tuple[str, str, str]] = []
        if industry_id == "ai-agencies":
            seeds = [
                (
                    "ops_efficiency",
                    "Ops efficiency → Terminal Teammate",
                    "fin_model_buyer_proof",
                ),
                (
                    "delivery_geometry",
                    "Delivery geometry without free-discovery burn",
                    "ops_efficiency_map",
                ),
            ]
        elif industry_id == "cloud-economy":
            seeds = [
                (
                    "third_party_api_spend",
                    "Cut third-party API spend, keep creative quality",
                    "api_cost_collapse",
                ),
                (
                    "expert_env_vs_llm",
                    "Expert env vs pure LLM (structural 12.5× unit)",
                    "api_cost_collapse",
                ),
            ]
        elif industry_id == "cost-engineering":
            seeds = [
                (
                    "parameter_waste",
                    "Simple waste-cut offer for broad cost-eng audience",
                    "parameter_void_cut",
                ),
                (
                    "simple_offer_surface",
                    "One product SKU cost engineers can resell",
                    "parameter_void_cut",
                ),
            ]
        elif industry_id == "chipmaking":
            seeds = [
                (
                    "design_loop_voids",
                    "Design-loop void pack (ops)",
                    "yield_gate_function",
                ),
                ("yield_geometry", "Yield geometry twin (product)", "yield_gate_function"),
                (
                    "clarity_over_hype",
                    "Semiconductor clarity event (promotion)",
                    "event_review_container",
                ),
            ]
        elif industry_id == "telecom":
            seeds = [
                ("sla_qos", "SLA-native SKU bridge", "signal_qos_bridge"),
                ("arpu_churn", "ARPU/churn lever pack", "signal_qos_bridge"),
                (
                    "intent_signal",
                    "Intent signal weave for care/MVNO",
                    "event_review_container",
                ),
            ]
        else:
            seeds = [
                (cats[0], f"Primary open opp · {cats[0]}", "ops_efficiency_map"),
                (
                    cats[min(1, len(cats) - 1)],
                    f"Secondary open opp · {cats[min(1, len(cats) - 1)]}",
                    "fin_model_buyer_proof",
                ),
            ]

        if signals.get("api_cost_pressure") and not any(
            s[2] == "api_cost_collapse" for s in seeds
        ):
            seeds.insert(
                0,
                (
                    "third_party_api_spend",
                    "API burn detected in brief → collapse path",
                    "api_cost_collapse",
                ),
            )

        out: list[OpenOpportunity] = []
        for i, (cat, title, fn) in enumerate(seeds[:4]):
            adj = 1.0 - i * 0.07
            cscore = round(clamp01(coop * adj), 4)
            out.append(
                OpenOpportunity(
                    id=_sid("opp", industry_id, cat, title),
                    title=title,
                    coop_score=cscore,
                    joint_surplus=round(joint * adj, 4),
                    buyer_gain=round(buyer_gain * adj, 4),
                    seller_gain=round(seller_gain * adj, 4),
                    system_category=cat,
                    abstraction_point=fn,
                    notes=[
                        "Cooperation calculus: joint surplus first",
                        f"Abstraction = function {fn}, not method stack",
                    ],
                )
            )
        out.sort(key=lambda o: o.coop_score, reverse=True)
        return out

    # ── 3. Analog engine ───────────────────────────────────────────────────

    def _analog_engine(
        self,
        system_state: dict[str, Any],
        opps: list[OpenOpportunity],
        industry_id: str,
    ) -> dict[str, Any]:
        """
        Physical-phenomena style: model properties, refuse raw value worship,
        shift emphasis from improved-execution methods → function selection.
        """
        m = system_state["metrics"]
        # Property planes (analog — continuous properties, not catalog keys)
        planes = {
            "tension": round(clamp01(m["vvi"] * 0.6 + (1 - m["health"]) * 0.4), 4),
            "plasticity": round(clamp01(m["rrc"] * 0.7 + m["er"] * 0.3), 4),
            "density": round(clamp01(system_state["success_composite"]), 4),
            "noise": round(clamp01(0.2 + 0.5 * m["vvi"] + 0.2 * (1 - m["er"])), 4),
            "coupling": round(
                clamp01(0.3 + 0.4 * safe_float((system_state.get("axes") or {}).get("entanglement"), 0.4)),
                4,
            ),
        }
        # Drop absolute "values" — keep relative ranks of properties
        ranked = sorted(planes.items(), key=lambda kv: kv[1], reverse=True)
        top_props = [k for k, _ in ranked[:3]]

        preferred = (opps[0].abstraction_point if opps else "") or ""
        target = system_state.get("abstraction_target", "")
        if preferred in self.FUNCTIONS:
            selected = preferred
        elif "api_cost" in target:
            selected = "api_cost_collapse"
        else:
            # Map top property → function
            if "tension" in top_props and industry_id in ("cost-engineering", "chipmaking"):
                selected = (
                    "parameter_void_cut"
                    if industry_id == "cost-engineering"
                    else "yield_gate_function"
                )
            elif "plasticity" in top_props:
                selected = "ops_efficiency_map"
            elif industry_id == "telecom":
                selected = "signal_qos_bridge"
            elif industry_id == "cloud-economy":
                selected = "api_cost_collapse"
            else:
                selected = "fin_model_buyer_proof"

        fn = self.FUNCTIONS.get(selected, self.FUNCTIONS["ops_efficiency_map"])
        return {
            "mode": "analog_property_planes",
            "refuses_raw_values": True,
            "emphasis": "function_selection_not_method_polish",
            "planes": planes,
            "top_properties": top_props,
            "selected_function": selected,
            "function_meta": fn,
            "method_iteration_blocked": planes["noise"] > 0.65 and planes["plasticity"] < 0.45,
            "note": (
                "Analog engine drops absolute KPI worship; selects a function on property planes. "
                "Method recursion only after function is locked."
            ),
        }

    # ── 4. Reverse context: ideas → categories ─────────────────────────────

    def _ideas_to_categories(
        self,
        *,
        ideas: list[dict[str, Any]],
        system_state: dict[str, Any],
        industry_id: str,
        function_key: str,
    ) -> dict[str, Any]:
        """
        Informatics law: more reverse context from forward context + system values.
        Solutions map back into categorical system data (not stored as free text only).
        """
        cats = system_state["categories_available"]
        mapped: list[dict[str, Any]] = []
        for idea in ideas[:8]:
            title = str(idea.get("title") or idea.get("label") or "")
            toks = _tokens(title)
            best_cat = cats[0]
            best_hit = -1
            for c in cats:
                hit = sum(1 for part in c.split("_") if part in toks or part[:4] in " ".join(toks))
                # soft match on keywords
                for t in toks:
                    if t[:4] in c or c.split("_")[0][:4] in t:
                        hit += 1
                if hit > best_hit:
                    best_hit = hit
                    best_cat = c
            # reverse pressure: category gets weight from idea score + system health
            score = safe_float(idea.get("score"), 0.5)
            reverse_weight = round(
                clamp01(0.4 * score + 0.35 * system_state["metrics"]["rrc"] + 0.25 * system_state["success_composite"]),
                4,
            )
            mapped.append(
                {
                    "idea_title": title[:120],
                    "track": idea.get("track") or idea.get("role") or "product",
                    "system_category": best_cat,
                    "reverse_weight": reverse_weight,
                    "function_affinity": function_key,
                }
            )

        # Aggregate category histogram (system values after reverse pass)
        hist: dict[str, float] = {c: 0.0 for c in cats}
        for row in mapped:
            hist[row["system_category"]] = hist.get(row["system_category"], 0.0) + row[
                "reverse_weight"
            ]
        for c in hist:
            hist[c] = round(hist[c], 4)

        return {
            "principle": "reverse_context_informatics_law",
            "forward_basis": ["system_metrics", "orientation_scores", "selected_function"],
            "mapped": mapped,
            "category_histogram": hist,
            "dominant_category": max(hist, key=hist.get) if hist else cats[0],
            "industry_id": industry_id,
        }

    # ── 5. Reader-assembler → technical tasks ──────────────────────────────

    def _reader_assemble_tasks(
        self,
        *,
        system_state: dict[str, Any],
        analog: dict[str, Any],
        categorical: dict[str, Any],
        opps: list[OpenOpportunity],
        business_text: str,
        industry_id: str,
    ) -> list[TechnicalTask]:
        fn_key = analog.get("selected_function") or "ops_efficiency_map"
        fn = analog.get("function_meta") or self.FUNCTIONS[fn_key]
        dom = categorical.get("dominant_category") or "ops_efficiency"
        brief_clip = (business_text or "")[:100].replace("\n", " ")

        tasks: list[TechnicalTask] = []

        # Primary tech-writing task from improved last version of analysis
        tasks.append(
            TechnicalTask(
                id=_sid("tt", industry_id, fn_key, "primary"),
                title=f"Tech write · {fn.get('title')}",
                language=(
                    f"TASK: Implement function «{fn.get('title')}» for industry `{industry_id}`.\n"
                    f"CONTEXT: Client brief fragment «{brief_clip}…».\n"
                    f"SYSTEM: dominant category `{dom}`, "
                    f"health={system_state['metrics']['health']}, "
                    f"RRC={system_state['metrics']['rrc']}.\n"
                    f"DO NOT: polish methods inside a wrong frame.\n"
                    f"DO: lock function output `{fn.get('out')}`, "
                    f"write acceptance criteria, hand off to SpecsForge recursion.\n"
                    f"OPEN OPP: {(opps[0].title if opps else 'n/a')} "
                    f"(coop={opps[0].coop_score if opps else 0:.2f})."
                ),
                acceptance=[
                    f"Function `{fn_key}` named and justified on property planes",
                    "Reverse-mapped categories present in the memo",
                    "SpecsForge can recurse without inventing scope",
                    "Client-facing language free of pure jargon dump",
                ],
                function_selected=fn_key,
                complexity_gate="max_5_planes; stop method recursion if noise>plasticity",
                specsforge_ready=system_state["metrics"]["health"] >= 0.45,
                reverse_context=[
                    dom,
                    f"histogram={categorical.get('category_histogram')}",
                ],
            )
        )

        # Secondary: consult frame task
        tasks.append(
            TechnicalTask(
                id=_sid("tt", industry_id, "consult", "meta"),
                title="Consult frame · MetaReality constraints",
                language=(
                    f"TASK: Produce MetaReality consultation frame for `{industry_id}`.\n"
                    f"INPUT: orientation scores + memo-convert open opportunities.\n"
                    f"OUTPUT: constraint map + which SKU (Terminal Teammate / Expert / simple offer).\n"
                    f"GATE: no tech-writing package until this frame is accepted."
                ),
                acceptance=[
                    "Constraint map signed or explicitly draft",
                    "One primary SKU recommended",
                    "Must-ask voids listed if coop_score < 0.35",
                ],
                function_selected=fn_key,
                complexity_gate="attribute_substitution_block",
                specsforge_ready=False,
                reverse_context=[dom],
            )
        )

        # Process personalization task
        if system_state.get("system_log_gravity", 0) > 0 or True:
            tasks.append(
                TechnicalTask(
                    id=_sid("tt", industry_id, "process", "personalize"),
                    title="Process personalization from system interactions",
                    language=(
                        "TASK: Personalize process answers using system log gravity + "
                        "category histogram + prior interaction features.\n"
                        "Optimize for *process tasks* (repeatable ops), not one-off essays.\n"
                        f"SYSTEM_LOG_GRAVITY={system_state.get('system_log_gravity')}.\n"
                        f"DECISION_MODE={system_state.get('decision_mode')}."
                    ),
                    acceptance=[
                        "Repeatable process step list (≤7)",
                        "Personalization keys from system state only (no invented CRM)",
                    ],
                    function_selected=fn_key,
                    complexity_gate="dimensionality_max_5",
                    specsforge_ready=True,
                    reverse_context=list((categorical.get("category_histogram") or {}).keys())[:3],
                )
            )

        return tasks

    # ── 6. Personalization ─────────────────────────────────────────────────

    def _personalize(
        self,
        *,
        system_state: dict[str, Any],
        categorical: dict[str, Any],
        tech_tasks: list[TechnicalTask],
        business_text: str,
    ) -> dict[str, Any]:
        gravity = system_state.get("system_log_gravity", 0.0)
        mode = system_state.get("decision_mode") or "scoring"
        dom = categorical.get("dominant_category")
        # Process-task optimization: shorter cycles when gravity high
        cycle = "tight_3_step" if gravity > 0.2 else "standard_5_step"
        tone = "operator" if "ops" in str(dom) else "founder"
        if system_state.get("signals", {}).get("api_cost_pressure"):
            tone = "cost_conscious_creative"

        return {
            "tone": tone,
            "process_cycle": cycle,
            "decision_mode": mode,
            "dominant_category": dom,
            "keys": {
                "industry": system_state.get("industry_id"),
                "health_band": (
                    "high"
                    if system_state["metrics"]["health"] >= 0.7
                    else "mid"
                    if system_state["metrics"]["health"] >= 0.45
                    else "low"
                ),
                "brief_hash": hashlib.sha256(
                    (business_text or "")[:200].encode()
                ).hexdigest()[:12],
            },
            "answer_shape": {
                "lead_with": tech_tasks[0].title if tech_tasks else "function",
                "then": "reverse categories",
                "close_with": "tech task acceptance + SpecsForge gate",
            },
            "optimized_for": "process_tasks",
        }

    # ── Complexity gates ───────────────────────────────────────────────────

    def _apply_complexity_gates(
        self,
        system_state: dict[str, Any],
        analog: dict[str, Any],
        opps: list[OpenOpportunity],
    ) -> list[dict[str, Any]]:
        applied = []
        for p in COMPLEXITY_PRINCIPLES:
            active = True
            reason = p["boundary"]
            if p["id"] == "cooperation_open_opp" and opps:
                active = opps[0].coop_score < 0.35 or True
                reason = f"best_coop={opps[0].coop_score:.2f}; {p['boundary']}"
            if p["id"] == "error_as_signal":
                active = system_state["metrics"]["er"] > 0.4
            if p["id"] == "void_plasticity":
                active = bool(analog.get("method_iteration_blocked")) or system_state[
                    "metrics"
                ]["vvi"] > 0.4
            applied.append(
                {
                    "id": p["id"],
                    "title": p["title"],
                    "rule": p["rule"],
                    "active": active,
                    "boundary": reason,
                    "source": p["source"],
                }
            )
        return applied

    def _engine_architecture_answer(
        self,
        analog: dict[str, Any],
        tech_tasks: list[TechnicalTask],
        system_state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Q: Can the last improved version seed an engine on the same architecture?
        A: Yes — Memo Convert itself is that recursive seed (function + reverse + assemble).
        """
        feasible = (
            bool(analog.get("selected_function"))
            and len(tech_tasks) >= 1
            and system_state["metrics"]["rrc"] >= 0.35
        )
        return {
            "feasible": feasible,
            "architecture": [
                "system_intake",
                "open_opportunity_coop",
                "analog_function_select",
                "reverse_categorical_map",
                "reader_assembler_tech_tasks",
                "personalize_process",
            ],
            "bootstrap_from": "last_improved_tech_task + function_meta + category_histogram",
            "answer_ru": (
                "Да: последняя улучшенная версия tech-task + выбранная функция + "
                "обратный категорийный контекст — достаточный seed, чтобы поднять "
                "движок той же архитектуры (intake→coop→analog→reverse→assemble), "
                "без отдельной БД решений."
            ),
            "next_engine_hook": "SpecsForge recursion consumes technical_tasks[0].language",
        }

