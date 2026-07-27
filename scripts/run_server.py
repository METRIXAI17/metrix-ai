#!/usr/bin/env python3
"""Start Metrix AI backend from project root."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.main import run

if __name__ == "__main__":
    run()
