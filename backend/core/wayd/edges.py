"""
System edges — unique functions emerge from module composition.

Each edge links two+ modules under a wayD label. The mesh score
feeds TerminalMetrics and GenCore slot unlocks.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SystemEdge:
    id: str
    label: str
    modules: list[str]
    function: str
    function_ru: str
    strength: float = 0.5
    unlocked: bool = True
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Catalog of compound functions (not available as single modules alone)
EDGE_CATALOG: list[dict[str, Any]] = [
    {
        "id": "E_gencore_livelog",
        "label": "L.edge.gencore_x_livelog",
        "modules": ["gencore", "live_log"],
        "function": "Live uniqueness trail — gen slots write proof ticks into 7-day log",
        "function_ru": "Живой трейл уникальности — слоты GenCore пишут proof-тики в 7-дневный лог",
        "requires": ["gencore", "live_log"],
    },
    {
        "id": "E_segment_path",
        "label": "L.edge.segment_x_path",
        "modules": ["client_segmentation", "user_paths"],
        "function": "Segment-locked path pack — sophisticated results only for matching persona",
        "function_ru": "Путь под сегмент — навороченный result pack только при match персоны",
        "requires": ["client_segmentation", "user_paths"],
    },
    {
        "id": "E_accept_orig",
        "label": "L.edge.accept_x_originality",
        "modules": ["acceptance_forecast", "originality_inject"],
        "function": "Acceptance-aware originality — raise unique phrasing when risk of template reject",
        "function_ru": "Оригинальность под приёмку — усиливает уникальные обороты при риске шаблонного отказа",
        "requires": ["acceptance_forecast", "originality_inject"],
    },
    {
        "id": "E_robotics_impl",
        "label": "L.edge.robotics_x_implement",
        "modules": ["robotics_harness", "implement_model"],
        "function": "Autonomous robotics executor — three-direction rollout without chat loop",
        "function_ru": "Автономный роботикс-исполнитель — раскатка трёх направлений без чат-цикла",
        "requires": ["robotics_harness", "implement_model"],
    },
    {
        "id": "E_expert_gencore",
        "label": "L.edge.expert_x_gencore",
        "modules": ["expert_base_directions", "gencore"],
        "function": "Expert-primed gen slots — popular direction priors bias v2–v5 artifacts",
        "function_ru": "Экспертные priors в слотах — популярные направления смещают артефакты v2–v5",
        "requires": ["expert_base_directions", "gencore"],
    },
    {
        "id": "E_wayd_terminal",
        "label": "L.metric.acceptance_p",
        "modules": ["wayd", "gencore", "live_log", "acceptance_forecast"],
        "function": "Terminal cockpit — density·signal·acceptance·mesh on one ops surface",
        "function_ru": "Терминальный кабинет — density·signal·acceptance·mesh на одной ops-панели",
        "requires": ["wayd", "acceptance_forecast"],
    },
]


@dataclass
class EdgeMesh:
    edges: list[SystemEdge] = field(default_factory=list)
    active_modules: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        unlocked = [e for e in self.edges if e.unlocked]
        strength = (
            sum(e.strength for e in unlocked) / max(1, len(unlocked)) if unlocked else 0.0
        )
        return {
            "model": "wayD.edges",
            "version": "1.0.0",
            "active_modules": self.active_modules,
            "edge_count": len(unlocked),
            "edge_strength": round(strength, 4),
            "edges": [e.to_dict() for e in self.edges],
            "unique_functions": [
                {"id": e.id, "function": e.function, "function_ru": e.function_ru, "strength": e.strength}
                for e in unlocked
            ],
        }


def compose_edges(
    active_modules: list[str] | None = None,
    *,
    quality_boost: float = 0.0,
    segment_fit: float = 0.5,
    path_fit: float = 0.5,
) -> EdgeMesh:
    mods = set(active_modules or [])
    # Always assume wayd spine present when this runs
    mods.add("wayd")
    edges: list[SystemEdge] = []
    for cat in EDGE_CATALOG:
        req = set(cat.get("requires") or cat.get("modules") or [])
        hit = len(req & mods)
        unlocked = hit >= max(1, len(req) - 0 if len(req) <= 2 else len(req) - 1) and hit >= 2
        # partial unlock if majority present
        if hit >= 2 and hit < len(req):
            unlocked = True
        strength = 0.35 + 0.25 * (hit / max(1, len(req)))
        strength += 0.15 * float(quality_boost)
        strength += 0.10 * float(segment_fit) + 0.10 * float(path_fit)
        strength = max(0.0, min(1.0, strength))
        edges.append(
            SystemEdge(
                id=cat["id"],
                label=cat["label"],
                modules=list(cat["modules"]),
                function=cat["function"],
                function_ru=cat["function_ru"],
                strength=round(strength, 4),
                unlocked=unlocked and strength >= 0.4,
                meta={"hit": hit, "required": len(req)},
            )
        )
    return EdgeMesh(edges=edges, active_modules=sorted(mods))


def unique_functions(mesh: EdgeMesh | dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(mesh, EdgeMesh):
        d = mesh.to_dict()
    else:
        d = mesh
    return list(d.get("unique_functions") or [])
