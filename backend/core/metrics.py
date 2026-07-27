"""
Ядровые метрики Metrix AI: VVI, ER, RRC.

VVI  — Vulnerability Void Index
       Насколько в спецификации / модели много «пустот» (дыры, неопределённости,
       уязвимости процесса). 0 = плотная спека, 1 = почти пусто.

ER   — Efficiency of Error
       Насколько обнаруженные ошибки и пробелы *полезны* для улучшения.
       Высокий ER = система учится на ошибках, а не тонет в них.

RRC  — Reverse Refragmentation Coefficient
       Насколько хорошо результат можно «разобрать обратно» и пересобрать
       в лучшую структуру (рефрагментация). Высокий RRC = живая система.

Все формулы прозрачные: вход → числа → bundle. Без чёрных ящиков.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Mapping, Sequence


@dataclass
class CoreMetrics:
    """Тройка VVI / ER / RRC + производные."""

    vvi: float
    er: float
    rrc: float
    health_score: float = 0.0
    labels: dict[str, str] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.vvi = _clamp01(self.vvi)
        self.er = _clamp01(self.er)
        self.rrc = _clamp01(self.rrc)
        # health: мало дыр + полезные ошибки + сильная пересборка
        self.health_score = _clamp01(
            (1.0 - self.vvi) * 0.40 + self.er * 0.30 + self.rrc * 0.30
        )
        self.labels = {
            "vvi": _label_vvi(self.vvi),
            "er": _label_er(self.er),
            "rrc": _label_rrc(self.rrc),
            "health": _label_health(self.health_score),
        }

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def improvement_vector(self) -> dict[str, float]:
        """Куда давить, чтобы улучшить систему (дефициты)."""
        return {
            "reduce_voids": self.vvi,
            "raise_error_efficiency": max(0.0, 1.0 - self.er),
            "raise_refragmentation": max(0.0, 1.0 - self.rrc),
        }


@dataclass
class MetricBundle:
    """Полный пакет метрик для ответа клиенту / агенту."""

    core: CoreMetrics
    info_roi: float = 0.0
    precision: float = 0.0
    speed_index: float = 0.0
    resource_efficiency: float = 0.0
    extras: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "core": self.core.to_dict(),
            "info_roi": round(self.info_roi, 4),
            "precision": round(self.precision, 4),
            "speed_index": round(self.speed_index, 4),
            "resource_efficiency": round(self.resource_efficiency, 4),
            "extras": self.extras,
        }


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _safe_div(a: float, b: float, default: float = 0.0) -> float:
    if abs(b) < 1e-12:
        return default
    return a / b


def _label_vvi(v: float) -> str:
    if v < 0.25:
        return "dense"
    if v < 0.45:
        return "manageable"
    if v < 0.70:
        return "porous"
    return "critical_voids"


def _label_er(v: float) -> str:
    if v >= 0.75:
        return "highly_leveraged"
    if v >= 0.55:
        return "productive"
    if v >= 0.35:
        return "mixed"
    return "noise_heavy"


def _label_rrc(v: float) -> str:
    if v >= 0.70:
        return "elastic"
    if v >= 0.50:
        return "reconfigurable"
    if v >= 0.30:
        return "rigid"
    return "brittle"


def _label_health(v: float) -> str:
    if v >= 0.75:
        return "excellent"
    if v >= 0.55:
        return "good"
    if v >= 0.35:
        return "needs_work"
    return "fragile"


# ── Формулы ───────────────────────────────────────────────────────────────────


def compute_vvi(
    known_params: int,
    required_params: int,
    ambiguity_score: float = 0.0,
    conflict_score: float = 0.0,
    missing_critical: int = 0,
) -> float:
    """
    VVI = weighted voids in the specification space.

    void_ratio   = 1 - known/required
    ambiguity    = [0..1] linguistic / conceptual blur
    conflict     = [0..1] contradictions between params
    critical_gap = missing critical params normalized
    """
    required_params = max(1, int(required_params))
    known_params = max(0, int(known_params))
    void_ratio = 1.0 - min(1.0, known_params / required_params)
    critical_gap = _clamp01(missing_critical / max(1, required_params * 0.25))
    ambiguity_score = _clamp01(ambiguity_score)
    conflict_score = _clamp01(conflict_score)

    vvi = (
        void_ratio * 0.40
        + ambiguity_score * 0.25
        + conflict_score * 0.20
        + critical_gap * 0.15
    )
    return _clamp01(vvi)


def compute_er(
    detected_errors: int,
    actionable_errors: int,
    false_positives: int = 0,
    improvement_delta: float = 0.0,
) -> float:
    """
    ER — Efficiency of Error.

    actionable_ratio = actionable / detected
    fp_penalty       = false positives dilute signal
    improvement      = measured quality gain after fixing
    """
    detected_errors = max(0, int(detected_errors))
    if detected_errors == 0:
        # Нет ошибок — либо идеально, либо слепо. Даём нейтральный «здоровый» ER.
        return _clamp01(0.50 + improvement_delta * 0.3)

    actionable_errors = max(0, min(actionable_errors, detected_errors))
    false_positives = max(0, int(false_positives))
    actionable_ratio = actionable_errors / detected_errors
    fp_ratio = min(1.0, false_positives / detected_errors)
    improvement_delta = _clamp01(improvement_delta)

    er = actionable_ratio * 0.55 + (1.0 - fp_ratio) * 0.20 + improvement_delta * 0.25
    return _clamp01(er)


def compute_rrc(
    fragments: int,
    successful_reassemblies: int,
    structure_entropy: float = 0.5,
    reverse_links: int = 0,
    forward_links: int = 1,
) -> float:
    """
    RRC — Reverse Refragmentation Coefficient.

    reassembly_rate = successful / fragments
    reverse_density = reverse links / forward (can go back)
    entropy_fit     = mid entropy is best (too rigid / too chaotic hurts)
    """
    fragments = max(1, int(fragments))
    successful_reassemblies = max(0, int(successful_reassemblies))
    reassembly_rate = min(1.0, successful_reassemblies / fragments)
    forward_links = max(1, int(forward_links))
    reverse_density = _clamp01(reverse_links / forward_links)
    # entropy peak around 0.5
    entropy_fit = 1.0 - abs(_clamp01(structure_entropy) - 0.5) * 2.0

    rrc = reassembly_rate * 0.50 + reverse_density * 0.30 + entropy_fit * 0.20
    return _clamp01(rrc)


def compute_core_metrics(
    *,
    known_params: int = 0,
    required_params: int = 10,
    ambiguity_score: float = 0.2,
    conflict_score: float = 0.1,
    missing_critical: int = 0,
    detected_errors: int = 0,
    actionable_errors: int = 0,
    false_positives: int = 0,
    improvement_delta: float = 0.0,
    fragments: int = 4,
    successful_reassemblies: int = 2,
    structure_entropy: float = 0.5,
    reverse_links: int = 2,
    forward_links: int = 4,
    notes: Sequence[str] | None = None,
) -> CoreMetrics:
    """Собрать CoreMetrics из «сырых» сигналов пайплайна."""
    vvi = compute_vvi(
        known_params, required_params, ambiguity_score, conflict_score, missing_critical
    )
    er = compute_er(detected_errors, actionable_errors, false_positives, improvement_delta)
    rrc = compute_rrc(
        fragments, successful_reassemblies, structure_entropy, reverse_links, forward_links
    )
    m = CoreMetrics(vvi=vvi, er=er, rrc=rrc)
    if notes:
        m.notes.extend(notes)
    m.notes.append(
        f"VVI={m.vvi:.3f} ({m.labels['vvi']}), "
        f"ER={m.er:.3f} ({m.labels['er']}), "
        f"RRC={m.rrc:.3f} ({m.labels['rrc']}), "
        f"health={m.health_score:.3f}"
    )
    return m


def blend_metrics(parts: Iterable[CoreMetrics], weights: Sequence[float] | None = None) -> CoreMetrics:
    """Взвешенное смешивание нескольких CoreMetrics (зоны → продукт)."""
    parts = list(parts)
    if not parts:
        return CoreMetrics(vvi=0.5, er=0.5, rrc=0.5)
    if weights is None:
        weights = [1.0] * len(parts)
    if len(weights) != len(parts):
        raise ValueError("weights length must match parts")
    tw = sum(weights) or 1.0
    vvi = sum(p.vvi * w for p, w in zip(parts, weights)) / tw
    er = sum(p.er * w for p, w in zip(parts, weights)) / tw
    rrc = sum(p.rrc * w for p, w in zip(parts, weights)) / tw
    return CoreMetrics(vvi=vvi, er=er, rrc=rrc, notes=["blended from zone metrics"])


def informational_roi(
    impact: float,
    scalability: float,
    long_term_value: float,
    implementation_cost: float,
    risk_factor: float = 0.15,
    novelty_bonus: float = 0.0,
) -> float:
    """
    Информационный ROI (не денежный P&L, а ценность информации/идеи).

    IROI = (impact * scalability * long_term * (1 + novelty)) / (cost * (1 + risk))

    Все входы нормализуются в [0..1], cost минимум 0.05 чтобы не делить на 0.
    """
    impact = _clamp01(impact)
    scalability = _clamp01(scalability)
    long_term_value = _clamp01(long_term_value)
    novelty_bonus = _clamp01(novelty_bonus)
    risk_factor = _clamp01(risk_factor)
    cost = max(0.05, _clamp01(implementation_cost))

    numerator = impact * scalability * long_term_value * (1.0 + novelty_bonus)
    denominator = cost * (1.0 + risk_factor)
    # scale to a readable band ~0..10
    raw = _safe_div(numerator, denominator, 0.0) * 4.0
    return round(min(10.0, raw), 4)


def entropy_of_weights(weights: Mapping[str, float] | Sequence[float]) -> float:
    """Нормализованная энтропия (0..1) для структуры идей / параметров."""
    if isinstance(weights, Mapping):
        vals = [max(0.0, float(v)) for v in weights.values()]
    else:
        vals = [max(0.0, float(v)) for v in weights]
    s = sum(vals)
    if s <= 0 or len(vals) < 2:
        return 0.0
    probs = [v / s for v in vals if v > 0]
    if not probs:
        return 0.0
    h = -sum(p * math.log(p + 1e-15) for p in probs)
    h_max = math.log(len(probs))
    return _clamp01(_safe_div(h, h_max, 0.0))
