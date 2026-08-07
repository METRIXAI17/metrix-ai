"""
Label ontology for Metrix concierge / wayD.

Convention: L.<namespace>.<token>
Namespaces: direction · unit · channel · segment · path · metric · edge · rail · skill
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable


# Canonical label catalog (concierge terminal)
CANONICAL: dict[str, dict[str, str]] = {
    # Three implementation directions (single paid SKU surface — internal)
    "L.direction.product_pack": {
        "ru": "Направление · product pack",
        "en": "Direction · product pack",
        "role": "direction",
    },
    "L.direction.unit_pack": {
        "ru": "Направление · unit pack",
        "en": "Direction · unit pack",
        "role": "direction",
    },
    "L.direction.ch_network": {
        "ru": "Направление · channel network",
        "en": "Direction · channel network",
        "role": "direction",
    },
    # Units / metrics
    "L.unit.paid_units": {"ru": "Unit · paid units", "en": "Unit · paid units", "role": "unit"},
    "L.unit.margin": {"ru": "Unit · margin", "en": "Unit · margin", "role": "unit"},
    "L.metric.vvi": {"ru": "Метрика VVI", "en": "Metric VVI", "role": "metric"},
    "L.metric.er": {"ru": "Метрика ER", "en": "Metric ER", "role": "metric"},
    "L.metric.rrc": {"ru": "Метрика RRC", "en": "Metric RRC", "role": "metric"},
    "L.metric.acceptance_p": {
        "ru": "Прогноз приёмки",
        "en": "Acceptance probability",
        "role": "metric",
    },
    "L.metric.originality": {
        "ru": "Оригинальность вставок",
        "en": "Originality density",
        "role": "metric",
    },
    "L.metric.delight": {"ru": "Delight score", "en": "Delight score", "role": "metric"},
    # Segments
    "L.segment.b2b_ops": {"ru": "Сегмент B2B ops", "en": "Segment B2B ops", "role": "segment"},
    "L.segment.b2b_product": {
        "ru": "Сегмент B2B product",
        "en": "Segment B2B product",
        "role": "segment",
    },
    "L.segment.b2b_knowledge": {
        "ru": "Сегмент knowledge/library",
        "en": "Segment knowledge/library",
        "role": "segment",
    },
    "L.segment.agency": {"ru": "Сегмент agency", "en": "Segment agency", "role": "segment"},
    "L.segment.founder_solo": {
        "ru": "Сегмент founder solo",
        "en": "Segment founder solo",
        "role": "segment",
    },
    "L.segment.platform": {
        "ru": "Сегмент platform",
        "en": "Segment platform",
        "role": "segment",
    },
    # Paths
    "L.path.library_ship": {
        "ru": "Путь · library → ship",
        "en": "Path · library → ship",
        "role": "path",
    },
    "L.path.agency_margin": {
        "ru": "Путь · agency margin",
        "en": "Path · agency margin",
        "role": "path",
    },
    "L.path.builder_pack": {
        "ru": "Путь · builder pack",
        "en": "Path · builder pack",
        "role": "path",
    },
    "L.path.api_cost": {
        "ru": "Путь · API cost cut",
        "en": "Path · API cost cut",
        "role": "path",
    },
    "L.path.expert_sku": {
        "ru": "Путь · expert SKU",
        "en": "Path · expert SKU",
        "role": "path",
    },
    # Rails / system
    "L.rail.no_auto_yield": {
        "ru": "Рельс · no auto-yield",
        "en": "Rail · no auto-yield",
        "role": "rail",
    },
    "L.rail.single_stop": {
        "ru": "Рельс · один stop-rule",
        "en": "Rail · single stop-rule",
        "role": "rail",
    },
    "L.rail.a01_a12_steps": {
        "ru": "Рельс · A01–A12 шаги",
        "en": "Rail · A01–A12 steps",
        "role": "rail",
    },
    "L.rail.hide_paid_surface": {
        "ru": "Рельс · платная поверхность скрыта",
        "en": "Rail · paid surface hidden",
        "role": "rail",
    },
    # Module edges (emergent functions)
    "L.edge.gencore_x_livelog": {
        "ru": "Edge · GenCore × LiveLog",
        "en": "Edge · GenCore × LiveLog",
        "role": "edge",
    },
    "L.edge.segment_x_path": {
        "ru": "Edge · Segment × Path",
        "en": "Edge · Segment × Path",
        "role": "edge",
    },
    "L.edge.accept_x_originality": {
        "ru": "Edge · Acceptance × Originality",
        "en": "Edge · Acceptance × Originality",
        "role": "edge",
    },
    "L.edge.robotics_x_implement": {
        "ru": "Edge · Robotics × Implement",
        "en": "Edge · Robotics × Implement",
        "role": "edge",
    },
    "L.edge.expert_x_gencore": {
        "ru": "Edge · ExpertBase × GenCore",
        "en": "Edge · ExpertBase × GenCore",
        "role": "edge",
    },
}


@dataclass
class Label:
    id: str
    weight: float = 1.0
    source: str = "system"
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        base = asdict(self)
        cat = CANONICAL.get(self.id) or {}
        base["catalog"] = cat
        base["role"] = cat.get("role") or self.id.split(".")[1] if "." in self.id else "custom"
        return base


class LabelBus:
    """Accumulates labels for a run; enforces hard rails as sticky labels."""

    def __init__(self) -> None:
        self._labels: dict[str, Label] = {}

    def add(self, label_id: str, weight: float = 1.0, source: str = "system", **meta: Any) -> None:
        prev = self._labels.get(label_id)
        if prev:
            prev.weight = max(prev.weight, float(weight))
            prev.meta.update(meta)
            return
        self._labels[label_id] = Label(id=label_id, weight=float(weight), source=source, meta=meta)

    def add_many(self, ids: Iterable[str], weight: float = 1.0, source: str = "system") -> None:
        for i in ids:
            self.add(i, weight=weight, source=source)

    def has(self, label_id: str) -> bool:
        return label_id in self._labels

    def by_role(self, role: str) -> list[Label]:
        out = []
        for lab in self._labels.values():
            cat = CANONICAL.get(lab.id) or {}
            r = cat.get("role") or ""
            if r == role:
                out.append(lab)
        return sorted(out, key=lambda x: -x.weight)

    def ids(self) -> list[str]:
        return sorted(self._labels.keys(), key=lambda k: -self._labels[k].weight)

    def stamp(self) -> dict[str, Any]:
        return {
            "model": "wayD",
            "version": "1.0.0",
            "labels": [lab.to_dict() for lab in sorted(self._labels.values(), key=lambda x: -x.weight)],
            "ids": self.ids(),
            "counts_by_role": _counts_by_role(self._labels.values()),
        }


def _counts_by_role(labels: Iterable[Label]) -> dict[str, int]:
    c: dict[str, int] = {}
    for lab in labels:
        cat = CANONICAL.get(lab.id) or {}
        r = cat.get("role") or "custom"
        c[r] = c.get(r, 0) + 1
    return c


def stamp_labels(
    *,
    direction_ids: list[str] | None = None,
    segment_id: str | None = None,
    path_id: str | None = None,
    extra: list[str] | None = None,
    rails: bool = True,
) -> dict[str, Any]:
    """One-shot stamp for pipeline modules."""
    bus = LabelBus()
    if rails:
        bus.add_many(
            [
                "L.rail.no_auto_yield",
                "L.rail.single_stop",
                "L.rail.a01_a12_steps",
                "L.rail.hide_paid_surface",
            ],
            weight=1.0,
            source="hard_rail",
        )
    for d in direction_ids or []:
        lid = d if d.startswith("L.") else f"L.direction.{d}"
        bus.add(lid, weight=1.0, source="direction")
    if segment_id:
        sid = segment_id if segment_id.startswith("L.") else f"L.segment.{segment_id}"
        bus.add(sid, weight=1.0, source="segment")
    if path_id:
        pid = path_id if path_id.startswith("L.") else f"L.path.{path_id}"
        bus.add(pid, weight=1.0, source="path")
    for e in extra or []:
        bus.add(e, weight=0.85, source="compose")
    bus.add_many(
        ["L.metric.vvi", "L.metric.er", "L.metric.rrc", "L.metric.acceptance_p", "L.metric.originality"],
        weight=0.7,
        source="terminal",
    )
    return bus.stamp()
