#!/usr/bin/env python3
"""trabajo.py -- el orquestador del trabajo autonomo del organismo MAK.

El cron lo dispara cada CADA_MIN. En cada tick hace UNA unidad de trabajo,
ciclando los verbos de roles.py (multiplicar/definir/limpiar/desarrollar) por
round-robin, con topes de carga/cupo/gap. El ritmo se adapta a la red: offline
(local serial y lento) se espacia mas. El fallback nube<->local lo maneja
red_ok() dentro de las libs de cada departamento; aca solo se decide QUE y
CUANDO, y se despacha por HTTP a research :8890 / codex :8891.

Apagar: quitar la linea MAK-TRABAJO del crontab.
Ajustar ritmo/verbos/modulos/semillas: editar roles.py.
"""
import json
import os
import re
import time
import urllib.parse
import urllib.request

HOME = os.path.expanduser("~")
import sys
sys.path.insert(0, os.path.join(HOME, "plataforma"))
sys.path.insert(0, os.path.join(HOME, "research"))
import roles  # noqa: E402
try:
    from research_lib import red_ok  # comparte la deteccion de red
except Exception:  # noqa: BLE001 - si falla, asumimos online
    def red_ok():
        return True
try:
    import backlog  # noqa: E402
    try:
        import material  # noqa: E402
    except Exception:
        material = None
except Exception:
    backlog = None

STATE = os.path.join(HOME, "plataforma/.trabajo_state.json")
LOG = os.path.join(HOME, "plataforma/logs/trabajo.log")
BACKLOG = os.path.join(HOME, "plataforma/backlog_codex.txt")
SEMILLAS_F = os.path.join(HOME, "plataforma/semillas_latido.txt")
RESEARCH = "http://127.0.0.1:8890/run"
CODEX = "http://127.0.0.1:8891/run"
BACKLOG_GEN = os.path.join(HOME, "plataforma/backlog.jsonl")
INFORMES_DIRS = [os.path.join(HOME, "research", d) for d in ("informes", "cadenas", "paneles", "refutaciones", "grafos", "memoria")]
# nota: dirs que no existen son saltados por cosechar


def log(m):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(m + "\n")
    except OSError:
        pass


def load1():
    try:
        return os.getloadavg()[0]
    except (OSError, AttributeError):
        return 0.0


def _state():
    try:
        with open(STATE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _save(s):
    try:
        with open(STATE, "w") as f:
            json.dump(s, f)
    except OSError:
        pass


def _lineas(path, fallback):
    try:
        with open(path, encoding="utf-8") as f:
            xs = [x.strip() for x in f if x.strip() and not x.startswith("#")]
        return xs or fallback
    except OSError:
        return fallback


def _post(url, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return r.read(2000).decode("utf-8", "replace")


def _resp_ok(resp):
    """Parsea el body JSON de /run; (True, "") si ok o no-JSON (legacy), (False, error) si ok==false."""
    try:
        d = json.loads(resp)
    except ValueError:
        return (True, "")
    if not isinstance(d, dict):
        return (True, "")
    if not d.get("ok", True):
        return (False, str(d.get("error", ""))[:200])
    return (True, "")


# Un tema que es el TEXTO DE UN FALLO no es un tema. Medido el 2026-08-01: el
# organismo estaba investigando "**Detalles del Evento:** No se encontraron
# detalles especificos", con los asteriscos de Markdown adentro. Eso no salio
# de una pregunta: salio de un campo vacio de una ficha, entro al backlog que
# se autorellena, y produjo un informe cada 30 minutos por cron. El formato del
# informe se puede arreglar -- se arreglo el mismo dia -- y no sirve de nada:
# un informe impecable sobre "no se encontraron detalles" sigue siendo basura,
# solo que mejor escrita.
#
# SOLO marcas de render, y esa lista corta es el resultado de haberse
# equivocado midiendo. La primera version rechazaba tambien por frases de
# ausencia ("no se encontro", "falta de", "no hay informacion"), y al correrla
# contra el backlog real -- 167 preguntas -- rechazaba 82. Mirando las 82, la
# mitad eran preguntas de investigacion LEGITIMAS: "la falta de investigacion
# sobre la relacion entre la estetica y la construccion de identidades
# culturales" es un tema, no un fallo. El filtro habria borrado la mitad del
# trabajo del organismo.
#
# Y la hipotesis de que la cola era una pregunta repetida tampoco se sostuvo:
# agrupadas por vocabulario, las 167 dan 150 grupos distintos. Solo 32 se
# repiten, y varias de esas son eventos DISTINTOS con la misma forma de
# pregunta, que no es repetirse.
#
# Lo unico que quedo probado como defecto fue el MARCADO: un tema no es un
# fragmento de documento. Esta es la red de ultimo momento; el arreglo de
# verdad esta en `backlog.preguntas_del_informe`, que lee el dato en vez de
# parsear la prosa.
_MARCAS_DE_RENDER = ("**", "##", "```", "|---")

# Se reusa el limpiador de `backlog` en vez de escribir un segundo: dos
# limpiadores del mismo marcado se separan, y entonces la cola y el que la
# consume dejan de coincidir sobre que es un tema.
try:
    from backlog import _limpiar_render
except ImportError:
    _limpiar_render = None


def tema_limpio(texto):
    """(tema, motivo). El tema listo para usar, o "" con el motivo del descarte.

    REPARA antes de rechazar, y esa es la diferencia que costo medirlo: en el
    backlog real hay 66 preguntas de 167 que traen marcado (`**Titulo:** cuerpo`)
    y NO son basura -- son preguntas envueltas en el formato del informe del que
    salieron. Tirarlas seria tirar el 40% del trabajo acumulado del organismo
    por un problema de presentacion.

    Solo se descarta lo que despues de desenvuelto no queda siendo nada: una
    fila de tabla, un separador, un titulo vacio.

    Devuelve el MOTIVO para que quien llame pueda contar por que descarto: un
    rechazo silencioso deja la cola vaciandose sin que nadie sepa de que."""
    t = (texto or "").strip()
    if _limpiar_render is not None:
        t = _limpiar_render(t)
    else:
        # Sin backlog importable se limpia lo minimo, en vez de dejar pasar el
        # marcado entero. Degradar no es lo mismo que no hacer nada.
        for m in _MARCAS_DE_RENDER:
            t = t.replace(m, " ")
        t = t.strip()
    if len(t) < 12:
        return "", "queda en %d caracteres despues de limpiar el marcado" % len(t)
    if len(t) > 400:
        return "", "demasiado largo (%d caracteres)" % len(t)
    if not any(c.isalpha() for c in t):
        return "", "no tiene una sola letra"
    return t, ""


def _tarea(verbo, st):
    """Arma (depto, payload_dict) para un verbo, o None si no hay trabajo."""
    v = next((x for x in roles.VERBOS if x["verbo"] == verbo), None)
    if not v:
        return None
    fuente = v["fuente"]
    sems = _lineas(SEMILLAS_F, roles.SEMILLAS)
    if fuente == "material":
        # La cola que sale de lo percibido (triangulacion RD + lineas de las
        # obras). Si esta vacia devolvemos None y la rotacion sigue: el modo
        # autonomo es el fallback, no el default.
        if material is None:
            return None
        tarea = material.pop_pendiente()
        if not tarea:
            return None
        if tarea.get("depto") == "codex":
            return ("codex", {"modo": tarea.get("modo", "generar"),
                              "pedido": tarea["texto"], "densidad": "medio"})
        tema, motivo = tema_limpio(tarea["texto"])
        if not tema:
            print("tema descartado (%s): %.70s" % (motivo, tarea["texto"]),
                  flush=True)
            return None
        return ("research", {"modo": tarea.get("modo", "research"),
                             "tema": tema, "densidad": "corto"})
    if fuente == "concepto":
        if backlog is not None:
            entrada = backlog.pop_pendiente(BACKLOG_GEN)
            if entrada:
                tema, motivo = tema_limpio(entrada["pregunta"])
                if not tema:
                    # Se DICE. Una tarea que desaparece sin dejar rastro es
                    # como esta cola se lleno de vinnetas sin que nadie lo
                    # notara durante dias.
                    print("tema descartado (%s): %.70s"
                          % (motivo, entrada["pregunta"]), flush=True)
                    return None
                return ("research", {"modo": v["modo"], "tema": tema,
                                     "densidad": "corto"})
        i = st.get("sem_idx", 0) % len(sems)
        st["sem_idx"] = i + 1
        return ("research", {"modo": v["modo"], "tema": sems[i], "densidad": "corto"})
    if fuente == "definir":
        i = st.get("def_idx", 0) % len(sems)
        st["def_idx"] = i + 1
        tema = "definicion cultural precisa y genealogia de: " + sems[i]
        return ("research", {"modo": v["modo"], "tema": tema, "densidad": "corto"})
    if fuente == "modulo":
        mods = roles.MODULOS
        i = st.get("mod_idx", 0) % len(mods)
        st["mod_idx"] = i + 1
        return ("codex", {"modo": v["modo"], "pedido": mods[i], "densidad": "medio"})
    if fuente == "backlog":
        bl = _lineas(BACKLOG, [])
        if not bl:
            return None  # sin backlog: desarrollar no tiene trabajo este tick
        i = st.get("bl_idx", 0) % len(bl)
        st["bl_idx"] = i + 1
        return ("codex", {"modo": v["modo"], "pedido": bl[i], "densidad": "medio"})
    return None


def main():
    ts = time.strftime("%F %T")
    now = time.time()
    # dia anclado a las 19:00 locales (de 19:00 a 19:00), no fecha calendario
    # 2026-07-23; causa: reset a medianoche regala las horas de trabajo del
    # usuario; retiro: tope dinamico por medicion de consumo
    hoy = time.strftime("%Y-%m-%d", time.localtime(now - 19 * 3600))
    st = _state()
    if st.get("date") != hoy:
        st = {"date": hoy, "count": 0, "last": 0, "verbo_idx": 0}
    if backlog is not None:
        try:
            n = backlog.cosechar(INFORMES_DIRS, BACKLOG_GEN)
            if n:
                log("%s cosecha: +%d preguntas al backlog generativo" % (ts, n))
        except Exception:
            pass
    if load1() > roles.LOAD_MAX:
        log("%s skip: load %.2f > %s" % (ts, load1(), roles.LOAD_MAX))
        return
    online = red_ok()
    gap = (roles.GAP_MIN if online else roles.GAP_MIN_OFFLINE) * 60
    if now - st.get("last", 0) < gap:
        return  # aun en el gap; el proximo tick del cron reintenta
    if st.get("count", 0) >= roles.MAX_DIA:
        log("%s skip: tope diario (%d)" % (ts, roles.MAX_DIA))
        return

    # PRIORIDAD: mientras haya material del usuario en cola, se atiende eso.
    # Sin esto el round-robin le daba 1 de cada 5 turnos y la cola crecia mas
    # rapido de lo que drenaba -- o sea, el modo autonomo seguia ganando.
    # Cuando la cola se vacia, el verbo atender no produce tarea y la rotacion normal
    # sigue su curso: el modo autonomo es el fallback, como fue disenado.
    n = len(roles.VERBOS)
    idx = st.get("verbo_idx", 0) % n
    if any(v["verbo"] == "atender" for v in roles.VERBOS):
        idx = next(i for i, v in enumerate(roles.VERBOS) if v["verbo"] == "atender")
    tarea = None
    verbo = None
    for k in range(n):
        verbo = roles.VERBOS[(idx + k) % n]["verbo"]
        tarea = _tarea(verbo, st)
        if tarea:
            st["verbo_idx"] = (idx + k + 1) % n
            break
    if not tarea:
        log("%s skip: ningun verbo con trabajo" % ts)
        _save(st)
        return

    depto, payload = tarea
    url = RESEARCH
    if depto == "codex":
        url = CODEX
    try:
        resp = _post(url, payload)
        ok, err = _resp_ok(resp)
        if not ok:
            log("%s [%s] %s RECHAZADO: %s"
                % (ts, "on" if online else "OFF", verbo, err))
            _save(st)
            return
        st["count"] = st.get("count", 0) + 1
        st["last"] = now
        _save(st)
        if backlog is not None and st["count"] % 8 == 0:
            try:
                backlog.curar(BACKLOG_GEN)
            except Exception:
                pass
        etiqueta = payload.get("tema") or payload.get("pedido") or ""
        log("%s [%s] %s #%d/%d (%s) -> %s"
            % (ts, "on" if online else "OFF", verbo, st["count"], roles.MAX_DIA,
               etiqueta[:60], resp[:50]))
    except Exception as e:  # noqa: BLE001 - el orquestador no debe morir
        _save(st)
        log("%s [%s] %s FALLO: %s" % (ts, "on" if online else "OFF", verbo, str(e)[:120]))


if __name__ == "__main__":
    main()
