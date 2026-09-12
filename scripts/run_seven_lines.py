#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run all 7 Metrix AI lines on the live brief. Measure wall time + RSS."""

from __future__ import annotations

import json
import sys
import time
import tracemalloc
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend.core.seven_lines import run_all

BRIEF = """
Саморазвитие. Личное отношение к проблемам в бизнесе. Время до первой сделки после идеи/MVP.
Насколько расслабляешься в тылу. Операционка. Хватает ли денег на бизнес/жизнь. Есть ли финансирование.
Кризис фрагментации: данные с чипов (FPGA/RTL/RISC-V) + назначение + функциональная роль + метрическая прошивка.
Metrix Store — 7 комнат. CraftShift — производная для постов в X и видео.
Вход без второго паспорта. Дружба как дверь. Терминальный ИИ сажает агента в денежный поток.
Скринер вкладки 5 режет эссе, фантомные цены и повтор схем.
"""


def main() -> int:
    tracemalloc.start()
    t0 = time.perf_counter()
    out = run_all(BRIEF.strip(), with_engine=True)
    elapsed = time.perf_counter() - t0
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    report = {
        "elapsed_sec": round(elapsed, 3),
        "peak_bytes": peak,
        "peak_mb": round(peak / (1024 * 1024), 3),
        "current_mb": round(current / (1024 * 1024), 3),
        "lines": [
            {
                "n": (ln.get("line") or i + 1),
                "title": ln.get("title"),
                "engine_ok": (ln.get("engine") or {}).get("ok"),
                "request_id": (ln.get("engine") or {}).get("request_id"),
                "idea": (ln.get("engine") or {}).get("idea_title"),
            }
            for i, ln in enumerate(out.get("lines") or [])
        ],
        "lattice": {
            "depth": (out.get("lattice") or {}).get("depth"),
            "remaining": (out.get("lattice") or {}).get("remaining"),
            "cbm": (out.get("lattice") or {}).get("cbm"),
        },
        "craftshift": (out.get("craftshift") or {}).get("title"),
        "ai_mgmt": (out.get("ai_mgmt") or {}).get("title"),
    }
    dest = ROOT / "docs" / "reports" / "SEVEN_LINES_RUN_2026-09-12.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("wrote", dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
