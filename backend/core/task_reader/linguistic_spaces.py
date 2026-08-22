"""
Linguistic space unfolding — the unnamed third side of Metrix.

Not NLU. Each theory opens a *space*; the brief is a trajectory through
those spaces. Intersections surface properties that no single theory names.
Absences, hedges and displaced agency are treated as first-class signals
(possible deliberate concealment, not noise).
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any


THEORIES: list[dict[str, str]] = [
    {
        "id": "saussure",
        "name": "Saussure sign",
        "lens": "signifier / signified split — what is said vs what is meant",
    },
    {
        "id": "peirce",
        "name": "Peirce triadic",
        "lens": "icon / index / symbol — resemblance, causal trace, convention",
    },
    {
        "id": "chomsky_ds",
        "name": "Deep / surface structure",
        "lens": "surface request vs deep propositional skeleton",
    },
    {
        "id": "frame",
        "name": "Frame semantics",
        "lens": "which commercial/ops frame is evoked and which slots are empty",
    },
    {
        "id": "metaphor",
        "name": "Conceptual metaphor",
        "lens": "source→target mappings that smuggle constraints",
    },
    {
        "id": "speech_act",
        "name": "Speech acts",
        "lens": "illocution: request, claim, conceal, commission, vent",
    },
    {
        "id": "possible_worlds",
        "name": "Possible worlds",
        "lens": "worlds the brief commits to vs worlds it refuses to name",
    },
    {
        "id": "discourse",
        "name": "Discourse concealment",
        "lens": "agent deletion, hedges, euphemism, topic shift",
    },
    {
        "id": "topology",
        "name": "Meaning topology",
        "lens": "folds, holes, boundary, connectivity of the brief as a space",
    },
    {
        "id": "dialogic",
        "name": "Dialogic (Bakhtin)",
        "lens": "whose other voice is being answered or silenced",
    },
]


_HEDGES = (
    r"\bпросто\b",
    r"\bлишь\b",
    r"\bкак бы\b",
    r"\bтипа\b",
    r"\bвроде\b",
    r"\bsomehow\b",
    r"\bjust\b",
    r"\bmerely\b",
    r"\bkind of\b",
    r"\bsort of\b",
    r"\bbasically\b",
    r"\bonly\b",
)
_PASSIVE_RU = re.compile(
    r"\b(делается|требуется|нужно|можно|должно быть|планируется|ожидается)\b",
    re.I,
)
_PASSIVE_EN = re.compile(
    r"\b(is needed|is required|should be|must be|it is planned|it is expected)\b",
    re.I,
)
_EUPHEMISM = (
    r"оптимизац",
    r"реструктур",
    r"challeng",
    r"opportun",
    r"синерг",
    r"трансформац",
    r"leverage",
    r"streamlin",
    r"rightsiz",
)
_AGENT_MARKERS = (
    r"\bя\b",
    r"\bмы\b",
    r"\bмне\b",
    r"\bнаш",
    r"\bi\b",
    r"\bwe\b",
    r"\bmy\b",
    r"\bour\b",
    r"клиент",
    r"заказчик",
    r"партн",
)
_MONEY = (
    r"руб",
    r"usd",
    r"\$",
    r"марж",
    r"прибыл",
    r"доход",
    r"выручк",
    r"revenue",
    r"margin",
    r"profit",
    r"ликвид",
    r"ордер",
    r"order",
)
_CREATIVE = (
    r"креатив",
    r"ролик",
    r"контент",
    r"идея",
    r"бренд",
    r"стори",
    r"reel",
    r"prompt",
    r"промпт",
)
_TRADE = (
    r"трейд",
    r"trad",
    r"позиц",
    r"стоп",
    r"фьюч",
    r"spot",
    r"pnl",
    r"просадк",
    r"drawdown",
)


def _hits(patterns: tuple[str, ...] | list[str], text: str) -> list[str]:
    found = []
    for p in patterns:
        if re.search(p, text, re.I):
            found.append(p.strip(r"\b"))
    return found


@dataclass
class SpaceUnfold:
    theory_id: str
    theory_name: str
    properties: list[str]
    holes: list[str]
    new_phenomena: list[str]
    concealment_score: float
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LinguisticReport:
    spaces: list[SpaceUnfold]
    intersection_properties: list[str]
    concealment: dict[str, Any]
    speech_act: str
    deep_structure: str
    surface_structure: str
    unnamed_phenomena: list[str]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": "Linguistic Space Unfolding",
            "spaces": [s.to_dict() for s in self.spaces],
            "intersection_properties": self.intersection_properties,
            "concealment": self.concealment,
            "speech_act": self.speech_act,
            "deep_structure": self.deep_structure,
            "surface_structure": self.surface_structure,
            "unnamed_phenomena": self.unnamed_phenomena,
            "summary": self.summary,
        }


def _concealment(text: str) -> dict[str, Any]:
    hedges = _hits(_HEDGES, text)
    euph = _hits(_EUPHEMISM, text)
    passive = bool(_PASSIVE_RU.search(text) or _PASSIVE_EN.search(text))
    agents = _hits(_AGENT_MARKERS, text)
    agentless = passive and not agents
    length = max(1, len(text.split()))
    questions = text.count("?")
    money = _hits(_MONEY, text)
    # concealment rises when agency is deleted, hedges pile, money is present
    # but not quantified, or the brief is long yet slot-empty
    score = 0.0
    flags: list[str] = []
    if hedges:
        score += min(0.25, 0.07 * len(hedges))
        flags.append("hedges")
    if euph:
        score += min(0.2, 0.08 * len(euph))
        flags.append("euphemism")
    if agentless:
        score += 0.22
        flags.append("agent_deletion")
    if money and not re.search(r"\d", text):
        score += 0.18
        flags.append("unquantified_money")
    if length > 40 and questions == 0 and not money:
        score += 0.1
        flags.append("assertive_without_slots")
    if re.search(r"не важно|не суть|later|потом разбер", text, re.I):
        score += 0.15
        flags.append("deferred_core")
    return {
        "score": round(min(1.0, score), 4),
        "flags": flags,
        "hedges": hedges[:8],
        "euphemisms": euph[:6],
        "agentless_passive": agentless,
        "agents_named": agents[:8],
        "possible_deliberate": score >= 0.45,
    }


def _speech_act(text: str) -> str:
    t = text.lower()
    if re.search(r"\b(купи|buy|оплат|invoice|заказ)\b", t):
        return "commission"
    if re.search(r"\b(сделай|построй|создай|build|design|generate)\b", t):
        return "directive_build"
    if re.search(r"\b(проанализ|разбер|analyze|audit|почему)\b", t):
        return "directive_analyze"
    if re.search(r"\b(хочу|нужно|надо|want|need)\b", t):
        return "request"
    if re.search(r"\?", t):
        return "question"
    if re.search(r"\b(мы уже|i already|готово|shipped)\b", t):
        return "claim"
    return "open_brief"


def unfold_linguistic_spaces(text: str, lang: str = "ru") -> LinguisticReport:
    t = (text or "").strip()
    low = t.lower()
    conc = _concealment(low)
    act = _speech_act(low)
    surface = t[:280] if t else ""
    money = bool(_hits(_MONEY, low))
    creative = bool(_hits(_CREATIVE, low))
    trade = bool(_hits(_TRADE, low))
    has_who = bool(_hits(_AGENT_MARKERS, low))

    deep_bits = []
    if act.startswith("directive"):
        deep_bits.append("AGENT wants SYSTEM to PRODUCE ARTIFACT")
    elif act == "request":
        deep_bits.append("AGENT lacks CAPABILITY and seeks PATH")
    elif act == "question":
        deep_bits.append("AGENT seeks DISAMBIGUATION not product")
    else:
        deep_bits.append("AGENT dumps FIELD; SYSTEM must orient")
    if money:
        deep_bits.append("VALUE/LIQUIDITY is a silent argument")
    if conc["possible_deliberate"]:
        deep_bits.append("SOME CONSTRAINT is withheld")
    deep = "; ".join(deep_bits)

    spaces: list[SpaceUnfold] = []

    spaces.append(
        SpaceUnfold(
            "saussure",
            "Saussure sign",
            properties=[
                f"signifier_length={len(t)}",
                f"signified_act={act}",
            ],
            holes=[] if has_who else ["subject_of_enunciation missing"],
            new_phenomena=["split_between_named_task_and_unnamed_stake"],
            concealment_score=0.2 if not has_who else 0.05,
            notes=["Do not collapse signifier into a SKU too early."],
        )
    )
    spaces.append(
        SpaceUnfold(
            "peirce",
            "Peirce triadic",
            properties=[
                "icon: marketplace/card UI as resemblance of CraftShift",
                "index: numbers, PnL, orders as traces",
                "symbol: Metrix modes, tracks, TZ",
            ],
            holes=[] if (money or trade) else ["indexical_trace (numbers) absent"],
            new_phenomena=["card_as_icon_of_liquidity"],
            concealment_score=0.15 if not money else 0.0,
        )
    )
    spaces.append(
        SpaceUnfold(
            "chomsky_ds",
            "Deep / surface structure",
            properties=[f"surface={act}", f"deep={deep}"],
            holes=["transformational_gaps"] if conc["score"] > 0.3 else [],
            new_phenomena=["multiple_end_readings_required"],
            concealment_score=conc["score"] * 0.5,
        )
    )
    frame_slots = ["agent", "goal", "constraint", "metric", "counterparty"]
    empty = []
    if not has_who:
        empty.append("agent")
    if not re.search(r"\b(чтобы|чтобы |so that|goal|цель|хочу)\b", low):
        empty.append("goal")
    if not re.search(r"\d", t):
        empty.append("metric")
    spaces.append(
        SpaceUnfold(
            "frame",
            "Frame semantics",
            properties=[f"evoked={'trade' if trade else 'creative' if creative else 'ops'}"],
            holes=[f"empty_slot:{s}" for s in empty],
            new_phenomena=["frame_with_deliberate_empty_slots"] if len(empty) >= 2 else [],
            concealment_score=min(0.6, 0.15 * len(empty)),
        )
    )
    meta_src = "journey" if re.search(r"путь|path|дорога", low) else "machine" if re.search(
        r"систем|engine|движ|терминал", low
    ) else "market"
    spaces.append(
        SpaceUnfold(
            "metaphor",
            "Conceptual metaphor",
            properties=[f"source_domain={meta_src}", "target=work_of_request"],
            holes=[],
            new_phenomena=[f"metaphor_imports_{meta_src}_constraints"],
            concealment_score=0.1,
        )
    )
    spaces.append(
        SpaceUnfold(
            "speech_act",
            "Speech acts",
            properties=[f"illocution={act}", "perlocution=mode_switch"],
            holes=["felicity_conditions"] if empty else [],
            new_phenomena=["illocution_mismatch_if_sold_as_chat"],
            concealment_score=0.12 if act == "open_brief" else 0.0,
        )
    )
    worlds = ["world_where_brief_is_complete", "world_where_constraint_is_hidden"]
    if conc["possible_deliberate"]:
        worlds.append("world_of_strategic_omission")
    spaces.append(
        SpaceUnfold(
            "possible_worlds",
            "Possible worlds",
            properties=worlds,
            holes=["accessibility_between_stated_and_unstated"],
            new_phenomena=["counterfactual_product_if_omission_is_true"],
            concealment_score=conc["score"] * 0.4,
        )
    )
    spaces.append(
        SpaceUnfold(
            "discourse",
            "Discourse concealment",
            properties=conc["flags"] or ["no_strong_concealment"],
            holes=conc["hedges"][:4],
            new_phenomena=["withheld_phenomenon"] if conc["possible_deliberate"] else [],
            concealment_score=conc["score"],
            notes=["Treat omission as data, not as user error."],
        )
    )
    holes_top = ["boundary_of_scope"] if len(t.split()) < 25 else []
    spaces.append(
        SpaceUnfold(
            "topology",
            "Meaning topology",
            properties=[
                "connected_if_goal+agent+metric",
                f"genus_holes={len(empty)}",
            ],
            holes=holes_top + [f"hole:{s}" for s in empty],
            new_phenomena=["unfolding_creates_new_boundary_properties"],
            concealment_score=0.08 * len(empty),
        )
    )
    spaces.append(
        SpaceUnfold(
            "dialogic",
            "Dialogic (Bakhtin)",
            properties=[
                "answers_market_voice" if money else "answers_self_voice",
                "silenced_counterparty" if not has_who else "named_I",
            ],
            holes=[] if has_who else ["other_not_addressed"],
            new_phenomena=["polyphony_of_product_ling_money"],
            concealment_score=0.1 if not has_who else 0.0,
        )
    )

    # Intersections: properties that appear as *relations* between spaces
    intersection: list[str] = []
    unnamed: list[str] = []
    if conc["possible_deliberate"] and money:
        intersection.append("liquidity_is_named_while_agent_or_constraint_is_not")
        unnamed.append("concealed_order_intent")
    if empty and act.startswith("directive"):
        intersection.append("command_without_felicity")
        unnamed.append("premature_execution_pressure")
    if creative and money:
        intersection.append("promo_as_liquidity_surface")
    if trade:
        intersection.append("journal_as_decision_trace")
        unnamed.append("nonformal_path_to_pending_order")
    if conc["score"] >= 0.3:
        unnamed.append("property_visible_only_after_multi_theory_unfold")
    intersection.append("three_sides_must_stay_split: product · linguistic · monetization")

    summary = (
        f"act={act}, concealment={conc['score']:.2f}, "
        f"empty_slots={empty}, unnamed={len(unnamed)}, "
        f"deliberate={conc['possible_deliberate']}"
    )
    return LinguisticReport(
        spaces=spaces,
        intersection_properties=intersection,
        concealment=conc,
        speech_act=act,
        deep_structure=deep,
        surface_structure=surface,
        unnamed_phenomena=unnamed,
        summary=summary,
    )
