from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def _load_dotenv() -> None:
    p = ROOT / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, _, v = s.partition("=")
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


_load_dotenv()


def env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def env_float(key: str, default: float) -> float:
    try:
        return float(env(key, str(default)))
    except ValueError:
        return default


def env_int(key: str, default: int) -> int:
    try:
        return int(env(key, str(default)))
    except ValueError:
        return default


def is_live() -> bool:
    return env("ROBOT_MODE", "paper").lower() == "live"


RISK_PCT = env_float("ROBOT_RISK_PCT", 0.5)
MAX_DAILY_LOSS_PCT = env_float("ROBOT_MAX_DAILY_LOSS_PCT", 2.0)
PAPER_EQUITY = env_float("ROBOT_PAPER_EQUITY", 10_000.0)
POLL_SEC = env_int("ROBOT_POLL_SEC", 20)

GOLD_SYMBOL = env("GOLD_SYMBOL", "XAUUSD")
GOLD_YAHOO = env("GOLD_YAHOO", "GC=F")
GOLD_TF = env("GOLD_TF", "15m")
GOLD_BROKER = env("GOLD_BROKER", "paper")  # paper | mt5

CRYPTO_EXCHANGE = env("CRYPTO_EXCHANGE", "binance")
CRYPTO_WATCH = [
    s.strip().upper()
    for s in env("CRYPTO_WATCH", "SOLUSDT,WIFUSDT,DOGEUSDT,PEPEUSDT,BONKUSDT").split(",")
    if s.strip()
]
CRYPTO_TF = env("CRYPTO_TF", "15m")
CRYPTO_QUOTE = env_float("CRYPTO_QUOTE_USDT", 50.0)

US_SYMBOL = env("US_SYMBOL", "SPY")
US_TF = env("US_TF", "5m")
US_BROKER = env("US_BROKER", "paper")  # paper | alpaca
US_OR_MINUTES = env_int("US_OR_MINUTES", 30)

DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
