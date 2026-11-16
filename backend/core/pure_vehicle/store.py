"""JSON stores over DATA_DIR. No new database."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def root() -> Path:
    from backend.config import DATA_DIR

    path = Path(DATA_DIR) / "pure_vehicle"
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(name: str, default: Any) -> Any:
    path = root() / name
    if not path.exists():
        return default
    try:
        data = json.loads(path.read_text("utf-8"))
    except (OSError, json.JSONDecodeError):
        return default
    return data


def write_json(name: str, data: Any) -> Path:
    path = root() / name
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)
    return path
