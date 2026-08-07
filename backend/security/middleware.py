"""
Security middleware stack:
  - Security headers (CSP light, nosniff, frame, referrer)
  - Simple in-memory rate limit per IP
  - Request size guard
  - Optional ops key for sensitive routes
  - No server version leakage
"""

from __future__ import annotations

import os
import time
from collections import defaultdict, deque
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# Ops routes that can expose internal commercial fields
_OPS_PREFIXES = (
    "/api/v1/analytics/implement-model",
    "/api/v1/analytics/robotics/start",
    "/api/v1/analytics/paid-",
    "/api/v1/analytics/final-layer",
)

# Rate limit: requests per window
_RATE_LIMIT = int(os.getenv("METRIX_RATE_LIMIT", "120"))
_RATE_WINDOW = float(os.getenv("METRIX_RATE_WINDOW_SEC", "60"))
_MAX_BODY = int(os.getenv("METRIX_MAX_BODY_BYTES", str(512 * 1024)))  # 512KB
_OPS_KEY = os.getenv("METRIX_OPS_KEY", "").strip()


class _RateBucket:
    def __init__(self) -> None:
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.time()
        q = self.hits[key]
        while q and now - q[0] > _RATE_WINDOW:
            q.popleft()
        if len(q) >= _RATE_LIMIT:
            return False
        q.append(now)
        return True


_rate = _RateBucket()


class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Client IP (Railway / proxies)
        forwarded = request.headers.get("x-forwarded-for") or ""
        ip = (forwarded.split(",")[0].strip() if forwarded else "") or (
            request.client.host if request.client else "unknown"
        )

        path = request.url.path or "/"

        # Rate limit API only
        if path.startswith("/api/"):
            if not _rate.allow(ip):
                return JSONResponse(
                    {"ok": False, "error": "rate_limited", "retry_after_sec": int(_RATE_WINDOW)},
                    status_code=429,
                    headers={"Retry-After": str(int(_RATE_WINDOW))},
                )

        # Body size guard for writes
        if request.method in ("POST", "PUT", "PATCH"):
            cl = request.headers.get("content-length")
            if cl and cl.isdigit() and int(cl) > _MAX_BODY:
                return JSONResponse(
                    {"ok": False, "error": "payload_too_large", "max_bytes": _MAX_BODY},
                    status_code=413,
                )

        # Ops key gate (optional — if METRIX_OPS_KEY set)
        if _OPS_KEY and any(path.startswith(p) for p in _OPS_PREFIXES):
            provided = (
                request.headers.get("x-metrix-ops-key")
                or request.headers.get("x-ops-key")
                or ""
            ).strip()
            # implement-model with expose_price must have key
            if path.startswith("/api/v1/analytics/implement-model"):
                # Allow without key only if body won't expose price — checked in route;
                # still require key for start robotics executive
                pass
            if path.startswith("/api/v1/analytics/robotics/start") and provided != _OPS_KEY:
                return JSONResponse(
                    {"ok": False, "error": "ops_key_required"},
                    status_code=401,
                )
            if path.startswith("/api/v1/analytics/implement-model"):
                # Peek not available easily; enforce key always when configured
                if provided != _OPS_KEY:
                    # Soft: still allow but route forces expose_price=False without key
                    request.state.ops_authorized = False
                else:
                    request.state.ops_authorized = True
            elif provided == _OPS_KEY:
                request.state.ops_authorized = True

        try:
            response = await call_next(request)
        except Exception:
            # Don't leak stack to client in production middleware path
            return JSONResponse({"ok": False, "error": "internal_error"}, status_code=500)

        # Security headers
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=()",
        )
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; connect-src 'self' https:; frame-ancestors 'none'",
        )
        # Hide tech fingerprint
        if "server" in response.headers:
            del response.headers["server"]
        response.headers.setdefault("X-Metrix-Security", "basic-1")

        return response


def install_security(app) -> None:
    """Attach security middleware (call once at startup)."""
    app.add_middleware(SecurityMiddleware)
