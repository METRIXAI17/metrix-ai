"""
Problem Recognition — lattice of client problems ranked by leverage.

Borrowed pattern from business ops: diagnose → prioritize → compose response.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


# Industry-biased problem templates (ontology seeds, not a solution DB)
INDUSTRY_PROBLEMS: dict[str, list[dict[str, Any]]] = {
    "ai-agencies": [
        {
            "id": "agent_chaos",
            "title": "Agent / delivery chaos without control loop",
            "title_ru": "Хаос агентов / сдачи без control loop",
            "family": "ops",
            "default_severity": 0.72,
            "signal_keys": ["ops_friction", "quality_risk"],
            "product_hook": "terminal_teammate",
        },
        {
            "id": "margin_leak_delivery",
            "title": "Margin leak in multi-step delivery",
            "title_ru": "Утечка маржи в многошаговой сдаче",
            "family": "cost",
            "default_severity": 0.65,
            "signal_keys": ["cost_pressure", "ops_friction"],
            "product_hook": "terminal_teammate",
        },
        {
            "id": "buyer_proof_gap",
            "title": "No buyer fin-model proof for Teammate sale",
            "title_ru": "Нет fin-model proof для продажи Teammate",
            "family": "promo",
            "default_severity": 0.55,
            "signal_keys": ["demand_signal"],
            "product_hook": "buyer_fin_model",
        },
    ],
    "api-for-devs": [
        {
            "id": "api_burn",
            "title": "Third-party API cost burn under quality floor",
            "title_ru": "Выгорание API-бюджета при quality floor",
            "family": "cost",
            "default_severity": 0.78,
            "signal_keys": ["cost_pressure"],
            "product_hook": "api_integration_map",
        },
        {
            "id": "integration_void",
            "title": "Integration map / TZ voids",
            "title_ru": "Пустоты карты интеграций / ТЗ",
            "family": "product",
            "default_severity": 0.62,
            "signal_keys": ["product_void", "quality_risk"],
            "product_hook": "api_integration_map",
        },
    ],
    "cloud-economy": [
        {
            "id": "api_burn",
            "title": "Third-party API cost burn under quality floor",
            "family": "cost",
            "default_severity": 0.78,
            "signal_keys": ["cost_pressure"],
            "product_hook": "api_integration_map",
        },
    ],
    "cost-engineering": [
        {
            "id": "param_waste",
            "title": "Waste parameters inflate rework cost",
            "title_ru": "Лишние параметры раздувают rework",
            "family": "ops",
            "default_severity": 0.7,
            "signal_keys": ["cost_pressure", "ops_friction"],
            "product_hook": "parameter_void_scanner",
        },
    ],
    "chipmaking": [
        {
            "id": "design_loop_void",
            "title": "Design-loop voids before tapeout",
            "family": "product",
            "default_severity": 0.74,
            "signal_keys": ["product_void", "quality_risk"],
            "product_hook": "yield_geometry_twin",
        },
    ],
    "telecom": [
        {
            "id": "sla_arpu_fog",
            "title": "SLA / ARPU levers hidden in spreadsheet fog",
            "family": "ops",
            "default_severity": 0.68,
            "signal_keys": ["ops_friction", "demand_signal"],
            "product_hook": "sla_native_sku_builder",
        },
    ],
    "device-assembly": [
        {
            "id": "station_rework",
            "title": "Station setup rework blocks scale",
            "family": "ops",
            "default_severity": 0.66,
            "signal_keys": ["ops_friction", "scale_intent"],
            "product_hook": "config_workflow",
        },
    ],
    "asset-decisions": [
        {
            "id": "decision_cognition_gap",
            "title": "No metric/risk pack for asset decisions",
            "family": "product",
            "default_severity": 0.7,
            "signal_keys": ["product_void", "quality_risk"],
            "product_hook": "decision_support_desk",
        },
    ],
    "freelace-d2c": [
        {
            "id": "doc_liquidity_gap",
            "title": "Idea never becomes freelace-ready document",
            "family": "liquidity",
            "default_severity": 0.72,
            "signal_keys": ["liquidity", "product_void"],
            "product_hook": "workspace_offramp",
        },
    ],
    "d2c-offramp": [
        {
            "id": "doc_liquidity_gap",
            "title": "Idea never becomes freelace-ready document",
            "family": "liquidity",
            "default_severity": 0.72,
            "signal_keys": ["liquidity", "product_void"],
            "product_hook": "workspace_offramp",
        },
    ],
    "expert-services": [
        {
            "id": "offer_pack_void",
            "title": "Expert offer not packaged as sellable TZ",
            "family": "promo",
            "default_severity": 0.6,
            "signal_keys": ["demand_signal", "product_void"],
            "product_hook": "offer_pack",
        },
    ],
    "ecommerce": [
        {
            "id": "unit_econ_fog",
            "title": "Unit economics fog on SKU / channel",
            "family": "cost",
            "default_severity": 0.64,
            "signal_keys": ["cost_pressure", "demand_signal"],
            "product_hook": "unit_econ_map",
        },
    ],
}

# Universal fallbacks
UNIVERSAL: list[dict[str, Any]] = [
    {
        "id": "readiness_gap",
        "title": "Execution readiness below pilot threshold",
        "title_ru": "Готовность ниже порога пилота",
        "family": "ops",
        "default_severity": 0.5,
        "signal_keys": ["ops_friction", "product_void"],
        "product_hook": "orientation_run",
    },
    {
        "id": "metric_blindness",
        "title": "No composed success metrics for this situation",
        "title_ru": "Нет собранных success-метрик под ситуацию",
        "family": "metrics",
        "default_severity": 0.48,
        "signal_keys": ["quality_risk"],
        "product_hook": "success_tz",
    },
]


@dataclass
class RecognizedProblem:
    id: str
    title: str
    family: str
    severity: float
    confidence: float
    product_hook: str
    evidence_signals: dict[str, float] = field(default_factory=dict)
    failure_mode: str = ""
    leverage: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProblemLattice:
    module: str
    problems: list[RecognizedProblem]
    primary: RecognizedProblem | None
    family_pressure: dict[str, float]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "problems": [p.to_dict() for p in self.problems],
            "primary": self.primary.to_dict() if self.primary else None,
            "family_pressure": {k: round(v, 4) for k, v in self.family_pressure.items()},
            "summary": self.summary,
        }


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


class ProblemRecognition:
    """Recognize and rank problems from system-reader signals + voids."""

    name = "Problem Recognition"

    def recognize(
        self,
        *,
        industry_id: str,
        signals: dict[str, float],
        voids: list[str] | None = None,
        readiness_band: str = "orientation_needed",
        scores: dict[str, float] | None = None,
    ) -> ProblemLattice:
        voids = voids or []
        scores = scores or {}
        templates = list(INDUSTRY_PROBLEMS.get(industry_id) or [])
        templates.extend(UNIVERSAL)

        problems: list[RecognizedProblem] = []
        for t in templates:
            sig_keys = list(t.get("signal_keys") or [])
            ev = {k: float(signals.get(k, 0.0)) for k in sig_keys}
            sig_avg = sum(ev.values()) / max(1, len(ev)) if ev else 0.2
            base = float(t.get("default_severity") or 0.5)
            void_boost = 0.08 * sum(
                1 for v in voids if any(k.split("_")[0] in v for k in sig_keys)
            )
            readiness_pen = 0.0
            if readiness_band in ("intake_thin", "orientation_needed"):
                readiness_pen = 0.08
            severity = _clamp01(base * 0.55 + sig_avg * 0.4 + void_boost + readiness_pen)
            conf = _clamp01(0.35 + sig_avg * 0.5 + (0.1 if voids else 0.0))
            # leverage ≈ severity × conf × inverse product fit (harder fit = more room)
            product_fit = float(scores.get("product_fit", 0.5))
            leverage = _clamp01(severity * conf * (0.55 + (1.0 - product_fit) * 0.45))
            failure = {
                "ops": "control_loop_collapse",
                "cost": "unit_econ_spiral",
                "product": "spec_void_expansion",
                "promo": "proof_starvation",
                "liquidity": "document_stall",
                "metrics": "metric_drift",
            }.get(str(t.get("family")), "unscoped_degradation")
            problems.append(
                RecognizedProblem(
                    id=str(t["id"]),
                    title=str(t.get("title") or t["id"]),
                    family=str(t.get("family") or "ops"),
                    severity=severity,
                    confidence=conf,
                    product_hook=str(t.get("product_hook") or ""),
                    evidence_signals=ev,
                    failure_mode=failure,
                    leverage=leverage,
                )
            )

        # de-dupe by id keep max leverage
        by_id: dict[str, RecognizedProblem] = {}
        for p in problems:
            prev = by_id.get(p.id)
            if prev is None or p.leverage > prev.leverage:
                by_id[p.id] = p
        ranked = sorted(by_id.values(), key=lambda p: (-p.leverage, -p.severity))
        # keep top 6
        ranked = ranked[:6]

        family_pressure: dict[str, float] = {}
        for p in ranked:
            family_pressure[p.family] = family_pressure.get(p.family, 0.0) + p.severity
        for k in list(family_pressure):
            family_pressure[k] = _clamp01(family_pressure[k] / 1.5)

        primary = ranked[0] if ranked else None
        summary = (
            f"ProblemRecognition: n={len(ranked)}; primary="
            + (f"{primary.id} sev={primary.severity:.2f} lev={primary.leverage:.2f}" if primary else "none")
        )
        return ProblemLattice(
            module=self.name,
            problems=ranked,
            primary=primary,
            family_pressure=family_pressure,
            summary=summary,
        )
