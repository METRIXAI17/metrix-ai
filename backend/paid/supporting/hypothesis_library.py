"""
Hypothesis Library — iterative navigator (step 15 + scoring for step 5).

Forms with every new iteration by calculating variants of the previous stage.
Acts as a smart navigator that:
  1) deeply analyzes ONE previous step,
  2) searches patterns / generalizations across a GROUP of previous steps,
  3) uses derivative-sensitivity-inspired formulas with lightweight learning (EMA).

Does not spin heavy recursive cycles — one navigation pass per request
(plus optional prior LearningState from a previous iteration).
"""

from __future__ import annotations

import math
from typing import Any

from backend.paid.types import LearningState, clamp01, safe_float


def _softmax(xs: list[float], temp: float = 0.85) -> list[float]:
    if not xs:
        return []
    t = max(0.15, temp)
    m = max(xs)
    exps = [math.exp((x - m) / t) for x in xs]
    s = sum(exps) or 1.0
    return [e / s for e in exps]


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    keys = set(a) | set(b)
    if not keys:
        return 0.0
    dot = sum(safe_float(a.get(k)) * safe_float(b.get(k)) for k in keys)
    na = math.sqrt(sum(safe_float(a.get(k)) ** 2 for k in keys)) or 1e-9
    nb = math.sqrt(sum(safe_float(b.get(k)) ** 2 for k in keys)) or 1e-9
    return max(-1.0, min(1.0, dot / (na * nb)))


class HypothesisLibrary:
    """
    Iterative navigator over hypothesis space.

    Selection score (learning-weighted):

      S_i = α·conf_i
          + β·exp(-d_i / σ)                    # proximity to root
          + γ·Σ_j w_j · |∂F/∂x_j| · cov(i,j)  # sensitivity alignment
          + δ·pattern_match_i
          + ε·ema_boost_i
          − ζ·tension_penalty_i

    EMA update (learning element):
      ema[lever] ← (1-λ)·ema[lever] + λ·|∂F/∂lever| · outcome

    OPEN: cross-request durable library store (disk/db) left for later.
    """

    name = "Hypothesis Library"

    def __init__(
        self,
        alpha: float = 0.28,
        beta: float = 0.24,
        gamma: float = 0.22,
        delta: float = 0.14,
        epsilon: float = 0.12,
        zeta: float = 0.15,
        ema_lambda: float = 0.35,
    ) -> None:
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.epsilon = epsilon
        self.zeta = zeta
        self.ema_lambda = ema_lambda

    def score_hypotheses(
        self,
        hypotheses: list[dict[str, Any]],
        *,
        sensitivities: list[dict[str, Any]] | None = None,
        root_alignment: float = 0.5,
        learning: LearningState | None = None,
        mega_points: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """Rank / re-score hypothesis modules with navigator formulas."""
        learning = learning or LearningState()
        sens = sensitivities or []
        sens_map = {
            str(s.get("parameter")): abs(safe_float(s.get("derivative")))
            for s in sens
        }
        # normalize sensitivities
        smax = max(sens_map.values()) if sens_map else 1.0
        sens_n = {k: v / smax for k, v in sens_map.items()}

        dist_by_id = {
            str(p.get("hypothesis_id")): safe_float(p.get("distance_to_root"), 0.5)
            for p in (mega_points or [])
            if p.get("hypothesis_id") != "root_task"
        }

        scored: list[dict[str, Any]] = []
        for h in hypotheses:
            conf = clamp01(safe_float(h.get("confidence"), 0.5))
            hid = str(h.get("id") or "")
            d = dist_by_id.get(hid, 0.45)
            proximity = math.exp(-d / 0.55)

            # Sensitivity alignment: indicators that mention top levers
            indicators = " ".join(h.get("supporting_indicators") or []) + " " + str(
                h.get("source") or ""
            )
            cov = 0.0
            for lever, sn in sens_n.items():
                if lever[:4] in indicators or lever in indicators:
                    cov += sn
                # soft: product/model sources get model_fit / impact leverage
                if lever in ("impact", "clarity") and "product" in str(h.get("source")):
                    cov += 0.5 * sn
                if lever in ("model_fit", "param_coverage") and "fin_model" in str(
                    h.get("source")
                ):
                    cov += 0.5 * sn
            sens_term = clamp01(cov / max(1.0, 0.5 * len(sens_n) or 1.0))

            # Pattern match vs library pattern weights
            source = str(h.get("source") or "unknown")
            pattern_match = clamp01(
                0.5
                + 0.5 * safe_float(learning.pattern_weights.get(source), 0.0)
            )

            # EMA boost from useful levers appearing in claim
            claim = str(h.get("claim") or "").lower()
            ema_boost = 0.0
            for lever, ema_v in learning.lever_ema.items():
                if lever[:5].lower() in claim or lever.lower() in claim:
                    ema_boost = max(ema_boost, clamp01(ema_v))
            if not learning.lever_ema:
                ema_boost = 0.35 * conf

            tension = 0.12 * len(h.get("tension_with") or [])

            S = (
                self.alpha * conf
                + self.beta * proximity
                + self.gamma * sens_term
                + self.delta * pattern_match
                + self.epsilon * ema_boost
                - self.zeta * tension
                + 0.05 * root_alignment
            )
            item = dict(h)
            item["navigator_score"] = round(S, 4)
            item["navigator_terms"] = {
                "confidence": round(conf, 4),
                "proximity": round(proximity, 4),
                "sensitivity_align": round(sens_term, 4),
                "pattern_match": round(pattern_match, 4),
                "ema_boost": round(ema_boost, 4),
                "tension_penalty": round(tension, 4),
            }
            scored.append(item)

        scored.sort(key=lambda x: x.get("navigator_score", 0), reverse=True)
        # Softmax pick weights for transparency
        weights = _softmax([safe_float(x.get("navigator_score")) for x in scored])
        for i, w in enumerate(weights):
            scored[i]["pick_weight"] = round(w, 4)
        return scored

    def deep_analyze_previous_step(
        self,
        step_trace: list[dict[str, Any]],
        *,
        focus_step: int | None = None,
    ) -> dict[str, Any]:
        """Deep analysis of one previous step (default: last completed)."""
        if not step_trace:
            return {
                "focus_step": None,
                "finding": "No previous step to analyze.",
                "leverage_hints": [],
            }
        # Prefer explicit focus, else last step with status ok
        target = None
        if focus_step is not None:
            for s in step_trace:
                if s.get("step") == focus_step:
                    target = s
                    break
        if target is None:
            for s in reversed(step_trace):
                if s.get("status") == "ok":
                    target = s
                    break
        target = target or step_trace[-1]

        payload = target.get("payload") or {}
        # Extract numeric density as complexity of step
        flat_nums: list[float] = []

        def walk(obj: Any, depth: int = 0) -> None:
            if depth > 4:
                return
            if isinstance(obj, (int, float)) and not isinstance(obj, bool):
                flat_nums.append(float(obj))
            elif isinstance(obj, dict):
                for v in list(obj.values())[:20]:
                    walk(v, depth + 1)
            elif isinstance(obj, list):
                for v in obj[:20]:
                    walk(v, depth + 1)

        walk(payload)
        mean_n = sum(flat_nums) / len(flat_nums) if flat_nums else 0.0
        var_n = (
            sum((x - mean_n) ** 2 for x in flat_nums) / len(flat_nums)
            if flat_nums
            else 0.0
        )
        finding = (
            f"Step {target.get('step')} «{target.get('name')}» "
            f"[{target.get('stage')}]: numeric_mass={len(flat_nums)}, "
            f"mean={mean_n:.3f}, var={var_n:.3f}."
        )
        leverage_hints: list[str] = []
        if "sensitivity" in str(payload).lower() or target.get("step") == 7:
            leverage_hints.append("Function sensitivity plane is high-leverage for next pick")
        if target.get("step") == 8:
            leverage_hints.append("Energy redistribution should reweight zone-linked hypotheses")
        if target.get("step") == 10:
            leverage_hints.append("Mega Map distances should dominate proximity term next iter")
        if not leverage_hints:
            leverage_hints.append("Carry step summary into pattern weights")

        return {
            "focus_step": target.get("step"),
            "focus_name": target.get("name"),
            "stage": target.get("stage"),
            "finding": finding,
            "numeric_mass": len(flat_nums),
            "mean": round(mean_n, 4),
            "variance": round(var_n, 4),
            "leverage_hints": leverage_hints,
        }

    def group_patterns(
        self,
        step_trace: list[dict[str, Any]],
        *,
        hypotheses: list[dict[str, Any]] | None = None,
        sensitivities: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Patterns and generalizations across the group of previous steps.

        Uses stage-level score vectors and source co-occurrence.
        """
        stage_hits: dict[str, int] = {}
        for s in step_trace:
            st = str(s.get("stage") or "unknown")
            stage_hits[st] = stage_hits.get(st, 0) + 1

        source_hits: dict[str, int] = {}
        for h in hypotheses or []:
            src = str(h.get("source") or "unknown")
            source_hits[src] = source_hits.get(src, 0) + 1

        # Generalization: if function + energy both ok → "compute_energy_stable"
        names_ok = {s.get("step") for s in step_trace if s.get("status") == "ok"}
        generalizations: list[str] = []
        if 7 in names_ok and 8 in names_ok:
            generalizations.append(
                "Compute+Energy stable: prefer hypotheses aligned with top lever and low entanglement"
            )
        if 9 in names_ok and 10 in names_ok:
            generalizations.append(
                "Form+Map complete: assembly points should pull map uncertainty down next pass"
            )
        if 11 in names_ok:
            generalizations.append(
                "Metric battery available: discount hypotheses that fail info-compatibility"
            )

        # Sensitivity generalization
        top_levers = [
            str(s.get("parameter"))
            for s in (sensitivities or [])[:3]
        ]
        if top_levers:
            generalizations.append(
                f"Top levers this pass: {', '.join(top_levers)} — "
                f"navigator γ-term should favor claims covering them"
            )

        # Pattern weight proposal
        total_src = sum(source_hits.values()) or 1
        pattern_weights = {
            k: round(v / total_src, 4) for k, v in source_hits.items()
        }

        return {
            "stage_hits": stage_hits,
            "source_hits": source_hits,
            "pattern_weights": pattern_weights,
            "generalizations": generalizations,
            "top_levers": top_levers,
        }

    def navigate(
        self,
        *,
        hypotheses: list[dict[str, Any]],
        step_trace: list[dict[str, Any]] | None = None,
        sensitivities: list[dict[str, Any]] | None = None,
        mega_map: dict[str, Any] | None = None,
        prior_learning: dict[str, Any] | None = None,
        outcome_score: float = 0.5,
        iteration: int = 1,
    ) -> dict[str, Any]:
        """
        Full navigator pass: deep one-step + group patterns + re-score + EMA learn.
        """
        step_trace = step_trace or []
        mega_map = mega_map or {}
        comparison = mega_map.get("comparison") or {}
        root_align = safe_float(comparison.get("root_alignment_score"), 0.5)

        learning = LearningState(
            iteration=iteration,
            lever_ema={
                k: safe_float(v)
                for k, v in (prior_learning or {}).get("lever_ema", {}).items()
            },
            pattern_weights={
                k: safe_float(v)
                for k, v in (prior_learning or {}).get("pattern_weights", {}).items()
            },
            step_scores=list((prior_learning or {}).get("step_scores") or []),
        )

        deep = self.deep_analyze_previous_step(step_trace)
        patterns = self.group_patterns(
            step_trace,
            hypotheses=hypotheses,
            sensitivities=sensitivities,
        )

        # Merge pattern weights into learning (EMA-style)
        lam = self.ema_lambda
        for k, w in (patterns.get("pattern_weights") or {}).items():
            prev = learning.pattern_weights.get(k, 0.2)
            learning.pattern_weights[k] = (1 - lam) * prev + lam * safe_float(w)

        # EMA on levers from sensitivities × outcome
        for s in sensitivities or []:
            lever = str(s.get("parameter") or "")
            if not lever:
                continue
            signal = abs(safe_float(s.get("derivative"))) * clamp01(outcome_score)
            prev = learning.lever_ema.get(lever, 0.25)
            learning.lever_ema[lever] = (1 - lam) * prev + lam * clamp01(signal)
        learning.step_scores.append(clamp01(outcome_score))
        learning.iteration = iteration

        scored = self.score_hypotheses(
            hypotheses,
            sensitivities=sensitivities,
            root_alignment=root_align,
            learning=learning,
            mega_points=list(mega_map.get("points") or []),
        )

        # Variants of previous stage: expand top-2 with ±sensitivity delta claims
        variants: list[dict[str, Any]] = []
        top_levers = patterns.get("top_levers") or []
        for base in scored[:2]:
            for lever in top_levers[:2]:
                variants.append(
                    {
                        "id": f"{base.get('id')}__var_{lever}",
                        "parent": base.get("id"),
                        "claim": (
                            f"Variant of «{str(base.get('claim'))[:60]}» "
                            f"emphasizing lever «{lever}»"
                        ),
                        "source": "hypothesis_library.variant",
                        "confidence": clamp01(
                            safe_float(base.get("confidence"), 0.5) * 0.95
                        ),
                        "coords": dict(base.get("coords") or {}),
                        "navigator_score": round(
                            safe_float(base.get("navigator_score")) * 0.92, 4
                        ),
                        "variant_of_stage": deep.get("focus_step"),
                    }
                )

        picked = scored[: min(4, len(scored))]
        return {
            "module": self.name,
            "iteration": iteration,
            "deep_previous_step": deep,
            "group_patterns": patterns,
            "scored_hypotheses": scored,
            "picked": picked,
            "variants_from_previous_stage": variants,
            "learning_state": learning.to_dict(),
            "formulas": {
                "selection": (
                    "S = α·conf + β·exp(-d/σ) + γ·sens_align + δ·pattern "
                    "+ ε·ema_boost − ζ·tension + 0.05·root_align"
                ),
                "ema": "ema[lever] ← (1-λ)·ema + λ·|∂F/∂lever|·outcome",
                "weights": {
                    "alpha": self.alpha,
                    "beta": self.beta,
                    "gamma": self.gamma,
                    "delta": self.delta,
                    "epsilon": self.epsilon,
                    "zeta": self.zeta,
                    "lambda": self.ema_lambda,
                },
            },
            "open_points": [
                "OPEN: durable Hypothesis Library across client requests",
                "OPEN: multi-iteration recursive scheme (only 1 navigator pass by default)",
            ],
            "summary": (
                f"Navigator iter={iteration}: scored={len(scored)}, "
                f"picked={len(picked)}, variants={len(variants)}; "
                f"deep_step={deep.get('focus_step')}; "
                f"patterns={len(patterns.get('generalizations') or [])}."
            ),
        }
