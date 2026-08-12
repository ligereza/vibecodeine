#!/usr/bin/env python3
"""La cola de trabajo que sale del material real, no de la propia salida.

MAK tenia cuatro fuentes de trabajo -- concepto, definir, modulo, backlog -- y
las cuatro nacen de lo que MAK ya escribio: el backlog se cosecha de las
"LAGUNAS DE INFORMACION" de sus propios informes, y las semillas son una lista
fija. Eso esta bien como MODO AUTONOMO (sin material nuevo, o sin internet), que
es para lo que se diseno. El defecto medido el 2026-07-26 es que corria como
modo POR DEFECTO teniendo 57 GB de material del usuario y red disponible: 2
trabajos de 24 ese dia, todos sobre genealogia cultural.

Esta cola invierte eso. Sale de lo percibido:

  RD    -> triangulacion: flyer con fecha + headliner y productora desconocida
           se convierte en una pregunta verificable para research.
           (formula del usuario: "si tienes headliner y tienes fecha = tienes
           productora potencialmente encontrable por research")

  iskvw -> lo que la propia obra propuso: `linea_investigacion` va a research,
           `oportunidad_codigo` va a codex.

Salida: ~/plataforma/material.jsonl, una tarea por linea, deduplicada por hash
del texto. trabajo.py la consume ANTES que las fuentes autonomas; cuando se
vacia, el organismo vuelve solo a su modo autonomo.

Uso:
    python3 material.py            # reconstruye la cola desde las fichas
    python3 material.py --contar   # solo informa cuanto hay
    python3 material.py --degradar-ocurrencias [--aplicar]
"""
import hashlib
from contextlib import contextmanager
import re
import threading
import time
import unicodedata
import json
import os
import sys

try:
    from cultura.mak_conductor.runtime import active_enabled, dispatch_sync
except ImportError:  # pragma: no cover - direct MAK deployment
    sys.path.insert(0, os.environ.get("MAK_CONDUCTOR_PATH", "/home/mak/flujo/cultura"))
    try:
        from mak_conductor.runtime import active_enabled, dispatch_sync
    except ImportError:
        active_enabled = lambda: False
        dispatch_sync = None

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows falls back to thread lock
    fcntl = None

FICHAS = os.path.expanduser("~/curatoria/fichas/fichas.jsonl")
COLA = os.path.expanduser("~/plataforma/material.jsonl")
_QUEUE_LOCK = threading.RLock()


@contextmanager
def _queue_exclusive():
    """Protect queue read-modify-write across Hub threads and MAK processes."""
    with _QUEUE_LOCK:
        lock_path = COLA + ".lock"
        fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)


# Palabras que aparecen en un cartel y no son el nombre de nadie. Sale de mirar
# lo que el modelo devolvio de verdad, no de imaginar: "FULL" fue el primer
# falso positivo que llego a produccion.
_NO_SON_ARTISTAS = {
    "full", "live", "set", "dj", "djs", "lineup", "line up", "guest",
    "invitado", "invitados", "residentes", "special", "guests", "b2b",
    "showcase", "presenta", "presents", "vs", "and", "more", "tba",
    # Eslogans que el modelo devolvia como si fueran el cartel. "LIVE JAM"
    # llego a produccion: el flyer decia "NO ES UN DJ SET, ESTO ES UN LIVE
    # JAM", y salio una pregunta preguntando que productora hizo el evento
    # "con LIVE JAM en el cartel".
    "jam", "session", "sessions", "party", "fiesta", "club", "night",
    "noche", "edition", "edicion", "open", "closing", "opening", "after",
    "warm", "up", "vol", "aniversario", "anniversary", "tour", "show",
    "air", "stage", "arena", "festival", "edicion",
}

# Palabras de ciudad que el OCR pega adelante del lugar: "SANTIAGO DE CHILE
# ESPACIO RIESGO" es un venue con la ciudad encima, no un venue distinto.
_CIUDADES = ("santiago de chile", "santiago", "chile", "region metropolitana")

# Un mes escrito, o algo con pinta de fecha. Sin esto entraba "23:00 HRS"
# como si fuera la fecha del evento.
_MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
          "agosto", "septiembre", "setiembre", "octubre", "noviembre",
          "diciembre", "jan", "feb", "mar", "apr", "abr", "may", "jun",
          "jul", "aug", "ago", "sep", "oct", "nov", "dic", "dec")
_FECHA_NUM = re.compile(r"\b\d{1,2}\s*[./-]\s*\d{1,2}(\s*[./-]\s*\d{2,4})?\b")
# El punto es ambiguo: "02.05" es el 2 de mayo y "21.00" son las nueve. Por eso
# solo cuenta como hora con dos puntos, o con un marcador explicito detras
# (hrs/am/pm). Sin esta distincion se borraba "02.05, 09.05", que eran las dos
# fechas de un ciclo, y la ficha quedaba sin fecha.
_HORARIO = re.compile(
    r"\b\d{1,2}\s*(?::\s*\d{2}|[.]\s*\d{2}\s*(?=\s*(?:hrs?|horas?|am|pm)))"
    r"\s*(hrs?|horas?|am|pm)?"
    r"(\s*[-a]\s*\d{1,2}\s*(?::\s*\d{2}|[.]\s*\d{2})\s*(hrs?|horas?|am|pm)?)?",
    re.I)


def _sin_acentos(t):
    return "".join(c for c in unicodedata.normalize("NFD", t)
                   if unicodedata.category(c) != "Mn")


def _norm(t):
    """Forma comparable: sin acentos, sin puntuacion, sin espacios de mas."""
    t = _sin_acentos(str(t or "").lower())
    return re.sub(r"[^a-z0-9 ]+", " ", t).strip()


def _fecha_util(fecha):
    """La fecha sin horarios, o "" si lo que vino no es una fecha.

    Devolver "" hace que la ficha NO genere pregunta, que es lo correcto: sin
    fecha no hay triangulacion posible y preguntar igual solo suma ruido.
    """
    limpia = _HORARIO.sub(" ", str(fecha or ""))
    limpia = re.sub(r"\s{2,}", " ", limpia).strip(" ,-").strip()
    if not limpia:
        return ""
    plana = _sin_acentos(limpia.lower())
    if any(m in plana for m in _MESES) or _FECHA_NUM.search(plana):
        return limpia
    return ""


def _venue_util(venue):
    """El lugar sin la ciudad pegada adelante, o "" si era solo la ciudad.

    Dos casos medidos sobre fichas reales: "SANTIAGO DE CHILE ESPACIO RIESGO"
    es un venue con la ciudad encima, y "SANTIAGO DE CHILE" a secas no es un
    venue -- preguntar "en DE CHILE" es peor que no decir donde.
    """
    v = re.sub(r"\s{2,}", " ", str(venue or "").strip())
    for _ in range(3):                       # "santiago" dentro de "santiago de chile"
        plano = _norm(v)
        if not plano:
            return ""
        if plano in _CIUDADES:               # el venue ERA la ciudad
            return ""
        recortado = None
        for ciudad in _CIUDADES:
            if plano.startswith(ciudad + " "):
                recortado = v[len(ciudad):].strip(" ,-")
                break
        if recortado is None:
            break
        v = recortado
    plano = _norm(v)
    # Lo que queda tiene que parecer un lugar, no una sobra ("de chile").
    if plano in _CIUDADES or len(plano) < 4 or plano in ("de chile", "de"):
        return ""
    return v.strip()


def _es_artista(nombre):
    """Un nombre compuesto SOLO de palabras genericas no es nadie.

    El filtro anterior miraba la palabra entera, asi que "LIVE JAM" pasaba por
    tener mas de 3 caracteres y no estar en la lista.
    """
    palabras = [p for p in _norm(nombre).split() if p]
    if not palabras:
        return False
    if len("".join(palabras)) <= 3:
        return False
    return any(p not in _NO_SON_ARTISTAS for p in palabras)


def _txt(v):
    if isinstance(v, list):
        return ", ".join(str(x) for x in v if x).strip()
    return str(v or "").strip()


def _hash(texto):
    return hashlib.sha1(texto.lower().encode("utf-8")).hexdigest()[:12]


# Con que estado nace una tarea segun de donde salio, y es la diferencia entre
# una pregunta y una ocurrencia.
#
# `rd` triangula: la pregunta la define el flyer -- fecha + cabeza de cartel --
# y la respuesta es un nombre con una URL o "NO SE ENCONTRO". Eso es una
# pregunta y nace `pendiente`.
#
# `ig` sale de `oportunidad_codigo` y `linea_investigacion`, dos campos donde al
# modelo se le pide EXPLICITAMENTE que especule: "si la obra sugiere un
# procedimiento que podria automatizarse, describi que programa la generaria".
# Eso es una ocurrencia sobre una foto, y hasta el 2026-08-01 se convertia
# textual en orden de trabajo.
#
# Medido ese dia sobre la cola real: 2.812 tareas, de las cuales 2.696 (95,9%)
# nacieron asi -- 1.342 desde `oportunidad_codigo` y 1.354 desde
# `linea_investigacion`, con 1.342 obras generando las DOS. Al ritmo real del
# organismo (~15 al dia) son 177 dias de cola, y se rellena cada hora. Una de
# ellas mando a MAK a "generar una base de datos de tatuajes por tipo de imagen
# y elementos" a las 02:00, desde una foto de 2020. Nadie lo decidio.
#
# Inventar que hacer esta bien; DECIDIRLO sin formato no (palabras del usuario,
# 2026-08-01). Asi que nacen `propuesta`: quedan escritas, contadas y visibles,
# y `pop_pendiente` no las despacha. Para pasar a `pendiente` tienen que
# responder las tres preguntas de `flujo.micelio.evaluar_propuesta` -- quien lo
# va a usar, donde se busco que no exista ya, y como se sabe que salio bien.
# No se borran: la ocurrencia puede ser buena y el archivo es del artista.
ESTADO_INICIAL = {"rd": "pendiente", "ig": "propuesta"}


def tareas_desde_fichas():
    vistos = set()
    tareas = []
    if not os.path.exists(FICHAS):
        return tareas
    with open(FICHAS, encoding="utf-8", errors="replace") as fh:
        for linea in fh:
            try:
                f = json.loads(linea)
            except Exception:
                continue
            fuente = f.get("fuente")
            v = f.get("vision") or {}
            e = f.get("datos_evento") or {}

            if fuente == "rd":
                fecha = _txt(e.get("fecha"))
                heads = e.get("headliners") or []
                if isinstance(heads, str):
                    heads = [heads]
                heads = [h for h in (str(x).strip() for x in heads) if h]
                prod = _txt(e.get("productora"))
                venue = _txt(e.get("venue"))
                # Solo los flyers de evento triangulan. Medido el 2026-07-26:
                # el modelo le pone `headliners` a un LOGO ("GRID SYSTEM",
                # "street machine" son marcas, no artistas del cartel), y eso
                # ensuciaba la cola con preguntas que no son preguntas.
                if f.get("categoria") != "flyer_evento":
                    continue
                # La fecha tiene que ser una fecha. "23:00 HRS" no lo es, y
                # entraba igual: se pregunto por "el evento del 23:00 HRS".
                fecha = _fecha_util(fecha)
                venue = _venue_util(venue)
                # Sin fecha o sin cartel no hay como triangular.
                if not fecha or not heads:
                    continue
                heads = [h for h in heads if _es_artista(h)]
                if not heads:
                    continue
                if prod:
                    continue  # ya se sabe quien fue; no se pregunta de nuevo
                # Un evento es su fecha mas su CABEZA DE CARTEL, y nada mas.
                # El venue queda fuera porque el OCR lo lee distinto en cada
                # pieza ("ESPACIO RIESCO" y "ESPACIO RIESGO" son el mismo
                # lugar). El resto del line-up tambien queda fuera: del mismo
                # evento el modelo saco ["AMELIE LENS"] de un flyer y
                # ["AMÉLIE LENS", "AURA"] de otro, y comparando la lista entera
                # seguian siendo dos preguntas para el mismo evento.
                clave = "rd|%s|%s" % (_norm(fecha), _norm(heads[0]))
                if clave in vistos:
                    continue
                vistos.add(clave)
                texto = (
                    "En CHILE (Santiago y alrededores), que productora organizo "
                    "el evento del %s con %s en el cartel%s? "
                    "REGLAS: el evento es en Chile, si lo que encontras es de "
                    "otro pais NO sirve. Solo se acepta respuesta con FUENTE "
                    "VERIFICABLE (URL de la productora, del recinto, de venta "
                    "de entradas o de prensa que nombre ese evento en esa "
                    "fecha). Los nombres del cartel son DATO DE ENTRADA, no "
                    "respuesta: repetirlos no identifica a nadie. Si no hay "
                    "fuente, responder exactamente NO SE ENCONTRO."
                    % (fecha, ", ".join(heads[:3]),
                       " en %s" % venue if venue else "")
                )
                depto, modo = "research", "research"

            elif fuente == "ig":
                # Una obra puede proponer las DOS cosas: una pregunta que vale
                # investigar y un procedimiento que vale programar. Antes esto
                # era un elif y la linea de investigacion se perdia cada vez que
                # tambien habia oportunidad de codigo -- probado el 2026-07-26
                # con una ficha que traia ambas y genero una sola tarea.
                propuestas = []
                oport = _txt(v.get("oportunidad_codigo"))
                if oport:
                    propuestas.append((oport, "codex", "generar"))
                linea_inv = _txt(v.get("linea_investigacion"))
                if linea_inv:
                    propuestas.append((linea_inv, "research", "research"))
                if not propuestas:
                    continue
            else:
                continue

            if fuente == "rd":
                propuestas = [(texto, depto, modo)]

            for texto_t, depto_t, modo_t in propuestas:
                h = _hash(texto_t)
                if h in vistos:
                    continue
                vistos.add(h)
                tareas.append({
                    "id": h,
                    "origen": fuente,
                    "ficha": f.get("id"),
                    "archivo": f.get("ruta_rel"),
                    "depto": depto_t,
                    "modo": modo_t,
                    "texto": texto_t,
                    # La variable de arriba se llama `propuestas` desde que se
                    # escribio, y despues se apendeaban como ordenes. Las de
                    # `ig` vuelven a ser lo que su nombre dice.
                    "estado": ESTADO_INICIAL[fuente],
                })
    return tareas


def cargar():
    if not os.path.exists(COLA):
        return []
    filas = []
    with open(COLA, encoding="utf-8", errors="replace") as fh:
        for linea in fh:
            try:
                filas.append(json.loads(linea))
            except Exception:
                continue
    return filas


def guardar(filas):
    with _queue_exclusive():
        _save_unlocked(filas)


def _save_unlocked(records):
    tmp = COLA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    os.replace(tmp, COLA)


def pop_pendiente():
    """Saca la siguiente tarea pendiente y la marca. Devuelve None si no hay.

    Lo usa trabajo.py. Si devuelve None, el organismo cae a su modo autonomo,
    que es exactamente para lo que ese modo existe.

    Lo depositado a mano va PRIMERO (`origen: micelio`). Medido el 2026-08-01:
    la cola tenia 2.733 tareas pendientes cosechadas de las fichas, y una
    semilla depositada ese dia quedaba detras de todas ellas -- a la velocidad
    real del organismo, meses. El formato del sobre estaba bien y el organismo
    tambien; el circuito no cerraba por el ORDEN. Una intencion escrita a mano
    no compite en igualdad con 2.733 tareas que el propio sistema se genero.
    """
    with _queue_exclusive():
        filas = cargar()
        pendientes = [r for r in filas if r.get("estado") == "pendiente"]
        if not pendientes:
            return None
        elegida = next((r for r in pendientes if r.get("origen") == "micelio"),
                       pendientes[0])
        elegida["estado"] = "despachada"
        _save_unlocked(filas)
        return elegida


def enqueue_front(task):
    """Insert one task atomically unless its id is already queued."""
    with _queue_exclusive():
        filas = cargar()
        if any(row.get("id") == task.get("id") for row in filas):
            return False
        _save_unlocked([task] + filas)
        return True


def reorder_by_pattern(pattern):
    """Move matching tasks to the front as one queue transaction."""
    pattern = (pattern or "").strip().lower()
    if not pattern:
        return 0
    with _queue_exclusive():
        filas = cargar()
        matching_tasks = [t for t in filas
                          if pattern in (t.get("texto") or "").lower()]
        if not matching_tasks:
            return 0
        remaining_tasks = [t for t in filas if t not in matching_tasks]
        _save_unlocked(matching_tasks + remaining_tasks)
        return len(matching_tasks)


def reconstruir():
    with _queue_exclusive():
        previas = {r.get("id"): r for r in cargar()}
        nuevas = tareas_desde_fichas()
        salida = []
        for t in nuevas:
            # No revivir lo ya despachado: la cola no se repite sola.
            anterior = previas.get(t["id"])
            salida.append(anterior if anterior else t)
        _save_unlocked(salida)
        pend = sum(1 for r in salida if r.get("estado") == "pendiente")
        return len(salida), pend


def degradar_ocurrencias(aplicar=False):
    """Las tareas de `ig` que ya estan encoladas vuelven a ser propuestas.

    `ESTADO_INICIAL` arregla las que NACEN de ahora en adelante. Las que ya
    estan en la cola siguen `pendiente`, porque `reconstruir()` conserva el
    estado anterior a proposito ("no revivir lo ya despachado"). Sin esta
    migracion el arreglo no toca las 2.696 que ya existen.

    Lo DESPACHADO no se toca: ya se trabajo, y volverlo atras seria reescribir
    lo que paso. Solo cambia lo que todavia no salio.
    """
    with _queue_exclusive():
        filas = cargar()
        afectadas = [r for r in filas
                     if r.get("origen") == "ig" and r.get("estado") == "pendiente"]
        if aplicar:
            for r in afectadas:
                r["estado"] = "propuesta"
            if afectadas:
                _save_unlocked(filas)
        return len(afectadas), len(filas)


def main():
    if active_enabled() and dispatch_sync is not None:
        payload = {"argv": sys.argv[1:], "bucket": int(time.time() // 3600)}

        def handle(_job):
            result = _main_unlocked()
            return {"validated": True, "result": result,
                    "artifacts": [{
                        "kind": "material_queue_manifest",
                        "content": json.dumps(payload, sort_keys=True),
                        "staging_path": COLA,
                    }]}

        return dispatch_sync(
            "material_rebuild", payload, producer="platform.material.main",
            handler=handle, template_version="material-rebuild-v1",
        )
    return _main_unlocked()


def _main_unlocked():
    if "--degradar-ocurrencias" in sys.argv:
        aplicar = "--aplicar" in sys.argv
        n, total = degradar_ocurrencias(aplicar)
        print("  cola: %d filas | de `ig` pendientes: %d" % (total, n))
        if aplicar:
            print("  pasadas a `propuesta`: %d" % n)
            print("  quedan como tarea solo las que nacieron de una pregunta")
        else:
            print("  (ensayo: no se escribio nada. Para aplicar: --aplicar)")
        return
    if "--contar" in sys.argv:
        filas = cargar()
        pend = sum(1 for r in filas if r.get("estado") == "pendiente")
        print("  tareas en cola: %d | pendientes: %d" % (len(filas), pend))
        return
    total, pend = reconstruir()
    por_depto = {}
    for r in cargar():
        if r.get("estado") == "pendiente":
            por_depto[r.get("depto")] = por_depto.get(r.get("depto"), 0) + 1
    print("  tareas totales   :", total)
    print("  pendientes       :", pend)
    print("  por departamento :", por_depto or "{}")
    print("  cola             :", COLA)


if __name__ == "__main__":
    main()
