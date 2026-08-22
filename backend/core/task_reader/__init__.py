"""Task reader + query assembly + automatic mode (Metrix update 2026-08)."""

from backend.core.task_reader.assembler import QueryAssembler, assemble_query
from backend.core.task_reader.linguistic_spaces import unfold_linguistic_spaces
from backend.core.task_reader.mode_selector import select_mode
from backend.core.task_reader.reader import TaskReader, read_task

__all__ = [
    "TaskReader",
    "QueryAssembler",
    "read_task",
    "assemble_query",
    "select_mode",
    "unfold_linguistic_spaces",
    "run_task_reader_assembly",
]


def run_task_reader_assembly(
    query: str,
    *,
    lang: str | None = None,
    industry_hint: str = "",
    surface_hint: str = "",
) -> dict:
    return assemble_query(
        query, lang=lang, industry_hint=industry_hint, surface_hint=surface_hint
    )
