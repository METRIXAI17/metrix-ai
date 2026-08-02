"""
Unique expert base builder — project-specific knowledge pack (not a generic dump).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.config import DATA_DIR


class ExpertBaseBuilder:
    """
    Synthesize a project-bound expert knowledge base:
    frames · playbooks · metrics · anti-patterns · distribution · worker SOPs.
    """

    name = "ExpertBaseBuilder"
    STORE = DATA_DIR / "knowledge_base"

    # World-class knowledge engineering ingredients (condensed operationally)
    LAYERS = (
        "ontology",       # entities & relations
        "epistemology",   # what we know / how we know
        "procedural",     # how-to playbooks
        "criterial",      # success / kill criteria
        "distribution",   # brand / platforms / networks
        "socio_tech",     # human+worker incentives
        "meta",           # self-test & update rules
    )

    def __init__(self) -> None:
        self.STORE.mkdir(parents=True, exist_ok=True)

    def build(
        self,
        *,
        business_text: str,
        domain: str,
        plan: dict[str, Any],
        synthesis: dict[str, Any],
        side: dict[str, Any],
        industry_id: str = "generic",
        project_name: str = "",
        lang: str = "ru",
    ) -> dict[str, Any]:
        pid = hashlib.sha256(
            f"{business_text[:200]}|{domain}|{industry_id}".encode()
        ).hexdigest()[:12]
        name = project_name or f"ExpertBase-{domain}-{pid}"

        ontology = self._ontology(domain, business_text)
        epistemology = {
            "known": (side.get("uncertainty") or {}).get("known", []),
            "unknown": (side.get("uncertainty") or {}).get("unknown", []),
            "assumptions": plan.get("assumptions", []),
            "confidence": plan.get("confidence", 0.5),
            "sources_of_truth": [
                "client brief",
                "side engines (flow/risk/graph)",
                "synthesis methods (analogy/matrix/morph/counterfactual)",
                "pilot metric only after human choice",
            ],
        }
        procedural = self._playbooks(domain, plan, synthesis)
        criterial = self._criteria(domain, side, plan)
        distribution = self._distribution_layer(domain, synthesis)
        socio = self._socio_tech(domain)
        meta = {
            "self_test_hooks": [
                "recompute uncertainty after each human answer",
                "forecast human objection before send",
                "matrix simplification must keep_energy ≥ 0.52",
                "counterfactual pre-patches attached to deliverable",
            ],
            "update_rule": "New fact → re-run synthesis methods affected → bump version",
            "version": "1.0.0",
            "built_at": datetime.now(timezone.utc).isoformat(),
        }

        pack = {
            "id": pid,
            "name": name,
            "domain": domain,
            "industry_id": industry_id,
            "lang": lang,
            "layers": {
                "ontology": ontology,
                "epistemology": epistemology,
                "procedural": procedural,
                "criterial": criterial,
                "distribution": distribution,
                "socio_tech": socio,
                "meta": meta,
            },
            "original_moves": synthesis.get("original_moves", []),
            "panel_widgets": self._panel_widgets(domain, side),
            "code_assembly_hints": self._code_hints(domain),
            "summary": (
                f"Экспертная база «{name}»: {len(self.LAYERS)} слоёв, "
                f"уверенность {epistemology['confidence']:.0%}, "
                f"домен {domain}."
            ),
        }

        path = self.STORE / f"{pid}.json"
        path.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
        pack["stored_path"] = str(path)
        return pack

    def _ontology(self, domain: str, text: str) -> dict[str, Any]:
        if domain == "resource_logistics":
            entities = [
                "source_stream", "fraction", "quality_grade", "route", "hub",
                "processor", "buyer", "settlement", "compliance_doc", "worker",
            ]
            relations = [
                "source_stream-produces->fraction",
                "fraction-graded_as->quality_grade",
                "route-moves->fraction",
                "hub-buffers->fraction",
                "processor-transforms->fraction",
                "buyer-pays_for->fraction",
                "settlement-closes->cash",
                "worker-operates->route|hub",
            ]
        else:
            entities = [
                "client", "problem", "offer", "unit", "channel", "metric",
                "artifact", "worker", "payment", "feedback",
            ]
            relations = [
                "client-has->problem",
                "offer-solves->problem",
                "unit-prices->offer",
                "channel-reaches->client",
                "metric-measures->success",
                "artifact-documents->offer",
                "worker-delivers->artifact",
                "payment-follows->value",
            ]
        return {"entities": entities, "relations": relations, "brief_tokens": len(text.split())}

    def _playbooks(self, domain: str, plan: dict, synthesis: dict) -> list[dict[str, Any]]:
        books = [
            {
                "id": "pb_intake",
                "title": "Intake & clarity",
                "steps": [
                    "Принять бриф 5–20 предложений",
                    "Прогнать uncertainty budget",
                    "Задать ≤4 вопроса / согласовать направления",
                ],
            },
            {
                "id": "pb_assemble",
                "title": "Assembly",
                "steps": [
                    "Собрать expert base",
                    "Сгенерировать control panel widgets",
                    "Выдать code pack hints для Grok Build",
                ],
            },
            {
                "id": "pb_pilot",
                "title": "Pilot",
                "steps": [
                    "Одна метрика, 14–21 день",
                    "Kill-switch из risk lattice",
                    "Отчёт: metric + next / stop",
                ],
            },
        ]
        if domain == "resource_logistics":
            books.insert(
                1,
                {
                    "id": "pb_flow",
                    "title": "Flow ops",
                    "steps": [
                        "Замерить inflow / capacity / leak",
                        "Найти bottleneck (flow engine)",
                        "Не масштабировать маркетинг до фикса bottleneck",
                    ],
                },
            )
        # attach original moves as micro-playbook
        books.append(
            {
                "id": "pb_original",
                "title": "Non-template moves",
                "steps": list(synthesis.get("original_moves") or [])[:5],
            }
        )
        return books

    def _criteria(self, domain: str, side: dict, plan: dict) -> dict[str, Any]:
        risk = side.get("risk_lattice") or {}
        return {
            "success": [
                "Согласованы S1–S4 с человеком",
                "Метрика пилота измерима ≤21 день",
                "Есть артефакт (документ/панель/код-пакет)",
            ],
            "kill": risk.get("kill_switches") or ["Нет оплаты/интереса после 2 итераций артефакта"],
            "hedges": risk.get("hedges") or [],
            "confidence_floor": 0.4,
            "plan_mode": plan.get("mode"),
        }

    def _distribution_layer(self, domain: str, synthesis: dict) -> dict[str, Any]:
        return {
            "brand": {
                "promise": "Инженерия бизнеса: артефакт + метрика, без кот-в-мешке",
                "voice": "спокойный оператор, не инфоцыган",
                "proof": "демо на живой нише + документ консультации",
            },
            "platforms": [
                {"id": "x", "role": "thought leadership + DM funnel"},
                {"id": "telegram", "role": "workers + warm ops"},
                {"id": "site", "role": "conversion surface Global Ru Workers"},
                {"id": "niche_boards", "role": "demand capture by industry"},
            ],
            "networks": [
                {"id": "warm_intros", "role": "highest trust, first revenue"},
                {"id": "partner_wl", "role": "white-label delivery"},
                {"id": "worker_pool", "role": "execution liquidity"},
            ],
            "contrast": (synthesis.get("contrast") or {}).get("positioning_line"),
        }

    def _socio_tech(self, domain: str) -> dict[str, Any]:
        return {
            "worker_incentives": [
                "Оплата за verified milestone, не за «обещание»",
                "Reputation score on-platform",
                "Прозрачный % / фикс — до старта задачи",
            ],
            "client_psychology": [
                "Снижать uncertainty короткими выборами",
                "Показывать demo wow до цены",
                "Дисклеймер: поддержка решений ≠ гарантия прибыли",
            ],
            "anti_patterns": [
                "Честное слово вместо proof of work",
                "Завышенный прайс без демо",
                "Параллельно 5 направлений без метрики",
            ],
        }

    def _panel_widgets(self, domain: str, side: dict) -> list[dict[str, str]]:
        w = [
            {"id": "uncertainty", "title": "Uncertainty budget", "bind": "side.uncertainty"},
            {"id": "risk", "title": "Risk lattice", "bind": "side.risk_lattice"},
            {"id": "plan", "title": "Human plan steps", "bind": "plan.steps"},
            {"id": "moves", "title": "Original moves", "bind": "synthesis.original_moves"},
        ]
        if domain == "resource_logistics":
            w.insert(0, {"id": "flow", "title": "Flow balance", "bind": "side.flow_balance"})
            w.insert(1, {"id": "graph", "title": "Critical path", "bind": "side.graph_reach"})
        return w

    def _code_hints(self, domain: str) -> dict[str, Any]:
        return {
            "target": "Grok Build / local stack",
            "packages": [
                "expert_base.json",
                "control_panel (widgets)",
                "pilot_checklist.md",
                "distribution_plan.json",
            ],
            "components": [
                "intake_form",
                "planner_wizard",
                "metric_dashboard",
                "worker_task_board",
                "payout_escrow_stub",
            ],
            "note": "Сборка из согласованных компонентов; без лишней генерации «всего интернета».",
        }

    def load(self, pack_id: str) -> dict[str, Any] | None:
        path = self.STORE / f"{pack_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
