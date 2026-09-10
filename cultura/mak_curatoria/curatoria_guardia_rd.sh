#!/bin/bash
# curatoria_guardia_rd.sh -- percepcion automatica, SOLO corpus RD.
#
# Por que separado de curatoria_guardia.sh: ese guard, una vez encendido
# (~/curatoria/AUTONOMY_ENABLE), procesa RD primero pero SIGUE con el
# corpus personal de IG (~7300 archivos, ~5700 sin procesar) sin parar --
# horas de GPU sobre un archivo que nadie pidio tocar ahora. El pedido
# (2026-09-09) era automatizar especificamente el camino issue->RD; este
# guard no tiene nocion de "ig" en absoluto, siempre pasa --solo-fuente rd.
#
# Mismo mutex que curatoria_guardia.sh (pgrep -f "percepcion.py correr"):
# las dos son GPU-bound y nunca deben correr juntas -- la GPU de 4GB no da
# para dos (fue lo que mato la corrida de julio). Si el guard general
# alguna vez se enciende tambien, este pgrep evita que se pisen.
#
# No requiere ~/curatoria/AUTONOMY_ENABLE a proposito: es un interruptor
# nuevo y mas chico, no el general. Apagar: quitar MAK-CURATORIA-RD del
# crontab.
set -u

CUR="$HOME/curatoria"
LOG="$CUR/guardia_rd.log"

exec 9>"$CUR/.guardia_rd.lock" || exit 0
flock -n 9 || exit 0

if pgrep -f "percepcion.py correr" > /dev/null; then
    exit 0
fi

# El render de Blender (disparado por issue_descarga_ig.yml en el runner de
# GitHub Actions) es la MISMA GPU de 4GB. No hay coordinacion explicita
# como la que tenia puente_issues.py (pausar_percepcion); lo mas simple y
# seguro es no arrancar si blender esta corriendo -- el proximo tick, 10
# minutos despues, casi seguro lo encuentra libre.
if pgrep -x blender > /dev/null; then
    exit 0
fi

python3 "$CUR/percepcion.py" reconciliar --out "$CUR" >> "$LOG" 2>&1 || exit 1

cd "$CUR" || exit 1
echo "$(date -Is) levantando percepcion (solo rd)" >> "$LOG"
python3 percepcion.py correr \
    --raiz-rd "$HOME/RD" \
    --out "$CUR" \
    --solo-fuente rd \
    --timeout-archivo 120 \
    < /dev/null >> "$CUR/repercepcion_rd.log" 2>&1
