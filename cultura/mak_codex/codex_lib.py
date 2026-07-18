#!/usr/bin/env python3
"""codex_lib.py -- nucleo del departamento CODEX (full coder de MAK).

Motor de codigo: DeepSeek via NVIDIA NIM (endpoints gratis hosteados) con
fallback a un DeepSeek local en ollama. NADA de Qwen (el usuario lo descarto:
"never understands the task"). El PLANNER (spec) usa el modelo capaz del
research (gpt-5-mini) porque planificar != codear.

El codigo generado se filtra ESTATICAMENTE y solo entonces corre en un
sandbox con limites duros de recursos; lo que toca red/procesos NO se
ejecuta, queda marcado para revision humana. Piezas en ~/codex/piezas
(.py + .md hermano indexable por el micelio).
"""
import json
import os
import re
import resource
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, "/home/mak/research")
from research_lib import (LLM, MODELO_CAPAZ, _http_json, escala_tok,  # noqa: E402
                          load_env, red_ok, slug, stamp)

# fallback_util vive junto a este archivo (deploy plano en ~/codex). Si falta
# en la caja viva, fallback_util queda en None y el mensaje de error de
# CoderLLM.call vuelve al comportamiento viejo (solo el ultimo error).
try:
    import fallback_util  # noqa: E402
except ImportError:
    fallback_util = None

BASE = "/home/mak/codex"
PIEZAS = os.path.join(BASE, "piezas")
REVISIONES = os.path.join(BASE, "revisiones")

# Cadena de CODERS (orden de fallback). NIM hosted primero (fuerte), local
# despues (offline, sobrevive 429). Sin Qwen por decision del usuario.
NIM_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
# WIN: notebook con RTX 4070 (8GB), alcanzable solo por el cable directo
# (192.168.50.1). Coder mas fuerte que el local de MAK; antes que el
# deepseek-coder:6.7b como ultimo recurso.
WIN_BASE_URL = "http://192.168.50.1:11434"
WIN_CODE_MODEL = "deepseek-coder-v2:16b-lite-instruct-q4_K_M"
CODER_CHAIN = [
    ("nim", "deepseek-ai/deepseek-v4-pro"),
    ("nim", "deepseek-ai/deepseek-v4-flash"),
    ("win", WIN_CODE_MODEL),
    ("ollama", "deepseek-coder:6.7b"),
]

# Timeouts por proveedor (segundos), espejo de los valores hardcodeados en
# _nim (120) y _ollama_chat (300). Solo informativo para el reporte de fallos.
_PROV_TIMEOUT = {"nim": 120, "win": 300, "ollama": 300}

PROMPT_CODER = (
    "Eres un ingeniero de software senior del departamento Codex de MAK. "
    "Escribes Python 3.11 stdlib-only, completo y ejecutable, con nombres y "
    "comentarios en espanol correcto (con tildes). Devuelves UN solo bloque "
    "```python``` con el archivo entero; sin explicaciones fuera del bloque."
)

_PELIGRO = [
    (r"\bimport\s+(os|subprocess|shutil|socket|ctypes|signal|pty|multiprocessing)\b", "modulo de sistema/red"),
    (r"\bfrom\s+(os|subprocess|shutil|socket|ctypes)\b", "modulo de sistema/red"),
    (r"\bimport\s+(urllib|requests|http|ftplib|smtplib|telnetlib)\b", "modulo de red"),
    (r"\b__import__\s*\(", "import dinamico"),
    (r"\bimportlib\b", "import dinamico"),
    (r"\beval\s*\(|\bexec\s*\(", "eval/exec"),
    (r"\bopen\s*\(\s*['\"]/", "apertura de ruta absoluta"),
    (r"os\.(system|popen|exec|spawn|remove|rmdir|unlink)", "llamada de sistema"),
    (r"shutil\.rmtree", "borrado recursivo"),
]


def _msgs(system, user):
    if system:
        return [{"role": "system", "content": system},
                {"role": "user", "content": user}]
    return [{"role": "user", "content": user}]


class CoderLLM:
    """Cadena de coders con fallback. DeepSeek NIM hosted -> DeepSeek local.
    call() devuelve (texto, modelo_real); acumula errores no fatales."""

    def __init__(self, chain=None):
        load_env()
        self.chain = chain or CODER_CHAIN
        self.stats = {}
        self.errors = []

    def _nim(self, system, user, max_tok, model):
        key = os.environ.get("NVIDIA_API_KEY")
        if not key:
            raise RuntimeError("falta NVIDIA_API_KEY")
        r = _http_json(
            NIM_URL,
            {"model": model, "messages": _msgs(system, user),
             "temperature": 0.1, "max_tokens": max_tok},
            {"Authorization": "Bearer " + key}, timeout=120)
        return r["choices"][0]["message"]["content"].strip()

    def _ollama_chat(self, base_url, system, user, max_tok, model):
        base = base_url.rstrip("/")
        r = _http_json(
            base + "/api/chat",
            {"model": model, "messages": _msgs(system, user), "stream": False,
             "options": {"temperature": 0.1, "num_predict": max_tok}},
            timeout=300)
        return (r.get("message", {}).get("content") or "").strip()

    def _ollama(self, system, user, max_tok, model):
        base = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        return self._ollama_chat(base, system, user, max_tok, model)

    def _win(self, system, user, max_tok, model):
        return self._ollama_chat(WIN_BASE_URL, system, user, max_tok, model)

    def call(self, system, user, max_tok=1200):
        cadena = list(self.chain)
        # sin internet: win/ollama primero (LAN directa, no depende de
        # internet). WIN (RTX 4070) antes que el local de MAK -- mas fuerte.
        if not red_ok():
            frente = [c for c in cadena if c[0] in ("win", "ollama")]
            cadena = frente + [c for c in cadena if c not in frente]
        fns = {"nim": self._nim, "win": self._win, "ollama": self._ollama}
        last = None
        intentos = []  # todos los intentos fallidos, no solo el ultimo
        for prov, model in cadena:
            try:
                text = fns[prov](system, user, max_tok, model)
                if text and text.strip():
                    self.stats[model] = self.stats.get(model, 0) + 1
                    return text, model
                last = model + " devolvio vacio"
                if fallback_util is not None:
                    intentos.append(fallback_util.parse_provider_error(
                        "devolvio vacio", prov, model))
            except Exception as e:  # noqa: BLE001 - fallback multi-coder
                last = model + ": " + str(e)[:140]
                self.errors.append(last)
                if fallback_util is not None:
                    intentos.append(fallback_util.parse_provider_error(
                        e, prov, model, timeout_sec=_PROV_TIMEOUT.get(prov)))
        if fallback_util is not None and intentos:
            raise RuntimeError(fallback_util.aggregate_failures(intentos))
        raise RuntimeError("Todos los coders fallaron. Ultimo: %s" % last)


# Presupuesto de tokens del CODER: generoso. DeepSeek escribe codigo verboso
# (docstrings, type hints); con poco presupuesto se trunca a mitad de un
# string y el sandbox da SyntaxError. El coder necesita espacio, no como la
# prosa del research (escala_tok tope 4000 es muy poco para un archivo).
CODER_TOK = {"corto": 4096, "medio": 6144, "largo": 8192}


def coder_tok(densidad="medio"):
    return CODER_TOK.get(densidad, 6144)


def coder_llm():
    """El motor de CODIGO (DeepSeek NIM + fallback local)."""
    return CoderLLM()


def planner_llm():
    """El PLANNER (spec/tests): modelo capaz del research (gpt-5-mini)."""
    load_env()
    return LLM(order="%s,groq,cerebras,ollama" % MODELO_CAPAZ)


def escanear(codigo):
    """Motivos por los que este codigo NO se auto-ejecuta (lista vacia = ok)."""
    motivos = []
    for patron, motivo in _PELIGRO:
        if re.search(patron, codigo):
            motivos.append(motivo)
    return sorted(set(motivos))


def extraer_codigo(texto):
    m = re.search(r"```(?:python|py)?\s*\n(.*?)```", texto or "", re.S)
    return (m.group(1) if m else (texto or "")).strip()


def _limites():
    resource.setrlimit(resource.RLIMIT_CPU, (20, 20))
    resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    resource.setrlimit(resource.RLIMIT_FSIZE, (20 << 20, 20 << 20))


def sandbox_run(path_py, timeout=30, argv=None):
    """Ejecuta un .py YA ESCANEADO en un interprete aislado con limites."""
    with open(path_py, encoding="utf-8", errors="replace") as f:
        codigo = f.read()
    motivos = escanear(codigo)
    if motivos:
        return {"ok": False, "bloqueado": True, "motivos": motivos,
                "stdout": "", "stderr": "", "rc": -1}
    with tempfile.TemporaryDirectory(prefix="codex-sbx-") as tmp:
        destino = os.path.join(tmp, os.path.basename(path_py))
        with open(destino, "w", encoding="utf-8") as f:
            f.write(codigo)
        cmd = [sys.executable, "-I", "-S", destino] + (argv or [])
        try:
            p = subprocess.run(
                cmd, cwd=tmp, capture_output=True, text=True,
                timeout=timeout, preexec_fn=_limites,
                env={"PATH": "/usr/bin:/bin", "HOME": tmp, "LANG": "C.UTF-8"})
            return {"ok": p.returncode == 0, "rc": p.returncode,
                    "stdout": p.stdout[-4000:], "stderr": p.stderr[-4000:]}
        except subprocess.TimeoutExpired:
            return {"ok": False, "rc": -9, "stdout": "",
                    "stderr": "timeout %ds en sandbox" % timeout}
        except OSError as e:
            return {"ok": False, "rc": -1, "stdout": "", "stderr": str(e)}


def guardar_pieza(pedido, codigo, resultado, meta):
    """Escribe la pieza .py + su .md hermano (indexable por el micelio)."""
    os.makedirs(PIEZAS, exist_ok=True)
    base = os.path.join(PIEZAS, "%s-%s" % (stamp(), slug(pedido)))
    with open(base + ".py", "w", encoding="utf-8") as f:
        f.write(codigo if codigo.endswith("\n") else codigo + "\n")
    with open(base + ".md", "w", encoding="utf-8") as f:
        f.write("# Codex: %s\n\n" % pedido)
        if resultado.get("bloqueado"):
            f.write("**Ejecución bloqueada — requiere revisión humana.** "
                    "Motivos: %s\n\n" % ", ".join(resultado["motivos"]))
        elif resultado.get("rc", -1) == 0:
            f.write("Sandbox: **OK** (rc=0).\n\n")
        else:
            f.write("Sandbox: **FALLÓ** (rc=%s).\n\n" % resultado.get("rc"))
        f.write("```python\n%s\n```\n\n" % codigo.strip())
        if resultado.get("stdout"):
            f.write("## stdout\n\n```\n%s\n```\n\n" % resultado["stdout"].strip())
        if resultado.get("stderr"):
            f.write("## stderr\n\n```\n%s\n```\n\n" % resultado["stderr"].strip())
        f.write("---\nmeta: %s\n" % json.dumps(meta, ensure_ascii=False))
    return base + ".py", base + ".md"


def guardia_espera():
    """Gate de recursos de la plataforma; sin guardia = sigue igual."""
    try:
        sys.path.insert(0, "/home/mak/plataforma")
        import guardia
        return guardia.esperar_recursos()
    except ImportError:
        return True


def tiempo_ms(t0):
    return int((time.time() - t0) * 1000)
