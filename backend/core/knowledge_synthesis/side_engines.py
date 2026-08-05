"""Side computation engines for analytics and decisions (not template text)."""

from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass, field
from typing import Any


def _seed(text: str) -> int:
    return int(hashlib.sha256((text or "x").encode("utf-8")).hexdigest()[:8], 16)


@dataclass
class FlowBalanceResult:
    """Conservation / bottleneck model for resource→logistics chains."""

    inflow: float
    capacity: float
    leak: float
    throughput: float
    bottleneck: str
    utilization: float
    surplus_or_deficit: float
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class FlowBalanceEngine:
    """Physics-style flow: min(inflow*(1-leak), capacity)."""

    name = "FlowBalanceEngine"

    def run(
        self,
        *,
        inflow: float = 100.0,
        capacity: float = 80.0,
        leak_rate: float = 0.12,
        node_label: str = "hub",
    ) -> FlowBalanceResult:
        leak = max(0.0, min(0.85, float(leak_rate)))
        net = float(inflow) * (1.0 - leak)
        thr = min(net, float(capacity))
        util = thr / float(capacity) if capacity > 0 else 0.0
        gap = net - float(capacity)
        if util >= 0.92:
            rec = f"Expand capacity at {node_label} before marketing spend."
            bn = "capacity"
        elif leak > 0.2:
            rec = f"Plug leaks first ({leak:.0%}) — cheap margin before new volume."
            bn = "leak"
        elif gap > 0:
            rec = f"Surplus {gap:.1f} units — open secondary outlet or storage."
            bn = "outlet"
        else:
            rec = f"Inflow limited — source contracts or quality of intake at {node_label}."
            bn = "inflow"
        return FlowBalanceResult(
            inflow=float(inflow),
            capacity=float(capacity),
            leak=leak,
            throughput=round(thr, 3),
            bottleneck=bn,
            utilization=round(util, 4),
            surplus_or_deficit=round(gap, 3),
            recommendation=rec,
        )


@dataclass
class RiskLatticeResult:
    dimensions: dict[str, float]
    composite: float
    band: str
    kill_switches: list[str]
    hedges: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RiskLatticeEngine:
    """Multi-axis risk composite with kill-switches (decision support, not trading)."""

    name = "RiskLatticeEngine"
    AXES = ("ops", "cash", "compliance", "demand", "partner", "tech")

    def run(self, scores: dict[str, float] | None = None, context: str = "") -> RiskLatticeResult:
        s = scores or {}
        dims: dict[str, float] = {}
        base = (_seed(context) % 40) / 100.0 + 0.25
        for i, ax in enumerate(self.AXES):
            raw = float(s.get(ax, base + (i * 0.03) % 0.2))
            dims[ax] = round(max(0.05, min(0.95, raw)), 3)
        # higher score = higher risk pressure
        composite = round(sum(dims.values()) / len(dims), 4)
        if composite >= 0.72:
            band = "red"
        elif composite >= 0.48:
            band = "amber"
        else:
            band = "green"
        kills = []
        hedges = []
        if dims["compliance"] > 0.55:
            kills.append("No public yield / guaranteed ROI claims")
        if dims["cash"] > 0.6:
            kills.append("Freeze fixed opex hiring until pilot cash cycle closes")
        if dims["partner"] > 0.55:
            hedges.append("Dual-source critical logistics partner")
        if dims["demand"] > 0.5:
            hedges.append("Pre-sell or LOI before capacity build")
        if dims["tech"] > 0.55:
            hedges.append("Manual fallback path for agent steps")
        if not kills:
            kills.append("Stay in TZ-scoped work; no open-ended retainers")
        if not hedges:
            hedges.append("Weekly metric review gate before next spend tranche")
        return RiskLatticeResult(
            dimensions=dims,
            composite=composite,
            band=band,
            kill_switches=kills,
            hedges=hedges,
        )


@dataclass
class GraphReachResult:
    nodes: list[str]
    edges: list[dict[str, str]]
    critical_path: list[str]
    centrality: dict[str, float]
    insight: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class GraphReachEngine:
    """Simple dependency graph: who blocks whom in the business chain."""

    name = "GraphReachEngine"

    def run(self, stages: list[str] | None = None, focus: str = "") -> GraphReachResult:
        stages = stages or [
            "intake",
            "sort_quality",
            "process",
            "store",
            "logistics",
            "buyer",
            "cash",
            "feedback",
        ]
        edges = []
        for a, b in zip(stages, stages[1:]):
            edges.append({"from": a, "to": b, "kind": "sequence"})
        # feedback loop
        edges.append({"from": "feedback", "to": "sort_quality", "kind": "loop"})
        edges.append({"from": "cash", "to": "intake", "kind": "fund"})
        n = len(stages)
        centrality = {
            s: round(0.35 + (0.5 if s in ("process", "logistics", "cash") else 0.15)
            + (0.1 if focus and focus.lower() in s else 0), 3)
            for s in stages
        }
        # critical path heuristic
        critical = [s for s in stages if s in ("intake", "process", "logistics", "buyer", "cash")]
        top = max(centrality, key=centrality.get)
        insight = (
            f"Critical path length={len(critical)}; highest leverage node «{top}». "
            f"Optimize {top} before adding marketing surface."
        )
        return GraphReachResult(
            nodes=list(stages),
            edges=edges,
            critical_path=critical,
            centrality=centrality,
            insight=insight,
        )


@dataclass
class UncertaintyBudget:
    known: list[str]
    unknown: list[str]
    assumable: list[str]
    entropy: float
    ask_next: list[str]
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class UncertaintyBudgetEngine:
    """Shannon-ish entropy over missing slots — drives human-like questions."""

    name = "UncertaintyBudgetEngine"

    SLOTS = (
        "who_pays",
        "unit_of_value",
        "first_channel",
        "constraint_cash",
        "constraint_time",
        "geography",
        "regulatory",
        "success_metric",
        "non_goals",
        "partner_dependency",
    )

    def run(self, business_text: str, answers: dict[str, str] | None = None) -> UncertaintyBudget:
        answers = answers or {}
        text = (business_text or "").lower()
        known, unknown, assumable = [], [], []
        markers = {
            "who_pays": (
                "клиент",
                "buyer",
                "b2b",
                "b2c",
                "плат",
                "customer",
                "билдер",
                "builder",
                "студи",
                "studio",
                "агент",
            ),
            "unit_of_value": (
                "тонн",
                "заказ",
                "unit",
                "sku",
                "час",
                "подписк",
                "карточ",
                "пакет",
                "pack",
                "архитект",
                "оффер",
                "ниш",
            ),
            "first_channel": (
                "telegram",
                "whatsapp",
                "x.com",
                "сайт",
                "маркетплейс",
                "marketplace",
                "холод",
                "online",
                "онлайн",
                "сеть",
                "network",
                "канал",
            ),
            "constraint_cash": ("бюджет", "cash", "капитал", "без денег", "bootstrap"),
            "constraint_time": ("дней", "недел", "месяц", "asap", "срок", "пилот", "pilot"),
            "geography": (
                "город",
                "регион",
                "rf",
                "eu",
                "local",
                "москв",
                "online",
                "онлайн",
            ),
            "regulatory": ("лиценз", "отход", "ндс", "compliance", "закон"),
            "success_metric": (
                "метрик",
                "kpi",
                "марж",
                "маржа",
                "conversion",
                "roi",
                "тест",
                "концепт",
                "решени",
                "proof",
            ),
            "non_goals": ("не дела", "не надо", "out of scope", "не трогать"),
            "partner_dependency": ("партнёр", "логист", "поставщик", "supplier", "carrier"),
        }
        for slot in self.SLOTS:
            if answers.get(slot):
                known.append(slot)
                continue
            hits = markers.get(slot, ())
            if any(h in text for h in hits):
                known.append(slot)
            elif slot in ("regulatory", "partner_dependency", "non_goals"):
                assumable.append(slot)
            else:
                unknown.append(slot)
        # entropy proxy
        u = len(unknown) / len(self.SLOTS)
        a = len(assumable) / len(self.SLOTS)
        entropy = round(-(u + 1e-9) * math.log(u + 1e-9) - (a + 1e-9) * math.log(a + 1e-9 + 0.01), 4)
        confidence = round(max(0.12, min(0.94, 1.0 - u * 0.85 - a * 0.25)), 3)
        ask_map = {
            "who_pays": "Кто платит первым циклом — B2B контракт, B2C, или площадка?",
            "unit_of_value": "В чём единица ценности (тонна, заказ, час, SKU)?",
            "first_channel": "Какой первый канал касания уже есть или реалистичен за 7 дней?",
            "constraint_cash": "Жёсткий потолок бюджета на пилот?",
            "constraint_time": "Окно до первого оплачиваемого результата (дни)?",
            "geography": "География: город / регион / online-only?",
            "regulatory": "Есть ли лицензии/эко-ограничения, которые нельзя игнорировать?",
            "success_metric": "Одна метрика успеха пилота (не «всё сразу»)?",
            "non_goals": "Что точно НЕ делаем в v1?",
            "partner_dependency": "Кто критический партнёр, без которого цепочка падает?",
        }
        ask_next = [ask_map[s] for s in unknown[:4]]
        if not ask_next and assumable:
            ask_next = [ask_map[s] for s in assumable[:2]]
        return UncertaintyBudget(
            known=known,
            unknown=unknown,
            assumable=assumable,
            entropy=entropy,
            ask_next=ask_next,
            confidence=confidence,
        )


class SideComputeBundle:
    """Run all side engines relevant to a business brief."""

    def run(
        self,
        business_text: str,
        *,
        numbers: dict[str, float] | None = None,
        answers: dict[str, str] | None = None,
        stages: list[str] | None = None,
    ) -> dict[str, Any]:
        n = numbers or {}
        flow = FlowBalanceEngine().run(
            inflow=float(n.get("inflow", 100)),
            capacity=float(n.get("capacity", 72)),
            leak_rate=float(n.get("leak", 0.14)),
            node_label=str(n.get("node", "ops-hub")),
        )
        risk = RiskLatticeEngine().run(
            {
                "ops": float(n.get("risk_ops", 0.4)),
                "cash": float(n.get("risk_cash", 0.45)),
                "compliance": float(n.get("risk_compliance", 0.35)),
                "demand": float(n.get("risk_demand", 0.5)),
                "partner": float(n.get("risk_partner", 0.42)),
                "tech": float(n.get("risk_tech", 0.38)),
            },
            context=business_text,
        )
        graph = GraphReachEngine().run(stages=stages, focus=str(n.get("focus", "")))
        unc = UncertaintyBudgetEngine().run(business_text, answers=answers)
        return {
            "flow_balance": flow.to_dict(),
            "risk_lattice": risk.to_dict(),
            "graph_reach": graph.to_dict(),
            "uncertainty": unc.to_dict(),
            "engines": [
                FlowBalanceEngine.name,
                RiskLatticeEngine.name,
                GraphReachEngine.name,
                UncertaintyBudgetEngine.name,
            ],
        }
