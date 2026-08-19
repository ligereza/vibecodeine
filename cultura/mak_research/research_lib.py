#!/usr/bin/env python3
"""research_lib -- nucleo compartido del nucleo research MAK (sin n8n).

Proveedores LLM gratis/locales con fallback (cerebras -> groq -> ollama),
busqueda Tavily, fetch de paginas y utilidades comunes que usan
research.py / panel.py / cola.py. Stdlib-only (urllib), Python 3.11.

Keys: ~/research/research.env (chmod 600) o el archivo que diga
la variable de entorno RESEARCH_ENV. NUNCA hardcodear keys aca.
"""
import hashlib
import json
import os
import re
import socket
import sys
import tempfile
import threading
import time
from contextlib import contextmanager, nullcontext
import unicodedata
import urllib.error
import urllib.request
import urllib.parse

try:
    from fallback_util import score_provider_health, parse_provider_error
except ImportError:
    score_provider_health = None
    parse_provider_error = None

try:
    from cultura.mak_conductor.runtime import (external_budget_limit,
                                                reserve_external_call,
                                                shared_gpu_lease,
                                                dispatch_sync, active_enabled,
                                                enqueue_shadow, observe_shadow)
    _CONDUCTOR_RUNTIME_AVAILABLE = True
except ImportError:  # mirrored MAK runtime imports from the repo's cultura dir
    sys.path.insert(0, os.environ.get("MAK_CONDUCTOR_PATH",
                                     "/home/mak/flujo/cultura"))
    try:
        from mak_conductor.runtime import (external_budget_limit,
                                           reserve_external_call,
                                           shared_gpu_lease,
                                           dispatch_sync, active_enabled,
                                           enqueue_shadow, observe_shadow)
        _CONDUCTOR_RUNTIME_AVAILABLE = True
    except ImportError:  # standalone legacy research checkout
        _CONDUCTOR_RUNTIME_AVAILABLE = False
        external_budget_limit = None
        reserve_external_call = None
        from contextlib import nullcontext
        def shared_gpu_lease(**_kwargs):
            return nullcontext()
        dispatch_sync = None
        enqueue_shadow = observe_shadow = None
        def active_enabled():
            return False

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows director has no fcntl
    fcntl = None

ENV_FILE = os.environ.get(
    "RESEARCH_ENV", os.path.expanduser("~/research/research.env")
)

DEFAULTS = {
    "GROQ_MODEL": "openai/gpt-oss-20b",
    "CEREBRAS_MODEL": "gpt-oss-120b",
    "AZURE_ENDPOINT": "https://ligereza.services.ai.azure.com",
    "AZURE_DEPLOYMENT": "gpt-5-mini",
    "RESEARCH_AZURE_ENABLED": "0",
    "OLLAMA_BASE_URL": "http://127.0.0.1:11434",
    "OLLAMA_MODEL": "gemma3:4b",
    # SearXNG propio (LAN, Docker): busqueda sin API key ni tope de
    # creditos. Reemplaza/complementa Tavily. Ver PLAN.md seccion 2.
    "SEARXNG_BASE_URL": "http://127.0.0.1:8888",
}

# Densidad del trabajo: escala max_tok por llamada. Tope duro para no
# pasar el timeout del worker (1800s) ni los limites de free-tier.
DENSIDAD_TOK = {"corto": 0.6, "medio": 1.0, "largo": 1.8}
TOPE_TOK = 4000


def escala_tok(base, densidad="medio"):
    return min(int(base * DENSIDAD_TOK.get(densidad, 1.0)), TOPE_TOK)


# Modelo capaz gratuito: Cerebras gpt-oss-120b. Azure/gpt-5-mini queda fuera
# de MAK mientras el usuario trabaja con ese cupo en la sesion principal.
MODELO_CAPAZ = "cerebras"

# Salud de proveedores: registro persistente de exitos/fallos por proveedor
# en una ventana de tiempo, para no reintentar de entrada un proveedor que
# viene fallando (ej. Groq free-tier en 429). Ver orden_por_salud().
SALUD_RUTA = os.path.join(os.path.expanduser("~"), "research", "salud_proveedores.json")
SALUD_VENTANA = 6 * 3600
_SALUD_LOCK = threading.RLock()
_EVENT_LOCK = threading.RLock()


def ollama_gpu_slot(model, *, caller, queue, department, trigger="manual",
                    job_id=""):
    """Return the shared MAK GPU slot for local Ollama calls.

    Cloud providers do not use MAK's local GPU and therefore must not consume
    this slot. The import stays lazy for standalone research utilities.
    """
    if not str(model or "") or _CONDUCTOR_RUNTIME_AVAILABLE:
        return nullcontext()
    try:
        base = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        if not (base.startswith("http://127.0.0.1") or
                base.startswith("http://localhost")):
            return nullcontext()
        platform = os.path.expanduser("~/plataforma")
        if platform not in sys.path:
            sys.path.insert(0, platform)
        from gpu_guard import slot
        return slot(caller=caller, queue=queue, model=model,
                    department=department, trigger=trigger, job_id=job_id,
                    resource="ollama")
    except (ImportError, OSError, TypeError):
        return nullcontext()


def _record_activity(kind, status, *, caller, queue, department, trigger,
                     job_id, provider="", model="", resource="", error="",
                     extra=None):
    """Best-effort activity event; provider failure must remain visible."""
    try:
        platform = os.path.expanduser("~/plataforma")
        if platform not in sys.path:
            sys.path.insert(0, platform)
        from actividad import record
        return record(kind, status, caller=caller, queue=queue,
                      department=department, trigger=trigger, job_id=job_id,
                      provider=provider, model=model, resource=resource,
                      error=error, extra=extra)
    except (ImportError, OSError, TypeError):
        return ""


@contextmanager
def _exclusive_salud_lock(path):
    """Protect provider-health read-modify-write across processes and threads."""
    with _SALUD_LOCK:
        lock_path = os.path.abspath(path) + ".lock"
        parent = os.path.dirname(lock_path)
        os.makedirs(parent, exist_ok=True)
        fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)


@contextmanager
def _exclusive_event_lock(path):
    """Serialize event appends across independent workers."""
    with _EVENT_LOCK:
        lock_path = os.path.abspath(path) + ".lock"
        parent = os.path.dirname(lock_path)
        os.makedirs(parent, exist_ok=True)
        fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

# Deteccion de internet: rapida y cacheada. Sin red, los departamentos siguen
# con ollama local en vez de esperar el timeout de cada nube. Al volver la red
# (ttl 60s) la nube vuelve a ir primera -> la tarea "vuelve al resto".
_RED = {"t": 0.0, "ok": True}


def red_ok(ttl=60):
    now = time.time()
    if now - _RED["t"] < ttl:
        return _RED["ok"]
    ok = False
    for host, port in (("1.1.1.1", 443), ("8.8.8.8", 53)):
        try:
            s = socket.create_connection((host, port), timeout=2.5)
            s.close()
            ok = True
            break
        except OSError:
            continue
    _RED["t"] = now
    _RED["ok"] = ok
    return ok


def _salud_cargar(ruta=None, ahora=None):
    """Lee el registro de salud de proveedores. Devuelve el dict
    proveedores (nombre -> {successes, timeouts, api_errors, errors}).
    Devuelve {} si el archivo no existe, esta corrupto, tiene forma
    invalida o la ventana (SALUD_VENTANA) ya vencio. Nunca lanza."""
    ruta = ruta or SALUD_RUTA
    try:
        with open(ruta, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    desde = data.get("desde")
    proveedores = data.get("proveedores")
    if not isinstance(desde, (int, float)) or not isinstance(proveedores, dict):
        return {}
    ahora = ahora if ahora is not None else time.time()
    if ahora - desde > SALUD_VENTANA:
        return {}
    return proveedores


def _salud_registrar(proveedor, exito, tipo="other", ruta=None, ahora=None):
    """Record provider health with a locked atomic read-modify-write cycle.

    Invalid or expired state starts a new window. The function is best effort
    and never raises to its caller.
    """
    ruta = ruta or SALUD_RUTA
    ahora = ahora if ahora is not None else time.time()
    try:
        with _exclusive_salud_lock(ruta):
            data = None
            try:
                with open(ruta, encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, ValueError):
                data = None
            if (not isinstance(data, dict)
                    or not isinstance(data.get("desde"), (int, float))
                    or not isinstance(data.get("proveedores"), dict)
                    or ahora - data["desde"] > SALUD_VENTANA):
                data = {"desde": ahora, "proveedores": {}}
            proveedores = data["proveedores"]
            contadores = proveedores.setdefault(
                proveedor,
                {"successes": 0, "timeouts": 0,
                 "api_errors": 0, "errors": 0})
            if exito:
                clave = "successes"
            elif tipo == "timeout":
                clave = "timeouts"
            elif tipo == "api_error":
                clave = "api_errors"
            else:
                clave = "errors"
            contadores[clave] = contadores.get(clave, 0) + 1
            parent = os.path.dirname(os.path.abspath(ruta))
            os.makedirs(parent, exist_ok=True)
            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(
                        "w", encoding="utf-8", dir=parent,
                        prefix=".salud-", suffix=".tmp", delete=False) as f:
                    temp_path = f.name
                    json.dump(data, f)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(temp_path, ruta)
                temp_path = None
            finally:
                if temp_path:
                    try:
                        os.unlink(temp_path)
                    except OSError:
                        pass
    except (OSError, ValueError):
        pass


def orden_por_salud(orden, stats):
    """Reordena `orden` (lista de nombres de proveedor) segun `stats` de
    salud (ver _salud_cargar()). PURA: sin I/O. Un proveedor se DEGRADA
    (va al final, tras los demas) si tiene >=3 intentos acumulados en
    stats Y su score_provider_health() es estrictamente menor a 0.5.
    Proveedores ausentes de stats nunca se degradan. Preserva el orden
    relativo dentro de cada grupo (no-degradados primero, degradados
    despues)."""
    if not stats or score_provider_health is None:
        return list(orden)
    scores = dict(score_provider_health(stats))
    degradados = []
    resto = []
    for p in orden:
        contadores = stats.get(p)
        intentos = sum(contadores.values()) if isinstance(contadores, dict) else 0
        if intentos >= 3 and scores.get(p, 1.0) < 0.5:
            degradados.append(p)
        else:
            resto.append(p)
    return resto + degradados


# Slots de modelo por ROL (throughput-first). El grueso a los rapidos; el capaz
# (cerebras) donde razonar importa (sintesis, juez, plan, diagnostico); las
# tareas cortas ('barato': resumen, status, clasificacion) van local primero
# para ahorrar cupo. red_ok() ya mete ollama al frente si no hay internet.
# ORDEN POR EFECTIVIDAD MEDIDA (2026-07-26, ver salud_proveedores.json).
# Antes groq iba PRIMERO aqui y en el orden por defecto, con 40% de exito
# medido (2 exitos / 3 api_errors), mientras cerebras -- 91.4% (74/7) -- iba
# segundo o tercero. El propio organismo escribio el informe pidiendo
# "mitigar la degradacion de groq" y nadie lo ejecuto; esto lo ejecuta.
# groq no se elimina: baja a ultimo recurso remoto. Si mejora, vuelve a subir
# por el mismo criterio: medicion, no costumbre.
# 2026-07-30: `watsonx` encabeza `razonar` por la misma regla -- 32/32 llamadas
# exitosas medidas ese dia (ver LLM.__init__). `bulk` y `barato` NO cambian:
# barato existe para ahorrar cupo con el modelo local, y meter ahi un proveedor
# de credito con fecha de vencimiento seria gastarlo en resumenes y clasificacion
# en vez de en la base cientifica. Retiro: el del credito IBM (2026-08-18).
# Nota honesta para quien venga: `orden_rol`/`_SLOTS` HOY no tienen llamador en
# el repo (research.py toma su cadena de `--providers`, y el resto usa `LLM()`
# directo). Cambiar esta tabla declara la intencion; lo que de verdad rutea es el
# `order` por defecto de LLM y el default de research.py.
_SLOTS = {
    "razonar": "watsonx,cerebras,groq,ollama",
    "bulk": "cerebras,groq,ollama",
    "barato": "ollama,cerebras,groq",
}


# ---------------------------------------------------------------------------
# Orden derivado de la salud medida
# ---------------------------------------------------------------------------

# Minimo de llamadas para que un porcentaje signifique algo. Con menos, el
# proveedor conserva la posicion que le dio la lista escrita: ante la duda se
# respeta la decision humana, no el ruido estadistico.
MIN_MUESTRA = 8


def salud_medida():
    """{proveedor: (exitos, total)} desde salud_proveedores.json. {} si no hay."""
    try:
        with open(SALUD_RUTA, encoding="utf-8") as f:
            datos = json.load(f)
        salida = {}
        for nombre, v in (datos.get("proveedores") or {}).items():
            exitos = int(v.get("successes") or 0)
            total = exitos + int(v.get("timeouts") or 0) \
                + int(v.get("api_errors") or 0) + int(v.get("errors") or 0)
            salida[nombre] = (exitos, total)
        return salida
    except Exception:
        return {}


def ordenar_por_salud(orden):
    """Reordena `orden` (lista de proveedores) por efectividad medida.

    Los de muestra insuficiente quedan donde estaban. Nunca se elimina ninguno:
    un proveedor degradado baja, no desaparece, y vuelve a subir solo cuando
    su medicion mejora.
    """
    salud = salud_medida()
    if not salud:
        return list(orden)

    con_datos = []
    for i, p in enumerate(orden):
        exitos, total = salud.get(p, (0, 0))
        if total >= MIN_MUESTRA:
            con_datos.append((i, p, exitos / total))

    if len(con_datos) < 2:
        return list(orden)   # nada que reordenar con fundamento

    posiciones = sorted(i for i, _, _ in con_datos)
    por_calidad = [p for _, p, _ in sorted(con_datos, key=lambda x: -x[2])]

    salida = list(orden)
    for pos, proveedor in zip(posiciones, por_calidad):
        salida[pos] = proveedor
    return salida


def orden_rol(rol):
    """Lista de proveedores para un ROL, o None (usa el default de LLM)."""
    s = _SLOTS.get(rol)
    if not s:
        return None
    # La lista escrita fija QUIENES participan; la salud medida decide en que
    # orden. Asi una degradacion se corrige sola en vez de esperar a que alguien
    # lea el informe que la caja ya escribio.
    return ordenar_por_salud([p.strip() for p in s.split(",")])


def correlacionar(llm, tema, piezas, densidad="medio"):
    """Departamento de research: un modelo capaz LEE las intervenciones de
    todos los modelos y produce un ordenamiento semantico + correlacion
    tematica (que ideas se refuerzan, cuales chocan, que hilo comun emerge).
    `piezas` = lista de {modelo, texto}. Devuelve (texto_correlacion, real).
    No inventa: solo ordena y relaciona lo que los modelos ya dijeron."""
    cuerpo = "\n\n".join(
        "[%s]: %s" % (p.get("modelo", "?"), (p.get("texto") or "")[:2000])
        for p in piezas if p.get("texto"))
    if not cuerpo.strip():
        return "", None
    orden = [MODELO_CAPAZ] + [x for x in llm.order if x != MODELO_CAPAZ]
    return llm.call(
        "Eres el coordinador de un departamento de investigacion cultural. "
        "NO aportas contenido nuevo: tu trabajo es CORRELACIONAR lo que ya "
        "dijeron los investigadores. Espanol correcto con tildes, Markdown.",
        'TEMA: "%s"\n\nINTERVENCIONES DE LOS INVESTIGADORES:\n%s\n\n'
        "Produce una CORRELACION con: 1. HILO COMUN (que idea central "
        "comparten), 2. CONVERGENCIAS (donde se refuerzan, cita por "
        "modelo), 3. TENSIONES (donde se contradicen o compiten), "
        "4. VACIOS (que angulo nadie cubrio), 5. MAPA ORDENADO (los "
        "hallazgos jerarquizados de mas a menos solido segun la evidencia "
        "citada)." % (tema, cuerpo),
        escala_tok(1200, densidad), order=orden)


def diagnosticar_error(llm, contexto, error, densidad="medio"):
    """Auto-reparacion: el modelo capaz LEE el error real de un job fallido
    y devuelve diagnostico + causa probable + fix concreto. Devuelve
    (texto, real). Capa de sugerencia: no ejecuta nada por si mismo."""
    orden = [MODELO_CAPAZ] + [x for x in llm.order if x != MODELO_CAPAZ]
    return llm.call(
        "Eres un ingeniero senior depurando un sistema de research "
        "multi-modelo en Python (research.py/panel.py/cadena.py/refutar.py "
        "sobre APIs Groq/Cerebras/Azure/Ollama + Tavily). Respondes conciso "
        "y accionable, en espanol, formato Markdown.",
        "CONTEXTO DEL JOB:\n%s\n\nERROR / SALIDA REAL:\n%s\n\n"
        "Diagnostica: 1. QUE FALLO (una linea), 2. CAUSA PROBABLE, "
        "3. FIX CONCRETO (comando o cambio exacto), 4. COMO EVITARLO. "
        "Si el error es un limite/rate de API o timeout, dilo claro."
        % (contexto[:1500], (error or "(sin detalle)")[:2500]),
        escala_tok(900, densidad), order=orden)

# Marco editorial cultura (flujo): capa descriptiva si, nada operativo,
# jamas perfilar personas reales. Viaja con toda pieza derivada.
MARCO_CULTURA = (
    "Investigacion cultural DESCRIPTIVA (historia, estetica, derecho, "
    "contexto social; nada operativo, nada de sintesis quimica ni cultivo, "
    "no perfilar personas reales): "
)
# Marco neutro: mismo nucleo (descriptivo, no perfilar personas reales) SIN
# las frases de negacion especificas de sustancias. Bug probado en vivo:
# modelos locales chicos leen "nada de sintesis
# quimica ni cultivo" en CUALQUIER tema y patron-matchean hacia el rechazo,
# incluso en ingenieria benigna sin relacion con sustancias.
MARCO_CULTURA_NEUTRO = (
    "Investigacion cultural DESCRIPTIVA (historia, estetica, derecho, "
    "contexto social; nada operativo, no perfilar personas reales): "
)
# lista conservadora: ante la duda de si el tema toca sustancias, se
# prefiere el marco completo (mas proteccion), no el neutro.
_TERMINOS_SUSTANCIA = (
    "droga", "drogas", "sustancia", "sustancias", "narcotico", "narcotica",
    "narcoticos", "narcoticas", "estupefaciente", "estupefacientes",
    "cannabis", "marihuana", "marijuana", "cocaina", "cocaína", "heroina",
    "heroína", "opio", "opioide", "opioides", "fentanilo", "metanfetamina",
    "anfetamina", "anfetaminas", "lsd", "mdma", "extasis", "éxtasis",
    "psicodelico", "psicodélico", "psicodelica", "psicoactiv", "alcaloide",
    "cultivo", "sintesis quimica", "síntesis química", "precursor quimico",
    "precursor químico", "reactivo", "narco", "hongo", "hongos", "ketamina",
    "peyote", "ayahuasca", "dmt",
)


def _es_tema_sustancia(topic):
    """True si el tema toca sustancias/farmacos (lista conservadora, no
    exhaustiva a proposito: ante la duda gana el marco completo)."""
    t = (topic or "").lower()
    return any(term in t for term in _TERMINOS_SUSTANCIA)


def load_env(path=ENV_FILE):
    """Carga KEY=VALOR del env file al entorno (sin pisar lo ya seteado)."""
    env = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k] = v
    except OSError:
        pass
    for k, v in env.items():
        os.environ.setdefault(k, v)
    for k, v in DEFAULTS.items():
        os.environ.setdefault(k, v)
    return env


# ------------------------------------------------------------------ watsonx
# El token IAM de IBM vence a la hora, asi que se cambia la API key por un
# bearer y se cachea. Sin cache, cada llamada pagaria 460 ms de ida y vuelta a
# iam.cloud.ibm.com antes de empezar a trabajar.
_WX_TOK = {"t": None, "exp": 0.0}


def _wx_token():
    if _WX_TOK["t"] and time.time() < _WX_TOK["exp"] - 60:
        return _WX_TOK["t"]
    cuerpo = urllib.parse.urlencode({
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": os.environ.get("WATSONX_API_KEY", ""),
    }).encode()
    req = urllib.request.Request(
        "https://iam.cloud.ibm.com/identity/token", data=cuerpo,
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "Accept": "application/json",
                 "User-Agent": "flujo-mak-research/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode("utf-8", "replace"))
    _WX_TOK["t"] = d["access_token"]
    _WX_TOK["exp"] = time.time() + float(d.get("expires_in", 3600))
    return _WX_TOK["t"]


def _http_json(url, body=None, headers=None, timeout=60, method=None):
    data = json.dumps(body).encode() if body is not None else None
    # UA custom: Cloudflare devuelve 403 codigo 1010 al UA default de
    # urllib (visto en groq/cerebras 2026-07-15)
    hdrs = {"Content-Type": "application/json",
            "User-Agent": "flujo-mak-research/1.0"}
    hdrs.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        # tope de lectura: una respuesta gigante no debe agotar la RAM
        return json.loads(r.read(20_000_000).decode("utf-8", "replace"))


def _err_str(e):
    if isinstance(e, urllib.error.HTTPError):
        try:
            detail = e.read().decode("utf-8", "replace")[:160]
        except Exception:
            detail = ""
        return "HTTP %s %s" % (e.code, detail)
    return str(e)[:160]


def _msgs(system, user):
    if system:
        return [{"role": "system", "content": system},
                {"role": "user", "content": user}]
    return [{"role": "user", "content": user}]


def limpiar_salida(text):
    """Remove hidden reasoning blocks emitted by some hosted models."""
    value = str(text or "")
    if re.search(r"<think>", value, re.I) and not re.search(r"</think>", value, re.I):
        return ""
    return re.sub(r"<think>.*?</think>", "", value,
                  flags=re.IGNORECASE | re.DOTALL).strip()


# The provider roster, in ONE place. It used to be written out by hand in every
# tool that accepted a provider list, and those copies went stale silently:
# refutar.py filtered its --orden against a literal
# ("groq", "cerebras", "azure", "ollama") that predates watsonx, so
# `--orden watsonx` was dropped without a word, the list came out empty, the
# default chain took over and every one of its providers was skipped for having
# no key. The tool died with "Todos los proveedores fallaron. Ultimo: None" --
# a message that names nothing because nothing was ever attempted. Measured
# 2026-07-31 on the box, where `research.env` carries ONLY the WATSONX_* keys:
# that is why the adversarial pass the quality gate depends on had run exactly
# once since 2026-07-16. A roster that can go stale is worse than no roster.
PROVIDER_ENV_KEY = {
    "watsonx": "WATSONX_API_KEY",
    "groq": "GROQ_API_KEY",
    "cerebras": "CEREBRAS_API_KEY",
    "azure": "AZURE_API_KEY",
    "ollama": "OLLAMA_BASE_URL",
}
PROVIDERS = tuple(PROVIDER_ENV_KEY)

# Los que aceptan que se les pida un modelo CONCRETO por llamada. El resto
# ignora el pedido y usa el suyo: pedirle un modelo a quien no puede elegirlo
# no es un error, es que ahi no habia nada que elegir. Sumar uno es agregarlo
# aca y darle el parametro `model` a su metodo.
PROVIDERS_CON_MODELO = ("watsonx",)

# Modelos por PAPEL para el flujo adversarial, de familias distintas.
#
# Medido el 2026-07-31: una corrida de `refutar` reporto `llm={'watsonx': 3}`
# -- el mismo modelo hizo de proponente, de refutador y de juez. Eso no es un
# debate, es un monologo con tres titulos: el refutador discutio matices de su
# propia tesis en vez de si el hecho era cierto, y el juez le dio la razon.
#
# Las tres familias se PROBARON contra la cuenta real el 2026-08-01, no se
# eligieron de una lista: `mistral-large-2512` responde 404 y quedo fuera por
# eso, no por criterio. Las que contestan: mistral-medium, mistral-small,
# llama-3-3-70b, llama-4-maverick, granite-4-h-small, granite-3-8b.
MODELOS_POR_PAPEL = {
    "watsonx": {
        "proponente": "mistralai/mistral-medium-2505",
        "refutador": "meta-llama/llama-3-3-70b-instruct",
        "juez": "ibm/granite-4-h-small",
    },
}


# Marcas de que el modelo entrego la FORMA de un informe en vez de un informe.
# Medido el 2026-08-01 sobre los 102 informes reales de la caja: 36 (35%) traen
# un marcador sin rellenar, casi siempre "**Investigador:** [Tu Nombre]". El
# modelo no fallo en investigar: imito la plantilla de un documento de
# investigacion, con el hueco del autor incluido. Un informe asi se lee como
# terminado y no lo esta, que es el mismo defecto que un 200 con cero
# resultados o un "campos perdidos: 0".
PLANTILLA_SIN_RELLENAR = (
    "[su nombre]", "[tu nombre", "[nombre del", "[nombre de la",
    "[insertar", "[completar", "[a completar", "[pendiente]", "[fecha]",
    "[todo]", "[xxx", "xxxx", "lorem ipsum",
)


def marcadores_de_plantilla(texto):
    """Los marcadores que quedaron sin rellenar. Vacio = ninguno.

    Se compara en minusculas y se devuelve la lista, no un booleano: quien lo
    use tiene que poder DECIR cual encontro. Un rechazo sin motivo manda a
    adivinar, y este repo ya pago eso.
    """
    bajo = (texto or "").lower()
    return [m for m in PLANTILLA_SIN_RELLENAR if m in bajo]


def modelos_por_papel(proveedor, pedidos=None):
    """Que modelo le toca a cada papel. Lo pedido a mano gana siempre.

    Devuelve {} para un proveedor que no elige modelo: ahi no hay nada que
    repartir, y rellenarlo con nombres que ese proveedor ignora seria inventar
    una diversidad que no existe.
    """
    base = dict(MODELOS_POR_PAPEL.get(proveedor) or {})
    for papel, valor in (pedidos or {}).items():
        if valor:
            base[papel] = valor
    return base


def _watsonx_llamar(mensajes, model, max_tok, temperatura, timeout):
    """El UNICO lugar que conoce el endpoint de watsonx.

    Existe porque `tests/test_codex_cadena.py` lo exige contando las
    apariciones de la ruta en este archivo, y esa cuenta atrapo el defecto en
    el acto: al escribir `watsonx_vision` quedaron DOS copias de la misma URL.
    Es exactamente lo que costo una tarde en `refutar.py` -- un padron de
    proveedores escrito a mano en dos archivos, uno se quedo viejo en silencio.
    Un guardian sirve cuando acusa a quien lo escribio.

    Lo unico que cambia entre un chat y una lectura de imagen es el CONTENIDO
    de los mensajes; el transporte es el mismo y vive aca una sola vez.
    """
    base = os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    r = _http_json(
        base.rstrip("/") + "/ml/v1/text/chat?version=2024-10-08",
        {"model_id": model,
         "project_id": os.environ.get("WATSONX_PROJECT_ID", ""),
         "messages": mensajes,
         "max_tokens": max_tok,
         "temperature": temperatura},
        {"Authorization": "Bearer " + _wx_token()},
        timeout=timeout,
    )
    return (r["choices"][0]["message"]["content"] or "").strip()


def watsonx_vision(prompt, imagen_b64, model=None, max_tok=700, temperatura=0.1,
                   timeout=240):
    """Una llamada que lleva una IMAGEN. Mismo endpoint, un solo lugar.

    El departamento de percepcion lee el archivo con `gemma3:4b` en una placa
    de 4 GB, y por eso el 76% de las 3.138 fichas no trae texto. Este es el
    transporte que le permite preguntarle a un modelo que ve de verdad.

    Se probo ANTES de escribirlo (`tools/watsonx_vision_smoke.py`, 2026-07-31):
    los tres candidatos de la cuenta aceptaron la imagen y sacaron venue, fecha
    y cuatro headliners de un flyer cuya ficha no tenia nada de eso. La
    capacidad se habia inferido de los NOMBRES -- `task_ids` no declara tarea de
    vision -- asi que primero se midio, la misma regla que dejo a `_watsonx`
    fuera de la cadena hasta que `watsonx_smoke.py` dio 4/4.

    El modelo por defecto lo eligio el BANCO, no su nombre
    (`tools/watsonx_vision_bench.py`, 8 imagenes reales, mitad de las que hoy
    vuelven vacias). El nombre volvio a mentir, igual que esta manana con
    `granite-8b-CODE-instruct`:

        llama-3-2-11b-VISION   solape 0.414   3 inventados   40.175 tok
        mistral-small-3-1-24b  solape 0.807   0 inventados    7.710 tok
        llama-4-maverick-17b   solape 0.807   1 inventado    12.019 tok

    El unico que se llama "vision" recupera la mitad del texto, inventa tres
    veces y cuesta cinco veces mas. Manda mistral-small: mismo solape que el
    mejor y CERO invencion, que en la base de RD es lo que decide -- una
    productora inventada es un cliente equivocado.

    Temperatura baja por lo mismo: un modelo tibio rellena `productora` con algo
    plausible. Un campo vacio es una respuesta correcta; uno inventado no.
    """
    if (reserve_external_call is not None and
            not reserve_external_call(
                "watsonx", limit_count=external_budget_limit("watsonx"))):
        raise RuntimeError("external_budget_exceeded:watsonx")
    return _watsonx_llamar(
        [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url",
             "image_url": {"url": "data:image/jpeg;base64," + imagen_b64}}]}],
        model or os.environ.get("WATSONX_VISION_MODEL",
                                "mistralai/mistral-small-3-1-24b-instruct-2503"),
        max_tok, temperatura, timeout)


def watsonx_chat(system, user, max_tok, model=None, temperatura=0.3):
    """Una llamada de chat a watsonx.ai. Funcion de modulo y no metodo porque
    el departamento codex tambien necesita este proveedor y NO deberia tener
    una segunda copia del endpoint: el mismo `refutar.py` acaba de costar una
    tarde por una lista de proveedores duplicada a mano.

    `temperatura` la elige quien llama: research redacta (0.3) y codex escribe
    codigo, donde una temperatura alta inventa APIs que no existen (0.1).
    """
    return _watsonx_llamar(
        _msgs(system, user),
        model or os.environ.get("WATSONX_MODEL",
                                "meta-llama/llama-3-3-70b-instruct"),
        max_tok, temperatura, 90)


class LLM:
    """Cadena de proveedores con fallback y stats (mismo diseno que el
    Code node probado 2026-07-15: cerebras/azure son razonadores, llevan
    margen extra de max_completion_tokens; azure NO acepta temperature)."""

    # La cadena activa usa solo proveedores disponibles en MAK.
    # `watsonx` ENTRO al orden por defecto y va PRIMERO (2026-07-30). Entro por
    # donde entra todo proveedor nuevo aca: salud medida, no confianza. Lote real
    # de 8 informes cortos con `--providers watsonx` sobre temas cientificos de
    # reduccion de dano, corrido en la caja MAK: 8/8 informes, 32/32 llamadas LLM
    # exitosas, 0 errores, 0 timeouts, 33.7-48.9 s por informe (media 42.1 s,
    # incluye busqueda y fetch). Queda registrado en salud_proveedores.json como
    # watsonx 32 successes / 0 fallos. Va primero porque el credito IBM ($200)
    # VENCE el 2026-08-18: gastarlo en la base cientifica es el uso, y groq
    # (40% medido el 2026-07-26) y cerebras siguen detras como respaldo real.
    # Retiro: cuando el credito se agote o venza -- ahi baja y cerebras vuelve a
    # encabezar --, o si su salud medida cae bajo la de cerebras.
    def __init__(self, order="watsonx,groq,cerebras,azure,ollama"):
        load_env()
        self.stats = {}
        self.errors = []
        # La lista blanca dice QUIENES pueden participar; el `order` de la firma
        # dice en que posicion arrancan y la salud medida decide el resto.
        base = [p.strip() for p in order.split(",")
                if p.strip() in ("groq", "cerebras", "azure", "ollama",
                                 "watsonx")]
        if not self._azure_enabled():
            base = [provider for provider in base if provider != "azure"]
        # Misma regla que orden_rol: la lista escrita dice QUIENES participan,
        # la salud medida decide el orden. Con muestra insuficiente no se toca.
        self.order = ordenar_por_salud(base)

    @staticmethod
    def _azure_enabled():
        """Azure LLM calls require an explicit opt-in to spend credits."""
        return os.environ.get("RESEARCH_AZURE_ENABLED") == "1"

    # -- proveedores ----------------------------------------------------
    def _groq(self, system, user, max_tok):
        payload = {"model": os.environ["GROQ_MODEL"],
                   "messages": _msgs(system, user),
                   "temperature": 0.3}
        # Groq's openai/gpt-oss models spend completion budget on reasoning;
        # max_tokens alone can return an empty visible answer on a long prompt.
        if os.environ["GROQ_MODEL"].startswith("openai/gpt-oss"):
            payload["max_completion_tokens"] = max_tok + 2048
        else:
            payload["max_tokens"] = max_tok
        r = _http_json(
            "https://api.groq.com/openai/v1/chat/completions",
            payload,
            {"Authorization": "Bearer " + os.environ["GROQ_API_KEY"]},
            timeout=60,
        )
        return r["choices"][0]["message"]["content"].strip()

    def _cerebras(self, system, user, max_tok):
        r = _http_json(
            "https://api.cerebras.ai/v1/chat/completions",
            {"model": os.environ["CEREBRAS_MODEL"],
             "messages": _msgs(system, user),
             "max_completion_tokens": max_tok + 2048},
            {"Authorization": "Bearer " + os.environ["CEREBRAS_API_KEY"]},
            timeout=60,
        )
        return r["choices"][0]["message"]["content"].strip()

    def _watsonx(self, system, user, max_tok, model=None):
        """IBM watsonx.ai. Verificado 4/4 por `tools/watsonx_smoke.py` contra la
        cuenta real el 2026-07-30: bearer en 460 ms, 24 modelos visibles, chat
        en 681 ms, 58 tokens = $0.000044.

        Salud medida el 2026-07-30 en la caja MAK con el organo completo (no un
        smoke): 8 informes de research.py, 32/32 llamadas LLM exitosas, 0
        errores. Desde esa medicion encabeza el orden por defecto; ver el
        comentario de LLM.__init__ para la causa y la condicion de retiro.
        """
        return watsonx_chat(system, user, max_tok, model, temperatura=0.3)

    def _azure(self, system, user, max_tok):
        base = os.environ["AZURE_ENDPOINT"].rstrip("/")
        r = _http_json(
            base + "/openai/deployments/" + os.environ["AZURE_DEPLOYMENT"]
            + "/chat/completions?api-version=2024-10-21",
            {"messages": _msgs(system, user),
             "max_completion_tokens": max_tok + 2048},
            {"api-key": os.environ["AZURE_API_KEY"]},
            timeout=90,
        )
        return r["choices"][0]["message"]["content"].strip()

    def _ollama_like(self, base_url, model, system, user, max_tok):
        base = base_url.rstrip("/")
        prompt = (system + "\n\n" + user) if system else user
        local = base.startswith("http://127.0.0.1") or base.startswith(
            "http://localhost")
        context = (ollama_gpu_slot(
            model, caller="mak-research.research_lib", queue="ollama.generate",
            department="research", trigger=os.environ.get("MAK_TRIGGER", "manual"),
            job_id=os.environ.get("MAK_JOB_ID", "")) if local else nullcontext())
        with context:
            r = _http_json(
                base + "/api/generate",
                {"model": model, "prompt": prompt,
                 "stream": False,
                 "options": {"temperature": 0.3, "num_predict": max_tok}},
                timeout=300,
            )
        # no tragar el error: si ollama devuelve {"error": ...} propagarlo
        # para que call() lo registre en self.errors (antes se perdia como "")
        if isinstance(r, dict) and r.get("error"):
            raise RuntimeError("ollama: " + str(r["error"])[:160])
        return (r.get("response") or "").strip()

    def _ollama(self, system, user, max_tok):
        with shared_gpu_lease(job_id="research-ollama-%s" % os.getpid(),
                              estimated_vram_mb=2500):
            return self._ollama_like(os.environ["OLLAMA_BASE_URL"],
                                     os.environ["OLLAMA_MODEL"], system, user,
                                     max_tok)

    def _has_key(self, name):
        return bool(os.environ.get(PROVIDER_ENV_KEY[name]))

    def call(self, system, user, max_tok=1024, order=None, model=None):
        """Devuelve (texto, proveedor). Recorre la cadena hasta respuesta
        no vacia; acumula errores no fatales en self.errors.

        `model` pide un modelo CONCRETO al proveedor que lo soporte (hoy solo
        watsonx, que expone 24). Existe para que un flujo adversarial pueda
        poner modelos DISTINTOS en cada papel: medido el 2026-07-31, un
        proponente y un refutador que son el mismo modelo no son adversarios --
        el refutador discutio matices de la tesis en vez de si el hecho era
        cierto. Se pasa por parametro y no por variable de entorno porque los
        refutadores corren en hilos: un `os.environ` compartido se pisaria.
        """
        # Se deriva del padron: mantener aca una segunda copia de los nombres es
        # como se rompio `refutar.py`. Cada proveedor de `PROVIDERS` tiene su
        # metodo `_<nombre>`, y si falta, falta ruidosamente al llamarlo.
        fns = {name: getattr(self, "_" + name) for name in PROVIDERS}
        orden = list(order or self.order)
        if not self._azure_enabled():
            orden = [provider for provider in orden if provider != "azure"]
        # sin internet: ollama local primero; no esperar timeouts de nubes.
        if not red_ok():
            frente = [p for p in ("ollama",) if p in orden]
            orden = frente + [x for x in orden if x not in frente]
        try:
            orden = orden_por_salud(orden, _salud_cargar())
        except Exception:
            pass
        last = None
        for name in orden:
            if name not in fns or not self._has_key(name):
                continue
            selected_model = model if name in PROVIDERS_CON_MODELO and model else os.environ.get(
                name.upper() + "_MODEL", "")
            _record_activity("model", "started", caller="mak-research.LLM",
                             queue="research.llm", department="research",
                             trigger=os.environ.get("MAK_TRIGGER", "api:research"),
                             job_id=os.environ.get("MAK_JOB_ID", ""),
                             provider=name, model=selected_model,
                             resource="ollama" if name == "ollama" else "cloud")
            try:
                if (name in ("watsonx", "groq", "cerebras", "azure") and
                        reserve_external_call is not None and
                        not active_enabled() and
                        not reserve_external_call(
                            name, limit_count=external_budget_limit(name))):
                        last = name + " presupuesto acotado agotado"
                        self.errors.append(last)
                        continue
                fn = fns[name]
                if dispatch_sync is not None and active_enabled():
                    def handle(job, _fn=fn, _provider=name):
                        if (_provider in ("watsonx", "groq", "cerebras", "azure")
                                and reserve_external_call is not None
                                and not reserve_external_call(
                                    _provider,
                                    limit_count=external_budget_limit(_provider))):
                            raise RuntimeError(
                                "external_budget_exceeded:%s" % _provider)
                        value = (_fn(system, user, max_tok, model)
                                 if model and _provider in PROVIDERS_CON_MODELO
                                 else _fn(system, user, max_tok))
                        return {"validated": bool(str(value or "").strip()),
                                "provider": _provider, "text": value}
                    queued = dispatch_sync(
                        "llm_call", {
                            "provider": name, "model": model or "",
                            "system": str(system), "user": str(user),
                            "prompt_hash": hashlib.sha256(
                                (str(system) + "\n" + str(user)).encode(
                                    "utf-8")).hexdigest(),
                            "prompt_length": len(str(system)) + len(str(user)),
                            "max_tokens": max_tok,
                        }, producer="research.LLM.call", handler=handle,
                        estimated_vram_mb=2500 if name == "ollama" else 0,
                        model=model or name, template_version="llm-call-v1")
                    text = (queued or {}).get("text", "")
                else:
                    shadow_job = (enqueue_shadow(
                        "llm_call", {
                            "provider": name, "model": model or "",
                            "prompt_hash": hashlib.sha256(
                                (str(system) + "\n" + str(user)).encode(
                                    "utf-8")).hexdigest(),
                            "prompt_length": len(str(system)) + len(str(user)),
                            "max_tokens": max_tok,
                        }, producer="research.LLM.call", estimated_vram_mb=(
                            2500 if name == "ollama" else 0),
                        model=model or name, template_version="llm-call-v1")
                        if enqueue_shadow is not None else None)
                    shadow_started = time.time()
                    try:
                        text = (fn(system, user, max_tok, model)
                                if model and name in PROVIDERS_CON_MODELO
                                else fn(system, user, max_tok))
                    except Exception as exc:
                        if observe_shadow is not None:
                            observe_shadow(
                                shadow_job, producer="research.LLM.call",
                                result_status="FAILED",
                                payload={"provider": name,
                                         "error": str(exc)[:2000]},
                                started_at=shadow_started, owner_pid=os.getpid())
                        raise
                    if observe_shadow is not None:
                        observe_shadow(
                            shadow_job, producer="research.LLM.call",
                            result_status="READY" if text else "EMPTY",
                            validated=bool(str(text or "").strip()),
                            payload={"provider": name},
                            started_at=shadow_started, owner_pid=os.getpid())
                text = limpiar_salida(text)
                if text:
                    self.stats[name] = self.stats.get(name, 0) + 1
                    try:
                        _salud_registrar(name, True)
                    except Exception:
                        pass
                    _record_activity("model", "finished", caller="mak-research.LLM",
                                     queue="research.llm", department="research",
                                     trigger=os.environ.get("MAK_TRIGGER", "api:research"),
                                     job_id=os.environ.get("MAK_JOB_ID", ""),
                                     provider=name, model=selected_model,
                                     resource="ollama" if name == "ollama" else "cloud")
                    return text, name
                last = name + " devolvio vacio"
                _record_activity("model", "failed", caller="mak-research.LLM",
                                 queue="research.llm", department="research",
                                 trigger=os.environ.get("MAK_TRIGGER", "api:research"),
                                 job_id=os.environ.get("MAK_JOB_ID", ""),
                                 provider=name, model=selected_model,
                                 resource="ollama" if name == "ollama" else "cloud",
                                 error="empty")
                try:
                    _salud_registrar(name, False, "empty")
                except Exception:
                    pass
            except Exception as e:  # noqa: BLE001 - fallback multi-proveedor
                last = name + ": " + _err_str(e)
                self.errors.append(last)
                _record_activity("model", "failed", caller="mak-research.LLM",
                                 queue="research.llm", department="research",
                                 trigger=os.environ.get("MAK_TRIGGER", "api:research"),
                                 job_id=os.environ.get("MAK_JOB_ID", ""),
                                 provider=name, model=selected_model,
                                 resource="ollama" if name == "ollama" else "cloud",
                                 error=_err_str(e))
                try:
                    tipo = (parse_provider_error(e, name, "?").get("error_type", "other")
                            if parse_provider_error else "other")
                except Exception:
                    tipo = "other"
                try:
                    _salud_registrar(name, False, tipo)
                except Exception:
                    pass
        raise RuntimeError("Todos los proveedores LLM fallaron. Ultimo: %s" % last)


# Tope duro de Tavily, medido contra la API el 2026-08-01: una consulta de mas
# de 400 caracteres responde HTTP 400 "Query is too long" y CERO resultados.
TOPE_CONSULTA = 400


def consulta_de(tema, tope=TOPE_CONSULTA):
    """Lo que se le manda al BUSCADOR, que no es lo que se le manda al modelo.

    Las tareas de triangulacion de RD miden 530 caracteres porque llevan la
    pregunta Y las reglas para el modelo en el mismo texto: "...que productora
    organizo el evento del 21 DE MARZO 2026 con ADRIATIQUE... REGLAS: el evento
    es en Chile, si lo que encontras es de otro pais NO sirve. Solo se acepta
    respuesta con FUENTE VERIFICABLE...". Un buscador hace match de palabras: le
    estabamos mandando instrucciones de comportamiento como si fueran terminos.

    Es el MISMO defecto que `marco_solo()` arreglo el 2026-07-26, cuando 148
    caracteres de encuadre viajaban a Tavily y devolvian el mismo PDF de
    metodologia peruano para cuatro temas distintos. Volvio a entrar por la cola
    de material, escrito a mano en otro archivo.

    Se corta en el primer "REGLAS:" y, si aun no entra, en el ultimo espacio
    antes del tope: partir una palabra por la mitad inventa un termino que nadie
    escribio.
    """
    texto = " ".join(str(tema or "").split())
    corte = texto.upper().find("REGLAS:")
    if corte > 20:
        texto = texto[:corte].strip(" .,;")
    if len(texto) <= tope:
        return texto
    recorte = texto[:tope]
    espacio = recorte.rfind(" ")
    return (recorte[:espacio] if espacio > tope // 2 else recorte).strip()


def _compact_search_query(query):
    stop = {"obtener", "resumenes", "resúmenes", "completos", "datos",
            "clave", "evidencias", "evidencia", "inferencia", "inferencias",
            "asegurando", "separar", "claramente", "analista", "repetir",
            "consulta", "anterior", "incluir", "incluyendo", "sobre", "para",
            "con", "las", "los", "una", "uno", "del", "de", "y", "en"}
    tokens = re.findall(r"[\w]+(?:[.:-][\w]+)*", str(query or ""), re.UNICODE)
    compact = []
    for token in tokens:
        if token.lower() in stop or len(token) < 3:
            continue
        if token not in compact:
            compact.append(token)
    return " ".join(compact[:18])


def firecrawl_search(query, max_results=5, errors=None):
    """Search the public web through Firecrawl when explicitly available."""
    load_env()
    key = os.environ.get("FIRECRAWL_API_KEY")
    if not key:
        return {"results": [], "answer": None, "motor": "firecrawl",
                "ciego": True, "motivo": "sin FIRECRAWL_API_KEY"}
    try:
        queries = [str(query or "").strip()]
        compact = _compact_search_query(query)
        if compact and compact != queries[0]:
            queries.append(compact)
        for used_query in queries:
            data = _http_json(
                "https://api.firecrawl.dev/v2/search",
                {"query": used_query, "limit": max_results},
                {"Authorization": "Bearer " + key}, timeout=60,
            )
            rows = ((data.get("data") or {}).get("web") or [])
            results = [{"url": row.get("url"), "title": row.get("title"),
                        "content": row.get("description") or row.get("snippet")}
                       for row in rows if row.get("url")]
            if results:
                return {"results": results[:max_results], "answer": None,
                        "motor": "firecrawl", "ciego": False,
                        "creditsUsed": data.get("creditsUsed"),
                        "queryUsed": used_query,
                        "queryCompacted": used_query != queries[0]}
        return {"results": [], "answer": None, "motor": "firecrawl",
                "ciego": False, "motivo": "sin resultados"}
    except Exception as e:  # noqa: BLE001 - otro buscador puede continuar
        if errors is not None:
            errors.append("firecrawl: " + _err_str(e))
        return {"results": [], "answer": None, "motor": "firecrawl",
                "ciego": True, "motivo": _err_str(e)}


def tavily_search(query, depth="basic", max_results=5, errors=None):
    """basic = 1 credito, advanced = 2. 1000/mes gratis."""
    load_env()
    if (reserve_external_call is not None and
            not reserve_external_call(
                "tavily", limit_count=external_budget_limit("tavily"))):
        error = "external_budget_exceeded:tavily"
        if errors is not None:
            errors.append(error)
        return {"results": [], "answer": None, "error": error}
    try:
        _r_tavily = _http_json(
            "https://api.tavily.com/search",
            {"query": query, "search_depth": depth,
             "max_results": max_results, "include_answer": True,
             "include_raw_content": False},
            {"Authorization": "Bearer " + os.environ["TAVILY_API_KEY"]},
            timeout=30,
        )
        _salud_registrar("tavily", True, tipo="search")
        _r_tavily["motor"] = "tavily"
        return _r_tavily
    except Exception as e:  # noqa: BLE001 - la busqueda fallida no mata el loop
        if errors is not None:
            errors.append("tavily: " + _err_str(e))
        _salud_registrar("tavily", False,
                         "timeout" if isinstance(e, socket.timeout) else "api_error")
        return {"results": [], "answer": None}



def searxng_search(query, max_results=5, errors=None):
    """Busqueda via SearXNG propio (LAN, Docker, sin API key ni tope de
    creditos). Mismo shape de retorno que tavily_search:
    {"results": [...], "answer": ...}. Registra salud igual que los
    proveedores LLM -> aparece solo en el panel del hub sin tocar hub.py."""
    load_env()
    base = os.environ.get("SEARXNG_BASE_URL", "http://127.0.0.1:8888").rstrip("/")
    # Una pregunta factica se busca en la web, no en bases academicas. Sin
    # esta categoria SearXNG usa las de su instancia y devolvia Google Scholar
    # para "que productora organizo la fiesta" -- comprobado el 2026-07-26: el
    # marco del prompt ya decia "no literatura academica" y el buscador seguia
    # trayendo scholar, porque el marco encuadra al modelo y no al buscador.
    categorias = "&categories=general" if _es_pregunta_factual(query) else ""
    # `SEARXNG_ENGINES` deja apuntar a motores concretos sin tocar la config de
    # la instancia. NO hay lista por defecto a proposito: una lista de motores
    # escrita en el codigo es la misma trampa que este archivo ya pago tres
    # veces -- el dia que bing se tape tambien, quedaria fija y ciega. Vacio =
    # los motores que la instancia tenga configurados.
    # Medido 2026-08-01 sobre la caja, con los cuatro generales caidos:
    #   bing 10 resultados | mojeek 1 | wikipedia y wikidata 0 pero vivos
    #   brave, google, startpage, duckduckgo, qwant, marginalia, stract: CAPTCHA
    #   o "too many requests"
    # O sea que la instancia se puede destapar sin cambiar codigo.
    motores = os.environ.get("SEARXNG_ENGINES", "").strip()
    engines = ("&engines=" + urllib.parse.quote(motores)) if motores else ""
    url = (base + "/search?q=" + urllib.parse.quote(query)
           + "&format=json&safesearch=0" + categorias + engines)
    try:
        data = _http_json(url, timeout=30)
        resultados = [
            {"url": r.get("url"), "title": r.get("title"),
             "content": r.get("content")}
            for r in (data.get("results") or [])[:max_results]
        ]
        if resultados:
            _salud_registrar("searxng", True, tipo="search")
            return {"results": resultados, "answer": data.get("answer"),
                    "ciego": False, "motor": "searxng"}
        # HTTP 200 con CERO resultados son DOS hechos distintos y hasta el
        # 2026-08-01 salian identicos: "busque y no hay nada" y "ningun motor
        # pudo buscar". Medido ese dia en la caja: los cuatro motores generales
        # devolvian `unresponsive_engines` -- brave y google cse suspendidos por
        # demasiadas peticiones, duckduckgo y startpage pidiendo CAPTCHA -- y
        # SearXNG contestaba 200 con `results: []`. Un lector aguas abajo lee
        # eso como "la web no dice nada del tema" y escribe un informe que
        # concluye que no hay fuentes. No es lo mismo no encontrar que no ver.
        mudos = [m for m in (data.get("unresponsive_engines") or [])
                 if isinstance(m, (list, tuple)) and m]
        motivo = "; ".join(
            "%s (%s)" % (m[0], m[1] if len(m) > 1 else "sin detalle")
            for m in mudos)
        _salud_registrar("searxng", False, "ciego" if mudos else "empty")
        if mudos and errors is not None:
            errors.append("searxng ciego: " + motivo)
        return {"results": [], "answer": data.get("answer"),
                "ciego": bool(mudos), "motivo": motivo}
    except Exception as e:  # noqa: BLE001 - busqueda fallida no mata el loop
        if errors is not None:
            errors.append("searxng: " + _err_str(e))
        _salud_registrar("searxng", False,
                         "timeout" if isinstance(e, socket.timeout) else "api_error")
        return {"results": [], "answer": None, "ciego": True,
                "motivo": _err_str(e)}


def web_search(query, depth="basic", max_results=5, errors=None):
    """Busqueda unificada con backend seleccionable y procedencia explicita.

    ``RESEARCH_SEARCH_PROVIDER=firecrawl`` hace que Firecrawl sea el primer
    motor para un trabajo que necesita resultados web relevantes. En modo
    ``auto`` SearXNG sigue siendo primero y Firecrawl queda como fallback;
    Tavily es el ultimo respaldo. Mismo
    shape que tavily_search. Ambas rutas registran salud (ver panel hub).

    Devuelve ademas `ciego`: True cuando NADIE pudo buscar, que es distinto de
    haber buscado y no encontrar. Quien decide si hay fuentes tiene que poder
    distinguirlo -- si no, un buscador tapado produce un informe que concluye
    que el tema no tiene respaldo en la web.
    """
    consulta = consulta_de(query)
    if consulta != " ".join(str(query or "").split()) and errors is not None:
        errors.append("consulta acortada para buscar: %d -> %d caracteres"
                      % (len(str(query or "")), len(consulta)))
    query = consulta
    preferred = os.environ.get("RESEARCH_SEARCH_PROVIDER", "auto").strip().lower()
    if preferred == "firecrawl":
        fire = firecrawl_search(query, max_results=max_results, errors=errors)
        if fire.get("results"):
            return fire

    res = searxng_search(query, max_results=max_results, errors=errors)
    if res.get("results"):
        return res
    fire = firecrawl_search(query, max_results=max_results, errors=errors)
    if fire.get("results"):
        return fire
    if not os.environ.get("TAVILY_API_KEY"):
        # Medido 2026-08-01 en la caja: no hay llave. Sin respaldo, un SearXNG
        # tapado deja la cadena entera sin ojos, y eso se dice.
        motivo = res.get("motivo") or ""
        if res.get("ciego"):
            motivo = (motivo + "; " if motivo else "") + \
                     "sin TAVILY_API_KEY: no hay buscador de respaldo"
            if errors is not None:
                errors.append("web_search: " + motivo)
        fire_motivo = fire.get("motivo") or ""
        if fire_motivo:
            motivo = (motivo + "; " if motivo else "") + fire_motivo
        res["motivo"] = motivo
        return res
    errores_antes = len(errors) if errors is not None else 0
    tav = tavily_search(query, depth=depth, max_results=max_results,
                        errors=errors)
    # Tavily tampoco vio nada: si SearXNG estaba ciego, la busqueda entera lo
    # esta. Un `ciego: False` aca seria afirmar que se busco bien.
    tav.setdefault("ciego", False)
    if not tav.get("results") and res.get("ciego"):
        tav["ciego"] = True
        # LOS DOS MOTIVOS, no el ultimo. La primera version pisaba el motivo
        # con el de SearXNG y tiraba el de Tavily, asi que 19 tareas pausaron
        # con "brave suspendido; duckduckgo CAPTCHA" cuando la causa real era
        # `HTTP 400 Query is too long` -- el error de Tavily. Ni un solo
        # checkpoint lo nombraba; sobrevivio unicamente en el registro de salud
        # (28 api_errors). El instrumento borraba al culpable, que es el mismo
        # defecto que el instrumento existe para no cometer.
        motivos = [res.get("motivo") or ""]
        if errors is not None:
            motivos += [e for e in errors[errores_antes:] if e.startswith("tavily")]
        tav["motivo"] = "; ".join(m for m in motivos if m)
    return tav

_TAG_RE = re.compile(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>|<[^>]+>|&[a-z#0-9]+;", re.I)


def fetch_url(url, limit=4000):
    """Baja una pagina y devuelve texto plano recortado. Vacio si falla."""
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (ResearchBot/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=12) as r:
            raw = r.read(600_000).decode("utf-8", "replace")
        text = _TAG_RE.sub(" ", raw)
        return re.sub(r"\s+", " ", text).strip()[:limit]
    except Exception:  # noqa: BLE001 - pagina caida = contenido vacio
        return ""


def slug(text, n=40):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text[:n] or "tema"


def stamp():
    return time.strftime("%Y%m%d-%H%M%S")


def mint_job_id():
    return "%s-%s" % (stamp(), os.urandom(2).hex())


def emitir_evento(depto, job_id, tipo, **campos):
    """Evento estructurado a ~/<depto>/eventos.jsonl (append-only). Best-effort:
    nunca lanza -- perder un evento no debe tumbar un job. Contrato en
    ~/plataforma/diseno/eventos_y_backlog.md."""
    if not job_id:
        return
    ruta = os.path.join(os.path.expanduser("~"), depto, "eventos.jsonl")
    ev = {"tipo": tipo, "job_id": job_id, "ts": int(time.time())}
    ev.update(campos)
    try:
        with _exclusive_event_lock(ruta):
            os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
            with open(ruta, "a", encoding="utf-8") as f:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
                f.flush()
    except OSError:
        pass


def ntfy_publish(topic, message, title="", priority="default", errors=None):
    """Publica a ntfy.sh. Header Title debe ser ASCII: se pliega."""
    if not topic:
        return False
    try:
        ascii_title = unicodedata.normalize("NFKD", title).encode(
            "ascii", "ignore").decode()[:120]
        req = urllib.request.Request(
            "https://ntfy.sh/" + topic,
            data=message.encode("utf-8"),
            headers={"Title": ascii_title or "MAK",
                     "Priority": priority},
        )
        urllib.request.urlopen(req, timeout=15).read()
        return True
    except Exception as e:  # noqa: BLE001 - notificacion es best-effort
        if errors is not None:
            errors.append("ntfy: " + _err_str(e))
        return False


# Marco FACTICO: para consultas concretas sobre eventos publicos y las
# organizaciones que los producen (la triangulacion de flyers). No es
# investigacion cultural y enmarcar la pregunta como tal hacia que se buscara
# en Dialnet o SciELO quien produjo una fiesta -- comprobado el 2026-07-26.
#
# Conserva y REFUERZA el limite de los otros marcos: no se perfila a personas.
# El sujeto es la organizacion; los nombres del cartel son un dato para
# identificar el evento, no algo sobre lo que investigar.
MARCO_FACTUAL = (
    "Consulta FACTICA sobre un evento publico y la organizacion que lo produjo. "
    "Buscar en fuentes web actuales (sitios de la productora, ticketeras, "
    "prensa, redes del evento), NO en literatura academica. "
    "El sujeto es la EMPRESA U ORGANIZACION productora: los nombres de artistas "
    "solo sirven para identificar de que evento se habla, y no se investiga ni "
    "se perfila a ninguna persona. "
    "Responder SOLO con lo que una fuente confirme, citandola. Si no se "
    "encuentra, decir explicitamente que no se encontro: una respuesta vacia "
    "verificable vale mas que una plausible inventada. "
)

# Senales de que la pregunta es de triangulacion y no de investigacion cultural.
_SENALES_FACTUAL = (
    "que productora organizo",
    "que productora se encargo",
    "que productora produjo",
    "quien organizo",
    "quien fue el organizador",
    "quien es el responsable",
    "responsable de la planificacion",
    "responsable de supervisar",
    "verificar si la productora",
    "seguridad en eventos masivos",
    "seguridad privada en eventos",
    "respuesta en caso de incidentes",
    "coordina la seguridad",
    "coordina la respuesta",
    "autoriza la seguridad",
    "garantizar la seguridad en eventos",
    "recinto donde se realizara el evento",
    "politica de devolucion",
    "proceso de autoatencion",
    "comprar entradas",
    "plataformas de venta de entradas",
    "ticketera",
)


def _fold_for_factual(texto):
    nfkd = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _es_pregunta_factual(topic):
    """Ante la duda, False: se prefiere el marco cultural, que protege mas."""
    t = _fold_for_factual((topic or "").lower())
    return any(s in t for s in _SENALES_FACTUAL)


def marco_solo(topic, activo=True):
    """El encuadre SIN el tema pegado, para ponerlo en el `system` del modelo.

    Existe por un defecto medido el 2026-07-30 sobre la tanda entera de informes
    RD. `marco()` devuelve encuadre+tema, y ese string completo se estaba
    mandando al BUSCADOR: 148 caracteres de "investigacion cultural DESCRIPTIVA
    (historia, estetica, derecho, contexto social...)" antes del tema real.
    Tavily hace match de palabras, asi que las dominantes eran las del encuadre
    y devolvia metodologia de la investigacion: el MISMO PDF de pedagogia
    peruano aparece en cuatro de los cinco informes, sobre cuatro temas que no
    tienen nada que ver entre si, mas una guia para tesistas, una definicion de
    diccionario y dos portadas de Google Scholar listadas como fuentes.

    El encuadre es correcto y protege de verdad -- pero protege en el MODELO,
    que es quien podria escribir una guia de consumo. El buscador solo tiene que
    recibir el tema. La prueba de que el mecanismo funciona cuando el prefijo no
    lo tapa: el informe de factibilidad si encontro uchile.cl, medicina.udd.cl y
    portal.saludarica.cl, fuentes chilenas reales.
    """
    if not activo:
        return ""
    if _es_pregunta_factual(topic) and not _es_tema_sustancia(topic):
        return MARCO_FACTUAL
    return MARCO_CULTURA if _es_tema_sustancia(topic) else MARCO_CULTURA_NEUTRO


def marco(topic, activo=True):
    if not activo:
        return topic
    # Una consulta factica sobre quien produjo un evento no es investigacion
    # cultural: enmarcarla como tal la mandaba a buscar en bases academicas.
    # El limite de no perfilar personas viaja igual en los tres marcos.
    #
    # OJO (2026-07-30): ese arreglo trataba el sintoma en un solo caso, y su
    # condicion `and not _es_tema_sustancia` dejaba fuera justo la clase de
    # pregunta de RD -- la que mas rompia. Hoy la causa esta cortada de raiz:
    # el encuadre ya NO viaja al buscador (ver `marco_solo`), asi que esta
    # eleccion decide unicamente que se le dice al MODELO, y para sustancias el
    # marco cultural es el que corresponde. La exclusion se queda, pero ahora
    # significa otra cosa.
    if _es_pregunta_factual(topic) and not _es_tema_sustancia(topic):
        return MARCO_FACTUAL + topic
    frame = MARCO_CULTURA if _es_tema_sustancia(topic) else MARCO_CULTURA_NEUTRO
    return frame + topic
