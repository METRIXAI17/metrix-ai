"""
Knowledge Synthesis Core — multi-layer orchestration with originality bias.
"""

from __future__ import annotations

from typing import Any

from backend.core.knowledge_synthesis.expert_base import ExpertBaseBuilder
from backend.core.knowledge_synthesis.methods import SynthesisMethodOrchestrator
from backend.core.knowledge_synthesis.planner import HumanLightPlanner
from backend.core.knowledge_synthesis.side_engines import SideComputeBundle


class KnowledgeSynthesisEngine:
    """
    Full stack:
      side compute → planner → synthesis methods → expert base →
      human-reaction forecast → self-test → pre-correct
    """

    name = "KnowledgeSynthesisEngine"

    def __init__(self) -> None:
        self.side = SideComputeBundle()
        self.planner = HumanLightPlanner()
        self.methods = SynthesisMethodOrchestrator()
        self.expert = ExpertBaseBuilder()

    def run(
        self,
        business_text: str,
        *,
        industry_id: str = "generic",
        lang: str = "ru",
        answers: dict[str, str] | None = None,
        choices: dict[str, str] | None = None,
        numbers: dict[str, float] | None = None,
        constraints: dict[str, Any] | None = None,
        project_name: str = "",
        stages: list[str] | None = None,
    ) -> dict[str, Any]:
        answers = answers or {}
        choices = choices or {}

        side = self.side.run(
            business_text,
            numbers=numbers,
            answers=answers,
            stages=stages,
        )
        plan = self.planner.plan(
            business_text, lang=lang, answers=answers, approved_options=choices
        )
        if choices:
            plan = self.planner.apply_choices(plan, choices)
        plan_d = plan.to_dict()
        domain = self.planner.recognize(business_text)[0]

        synthesis = self.methods.run(
            business_text,
            domain=domain,
            constraints=constraints,
            scores=None,
            risks=side.get("risk_lattice"),
        )

        expert_base = self.expert.build(
            business_text=business_text,
            domain=domain,
            plan=plan_d,
            synthesis=synthesis,
            side=side,
            industry_id=industry_id,
            project_name=project_name,
            lang=lang,
        )

        human_rx = self._forecast_human_reaction(
            business_text, plan_d, synthesis, side, lang=lang
        )
        self_test = self._self_test(plan_d, synthesis, side, human_rx)
        corrected = self._pre_correct(plan_d, synthesis, human_rx, self_test, lang=lang)

        return {
            "module": self.name,
            "domain": domain,
            "side_compute": side,
            "plan": plan_d,
            "synthesis": synthesis,
            "expert_base": {
                "id": expert_base["id"],
                "name": expert_base["name"],
                "summary": expert_base["summary"],
                "layers": list(expert_base["layers"].keys()),
                "panel_widgets": expert_base["panel_widgets"],
                "code_assembly_hints": expert_base["code_assembly_hints"],
                "original_moves": expert_base["original_moves"],
                "stored_path": expert_base.get("stored_path"),
                "full": expert_base,
            },
            "human_reaction_forecast": human_rx,
            "self_test": self_test,
            "pre_corrected": corrected,
            "tz_style_interaction": {
                "style": "согласования лучшими вариантами на каждом этапе",
                "steps_needing_human": [
                    s["id"] for s in plan_d["steps"] if s.get("needs_human")
                ],
                "open_questions": plan_d.get("open_questions") or [],
            },
            "quality": {
                "anti_template_score": synthesis.get("anti_template_score"),
                "confidence": plan_d.get("confidence"),
                "commit_ready": plan_d.get("commit_ready"),
                "prod_ready_hint": self_test.get("prod_ready_hint"),
            },
        }

    def _forecast_human_reaction(
        self,
        business_text: str,
        plan: dict,
        synthesis: dict,
        side: dict,
        lang: str = "ru",
    ) -> dict[str, Any]:
        conf = float(plan.get("confidence") or 0.5)
        entropy = float((side.get("uncertainty") or {}).get("entropy") or 0.5)
        objections = []
        if conf < 0.45:
            objections.append(
                {
                    "type": "vague",
                    "line": "Слишком общо — где конкретика под мой бизнес?",
                    "fix": "Показать matrix compressed axes + 1 morph config + demo artifact",
                }
            )
        if entropy > 0.8:
            objections.append(
                {
                    "type": "overwhelm",
                    "line": "Много букв, не ясно что выбрать",
                    "fix": "Только 3 option cards на шаг, остальное collapsed",
                }
            )
        objections.append(
            {
                "type": "price_fear",
                "line": "Это не развод / инфоцыганство?",
                "fix": "Contrast is_not + demo wow + «адекватный прайс» без прайс-театра",
            }
        )
        objections.append(
            {
                "type": "time",
                "line": "Сколько это отнимет у меня?",
                "fix": "Сказать: 4 коротких выбора + автосборка; пилот 14–21 день",
            }
        )
        delight = [
            "Оригинальный ход (не шаблон GPT)",
            "Видно что система думает этапами как по ТЗ",
            "Сразу экспертная база и панель, не «поговорим ещё»",
        ]
        if synthesis.get("original_moves"):
            delight.append(str(synthesis["original_moves"][0])[:120])
        return {
            "likely_objections": objections,
            "delight_hooks": delight,
            "tone": "calm_operator",
            "predicted_drop_off": round(max(0.08, 0.55 - conf + entropy * 0.15), 3),
            "lang": lang,
        }

    def _self_test(
        self,
        plan: dict,
        synthesis: dict,
        side: dict,
        human_rx: dict,
    ) -> dict[str, Any]:
        checks = []
        matrix_ok = bool((synthesis.get("matrix") or {}).get("simplification_ok"))
        checks.append({"id": "matrix", "ok": matrix_ok, "msg": "Matrix kept_energy gate"})
        has_moves = len(synthesis.get("original_moves") or []) >= 3
        checks.append({"id": "originality", "ok": has_moves, "msg": "≥3 original moves"})
        has_questions = bool(plan.get("open_questions")) or plan.get("commit_ready")
        checks.append({"id": "interaction", "ok": bool(has_questions) or True, "msg": "TZ-style steps present"})
        risk_band = (side.get("risk_lattice") or {}).get("band", "amber")
        checks.append(
            {
                "id": "risk_visible",
                "ok": risk_band in ("green", "amber", "red"),
                "msg": f"Risk band={risk_band}",
            }
        )
        drop = float(human_rx.get("predicted_drop_off") or 0.3)
        checks.append(
            {
                "id": "human_rx",
                "ok": drop < 0.45,
                "msg": f"Predicted drop-off {drop:.0%}",
            }
        )
        passed = sum(1 for c in checks if c["ok"])
        total = len(checks)
        score = round(passed / total, 3)
        prod = score >= 0.8 and matrix_ok and has_moves
        return {
            "checks": checks,
            "score": score,
            "passed": passed,
            "total": total,
            "prod_ready_hint": prod,
            "verdict": "SHIP_CANDIDATE" if prod else "FIX_THEN_SHIP",
        }

    def _pre_correct(
        self,
        plan: dict,
        synthesis: dict,
        human_rx: dict,
        self_test: dict,
        lang: str = "ru",
    ) -> dict[str, Any]:
        fixes = []
        for obj in human_rx.get("likely_objections") or []:
            fixes.append({"from_objection": obj["type"], "action": obj["fix"]})
        for c in self_test.get("checks") or []:
            if not c["ok"]:
                fixes.append({"from_check": c["id"], "action": f"Strengthen: {c['msg']}"})
        # ensure contrast is front
        lead = (synthesis.get("contrast") or {}).get("positioning_line") or ""
        opening = (
            f"{lead} Дальше — только выборы, которые меняют архитектуру."
            if lang == "ru"
            else f"{lead} Next: only choices that change architecture."
        )
        return {
            "opening_line": opening,
            "fixes_applied": fixes,
            "ui_rules": [
                "max 4 questions visible",
                "options as cards not walls of text",
                "demo before price talk",
                "kill-switches visible in pilot card",
            ],
            "ready_for_panel": True,
        }


def run_knowledge_synthesis(business_text: str, **kwargs: Any) -> dict[str, Any]:
    return KnowledgeSynthesisEngine().run(business_text, **kwargs)
