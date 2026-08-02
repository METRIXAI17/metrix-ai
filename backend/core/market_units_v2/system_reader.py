"""
System Reader — business-grade intake for Market Units.

Reads free-text brief + orientation scores into a semantic state graph:
entities, constraints, signals, readiness bands. No external LLM.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass, field
from typing import Any


SIGNAL_LEXICON: dict[str, tuple[str, ...]] = {
    "ops_friction": (
        "chaos", "rework", "delay", "bottleneck", "handoff", "sla miss",
        "хаос", "переделк", "задерж", "узк", "срыв", "операц",
    ),
    "cost_pressure": (
        "cost", "api", "token", "burn", "margin", "expensive", "waste",
        "стоим", "дорог", "токен", "марж", "расход", "утеч",
    ),
    "product_void": (
        "unclear", "vague", "no product", "mvp", "spec gap", "undefined",
        "неясн", "размыт", "нет продукт", "дыры", "пустот", "тз",
    ),
    "demand_signal": (
        "buyer", "client", "pipeline", "lead", "demand", "retention",
        "клиент", "спрос", "лид", "воронк", "удержан",
    ),
    "quality_risk": (
        "quality", "error", "bug", "defect", "reliability", "trust",
        "качеств", "ошибк", "баг", "дефект", "надёж", "довер",
    ),
    "scale_intent": (
        "scale", "growth", "multi", "team", "hire", "volume",
        "масштаб", "рост", "команд", "объём", "наём",
    ),
    "liquidity": (
        "liquidity", "cash", "order", "offramp", "document", "deal",
        "ликвид", "заказ", "оффер", "документ", "сделк", "оплат",
    ),
}

ENTITY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("budget", re.compile(r"(?:budget|бюджет)\s*[:=]?\s*\$?\s*(\d[\d\s,]*)", re.I)),
    ("deadline_days", re.compile(r"(?:deadline|срок|days?|дн[ея])\s*[:=]?\s*(\d{1,3})", re.I)),
    ("clients", re.compile(r"(?:clients?|клиент)\w*\s*[:=]?\s*(\d{1,5})", re.I)),
]


@dataclass
class SemanticNode:
    id: str
    kind: str
    label: str
    weight: float
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SystemReadResult:
    module: str
    brief_hash: str
    length: int
    language_hint: str
    signals: dict[str, float]
    entities: dict[str, float]
    nodes: list[SemanticNode]
    readiness_band: str
    density: float
    voids: list[str]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "brief_hash": self.brief_hash,
            "length": self.length,
            "language_hint": self.language_hint,
            "signals": {k: round(v, 4) for k, v in self.signals.items()},
            "entities": self.entities,
            "nodes": [n.to_dict() for n in self.nodes],
            "readiness_band": self.readiness_band,
            "density": round(self.density, 4),
            "voids": self.voids,
            "summary": self.summary,
        }


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _lang_hint(text: str) -> str:
    cyr = sum(1 for c in text if "\u0400" <= c <= "\u04ff")
    return "ru" if cyr > max(3, len(text) // 8) else "en"


class SystemReader:
    """Deterministic system reader — maps text → semantic graph."""

    name = "System Reader"

    def read(
        self,
        *,
        business_text: str,
        industry_id: str,
        orientation: dict[str, Any] | None = None,
        scores: dict[str, float] | None = None,
    ) -> SystemReadResult:
        text = (business_text or "").strip()
        low = text.lower()
        orientation = orientation or {}
        scores = scores or dict(orientation.get("scores") or {})

        signals: dict[str, float] = {}
        nodes: list[SemanticNode] = []
        for sig_id, words in SIGNAL_LEXICON.items():
            hits = [w for w in words if w in low]
            # length-normalized signal strength
            raw = len(hits) / max(2.0, len(words) * 0.35)
            score_boost = 0.0
            if sig_id == "ops_friction":
                score_boost = max(0.0, 0.55 - float(scores.get("readiness", 0.5)))
            elif sig_id == "product_void":
                score_boost = max(0.0, 0.5 - float(scores.get("product_fit", 0.5)))
            elif sig_id == "demand_signal":
                score_boost = float(scores.get("promo_fit", 0.4)) * 0.25
            strength = _clamp01(raw * 0.55 + score_boost)
            signals[sig_id] = strength
            if strength >= 0.12:
                nodes.append(
                    SemanticNode(
                        id=f"sig:{sig_id}",
                        kind="signal",
                        label=sig_id,
                        weight=strength,
                        evidence=hits[:5],
                    )
                )

        entities: dict[str, float] = {}
        for name, pat in ENTITY_PATTERNS:
            m = pat.search(text)
            if m:
                try:
                    val = float(str(m.group(1)).replace(" ", "").replace(",", ""))
                    entities[name] = val
                    nodes.append(
                        SemanticNode(
                            id=f"ent:{name}",
                            kind="entity",
                            label=name,
                            weight=_clamp01(val / (10000 if name == "budget" else 100)),
                            evidence=[m.group(0)[:80]],
                        )
                    )
                except ValueError:
                    pass

        # structural voids from orientation missing params
        missing = list(
            (orientation.get("parameter_map") or {}).get("missing") or []
        )
        voids = [str(m) for m in missing[:8]]
        if signals.get("product_void", 0) > 0.4 and "product_definition" not in voids:
            voids.append("product_definition")
        if signals.get("ops_friction", 0) > 0.45 and "ops_control_loop" not in voids:
            voids.append("ops_control_loop")

        known = float(scores.get("overall_orientation", 0.5))
        density = _clamp01(
            0.25
            + known * 0.35
            + min(0.25, len(text) / 800.0)
            + min(0.15, sum(1 for v in signals.values() if v > 0.2) * 0.03)
        )
        readiness = float(scores.get("readiness", 0.5))
        if readiness >= 0.7 and density >= 0.55:
            band = "execution_ready"
        elif readiness >= 0.45:
            band = "pilot_ready"
        elif density >= 0.4:
            band = "orientation_needed"
        else:
            band = "intake_thin"

        nodes.append(
            SemanticNode(
                id=f"ind:{industry_id}",
                kind="industry",
                label=industry_id,
                weight=1.0,
                evidence=[],
            )
        )

        top_sig = sorted(signals.items(), key=lambda x: -x[1])[:3]
        summary = (
            f"SystemReader[{industry_id}]: band={band}, density={density:.2f}; "
            f"top signals="
            + ", ".join(f"{k}={v:.2f}" for k, v in top_sig)
            + (f"; voids={len(voids)}" if voids else "")
        )

        return SystemReadResult(
            module=self.name,
            brief_hash=hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],
            length=len(text),
            language_hint=_lang_hint(text),
            signals=signals,
            entities=entities,
            nodes=nodes,
            readiness_band=band,
            density=density,
            voids=voids,
            summary=summary,
        )
