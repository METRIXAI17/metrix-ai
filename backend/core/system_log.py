"""
System log analyst
==================

Читает общий лог запросов (backend/data/requests/*.json),
вытаскивает **features** системы (частоты mode, industries, IROI bands,
firmware signatures) и отдаёт их в Operational Analytics / Decision Core.

Это «память контура» без тяжёлой БД — только файловый журнал.
"""

from __future__ import annotations

import json
import logging
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from backend.config import DATA_DIR

logger = logging.getLogger("metrix.system_log")


@dataclass
class SystemLogFeatures:
    n_requests: int = 0
    industries: dict[str, int] = field(default_factory=dict)
    modes: dict[str, int] = field(default_factory=dict)
    mean_iroi: float = 0.0
    mean_health: float = 0.0
    paid_true_rate: float = 0.0
    top_idea_tokens: list[str] = field(default_factory=list)
    recurring_patterns: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SystemLogAnalyst:
    name = "System Log Analyst"

    def __init__(self, store: Path | None = None) -> None:
        self.store = Path(store or (DATA_DIR / "requests"))

    def analyze(self, limit: int = 80) -> SystemLogFeatures:
        files = sorted(
            self.store.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[:limit]
        if not files:
            return SystemLogFeatures(
                notes=["empty log — cold start, no prior features"]
            )

        ind_c: Counter[str] = Counter()
        mode_c: Counter[str] = Counter()
        irois: list[float] = []
        healths: list[float] = []
        paid_flags: list[bool] = []
        idea_tokens: Counter[str] = Counter()

        for fp in files:
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                logger.debug("skip log %s: %s", fp.name, exc)
                continue
            resp = data.get("response") or data
            ind = resp.get("industry") or ""
            if ind:
                ind_c[ind] += 1
            mode = resp.get("operating_mode") or ""
            if mode:
                mode_c[mode] += 1

            profit = (resp.get("breakdown") or {}).get("profitability") or {}
            iroi = profit.get("info_roi")
            if iroi is not None:
                irois.append(float(iroi))
            paid_flags.append(bool(profit.get("recommended")))

            um = (resp.get("metrics") or {}).get("unified") or {}
            h = um.get("health_score")
            if h is None and isinstance(um.get("core"), dict):
                h = um["core"].get("health_score")
            if h is not None:
                healths.append(float(h))

            title = ((resp.get("demo_idea") or {}).get("title") or "").lower()
            for tok in title.replace(":", " ").replace("—", " ").split():
                if len(tok) >= 4:
                    idea_tokens[tok] += 1

        n = max(len(files), 1)
        patterns: list[str] = []
        if ind_c:
            top_ind, top_n = ind_c.most_common(1)[0]
            if top_n / n >= 0.35:
                patterns.append(f"industry_gravity:{top_ind}")
        if mode_c:
            top_mode, _ = mode_c.most_common(1)[0]
            patterns.append(f"mode_gravity:{top_mode}")
        if irois and sum(irois) / len(irois) >= 2.5:
            patterns.append("high_iroi_cluster")
        if paid_flags and sum(1 for p in paid_flags if p) / len(paid_flags) >= 0.5:
            patterns.append("paid_majority")
        if idea_tokens:
            top_tok = idea_tokens.most_common(1)[0][0]
            patterns.append(f"idea_token_gravity:{top_tok}")

        feat = SystemLogFeatures(
            n_requests=len(files),
            industries=dict(ind_c),
            modes=dict(mode_c),
            mean_iroi=round(sum(irois) / len(irois), 4) if irois else 0.0,
            mean_health=round(sum(healths) / len(healths), 4) if healths else 0.0,
            paid_true_rate=round(
                sum(1 for p in paid_flags if p) / len(paid_flags), 4
            )
            if paid_flags
            else 0.0,
            top_idea_tokens=[t for t, _ in idea_tokens.most_common(8)],
            recurring_patterns=patterns,
            notes=[
                f"Analyzed {len(files)} request log files",
                f"mean_iroi={sum(irois)/len(irois):.2f}" if irois else "no iroi yet",
            ],
        )
        return feat
