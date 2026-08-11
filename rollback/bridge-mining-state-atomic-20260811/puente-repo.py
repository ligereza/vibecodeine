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
import signal
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows director has no fcntl
    fcntl = None

HOME = Path.home()
REPO = "ligereza/vibecodeine"

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

ESTADO = HOME / "plataforma" / "puente_issues_estado.json"

# Configuracion editable desde la cara del organismo (departamento render).
# Se relee en cada pasada a proposito: el cron arranca un proceso nuevo cada
# vez, pero si algun dia esto vive dentro de un servidor, un cambio hecho en la
# interfaz tiene que valer sin reiniciar nada.
CONFIG = HOME / "plataforma" / "render_config.json"
CONFIG_POR_DEFECTO = {
    "activo": True,
    "remoto": "gdrive",
    "carpeta": "RD/renders",
    "etiqueta": "instagram",
    "al_departamento": True,
    "pausar_percepcion": True,
}


def config():
    cfg = dict(CONFIG_POR_DEFECTO)
    try:
        cfg.update(json.loads(CONFIG.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        pass
    # El entorno sigue mandando sobre el archivo: sirve para probar una
    # entrega distinta sin tocar la configuracion que usa el cron.
    cfg["remoto"] = os.environ.get("MAK_RCLONE_REMOTO", cfg["remoto"])
    cfg["carpeta"] = os.environ.get("MAK_RCLONE_CARPETA", cfg["carpeta"])
    return cfg


IG_RE = re.compile(r"https://www\.instagram\.com/[^\s\)\]\"']+", re.IGNORECASE)
_RUTA_ABS = re.compile(
    r"(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/][^\s\"'<>|]+|"
    r"/(?:home|tmp|var|Users|mnt|opt|root|srv|work)[\\/][^\s\"'<>|]+)"
)


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


def issues_abiertos(etiqueta):
    r = _gh("issue", "list", "--repo", REPO, "--label", etiqueta,
            "--state", "open", "--json", "number,title,body", "--limit", "20")
    if r.returncode != 0:
        _log("error: gh issue list -- %s" % r.stderr.strip()[:200])
        return []
    try:
        return json.loads(r.stdout or "[]")
    except ValueError:
        return []


def _links_ig(texto):
    """TODOS los links del issue, sin repetir y en orden.

    Antes se tomaba solo el primero. La jefa del usuario manda mas de un evento
    en el mismo correo -- el issue #326 llego con dos -- y el segundo se perdia
    en silencio, que es el mismo defecto que este repo persigue: hacer menos de
    lo pedido sin decirlo.
    """
    vistos, salida = set(), []
    for m in IG_RE.finditer(texto or ""):
        u = m.group(0).rstrip(".,)")
        # El cuerpo del issue repite los links (lista + texto del correo).
        clave = _shortcode(u) + "|" + str(_indice_pedido_local(u))
        if clave in vistos:
            continue
        vistos.add(clave)
        salida.append(u)
    return salida


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
        # Que ollama suelte la VRAM: con el modelo residente, el render no entra
        # en los 4 GB. Es la causa de los OOM historicos.
        #
        # Esto va FUERA del `if self.pids` (2026-07-27). Antes solo se liberaba
        # cuando habia percepcion corriendo, y el modelo queda residente lo
        # cargue quien lo cargue: research, codex o el hub tambien lo levantan.
        # Medido en la caja ese dia: gemma3:4b con 1814 MiB de VRAM tomados y
        # 0% de uso. Con la percepcion detenida y el modelo cargado, el render
        # salia a competir por la memoria y esa es exactamente la condicion del
        # OOM que este bloque existe para evitar.
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


def guardado(numero, shortcode):
    """El render con nombre propio, para que renderizar y entregar se separen.

    `render_output.png` es una ruta FIJA que el CLI reescribe en cada corrida,
    asi que una entrega fallida costaba un render nuevo. Medido el 2026-07-31:
    el issue #420 se renderizo dos veces seguidas (~7 min cada una) porque
    rclone no alcanzaba a subirlo, y la pasada siguiente empezaba de cero en
    vez de reintentar la entrega. Con nombre propio, una pasada que encuentra
    el render hecho SOLO entrega.
    """
    d = BASE / "renders"
    d.mkdir(parents=True, exist_ok=True)
    return d / ("render_issue%d_%s.png" % (numero, shortcode))


def subir(png, numero, shortcode, cfg):
    """Entrega real: el render a la nube. Devuelve el destino o None.

    Es lo que hace util al puente cuando el usuario no esta en casa: el
    archivo aparece en su Drive, no en un disco al que no puede llegar.
    """
    nombre = "render_issue%d_%s.png" % (numero, shortcode)
    destino = "%s:%s/%s" % (cfg["remoto"], cfg["carpeta"], nombre)
    # Los reintentos se acotan a proposito. Medido el 2026-07-31 sobre el #420:
    # rclone llevaba escritos 363 MB para entregar un PNG de 16,6 MB -- estaba
    # reintentando en bucle, no subiendo lento (una prueba de 8 MB en la misma
    # ventana subio a 306 KiB/s). Un bucle interno se come el timeout entero y
    # la pasada reporta "fallo" sin decir que nunca dejo de intentar. Acotado,
    # falla temprano y el render queda guardado para el siguiente intento.
    r = subprocess.run(["rclone", "copyto", "--retries", "1",
                        "--low-level-retries", "3", str(png), destino],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        _log("error: rclone -- %s" % r.stderr.strip()[:200])
        return None
    return "%s/%s" % (cfg["carpeta"], nombre)


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


def cerrar_si_esta(numero, completo, piezas, dry_run):
    """Close the issue when the render is DELIVERED. It never comments.

    The user's order, 2026-07-31, after seeing an issue with ELEVEN comments:
    it should not create issues nor comment, only close when it has the render;
    otherwise the issue stays open and he will see it.

    How it got there: this commented on EVERY pass and only closed when
    everything had gone through. The cron runs every 10 minutes, so a request
    that does not finish becomes a comment every ten minutes -- eleven comments
    is under two hours. And every comment mails the user, and that mail can come
    back as a new issue through the Gmail bridge: the comment was not noise, it
    was the fuel of a loop.

    An open issue IS the message. It does not need writing down.

    What is lost: the failure detail no longer sits in the issue. What is not
    lost: it stays in `puente_issues_estado.json` and in the log, which is where
    whoever can act on it looks.
    """
    if not completo:
        pendientes = [p["code"] for p in piezas if not p["ok"]]
        _log("  #%d queda ABIERTO (%s pendiente) -- no comento" %
             (numero, ", ".join(pendientes) or "sin detalle"))
        return
    if dry_run:
        _log("[dry-run] cerraria #%d" % numero)
        return
    c = _gh("issue", "close", str(numero), "--repo", REPO)
    if c.returncode != 0:
        _log("error: cerrar #%d -- %s" % (numero, c.stderr.strip()[:160]))
    else:
        _log("  #%d CERRADO: el render esta entregado" % numero)

def _sin_rutas(texto):
    """Deja el nombre del archivo y borra el resto de la ruta.

    El issue es publico y el log de Blender viene lleno de rutas del disco.
    Cubre Windows y Linux porque el mismo puente corrio en las dos.
    """
    def corta(m):
        s = m.group(0)
        return ".../" + re.split(r"[\\/]", s)[-1]
    return _RUTA_ABS.sub(corta, texto or "")


def _indice_pedido_local(url):
    """Que imagen del carrusel pidio el link. Se guarda para que la cara pueda
    mostrar 'imagen 2 de un carrusel' y no dejar dudas de cual se uso."""
    import urllib.parse
    try:
        crudo = urllib.parse.parse_qs(
            urllib.parse.urlparse(url).query).get("img_index", ["1"])[0]
        return max(1, int(crudo))
    except (ValueError, TypeError):
        return 1


ES_VIDEO = re.compile(r"/(?:reel|tv)/", re.IGNORECASE)


def _motivo_pendiente(url, salida):
    """Por que MAK no puede resolver este link, en palabras del usuario.

    Existe porque el modo de falla mas caro no es fallar: es fallar en
    silencio. Un link que no se puede bajar tiene que quedar VISIBLE con su
    razon, no desaparecer del issue.
    """
    if ES_VIDEO.search(url or ""):
        return ("es un video: el render de video se hace en Windows, "
                "desde la app de flujo")
    texto = (salida or "").lower()
    if "httperrorpage" in texto or "no traia imagen" in texto:
        return ("Instagram no expone este post sin sesion (su embed devuelve "
                "una pagina de error). Pasa con posts sueltos y con perfiles "
                "con alcance restringido; se resuelve desde Windows")
    if "403" in texto or "login wall" in texto:
        return "Instagram bloqueo la descarga; se resuelve desde Windows"
    return "no se pudo bajar el flyer; se resuelve desde Windows"


def una_pasada(dry_run=False, solo=None):
    cfg = config()
    if not cfg.get("activo", True) and solo is None:
        _log("el departamento de render esta apagado en la configuracion")
        return 0
    issues = issues_abiertos(cfg["etiqueta"])
    if solo is not None:
        issues = [i for i in issues if i.get("number") == solo]
    if not issues:
        _log("sin issues de flyer pendientes")
        return 0

    st = _estado()
    hechos = 0
    for it in issues:
        numero = it.get("number")
        links = _links_ig(it.get("body") or "")
        if not links:
            _log("#%d sin link de Instagram, lo salteo" % numero)
            continue

        previo = st["hechos"].get(str(numero))
        # Solo se saltea lo COMPLETO. Anotar un fallo como hecho dejaba el
        # issue muerto para siempre: el #322 fallo por un 403 y los ticks
        # siguientes lo saltearon en silencio. Un fallo suele ser transitorio.
        if previo and previo.get("ok") and solo is None:
            continue
        if previo and solo is None:
            _log("#%d quedo incompleto (%s); reintento"
                 % (numero, previo.get("ts", "")))

        _log("#%d tiene %d link(s)" % (numero, len(links)))
        piezas = []
        for url in links:
            code = _shortcode(url)
            idx = _indice_pedido_local(url)

            # El video no se renderiza aca por decision del usuario: el de 600
            # cuadros se hace en Windows, que tiene la placa grande.
            if ES_VIDEO.search(url):
                _log("  %s es video -> pendiente para Windows" % code)
                piezas.append({"url": url, "code": code, "imagen": idx,
                               "ok": False, "destino": None,
                               "en_departamento": None,
                               "pendiente": _motivo_pendiente(url, "")})
                continue

            if dry_run:
                _log("  renderizando %s (imagen %d)" % (code, idx))
                piezas.append({"url": url, "code": code, "imagen": idx,
                               "ok": True, "destino": "[dry-run]",
                               "en_departamento": None, "pendiente": None})
                continue

            # Renderizar y entregar son dos actos, no uno. Si el render de una
            # pasada anterior sigue en disco, esta pasada solo lo entrega: la
            # GPU no vuelve a trabajar por un fallo que era de la red.
            hecho = guardado(numero, code)
            if hecho.exists() and hecho.stat().st_size > 0:
                _log("  %s ya renderizado -- solo entrego" % code)
                ok, salida, png = True, "", hecho
            else:
                _log("  renderizando %s (imagen %d)" % (code, idx))
                if cfg.get("pausar_percepcion", True):
                    with PercepcionEnPausa():
                        ok, salida, png = renderizar(url)
                else:
                    ok, salida, png = renderizar(url)
                if ok:
                    # El CLI escribe siempre en la misma ruta: se copia con
                    # nombre propio ANTES de intentar la entrega, que es lo que
                    # puede fallar.
                    shutil.copy2(str(png), str(hecho))
                    png = hecho
            destino = subir(png, numero, code, cfg) if ok else None
            en_depto = (al_departamento(numero, code)
                        if ok and cfg.get("al_departamento", True) else None)
            piezas.append({
                "url": url, "code": code, "imagen": idx, "ok": ok,
                "destino": destino, "en_departamento": en_depto,
                "pendiente": None if ok else _motivo_pendiente(url, salida),
                "log": _sin_rutas(salida)[-1200:] if not ok else "",
            })
            _log("  %s %s" % (code, "listo" if ok else "pendiente"))

        completo = all(p["ok"] for p in piezas)
        cerrar_si_esta(numero, completo, piezas, dry_run)
        st["hechos"][str(numero)] = {
            "ok": completo, "piezas": piezas,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        _guardar_estado(st)
        hechos += 1
        _log("#%d %s (%d/%d piezas)"
             % (numero, "cerrado" if completo else "queda abierto",
                sum(1 for p in piezas if p["ok"]), len(piezas)))
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
            if fcntl is not None:
                fcntl.flock(fh, fcntl.LOCK_EX if args.esperar_gpu
                            else fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            _log("ya hay una pasada del puente corriendo; "
                 "reintento al proximo tick")
            return 0

    # A diferencia de las otras guardias, esta NO se retira si hay percepcion:
    # la pausa (ver PercepcionEnPausa) y la reanuda al terminar. El lock de
    # arriba sigue siendo el que impide dos renders a la vez.
    return una_pasada(dry_run=args.dry_run, solo=args.issue)


if __name__ == "__main__":
    sys.exit(0 if main() is not None else 1)
