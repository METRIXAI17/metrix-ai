"""
Automatic mode selection from assembled readings.

The assembly chooses the mode — the user does not pick a dropdown.
Maps onto existing DecisionMakingCore modes plus Mini App surfaces.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from backend.core.task_reader.reader import TaskRead


SURFACE_MODES = (
    "consult_qa",          # работа по запросу
    "generative_territory",
    "linguistic_unfold",
    "metric_push",
    "promo_lite",
    "terminal_liquidity",
    "creative_assist",
    "solution_logger",
    "digital_mockup",
    "scoring",
)

# Mini App surfaces the user sees
SURFACE_TO_VIEW = {
    "consult_qa": "request",
    "generative_territory": "request",
    "linguistic_unfold": "request",
    "metric_push": "flagships",
    "promo_lite": "promo",
    "terminal_liquidity": "terminal",
    "creative_assist": "fn-creative",
    "solution_logger": "fn-logger",
    "digital_mockup": "fn-mockup",
    "scoring": "request",
}

METRIX_MODE = {
    "consult_qa": "scoring",
    "generative_territory": "generative_development",
    "linguistic_unfold": "dual_ricochet",
    "metric_push": "recursive_refinement",
    "promo_lite": "scoring",
    "terminal_liquidity": "paid_handoff",
    "creative_assist": "generative_development",
    "solution_logger": "recursive_refinement",
    "digital_mockup": "generative_development",
    "scoring": "scoring",
}

SKU = {
    "consult_qa": "request_deep",
    "generative_territory": "request_deep",
    "linguistic_unfold": "request_deep",
    "metric_push": "flagship_metric",
    "promo_lite": "promo_pack",
    "terminal_liquidity": "terminal_mine",
    "creative_assist": "fn_creative",
    "solution_logger": "fn_logger",
    "digital_mockup": "fn_mockup",
    "scoring": "request_orient",
}

LEVER = {
    "consult_qa": "orient_run",
    "generative_territory": "orient_run",
    "linguistic_unfold": "orient_run",
    "metric_push": "full_package",
    "promo_lite": "promo_pack",
    "terminal_liquidity": "auto_orders",
    "creative_assist": "orient_run",
    "solution_logger": "orient_run",
    "digital_mockup": "orient_run",
    "scoring": "consult_tech",
}


@dataclass
class ModeDecision:
    surface_mode: str
    metrix_mode: str
    view: str
    sku: str
    earning_lever: str
    surface: str
    confidence: float
    reasons: list[str]
    alternatives: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _id_set(read: "TaskRead") -> set[str]:
    s: set[str] = set()
    for e in read.selected_end_states:
        s.add(e.id)
    for v in read.variants:
        for e in v.end_states:
            if e.confidence >= 0.62:
                s.add(e.id)
    return s


def select_mode(
    read: "TaskRead",
    *,
    industry_hint: str = "",
    surface_hint: str = "",
) -> ModeDecision:
    if surface_hint in SURFACE_MODES:
        sm = surface_hint
        reasons = [f"surface_hint={surface_hint}"]
        conf = 0.9
        alts: list[str] = []
        return ModeDecision(
            surface_mode=sm,
            metrix_mode=METRIX_MODE[sm],
            view=SURFACE_TO_VIEW[sm],
            sku=SKU[sm],
            earning_lever=LEVER[sm],
            surface="terminal" if sm == "terminal_liquidity" else "request",
            confidence=conf,
            reasons=reasons,
            alternatives=alts,
        )

    text = (read.query or "").lower()
    ids = _id_set(read)
    votes: dict[str, float] = {m: 0.0 for m in SURFACE_MODES}
    reasons: list[str] = []

    def bump(mode: str, w: float, why: str) -> None:
        votes[mode] = votes.get(mode, 0.0) + w
        reasons.append(f"{mode}+{w:.2f}:{why}")

    # lexical (weak — never sole decider)
    if any(
        k in text
        for k in (
            "промо",
            "ролик",
            "промпт",
            "карточки описан",
            "идеи для роли",
            "reel",
            "promo",
            "консалтинг-промпт",
        )
    ):
        bump("promo_lite", 2.4, "lex_promo")
    if any(k in text for k in ("трейд", "trade", "pnl", "просад", "журнал")):
        bump("solution_logger", 2.2, "lex_trade")
    if any(k in text for k in ("макет", "подоби", "двойник", "mockup", "цифров")):
        bump("digital_mockup", 1.4, "lex_mockup")
    if any(k in text for k in ("креатив", "идея для", "ассистент", "creative")):
        bump("creative_assist", 1.1, "lex_creative")
    if any(k in text for k in ("ордер", "ликвид", "терминал", "mining", "order")):
        bump("terminal_liquidity", 1.6, "lex_terminal")

    # readings (strong)
    if "gen_territory" in ids:
        bump("generative_territory", 1.8, "end:gen_territory")
    if "gen_quality_first" in ids or "metric_push" in ids:
        bump("metric_push", 1.7, "end:metric")
    if "ling_unfold" in ids or "ling_hidden" in ids:
        bump("linguistic_unfold", 1.5, "end:ling")
    if "ops_path" in ids:
        bump("terminal_liquidity", 1.3, "end:ops_path")
    if "ops_deliverable" in ids:
        if votes.get("promo_lite", 0) > 0:
            bump("promo_lite", 0.7, "ops_as_promo_pack")
        elif votes.get("solution_logger", 0) > 0:
            bump("solution_logger", 0.5, "ops_as_logger")
        else:
            bump("consult_qa", 1.0, "end:ops_deliverable")
    if "literal_incomplete" in ids:
        bump("consult_qa", 0.8, "end:incomplete")
    if "adv_omission" in ids:
        bump("linguistic_unfold", 0.9, "end:omission")

    # geometry
    if read.disagreement >= 0.55:
        bump("generative_territory", 0.8, "high_disagreement")
        bump("metric_push", 0.6, "high_disagreement")
    conc = float((read.linguistic.get("concealment") or {}).get("score") or 0)
    if conc >= 0.45:
        bump("linguistic_unfold", 1.2, "concealment")

    if industry_hint == "asset-decisions":
        bump("solution_logger", 0.5, "industry")
        bump("terminal_liquidity", 0.4, "industry")
    if industry_hint == "content-monetize":
        bump("promo_lite", 0.5, "industry")
        bump("creative_assist", 0.4, "industry")

    # default mass of consult
    bump("consult_qa", 0.7, "prior")

    # Explicit mass / function surfaces beat open generative territory.
    for mass in ("promo_lite", "solution_logger", "digital_mockup", "creative_assist", "terminal_liquidity"):
        if votes[mass] >= 1.8:
            votes["generative_territory"] = min(
                votes["generative_territory"], votes[mass] - 0.35
            )
            votes["linguistic_unfold"] = min(
                votes["linguistic_unfold"], votes[mass] - 0.25
            )
            votes["metric_push"] = min(votes["metric_push"], votes[mass] - 0.15)

    ranked = sorted(votes.items(), key=lambda x: -x[1])
    sm = ranked[0][0]
    top_s = ranked[0][1]
    second = ranked[1][1] if len(ranked) > 1 else 0.0
    conf = 0.5 + min(0.45, (top_s - second) / 4.0)
    alts = [m for m, s in ranked[1:4] if s > 0.8]

    surface = "terminal" if sm == "terminal_liquidity" else (
        "promo" if sm == "promo_lite" else "request"
    )
    return ModeDecision(
        surface_mode=sm,
        metrix_mode=METRIX_MODE[sm],
        view=SURFACE_TO_VIEW[sm],
        sku=SKU[sm],
        earning_lever=LEVER[sm],
        surface=surface,
        confidence=round(conf, 4),
        reasons=reasons[:16],
        alternatives=alts,
    )
