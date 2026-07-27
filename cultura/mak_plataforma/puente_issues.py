#!/usr/bin/env python3
"""puente_issues.py -- MAK atiende los issues de flyers, solo, sin Windows.

Pedido del usuario (2026-07-27): el puente ya funcionaba, pero corria EN
WINDOWS y en primer plano -- habia que estar presente y lanzarlo a mano. Eso
lo hacia inservible justo cuando se lo necesita: el usuario fuera de casa
pidiendo un render. Aca el mismo trabajo lo hace MAK por cron.

Que hace, en orden:

1. Busca issues abiertos con la etiqueta del intake Gmail -> issue.
2. Saca el link de Instagram del cuerpo y renderiza el flyer con el Blender
   local (GPU, Cycles) via el CLI del repo.
3. Sube el render a la nube con rclone. ESA es la entrega: el usuario lo abre
   desde el telefono, sin entrar a la maquina.
4. Comenta y cierra el issue.
5. Deja el flyer descargado en la bandeja del departamento, para que la
   curatoria lo perciba y su data entre a la cadena de RD.

Tres cosas que NO hace, a proposito:

- **No abre issues.** Orden del usuario: los issues son un CANAL suyo
  (Gmail -> Apps Script -> issue), no un tablero para agentes. Comentar y
  cerrar si; crear, nunca.
- **No renderea junto a una percepcion.** La GPU es de 4 GB y dos consumidores
  a la vez es lo que mato la corrida de julio. Pero a diferencia de las otras
  guardias, esta no se retira a esperar: PAUSA la percepcion, renderea y la
  reanuda. Un pedido del usuario le gana al trabajo de fondo, o el flyer
  llegaria al dia siguiente. Por eso NO toma el lock de la curatoria: ese lo
  retiene su guardia durante horas, y pedirlo dejaba al puente saliendose en
  cada tick sin renderizar nunca.
- **No publica rutas absolutas.** El issue es publico; el comentario lleva el
  destino en la nube y el nombre del archivo, nunca el disco.

Uso:
    python3 puente_issues.py              # una pasada (asi lo llama el cron)
    python3 puente_issues.py --dry-run    # ve que haria, no renderiza ni cierra
    python3 puente_issues.py --issue 320  # fuerza uno concreto

Cron sugerido (cada 10 minutos):
    */10 * * * * /usr/bin/python3 /home/mak/plataforma/puente_issues.py >> \\
      /home/mak/plataforma/logs/puente_issues.log 2>&1 # MAK-PUENTE-ISSUES
"""
import argparse
import fcntl
import signal
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HOME = Path.home()
REPO = "ligereza/vibecodeine"
ETIQUETA = "instagram"          # "Contains Instagram link", la del intake Gmail

FLUJO_SRC = HOME / "flujo" / "src"
RAIZ_RD = HOME / "RD"
BASE = RAIZ_RD / "AUTOMATIZACION"
BLENDER = HOME / "blender" / "blender"

# Lock PROPIO, y aca la razon, que costo un tick perdido el 2026-07-27:
# el lock de la curatoria (.guardia.lock) lo retiene su guardia durante TODAS
# las horas que dura una percepcion. Pedirlo aca dejaba al puente saliendose
# en cada tick -- justo en el caso para el que existe. Este lock solo impide
# que se solapen dos pasadas del puente; la contencion de GPU contra la
# percepcion se resuelve pausandola (ver PercepcionEnPausa), no esperandola.
LOCK = HOME / "plataforma" / ".puente_issues.lock"

# Bandeja del departamento: lo que cae aca lo percibe la curatoria en su
# proxima pasada (recorre ~/RD y saltea lo ya procesado), y de ahi sale la
# triangulacion headliner + fecha -> productora.
BANDEJA = RAIZ_RD / "desde_issues"

REMOTO = os.environ.get("MAK_RCLONE_REMOTO", "gdrive")
CARPETA_REMOTA = os.environ.get("MAK_RCLONE_CARPETA", "RD/renders")

ESTADO = HOME / "plataforma" / "puente_issues_estado.json"
IG_RE = re.compile(r"https://www\.instagram\.com/[^\s\)\]\"']+", re.IGNORECASE)


def _log(msg):
    print("%s %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


def _gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True, timeout=90)


def _estado():
    try:
        return json.loads(ESTADO.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"hechos": {}}


def _guardar_estado(st):
    try:
        ESTADO.parent.mkdir(parents=True, exist_ok=True)
        tmp = ESTADO.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(ESTADO)
    except OSError as e:
        _log("aviso: no pude guardar el estado (%s)" % e)


def issues_abiertos():
    r = _gh("issue", "list", "--repo", REPO, "--label", ETIQUETA,
            "--state", "open", "--json", "number,title,body", "--limit", "20")
    if r.returncode != 0:
        _log("error: gh issue list -- %s" % r.stderr.strip()[:200])
        return []
    try:
        return json.loads(r.stdout or "[]")
    except ValueError:
        return []


def _link_ig(texto):
    m = IG_RE.search(texto or "")
    return m.group(0).rstrip(".,)") if m else None


def _shortcode(url):
    m = re.search(r"/(?:p|reel|tv)/([A-Za-z0-9_-]+)", url or "")
    return m.group(1) if m else "sin-codigo"


def _pids_percepcion():
    r = subprocess.run(["pgrep", "-f", "percepcion.py correr"],
                       capture_output=True, text=True)
    return [int(p) for p in r.stdout.split() if p.strip().isdigit()]


class PercepcionEnPausa:
    """Pausa la percepcion mientras dura el render, y la reanuda siempre.

    Por que pausar y no esperar: la percepcion de un corpus dura HORAS. Si el
    puente espera su turno, un flyer pedido por el usuario llega al dia
    siguiente -- que es justo el caso que este puente existe para resolver
    (el usuario fuera de casa pidiendo un render). Un pedido humano le gana al
    trabajo de fondo, igual que una idea suya entra al frente de la cola.

    Por que es seguro: la percepcion lleva su propio checkpoint en
    procesados.txt y SIGSTOP no le hace perder nada; se probo cinco veces la
    noche del 2026-07-26. Lo que NO se hace nunca es matarla.

    El reanudar va en finally: si el render explota, la percepcion vuelve
    igual. Dejarla detenida seria peor que no haber renderizado.
    """

    def __init__(self):
        self.pids = []

    def __enter__(self):
        self.pids = _pids_percepcion()
        for pid in self.pids:
            try:
                os.kill(pid, signal.SIGSTOP)
            except OSError:
                pass
        if self.pids:
            _log("percepcion en pausa (%s) mientras renderizo"
                 % ",".join(str(p) for p in self.pids))
            # Que ollama suelte la VRAM: con el modelo residente, el render
            # no entra en los 4 GB. Es la causa de los OOM historicos.
            subprocess.run(
                ["curl", "-s", "http://127.0.0.1:11434/api/generate",
                 "-d", '{"model":"gemma3:4b","keep_alive":0}'],
                capture_output=True, timeout=30)
            time.sleep(4)
        return self

    def __exit__(self, *exc):
        for pid in self.pids:
            try:
                os.kill(pid, signal.SIGCONT)
            except OSError:
                pass
        if self.pids:
            _log("percepcion reanudada")
        return False


def renderizar(url):
    """Corre el CLI del repo. Devuelve (ok, salida, ruta_png|None)."""
    entorno = dict(os.environ)
    entorno["PYTHONPATH"] = str(FLUJO_SRC)
    entorno["FLUJO_RD_ROOT"] = str(RAIZ_RD)
    cmd = [sys.executable, "-m", "flujo", "eventos", "flyer-auto", url,
           "--render-blender", "--yes", "--blender-exe", str(BLENDER)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=3600, env=entorno, cwd=str(HOME / "flujo"))
    except subprocess.TimeoutExpired:
        return False, "el render paso de una hora y se corto", None
    salida = (r.stdout or "") + (r.stderr or "")
    png = BASE / "render_output.png"
    if r.returncode != 0 or not png.exists():
        return False, salida, None
    return True, salida, png


def subir(png, numero, shortcode):
    """Entrega real: el render a la nube. Devuelve el destino o None.

    Es lo que hace util al puente cuando el usuario no esta en casa: el
    archivo aparece en su Drive, no en un disco al que no puede llegar.
    """
    nombre = "render_issue%d_%s.png" % (numero, shortcode)
    destino = "%s:%s/%s" % (REMOTO, CARPETA_REMOTA, nombre)
    r = subprocess.run(["rclone", "copyto", str(png), destino],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        _log("error: rclone -- %s" % r.stderr.strip()[:200])
        return None
    return "%s/%s" % (CARPETA_REMOTA, nombre)


def al_departamento(numero, shortcode):
    """Copia el flyer descargado a la bandeja de la curatoria.

    El flyer no es solo una imagen a renderizar: trae headliners, fecha y
    lugar. Percibido, alimenta la triangulacion que el usuario definio
    (headliner + fecha = productora encontrable). Si no se copia, el dato se
    pierde apenas el proximo issue sobrescriba input_ig.jpg.
    """
    origen = BASE / "input_ig.jpg"
    if not origen.exists():
        return None
    try:
        BANDEJA.mkdir(parents=True, exist_ok=True)
        destino = BANDEJA / ("issue%d-%s.jpg" % (numero, shortcode))
        shutil.copy2(origen, destino)
        return destino.name
    except OSError as e:
        _log("aviso: no pude dejar el flyer en la bandeja (%s)" % e)
        return None


def comentar_y_cerrar(numero, ok, url, salida, destino, en_depto, dry_run):
    estado = "OK" if ok else "FALLO"
    partes = ["MAK: render %s para %s" % (estado, url)]
    if destino:
        partes.append("")
        partes.append("Entregado en `%s`." % destino)
    if en_depto:
        partes.append("Flyer enviado al departamento como `%s`: "
                      "su data entra a la cadena de RD." % en_depto)
    # Solo la cola del log y sin rutas: el issue es publico.
    partes.append("")
    partes.append("```\n%s\n```" % _sin_rutas(salida)[-2500:])
    cuerpo = "\n".join(partes)

    if dry_run:
        _log("[dry-run] comentaria y %s el issue #%d:\n%s"
             % ("cerraria" if ok else "dejaria abierto", numero, cuerpo))
        return
    r = _gh("issue", "comment", str(numero), "--repo", REPO, "--body", cuerpo)
    if r.returncode != 0:
        _log("error: comentar #%d -- %s" % (numero, r.stderr.strip()[:160]))
    if ok:
        c = _gh("issue", "close", str(numero), "--repo", REPO)
        if c.returncode != 0:
            _log("error: cerrar #%d -- %s" % (numero, c.stderr.strip()[:160]))


_RUTA_ABS = re.compile(r"(?:[A-Za-z]:\\[^\"'\r\n]*|/home/[^\s\"'\r\n]*)")


def _sin_rutas(texto):
    """Deja el nombre del archivo y borra el resto de la ruta.

    El issue es publico y el log de Blender viene lleno de rutas del disco.
    Cubre Windows y Linux porque el mismo puente corrio en las dos.
    """
    def corta(m):
        s = m.group(0)
        return ".../" + re.split(r"[\\/]", s)[-1]
    return _RUTA_ABS.sub(corta, texto or "")


def una_pasada(dry_run=False, solo=None):
    issues = issues_abiertos()
    if solo is not None:
        issues = [i for i in issues if i.get("number") == solo]
    if not issues:
        _log("sin issues de flyer pendientes")
        return 0

    st = _estado()
    hechos = 0
    for it in issues:
        numero = it.get("number")
        url = _link_ig(it.get("body") or "")
        if not url:
            _log("#%d sin link de Instagram, lo salteo" % numero)
            continue
        if str(numero) in st["hechos"] and solo is None:
            continue
        code = _shortcode(url)
        _log("#%d renderizando %s" % (numero, url))
        if dry_run:
            _log("[dry-run] no renderizo")
            comentar_y_cerrar(numero, True, url, "[dry-run]", None, None, True)
            continue

        with PercepcionEnPausa():
            ok, salida, png = renderizar(url)
        destino = subir(png, numero, code) if ok else None
        en_depto = al_departamento(numero, code) if ok else None
        comentar_y_cerrar(numero, ok, url, salida, destino, en_depto, False)
        st["hechos"][str(numero)] = {"url": url, "ok": ok,
                                     "destino": destino,
                                     "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
        _guardar_estado(st)
        hechos += 1
        _log("#%d %s" % (numero, "listo" if ok else "fallo"))
    return hechos


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--issue", type=int, default=None)
    ap.add_argument("--esperar-gpu", action="store_true",
                    help="espera el lock en vez de salir (por defecto sale y "
                         "reintenta en el proximo tick del cron)")
    args = ap.parse_args()

    # El lock protege la GPU, y --dry-run no la toca: pedirselo ahi solo
    # impediria mirar que haria el puente mientras la percepcion trabaja.
    if not args.dry_run:
        LOCK.parent.mkdir(parents=True, exist_ok=True)
        fh = open(LOCK, "w")
        try:
            fcntl.flock(fh, fcntl.LOCK_EX if args.esperar_gpu
                        else fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            _log("la GPU esta ocupada (percepcion o micelio); "
                 "reintento al proximo tick")
            return 0

    # A diferencia de las otras guardias, esta NO se retira si hay percepcion:
    # la pausa (ver PercepcionEnPausa) y la reanuda al terminar. El lock de
    # arriba sigue siendo el que impide dos renders a la vez.
    return una_pasada(dry_run=args.dry_run, solo=args.issue)


if __name__ == "__main__":
    sys.exit(0 if main() is not None else 1)
