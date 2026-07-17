#!/bin/bash
# watchdog_mak.sh -- revive hub, codex y monitor xio (capa extra bajo systemd).
# Cron */5. No toca los servicios del research (tienen su propio watchdog).
set -u
LOGDIR="$HOME/plataforma/logs"
mkdir -p "$LOGDIR"

vivo() { pgrep -f "$1" >/dev/null 2>&1; }

if ! vivo "plataforma/hub.py"; then
  setsid python3 "$HOME/plataforma/hub.py" >>"$LOGDIR/hub.log" 2>&1 </dev/null &
  echo "$(date '+%F %T') revivi hub" >>"$LOGDIR/watchdog.log"
fi

if ! vivo "codex/interfaz_codex.py"; then
  if [ -f "$HOME/codex/.token" ]; then
    # shellcheck disable=SC1091
    . "$HOME/codex/.token"
    export CODEX_TOKEN
    setsid python3 "$HOME/codex/interfaz_codex.py" >>"$LOGDIR/codex.log" 2>&1 </dev/null &
    echo "$(date '+%F %T') revivi codex" >>"$LOGDIR/watchdog.log"
  else
    echo "$(date '+%F %T') codex sin .token, no arranco" >>"$LOGDIR/watchdog.log"
  fi
fi

if ! vivo "xio_puente/monitor.py"; then
  setsid python3 "$HOME/xio_puente/monitor.py" >>"$LOGDIR/xio.log" 2>&1 </dev/null &
  echo "$(date '+%F %T') revivi monitor xio" >>"$LOGDIR/watchdog.log"
fi
