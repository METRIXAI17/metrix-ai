"""Input sanitization and safe path helpers."""

from __future__ import annotations

import re
from typing import Any

# Strip control chars except tab/newline
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
# Obvious injection / path traversal markers in free text (soft)
_SUSPICIOUS = re.compile(
    r"(?i)(\.\./|\.\.\\x00|<script|javascript:|onerror\s*=|union\s+select|drop\s+table)",
)


def sanitize_text(text: str, *, max_len: int = 20_000) -> str:
    """Normalize client free-text fields."""
    if text is None:
        return ""
    s = str(text)
    s = _CTRL.sub("", s)
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    if len(s) > max_len:
        s = s[:max_len]
    return s.strip()


def is_suspicious(text: str) -> bool:
    return bool(_SUSPICIOUS.search(text or ""))


def assert_safe_path_segment(value: str, *, pattern: str = r"^[A-Za-z0-9_.:-]{1,80}$") -> str:
    v = (value or "").strip()
    if not re.match(pattern, v):
        raise ValueError("invalid_path_segment")
    if ".." in v or "/" in v or "\\" in v:
        raise ValueError("path_traversal")
    return v


def strip_secrets_from_dict(d: dict[str, Any]) -> dict[str, Any]:
    """Remove accidental secret keys from debug payloads."""
    banned = {
        "password",
        "secret",
        "token",
        "api_key",
        "apikey",
        "authorization",
        "service_role",
        "service_role_key",
        "supabase_service_role_key",
        "private_key",
    }
    out = {}
    for k, v in (d or {}).items():
        if str(k).lower() in banned:
            continue
        if isinstance(v, dict):
            out[k] = strip_secrets_from_dict(v)
        else:
            out[k] = v
    return out
