#!/bin/sh
# API always. Bot polls when TELEGRAM_BOT_TOKEN is set (Railway Variables).
set -eu
PORT="${PORT:-8787}"
uvicorn backend.main:app --host 0.0.0.0 --port "$PORT" \
  --proxy-headers --forwarded-allow-ips='*' --log-level info --timeout-keep-alive 30 &
API_PID=$!
if [ -n "${TELEGRAM_BOT_TOKEN:-}" ]; then
  python -m telegram_app.bot &
fi
wait "$API_PID"
