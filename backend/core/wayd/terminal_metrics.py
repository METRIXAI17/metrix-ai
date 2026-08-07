"""
Terminal metrics model (wayD) — density / signal / acceptance / mesh.

Composes VVI·ER·RRC with acceptance_p, originality, path fit into one terminal bundle.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


def _c01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


@dataclass
class TerminalMetrics:
    """wayD terminal — single analytical surface for ops pad."""

    vvi: float = 0.4
    er: float = 0.5
    rrc: float = 0.5
    health: float = 0.5
    density: float = 0.5  # 1 - voids, how packed the pack is
    signal: float = 0.5  # useful error + proof density
    acceptance_p: float = 0.55  # P(final acceptance)
    originality: float = 0.5
    delight: float = 0.5
    path_fit: float = 0.5
    segment_fit: float = 0.5
    mesh_score: float = 0.5  # emergent edge strength
    ship_gate: str = "hold"  # hold | near_core | ship
    labels: dict[str, str] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        for k in (
            "vvi",
            "er",
            "rrc",
            "health",
            "density",
            "signal",
            "acceptance_p",
            "originality",
            "delight",
            "path_fit",
            "segment_fit",
            "mesh_score",
        ):
            d[k] = round(float(d[k]), 4)
        return d


def compute_terminal(
    *,
    core_metrics: dict[str, Any] | None = None,
    acceptance_p: float | None = None,
    originality: float | None = None,
    delight: float | None = None,
    path_fit: float | None = None,
    segment_fit: float | None = None,
    edge_count: int = 0,
    edge_strength: float = 0.0,
    quality: dict[str, Any] | None = None,
    notes: list[str] | None = None,
) -> TerminalMetrics:
    cm = core_metrics or {}
    # tolerate nested {core: {...}}
    if "core" in cm and isinstance(cm["core"], dict):
        cm = cm["core"]
    vvi = _c01(cm.get("vvi", 0.4))
    er = _c01(cm.get("er", 0.5))
    rrc = _c01(cm.get("rrc", 0.5))
    health = _c01(cm.get("health_score", cm.get("health", (1 - vvi) * 0.4 + er * 0.3 + rrc * 0.3)))

    q = quality or {}
    q_score = _c01(q.get("score", q.get("overall", 0.55)))

    dens = _c01(0.55 * (1.0 - vvi) + 0.25 * rrc + 0.20 * q_score)
    sig = _c01(0.45 * er + 0.30 * q_score + 0.25 * (1.0 - vvi))

    ap = _c01(acceptance_p if acceptance_p is not None else 0.45 * dens + 0.35 * sig + 0.20 * health)
    orig = _c01(originality if originality is not None else 0.5)
    deli = _c01(delight if delight is not None else 0.55)
    pf = _c01(path_fit if path_fit is not None else 0.55)
    sf = _c01(segment_fit if segment_fit is not None else 0.55)

    # mesh: how strongly module edges fire
    mesh = _c01(
        0.35 * min(1.0, edge_count / 6.0)
        + 0.35 * _c01(edge_strength)
        + 0.15 * orig
        + 0.15 * ap
    )

    # ship gate from terminal
    composite = _c01(0.30 * ap + 0.20 * dens + 0.15 * sig + 0.15 * mesh + 0.10 * deli + 0.10 * pf)
    if composite >= 0.72 and ap >= 0.62:
        gate = "ship"
    elif composite >= 0.55:
        gate = "near_core"
    else:
        gate = "hold"

    labels = {
        "density": _band(dens, "sparse", "ok", "dense"),
        "signal": _band(sig, "noise", "mixed", "clear"),
        "acceptance_p": _band(ap, "risky", "viable", "strong"),
        "mesh": _band(mesh, "isolated", "linked", "compound"),
        "ship_gate": gate,
    }

    return TerminalMetrics(
        vvi=vvi,
        er=er,
        rrc=rrc,
        health=health,
        density=dens,
        signal=sig,
        acceptance_p=ap,
        originality=orig,
        delight=deli,
        path_fit=pf,
        segment_fit=sf,
        mesh_score=mesh,
        ship_gate=gate,
        labels=labels,
        notes=list(notes or []),
    )


def _band(v: float, low: str, mid: str, high: str) -> str:
    if v < 0.4:
        return low
    if v < 0.7:
        return mid
    return high
