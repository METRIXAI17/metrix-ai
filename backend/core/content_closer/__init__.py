"""CONTENT AI CLOSER — bottom layer of Metrix.

Pipeline: abstraction → function cards → prompt rewrite for the main engine
→ landing as event vision → quiet engine assistant → making chamber.

Public sections of the bot (three):
  1. landing  — видение события (landing studio instead of a studio button)
  2. engine   — движок; top module is the quiet assistant (ideas + growth)
  3. making   — мейкинг; new function `making_chamber`
"""

from backend.core.content_closer.abstraction import (
    compose_abstraction,
    format_abstraction_telegram,
)
from backend.core.content_closer.archetypes import pick_archetypes, score_vectors
from backend.core.content_closer.cards import cards_as_table, translate_cards
from backend.core.content_closer.comfort import comfort_turn
from backend.core.content_closer.landing import compose_event
from backend.core.content_closer.making import (
    MakingRefused,
    format_making_telegram,
    run_making_chamber,
)
from backend.core.content_closer.pipeline import (
    audit_hypotheses,
    closer_as_artifact,
    run_closer,
)
from backend.core.content_closer.prompt_rewrite import rewrite_prompt
from backend.core.content_closer.trends import screen_trends

__all__ = [
    "MakingRefused",
    "audit_hypotheses",
    "cards_as_table",
    "closer_as_artifact",
    "comfort_turn",
    "compose_abstraction",
    "compose_event",
    "format_abstraction_telegram",
    "format_making_telegram",
    "pick_archetypes",
    "rewrite_prompt",
    "run_closer",
    "run_making_chamber",
    "score_vectors",
    "screen_trends",
    "translate_cards",
]
