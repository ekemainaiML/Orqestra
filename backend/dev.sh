#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8000}"

echo "==> Killing any existing process on port $PORT..."
lsof -ti :"$PORT" 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 1

echo "==> Starting uvicorn with live reload on port $PORT..."
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --reload --reload-dir app
