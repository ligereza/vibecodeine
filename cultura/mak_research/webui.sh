#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

mkdir -p logs
PORT="${INTERFAZ_PORT:-8890}"
PID_FILE="$BASE_DIR/.webui.pid"

if [ -f "$PID_FILE" ]; then
  OLD_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "Web UI ya está corriendo (PID $OLD_PID)."
    echo "Abrir: http://127.0.0.1:$PORT"
    exit 0
  fi
fi

nohup python3 interfaz.py > "$BASE_DIR/logs/webui.log" 2>&1 &
NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"

sleep 2
if kill -0 "$NEW_PID" 2>/dev/null; then
  echo "Web UI iniciada en http://127.0.0.1:$PORT"
  echo "Log: $BASE_DIR/logs/webui.log"
else
  echo "No se pudo iniciar la Web UI." >&2
  exit 1
fi
