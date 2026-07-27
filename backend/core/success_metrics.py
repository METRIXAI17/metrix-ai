"""
Custom Success Metrics Positioning
==================================

Клиент (или система) может **позиционировать** success-метрики
относительно текущего запроса. Это становится частью уникального ТЗ (TZ)
и влияет на scoring, Decision Core и Operational Analytics Engine.

Стандарт (applied meaning vector specs for paid part) хранится отдельно —
см. backend/paid/meaning_vectors.py (блок 18 — ядро платного продукта).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from backend.config import METRIC_THRESHOLDS


# ── Стандартный каркас success-метрик (можно переопределить per-request) ─────
DEFAULT_SUCCESS_METRIC_DEFS: dict[str, dict[str, Any]] = {
    "clarity": {
        "label": "Clarity of geometry",
        "description": "Насколько запрос даёт чёткую карту параметров",
        "default_weight": 0.18,
        "source": "orientation.readiness + p_clarity",
    },
    "impact": {
        "label": "Decision impact",
        "description": "Потенциал сдвига решения клиента",
        "default_weight": 0.20,
        "source": "scores.overall_orientation",
    },
    "iroi": {
        "label": "Informational ROI",
        "description": "Ценность информации vs стоимость внедрения",
        "default_weight": 0.22,
        "source": "profit.info_roi (normalized)",
    },
    "vvi_health": {
        "label": "Void density (inverse)",
        "description": "Мало дыр в спеке = выше success",
        "default_weight": 0.12,
        "source": "1 - metrics.vvi",
    },
    "er_leverage": {
        "label": "Error leverage",
        "description": "Ошибки превращаются в улучшения",
        "default_weight": 0.10,
        "source": "metrics.er",
    },
    "rrc_elastic": {
        "label": "Refragmentation elasticity",
        "description": "Способность пересобрать структуру",
        "default_weight": 0.10,
        "source": "metrics.rrc",
    },
    "monetization_fit": {
        "label": "Monetization readiness",
        "description": "Готовность к promo / MM / paid path",
        "default_weight": 0.08,
        "source": "scores.promo_fit + axes.monetization_fit",
    },
}


@dataclass
class MetricPosition:
    """Позиция одной success-метрики в ТЗ запроса."""

    metric_id: str
    weight: float
    target: float  # желаемый уровень 0..1
    priority: int  # 1 = highest
    custom_label: str = ""
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SuccessMetricsTZ:
    """
    Уникальное ТЗ success-метрик для одного запроса.

    Влияет на:
    - scoring weights (как считаем composite)
    - Decision Core (когда switch mode)
    - Operational Analytics (shift / ricochet thresholds)
    """

    request_id: str
    positions: list[MetricPosition]
    composite_target: float = 0.65
    industry_bias: dict[str, float] = field(default_factory=dict)
    narrative: str = ""
    is_custom: bool = False

    def weight_map(self) -> dict[str, float]:
        raw = {p.metric_id: max(0.0, p.weight) for p in self.positions}
        s = sum(raw.values()) or 1.0
        return {k: v / s for k, v in raw.items()}

    def priority_order(self) -> list[str]:
        return [p.metric_id for p in sorted(self.positions, key=lambda x: x.priority)]

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "positions": [p.to_dict() for p in self.positions],
            "composite_target": self.composite_target,
            "industry_bias": self.industry_bias,
            "narrative": self.narrative,
            "is_custom": self.is_custom,
            "weight_map": self.weight_map(),
            "priority_order": self.priority_order(),
            "module": "Custom Success Metrics Positioning",
        }


@dataclass
class SuccessScorecard:
    """Оценки success-метрик после прогона."""

    values: dict[str, float]
    weighted_composite: float
    gaps: dict[str, float]
    hits_target: bool
    tz: dict[str, Any]
    influence: dict[str, Any]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SuccessMetricsPositioner:
    """
    Строит / применяет custom positioning success-метрик.

    Custom input example (в ClientRequest.success_metrics):
    {
      "weights": {"iroi": 0.35, "clarity": 0.2, ...},
      "targets": {"iroi": 0.7, "clarity": 0.6},
      "priority": ["iroi", "impact", "clarity"],
      "composite_target": 0.7
    }
    """

    name = "Custom Success Metrics Positioning"

    # industry soft bias (adds to default weights before renorm)
    INDUSTRY_BIAS: dict[str, dict[str, float]] = {
        "ai-agencies": {"monetization_fit": 0.04, "impact": 0.03},
        "cloud-economy": {"clarity": 0.03, "iroi": 0.04},
        "cost-engineering": {"vvi_health": 0.05, "er_leverage": 0.03},
        "chipmaking": {"vvi_health": 0.06, "rrc_elastic": 0.03},
        "telecom": {"clarity": 0.03, "monetization_fit": 0.03},
        "device-assembly": {"er_leverage": 0.04, "clarity": 0.02},
    }

    def build_tz(
        self,
        request_id: str,
        industry_id: str,
        custom: dict[str, Any] | None = None,
    ) -> SuccessMetricsTZ:
        custom = custom or {}
        weights_in = dict(custom.get("weights") or {})
        targets_in = dict(custom.get("targets") or {})
        priority_in = list(custom.get("priority") or [])
        composite_target = float(
            custom.get("composite_target")
            or METRIC_THRESHOLDS.get("info_roi_attractive", 1.8) / 4.0  # ~0.45 floor
        )
        # default composite target more intuitive
        if "composite_target" not in custom:
            composite_target = 0.62

        bias = dict(self.INDUSTRY_BIAS.get(industry_id, {}))
        is_custom = bool(weights_in or targets_in or priority_in or custom.get("composite_target"))

        positions: list[MetricPosition] = []
        for i, (mid, meta) in enumerate(DEFAULT_SUCCESS_METRIC_DEFS.items()):
            w = float(weights_in.get(mid, meta["default_weight"]))
            w += bias.get(mid, 0.0)
            tgt = float(targets_in.get(mid, 0.60 if mid != "iroi" else 0.55))
            if priority_in and mid in priority_in:
                pr = priority_in.index(mid) + 1
            else:
                pr = i + 1
            positions.append(
                MetricPosition(
                    metric_id=mid,
                    weight=max(0.01, w),
                    target=_clamp01(tgt),
                    priority=pr,
                    custom_label=str(custom.get("labels", {}).get(mid, meta["label"])),
                    notes=str(meta.get("description", "")),
                )
            )

        # renorm happens in weight_map()
        narrative = (
            f"{self.name}: TZ for request {request_id[:8]}… "
            f"industry={industry_id}, custom={is_custom}, "
            f"top={sorted(positions, key=lambda p: p.priority)[0].metric_id}, "
            f"composite_target={composite_target:.2f}."
        )
        return SuccessMetricsTZ(
            request_id=request_id,
            positions=positions,
            composite_target=_clamp01(composite_target),
            industry_bias=bias,
            narrative=narrative,
            is_custom=is_custom,
        )

    def score(
        self,
        tz: SuccessMetricsTZ,
        *,
        readiness: float,
        overall: float,
        info_roi: float,
        vvi: float,
        er: float,
        rrc: float,
        promo_fit: float,
        monetization_axis: float,
    ) -> SuccessScorecard:
        """Считает значения success-метрик и weighted composite."""
        values = {
            "clarity": _clamp01(readiness),
            "impact": _clamp01(overall),
            # IROI ~0..10 → 0..1
            "iroi": _clamp01(float(info_roi) / 5.0),
            "vvi_health": _clamp01(1.0 - float(vvi)),
            "er_leverage": _clamp01(er),
            "rrc_elastic": _clamp01(rrc),
            "monetization_fit": _clamp01(0.5 * promo_fit + 0.5 * monetization_axis),
        }
        wm = tz.weight_map()
        composite = sum(values.get(k, 0.0) * w for k, w in wm.items())
        gaps = {
            p.metric_id: round(max(0.0, p.target - values.get(p.metric_id, 0.0)), 4)
            for p in tz.positions
        }
        hits = composite >= tz.composite_target

        # influence vectors for other engines
        influence = {
            "scoring_multiplier": round(0.85 + 0.3 * composite, 4),
            "prefer_generative": gaps.get("impact", 0) > 0.15 or gaps.get("iroi", 0) > 0.2,
            "prefer_recursive_refine": gaps.get("vvi_health", 0) > 0.2
            or gaps.get("rrc_elastic", 0) > 0.15,
            "prefer_scoring_only": hits and gaps.get("clarity", 0) < 0.1,
            "decision_bias": tz.priority_order()[:3],
            "oae_shift_sensitivity": round(0.4 + wm.get("impact", 0.2) + wm.get("iroi", 0.2), 4),
            "oae_ricochet_gain": round(0.5 + wm.get("rrc_elastic", 0.1) * 1.5, 4),
        }

        summary = (
            f"{self.name}: composite={composite:.3f} "
            f"(target {tz.composite_target:.2f}) → "
            f"{'HIT' if hits else 'GAP'}; "
            f"worst_gap={max(gaps, key=gaps.get) if gaps else '—'}."
        )
        return SuccessScorecard(
            values={k: round(v, 4) for k, v in values.items()},
            weighted_composite=round(composite, 4),
            gaps=gaps,
            hits_target=hits,
            tz=tz.to_dict(),
            influence=influence,
            summary=summary,
        )


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))
