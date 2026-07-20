#!/usr/bin/env python3
"""research_lib -- nucleo compartido del nucleo research MAK (sin n8n).

Proveedores LLM gratis con fallback (groq -> cerebras -> azure -> ollama),
busqueda Tavily, fetch de paginas y utilidades comunes que usan
research.py / panel.py / cola.py. Stdlib-only (urllib), Python 3.11.

Keys: ~/n8n-local/research.env (chmod 600) o el archivo que diga
la variable de entorno RESEARCH_ENV. NUNCA hardcodear keys aca.
"""
import json
import os
import re
import socket
import time
import unicodedata
import urllib.error
import urllib.request
import urllib.parse

try:
    from fallback_util import score_provider_health, parse_provider_error
except ImportError:
    score_provider_health = None
    parse_provider_error = None

ENV_FILE = os.environ.get(
    "RESEARCH_ENV", os.path.expanduser("~/n8n-local/research.env")
)

DEFAULTS = {
    "GROQ_MODEL": "llama-3.3-70b-versatile",
    "CEREBRAS_MODEL": "gpt-oss-120b",
    "AZURE_ENDPOINT": "https://ligereza.services.ai.azure.com",
    "AZURE_DEPLOYMENT": "gpt-5-mini",
    "OLLAMA_BASE_URL": "http://127.0.0.1:11434",
    "OLLAMA_MODEL": "gemma3:4b",
    # WIN: notebook Windows con RTX 4070 (8GB VRAM), alcanzable SOLO por el
    # cable ethernet directo (192.168.50.x). Motor local mas fuerte que el
    # de MAK; se prueba antes que el gemma3:4b local como ultimo recurso.
    "WIN_BASE_URL": "http://192.168.50.1:11434",
    "WIN_MODEL": "llama3.1:8b",
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


# Modelo "capaz": el mas fuerte razonando/correlacionando. gpt-5-mini
# (azure) por defecto; se usa para correlacion semantica y auto-reparacion.
MODELO_CAPAZ = "azure"

# Salud de proveedores: registro persistente de exitos/fallos por proveedor
# en una ventana de tiempo, para no reintentar de entrada un proveedor que
# viene fallando (ej. Groq free-tier en 429). Ver orden_por_salud().
SALUD_RUTA = os.path.join(os.path.expanduser("~"), "research", "salud_proveedores.json")
SALUD_VENTANA = 6 * 3600

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
    """Registra un resultado (exito/fallo) de `proveedor` en el archivo de
    salud, con lectura-modificacion-escritura. Si la ventana vencio o el
    archivo esta invalido, arranca de cero. Best-effort: sin lock de
    archivo, incrementos perdidos en carrera concurrente son aceptables.
    Nunca lanza."""
    ruta = ruta or SALUD_RUTA
    ahora = ahora if ahora is not None else time.time()
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
        proveedor, {"successes": 0, "timeouts": 0, "api_errors": 0, "errors": 0})
    if exito:
        clave = "successes"
    elif tipo == "timeout":
        clave = "timeouts"
    elif tipo == "api_error":
        clave = "api_errors"
    else:
        clave = "errors"
    contadores[clave] = contadores.get(clave, 0) + 1
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(data, f)
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
# (azure) solo donde razonar importa (sintesis, juez, plan, diagnostico); las
# tareas cortas ('barato': resumen, status, clasificacion) van local primero
# para ahorrar cupo. red_ok() ya mete ollama al frente si no hay internet.
_SLOTS = {
    "razonar": "azure,cerebras,groq,ollama",
    "bulk": "cerebras,groq,azure,ollama",
    "barato": "ollama,cerebras,groq",
}


def orden_rol(rol):
    """Lista de proveedores para un ROL, o None (usa el default de LLM)."""
    s = _SLOTS.get(rol)
    return [p.strip() for p in s.split(",")] if s else None


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
# modelos locales chicos (llama3.1:8b via win) leen "nada de sintesis
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


class LLM:
    """Cadena de proveedores con fallback y stats (mismo diseno que el
    Code node probado 2026-07-15: cerebras/azure son razonadores, llevan
    margen extra de max_completion_tokens; azure NO acepta temperature)."""

    def __init__(self, order="groq,cerebras,azure,win,ollama"):
        load_env()
        self.stats = {}
        self.errors = []
        self.order = [p.strip() for p in order.split(",")
                      if p.strip() in ("groq", "cerebras", "azure", "win", "ollama")]

    # -- proveedores ----------------------------------------------------
    def _groq(self, system, user, max_tok):
        r = _http_json(
            "https://api.groq.com/openai/v1/chat/completions",
            {"model": os.environ["GROQ_MODEL"],
             "messages": _msgs(system, user),
             "temperature": 0.3, "max_tokens": max_tok},
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
        return self._ollama_like(os.environ["OLLAMA_BASE_URL"],
                                 os.environ["OLLAMA_MODEL"], system, user, max_tok)

    def _win(self, system, user, max_tok):
        """WIN: la RTX 4070 del notebook, alcanzable solo por el cable directo.
        Mismo protocolo que ollama local; timeout corto en la conexion (si WIN
        esta apagada/dormida, cae rapido al fallback siguiente)."""
        return self._ollama_like(os.environ["WIN_BASE_URL"],
                                 os.environ["WIN_MODEL"], system, user, max_tok)

    def _has_key(self, name):
        need = {"groq": "GROQ_API_KEY", "cerebras": "CEREBRAS_API_KEY",
                "azure": "AZURE_API_KEY", "win": "WIN_BASE_URL",
                "ollama": "OLLAMA_BASE_URL"}
        return bool(os.environ.get(need[name]))

    def call(self, system, user, max_tok=1024, order=None):
        """Devuelve (texto, proveedor). Recorre la cadena hasta respuesta
        no vacia; acumula errores no fatales en self.errors."""
        fns = {"groq": self._groq, "cerebras": self._cerebras,
               "azure": self._azure, "win": self._win, "ollama": self._ollama}
        orden = list(order or self.order)
        # sin internet: win/ollama primero (LAN directa, no depende de internet;
        # no esperar los timeouts de la nube). WIN (RTX 4070) antes que el
        # gemma3 local de MAK -- mas fuerte, mismo cable.
        if not red_ok():
            frente = [p for p in ("win", "ollama") if p in orden]
            orden = frente + [x for x in orden if x not in frente]
        try:
            orden = orden_por_salud(orden, _salud_cargar())
        except Exception:
            pass
        last = None
        for name in orden:
            if name not in fns or not self._has_key(name):
                continue
            try:
                text = fns[name](system, user, max_tok)
                if text:
                    self.stats[name] = self.stats.get(name, 0) + 1
                    try:
                        _salud_registrar(name, True)
                    except Exception:
                        pass
                    return text, name
                last = name + " devolvio vacio"
                try:
                    _salud_registrar(name, False, "empty")
                except Exception:
                    pass
            except Exception as e:  # noqa: BLE001 - fallback multi-proveedor
                last = name + ": " + _err_str(e)
                self.errors.append(last)
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


def tavily_search(query, depth="basic", max_results=5, errors=None):
    """basic = 1 credito, advanced = 2. 1000/mes gratis."""
    load_env()
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
    url = base + "/search?q=" + urllib.parse.quote(query) + "&format=json&safesearch=0"
    try:
        data = _http_json(url, timeout=30)
        resultados = [
            {"url": r.get("url"), "title": r.get("title"),
             "content": r.get("content")}
            for r in (data.get("results") or [])[:max_results]
        ]
        _salud_registrar("searxng", True, tipo="search")
        return {"results": resultados, "answer": data.get("answer")}
    except Exception as e:  # noqa: BLE001 - busqueda fallida no mata el loop
        if errors is not None:
            errors.append("searxng: " + _err_str(e))
        _salud_registrar("searxng", False,
                         "timeout" if isinstance(e, socket.timeout) else "api_error")
        return {"results": [], "answer": None}


def web_search(query, depth="basic", max_results=5, errors=None):
    """Busqueda unificada: SearXNG propio primero (sin tope de creditos);
    Tavily como fallback solo si SearXNG no devuelve resultados. Mismo
    shape que tavily_search. Ambas rutas registran salud (ver panel hub)."""
    res = searxng_search(query, max_results=max_results, errors=errors)
    if res.get("results"):
        return res
    return tavily_search(query, depth=depth, max_results=max_results,
                         errors=errors)

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
        with open(ruta, "a", encoding="utf-8") as f:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")
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


def marco(topic, activo=True):
    if not activo:
        return topic
    frame = MARCO_CULTURA if _es_tema_sustancia(topic) else MARCO_CULTURA_NEUTRO
    return frame + topic
