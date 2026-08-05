#!/usr/bin/env bash
# watchdog.sh - Mantiene vivos los servicios de MAK research y rota logs.
# Se corre via cron cada 5 minutos.

BASE="$HOME/research"
ENV_FILE="${RESEARCH_ENV:-$HOME/n8n-local/research.env}"
COLA_DISABLED="$BASE/.cola.disabled.missing_ntfy"
cd "$BASE" || exit 1

# 1. Lock para no duplicar el watchdog si por alguna razon se cuelga
exec 9> watchdog.lock
if ! flock -n 9; then
    echo "Watchdog ya esta corriendo."
    exit 0
fi

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

# 3. Start cola.py only when the mobile ntfy inbox is configured.
# Without this guard cron restarts cola.py every five minutes and fills
# cola.log with the same "Falta NTFY_TOPIC_IN" line. That is not a service; it
# is noise that hides the real status of MAK.
if [ -n "${NTFY_TOPIC_IN:-}" ] || { [ -f "$ENV_FILE" ] && grep -Eq '^[[:space:]]*NTFY_TOPIC_IN=.+$' "$ENV_FILE"; }; then
    rm -f "$COLA_DISABLED"
    if ! pgrep -f "python3.*cola\.py" > /dev/null; then
        echo "$(date) - cola.py no esta corriendo. Lanzando..."
        nohup python3 "$BASE/cola.py" >> "$BASE/cola.log" 2>&1 9>&- &
    fi
else
    if [ ! -f "$COLA_DISABLED" ]; then
        echo "$(date) - cola.py desactivada: falta NTFY_TOPIC_IN en research.env"
        : > "$COLA_DISABLED"
    fi
fi

# 4. Levantar interfaz.py si no corre
if ! pgrep -f "python3.*interfaz\.py" > /dev/null; then
    echo "$(date) - interfaz.py no esta corriendo. Lanzando..."
    nohup python3 "$BASE/interfaz.py" >> "$BASE/interfaz.log" 2>&1 9>&- &
fi
