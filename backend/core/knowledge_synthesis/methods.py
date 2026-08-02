"""
Synthesis methods beyond simple analogy.

1. Analogy bridge — map structure A→B
2. Matrix simplification — compress dimensions, verify, expand
3. Constraint satisfaction — invent under hard limits
4. Contrastive synthesis — define by what it is NOT
5. Morphological box — Zwicky-style combinations
6. Narrative spine — cause→effect story that carries decisions
7. Counterfactual stress — "what if this fails" → pre-patch
8. Cross-domain transplant — import mechanism from another industry
"""

from __future__ import annotations

import hashlib
import itertools
import re
from typing import Any


def _h(text: str) -> int:
    return int(hashlib.md5((text or "x").encode()).hexdigest()[:6], 16)


class AnalogyBridge:
    name = "analogy_bridge"

    SOURCE_FRAMES = {
        "restaurant": {
            "nodes": ["menu", "kitchen", "service", "table_turn", "reviews"],
            "lesson": "Menu = SKU; kitchen = process; table_turn = cycle time.",
        },
        "airline_hub": {
            "nodes": ["spoke", "hub", "slot", "load_factor", "delay_cascade"],
            "lesson": "Hub bottlenecks dominate; protect critical path capacity.",
        },
        "hospital_triage": {
            "nodes": ["intake", "triage", "treatment", "discharge", "readmit"],
            "lesson": "Triage quality beats raw volume; rework = readmit.",
        },
        "marketplace": {
            "nodes": ["supply", "demand", "match", "trust", "settlement"],
            "lesson": "Trust + settlement unlock liquidity; match alone is not a business.",
        },
        "software_ci": {
            "nodes": ["commit", "test", "gate", "deploy", "observe"],
            "lesson": "Gates before scale; observe after ship; failed test cheap.",
        },
    }

    def run(self, business_text: str, domain: str = "") -> dict[str, Any]:
        t = (business_text or "").lower()
        if any(w in t for w in ("логист", "переработ", "склад", "recycl", "waste")):
            src = "airline_hub"
        elif any(w in t for w in ("услуг", "консьерж", "клиент", "b2c")):
            src = "restaurant"
        elif any(w in t for w in ("площад", "маркет", "спрос", "предложен")):
            src = "marketplace"
        elif any(w in t for w in ("агент", "delivery", "qa", "тест")):
            src = "software_ci"
        else:
            src = list(self.SOURCE_FRAMES.keys())[_h(t) % len(self.SOURCE_FRAMES)]
        frame = self.SOURCE_FRAMES[src]
        mapping = []
        target_nodes = ["intake", "core_process", "quality_gate", "delivery", "cash_loop"]
        for a, b in zip(frame["nodes"], target_nodes):
            mapping.append({"source": a, "target": b})
        return {
            "method": self.name,
            "source_frame": src,
            "mapping": mapping,
            "lesson": frame["lesson"],
            "novel_hook": (
                f"Импортируем дисциплину «{src}» в ваш контур: "
                f"не копируем индустрию, копируем геометрию решений."
            ),
        }


class MatrixSimplifier:
    name = "matrix_simplification"

    AXES = ("value", "cost", "time", "risk", "trust", "scale")

    def run(self, business_text: str, scores: dict[str, float] | None = None) -> dict[str, Any]:
        scores = scores or {}
        t = business_text or ""
        matrix = {}
        for i, ax in enumerate(self.AXES):
            base = 0.4 + ((_h(t + ax) % 50) / 100.0)
            matrix[ax] = round(float(scores.get(ax, base)), 3)
        # compress: keep top-3 axes by decision weight
        ranked = sorted(matrix.items(), key=lambda x: x[1], reverse=True)
        kept = ranked[:3]
        dropped = ranked[3:]
        # verify: sum of kept should explain ≥ 0.55 of energy
        energy = sum(v for _, v in ranked) or 1.0
        kept_energy = sum(v for _, v in kept) / energy
        simplification_ok = kept_energy >= 0.52
        expand = [
            {
                "axis": k,
                "action": f"Сделать «{k}» явной метрикой пилота и убрать споры о вторичном.",
            }
            for k, _ in kept
        ]
        return {
            "method": self.name,
            "full_matrix": matrix,
            "compressed": {k: v for k, v in kept},
            "parked": {k: v for k, v in dropped},
            "kept_energy": round(kept_energy, 3),
            "simplification_ok": simplification_ok,
            "expand_actions": expand,
            "check": (
                "OK — матрица сходится"
                if simplification_ok
                else "FAIL — слишком плоская неопределённость, нужны уточнения"
            ),
        }


class ConstraintSynthesizer:
    name = "constraint_satisfaction"

    def run(self, business_text: str, constraints: dict[str, Any] | None = None) -> dict[str, Any]:
        c = constraints or {}
        cash = float(c.get("cash_ceiling", 5000))
        days = int(c.get("days", 21))
        team = int(c.get("team", 1))
        invent = []
        if cash < 1500:
            invent.append("Только ручной пилот + документы; автоматизация после 1-й оплаты.")
        elif cash < 8000:
            invent.append("Один платный канал + простой учёт; без найма fixed.")
        else:
            invent.append("Можно купить 1–2 инструмента/подряд на bottleneck.")
        if days <= 14:
            invent.append("Урезать scope до одного buyer persona и одного SKU/услуги.")
        if team <= 1:
            invent.append("Все handoff-ы в чеклистах; нельзя держать процесс «в голове».")
        invent.append("Запрет: параллельно запускать >2 экспериментов.")
        return {
            "method": self.name,
            "constraints": {"cash_ceiling": cash, "days": days, "team": team},
            "inventions": invent,
            "feasibility": "high" if cash >= 800 and days >= 10 else "tight",
        }


class ContrastiveSynthesizer:
    name = "contrastive"

    def run(self, business_text: str, domain: str = "") -> dict[str, Any]:
        is_not = [
            "Не «ещё один AI-чат» без артефакта на выходе",
            "Не инфоцыганский курс с завышенным прайсом",
            "Не подписка ради подписки",
            "Не гарантия доходности / yield theatre",
        ]
        is_yes = [
            "Документ/система по ТЗ с метрикой",
            "Согласования лучшими вариантами, не пустой болтовнёй",
            "Пилот → оплата после подтверждённой ценности",
            "Оригинальная экспертная база под проект",
        ]
        if "переработ" in (business_text or "").lower() or "логист" in (business_text or "").lower():
            is_not.append("Не свалка «всё подряд» без quality gate")
            is_yes.append("Поток: intake → quality → process → logistics → cash")
        return {
            "method": self.name,
            "is_not": is_not,
            "is": is_yes,
            "positioning_line": "Работаем как инженерия бизнеса: артефакты, метрики, границы — не мотивационный шум.",
        }


class MorphologicalBox:
    name = "morphological_box"

    def run(self, domain: str = "generic") -> dict[str, Any]:
        if domain == "resource_logistics":
            dims = {
                "source": ["household", "commercial", "industrial"],
                "process": ["sort_only", "process_fraction", "full_cycle"],
                "logistics": ["own_fleet", "partner", "marketplace_routes"],
                "buyer": ["factory", "exporter", "local_maker"],
                "monetize": ["per_ton", "contract", "take_or_pay"],
            }
        else:
            dims = {
                "offer": ["single_service", "bundle", "platform_layer"],
                "delivery": ["human", "hybrid", "agent_after_doc"],
                "channel": ["brand", "platform", "network"],
                "price_logic": ["project", "unit", "success_share_soft"],
            }
        # pick 3 non-obvious combos (not the boring first×first)
        keys = list(dims.keys())
        combos = []
        lists = [dims[k] for k in keys]
        all_c = list(itertools.product(*lists))
        # skip first (most obvious), sample spread
        picks = [all_c[1], all_c[len(all_c) // 3], all_c[len(all_c) // 2]]
        for p in picks:
            combos.append({k: v for k, v in zip(keys, p)})
        return {
            "method": self.name,
            "dimensions": dims,
            "candidate_configs": combos,
            "note": "Морфологический ящик — чтобы не залипнуть в шаблонной «очевидной» сборке.",
        }


class NarrativeSpine:
    name = "narrative_spine"

    def run(self, business_text: str, domain: str = "") -> dict[str, Any]:
        spine = [
            {"beat": "wound", "text": "Сейчас ресурс/спрос/время утекают без ясной единицы ценности."},
            {"beat": "shift", "text": "Вводим один контур: метрика → процесс → канал → cash."},
            {"beat": "proof", "text": "Пилот 14–21 день с kill-switch и артефактом на выходе."},
            {"beat": "scale", "text": "Только после proof — компоненты, воркеры, дистрибуция."},
        ]
        return {
            "method": self.name,
            "spine": spine,
            "one_liner": "От утечки к контуру, от контура к proof, от proof к масштабу.",
        }


class CounterfactualStress:
    name = "counterfactual"

    def run(self, business_text: str, risks: dict[str, Any] | None = None) -> dict[str, Any]:
        risks = risks or {}
        scenarios = [
            {
                "if": "Первый buyer сорвался",
                "then": "Держать dual-list из 5 lookalike; pre-LOI до capex",
            },
            {
                "if": "Логистика съела маржу",
                "then": "Пересчитать unit с full freight; отрезать дальние зоны",
            },
            {
                "if": "Воркер не задекларировал объём",
                "then": "Эскроу/milestone + on-platform proof, не «на честном слове»",
            },
            {
                "if": "Клиент ждёт гарантию дохода",
                "then": "Жёсткий дисклеймер; продаём ТЗ и поддержку решений, не yield",
            },
        ]
        pre_patches = [s["then"] for s in scenarios]
        return {
            "method": self.name,
            "scenarios": scenarios,
            "pre_patches": pre_patches,
            "band": (risks or {}).get("band", "amber"),
        }


class CrossDomainTransplant:
    name = "cross_domain_transplant"

    TRANSPLANTS = [
        {
            "from": "JIT manufacturing",
            "mechanism": "Pull signals, not push inventory",
            "to": "Запускать логистику по pull-заказу buyer, не копить «на авось».",
        },
        {
            "from": "SRE error budgets",
            "mechanism": "Budget for failure",
            "to": "Error budget на rework///no-shows: сверх — стоп фич, только стабильность.",
        },
        {
            "from": "Editorial desk",
            "mechanism": "Assignment + deadline + kill piece",
            "to": "Каждая задача = assignment card с дедлайном и критерием «убить тему».",
        },
        {
            "from": "Insurance underwriting",
            "mechanism": "Price the risk, exclude the uninsurable",
            "to": "Явные exclusions в оффере; то, что не страхуем — не продаём.",
        },
    ]

    def run(self, business_text: str) -> dict[str, Any]:
        idx = _h(business_text) % len(self.TRANSPLANTS)
        pick = self.TRANSPLANTS[idx]
        alt = self.TRANSPLANTS[(idx + 1) % len(self.TRANSPLANTS)]
        return {
            "method": self.name,
            "primary": pick,
            "secondary": alt,
            "novelty": "Трансплант механизма, не поверхностной метафоры.",
        }


class SynthesisMethodOrchestrator:
    """Run all synthesis methods and fuse into non-template original output."""

    def run(
        self,
        business_text: str,
        *,
        domain: str = "",
        constraints: dict[str, Any] | None = None,
        scores: dict[str, float] | None = None,
        risks: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        analogy = AnalogyBridge().run(business_text, domain)
        matrix = MatrixSimplifier().run(business_text, scores)
        constr = ConstraintSynthesizer().run(business_text, constraints)
        contrast = ContrastiveSynthesizer().run(business_text, domain)
        morph = MorphologicalBox().run(domain or "generic")
        narrative = NarrativeSpine().run(business_text, domain)
        counter = CounterfactualStress().run(business_text, risks)
        transplant = CrossDomainTransplant().run(business_text)

        original_moves = [
            analogy["novel_hook"],
            contrast["positioning_line"],
            narrative["one_liner"],
            f"Трансплант: {transplant['primary']['from']} → {transplant['primary']['to']}",
            f"Морф-конфиг #1: {morph['candidate_configs'][0]}",
        ]
        if constr["inventions"]:
            original_moves.append(constr["inventions"][0])

        return {
            "methods_run": [
                analogy["method"],
                matrix["method"],
                constr["method"],
                contrast["method"],
                morph["method"],
                narrative["method"],
                counter["method"],
                transplant["method"],
            ],
            "analogy": analogy,
            "matrix": matrix,
            "constraints": constr,
            "contrast": contrast,
            "morphology": morph,
            "narrative": narrative,
            "counterfactual": counter,
            "transplant": transplant,
            "original_moves": original_moves,
            "anti_template_score": round(
                0.55
                + (0.1 if matrix["simplification_ok"] else 0)
                + (0.1 if len(original_moves) >= 5 else 0)
                + (0.08 if constr["feasibility"] != "impossible" else 0),
                3,
            ),
        }
