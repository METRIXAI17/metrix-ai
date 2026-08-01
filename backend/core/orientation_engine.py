"""
OrientationForge Dynamic Compass (Orientation Engine).

Не «загружаем всё в БД и учим». Каждый запрос:

1. PLACE  — кладём бизнес в концептуальную систему координат индустрии
2. MINE   — добываем только параметры, которые важны для ЭТОЙ задачи
3. CALCULATE — считаем в реальном времени по parameter map + алгоритмам

Это сердце «динамической ориентации» @karimmetrix.
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import asdict, dataclass, field
from typing import Any

from backend.config import INDUSTRIES
from backend.core.metrics import (
    CoreMetrics,
    compute_core_metrics,
    entropy_of_weights,
)


# Параметры, которые «ищем» в тексте по индустриям (лёгкий mining без LLM)
INDUSTRY_PARAM_LEXICON: dict[str, list[str]] = {
    "ai-agencies": [
        "client", "agent", "delivery", "retainer", "prompt", "workflow",
        "automation", "demo", "proposal", "margin", "ops", "sla",
    ],
    "cloud-economy": [
        "cost", "spend", "latency", "region", "edge", "workload",
        "reserved", "spot", "finops", "capacity", "egress", "sla",
    ],
    "cost-engineering": [
        "cost", "waste", "parameter", "yield", "tolerance", "bom",
        "cycle", "rework", "efficiency", "capex", "opex", "nre",
    ],
    "chipmaking": [
        "yield", "node", "fab", "die", "design", "tapeout", "pdk",
        "power", "leakage", "dft", "mask", "wafer", "nre",
    ],
    "telecom": [
        "network", "latency", "bandwidth", "protocol", "signal", "qos",
        "arpu", "churn", "spectrum", "core", "ran", "sla", "packet",
    ],
    "device-assembly": [
        "assembly", "bom", "setup", "config", "rework", "throughput",
        "station", "fixture", "firmware", "qc", "kit", "line",
    ],
    "asset-decisions": [
        "asset", "capital", "risk", "metric", "portfolio", "strategy",
        "monitor", "cognition", "liquidity", "private", "horizon", "drawdown",
    ],
    "d2c-offramp": [
        "d2c", "freelace", "freelance", "document", "workspace", "offramp",
        "agent", "order", "brief", "exchange", "handoff", "idea", "outreach",
    ],
}

# Оси концептуального пространства (общие + индустриальные)
BASE_AXES = ("value_density", "time_pressure", "complexity", "monetization_fit", "risk")


@dataclass
class ParameterMap:
    """Минимальный набор параметров для задачи — ничего лишнего."""

    params: dict[str, float]
    mined_keywords: list[str]
    missing: list[str]
    required_count: int
    known_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CoordinateFrame:
    """Концептуальная система координат для бизнеса."""

    industry_id: str
    industry_name: str
    axes: dict[str, float]
    seed: str
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class OrientationResult:
    """Результат динамической ориентации одного запроса."""

    frame: CoordinateFrame
    parameter_map: ParameterMap
    scores: dict[str, float]
    metrics: CoreMetrics
    operating_mode: str
    narrative: str
    tracks_recommended: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "frame": self.frame.to_dict(),
            "parameter_map": self.parameter_map.to_dict(),
            "scores": self.scores,
            "metrics": self.metrics.to_dict(),
            "operating_mode": self.operating_mode,
            "narrative": self.narrative,
            "tracks_recommended": self.tracks_recommended,
        }


class OrientationEngine:
    """
    OrientationForge Dynamic Compass.

    Простая логика: текст + индустрия → координаты → parameter map → scores.
    Никакого тяжёлого обучения. Каждый вызов независим (zero bias from stale DB).
    """

    def __init__(self) -> None:
        self.name = "OrientationForge Dynamic Compass"

    def orient(
        self,
        business_text: str,
        industry_id: str,
        track: str | None = None,
        extra_params: dict[str, float] | None = None,
    ) -> OrientationResult:
        industry = INDUSTRIES.get(industry_id)
        if not industry:
            raise ValueError(
                f"Unknown industry '{industry_id}'. "
                f"Allowed: {', '.join(INDUSTRIES)}"
            )

        text = (business_text or "").strip()
        if len(text) < 10:
            raise ValueError("business_text too short — need a real description")

        # 1) PLACE
        frame = self._place(text, industry)

        # 2) MINE
        pmap = self._mine(text, industry_id, extra_params or {})

        # 3) CALCULATE
        scores = self._calculate(frame, pmap, track)
        metrics = self._metrics_from(pmap, scores)
        mode = self._pick_mode(scores, metrics)
        tracks = self._recommend_tracks(scores, track)
        narrative = self._narrate(frame, pmap, scores, mode, metrics)

        return OrientationResult(
            frame=frame,
            parameter_map=pmap,
            scores=scores,
            metrics=metrics,
            operating_mode=mode,
            narrative=narrative,
            tracks_recommended=tracks,
        )

    # ── steps ────────────────────────────────────────────────────────────────

    def _place(self, text: str, industry: dict[str, Any]) -> CoordinateFrame:
        seed = hashlib.sha256(
            f"{industry['id']}|{text[:400]}".encode("utf-8")
        ).hexdigest()[:12]

        tokens = _tokenize(text)
        length_factor = min(1.0, len(tokens) / 80.0)
        urgency = _keyword_density(tokens, ["urgent", "asap", "now", "fast", "deadline", "срочно"])
        complexity = _keyword_density(
            tokens,
            ["complex", "multi", "scale", "enterprise", "integration", "сложн", "масштаб"],
        )
        money = _keyword_density(
            tokens,
            ["revenue", "margin", "price", "payback", "roi", "profit", "маржа", "выруч"],
        )
        risk = _keyword_density(
            tokens,
            ["risk", "compliance", "security", "fail", "churn", "риск", "безопас"],
        )
        value = _keyword_density(
            tokens,
            ["unique", "advantage", "premium", "leverage", "edge", "преимущ", "уник"],
        )

        axes = {
            "value_density": _clamp01(0.25 + value * 2.5 + length_factor * 0.15),
            "time_pressure": _clamp01(0.20 + urgency * 3.0),
            "complexity": _clamp01(0.20 + complexity * 2.8 + length_factor * 0.2),
            "monetization_fit": _clamp01(0.30 + money * 2.5 + value * 0.5),
            "risk": _clamp01(0.15 + risk * 2.8),
        }
        # tiny deterministic wobble from seed so same text → same coords
        for i, axis in enumerate(BASE_AXES):
            wobble = (int(seed[i * 2 : i * 2 + 2], 16) / 255.0 - 0.5) * 0.06
            axes[axis] = _clamp01(axes[axis] + wobble)

        return CoordinateFrame(
            industry_id=industry["id"],
            industry_name=industry["name"],
            axes=axes,
            seed=seed,
            notes=[
                f"Placed into {industry['name']} conceptual frame",
                f"seed={seed}",
            ],
        )

    def _mine(
        self,
        text: str,
        industry_id: str,
        extra: dict[str, float],
    ) -> ParameterMap:
        tokens = set(_tokenize(text))
        lexicon = INDUSTRY_PARAM_LEXICON.get(industry_id, [])
        mined: dict[str, float] = {}
        found_kw: list[str] = []

        for kw in lexicon:
            if kw in tokens or kw in text.lower():
                # presence strength: frequency-ish
                count = text.lower().count(kw)
                mined[f"p_{kw}"] = _clamp01(0.35 + min(0.55, count * 0.12))
                found_kw.append(kw)

        # generic structural params always present
        mined["p_clarity"] = _clamp01(min(1.0, len(text) / 400.0))
        mined["p_specificity"] = _clamp01(len(found_kw) / max(6, len(lexicon) * 0.4))
        mined["p_actionability"] = _clamp01(
            0.3
            + _keyword_density(
                list(tokens),
                ["need", "want", "build", "sell", "optimize", "reduce", "launch", "нужн", "хочу"],
            )
            * 2.0
        )

        for k, v in extra.items():
            mined[str(k)] = _clamp01(float(v))

        required = max(8, int(len(lexicon) * 0.5) + 3)
        known = len([1 for v in mined.values() if v >= 0.3])
        missing = [f"p_{kw}" for kw in lexicon if f"p_{kw}" not in mined][:8]

        return ParameterMap(
            params=mined,
            mined_keywords=found_kw,
            missing=missing,
            required_count=required,
            known_count=known,
        )

    def _calculate(
        self,
        frame: CoordinateFrame,
        pmap: ParameterMap,
        track: str | None,
    ) -> dict[str, float]:
        a = frame.axes
        specificity = pmap.params.get("p_specificity", 0.3)
        clarity = pmap.params.get("p_clarity", 0.3)
        action = pmap.params.get("p_actionability", 0.3)

        product_fit = _clamp01(
            a["value_density"] * 0.45 + specificity * 0.35 + (1 - a["risk"]) * 0.20
        )
        model_fit = _clamp01(
            a["monetization_fit"] * 0.50 + clarity * 0.25 + a["complexity"] * 0.25
        )
        promo_fit = _clamp01(
            action * 0.40 + a["value_density"] * 0.30 + a["time_pressure"] * 0.30
        )

        # if track forced — boost it
        if track == "product":
            product_fit = _clamp01(product_fit + 0.12)
        elif track == "models":
            model_fit = _clamp01(model_fit + 0.12)
        elif track == "promotion":
            promo_fit = _clamp01(promo_fit + 0.12)

        overall = _clamp01(product_fit * 0.34 + model_fit * 0.33 + promo_fit * 0.33)
        readiness = _clamp01(
            (pmap.known_count / max(1, pmap.required_count)) * 0.6
            + clarity * 0.4
        )

        return {
            "product_fit": round(product_fit, 4),
            "model_fit": round(model_fit, 4),
            "promo_fit": round(promo_fit, 4),
            "overall_orientation": round(overall, 4),
            "readiness": round(readiness, 4),
            "entropy": round(entropy_of_weights(pmap.params), 4),
        }

    def _metrics_from(self, pmap: ParameterMap, scores: dict[str, float]) -> CoreMetrics:
        ambiguity = 1.0 - pmap.params.get("p_clarity", 0.3)
        missing_crit = max(0, pmap.required_count - pmap.known_count)
        # treat missing keywords as soft "errors" that are actionable
        detected = len(pmap.missing) + max(0, 3 - len(pmap.mined_keywords))
        actionable = max(0, detected - 1)

        return compute_core_metrics(
            known_params=pmap.known_count,
            required_params=pmap.required_count,
            ambiguity_score=ambiguity,
            conflict_score=0.08,
            missing_critical=min(missing_crit, 4),
            detected_errors=detected,
            actionable_errors=actionable,
            false_positives=0,
            improvement_delta=scores.get("readiness", 0.3) * 0.5,
            fragments=max(3, len(pmap.params)),
            successful_reassemblies=max(1, pmap.known_count // 2),
            structure_entropy=scores.get("entropy", 0.5),
            reverse_links=max(1, len(pmap.mined_keywords) // 2),
            forward_links=max(2, len(pmap.params)),
            notes=["metrics derived from orientation parameter map"],
        )

    def _pick_mode(self, scores: dict[str, float], metrics: CoreMetrics) -> str:
        """Режим работы OAS под запрос (как в посте про 8 pillars)."""
        if metrics.vvi > 0.65:
            return "specs_deep_dive"
        if scores["promo_fit"] >= max(scores["product_fit"], scores["model_fit"]) + 0.05:
            return "promotion_first"
        if scores["model_fit"] >= scores["product_fit"]:
            return "fin_model_focus"
        if scores["readiness"] < 0.4:
            return "orientation_expand"
        if metrics.health_score >= 0.7:
            return "full_package_ready"
        return "balanced_product_path"

    def _recommend_tracks(self, scores: dict[str, float], forced: str | None) -> list[str]:
        if forced in ("product", "models", "promotion"):
            rest = [t for t in ("product", "models", "promotion") if t != forced]
            ranked = sorted(
                rest,
                key=lambda t: scores[
                    {"product": "product_fit", "models": "model_fit", "promotion": "promo_fit"}[t]
                ],
                reverse=True,
            )
            return [forced] + ranked
        pairs = [
            ("product", scores["product_fit"]),
            ("models", scores["model_fit"]),
            ("promotion", scores["promo_fit"]),
        ]
        pairs.sort(key=lambda x: x[1], reverse=True)
        return [p[0] for p in pairs]

    def _narrate(
        self,
        frame: CoordinateFrame,
        pmap: ParameterMap,
        scores: dict[str, float],
        mode: str,
        metrics: CoreMetrics,
    ) -> str:
        top_axis = max(frame.axes.items(), key=lambda x: x[1])
        return (
            f"{self.name} oriented «{frame.industry_name}» "
            f"(seed {frame.seed}). Dominant axis: {top_axis[0]}={top_axis[1]:.2f}. "
            f"Mined {len(pmap.mined_keywords)} industry signals "
            f"({', '.join(pmap.mined_keywords[:5]) or 'generic'}). "
            f"Mode: {mode}. Health={metrics.health_score:.2f} "
            f"(VVI={metrics.vvi:.2f}, ER={metrics.er:.2f}, RRC={metrics.rrc:.2f}). "
            f"Track fit P/M/Pr = "
            f"{scores['product_fit']:.2f}/"
            f"{scores['model_fit']:.2f}/"
            f"{scores['promo_fit']:.2f}."
        )


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9_+#.-]{2,}", text.lower())


def _keyword_density(tokens: list[str], keywords: list[str]) -> float:
    if not tokens:
        return 0.0
    hits = sum(1 for t in tokens if t in keywords)
    return min(1.0, hits / max(8, len(tokens) * 0.08))


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))
