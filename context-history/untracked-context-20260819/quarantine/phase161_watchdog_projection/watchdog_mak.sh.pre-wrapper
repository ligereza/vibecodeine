#!/usr/bin/env bash
# Cron safety check for the long-running MAK services.
# systemd owns every daemon; this script never launches a detached process.
set -u

LOGDIR="$HOME/plataforma/logs"
mkdir -p "$LOGDIR"
exec 9>"$LOGDIR/watchdog.lock" || exit 0
flock -n 9 || exit 0

PYTHON="$HOME/plataforma/.venv/bin/python"
if [ ! -x "$PYTHON" ]; then
  PYTHON="$(command -v python3 || true)"
fi
GUARDIA="$HOME/plataforma/guardia.py"

set_user_bus() {
  local mak_user_id
  mak_user_id="$(id -u)"
  export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$mak_user_id}"
  export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=$XDG_RUNTIME_DIR/bus}"
}

set_user_bus

log() {
  printf '%s %s\n' "$(date '+%F %T')" "$*" >>"$LOGDIR/watchdog.log"
}

run_timeout() {
  timeout --signal=TERM --kill-after=5s 20s "$@"
}

if [ -x "$PYTHON" ] && [ -r "$GUARDIA" ]; then
  if ! run_timeout "$PYTHON" "$GUARDIA" --reap-stale-scans \
      >>"$LOGDIR/guardia.log" 2>&1; then
    log "process guard failed"
  fi
  if ! run_timeout "$PYTHON" "$GUARDIA" \
      >>"$LOGDIR/guardia.log" 2>&1; then
    log "resource check reported a constrained host"
  fi
fi

if [ ! -S "$XDG_RUNTIME_DIR/bus" ]; then
  log "user systemd bus unavailable: supervision deferred"
  exit 0
fi

systemctl_user() {
  run_timeout systemctl --user "$@"
}

ensure_unit() {
  unit="$1"
  if systemctl_user is-active --quiet "$unit"; then
    return 0
  fi

  log "unit inactive: $unit; requesting systemd start"
  systemctl_user reset-failed "$unit" >/dev/null 2>&1 || true
  if systemctl_user start "$unit" >/dev/null 2>&1; then
    log "systemd started: $unit"
  else
    log "systemd start failed: $unit"
    return 1
  fi
}

check_http() {
  unit="$1"
  url="$2"
  for attempt in 1 2 3 4 5; do
    if curl --fail --silent --show-error --max-time 8 \
        --output /dev/null "$url" 2>/dev/null; then
      return 0
    fi
    sleep 1
  done
  log "health check failed: $unit $url; requesting systemd restart"
  if systemctl_user restart "$unit" >/dev/null 2>&1; then
    log "systemd restarted after health failure: $unit"
    return 0
  fi
  log "systemd restart failed after health failure: $unit"
  return 1
}

# These are the only persistent services this watchdog is allowed to repair.
ensure_unit mak-hub.service || true
ensure_unit mak-codex.service || true
ensure_unit mak-xio.service || true
ensure_unit mak-research.service || true

health_ok=1
check_http mak-hub.service http://127.0.0.1:8900/health || health_ok=0
check_http mak-codex.service http://127.0.0.1:8891/api/jobs || health_ok=0
check_http mak-research.service http://127.0.0.1:8890/api/jobs || health_ok=0
if [ "$health_ok" -eq 1 ]; then
  log "supervision check passed"
else
  log "supervision check incomplete"
fi
