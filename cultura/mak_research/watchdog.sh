#!/usr/bin/env bash
# Cron safety check for MAK Research and its optional ntfy queue.
# systemd owns persistent processes; this script never creates detached launches.

BASE="$HOME/research"
ENV_FILE="${RESEARCH_ENV:-$HOME/research/research.env}"
COLA_DISABLED="$BASE/.cola.disabled.missing_ntfy"
RESEARCH_UNIT="mak-research.service"
QUEUE_UNIT="mak-research-queue.service"

set_user_bus() {
    local mak_user_id
    mak_user_id="$(id -u)"
    export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$mak_user_id}"
    export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=$XDG_RUNTIME_DIR/bus}"
}

set_user_bus

cd "$BASE" || exit 1

# 1. Lock para no duplicar el watchdog si por alguna razon se cuelga
exec 9> watchdog.lock
if ! flock -n 9; then
    echo "Watchdog is already running."
    exit 0
fi

systemctl_user() {
    timeout --signal=TERM --kill-after=5s 20s systemctl --user "$@"
}

ensure_unit() {
    unit="$1"
    if systemctl_user is-active --quiet "$unit"; then
        return 0
    fi
    echo "$(date) - $unit is inactive; requesting systemd start"
    systemctl_user reset-failed "$unit" >/dev/null 2>&1 || true
    if ! systemctl_user start "$unit" >/dev/null 2>&1; then
        echo "$(date) - systemd could not start $unit"
        return 1
    fi
    echo "$(date) - systemd started $unit"
}

# 2. Rotacion simple de logs (> 1MB)
for log in cola.log interfaz.log; do
    if [ -f "$log" ]; then
        size=$(stat -c%s "$log")
        if [ "$size" -gt 1048576 ]; then
            echo "$(date) - Rotando $log (tamano: $size bytes)"
            tail -c 500000 "$log" > "$log.tmp" && cat "$log.tmp" > "$log" && rm "$log.tmp"
        fi
    fi
done

if [ ! -S "$XDG_RUNTIME_DIR/bus" ]; then
    echo "$(date) - user systemd bus unavailable: supervision deferred"
    exit 0
fi

# 3. Start the queue only when the mobile ntfy inbox is configured.
# Without this guard cron restarts cola.py every five minutes and fills
# cola.log with the same "Falta NTFY_TOPIC_IN" line. That is not a service; it
# is noise that hides the real status of MAK.
if [ -n "${NTFY_TOPIC_IN:-}" ] || { [ -f "$ENV_FILE" ] && grep -Eq '^[[:space:]]*NTFY_TOPIC_IN=.+$' "$ENV_FILE"; }; then
    rm -f "$COLA_DISABLED"
    ensure_unit "$QUEUE_UNIT" || true
else
    if [ ! -f "$COLA_DISABLED" ]; then
        echo "$(date) - cola.py disabled: NTFY_TOPIC_IN is missing"
        : > "$COLA_DISABLED"
    fi
    if systemctl_user is-active --quiet "$QUEUE_UNIT"; then
        systemctl_user stop "$QUEUE_UNIT" >/dev/null 2>&1 || true
    fi
fi

# 4. Research interface is a systemd service. Do not launch a session child.
ensure_unit "$RESEARCH_UNIT" || true
echo "$(date) - supervision check passed"
