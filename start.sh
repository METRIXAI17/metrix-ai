#!/bin/sh
# API always. Bot polls when TELEGRAM_BOT_TOKEN is set (Railway Variables).
# Bot loop: a crash must not leave Telegram silent until the next deploy.
set -eu
PORT="${PORT:-8787}"
uvicorn backend.main:app --host 0.0.0.0 --port "$PORT" \
  --proxy-headers --forwarded-allow-ips='*' --log-level info --timeout-keep-alive 30 &
API_PID=$!
if [ -n "${TELEGRAM_BOT_TOKEN:-}" ]; then
  (
    while true; do
      python -m telegram_app.bot || true
      echo "telegram bot exited; restart in 3s"
      sleep 3
    done
  ) &
fi
wait "$API_PID"
