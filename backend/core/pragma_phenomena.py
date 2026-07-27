"""
Pragma Collection phenomena (2021 lineage) → recursive splitting method
=====================================================================

Когда обычный scoring «не дотягивает», а «прошивка метрик» (VVI/ER/RRC + success)
даёт **специфические комбинации индикаторов**, эти комбинации становятся
**точками расщепления (splitting points)** для рекурсивной генеративной
разработки идей — быстрый качественный demo mode.

Pragma = практический паттерн, который уже «работал»; здесь — мета-паттерны
рекурсии, а не только industry playbooks из PragmaVault.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SplittingPoint:
    """Точка, с которой запускается recursive generative branch."""

    id: str
    phenomenon: str
    condition: str
    severity: float
    branch_mode: str  # generative_development | recursive_refinement | dual_ricochet
    seed_hint: str
    pragma_ref: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PragmaPhenomenaResult:
    triggered: list[SplittingPoint]
    firmware_signature: str
    scoring_failed: bool
    demo_fast_path: bool
    method_notes: list[str]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": "Pragma Collection Phenomena (2021→Metrix)",
            "triggered": [t.to_dict() for t in self.triggered],
            "firmware_signature": self.firmware_signature,
            "scoring_failed": self.scoring_failed,
            "demo_fast_path": self.demo_fast_path,
            "method_notes": self.method_notes,
            "summary": self.summary,
        }


# ── Phenomenon library (combinations of metric firmware) ─────────────────────
# Each rule: name, predicate on context floats, branch, hint


def evaluate_pragma_phenomena(
    *,
    vvi: float,
    er: float,
    rrc: float,
    health: float,
    readiness: float,
    overall: float,
    info_roi: float,
    success_composite: float,
    success_target: float,
    product_fit: float,
    promo_fit: float,
) -> PragmaPhenomenaResult:
    """
    Анализирует «прошивку» метрик и возвращает splitting points.

    scoring_failed = success не достиг target ИЛИ overall низкий при высокой ambiguity.
    """
    triggered: list[SplittingPoint] = []
    notes: list[str] = []

    scoring_failed = (success_composite < success_target - 0.02) or (
        overall < 0.42 and readiness < 0.45
    )

    # Signature for logs / paid block later
    firmware_signature = (
        f"VVI{vvi:.2f}|ER{er:.2f}|RRC{rrc:.2f}|H{health:.2f}|"
        f"R{readiness:.2f}|O{overall:.2f}|I{info_roi:.1f}|S{success_composite:.2f}"
    )

    # ── P1: Void-rich + high ER → «productive voids» (classic pragma) ──────
    if vvi >= 0.40 and er >= 0.50:
        triggered.append(
            SplittingPoint(
                id="split_productive_void",
                phenomenon="productive_voids",
                condition="VVI≥0.40 ∧ ER≥0.50",
                severity=round(min(1.0, vvi * 0.6 + er * 0.4), 4),
                branch_mode="recursive_refinement",
                seed_hint="Turn voids into explicit acceptance criteria branches",
                pragma_ref="Pragma/2021: voids_as_constructors",
            )
        )
        notes.append("Productive voids: дыры — топливо для recursive refine")

    # ── P2: Low RRC + mid VVI → brittle structure → reverse refragment ─────
    if rrc < 0.48 and vvi >= 0.30:
        triggered.append(
            SplittingPoint(
                id="split_brittle_refrag",
                phenomenon="brittle_refragmentation",
                condition="RRC<0.48 ∧ VVI≥0.30",
                severity=round(min(1.0, (0.48 - rrc) + vvi * 0.3), 4),
                branch_mode="dual_ricochet",
                seed_hint="Reverse void ricochet: reassemble idea tree from double-bottom coords",
                pragma_ref="Pragma/2021: reverse_refragment_lattice",
            )
        )
        notes.append("Brittle structure → reverse void ricochet path")

    # ── P3: Scoring fails but IROI still ok → generative demo boost ───────
    if scoring_failed and info_roi >= 1.4:
        triggered.append(
            SplittingPoint(
                id="split_scoring_fail_generative",
                phenomenon="scoring_fail_generative",
                condition="success<target ∧ IROI≥1.4",
                severity=round(min(1.0, (success_target - success_composite) + 0.2), 4),
                branch_mode="generative_development",
                seed_hint="Scoring shelf insufficient — open generative branch on abstract coords",
                pragma_ref="Pragma/2021: fail_open_to_generate",
            )
        )
        notes.append("Scoring failed with salvageable IROI → generative development")

    # ── P4: High promo + low product → dual-surface idea (double bottom) ───
    if promo_fit >= 0.55 and product_fit < 0.50:
        triggered.append(
            SplittingPoint(
                id="split_double_bottom_promo",
                phenomenon="double_bottom_promo",
                condition="promo_fit≥0.55 ∧ product_fit<0.50",
                severity=round(promo_fit - product_fit, 4),
                branch_mode="generative_development",
                seed_hint="Double bottom: product seed + latent promo coordinate fly-out",
                pragma_ref="Pragma/2021: double_bottom_surface",
            )
        )
        notes.append("Double bottom: promo surface stronger than product surface")

    # ── P5: Healthy firmware — stay scoring, light polish ─────────────────
    if health >= 0.72 and success_composite >= success_target and not scoring_failed:
        triggered.append(
            SplittingPoint(
                id="split_stable_scoring",
                phenomenon="stable_scoring_hold",
                condition="health≥0.72 ∧ success≥target",
                severity=0.15,
                branch_mode="scoring",
                seed_hint="Hold scoring path; minor polish only",
                pragma_ref="Pragma/2021: do_not_overfit_recursion",
            )
        )
        notes.append("Stable hold — recursion not required")

    # ── P6: High VVI + low ER → blind voids (need constructor form) ────────
    if vvi >= 0.50 and er < 0.45:
        triggered.append(
            SplittingPoint(
                id="split_blind_void_constructor",
                phenomenon="blind_void_constructor",
                condition="VVI≥0.50 ∧ ER<0.45",
                severity=round(vvi * 0.7 + (0.45 - er), 4),
                branch_mode="recursive_refinement",
                seed_hint="Treat undefined params as constructor-of-form; assemble embedding",
                pragma_ref="Pragma/2021: constructor_of_certain_form",
            )
        )
        notes.append("Blind voids → constructor-of-form embedding assembly")

    demo_fast = any(
        t.branch_mode in ("generative_development", "dual_ricochet", "recursive_refinement")
        and t.severity >= 0.35
        for t in triggered
    ) or (scoring_failed and len(triggered) >= 1)

    if not triggered:
        notes.append("No pragma phenomenon fired — pure scoring path")

    summary = (
        f"Pragma phenomena: {len(triggered)} split(s), "
        f"scoring_failed={scoring_failed}, demo_fast={demo_fast}, "
        f"sig={firmware_signature[:40]}…"
    )
    return PragmaPhenomenaResult(
        triggered=triggered,
        firmware_signature=firmware_signature,
        scoring_failed=scoring_failed,
        demo_fast_path=demo_fast,
        method_notes=notes,
        summary=summary,
    )
