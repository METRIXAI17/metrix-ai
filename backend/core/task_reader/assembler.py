"""
Query assembler — turns multi-variant readings into a structured request pack.

Karim Metrix: order parsing, assembling and structuring files before
automatic delivery. Three sides stay split: product · linguistic · monetization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.core.task_reader.mode_selector import ModeDecision, select_mode
from backend.core.task_reader.reader import TaskRead, TaskReader, detect_lang


def _end_readings(read: TaskRead) -> list[dict[str, Any]]:
    return [e.to_dict() for e in read.selected_end_states]


def _product_side(read: TaskRead, text: str) -> dict[str, Any]:
    ids = {e.id for e in read.selected_end_states}
    artifacts = []
    if any(i.startswith("ops") for i in ids):
        artifacts.append("operational_deliverable")
    if "gen_territory" in ids:
        artifacts.append("generative_branch_pack")
    if "metric_push" in ids:
        artifacts.append("metric_delta_pack")
    if "literal_incomplete" in ids:
        artifacts.append("clarifying_slots")
    return {
        "side": "product",
        "intent": "ship a usable pack, not a chat",
        "candidate_artifacts": artifacts or ["consult_pack"],
        "files_to_structure": [
            "01_brief.md",
            "02_end_readings.json",
            "03_mode.json",
            "04_product_pack.md",
            "05_linguistic_spaces.json",
            "06_monetization.json",
        ],
    }


def _money_side(read: TaskRead, mode: ModeDecision) -> dict[str, Any]:
    sku = mode.sku
    return {
        "side": "monetization",
        "sku": sku,
        "earning_lever": mode.earning_lever,
        "surface": mode.surface,
        "rule": "demo/orientation free · pay on approved implementation or SKU",
        "pending_order": mode.surface == "terminal",
    }


@dataclass
class AssembledQuery:
    brief: str
    lang: str
    reading: dict[str, Any]
    end_readings: list[dict[str, Any]]
    product: dict[str, Any]
    linguistic: dict[str, Any]
    monetization: dict[str, Any]
    mode: dict[str, Any]
    files: list[dict[str, str]]
    unknowns: list[str]
    disagreement: float
    ready_for_delivery: bool
    summary: str
    extras: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": "Query Assembler",
            "brief": self.brief[:2000],
            "lang": self.lang,
            "reading": self.reading,
            "end_readings": self.end_readings,
            "three_sides": {
                "product": self.product,
                "linguistic": self.linguistic,
                "monetization": self.monetization,
            },
            "mode": self.mode,
            "files": self.files,
            "unknowns": self.unknowns,
            "disagreement": self.disagreement,
            "ready_for_delivery": self.ready_for_delivery,
            "summary": self.summary,
            **self.extras,
        }


class QueryAssembler:
    name = "Query Assembler"

    def __init__(self) -> None:
        self.reader = TaskReader()

    def assemble(
        self,
        query: str,
        *,
        lang: str | None = None,
        industry_hint: str = "",
        surface_hint: str = "",
    ) -> AssembledQuery:
        lang = lang or detect_lang(query)
        read = self.reader.read(query, lang=lang)
        mode = select_mode(read, industry_hint=industry_hint, surface_hint=surface_hint)
        unknowns: list[str] = []
        for e in read.selected_end_states:
            unknowns.extend(e.residual_unknowns)
        # unique, preserve order
        seen = set()
        unk = []
        for u in unknowns:
            if u and u not in seen:
                seen.add(u)
                unk.append(u)

        product = _product_side(read, query)
        linguistic = {
            "side": "linguistic",
            "report": read.linguistic,
            "role": "unfold spaces · name withheld phenomena · do not flatten into SKU",
        }
        money = _money_side(read, mode)
        files = [
            {"name": n, "role": "structured_before_delivery"}
            for n in product["files_to_structure"]
        ]
        ready = read.disagreement < 0.72 and "felicity" not in unk
        summary = (
            f"{self.name}: mode={mode.surface_mode} metrix={mode.metrix_mode} "
            f"sku={mode.sku} disagreement={read.disagreement:.2f} "
            f"ready={ready} sides=product|linguistic|monetization"
        )
        return AssembledQuery(
            brief=query,
            lang=lang,
            reading=read.to_dict(),
            end_readings=_end_readings(read),
            product=product,
            linguistic=linguistic,
            monetization=money,
            mode=mode.to_dict(),
            files=files,
            unknowns=unk,
            disagreement=read.disagreement,
            ready_for_delivery=ready,
            summary=summary,
        )


def assemble_query(
    query: str,
    *,
    lang: str | None = None,
    industry_hint: str = "",
    surface_hint: str = "",
) -> dict[str, Any]:
    return QueryAssembler().assemble(
        query, lang=lang, industry_hint=industry_hint, surface_hint=surface_hint
    ).to_dict()
