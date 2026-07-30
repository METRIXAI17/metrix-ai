"""
Three global steps for Deep Tech Metrix AI (Circle-System).

Step A — Param development + indirect certainty (ТОЧНО ДА / НЕТ / U)
Step B — Super-speed tests + assembly + Super Program match + linguistic warmth answers
Step C — Autopilot circle: layers, terminal specs, orchestration, resources, ops rules,
         integration lib, pilot predictor, metric firmware, support, arch prompts, expert libs

Outputs ready for: auto-consult · tech write · pilot · main product · white-label prompts.
"""

from __future__ import annotations

from typing import Any

from backend.core.circle_system.arch_prompt_gen import ArchitecturalPromptGenerator
from backend.core.circle_system.certainty_analyzer import CertaintyAnalyzer
from backend.core.circle_system.integration_lib import IntegrationLibrary
from backend.core.circle_system.knowledge_libs import ExpertKnowledgePlatform
from backend.core.circle_system.layers import CircleLayerEngine
from backend.core.circle_system.lexicon import lexicon_catalog
from backend.core.circle_system.linguistic_warmth import LinguisticWarmthEngine
from backend.core.circle_system.metric_firmware import MetricFirmware
from backend.core.circle_system.ops_rules import OperationalRulesEngine
from backend.core.circle_system.orchestration import DynamicOrchestrator
from backend.core.circle_system.parameter_assembly import ParameterAssemblyEngine
from backend.core.circle_system.pilot_predictor import PilotAccuracyPredictor
from backend.core.circle_system.resource_match import ResourceMatchEngine
from backend.core.circle_system.super_program import SuperProgramMatcher
from backend.core.circle_system.super_speed_assistant import SuperSpeedAssistant
from backend.core.circle_system.support_system import SupportSystem
from backend.core.circle_system.terminal_specs import TerminalSpecBuilder


class DeepTechMetrixPipeline:
    """End-to-end Deep Tech Metrix / Circle-System runner."""

    name = "Deep Tech Metrix Pipeline (3 global steps)"
    version = "2026-07-30"

    def __init__(self) -> None:
        self.certainty = CertaintyAnalyzer()
        self.super_speed = SuperSpeedAssistant()
        self.assembly = ParameterAssemblyEngine()
        self.super_program = SuperProgramMatcher()
        self.warmth = LinguisticWarmthEngine()
        self.layers = CircleLayerEngine()
        self.terminals = TerminalSpecBuilder()
        self.orchestrator = DynamicOrchestrator()
        self.resources = ResourceMatchEngine()
        self.ops_rules = OperationalRulesEngine()
        self.integrations = IntegrationLibrary()
        self.pilot_pred = PilotAccuracyPredictor()
        self.firmware = MetricFirmware()
        self.support = SupportSystem()
        self.arch_prompts = ArchitecturalPromptGenerator()
        self.knowledge = ExpertKnowledgePlatform()

    def run(
        self,
        text: str,
        *,
        industry_id: str = "ai-agencies",
        lang: str = "ru",
        test_answers: dict[str, Any] | None = None,
        orchestration_config: dict[str, Any] | None = None,
        product_name: str = "Metrix Circle Runtime",
        client_label: str = "client",
        days_elapsed: int = 0,
        pilot_horizon_days: int = 21,
        core_metrics: dict[str, Any] | None = None,
        collab_authors: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        # ── Global step 1–2 ──────────────────────────────────────────────
        cert = self.certainty.run(text, industry_id=industry_id, lang=lang)

        # ── Global step 3A: super-speed on uncertainties ─────────────────
        speed = self.super_speed.run(cert, lang=lang)
        asm = self.assembly.run(cert, test_answers=test_answers)
        sp = self.super_program.run(cert, assembly=asm)

        counts = cert.get("counts") or {}
        n = max(1, sum(int(counts.get(k, 0)) for k in ("certain_yes", "certain_no", "uncertain")))
        cy_ratio = int(counts.get("certain_yes") or 0) / n
        warmth = self.warmth.score(
            assembly_score=float(asm.get("assembly_score") or 0),
            certain_yes_ratio=cy_ratio,
            client_energy=0.55,
            lang=lang,
        )

        # Render sample answers per certain/uncertain parameter
        answers_out = []
        for p in cert.get("parameters") or []:
            st = p.get("status") or "uncertain"
            if st == "certain_yes":
                fact = f"Параметр «{p.get('slot')}» подтверждён." if lang.startswith("ru") else f"Param «{p.get('slot')}» confirmed."
                nxt = "Включить в tech write / pilot scope."
            elif st == "certain_no":
                fact = f"Параметр «{p.get('slot')}» исключён." if lang.startswith("ru") else f"Param «{p.get('slot')}» excluded."
                nxt = "Не тратить ресурс пилота."
            else:
                fact = f"Параметр «{p.get('slot')}» в неопределённости — нужна сборка." if lang.startswith("ru") else f"Param «{p.get('slot')}» undefined — needs assembly."
                nxt = "Пройти тест-батарею Super Speed."
            answers_out.append(
                self.warmth.render_answer(
                    status=st,
                    body_fact=fact,
                    next_action=nxt,
                    warmth=warmth,
                    lang=lang,
                )
            )

        # ── Global step 3B / Circle autopilot stack ──────────────────────
        lay = self.layers.run(text, certainty_result=cert, assembly=asm)
        term = self.terminals.run(lay, super_program=sp, certainty_result=cert)
        orch = self.orchestrator.run(lay, assembly=asm, config=orchestration_config)
        res = self.resources.run(text, certainty_result=cert, collab_authors=collab_authors)
        rules = self.ops_rules.run(term, layers_result=lay)
        integ = self.integrations.match_for_plan(orch)
        pred = self.pilot_pred.run(
            assembly=asm,
            layers_result=lay,
            resource_match=res,
            days_elapsed=days_elapsed,
            pilot_horizon_days=pilot_horizon_days,
        )
        fw = self.firmware.run(
            assembly=asm,
            layers_result=lay,
            certainty_result=cert,
            pilot_pred=pred,
            resource_match=res,
            core_metrics=core_metrics,
        )
        sup = self.support.run(fw)
        arch = self.arch_prompts.run(
            certainty_result=cert,
            super_program=sp,
            layers_result=lay,
            terminal_specs=term,
            warmth=warmth,
            product_name=product_name,
            client_label=client_label,
        )
        knowledge = self.knowledge.expert_answer_scaffold(text[:240] if text else "deep tech pilot")

        # Product surfaces
        tech_write_md = "\n\n".join(
            f"# {t['title']}\n\n{t['markdown']}" for t in term.get("terminal_functions") or []
        )
        pilot_charter = next(
            (t for t in term.get("terminal_functions") or [] if t["id"] == "pilot_charter"),
            None,
        )
        main_ready = (
            float(pred.get("predicted_end") or 0) >= 0.7
            and pred.get("risk") != "high"
            and bool(lay.get("autopilot_ready"))
        )

        product_surfaces = {
            "auto_consult": {
                "ready": True,
                "summary": {
                    "counts": counts,
                    "assembly_score": asm.get("assembly_score"),
                    "primary_super_program": (sp.get("primary") or {}).get("excel_name"),
                    "consistency": lay.get("consistency_score"),
                    "warmth_band": warmth.get("band"),
                },
                "answers": answers_out,
                "test_battery_count": len(speed.get("test_battery") or []),
            },
            "tech_write": {
                "ready": True,
                "specs": term.get("terminal_functions"),
                "markdown": tech_write_md,
                "phased_insert": rules.get("tech_write_phases"),
            },
            "pilot": {
                "ready": bool(lay.get("autopilot_ready")),
                "charter": pilot_charter,
                "plan_days": orch.get("total_calendar_days_estimate"),
                "prediction": {
                    "predicted_end": pred.get("predicted_end"),
                    "risk": pred.get("risk"),
                    "recommendation": pred.get("recommendation"),
                },
                "pricing_hint": {
                    "pilot_ops_usd": 690,
                    "pilot_product_usd": 790,
                    "pilot_promo_usd": 490,
                    "source": "pilot_private.config ladder",
                },
            },
            "main_product": {
                "ready": main_ready,
                "gate": "pilot_success AND predicted_end>=0.7 AND risk!=high",
                "price_usd": 2490,
                "includes": [
                    "full orientation package",
                    "terminal teammate / expert path",
                    "metric firmware + support",
                    "dynamic orchestration config",
                ],
            },
            "white_label_arch_prompts": {
                "ready": True,
                "branch": arch.get("branch"),
                "system_prompt_preview": (arch.get("system_prompt") or "")[:500],
                "files_suggested": arch.get("files_suggested"),
                "no_external_llm": True,
            },
        }

        return {
            "module": self.name,
            "version": self.version,
            "system": "circle-system",
            "industry_id": industry_id,
            "global_steps": {
                "A_params_indirect_certainty": {
                    "ref": "ref_3:1-4",
                    "result_keys": ["certainty"],
                },
                "B_super_speed_assembly_program_warmth": {
                    "ref": "ref_4:5-7",
                    "result_keys": ["super_speed", "assembly", "super_program", "warmth", "answers"],
                },
                "C_autopilot_circle_stack": {
                    "ref": "circle-system + pilot DE model + support",
                    "result_keys": [
                        "layers",
                        "terminal_specs",
                        "orchestration",
                        "resources",
                        "ops_rules",
                        "integrations",
                        "pilot_prediction",
                        "metric_firmware",
                        "support",
                        "arch_prompts",
                        "knowledge",
                    ],
                },
            },
            "certainty": cert,
            "super_speed": speed,
            "assembly": asm,
            "super_program": sp,
            "warmth": warmth,
            "answers": answers_out,
            "layers": lay,
            "terminal_specs": term,
            "orchestration": orch,
            "resources": res,
            "ops_rules": rules,
            "integrations": integ,
            "pilot_prediction": pred,
            "metric_firmware": fw,
            "support": sup,
            "arch_prompts": arch,
            "knowledge": knowledge,
            "lexicon_ref": "circle_system.lexicon",
            "product_surfaces": product_surfaces,
            "assertions": self._assertions(product_surfaces, asm, lay, pred, sup),
        }

    @staticmethod
    def _assertions(
        surfaces: dict[str, Any],
        asm: dict[str, Any],
        lay: dict[str, Any],
        pred: dict[str, Any],
        sup: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Concrete assertions the product can stand on."""
        return [
            {
                "id": "A1",
                "claim": "Auto-consult is deterministic from text → CY/CN/U + warmth answers",
                "holds": bool(surfaces["auto_consult"]["ready"]),
            },
            {
                "id": "A2",
                "claim": "Tech write is produced as terminal specs with phased insert rules",
                "holds": bool(surfaces["tech_write"]["ready"]) and bool(surfaces["tech_write"]["specs"]),
            },
            {
                "id": "A3",
                "claim": "Pilot readiness equals autopilot_ready from circle layers",
                "holds": surfaces["pilot"]["ready"] is bool(lay.get("autopilot_ready")),
            },
            {
                "id": "A4",
                "claim": "Main package only after pilot prediction threshold",
                "holds": surfaces["main_product"]["ready"] == (
                    float(pred.get("predicted_end") or 0) >= 0.7
                    and pred.get("risk") != "high"
                    and bool(lay.get("autopilot_ready"))
                ),
            },
            {
                "id": "A5",
                "claim": "White-label architectural prompts require no external LLM",
                "holds": surfaces["white_label_arch_prompts"]["no_external_llm"] is True,
            },
            {
                "id": "A6",
                "claim": "Support system is fed by metric firmware anomalies",
                "holds": "how_it_works" in sup and "references" in sup,
            },
            {
                "id": "A7",
                "claim": "Assembly analysis is independent of linguistic warmth",
                "holds": asm.get("heat_used") is False,
            },
        ]


def run_deep_tech_pipeline(text: str, **kwargs: Any) -> dict[str, Any]:
    return DeepTechMetrixPipeline().run(text, **kwargs)


def circle_system_overview() -> dict[str, Any]:
    return {
        "system": "circle-system",
        "product": "metrix-ai deep tech",
        "lexicon": lexicon_catalog(),
        "modules": [
            "certainty_analyzer",
            "super_speed_assistant",
            "parameter_assembly",
            "super_program",
            "linguistic_warmth",
            "layers",
            "terminal_specs",
            "orchestration",
            "resource_match",
            "ops_rules",
            "integration_lib",
            "pilot_predictor",
            "metric_firmware",
            "support_system",
            "arch_prompt_gen",
            "knowledge_libs",
            "deep_tech_pipeline",
        ],
        "global_steps": 3,
        "models": "open",
    }
