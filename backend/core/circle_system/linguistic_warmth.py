"""
Linguistic warmth scorer for *answers only*.

Assembly analysis of parameters is independent; warmth never overrides certainty.
"""

from __future__ import annotations

from typing import Any

from backend.core.circle_system.lexicon import WARMTH_BANDS, STATUS_LABELS
from backend.paid.types import clamp01


class LinguisticWarmthEngine:
    """Score and render answer warmth without changing parameter truth."""

    name = "Linguistic Warmth Engine"

    def score(
        self,
        *,
        assembly_score: float,
        certain_yes_ratio: float,
        client_energy: float = 0.5,
        lang: str = "ru",
    ) -> dict[str, Any]:
        # Warmth may rise only when assembly is solid; else stay cool/cold
        raw = (
            0.45 * clamp01(assembly_score)
            + 0.25 * clamp01(certain_yes_ratio)
            + 0.20 * clamp01(client_energy)
            + 0.10 * (0.5 if assembly_score >= 0.55 else 0.2)
        )
        if assembly_score < 0.35:
            raw = min(raw, 0.44)  # cap at cool when assembly weak
        warmth = clamp01(raw)
        band = self._band(warmth)
        meta = WARMTH_BANDS[band]
        lex = meta["lexemes_ru"] if lang.startswith("ru") else meta["lexemes_en"]
        return {
            "module": self.name,
            "warmth": round(warmth, 3),
            "band": band,
            "tone": meta["tone"],
            "lexemes": list(lex),
            "rule": meta["rule"],
            "cap_reason": "assembly_weak" if assembly_score < 0.35 else None,
            "note": "Warmth is linguistic presentation only; certainty status is independent.",
        }

    def render_answer(
        self,
        *,
        status: str,
        body_fact: str,
        next_action: str,
        warmth: dict[str, Any],
        lang: str = "ru",
    ) -> dict[str, Any]:
        labels = STATUS_LABELS.get(status, STATUS_LABELS["uncertain"])
        label = labels["ru"] if lang.startswith("ru") else labels["en"]
        opener = (warmth.get("lexemes") or ["fact:"])[0]
        if warmth.get("band") in ("cold", "cool"):
            text = f"{opener} [{label}] {body_fact} → {next_action}"
        elif warmth.get("band") == "hot":
            text = f"{opener}: [{label}] {body_fact}. {next_action}"
        else:
            text = f"{opener} [{label}] — {body_fact}. Next: {next_action}"
        return {
            "status": status,
            "label": label,
            "warmth_band": warmth.get("band"),
            "text": text,
            "body_fact": body_fact,
            "next_action": next_action,
        }

    @staticmethod
    def _band(score: float) -> str:
        for name, meta in WARMTH_BANDS.items():
            lo, hi = meta["score_range"]
            if lo <= score < hi:
                return name
        return "neutral"
