"""
IdeaStructure Synthesizer (Intelligent Folder & Idea Structure Management)

Пока система работает над продуктовым результатом, она:
- пересобирает структуру идей
- детектит субоптимальную организацию
- предлагает лучшую раскладку папок / кластеров

Это «живая» файловая/идеевая геометрия workspace.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.config import WORKSPACE_ROOT
from backend.core.metrics import entropy_of_weights


@dataclass
class IdeaNode:
    id: str
    title: str
    kind: str  # idea | fin_model | promo | spec | note
    tags: list[str] = field(default_factory=list)
    score: float = 0.5
    parent: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class StructureProposal:
    reason: str
    from_layout: dict[str, list[str]]
    to_layout: dict[str, list[str]]
    gain_estimate: float
    suboptimal_flags: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class StructureResult:
    workspace_id: str
    nodes: list[dict[str, Any]]
    current_layout: dict[str, list[str]]
    proposal: StructureProposal | None
    applied: bool
    entropy_before: float
    entropy_after: float
    summary: str
    path: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": "IdeaStructure Synthesizer",
            "workspace_id": self.workspace_id,
            "nodes": self.nodes,
            "current_layout": self.current_layout,
            "proposal": self.proposal.to_dict() if self.proposal else None,
            "applied": self.applied,
            "entropy_before": self.entropy_before,
            "entropy_after": self.entropy_after,
            "summary": self.summary,
            "path": self.path,
        }


class IdeaStructureSynthesizer:
    name = "IdeaStructure Synthesizer"

    DEFAULT_FOLDERS = (
        "01_orientation",
        "02_specs",
        "03_product_ideas",
        "04_fin_models",
        "05_promotion",
        "06_cloud_plans",
        "07_monetization",
        "08_deliverables",
        "09_paid_portal",
        "10_consult_metareality",
        "10_client_pack",
        "11_tech_write_specsforge",
        "12_package_result",
    )

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root or WORKSPACE_ROOT)
        self.root.mkdir(parents=True, exist_ok=True)

    def manage(
        self,
        workspace_id: str,
        ideas: list[dict[str, Any]],
        industry_id: str,
        auto_apply: bool = True,
    ) -> StructureResult:
        ws = self.root / _safe(workspace_id)
        ws.mkdir(parents=True, exist_ok=True)
        for folder in self.DEFAULT_FOLDERS:
            (ws / folder).mkdir(exist_ok=True)

        nodes = [self._to_node(i, idx) for idx, i in enumerate(ideas)]
        layout = self._layout_from_nodes(nodes)
        ent_before = self._layout_entropy(layout)

        flags = self._detect_suboptimal(layout, nodes)
        proposal = None
        ent_after = ent_before
        applied = False
        final_layout = layout

        if flags:
            new_layout = self._resynthesize(nodes, industry_id)
            ent_after = self._layout_entropy(new_layout)
            gain = max(0.0, ent_before - ent_after) + self._balance_gain(layout, new_layout)
            proposal = StructureProposal(
                reason="; ".join(flags),
                from_layout=layout,
                to_layout=new_layout,
                gain_estimate=round(gain, 4),
                suboptimal_flags=flags,
            )
            if auto_apply and gain >= 0.02:
                final_layout = new_layout
                applied = True
                self._write_layout(ws, final_layout, nodes)
            else:
                self._write_layout(ws, layout, nodes)
        else:
            self._write_layout(ws, layout, nodes)

        # always write manifest
        manifest = {
            "workspace_id": workspace_id,
            "industry_id": industry_id,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "layout": final_layout,
            "applied_resynth": applied,
        }
        (ws / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        summary = (
            f"{self.name}: workspace={workspace_id}, nodes={len(nodes)}, "
            f"entropy {ent_before:.2f}→{ent_after:.2f}, "
            f"resynth={'yes' if applied else 'no'}."
        )
        if flags:
            summary += f" Flags: {', '.join(flags[:3])}."

        return StructureResult(
            workspace_id=workspace_id,
            nodes=[n.to_dict() for n in nodes],
            current_layout=final_layout,
            proposal=proposal,
            applied=applied,
            entropy_before=round(ent_before, 4),
            entropy_after=round(ent_after, 4),
            summary=summary,
            path=str(ws),
        )

    def _to_node(self, raw: dict[str, Any], idx: int) -> IdeaNode:
        return IdeaNode(
            id=str(raw.get("id") or f"idea_{idx}"),
            title=str(raw.get("title") or raw.get("name") or f"Idea {idx}"),
            kind=str(raw.get("kind") or "idea"),
            tags=list(raw.get("tags") or []),
            score=float(raw.get("score") or 0.5),
            parent=raw.get("parent"),
        )

    def _layout_from_nodes(self, nodes: list[IdeaNode]) -> dict[str, list[str]]:
        layout: dict[str, list[str]] = {f: [] for f in self.DEFAULT_FOLDERS}
        for n in nodes:
            folder = self._folder_for_kind(n.kind)
            layout[folder].append(n.id)
        return layout

    def _folder_for_kind(self, kind: str) -> str:
        return {
            "orientation": "01_orientation",
            "spec": "02_specs",
            "idea": "03_product_ideas",
            "product": "03_product_ideas",
            "fin_model": "04_fin_models",
            "model": "04_fin_models",
            "promo": "05_promotion",
            "promotion": "05_promotion",
            "cloud": "06_cloud_plans",
            "monetization": "07_monetization",
            "deliverable": "08_deliverables",
            "consult": "10_consult_metareality",
            "consultation": "10_consult_metareality",
            "tech_write": "11_tech_write_specsforge",
            "techwrite": "11_tech_write_specsforge",
            "package_result": "12_package_result",
            "note": "03_product_ideas",
        }.get(kind, "03_product_ideas")

    def _detect_suboptimal(
        self, layout: dict[str, list[str]], nodes: list[IdeaNode]
    ) -> list[str]:
        flags: list[str] = []
        sizes = [len(v) for v in layout.values()]
        if not nodes:
            return ["empty_workspace"]
        if max(sizes) >= max(4, len(nodes) * 0.7):
            flags.append("one_folder_overloaded")
        empty = sum(1 for s in sizes if s == 0)
        if empty >= 5 and len(nodes) >= 3:
            flags.append("too_many_empty_folders_with_active_ideas")
        # duplicate-ish titles
        titles = [n.title.lower().strip() for n in nodes]
        if len(titles) != len(set(titles)):
            flags.append("duplicate_idea_titles")
        # low score cluster dumped in product
        product_ids = set(layout.get("03_product_ideas", []))
        weak = [n for n in nodes if n.id in product_ids and n.score < 0.35]
        if len(weak) >= 2:
            flags.append("weak_ideas_polluting_product_folder")
        ent = self._layout_entropy(layout)
        if ent < 0.25 and len(nodes) >= 4:
            flags.append("structure_too_concentrated")
        if ent > 0.92 and len(nodes) >= 6:
            flags.append("structure_too_scattered")
        return flags

    def _resynthesize(
        self, nodes: list[IdeaNode], industry_id: str
    ) -> dict[str, list[str]]:
        layout: dict[str, list[str]] = {f: [] for f in self.DEFAULT_FOLDERS}
        for n in nodes:
            folder = self._folder_for_kind(n.kind)
            # weak product ideas → deliverables quarantine or specs
            if n.kind in ("idea", "product") and n.score < 0.35:
                folder = "02_specs" if "spec" in " ".join(n.tags) else "08_deliverables"
            if n.kind == "promo" or "promo" in n.tags:
                folder = "05_promotion"
            if industry_id == "telecom" and "signal" in " ".join(n.tags).lower():
                folder = "06_cloud_plans"
            layout[folder].append(n.id)
        # rebalance overload
        for folder, ids in list(layout.items()):
            if len(ids) > 5:
                overflow = ids[5:]
                layout[folder] = ids[:5]
                target = "08_deliverables"
                layout[target].extend(overflow)
        return layout

    def _layout_entropy(self, layout: dict[str, list[str]]) -> float:
        weights = {k: float(len(v)) for k, v in layout.items()}
        return entropy_of_weights(weights)

    def _balance_gain(
        self, old: dict[str, list[str]], new: dict[str, list[str]]
    ) -> float:
        def spread(l: dict[str, list[str]]) -> float:
            sizes = [len(v) for v in l.values() if v]
            if not sizes:
                return 0.0
            avg = sum(sizes) / len(sizes)
            var = sum((s - avg) ** 2 for s in sizes) / len(sizes)
            return 1.0 / (1.0 + var)

        return max(0.0, spread(new) - spread(old))

    def _write_layout(
        self,
        ws: Path,
        layout: dict[str, list[str]],
        nodes: list[IdeaNode],
    ) -> None:
        by_id = {n.id: n for n in nodes}
        for folder, ids in layout.items():
            folder_path = ws / folder
            folder_path.mkdir(exist_ok=True)
            # clear old idea jsons lightly (keep manifest elsewhere)
            for old in folder_path.glob("*.idea.json"):
                old.unlink(missing_ok=True)
            for iid in ids:
                n = by_id.get(iid)
                if not n:
                    continue
                (folder_path / f"{_safe(iid)}.idea.json").write_text(
                    json.dumps(n.to_dict(), ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )


def _safe(s: str) -> str:
    s = re.sub(r"[^\w.\-]+", "_", s.strip())[:80]
    return s or "ws"
