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
import time
import unicodedata
import urllib.error
import urllib.request

ENV_FILE = os.environ.get(
    "RESEARCH_ENV", os.path.expanduser("~/n8n-local/research.env")
)

DEFAULTS = {
    "GROQ_MODEL": "llama-3.3-70b-versatile",
    "CEREBRAS_MODEL": "gpt-oss-120b",
    "AZURE_ENDPOINT": "https://ligereza.services.ai.azure.com",
    "AZURE_DEPLOYMENT": "gpt-5-mini",
    "OLLAMA_BASE_URL": "http://127.0.0.1:11434",
    "OLLAMA_MODEL": "aya-expanse:8b",
}

# Marco editorial cultura (flujo): capa descriptiva si, nada operativo,
# jamas perfilar personas reales. Viaja con toda pieza derivada.
MARCO_CULTURA = (
    "Investigacion cultural DESCRIPTIVA (historia, estetica, derecho, "
    "contexto social; nada operativo, nada de sintesis quimica ni cultivo, "
    "no perfilar personas reales): "
)


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
        return json.loads(r.read().decode("utf-8", "replace"))


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

    def __init__(self, order="groq,cerebras,azure,ollama"):
        load_env()
        self.stats = {}
        self.errors = []
        self.order = [p.strip() for p in order.split(",")
                      if p.strip() in ("groq", "cerebras", "azure", "ollama")]

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

    def _ollama(self, system, user, max_tok):
        base = os.environ["OLLAMA_BASE_URL"].rstrip("/")
        prompt = (system + "\n\n" + user) if system else user
        r = _http_json(
            base + "/api/generate",
            {"model": os.environ["OLLAMA_MODEL"], "prompt": prompt,
             "stream": False,
             "options": {"temperature": 0.3, "num_predict": max_tok}},
            timeout=300,
        )
        return (r.get("response") or "").strip()

    def _has_key(self, name):
        need = {"groq": "GROQ_API_KEY", "cerebras": "CEREBRAS_API_KEY",
                "azure": "AZURE_API_KEY", "ollama": "OLLAMA_BASE_URL"}
        return bool(os.environ.get(need[name]))

    def call(self, system, user, max_tok=1024, order=None):
        """Devuelve (texto, proveedor). Recorre la cadena hasta respuesta
        no vacia; acumula errores no fatales en self.errors."""
        fns = {"groq": self._groq, "cerebras": self._cerebras,
               "azure": self._azure, "ollama": self._ollama}
        last = None
        for name in (order or self.order):
            if name not in fns or not self._has_key(name):
                continue
            try:
                text = fns[name](system, user, max_tok)
                if text:
                    self.stats[name] = self.stats.get(name, 0) + 1
                    return text, name
                last = name + " devolvio vacio"
            except Exception as e:  # noqa: BLE001 - fallback multi-proveedor
                last = name + ": " + _err_str(e)
                self.errors.append(last)
        raise RuntimeError("Todos los proveedores LLM fallaron. Ultimo: %s" % last)


def tavily_search(query, depth="basic", max_results=5, errors=None):
    """basic = 1 credito, advanced = 2. 1000/mes gratis."""
    load_env()
    try:
        return _http_json(
            "https://api.tavily.com/search",
            {"query": query, "search_depth": depth,
             "max_results": max_results, "include_answer": True,
             "include_raw_content": False},
            {"Authorization": "Bearer " + os.environ["TAVILY_API_KEY"]},
            timeout=30,
        )
    except Exception as e:  # noqa: BLE001 - la busqueda fallida no mata el loop
        if errors is not None:
            errors.append("tavily: " + _err_str(e))
        return {"results": [], "answer": None}


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
    return (MARCO_CULTURA + topic) if activo else topic
