#!/bin/bash
# curatoria_guardia.sh -- mantiene viva la percepcion, un corpus a la vez.
#
# Por que existe: el 2026-07-23 la corrida se detuvo a las 18:04 y nadie se
# entero. No habia cron, se lanzaba a mano, y al morir quedo tres dias parada.
# Un lanzamiento por SSH tampoco sobrevive al cierre de la sesion.
#
# Por que flock y no solo pgrep: probado el 2026-07-26, pgrep sola dejo levantar
# un segundo proceso. Dos percepciones sobre una GPU de 4 GB es exactamente lo
# que provoco los timeouts de ollama que mataron la corrida de julio.
#
# Por que un corpus a la vez: misma razon. RD primero (alimenta la cola de
# triangulacion), y cuando RD termina, el archivo del artista (alimenta el mapa
# conceptual). Nunca los dos juntos.
#
# Corre cada 10 minutos. Apagar: quitar MAK-CURATORIA del crontab.
set -u

CUR="$HOME/curatoria"
LOG="$CUR/guardia.log"

if [ ! -f "$CUR/AUTONOMY_ENABLE" ]; then
    exit 0
fi

exec 9>"$CUR/.guardia.lock" || exit 0
flock -n 9 || exit 0

if pgrep -f "percepcion.py correr" > /dev/null; then
    exit 0
fi

# Repair the legacy checkpoint and compact retries before deciding that a
# corpus is complete. Without this call, a completed legacy corpus never starts
# Python and therefore never gets a chance to repair itself.
python3 "$CUR/percepcion.py" reconciliar --out "$CUR" >> "$LOG" 2>&1 || exit 1

# Que corpus toca. Devuelve 'rd', 'ig' o 'listo'.
FUENTE=$(python3 - <<'PY' 2>/dev/null
import hashlib, json, os

CUR = os.path.expanduser("~/curatoria")


def procesados_por_fuente():
    hechos = {"rd": set(), "ig": set()}
    try:
        with open(os.path.join(CUR, "procesados.txt"), encoding="utf-8") as fh:
            for linea in fh:
                linea = linea.strip()
                if ":" in linea:
                    f, resto = linea.split(":", 1)
                    if f in hechos:
                        hechos[f].add(resto)
    except OSError:
        pass
    return hechos


def cuarentena_por_fuente(raices):
    hechos = {"rd": set(), "ig": set()}
    try:
        with open(os.path.join(CUR, "fallos.json"), encoding="utf-8") as fh:
            fallos = json.load(fh)
        for clave, estado in fallos.items():
            if not isinstance(estado, dict) or not estado.get("cuarentena"):
                continue
            if ":" in clave:
                fuente, ruta = clave.split(":", 1)
                if fuente in hechos and fuente in raices:
                    try:
                        st = os.stat(os.path.join(raices[fuente], ruta))
                        path = os.path.join(raices[fuente], ruta)
                        with open(path, "rb") as fh:
                            head = fh.read(65536)
                            fh.seek(max(0, st.st_size - 65536))
                            tail = fh.read(65536)
                        digest = hashlib.sha256(head + tail).hexdigest()[:16]
                        firma_actual = "%s:%s:%s" % (st.st_size, st.st_mtime, digest)
                    except OSError:
                        continue
                    if estado.get("firma") == firma_actual:
                        hechos[fuente].add(ruta)
    except (OSError, ValueError):
        pass
    return hechos


def total(raiz):
    n = 0
    for _, _, archivos in os.walk(raiz):
        n += len(archivos)
    return n


raices = {
    "rd": os.path.expanduser("~/RD"),
    "ig": os.path.expanduser("~/portfolio_media/media"),
}
hechos = procesados_por_fuente()
cuarentena = cuarentena_por_fuente(raices)
rd_total = total(raices["rd"])
if len(hechos["rd"] | cuarentena["rd"]) < rd_total:
    print("rd")
else:
    ig = raices["ig"]
    if os.path.isdir(ig) and len(hechos["ig"] | cuarentena["ig"]) < total(ig):
        print("ig")
    else:
        print("listo")
PY
)

[ "$FUENTE" = "listo" ] && exit 0
[ -z "$FUENTE" ] && exit 0

echo "$(date -Is) levantando percepcion (fuente=$FUENTE)" >> "$LOG"
cd "$CUR" || exit 1

if [ "$FUENTE" = "rd" ]; then
    RAIZ_FLAG=(--raiz-rd "$HOME/RD")
else
    RAIZ_FLAG=(--raiz-ig "$HOME/portfolio_media/media")
fi

# Keep the worker attached to this cron invocation. The lock remains held for
# the whole run, so the next tick skips it instead of creating a child orphan.
python3 percepcion.py correr \
    "${RAIZ_FLAG[@]}" \
    --out "$CUR" \
    --solo-fuente "$FUENTE" \
    --timeout-archivo 120 \
    < /dev/null >> "$CUR/repercepcion_${FUENTE}.log" 2>&1
