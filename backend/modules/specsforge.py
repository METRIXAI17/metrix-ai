"""
SpecsForge Recursive Oracle

Мощный рекурсивный разбор и уточнение спецификаций.
Интегрирует VVI / ER / RRC: на каждом уровне глубины пересчитывает метрики
и ищет возможности улучшения (improvement opportunities).

Было: Specification Engine
Стало: SpecsForge Recursive Oracle
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

from backend.config import SPECS_IMPROVEMENT_DELTA, SPECS_MAX_DEPTH
from backend.core.metrics import CoreMetrics, compute_core_metrics


@dataclass
class SpecNode:
    """Узел спецификации (дерево требований)."""

    id: str
    title: str
    detail: str
    priority: float
    depth: int
    children: list["SpecNode"] = field(default_factory=list)
    voids: list[str] = field(default_factory=list)
    improvements: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "detail": self.detail,
            "priority": self.priority,
            "depth": self.depth,
            "children": [c.to_dict() for c in self.children],
            "voids": self.voids,
            "improvements": self.improvements,
            "metrics": self.metrics,
        }


@dataclass
class SpecsForgeResult:
    root: SpecNode
    iterations: int
    final_metrics: CoreMetrics
    improvement_log: list[dict[str, Any]]
    quality_curve: list[float]
    ready_for_build: bool
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": self.root.to_dict(),
            "iterations": self.iterations,
            "final_metrics": self.final_metrics.to_dict(),
            "improvement_log": self.improvement_log,
            "quality_curve": self.quality_curve,
            "ready_for_build": self.ready_for_build,
            "summary": self.summary,
            "module": "SpecsForge Recursive Oracle",
        }


class SpecsForgeRecursiveOracle:
    """
    Рекурсивно:
      parse → measure VVI/ER/RRC → detect voids → refine children → repeat
    пока прирост health не станет меньше SPECS_IMPROVEMENT_DELTA
    или depth == SPECS_MAX_DEPTH.
    """

    name = "SpecsForge Recursive Oracle"

    # Каркас разделов спеки (универсальный + расширяется индустрией)
    BASE_SECTIONS = [
        ("goal", "Outcome & Goal", "What success looks like for the client."),
        ("actors", "Actors & Roles", "Who uses, decides, pays, operates."),
        ("inputs", "Inputs & Signals", "Data, events, and signals entering the system."),
        ("process", "Core Process", "Steps that create value."),
        ("constraints", "Constraints", "Budget, time, compliance, tech limits."),
        ("metrics", "Success Metrics", "How we know it works (incl. VVI/ER/RRC)."),
        ("risks", "Risks & Voids", "What can break or is undefined."),
        ("monetization", "Monetization Hooks", "Promo / market making / auto-orders touchpoints."),
    ]

    INDUSTRY_EXTRA: dict[str, list[tuple[str, str, str]]] = {
        "chipmaking": [
            ("yield", "Yield Geometry", "Yield, defect density, test coverage voids."),
            ("nre", "NRE & Mask Cost", "Non-recurring engineering cost map."),
        ],
        "telecom": [
            ("signal", "Signal Path", "Protocol, QoS, linguistic/signal cooperation."),
            ("sla", "SLA Lattice", "Latency, jitter, availability commitments."),
        ],
        "cloud-economy": [
            ("finops", "FinOps Map", "Spend, reserved capacity, edge placement."),
        ],
        "ai-agencies": [
            ("delivery", "Delivery System", "Agent stack, handoff, SLA to client."),
        ],
        "cost-engineering": [
            ("param_cost", "Parameter Cost Map", "Which parameters burn money."),
        ],
        "device-assembly": [
            ("line", "Line & Config", "Stations, fixtures, setup, rework loops."),
        ],
    }

    def refine(
        self,
        business_text: str,
        industry_id: str,
        orientation_params: dict[str, float] | None = None,
        max_depth: int | None = None,
    ) -> SpecsForgeResult:
        max_depth = max_depth or SPECS_MAX_DEPTH
        orientation_params = orientation_params or {}
        sentences = _split_sentences(business_text)

        root = SpecNode(
            id="spec_root",
            title="Product Specification Root",
            detail=business_text[:500],
            priority=1.0,
            depth=0,
        )

        sections = list(self.BASE_SECTIONS) + self.INDUSTRY_EXTRA.get(industry_id, [])
        for sid, title, detail in sections:
            child = SpecNode(
                id=f"sec_{sid}",
                title=title,
                detail=detail,
                priority=_section_priority(sid, orientation_params),
                depth=1,
            )
            # attach relevant sentence fragments
            hits = [s for s in sentences if _related(s, sid, title)]
            if hits:
                child.detail = f"{detail} | Evidence: {' '.join(hits[:2])}"
            else:
                child.voids.append(f"No explicit evidence for «{title}» in client text")
                child.improvements.append(f"Ask client 1 clarifying question on «{title}»")
            root.children.append(child)

        improvement_log: list[dict[str, Any]] = []
        quality_curve: list[float] = []
        metrics = self._measure_tree(root)
        quality_curve.append(metrics.health_score)

        iteration = 0
        for depth in range(2, max_depth + 1):
            iteration += 1
            before = metrics.health_score
            expanded = 0
            for node in list(_walk(root)):
                if node.depth != depth - 1:
                    continue
                if not node.voids and metrics.vvi < 0.3:
                    continue
                # recursive refinement: spawn micro-specs for voids
                for i, void in enumerate(node.voids[:2]):
                    kid = SpecNode(
                        id=f"{node.id}_r{depth}_{i}",
                        title=f"Refine: {node.title}",
                        detail=f"Closing void → {void}",
                        priority=node.priority * 0.85,
                        depth=depth,
                        improvements=[
                            f"Define acceptance criterion for: {void}",
                            "Link to VVI reduction action",
                        ],
                    )
                    # void partially closed by creating explicit child
                    kid.voids = []
                    node.children.append(kid)
                    expanded += 1
                if expanded:
                    # parent voids become improvements once children exist
                    node.improvements.extend(
                        [f"Addressed via child: {v}" for v in node.voids[:2]]
                    )
                    node.voids = node.voids[2:]

            metrics = self._measure_tree(root)
            gain = metrics.health_score - before
            quality_curve.append(metrics.health_score)
            improvement_log.append(
                {
                    "iteration": iteration,
                    "depth": depth,
                    "expanded_nodes": expanded,
                    "health_before": round(before, 4),
                    "health_after": round(metrics.health_score, 4),
                    "gain": round(gain, 4),
                    "vvi": round(metrics.vvi, 4),
                    "er": round(metrics.er, 4),
                    "rrc": round(metrics.rrc, 4),
                }
            )
            if gain < SPECS_IMPROVEMENT_DELTA and expanded == 0:
                break

        ready = metrics.vvi < 0.45 and metrics.health_score >= 0.50
        summary = (
            f"{self.name}: {iteration} recursive passes, "
            f"health {quality_curve[0]:.2f} → {metrics.health_score:.2f}, "
            f"VVI={metrics.vvi:.2f}, ready_for_build={ready}."
        )

        return SpecsForgeResult(
            root=root,
            iterations=iteration,
            final_metrics=metrics,
            improvement_log=improvement_log,
            quality_curve=quality_curve,
            ready_for_build=ready,
            summary=summary,
        )

    def _measure_tree(self, root: SpecNode) -> CoreMetrics:
        nodes = list(_walk(root))
        total = len(nodes)
        with_voids = sum(1 for n in nodes if n.voids)
        with_improvements = sum(1 for n in nodes if n.improvements)
        known = total - with_voids
        required = max(total, 8)
        detected = with_voids
        actionable = with_improvements
        fragments = total
        reassemblies = sum(1 for n in nodes if n.children)

        metrics = compute_core_metrics(
            known_params=max(1, known),
            required_params=required,
            ambiguity_score=min(1.0, with_voids / max(1, total)),
            conflict_score=0.05,
            missing_critical=min(4, with_voids // 2),
            detected_errors=detected,
            actionable_errors=actionable,
            false_positives=0,
            improvement_delta=min(1.0, with_improvements / max(1, total)),
            fragments=fragments,
            successful_reassemblies=reassemblies,
            structure_entropy=0.45,
            reverse_links=reassemblies,
            forward_links=max(1, total),
        )
        root.metrics = metrics.to_dict()
        return metrics


def _walk(node: SpecNode):
    yield node
    for c in node.children:
        yield from _walk(c)


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"[.!?\n]+", text)
    return [p.strip() for p in parts if len(p.strip()) > 12]


def _related(sentence: str, sid: str, title: str) -> bool:
    s = sentence.lower()
    keys = sid.replace("_", " ").split() + title.lower().split()
    keys = [k for k in keys if len(k) > 3]
    return any(k in s for k in keys)


def _section_priority(sid: str, params: dict[str, float]) -> float:
    base = {
        "goal": 1.0,
        "actors": 0.85,
        "inputs": 0.75,
        "process": 0.95,
        "constraints": 0.8,
        "metrics": 0.9,
        "risks": 0.85,
        "monetization": 0.88,
    }.get(sid, 0.7)
    boost = 0.0
    if sid in ("monetization", "metrics") and params.get("p_actionability", 0) > 0.5:
        boost = 0.08
    return min(1.0, base + boost)
