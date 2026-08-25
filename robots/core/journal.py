from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from robots.config import DATA_DIR


def _path(name: str) -> Path:
    return DATA_DIR / f"{name}.jsonl"


def log(name: str, event: dict[str, Any]) -> None:
    row = {"ts": datetime.now(timezone.utc).isoformat(), **event}
    p = _path(name)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps(row, ensure_ascii=False))
