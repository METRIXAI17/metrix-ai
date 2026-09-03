"""
Global step 1–2: complex-text → parameters; indirect re-pass as CERTAIN YES / NO / U.

Indirect pass uses secondary signals (absence, hedges, contradictions), not only
direct yes/no words.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

from backend.core.circle_system.lexicon import (
    CERTAIN_NO_RU,
    CERTAIN_YES_RU,
    LAYER_NEED_MARKERS,
    STATUS_LABELS,
    UNCERTAIN_RU,
    detect_markers,
)
from backend.paid.types import clamp01


# Core parameter slots developed from complex text
PARAM_SLOTS = (
    "goal",
    "client_segment",
    "offer",
    "constraint",
    "resource",
    "metric",
    "timeline",
    "integration",
    "pilot_scope",
    "success_criterion",
)

SLOT_HINTS: dict[str, tuple[str, ...]] = {
    "goal": ("цель", "хотим", "нужно", "goal", "want", "need to", "задача"),
    "client_segment": ("клиент", "ниша", "сегмент", "b2b", "b2c", "audience", "buyer"),
    "offer": ("оффер", "продукт", "услуга", "offer", "sku", "пакет", "deliverable"),
    "constraint": ("огранич", "нельзя", "бюджет до", "deadline", "constraint", "лимит"),
    "resource": ("есть", "команда", "стек", "бюджет", "resource", "already have"),
    "metric": ("kpi", "метрик", "roi", "конверс", "%", "metric", "измер"),
    "timeline": ("срок", "дней", "недел", "месяц", "timeline", "q1", "q2", "asap"),
    "integration": ("интегр", "api", "crm", "webhook", "подключ", "ledger"),
    "pilot_scope": ("пилот", "pilot", "mvp", "пробн", "14", "30"),
    "success_criterion": ("успех", "если", "accept", "критер", "done when", "готовый"),
}


def _count_hits(text: str, words: tuple[str, ...]) -> int:
    low = text.lower()
    return sum(1 for w in words if w.lower() in low)


def _sentences(text: str) -> list[str]:
    parts = re.split(r"[.!?\n]+", text or "")
    return [p.strip() for p in parts if len(p.strip()) >= 8]


def _param_id(slot: str, snippet: str) -> str:
    h = hashlib.sha1(f"{slot}:{snippet[:80]}".encode("utf-8")).hexdigest()[:8]
    return f"p_{slot}_{h}"


class CertaintyAnalyzer:
    """
    Develop suitable parameters from complex text, then re-analyze each
    parameter with indirect certainty (ТОЧНО ДА / ТОЧНО НЕТ / U).
    """

    name = "Certainty Analyzer (params + indirect CY/CN/U)"

    def run(
        self,
        text: str,
        *,
        industry_id: str = "",
        lang: str = "ru",
        artefact_priors: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        text = text or ""
        sentences = _sentences(text)
        layers = detect_markers(text, LAYER_NEED_MARKERS)

        # Step 1: develop parameters
        params: list[dict[str, Any]] = []
        for slot in PARAM_SLOTS:
            hints = SLOT_HINTS[slot]
            matched = [s for s in sentences if any(h in s.lower() for h in hints)]
            if not matched and slot in ("goal", "offer", "metric"):
                # force skeleton slots even if weak signal
                snippet = sentences[0] if sentences else text[:120]
                strength = 0.15
            elif matched:
                snippet = matched[0][:220]
                strength = min(1.0, 0.35 + 0.2 * len(matched))
            else:
                continue
            params.append(
                {
                    "id": _param_id(slot, snippet),
                    "slot": slot,
                    "snippet": snippet,
                    "extract_strength": round(strength, 3),
                    "source_hits": len(matched),
                }
            )

        # If still empty, synthesize minimal parameter set from whole text
        if not params and text.strip():
            for slot in ("goal", "offer", "constraint", "pilot_scope"):
                params.append(
                    {
                        "id": _param_id(slot, text[:40]),
                        "slot": slot,
                        "snippet": text[:180],
                        "extract_strength": 0.12,
                        "source_hits": 0,
                    }
                )

        # Step 2: indirect certainty pass
        cy = _count_hits(text, CERTAIN_YES_RU)
        cn = _count_hits(text, CERTAIN_NO_RU)
        uu = _count_hits(text, UNCERTAIN_RU)
        digit_density = len(re.findall(r"\d+", text)) / max(1, len(text.split()))

        analyzed: list[dict[str, Any]] = []
        for p in params:
            sn = p["snippet"].lower()
            local_cy = _count_hits(sn, CERTAIN_YES_RU)
            local_cn = _count_hits(sn, CERTAIN_NO_RU)
            local_u = _count_hits(sn, UNCERTAIN_RU)
            has_number = bool(re.search(r"\d", sn))
            has_hedge = any(h in sn for h in ("примерно", "около", "maybe", "or ", "или "))
            has_neg = any(h in sn for h in ("не ", "нет", "without", "no "))
            # Presence of concrete offer/scope language raises indirect yes
            concrete = any(
                w in sn
                for w in (
                    "есть", "бюджет", "срок", "оффер", "цель", "usd", "руб",
                    "have", "budget", "offer", "goal", "metric", "пилот", "pilot",
                )
            )

            # Indirect signals (secondary pass — not only yes/no words)
            indirect_yes = 0.0
            indirect_no = 0.0
            if has_number and not has_hedge:
                indirect_yes += 0.3
            if concrete and not has_hedge and not has_neg:
                indirect_yes += 0.25
            if p["extract_strength"] >= 0.55 and not has_hedge:
                indirect_yes += 0.2
            if local_cy:
                indirect_yes += 0.35
            if has_hedge or local_u:
                indirect_yes -= 0.15
            if has_neg and local_cn == 0 and not local_cy:
                indirect_no += 0.25
            if local_cn:
                indirect_no += 0.4
            if p["source_hits"] == 0 and not concrete:
                indirect_no += 0.1

            yes_score = clamp01(0.35 * local_cy + indirect_yes + 0.1 * digit_density)
            no_score = clamp01(0.35 * local_cn + indirect_no)
            unc_score = clamp01(
                0.3 + 0.2 * local_u + (0.25 if has_hedge else 0) - 0.35 * max(yes_score, no_score)
            )
            # Artefact cy_cn_u_hint is a PRIOR only — never the truth.
            for ap in artefact_priors or []:
                hint = str(ap.get("cy_cn_u_hint") or "U").upper()
                affects = ap.get("affects") or []
                form_slot = p.get("slot")
                if form_slot not in affects and p.get("slot") not in affects:
                    continue
                if hint == "U" or ap.get("evidence_grade") == "contested":
                    unc_score = clamp01(unc_score + 0.08)
                    yes_score = clamp01(yes_score - 0.04)
                elif hint == "CY":
                    yes_score = clamp01(yes_score + 0.08)  # cannot alone flip ≥0.55 from 0
                elif hint == "CN":
                    no_score = clamp01(no_score + 0.08)

            if yes_score >= 0.55 and yes_score > no_score and yes_score > unc_score:
                status = "certain_yes"
            elif no_score >= 0.55 and no_score > yes_score:
                status = "certain_no"
            else:
                status = "uncertain"

            labels = STATUS_LABELS[status]
            analyzed.append(
                {
                    **p,
                    "status": status,
                    "label": labels["ru"] if lang.startswith("ru") else labels["en"],
                    "code": labels["code"],
                    "scores": {
                        "yes": round(yes_score, 3),
                        "no": round(no_score, 3),
                        "uncertain": round(unc_score, 3),
                    },
                    "indirect_signals": {
                        "has_number": has_number,
                        "has_hedge": has_hedge,
                        "has_negation": has_neg,
                    },
                }
            )

        buckets = {
            "certain_yes": [a for a in analyzed if a["status"] == "certain_yes"],
            "certain_no": [a for a in analyzed if a["status"] == "certain_no"],
            "uncertain": [a for a in analyzed if a["status"] == "uncertain"],
        }

        return {
            "module": self.name,
            "global_step": "1_2_params_and_indirect_certainty",
            "industry_id": industry_id,
            "ref": "ref_3:points_1_2_3_4",
            "text_stats": {
                "sentences": len(sentences),
                "certain_yes_markers": cy,
                "certain_no_markers": cn,
                "uncertain_markers": uu,
                "digit_density": round(digit_density, 4),
            },
            "layer_needs_detected": layers,
            "parameters": analyzed,
            "buckets": {
                k: [{"id": x["id"], "slot": x["slot"], "label": x["label"]} for x in v]
                for k, v in buckets.items()
            },
            "counts": {k: len(v) for k, v in buckets.items()},
            "uncertain_ids": [a["id"] for a in buckets["uncertain"]],
        }
