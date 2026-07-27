"""Supporting modules for the Paid Product Core."""

from backend.paid.supporting.critical_thinking import CriticalThinkingLayer
from backend.paid.supporting.hypothesis import HypothesisModuleSelector
from backend.paid.supporting.hypothesis_library import HypothesisLibrary
from backend.paid.supporting.reader import Reader

__all__ = [
    "HypothesisModuleSelector",
    "HypothesisLibrary",
    "Reader",
    "CriticalThinkingLayer",
]
