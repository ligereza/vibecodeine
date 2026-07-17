#!/usr/bin/env bash
# watchdog.sh - Mantiene vivos los servicios de MAK research y rota logs.
# Se corre via cron cada 5 minutos.

BASE="$HOME/research"
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

# 3. Levantar cola.py si no corre
if ! pgrep -f "python3.*cola\.py" > /dev/null; then
    echo "$(date) - cola.py no esta corriendo. Lanzando..."
    nohup python3 "$BASE/cola.py" >> "$BASE/cola.log" 2>&1 9>&- &
fi

# 4. Levantar interfaz.py si no corre
if ! pgrep -f "python3.*interfaz\.py" > /dev/null; then
    echo "$(date) - interfaz.py no esta corriendo. Lanzando..."
    nohup python3 "$BASE/interfaz.py" >> "$BASE/interfaz.log" 2>&1 9>&- &
fi
