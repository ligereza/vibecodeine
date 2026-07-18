#!/usr/bin/env python3
"""interfaz.py -- interfaz web LAN del research MAK (puerto 8890).

Interfaz tipo n8n con canvas visual, nodos arrastrables, conexiones SVG
editables (dos clicks entre puertos) y 4 modelos intercambiables/editables
(Groq, Cerebras, Azure, Ollama). Soporta multiples triggers/outputs.

Modos: single, pipeline (encadenado), discussion (comite: todos convergen
al output), adversarial (proponente->refutadores->juez) y grafo (custom:
las conexiones dibujadas dirigen la ejecucion real via grafo.py). Los
primeros cuatro regeneran su topologia como preset; grafo la respeta.

    python3 interfaz.py   # http://192.168.50.2:8890

Deployment Linux:
    systemctl start mak-interfaz
    systemctl enable mak-interfaz
"""
import html
import json
import os
import re
import shutil
import signal
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pausa
from research_lib import emitir_evento, load_env, mint_job_id
from worker import run_tema

# ── configuración ──
PORT = int(os.environ.get("INTERFAZ_PORT", "8890"))
DIRS = {
    "informes": os.path.expanduser("~/research/informes"),
    "paneles": os.path.expanduser("~/research/paneles"),
    "cadenas": os.path.expanduser("~/research/cadenas"),
    "refutaciones": os.path.expanduser("~/research/refutaciones"),
    "correlaciones": os.path.expanduser("~/research/correlaciones"),
    "grafos": os.path.expanduser("~/research/grafos"),
    "memoria": os.path.expanduser("~/research/memoria"),
}
# modo (backend script) -> carpeta de salida; single reusa el motor de research
MODO_DIR = {"research": "informes", "panel": "paneles",
            "cadena": "cadenas", "refutar": "refutaciones",
            "corpus": "correlaciones", "grafo": "grafos",
            "memoria": "memoria"}
# modos que NO requieren tema (correlacionan el archivo entero)
MODO_SIN_TEMA = {"corpus"}
# paleta cultura (abisal + fungico + tierras) por tipo de producto
DIR_COLOR = {"informes": "#9db67c", "paneles": "#d4a259",
             "cadenas": "#7ba6a3", "refutaciones": "#c46d5e",
             "correlaciones": "#b48ead", "grafos": "#93a8c7",
             "memoria": "#e0c58f"}
FECHA_RE = re.compile(r"(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})-(.+)\.md$")
DIR_CHIP = {"informes": "informe", "paneles": "panel", "cadenas": "cadena",
            "refutaciones": "refutacion", "correlaciones": "correlacion",
            "grafos": "grafo", "memoria": "memoria"}
JOBS_FILE = os.path.expanduser("~/research/jobs.jsonl")
ENV_FILE = os.environ.get("RESEARCH_ENV", os.path.expanduser("~/n8n-local/research.env"))
WORKFLOW_FILE = os.path.expanduser("~/research/workflow.json")

JOBS = []
JOBS_LOCK = threading.Lock()
WORKFLOW_LOCK = threading.Lock()

CONFIG_FIELDS = [
    ("GROQ_MODEL", "Groq model"),
    ("CEREBRAS_MODEL", "Cerebras model"),
    ("AZURE_DEPLOYMENT", "Azure deployment"),
    ("OLLAMA_MODEL", "Ollama model"),
    ("PROVIDERS_ORDER", "Order de providers"),
]
CONFIG_KEYS = {k for k, _ in CONFIG_FIELDS}

NOMBRE_OK = re.compile(r"^[A-Za-z0-9._-]+\.(md|json)$")

# ── workflow persistence ──

DEFAULT_WORKFLOW = {
    # single | pipeline | discussion | adversarial | grafo (custom)
    "mode": "pipeline",
    "nodes": {
        "trigger": {"x": 80, "y": 200, "active": True, "tipo": "trigger"},
        "groq": {
            "x": 340, "y": 80, "active": True,
            "model": "", "temperature": 0.7, "max_tokens": 4096,
            "system_prompt": "", "priority": 1,
        },
        "cerebras": {
            "x": 340, "y": 200, "active": True,
            "model": "", "temperature": 0.7, "max_tokens": 4096,
            "system_prompt": "", "priority": 2,
        },
        "azure": {
            "x": 340, "y": 320, "active": True,
            "model": "", "temperature": 0.7, "max_tokens": 4096,
            "system_prompt": "", "priority": 3,
        },
        "ollama": {
            "x": 340, "y": 440, "active": False,
            "model": "", "temperature": 0.7, "max_tokens": 4096,
            "system_prompt": "", "priority": 4,
        },
        "output": {"x": 700, "y": 200, "active": True, "tipo": "output"},
    },
    # Conexiones dirigidas [{from, to}]. En modo 'grafo' DIRIGEN la
    # ejecucion real (grafo.py, orden topologico). En los otros modos son
    # el dibujo del canvas (el preset del modo las regenera).
    "connections": [
        {"from": "trigger", "to": "groq"},
        {"from": "groq", "to": "cerebras"},
        {"from": "cerebras", "to": "azure"},
        {"from": "azure", "to": "output"},
    ],
}


def _deep_copy_default():
    return json.loads(json.dumps(DEFAULT_WORKFLOW))


def _load_workflow():
    try:
        with open(WORKFLOW_FILE, "r", encoding="utf-8") as f:
            wf = json.load(f)
        merged = _deep_copy_default()
        if "mode" in wf:
            merged["mode"] = wf["mode"]
        if "nodes" in wf:
            merged["nodes"] = {}
            for k, v in wf["nodes"].items():
                base = DEFAULT_WORKFLOW["nodes"].get(k)
                if base:
                    node = json.loads(json.dumps(base))
                    node.update(v)
                    merged["nodes"][k] = node
                else:
                    merged["nodes"][k] = v
        # connections: si el archivo las trae (aunque sea []), mandan ellas;
        # la lista vacia es un estado valido (grafo sin aristas aun)
        if isinstance(wf.get("connections"), list):
            merged["connections"] = wf["connections"]
        return merged
    except (OSError, json.JSONDecodeError, TypeError):
        return _deep_copy_default()


def _save_workflow(wf):
    os.makedirs(os.path.dirname(WORKFLOW_FILE), exist_ok=True)
    tmp = WORKFLOW_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(wf, f, indent=2)
    os.replace(tmp, WORKFLOW_FILE)


# ── jobs ──

def _load_jobs():
    global JOBS
    try:
        with open(JOBS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        JOBS.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        JOBS = JOBS[-15:]
    except OSError:
        pass


def _diagnosticar(tema, error):
    """Auto-reparacion: el modelo capaz lee el error real y devuelve
    diagnostico + fix. Sincronico (bloquea la request), sin lock de job:
    es solo una llamada LLM de lectura, no corre nada."""
    from research_lib import LLM, diagnosticar_error
    load_env(ENV_FILE)
    llm = LLM()
    contexto = "Job de research MAK, tema: %s" % (tema or "(corpus)")
    texto, _ = diagnosticar_error(llm, contexto, error)
    return texto


def _memoria_stats():
    """Cuenta chunks indexados en la memoria del departamento."""
    try:
        with open(os.path.expanduser("~/research/memoria/index.jsonl"),
                  encoding="utf-8") as f:
            chunks = sum(1 for line in f if line.strip())
    except OSError:
        chunks = 0
    return {"chunks": chunks}


_REINDEX_LOCK = threading.Lock()


def _reindexar_async(rebuild=False):
    """Reindexa en background (no bloquea la request). Un reindex a la vez."""
    if not _REINDEX_LOCK.acquire(blocking=False):
        return False

    def correr():
        try:
            import memoria
            memoria.indexar(rebuild=rebuild)
        except Exception as e:  # noqa: BLE001 - reindex es best-effort
            print("[interfaz] reindex error: %s" % e, file=sys.stderr)
        finally:
            _REINDEX_LOCK.release()

    threading.Thread(target=correr, daemon=True).start()
    return True


def _orden_canvas():
    """CSV de proveedores segun la prioridad definida en el canvas.
    Usado por modo=cadena/refutar para que 'ordenar los nodos' en la UI
    realmente cambie el orden de ejecucion, no solo el dibujo."""
    with WORKFLOW_LOCK:
        wf = _load_workflow()
    provs = [k for k in ("groq", "cerebras", "azure", "ollama")
            if wf.get("nodes", {}).get(k, {}).get("active", True)]
    provs.sort(key=lambda k: wf["nodes"].get(k, {}).get("priority", 99))
    return ",".join(provs) if provs else None


def _guardia_contenido(tema):
    """Clasifica la peticion via plataforma/filtro_entrada. Devuelve el dict
    del veredicto o None si el filtro no esta (fail-open: no bloquear research
    legitimo por falta del modulo)."""
    try:
        sys.path.insert(0, "/home/mak/plataforma")
        import filtro_entrada
        return filtro_entrada.clasificar(tema)
    except Exception:  # noqa: BLE001 - sin guardia = sigue (fail-open)
        return None


def _aplicar_resultado_job(job, r):
    """Interpreta el dict devuelto por run_tema() y actualiza `job` in-place
    (listo/FALLO/PAUSADO). Compartido entre el lanzamiento inicial (_lanzar)
    y el reanudar tras pausa (_reanudar_logic)."""
    if r.get("pausado"):
        job["estado"] = "PAUSADO"
        job["checkpoint"] = r.get("checkpoint", "")
        job["error"] = (r.get("tail") or "").strip()[:2000]
        return
    job["estado"] = "listo" if r.get("ok") else "FALLO"
    job["path"] = os.path.basename(r["path"]) if r.get("path") else ""
    if not r.get("ok"):
        # log explicito: ultimas lineas reales del proceso, no solo "FALLO"
        job["error"] = (r.get("tail") or "").strip()[-2000:]


def _cerrar_job(job, t0):
    """Cierra el job: ms transcurridos, linea en JOBS_FILE, reindex best-effort."""
    job["ms"] = int((time.time() - t0) * 1000)
    try:
        with open(JOBS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(job) + "\n")
    except OSError:
        pass
    # el archivo crece -> la memoria/micelio se remodela solo (incremental)
    try:
        _reindexar_async()
    except Exception:  # noqa: BLE001 - el reindex es best-effort
        pass


def _lanzar(modo, tema, n, densidad="medio", memoria=False):
    job = {
        "tema": tema, "modo": modo, "estado": "en cola",
        "path": "", "error": "", "t": time.strftime("%H:%M:%S"),
        "job_id": mint_job_id(),
    }
    with JOBS_LOCK:
        JOBS.append(job)

    def correr():
        t0 = time.time()
        job["estado"] = "corriendo"
        # guardia de contenido: no corre lo que pida PRODUCIR dano o SALTAR
        # filtros; el research DESCRIPTIVO de temas sensibles SI pasa
        if modo not in MODO_SIN_TEMA:
            g = _guardia_contenido(tema)
            if g and g.get("veredicto") != "DESCRIPTIVO":
                job["estado"] = "BLOQUEADO"
                job["error"] = "guardia de contenido: %s -- %s" % (
                    g["veredicto"], g["razon"])
                job["ms"] = int((time.time() - t0) * 1000)
                try:
                    with open(JOBS_FILE, "a", encoding="utf-8") as f:
                        f.write(json.dumps(job) + "\n")
                except OSError:
                    pass
                return
        try:
            orden = _orden_canvas() if modo in ("cadena", "refutar") else None
            r = run_tema(modo, tema, n=n, ntfy=True, densidad=densidad,
                        orden=orden, memoria=memoria, job_id=job["job_id"])
            _aplicar_resultado_job(job, r)
        except Exception as e:
            job["estado"] = "FALLO"
            job["path"] = ""
            job["error"] = str(e)[:2000]
            print(f"[interfaz] job error: {e}", file=sys.stderr)
        _cerrar_job(job, t0)

    threading.Thread(target=correr, daemon=True).start()


def _reanudar_logic(q):
    """Decide la accion sobre un job PAUSADO (reintentar/editar/saltar/abortar).
    Recibe el dict de urllib.parse.parse_qs (valores como listas). Devuelve
    (status_code, payload). Thread-safe: busca el job bajo JOBS_LOCK. Lanza
    el hilo de reanudacion cuando corresponde -- testeable sin servidor HTTP
    real (monkeypatch run_tema / pausa.aplicar_accion)."""
    job_id = (q.get("job_id") or [""])[0]
    accion = (q.get("accion") or [""])[0]
    texto = (q.get("texto") or [""])[0]

    with JOBS_LOCK:
        job = next((j for j in JOBS if j.get("job_id") == job_id), None)
    if job is None:
        return 404, {"ok": False, "error": "job no encontrado"}
    if job.get("estado") != "PAUSADO":
        return 400, {"ok": False, "error": "job no esta PAUSADO"}

    if accion == "abortar":
        job["estado"] = "abortado"
        try:
            emitir_evento("research", job_id, "node_end", estado="abortado")
        except Exception:  # noqa: BLE001 - el evento es best-effort
            pass
        try:
            with open(JOBS_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(job) + "\n")
        except OSError:
            pass
        return 200, {"ok": True, "estado": "abortado"}

    if accion not in ("reintentar", "editar", "saltar"):
        return 400, {"ok": False, "error": "accion invalida"}

    try:
        pausa.aplicar_accion(job["checkpoint"], accion, texto)
    except ValueError:
        return 400, {"ok": False, "error": "accion invalida"}
    except OSError as e:
        return 500, {"ok": False, "error": str(e)[:300]}

    job["estado"] = "corriendo"

    def relanzar():
        t0 = time.time()
        try:
            r = run_tema(job["modo"], job["tema"], ntfy=True, job_id=job["job_id"],
                        extra=["--resume", job["checkpoint"]])
            _aplicar_resultado_job(job, r)
        except Exception as e:
            job["estado"] = "FALLO"
            job["error"] = str(e)[:2000]
            print(f"[interfaz] job resume error: {e}", file=sys.stderr)
        _cerrar_job(job, t0)

    threading.Thread(target=relanzar, daemon=True).start()
    return 200, {"ok": True, "estado": "corriendo"}


# ── utilidades ──

def _config_actual():
    load_env(ENV_FILE)
    return {k: os.environ.get(k, "") for k, _ in CONFIG_FIELDS}


def _guardar_config(values):
    load_env(ENV_FILE)
    if os.path.exists(ENV_FILE):
        shutil.copy2(ENV_FILE, ENV_FILE + ".bak")
    os.makedirs(os.path.dirname(ENV_FILE), exist_ok=True)
    existing = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    existing[k] = v
    for k, _ in CONFIG_FIELDS:
        if k in values:
            v = values[k][0] if isinstance(values[k], list) else values[k]
            existing[k] = str(v)
            os.environ[k] = str(v)
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        for k, _ in CONFIG_FIELDS:
            f.write(f"{k}={existing.get(k, '')}\n")
        for k, v in sorted(existing.items()):
            if k not in CONFIG_KEYS:
                f.write(f"{k}={v}\n")
    return _config_actual()


# ─────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────

CSS = """
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;overflow:hidden}
body{
  font-family:'Inter','Segoe UI',system-ui,-apple-system,sans-serif;
  background:#0d1117;color:#e6edf3;display:flex;flex-direction:column;
}
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:#161b22}
::-webkit-scrollbar-thumb{background:#30363d;border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:#484f58}

/* ── topbar ── */
.topbar{
  display:flex;align-items:center;justify-content:space-between;
  background:linear-gradient(135deg,#161b22 0%,#1c2430 100%);
  border-bottom:1px solid #30363d;padding:0 20px;height:52px;
  flex-shrink:0;z-index:100;
}
.topbar-left{display:flex;align-items:center;gap:14px}
.logo{display:flex;align-items:center;gap:8px;font-weight:700;font-size:1.05rem;color:#e6edf3}
.logo svg{width:26px;height:26px}
.topbar-center{display:flex;gap:6px}
.mode-btn{
  padding:6px 14px;border-radius:8px;border:1px solid #30363d;
  background:#161b22;color:#8b949e;cursor:pointer;font-size:.82rem;
  transition:all .15s;font-family:inherit;
}
.mode-btn:hover{border-color:#58a6ff;color:#58a6ff}
.mode-btn.active{background:#1f6feb;border-color:#1f6feb;color:#fff}
.topbar-right{display:flex;gap:10px;align-items:center}
.topbar-pill{
  background:rgba(255,255,255,.06);padding:5px 12px;border-radius:999px;
  font-size:.78rem;color:#8b949e;border:1px solid #30363d;
}
.status-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:6px}
.status-dot.idle{background:#3fb950}
.status-dot.busy{background:#d29922;animation:pulse 1s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}

/* ── main layout ── */
.main-wrap{display:flex;flex:1;overflow:hidden}

/* ── canvas ── */
.canvas-wrap{
  flex:1;position:relative;overflow:hidden;background:#0d1117;
  background-image:radial-gradient(circle,#21262d 1px,transparent 1px);
  background-size:24px 24px;cursor:grab;
}
.canvas-wrap.panning{cursor:grabbing}
#canvas-world{
  position:absolute;top:0;left:0;width:3000px;height:2000px;
  transform-origin:0 0;
}
#canvas-svg{position:absolute;top:0;left:0;width:3000px;height:2000px;pointer-events:none;z-index:1}
.node{
  position:absolute;z-index:10;min-width:195px;max-width:240px;
  background:#161b22;border:2px solid #30363d;border-radius:14px;
  padding:0;cursor:grab;user-select:none;
  box-shadow:0 4px 16px rgba(0,0,0,.4);
  transition:border-color .2s,box-shadow .2s;
}
.node:hover{border-color:#58a6ff;box-shadow:0 4px 24px rgba(88,166,255,.15)}
.node.selected{border-color:#f0883e;box-shadow:0 0 0 3px rgba(240,136,62,.25)}
.node.inactive{opacity:.4}
.node-header{
  display:flex;align-items:center;gap:8px;
  padding:10px 14px;border-bottom:1px solid #21262d;
  border-radius:12px 12px 0 0;
}
.node-icon{
  width:32px;height:32px;border-radius:8px;
  display:flex;align-items:center;justify-content:center;
  font-size:.85rem;font-weight:700;color:#fff;flex-shrink:0;
}
.node-title{font-weight:600;font-size:.88rem;color:#e6edf3}
.node-subtitle{font-size:.72rem;color:#8b949e;margin-top:1px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:130px}
.node-body{padding:8px 14px 10px;font-size:.78rem;color:#8b949e}
.node-badge{
  display:inline-block;padding:2px 8px;border-radius:6px;
  font-size:.68rem;font-weight:600;margin-top:4px;
}
.node-priority{
  position:absolute;top:-8px;right:-8px;width:22px;height:22px;
  border-radius:50%;background:#1f6feb;color:#fff;font-size:.7rem;
  display:flex;align-items:center;justify-content:center;
  font-weight:700;border:2px solid #0d1117;
}
.node-toggle{
  position:absolute;top:10px;right:10px;width:36px;height:20px;
  border-radius:10px;background:#30363d;cursor:pointer;border:none;
  transition:background .2s;z-index:5;
}
.node-toggle::after{
  content:'';position:absolute;top:2px;left:2px;width:16px;height:16px;
  border-radius:50%;background:#8b949e;transition:all .2s;
}
.node-toggle.on{background:#238636}
.node-toggle.on::after{left:18px;background:#fff}

/* connector ports */
.port{
  position:absolute;width:12px;height:12px;border-radius:50%;
  background:#30363d;border:2px solid #161b22;z-index:15;
  transition:background .15s;
}
.port:hover{background:#58a6ff}
.port-out{right:-7px;top:50%;transform:translateY(-50%)}
.port-in{left:-7px;top:50%;transform:translateY(-50%)}

/* canvas tools menu */
.canvas-controls{
  position:absolute;bottom:14px;left:14px;display:flex;flex-direction:column;
  gap:8px;z-index:20;
}
.tool-group{
  display:flex;gap:4px;background:#0d1117cc;border:1px solid #30363d;
  border-radius:10px;padding:4px;backdrop-filter:blur(4px);
}
.tool-group .tool-label{
  font-size:.62rem;color:#6e7681;text-transform:uppercase;letter-spacing:.5px;
  align-self:center;padding:0 6px 0 4px;
}
.canvas-controls button{
  min-width:32px;height:30px;padding:0 8px;border-radius:7px;border:1px solid #30363d;
  background:#161b22;color:#c9d1d9;cursor:pointer;font-size:.9rem;font-weight:600;
  display:flex;align-items:center;justify-content:center;gap:4px;
  transition:all .15s;
}
.canvas-controls button:hover{background:#21262d;color:#fff;border-color:#58a6ff}
.zoom-level{
  min-width:44px;text-align:center;font-size:.75rem;color:#8b949e;
  align-self:center;font-variant-numeric:tabular-nums;
}

/* ── right panel ── */
.panel{
  width:360px;background:#161b22;border-left:1px solid #30363d;
  overflow-y:auto;flex-shrink:0;display:flex;flex-direction:column;
}
.panel-header{
  padding:16px 18px;border-bottom:1px solid #21262d;
  font-weight:600;font-size:.95rem;display:flex;align-items:center;gap:8px;
}
.panel-section{padding:14px 18px;border-bottom:1px solid #21262d}
.panel-section h3{
  font-size:.75rem;text-transform:uppercase;letter-spacing:.5px;
  color:#8b949e;margin-bottom:10px;
}
.field{margin-bottom:12px}
.field label{display:block;font-size:.75rem;color:#8b949e;margin-bottom:4px;font-weight:500}
.field input,.field select,.field textarea{
  width:100%;padding:8px 10px;border-radius:8px;
  border:1px solid #30363d;background:#0d1117;color:#e6edf3;
  font-size:.82rem;font-family:inherit;transition:border-color .15s;
}
.field input:focus,.field select:focus,.field textarea:focus{
  outline:none;border-color:#58a6ff;box-shadow:0 0 0 2px rgba(88,166,255,.15);
}
.field textarea{min-height:70px;resize:vertical}
.field .range-wrap{display:flex;align-items:center;gap:8px}
.field input[type=range]{flex:1;accent-color:#1f6feb;height:4px}
.field .range-val{font-size:.8rem;color:#58a6ff;min-width:38px;text-align:right;font-weight:600}

/* ── buttons ── */
.btn{
  display:inline-flex;align-items:center;gap:6px;padding:8px 16px;
  border-radius:8px;border:none;font-size:.82rem;font-weight:600;
  cursor:pointer;transition:all .15s;font-family:inherit;
}
.btn-primary{background:#238636;color:#fff}
.btn-primary:hover{background:#2ea043}
.btn-secondary{background:#21262d;color:#e6edf3;border:1px solid #30363d}
.btn-secondary:hover{background:#30363d}
.btn-accent{background:#1f6feb;color:#fff}
.btn-accent:hover{background:#388bfd}

/* ── execution bar (bottom) ── */
.exec-bar{
  display:flex;align-items:center;gap:12px;padding:10px 18px;
  background:#161b22;border-top:1px solid #30363d;flex-shrink:0;z-index:50;
}
.exec-bar input,.exec-bar select{
  padding:8px 12px;border-radius:8px;border:1px solid #30363d;
  background:#0d1117;color:#e6edf3;font-size:.85rem;font-family:inherit;
}
.exec-bar input:focus,.exec-bar select:focus{outline:none;border-color:#58a6ff}
.exec-bar .tema-input{flex:1}

/* ── jobs / history ── */
.job-list{list-style:none}
.job-item{
  display:flex;align-items:center;gap:10px;padding:8px 0;
  border-bottom:1px solid #21262d;font-size:.8rem;
}
.job-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.job-dot.en-cola{background:#d29922}
.job-dot.corriendo{background:#58a6ff;animation:pulse 1s infinite}
.job-dot.listo{background:#3fb950}
.job-dot.fallo{background:#f85149}
.job-dot.pausado{background:#e0a458}
.job-dot.abortado{background:#8a8578}

/* ── tabs ── */
.tabs{display:flex;border-bottom:1px solid #21262d}
.tab{
  flex:1;padding:10px;text-align:center;font-size:.78rem;font-weight:600;
  color:#8b949e;cursor:pointer;border:none;background:none;
  border-bottom:2px solid transparent;transition:all .15s;font-family:inherit;
}
.tab:hover{color:#e6edf3}
.tab.active{color:#58a6ff;border-bottom-color:#58a6ff}
.tab-content{display:none}
.tab-content.active{display:block}

/* ── file list ── */
.file-list{list-style:none}
.file-item{padding:6px 0;font-size:.78rem;border-bottom:1px solid #21262d}
.file-item a{color:#58a6ff;text-decoration:none}
.file-item a:hover{text-decoration:underline}

/* ── toast ── */
.toast{
  position:fixed;bottom:70px;right:20px;z-index:999;
  padding:12px 20px;border-radius:10px;font-size:.85rem;font-weight:600;
  opacity:0;transform:translateY(10px);transition:all .3s;pointer-events:none;
}
.toast.show{opacity:1;transform:translateY(0)}
.toast.success{background:#238636;color:#fff}
.toast.error{background:#da3633;color:#fff}
.toast.info{background:#1f6feb;color:#fff}

.view-overlay{
  display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);
  z-index:1000;align-items:center;justify-content:center;
}
.view-overlay.show{display:flex}
.view-box{
  background:#161b22;border:1px solid #30363d;border-radius:10px;
  width:min(820px,92vw);max-height:86vh;display:flex;flex-direction:column;
  overflow:hidden;
}
.view-box-head{
  display:flex;align-items:center;justify-content:space-between;
  padding:12px 16px;border-bottom:1px solid #30363d;font-weight:600;
}
.view-box-body{
  padding:16px 20px;overflow-y:auto;line-height:1.55;font-size:.9rem;
}
.view-box-body h1,.view-box-body h2,.view-box-body h3{margin:.8em 0 .4em;color:#e6edf3}
.view-box-body p{margin:.5em 0}
.view-box-body ul{margin:.4em 0;padding-left:1.4em}
.view-box-body a{color:#58a6ff}
.view-box-body.error-view{
  font-family:ui-monospace,monospace;white-space:pre-wrap;
  color:#ffa198;font-size:.82rem;
}

/* ── connection animation ── */
@keyframes dash-flow{to{stroke-dashoffset:-20}}
.conn-animated{stroke-dasharray:8 4;animation:dash-flow .6s linear infinite}

/* ── view toggle (Flujo / Mapa) ── */
.view-toggle{
  display:flex;background:#0d1117;border:1px solid #30363d;border-radius:9px;
  padding:3px;gap:2px;
}
.view-toggle button{
  display:flex;align-items:center;gap:6px;padding:5px 12px;border:none;
  background:none;color:#8b949e;border-radius:7px;cursor:pointer;
  font-size:.82rem;font-weight:600;font-family:inherit;transition:all .15s;
}
.view-toggle button svg{width:15px;height:15px}
.view-toggle button:hover{color:#e6edf3}
.view-toggle button.active{background:#1f6feb;color:#fff}

/* ── semantic map view ── */
#map-view{
  position:absolute;inset:0;display:none;background:
    radial-gradient(circle at 30% 20%,#12161f 0,#0a0c10 55%,#08090c 100%);
  overflow:hidden;
}
#map-view.show{display:block}
#map-canvas{position:absolute;inset:0;width:100%;height:100%;display:block;cursor:grab}
#map-canvas.grabbing{cursor:grabbing}
#map-canvas.hot{cursor:pointer}
.map-legend{
  position:absolute;top:16px;left:16px;background:#0d1117cc;border:1px solid #30363d;
  border-radius:12px;padding:12px 14px;backdrop-filter:blur(8px);z-index:6;
  max-width:220px;
}
.map-legend h4{font-size:.7rem;text-transform:uppercase;letter-spacing:.6px;color:#8b949e;margin-bottom:9px}
.map-legend .lg-row{display:flex;align-items:center;gap:8px;font-size:.78rem;color:#c9d1d9;margin:4px 0;cursor:pointer;opacity:.9}
.map-legend .lg-row:hover{opacity:1}
.map-legend .lg-row.off{opacity:.35}
.map-legend .lg-dot{width:11px;height:11px;border-radius:50%;flex-shrink:0;box-shadow:0 0 8px currentColor}
.map-controls{
  position:absolute;bottom:16px;left:16px;display:flex;flex-direction:column;gap:8px;z-index:6;
}
.map-controls .tool-group{align-items:center}
.map-controls .mc-slider{display:flex;align-items:center;gap:8px;color:#8b949e;font-size:.74rem}
.map-controls input[type=range]{width:120px;accent-color:#a371f7;height:4px}
.map-hint{
  position:absolute;top:16px;right:16px;background:#0d1117cc;border:1px solid #30363d;
  border-radius:10px;padding:8px 12px;font-size:.74rem;color:#8b949e;z-index:6;
  backdrop-filter:blur(8px);max-width:230px;line-height:1.5;
}
.map-tooltip{
  position:absolute;pointer-events:none;z-index:8;background:#161b22ee;
  border:1px solid #444c56;border-radius:9px;padding:8px 11px;max-width:280px;
  font-size:.78rem;color:#e6edf3;box-shadow:0 6px 20px rgba(0,0,0,.5);
  transform:translate(-50%,-115%);display:none;line-height:1.4;
}
.map-tooltip.show{display:block}
.map-tooltip .mt-dir{font-size:.68rem;color:#8b949e;text-transform:uppercase;letter-spacing:.5px}
.map-empty{
  position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  flex-direction:column;gap:10px;color:#6e7681;text-align:center;padding:30px;
}

/* ── view toggle (Flujo / Micelio) ── */
.main-wrap{position:relative}
.view-toggle{
  display:flex;background:#0d1117;border:1px solid #30363d;border-radius:9px;
  padding:3px;gap:2px;
}
.view-toggle button{
  display:flex;align-items:center;gap:6px;padding:5px 12px;border:none;
  background:none;color:#8b949e;border-radius:7px;cursor:pointer;
  font-size:.82rem;font-weight:600;font-family:inherit;transition:all .15s;
}
.view-toggle button svg{width:15px;height:15px}
.view-toggle button:hover{color:#e6edf3}
.view-toggle button.active{background:#9db67c;color:#0b0a09}

/* ── micelio semantico (archivo vivo, paleta cultura: abisal + fungico) ── */
#map-view{
  position:absolute;inset:0;display:none;background:
    radial-gradient(ellipse at 32% 24%,#15130e 0,#0b0a09 58%,#070706 100%);
  overflow:hidden;z-index:30;
}
#map-view.show{display:block}
#map-canvas{position:absolute;inset:0;width:100%;height:100%;display:block;cursor:grab}
#map-canvas.grabbing{cursor:grabbing}
#map-canvas.hot{cursor:pointer}
.map-legend{
  position:absolute;top:16px;left:16px;background:#0b0a09d9;border:1px solid #2a2820;
  border-radius:12px;padding:12px 14px;backdrop-filter:blur(8px);z-index:6;
  max-width:230px;font-family:ui-monospace,SFMono-Regular,monospace;
}
.map-legend h4{font-size:.68rem;text-transform:uppercase;letter-spacing:.8px;color:#9db67c;margin-bottom:9px}
.map-legend .lg-row{display:flex;align-items:center;gap:8px;font-size:.75rem;color:#c9c5b9;margin:4px 0;cursor:pointer;opacity:.9;transition:opacity .15s}
.map-legend .lg-row:hover{opacity:1}
.map-legend .lg-row.off{opacity:.28;text-decoration:line-through}
.map-legend .lg-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;box-shadow:0 0 9px currentColor}
.map-counts{margin-top:9px;font-size:.68rem;color:#6e6a5e;line-height:1.6}
.map-controls{
  position:absolute;bottom:16px;left:16px;display:flex;flex-direction:column;gap:8px;z-index:6;
}
.map-controls .tool-group{align-items:center;background:#0b0a09d9;border-color:#2a2820}
.map-controls .mc-slider{display:flex;align-items:center;gap:8px;color:#8a8577;font-size:.72rem;padding:0 6px;font-family:ui-monospace,monospace}
.map-controls input[type=range]{width:120px;accent-color:#9db67c;height:4px}
.map-hint{
  position:absolute;top:16px;right:16px;background:#0b0a09d9;border:1px solid #2a2820;
  border-radius:10px;padding:9px 12px;font-size:.72rem;color:#8a8577;z-index:6;
  backdrop-filter:blur(8px);max-width:235px;line-height:1.55;
  font-family:ui-monospace,monospace;
}
.map-hint b{color:#9db67c;font-weight:600}
.map-tooltip{
  position:absolute;pointer-events:none;z-index:8;background:#12100cf0;
  border:1px solid #3d3a2e;border-radius:9px;padding:8px 11px;max-width:290px;
  font-size:.78rem;color:#e2ddd0;box-shadow:0 8px 26px rgba(0,0,0,.6);
  transform:translate(-50%,-118%);display:none;line-height:1.45;
  font-family:ui-monospace,monospace;
}
.map-tooltip.show{display:block}
.map-tooltip .mt-dir{font-size:.66rem;color:#9db67c;text-transform:uppercase;letter-spacing:.6px;margin-top:3px}
.map-empty{
  position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  flex-direction:column;gap:10px;color:#6e6a5e;text-align:center;padding:30px;
  font-family:ui-monospace,monospace;z-index:5;
}
/* tarjeta de acciones sobre una pieza del micelio: investigar desde el mapa */
.map-action{
  position:absolute;z-index:9;background:#12100cf2;border:1px solid #3d3a2e;
  border-radius:11px;padding:10px 12px;min-width:210px;max-width:280px;
  box-shadow:0 10px 32px rgba(0,0,0,.65);font-family:ui-monospace,monospace;
  display:none;
}
.map-action.show{display:block}
.map-action .ma-title{font-size:.78rem;color:#f4f1e6;line-height:1.35;margin-bottom:2px}
.map-action .ma-meta{font-size:.66rem;color:#9db67c;text-transform:uppercase;letter-spacing:.5px;margin-bottom:9px}
.map-action .ma-btns{display:flex;flex-wrap:wrap;gap:6px}
.map-action button{
  padding:5px 10px;border-radius:7px;border:1px solid #3d3a2e;background:#1a1712;
  color:#c9c5b9;cursor:pointer;font-size:.72rem;font-family:inherit;
  transition:all .15s;
}
.map-action button:hover{border-color:#9db67c;color:#e8f0d8}
.map-action button.ma-go{background:#9db67c;color:#0b0a09;border-color:#9db67c;font-weight:700}
.map-action button.ma-go:hover{background:#b1c893}

/* ── puertos mas grandes + estado conectando ── */
.port{width:16px;height:16px;border-width:2px;transition:transform .12s,background .15s,box-shadow .15s}
.port-out{right:-9px}
.port-in{left:-9px}
.port:hover{transform:translateY(-50%) scale(1.4);background:#9db67c;box-shadow:0 0 10px #9db67c99}
body.connecting .port-in{background:#9db67c;box-shadow:0 0 12px #9db67caa;animation:pulse 1.1s infinite}
body.connecting .node{cursor:crosshair}

/* ── iconos del toolbar ── */
.canvas-controls button svg{width:14px;height:14px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.view-toggle button svg{fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}

/* ── archivo (Files) como cards ── */
.file-search{
  width:100%;padding:8px 11px;border-radius:8px;border:1px solid #30363d;
  background:#0d1117;color:#e6edf3;font-size:.8rem;font-family:inherit;
}
.file-search:focus{outline:none;border-color:#9db67c}
.file-card{
  display:flex;align-items:center;gap:10px;padding:9px 10px;margin:6px 0;
  background:#0d1117;border:1px solid #21262d;border-radius:10px;cursor:pointer;
  transition:border-color .15s,transform .12s;
}
.file-card:hover{border-color:#9db67c66;transform:translateX(2px)}
.fc-dot{width:9px;height:9px;border-radius:50%;flex-shrink:0;box-shadow:0 0 7px currentColor}
.fc-body{overflow:hidden;flex:1}
.fc-title{font-size:.8rem;color:#e6edf3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.fc-meta{font-size:.68rem;color:#6e7681;font-family:ui-monospace,monospace;margin-top:2px}
.fc-chip{
  font-size:.62rem;padding:2px 7px;border-radius:99px;flex-shrink:0;
  text-transform:uppercase;letter-spacing:.4px;font-weight:600;
}

/* ── responsive ── */
@media(max-width:900px){
  .panel{width:100%;position:absolute;bottom:50px;right:0;top:auto;
    height:45vh;border-left:none;border-top:1px solid #30363d;z-index:60}
  .topbar-center{display:none}
}
"""

# ─────────────────────────────────────────────────────
#  JavaScript
# ─────────────────────────────────────────────────────

JS = r"""
// ── state ──
let workflow = ___WF_DATA___;
let selectedNode = null;
let dragging = null;
let dragOffset = {x: 0, y: 0};
let saveTimer = null;

const COLORS = {
  trigger: '#8957e5', groq: '#f0883e', cerebras: '#3fb950',
  azure: '#58a6ff', ollama: '#d29922', output: '#f778ba', nota: '#6e7681',
};
const ICONS = {
  trigger: '&#9654;', groq: 'G', cerebras: 'C', azure: 'A', ollama: 'O',
  output: '&#9678;', nota: '&#128221;',
};
const LABELS = {
  trigger: 'Trigger', groq: 'Groq', cerebras: 'Cerebras',
  azure: 'Azure', ollama: 'Ollama', output: 'Output',
};
const PROVIDERS = ['groq', 'cerebras', 'azure', 'ollama'];

// tipo real de un nodo (compat con datos viejos sin campo tipo)
function ntipo(id) {
  var nd = workflow.nodes[id] || {};
  if (nd.tipo) return nd.tipo;
  if (PROVIDERS.indexOf(id) >= 0) return 'modelo';
  if (id.indexOf('trigger') === 0) return 'trigger';
  if (id.indexOf('output') === 0) return 'output';
  if (id.indexOf('nota') === 0) return 'nota';
  return 'modelo';
}
function isModelo(id) { return ntipo(id) === 'modelo'; }

// estado de conexion manual: click en port-out arma, click en port-in cierra
var connectFrom = null;   // id del nodo origen mientras se traza una arista
var mousePos = {x: 0, y: 0};   // en coords de mundo (para la linea preview)

if (!Array.isArray(workflow.connections)) workflow.connections = [];

// ── safe escaping for HTML + template literals ──
function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    .replace(/`/g, '&#96;')
    .replace(/\$/g, '&#36;');
}

// ── color / label / icono por tipo (soporta multi trigger/output/nota) ──
function nodeColor(id) {
  var t = ntipo(id);
  if (t === 'modelo') return COLORS[id] || '#8b949e';
  return COLORS[t] || '#8b949e';
}
function nodeLabel(id) {
  var nd = workflow.nodes[id] || {};
  var t = ntipo(id);
  if (t === 'nota') return nd.titulo || 'Nota';
  if (t === 'modelo') return LABELS[id] || id;
  // trigger/output: numerar los extra (trigger, trigger2, ...)
  var base = LABELS[t] || t;
  var suf = id.replace(t, '');
  return suf ? base + ' ' + suf : base;
}
function nodeIcon(id) {
  var t = ntipo(id);
  if (t === 'modelo') return ICONS[id] || '?';
  return ICONS[t] || '?';
}
function nextId(prefix) {
  if (!workflow.nodes[prefix]) return prefix;   // primero sin sufijo
  var n = 2;
  while (workflow.nodes[prefix + n]) n++;
  return prefix + n;
}
// Agrega un nodo del tipo pedido. modelo NO se agrega (solo hay 4 fijos).
function addNode(tipo) {
  tipo = tipo || 'nota';
  var id = nextId(tipo);
  var base = {x: 140 + (Object.keys(workflow.nodes).length * 26) % 320,
              y: 360, active: true, tipo: tipo};
  if (tipo === 'nota') { base.titulo = 'Nota'; base.texto = ''; }
  workflow.nodes[id] = base;
  debouncedSave();
  renderNodes();
  drawConnections();
  selectNode(id);
  showToast('Nodo ' + tipo + ' agregado', 'success');
}
// Borra un nodo agregado (trigger/output extra o nota) y sus conexiones.
// Los nodos base (trigger, output, los 4 modelos) NO se borran, se apagan.
function deleteNode(id) {
  var t = ntipo(id);
  var esBase = (id === 'trigger' || id === 'output' || isModelo(id));
  if (!workflow.nodes[id] || esBase) {
    showToast('Ese nodo no se borra (apagalo con el toggle)', 'info');
    return;
  }
  delete workflow.nodes[id];
  workflow.connections = workflow.connections.filter(function(c) {
    return c.from !== id && c.to !== id;
  });
  selectedNode = null;
  debouncedSave();
  renderNodes();
  drawConnections();
  renderPanel();
  showToast('Nodo eliminado', 'info');
}

// ── render nodes ──
function renderNodes() {
  document.querySelectorAll('.node').forEach(function(n) { n.remove(); });
  var wrap = document.getElementById('canvas-world');
  var keys = Object.keys(workflow.nodes);
  for (var ki = 0; ki < keys.length; ki++) {
    var id = keys[ki];
    var nd = workflow.nodes[id];
    var el = document.createElement('div');
    var cls = 'node';
    if (nd.active === false) cls += ' inactive';
    if (selectedNode === id) cls += ' selected';
    el.className = cls;
    el.id = 'node-' + id;
    el.style.left = nd.x + 'px';
    el.style.top = nd.y + 'px';

    var t = ntipo(id);
    var color = nodeColor(id);
    var label = nodeLabel(id);
    var subtitle;
    if (t === 'nota') {
      subtitle = esc((nd.texto || '(nota vacía)').slice(0, 40));
    } else if (t === 'trigger') {
      subtitle = 'Entrada de tema';
    } else if (t === 'output') {
      subtitle = 'Recopila resultados';
    } else if (nd.model) {
      subtitle = esc(nd.model);
    } else {
      subtitle = 'No configurado';
    }

    // badge: los nodos modelo muestran su orden en el flujo; trigger/output
    // muestran su rol; nota nada
    var badgeText = '', badgeColor = '#238636';
    if (nd.active === false) {
      badgeText = 'OFF'; badgeColor = '#30363d';
    } else if (t === 'modelo') {
      badgeText = workflow.mode === 'pipeline' ? 'Pipe #' + nd.priority
                : (workflow.mode === 'single' ? 'Single' : 'Modelo');
      badgeColor = '#1f6feb';
    } else if (t === 'trigger') {
      badgeText = 'IN'; badgeColor = '#8957e5';
    } else if (t === 'output') {
      badgeText = 'OUT'; badgeColor = '#bc4b91';
    }

    var toggleClass = 'node-toggle' + (nd.active !== false ? ' on' : '');
    var priorityHtml = '';
    if (t === 'modelo' && workflow.mode !== 'single') {
      priorityHtml = '<div class="node-priority">' + esc(nd.priority) + '</div>';
    }
    var tempStr = (t === 'modelo' && nd.temperature !== undefined)
                  ? ' &middot; T:' + nd.temperature : '';

    el.innerHTML =
      '<button class="' + toggleClass + '" data-id="' + esc(id) + '" title="Activar/Desactivar"></button>' +
      priorityHtml +
      '<div class="node-header">' +
        '<div class="node-icon" style="background:' + color + '">' + nodeIcon(id) + '</div>' +
        '<div style="overflow:hidden">' +
          '<div class="node-title">' + esc(label) + '</div>' +
          '<div class="node-subtitle">' + subtitle + '</div>' +
        '</div>' +
      '</div>' +
      '<div class="node-body">' +
        (badgeText ? '<span class="node-badge" style="background:' + badgeColor + ';color:#fff">' + badgeText + '</span>' : '') +
        tempStr +
      '</div>' +
      // trigger no tiene entrada; output no tiene salida
      (t === 'trigger' ? '' : '<div class="port port-in" data-port="in" data-id="' + esc(id) + '"></div>') +
      (t === 'output' ? '' : '<div class="port port-out" data-port="out" data-id="' + esc(id) + '"></div>');

    wrap.appendChild(el);

    // closure for event handlers
    (function(nodeId, nodeEl) {
      nodeEl.addEventListener('mousedown', function(e) {
        if (e.target.classList.contains('node-toggle') || e.target.classList.contains('port')) return;
        dragging = nodeId;
        var nd = workflow.nodes[nodeId];
        dragStart = {mx: e.clientX, my: e.clientY, nx: nd.x, ny: nd.y};
        nodeEl.style.cursor = 'grabbing';
        nodeEl.style.zIndex = '50';
        selectNode(nodeId);
        e.stopPropagation();
        e.preventDefault();
      });
      nodeEl.addEventListener('click', function(e) {
        if (e.target.classList.contains('node-toggle') || e.target.classList.contains('port')) return;
        selectNode(nodeId);
      });
      // ── conexiones por puertos: ARRASTRA desde la salida y suelta en
      // una entrada (estilo n8n); tambien funciona en dos clicks. Las
      // entradas validas se encienden en verde mientras conectas. ──
      var pOut = nodeEl.querySelector('.port-out');
      if (pOut) pOut.addEventListener('mousedown', function(e) {
        e.stopPropagation(); e.preventDefault();
        connectFrom = nodeId;
        document.body.classList.add('connecting');
        mousePos.x = workflow.nodes[nodeId].x + 210;
        mousePos.y = workflow.nodes[nodeId].y + 40;
        drawConnections();
        showToast('Suelta (o click) sobre una entrada verde -- Esc cancela', 'info');
      });
      var pIn = nodeEl.querySelector('.port-in');
      if (pIn) pIn.addEventListener('mousedown', function(e) { e.stopPropagation(); });
      if (pIn) pIn.addEventListener('click', function(e) {
        e.stopPropagation();
        if (connectFrom) finishConnection(nodeId);
      });
    })(id, el);
  }

  // toggle buttons
  document.querySelectorAll('.node-toggle').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.stopPropagation();
      e.preventDefault();
      var nid = btn.dataset.id;
      workflow.nodes[nid].active = !workflow.nodes[nid].active;
      debouncedSave();
      renderNodes();
      drawConnections();
    });
  });
}

// ── SVG connections ──
function drawConnections() {
  var svg = document.getElementById('canvas-svg');
  svg.innerHTML = '';
  var ns = 'http://www.w3.org/2000/svg';

  // glow filter
  var defs = document.createElementNS(ns, 'defs');
  var filter = document.createElementNS(ns, 'filter');
  filter.setAttribute('id', 'glow');
  var blur = document.createElementNS(ns, 'feGaussianBlur');
  blur.setAttribute('stdDeviation', '3');
  blur.setAttribute('result', 'blur');
  filter.appendChild(blur);
  var merge = document.createElementNS(ns, 'feMerge');
  var mn1 = document.createElementNS(ns, 'feMergeNode');
  mn1.setAttribute('in', 'blur');
  var mn2 = document.createElementNS(ns, 'feMergeNode');
  mn2.setAttribute('in', 'SourceGraphic');
  merge.appendChild(mn1);
  merge.appendChild(mn2);
  filter.appendChild(merge);
  defs.appendChild(filter);
  svg.appendChild(defs);

  // Render de la lista real de conexiones. En modo grafo estas DIRIGEN
  // la ejecucion; en los otros son el dibujo (el preset del modo las fija).
  // Una arista con algun extremo inactivo se dibuja tenue (no corre).
  var conns = workflow.connections || [];
  for (var i = 0; i < conns.length; i++) {
    var c = conns[i];
    var fromEl = document.getElementById('node-' + c.from);
    var toEl = document.getElementById('node-' + c.to);
    if (!fromEl || !toEl) continue;
    var nf = workflow.nodes[c.from], nt2 = workflow.nodes[c.to];
    var apagada = (nf && nf.active === false) || (nt2 && nt2.active === false);
    drawPath(svg, ns, fromEl, toEl, nodeColor(c.from), !apagada, i, apagada);
  }

  // linea preview mientras se traza una conexion nueva
  if (connectFrom) {
    var fEl = document.getElementById('node-' + connectFrom);
    if (fEl) {
      var px = fEl.offsetLeft + fEl.offsetWidth;
      var py = fEl.offsetTop + fEl.offsetHeight / 2;
      var pv = document.createElementNS(ns, 'path');
      pv.setAttribute('d', 'M' + px + ',' + py + ' L' + mousePos.x + ',' + mousePos.y);
      pv.setAttribute('stroke', '#58a6ff');
      pv.setAttribute('stroke-width', '2');
      pv.setAttribute('stroke-dasharray', '5 4');
      pv.setAttribute('fill', 'none');
      svg.appendChild(pv);
    }
  }
}

// alta de conexion validada: sin auto-lazo, sin duplicado, sin salir de
// output ni entrar a trigger (esos no tienen ese puerto)
function addConnection(from, to) {
  if (!from || !to || from === to) { showToast('Conexion invalida', 'error'); return; }
  if (ntipo(to) === 'trigger') { showToast('Un trigger no recibe entrada', 'error'); return; }
  if (ntipo(from) === 'output') { showToast('Un output no tiene salida', 'error'); return; }
  var dup = workflow.connections.some(function(c) { return c.from === from && c.to === to; });
  if (dup) { showToast('Esa conexion ya existe', 'info'); return; }
  workflow.connections.push({from: from, to: to});
  debouncedSave();
  drawConnections();
  showToast('Conectado: ' + from + ' -> ' + to, 'success');
}

function finishConnection(toId) {
  addConnection(connectFrom, toId);
  connectFrom = null;
  document.body.classList.remove('connecting');
  drawConnections();
}

function removeConnection(idx) {
  if (idx < 0 || idx >= workflow.connections.length) return;
  var c = workflow.connections[idx];
  workflow.connections.splice(idx, 1);
  debouncedSave();
  drawConnections();
  showToast('Conexion quitada: ' + c.from + ' -> ' + c.to, 'info');
}

function drawPath(svg, ns, fromEl, toEl, color, animated, connIdx, apagada) {
  if (!fromEl || !toEl) return;
  var x1 = fromEl.offsetLeft + fromEl.offsetWidth;
  var y1 = fromEl.offsetTop + fromEl.offsetHeight / 2;
  var x2 = toEl.offsetLeft;
  var y2 = toEl.offsetTop + toEl.offsetHeight / 2;
  var dx = Math.max(Math.abs(x2 - x1) * 0.5, 40);

  var d = 'M' + x1 + ',' + y1 + ' C' + (x1 + dx) + ',' + y1 + ' ' + (x2 - dx) + ',' + y2 + ' ' + x2 + ',' + y2;

  // glow background
  var pathBg = document.createElementNS(ns, 'path');
  pathBg.setAttribute('d', d);
  pathBg.setAttribute('fill', 'none');
  pathBg.setAttribute('stroke', color);
  pathBg.setAttribute('stroke-width', '5');
  pathBg.setAttribute('opacity', apagada ? '0.04' : '0.1');
  pathBg.setAttribute('filter', 'url(#glow)');
  svg.appendChild(pathBg);

  // main line
  var path = document.createElementNS(ns, 'path');
  path.setAttribute('d', d);
  path.setAttribute('fill', 'none');
  path.setAttribute('stroke', color);
  path.setAttribute('stroke-width', '2');
  path.setAttribute('stroke-linecap', 'round');
  path.setAttribute('opacity', apagada ? '0.3' : '1');
  if (animated) path.setAttribute('class', 'conn-animated');
  svg.appendChild(path);

  // arrowhead
  var arrow = document.createElementNS(ns, 'polygon');
  arrow.setAttribute('points', (x2 - 2) + ',' + (y2 - 5) + ' ' + (x2 + 7) + ',' + y2 + ' ' + (x2 - 2) + ',' + (y2 + 5));
  arrow.setAttribute('fill', color);
  arrow.setAttribute('opacity', apagada ? '0.3' : '1');
  svg.appendChild(arrow);

  // hit area clickable para borrar la conexion (solo si tiene indice)
  if (connIdx !== undefined && connIdx !== null && connIdx >= 0) {
    var hit = document.createElementNS(ns, 'path');
    hit.setAttribute('d', d);
    hit.setAttribute('fill', 'none');
    hit.setAttribute('stroke', 'transparent');
    hit.setAttribute('stroke-width', '14');
    hit.style.pointerEvents = 'stroke';
    hit.style.cursor = 'pointer';
    hit.addEventListener('click', function(e) {
      e.stopPropagation();
      removeConnection(connIdx);
    });
    var tt = document.createElementNS(ns, 'title');
    tt.textContent = 'Click para quitar esta conexion';
    hit.appendChild(tt);
    svg.appendChild(hit);
  }
}

// ── node selection + panel ──
function selectNode(id) {
  selectedNode = id;
  document.querySelectorAll('.node').forEach(function(n) { n.classList.remove('selected'); });
  var el = document.getElementById('node-' + id);
  if (el) el.classList.add('selected');
  renderPanel();
}

function renderPanel() {
  var panelBody = document.getElementById('panel-body');
  if (!selectedNode || !workflow.nodes[selectedNode]) {
    panelBody.innerHTML = '<div class="panel-section"><p style="color:#8b949e;font-size:.85rem">Click en un nodo del canvas para editarlo</p></div>';
    return;
  }
  var id = selectedNode;
  var nd = workflow.nodes[id];
  var t = ntipo(id);
  // los nodos extra (trigger2/output2/nota) se pueden borrar; los base no
  var esExtra = (id !== 'trigger' && id !== 'output' && !isModelo(id));

  if (t === 'nota') {
    panelBody.innerHTML =
      '<div class="panel-section">' +
        '<h3>Nodo nota</h3>' +
        '<div class="field"><label>Título</label>' +
          '<input type="text" id="cfg-titulo" value="' + esc(nd.titulo || '') + '"></div>' +
        '<div class="field"><label>Texto / instrucción</label>' +
          '<textarea id="cfg-nota" placeholder="Anotación del flujo...">' + esc(nd.texto || '') + '</textarea></div>' +
        '<div style="display:flex;gap:8px;margin-top:14px">' +
          '<button class="btn btn-primary" onclick="saveNota()">&#128190; Guardar</button>' +
          '<button class="btn btn-secondary" onclick="deleteNode(\'' + esc(id) + '\')">&#128465; Eliminar</button>' +
        '</div>' +
      '</div>';
    return;
  }

  if (t === 'trigger' || t === 'output') {
    panelBody.innerHTML =
      '<div class="panel-section">' +
        '<h3>Nodo: ' + esc(nodeLabel(id)) + '</h3>' +
        '<p style="color:#8b949e;font-size:.82rem">' +
          (t === 'trigger'
            ? 'Entrada del tema. Puedes tener varias entradas; cada modelo conectado recibe el tema.'
            : 'Recopila los resultados de sus predecesores. Puedes tener varias salidas.') +
        '</p>' +
        '<div style="margin-top:12px">' +
          '<span style="font-size:.75rem;color:#8b949e">Posición</span>' +
          '<div style="font-size:.82rem;margin-top:4px">x: ' + nd.x + ' &middot; y: ' + nd.y + '</div>' +
        '</div>' +
        (esExtra
          ? '<div style="margin-top:14px"><button class="btn btn-secondary" onclick="deleteNode(\'' + esc(id) + '\')">&#128465; Eliminar</button></div>'
          : '<p style="color:#6e7681;font-size:.75rem;margin-top:12px">Nodo base: se apaga con el toggle, no se borra.</p>') +
      '</div>';
    return;
  }

  var modelEnvKey = ({groq:'GROQ_MODEL',cerebras:'CEREBRAS_MODEL',azure:'AZURE_DEPLOYMENT',ollama:'OLLAMA_MODEL'})[id] || '';
  var envVal = ENV_DATA[modelEnvKey] || '';

  panelBody.innerHTML =
    '<div class="panel-section">' +
      '<h3>Modelo: ' + esc(LABELS[id]) + '</h3>' +
      '<div class="field">' +
        '<label>Nombre del modelo / deployment</label>' +
        '<input type="text" id="cfg-model" value="' + esc(nd.model || envVal) + '" placeholder="' + esc(envVal || 'model-name') + '">' +
      '</div>' +
      '<div class="field">' +
        '<label>Temperatura</label>' +
        '<div class="range-wrap">' +
          '<input type="range" id="cfg-temp" min="0" max="2" step="0.05" value="' + nd.temperature + '" oninput="document.getElementById(\'temp-val\').textContent=this.value">' +
          '<span class="range-val" id="temp-val">' + nd.temperature + '</span>' +
        '</div>' +
      '</div>' +
      '<div class="field">' +
        '<label>Max tokens</label>' +
        '<input type="number" id="cfg-maxtok" value="' + nd.max_tokens + '" min="256" max="128000" step="256">' +
      '</div>' +
      '<div class="field">' +
        '<label>System prompt</label>' +
        '<textarea id="cfg-sysprompt" placeholder="Eres un asistente de investigación...">' + esc(nd.system_prompt || '') + '</textarea>' +
      '</div>' +
      '<div class="field">' +
        '<label>Prioridad (orden en el flujo)</label>' +
        '<input type="number" id="cfg-priority" value="' + nd.priority + '" min="1" max="10">' +
      '</div>' +
      '<div style="display:flex;gap:8px;margin-top:14px">' +
        '<button class="btn btn-primary" onclick="saveNodeConfig()">&#128190; Guardar</button>' +
        '<button class="btn btn-secondary" onclick="resetNode(\'' + esc(id) + '\')">&#8634; Reset</button>' +
      '</div>' +
    '</div>' +
    '<div class="panel-section">' +
      '<h3>Env actual</h3>' +
      '<div style="font-size:.78rem;color:#8b949e"><code>' + esc(modelEnvKey) + '=' + esc(envVal) + '</code></div>' +
    '</div>';
}

function saveNodeConfig() {
  var nd = workflow.nodes[selectedNode];
  if (!nd) return;
  nd.model = document.getElementById('cfg-model').value.trim();
  nd.temperature = parseFloat(document.getElementById('cfg-temp').value) || 0.7;
  nd.max_tokens = parseInt(document.getElementById('cfg-maxtok').value) || 4096;
  nd.system_prompt = document.getElementById('cfg-sysprompt').value;
  nd.priority = parseInt(document.getElementById('cfg-priority').value) || 1;
  debouncedSave();
  renderNodes();
  drawConnections();
  showToast('Configuración guardada', 'success');
}

function saveNota() {
  var nd = workflow.nodes[selectedNode];
  if (!nd || nd.tipo !== 'nota') return;
  nd.titulo = document.getElementById('cfg-titulo').value.trim() || 'Nota';
  nd.texto = document.getElementById('cfg-nota').value;
  debouncedSave();
  renderNodes();
  showToast('Nota guardada', 'success');
}

function resetNode(id) {
  var def = DEFAULT_WF.nodes[id];
  if (def) {
    Object.keys(def).forEach(function(k) { workflow.nodes[id][k] = def[k]; });
    debouncedSave();
    renderNodes();
    drawConnections();
    renderPanel();
    showToast('Nodo reseteado', 'info');
  }
}

// ── view (pan/zoom) ──
var view = {x: 0, y: 0, k: 1};
var panning = null;   // {mx, my, vx, vy} cuando se arrastra el fondo
var dragStart = null; // {mx, my, nx, ny} cuando se arrastra un nodo

function applyView() {
  var world = document.getElementById('canvas-world');
  world.style.transform = 'translate(' + view.x + 'px,' + view.y + 'px) scale(' + view.k + ')';
  var zl = document.getElementById('zoom-level');
  if (zl) zl.textContent = Math.round(view.k * 100) + '%';
}
function zoomBy(delta) {
  var wrap = document.getElementById('canvas-wrap');
  var r = wrap.getBoundingClientRect();
  zoomAround(r.width / 2, r.height / 2, view.k + delta);
}
function zoomAround(px, py, nk) {
  nk = Math.max(0.3, Math.min(2, nk));
  // mantener el punto (px,py) fijo en pantalla al cambiar el zoom
  var wx = (px - view.x) / view.k;
  var wy = (py - view.y) / view.k;
  view.k = nk;
  view.x = px - wx * view.k;
  view.y = py - wy * view.k;
  applyView();
}
function zoomReset() { view.k = 1; applyView(); }
function centerView() { view.x = 0; view.y = 0; applyView(); }

// ── drag handling (nodos y paneo del fondo) ──
document.addEventListener('mousemove', function(e) {
  if (dragging) {
    var dx = (e.clientX - dragStart.mx) / view.k;
    var dy = (e.clientY - dragStart.my) / view.k;
    var x = Math.max(0, Math.round(dragStart.nx + dx));
    var y = Math.max(0, Math.round(dragStart.ny + dy));
    workflow.nodes[dragging].x = x;
    workflow.nodes[dragging].y = y;
    var el = document.getElementById('node-' + dragging);
    if (el) { el.style.left = x + 'px'; el.style.top = y + 'px'; }
    drawConnections();
  } else if (panning) {
    view.x = panning.vx + (e.clientX - panning.mx);
    view.y = panning.vy + (e.clientY - panning.my);
    applyView();
  } else if (connectFrom) {
    // posicion del mouse en coords de mundo para la linea preview
    var wrap = document.getElementById('canvas-wrap');
    var r = wrap.getBoundingClientRect();
    mousePos.x = (e.clientX - r.left - view.x) / view.k;
    mousePos.y = (e.clientY - r.top - view.y) / view.k;
    drawConnections();
  }
});

// paneo: arrastrar el fondo vacio del canvas
document.getElementById('canvas-wrap').addEventListener('mousedown', function(e) {
  if (e.target.id !== 'canvas-wrap' && e.target.id !== 'canvas-world'
      && e.target.id !== 'canvas-svg') return;
  // click en vacio cancela una conexion a medio trazar
  if (connectFrom) {
    connectFrom = null;
    document.body.classList.remove('connecting');
    drawConnections();
    return;
  }
  panning = {mx: e.clientX, my: e.clientY, vx: view.x, vy: view.y};
  this.classList.add('panning');
});
// zoom con la rueda sobre el cursor
document.getElementById('canvas-wrap').addEventListener('wheel', function(e) {
  e.preventDefault();
  var r = this.getBoundingClientRect();
  zoomAround(e.clientX - r.left, e.clientY - r.top,
             view.k + (e.deltaY < 0 ? 0.1 : -0.1));
}, {passive: false});

document.addEventListener('mouseup', function(e) {
  if (dragging) {
    var el = document.getElementById('node-' + dragging);
    if (el) el.style.zIndex = '10';
    debouncedSave();
    dragging = null;
    dragStart = null;
  }
  if (panning) {
    panning = null;
    var w = document.getElementById('canvas-wrap');
    if (w) w.classList.remove('panning');
  }
  // drag-to-connect: soltar sobre un puerto de entrada cierra la conexion
  if (connectFrom) {
    var target = document.elementFromPoint(e.clientX, e.clientY);
    if (target && target.classList && target.classList.contains('port-in')) {
      finishConnection(target.dataset.id);
    }
    // si suelta en otro lado, queda armado (modo dos-clicks); Esc cancela
  }
});

// ── debounced save ──
function debouncedSave() {
  if (saveTimer) clearTimeout(saveTimer);
  saveTimer = setTimeout(function() { save(); }, 400);
}

function save() {
  fetch('/api/workflow', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(workflow),
  })
  .then(function(r) {
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  })
  .catch(function(err) {
    console.error('save error:', err);
    showToast('Error al guardar', 'error');
  });
}

// ── mode switching ──
// canvas mode -> script backend real. grafo = ejecutor real (grafo.py):
// las conexiones dibujadas DIRIGEN el orden (no hay preset que las pise).
var MODE_TO_BACKEND = {single: 'research', pipeline: 'cadena',
                      discussion: 'panel', adversarial: 'refutar',
                      grafo: 'grafo'};

// ids de nodos activos por tipo, modelos ordenados por prioridad
function activosPorTipo() {
  var trigs = [], outs = [], modelos = [];
  Object.keys(workflow.nodes).forEach(function(id) {
    var nd = workflow.nodes[id];
    if (nd.active === false) return;
    var t = ntipo(id);
    if (t === 'trigger') trigs.push(id);
    else if (t === 'output') outs.push(id);
    else if (t === 'modelo') modelos.push(id);
  });
  modelos.sort(function(a, b) {
    return (workflow.nodes[a].priority || 0) - (workflow.nodes[b].priority || 0);
  });
  return {trigs: trigs, outs: outs, modelos: modelos};
}

// Genera las conexiones de un preset. Soporta multiples trigger/output.
// discussion = comite (todos convergen al output = correlacion).
// adversarial = proponente -> refutadores -> juez.
function presetConnections(mode) {
  var a = activosPorTipo();
  var C = [], i;
  function link(f, t) { C.push({from: f, to: t}); }
  if (!a.modelos.length || !a.trigs.length || !a.outs.length) return C;
  var M = a.modelos;
  if (mode === 'single') {
    a.trigs.forEach(function(tr) { link(tr, M[0]); });
    a.outs.forEach(function(o) { link(M[0], o); });
  } else if (mode === 'pipeline') {
    a.trigs.forEach(function(tr) { link(tr, M[0]); });
    for (i = 0; i < M.length - 1; i++) link(M[i], M[i + 1]);
    a.outs.forEach(function(o) { link(M[M.length - 1], o); });
  } else if (mode === 'discussion') {
    // comite: cada trigger alimenta a todos, todos convergen al output
    M.forEach(function(m) {
      a.trigs.forEach(function(tr) { link(tr, m); });
      a.outs.forEach(function(o) { link(m, o); });
    });
  } else if (mode === 'adversarial') {
    var prop = M[0], juez = M[M.length - 1];
    var refs = M.slice(1, M.length - 1);
    a.trigs.forEach(function(tr) { link(tr, prop); });
    if (M.length === 1) {           // 1 modelo: propone y juzga
      a.outs.forEach(function(o) { link(prop, o); });
    } else if (refs.length === 0) { // 2 modelos: proponente -> juez
      link(prop, juez);
      a.outs.forEach(function(o) { link(juez, o); });
    } else {
      refs.forEach(function(r) { link(prop, r); link(r, juez); });
      a.outs.forEach(function(o) { link(juez, o); });
    }
  }
  return C;
}

function setMode(mode) {
  workflow.mode = mode;
  document.querySelectorAll('.mode-btn').forEach(function(b) {
    b.classList.toggle('active', b.dataset.mode === mode);
  });
  var sel = document.getElementById('run-modo');
  if (sel && MODE_TO_BACKEND[mode]) sel.value = MODE_TO_BACKEND[mode];
  // grafo = custom: respeta las conexiones dibujadas a mano.
  // el resto regenera su topologia (asi el dibujo SIEMPRE matchea el modo).
  if (mode !== 'grafo') workflow.connections = presetConnections(mode);
  debouncedSave();
  renderNodes();
  drawConnections();
  var msg = mode === 'grafo'
    ? 'Modo grafo: las conexiones que dibujes dirigen la ejecucion'
    : 'Modo: ' + mode;
  showToast(msg, 'info');
}

// ── validacion de flujo extremo (espejo de grafo.py, pre-check en la UI) ──
var MAXNODOS = 12, MAXFAN = 6;
function validarGrafo() {
  var a = activosPorTipo();
  var errs = [];
  if (!a.trigs.length) errs.push('Falta un nodo de entrada (trigger) activo.');
  if (!a.outs.length) errs.push('Falta un nodo de salida (output) activo.');
  if (!a.modelos.length) errs.push('No hay ningun modelo activo.');
  if (a.modelos.length > MAXNODOS) errs.push('Demasiados modelos (' + a.modelos.length + ' > ' + MAXNODOS + ').');

  var activos = {};
  a.trigs.concat(a.outs, a.modelos).forEach(function(id) { activos[id] = true; });
  var edges = (workflow.connections || []).filter(function(c) {
    return activos[c.from] && activos[c.to];
  });
  // fan-out / fan-in
  var fout = {}, fin = {}, adj = {}, indeg = {}, nodes = {};
  edges.forEach(function(c) {
    fout[c.from] = (fout[c.from] || 0) + 1;
    fin[c.to] = (fin[c.to] || 0) + 1;
    (adj[c.from] = adj[c.from] || []).push(c.to);
    indeg[c.to] = (indeg[c.to] || 0) + 1;
    nodes[c.from] = nodes[c.to] = true;
  });
  Object.keys(fout).forEach(function(k) { if (fout[k] > MAXFAN) errs.push("Nodo '" + k + "' con fan-out extremo (" + fout[k] + ')'); });
  Object.keys(fin).forEach(function(k) { if (fin[k] > MAXFAN) errs.push("Nodo '" + k + "' con fan-in extremo (" + fin[k] + ')'); });
  // ciclo (Kahn)
  var idg = {}; Object.keys(nodes).forEach(function(k) { idg[k] = indeg[k] || 0; });
  var cola = Object.keys(nodes).filter(function(k) { return !idg[k]; });
  var visto = 0;
  while (cola.length) {
    var n = cola.pop(); visto++;
    (adj[n] || []).forEach(function(m) { if (--idg[m] === 0) cola.push(m); });
  }
  if (visto < Object.keys(nodes).length) errs.push('El grafo tiene un ciclo (quita alguna conexion).');
  // alcanzabilidad trigger -> output + huerfanos
  if (a.trigs.length && a.outs.length && !errs.length) {
    var seen = {}, stack = a.trigs.slice();
    a.trigs.forEach(function(t) { seen[t] = true; });
    while (stack.length) {
      var x = stack.pop();
      (adj[x] || []).forEach(function(m) { if (!seen[m]) { seen[m] = true; stack.push(m); } });
    }
    if (!a.outs.some(function(o) { return seen[o]; })) errs.push('Ningun output es alcanzable desde un trigger.');
    var huer = a.modelos.filter(function(m) { return !seen[m]; });
    if (huer.length) errs.push('Modelos sin conexion desde la entrada: ' + huer.join(', ') + '.');
  }
  return errs;
}

// ── canvas controls ──
// Encaja TODO en la vista ajustando zoom/pan (no mueve los nodos).
function fitToView() {
  var nodes = workflow.nodes;
  var keys = Object.keys(nodes);
  if (keys.length === 0) return;
  var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  keys.forEach(function(k) {
    var nd = nodes[k];
    if (nd.x < minX) minX = nd.x;
    if (nd.y < minY) minY = nd.y;
    if (nd.x + 220 > maxX) maxX = nd.x + 220;
    if (nd.y + 120 > maxY) maxY = nd.y + 120;
  });
  var wrap = document.getElementById('canvas-wrap');
  var wW = wrap.clientWidth, wH = wrap.clientHeight;
  var bw = maxX - minX, bh = maxY - minY;
  var k = Math.min(2, Math.max(0.3, Math.min((wW - 60) / bw, (wH - 60) / bh)));
  view.k = k;
  view.x = (wW - bw * k) / 2 - minX * k;
  view.y = (wH - bh * k) / 2 - minY * k;
  applyView();
  showToast('Vista ajustada', 'info');
}

// Auto-organiza: trigger a la izquierda, modelos en columna por
// prioridad, notas abajo, output a la derecha.
function organizar() {
  var nodes = workflow.nodes;
  var modelos = Object.keys(nodes).filter(function(k) {
    var nd = nodes[k];
    return k !== 'trigger' && k !== 'output' && nd.tipo !== 'nota';
  }).sort(function(a, b) {
    return (nodes[a].priority || 0) - (nodes[b].priority || 0);
  });
  var notas = Object.keys(nodes).filter(function(k) {
    return nodes[k].tipo === 'nota';
  });
  if (nodes.trigger) { nodes.trigger.x = 60; nodes.trigger.y = 260; }
  modelos.forEach(function(k, i) { nodes[k].x = 380; nodes[k].y = 60 + i * 140; });
  if (nodes.output) { nodes.output.x = 720; nodes.output.y = 260; }
  notas.forEach(function(k, i) { nodes[k].x = 60 + i * 260; nodes[k].y = 520; });
  debouncedSave();
  renderNodes();
  drawConnections();
  fitToView();
  showToast('Nodos organizados', 'success');
}

function resetLayout() {
  var def = DEFAULT_WF;
  Object.keys(def.nodes).forEach(function(k) {
    if (workflow.nodes[k]) {
      workflow.nodes[k].x = def.nodes[k].x;
      workflow.nodes[k].y = def.nodes[k].y;
    }
  });
  debouncedSave();
  renderNodes();
  drawConnections();
  showToast('Layout reseteado', 'info');
}

// ── toast ──
function showToast(msg, type) {
  var t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast show ' + (type || 'info');
  setTimeout(function() { t.className = 'toast'; }, 2500);
}

// ── modal: visualizar resultado DENTRO de la app (no texto plano aparte) ──
function mdToHtml(src) {
  var lines = src.split('\n');
  var out = [], inList = false;
  function inline(s) {
    s = esc(s);
    s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    s = s.replace(/\*(.+?)\*/g, '<em>$1</em>');
    s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    return s;
  }
  lines.forEach(function(line) {
    var m = line.match(/^(#{1,3})\s+(.*)/);
    if (m) {
      if (inList) { out.push('</ul>'); inList = false; }
      var lvl = m[1].length;
      out.push('<h' + lvl + '>' + inline(m[2]) + '</h' + lvl + '>');
      return;
    }
    if (/^[-*]\s+/.test(line)) {
      if (!inList) { out.push('<ul>'); inList = true; }
      out.push('<li>' + inline(line.replace(/^[-*]\s+/, '')) + '</li>');
      return;
    }
    if (inList) { out.push('</ul>'); inList = false; }
    if (line.trim() === '') return;
    out.push('<p>' + inline(line) + '</p>');
  });
  if (inList) out.push('</ul>');
  return out.join('\n');
}

function abrirModal(titulo, htmlBody, esError) {
  document.getElementById('view-modal-title').textContent = titulo;
  var body = document.getElementById('view-modal-body');
  body.innerHTML = htmlBody;
  body.className = 'view-box-body' + (esError ? ' error-view' : '');
  document.getElementById('view-modal').classList.add('show');
}
function cerrarModal() {
  document.getElementById('view-modal').classList.remove('show');
}
function verArchivo(dir, nombreEnc) {
  var nombre = decodeURIComponent(nombreEnc);
  fetch('/f?d=' + dir + '&n=' + nombreEnc)
    .then(function(r) { return r.text(); })
    .then(function(txt) { abrirModal(nombre, mdToHtml(txt), false); })
    .catch(function() { showToast('No se pudo cargar el archivo', 'error'); });
}
function verError(temaEnc, errorEnc) {
  var tema = decodeURIComponent(temaEnc);
  var err = errorEnc ? decodeURIComponent(errorEnc) : '(sin detalle)';
  document.getElementById('view-modal-title').textContent = 'Error: ' + tema;
  var body = document.getElementById('view-modal-body');
  body.className = 'view-box-body error-view';
  body.innerHTML = '<pre>' + esc(err) + '</pre>' +
    '<div style="margin-top:14px"><button class="btn btn-primary" ' +
    'onclick="repararError(\'' + temaEnc + '\',\'' + errorEnc + '\')">' +
    '&#128295; Reparar (modelo capaz diagnostica)</button></div>' +
    '<div id="repair-out" style="margin-top:14px"></div>';
  document.getElementById('view-modal').classList.add('show');
}

function repararError(temaEnc, errorEnc) {
  var out = document.getElementById('repair-out');
  out.innerHTML = '<em style="color:#8b949e">Diagnosticando con el modelo capaz...</em>';
  fetch('/api/repair', {
    method: 'POST',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: 'tema=' + temaEnc + '&error=' + errorEnc,
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    if (data.ok) {
      out.className = '';
      out.innerHTML = '<div style="background:#0d1117;border:1px solid #30363d;' +
        'border-radius:8px;padding:12px;color:#c9d1d9;font-family:system-ui">' +
        mdToHtml(data.diagnostico) + '</div>';
    } else {
      out.innerHTML = '<span style="color:#ff7b72">Fallo diagnostico: ' +
        esc(data.error || '') + '</span>';
    }
  })
  .catch(function() { out.innerHTML = '<span style="color:#ff7b72">Error de conexión</span>'; });
}

// ── reanudar un job PAUSADO (checkpoint humano) ──
function reanudar(jobIdEnc, accion) {
  var texto = '';
  if (accion === 'editar') {
    texto = prompt('Nueva consulta:');
    if (texto === null) return;
  }
  fetch('/api/reanudar', {
    method: 'POST',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: 'job_id=' + jobIdEnc + '&accion=' + accion + '&texto=' + encodeURIComponent(texto || ''),
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    if (data.ok) {
      refreshJobs();
    } else {
      alert(data.error || 'error');
    }
  })
  .catch(function() { alert('Error de conexión'); });
}

// ── tab switching ──
function switchTab(tabId) {
  document.querySelectorAll('.tab').forEach(function(t) {
    t.classList.toggle('active', t.dataset.tab === tabId);
  });
  document.querySelectorAll('.tab-content').forEach(function(c) {
    c.classList.toggle('active', c.id === 'tab-' + tabId);
  });
}

// ── auto-refresh jobs ──
function refreshJobs() {
  fetch('/api/jobs')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var list = document.getElementById('job-list');
      if (!list) return;
      if (data.length === 0) {
        list.innerHTML = '<li class="job-item" style="color:#8b949e">Sin jobs</li>';
        return;
      }
      list.innerHTML = data.map(function(j) {
        var dotClass = 'job-dot ' + (j.estado || '').toLowerCase().replace(/\s+/g, '-');
        var link = '';
        if (j.path) {
          var MODO_DIR_JS = {research: 'informes', panel: 'paneles',
                            cadena: 'cadenas', refutar: 'refutaciones',
                            corpus: 'correlaciones', grafo: 'grafos',
                            memoria: 'memoria'};
          var dir = MODO_DIR_JS[j.modo] || 'informes';
          link = '<a href="#" onclick="verArchivo(\'' + dir + '\',\'' +
            encodeURIComponent(j.path) + '\');return false;" style="color:#58a6ff;font-size:.75rem">ver</a>';
        } else if (j.estado === 'FALLO') {
          link = '<a href="#" onclick="verError(\'' + encodeURIComponent(j.tema) + '\',\'' +
            encodeURIComponent(j.error || '') + '\');return false;" style="color:#ff7b72;font-size:.75rem">error</a>';
        } else if (j.estado === 'PAUSADO') {
          var jidEnc = encodeURIComponent(j.job_id || '');
          var motivoEsc = esc((j.error || '').slice(0, 160));
          link = '<span style="color:#e0a458;font-size:.72rem;max-width:140px;' +
            'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:inline-block" ' +
            'title="' + motivoEsc + '">' + motivoEsc + '</span> ' +
            '<a href="#" onclick="reanudar(\'' + jidEnc + '\',\'reintentar\');return false;" ' +
            'style="color:#58a6ff;font-size:.72rem">reintentar</a> ' +
            '<a href="#" onclick="reanudar(\'' + jidEnc + '\',\'editar\');return false;" ' +
            'style="color:#58a6ff;font-size:.72rem">editar</a> ' +
            '<a href="#" onclick="reanudar(\'' + jidEnc + '\',\'saltar\');return false;" ' +
            'style="color:#58a6ff;font-size:.72rem">saltar</a> ' +
            '<a href="#" onclick="reanudar(\'' + jidEnc + '\',\'abortar\');return false;" ' +
            'style="color:#ff7b72;font-size:.72rem">abortar</a>';
        }
        return '<li class="job-item">' +
          '<span class="' + dotClass + '"></span>' +
          '<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' + esc(j.tema) + '</span>' +
          '<span style="color:#8b949e;font-size:.72rem">' + esc(j.t) + ' &middot; ' + esc(j.estado) + '</span>' +
          link +
          '</li>';
      }).join('');
    })
    .catch(function() {});
}

// ── memoria del departamento (RAG local) ──
function refreshMemStats() {
  fetch('/api/memoria/stats')
    .then(function(r) { return r.json(); })
    .then(function(d) {
      var el = document.getElementById('mem-count');
      if (el) el.textContent = (d.chunks || 0) + ' frag';
    })
    .catch(function() {});
}
function reindexarMemoria() {
  showToast('Reindexando memoria...', 'info');
  fetch('/api/memoria/index', {
    method: 'POST',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: '',
  })
  .then(function(r) { return r.json(); })
  .then(function(d) {
    showToast(d.started ? 'Indexando en background...' : 'Ya hay un reindex corriendo', 'info');
    var n = 0;
    var iv = setInterval(function() {
      refreshMemStats();
      if (++n >= 12) clearInterval(iv);
    }, 2500);
  })
  .catch(function() { showToast('Error al reindexar', 'error'); });
}

// ── keyboard shortcuts ──
document.addEventListener('keydown', function(e) {
  // Escape: cancela conexion/puente a medio trazar; si no, deselecciona
  if (e.key === 'Escape') {
    if (MAPA.bridge || MAPA.sel) {
      MAPA.bridge = null;
      mapCloseActions();
    } else if (connectFrom) {
      connectFrom = null;
      document.body.classList.remove('connecting');
      drawConnections();
    } else selectNode(null);
  }
  // Delete: apaga el nodo seleccionado (o lo borra si es nota/extra)
  if (e.key === 'Delete' && selectedNode && selectedNode !== 'trigger' && selectedNode !== 'output') {
    var nd = workflow.nodes[selectedNode];
    if (nd) {
      nd.active = !nd.active;
      debouncedSave();
      renderNodes();
      drawConnections();
      renderPanel();
    }
  }
});

// ── validar el grafo antes de correr (feedback instantaneo) ──
// Muestra los problemas en el modal; devuelve true si esta sano.
function chequearGrafo(bloquea) {
  var errs = validarGrafo();
  if (errs.length) {
    var html = '<h3>Flujo con problemas</h3><ul>' +
      errs.map(function(e) { return '<li>' + esc(e) + '</li>'; }).join('') + '</ul>' +
      '<p style="color:#8b949e;margin-top:8px">' +
      (bloquea ? 'Corrige el grafo antes de correr en modo grafo.'
               : 'Aviso: el modo actual usa su propio script, pero el dibujo tiene estos problemas.') +
      '</p>';
    abrirModal('Validacion del grafo', html, false);
  }
  return errs.length === 0;
}

// ── filtro del archivo (Files) ──
function filtrarArchivo(q) {
  q = (q || '').toLowerCase().trim();
  document.querySelectorAll('#archivo-list .file-card').forEach(function(li) {
    li.style.display = (!q || (li.dataset.q || '').indexOf(q) >= 0) ? '' : 'none';
  });
}

// ══════════════════════════════════════════════════════════════════════
//  MICELIO -- mapa semantico del archivo (canvas 2D, fisica propia).
//  Nodo = pieza de research. Filamento = afinidad entre embeddings.
//  El organismo crece y se remodela con cada research nuevo.
// ══════════════════════════════════════════════════════════════════════
var DIR_COLORS = {informes:'#9db67c',paneles:'#d4a259',cadenas:'#7ba6a3',
                 refutaciones:'#c46d5e',correlaciones:'#b48ead',
                 grafos:'#93a8c7',memoria:'#e0c58f'};
var MAPA = {
  nodes: [], edges: [], byId: {}, loaded: false, running: false,
  view: {x: 0, y: 0, k: 1}, umbral: 0.55, dirOff: {},
  hover: null, dragN: null, panM: null, downAt: null,
  sel: null, bridge: null,
  alpha: 0, t: 0, raf: 0,
};

function setView(v) {
  var mv = document.getElementById('map-view');
  document.getElementById('vt-flujo').classList.toggle('active', v === 'flujo');
  document.getElementById('vt-mapa').classList.toggle('active', v === 'mapa');
  if (v === 'mapa') {
    mv.classList.add('show');
    mapResize();
    if (!MAPA.loaded) mapRefresh(true);
    else MAPA.alpha = Math.max(MAPA.alpha, 0.3);
    if (!MAPA.running) { MAPA.running = true; MAPA.raf = requestAnimationFrame(mapLoop); }
  } else {
    mv.classList.remove('show');
    MAPA.running = false;
    cancelAnimationFrame(MAPA.raf);
  }
}

function mapResize() {
  var c = document.getElementById('map-canvas');
  if (!c) return;
  var dpr = window.devicePixelRatio || 1;
  c.width = c.clientWidth * dpr;
  c.height = c.clientHeight * dpr;
}

function mapSetUmbral(v) {
  MAPA.umbral = v / 100;
  var el = document.getElementById('map-umbral-val');
  if (el) el.textContent = MAPA.umbral.toFixed(2);
  MAPA.alpha = 1;
  mapLegend();
}

function mapRefresh(fit) {
  fetch('/api/memoria/grafo?umbral=0.35')
    .then(function(r) { return r.json(); })
    .then(function(d) {
      mapMerge(d.nodes || [], d.edges || []);
      MAPA.loaded = true;
      mapLegend();
      var emp = document.getElementById('map-empty');
      if (emp) emp.style.display = MAPA.nodes.length ? 'none' : 'flex';
      if (fit) setTimeout(mapFit, 900);
    })
    .catch(function() { showToast('No se pudo cargar el micelio', 'error'); });
}

// merge: los nodos existentes conservan su posicion; los nuevos NACEN
// cerca del centro con animacion de anillo (el organismo crece).
function mapMerge(nodes, edges) {
  var c = document.getElementById('map-canvas');
  var W = (c && c.clientWidth) || 900, H = (c && c.clientHeight) || 600;
  var prev = MAPA.byId, by = {}, out = [];
  nodes.forEach(function(n, i) {
    var old = prev[n.id];
    var ang = (i / Math.max(1, nodes.length)) * Math.PI * 2;
    var nd = old || {
      id: n.id,
      x: W / 2 + Math.cos(ang) * (110 + Math.random() * 100),
      y: H / 2 + Math.sin(ang) * (110 + Math.random() * 100),
      vx: 0, vy: 0,
      birth: MAPA.loaded ? MAPA.t : -99,
      phase: Math.random() * Math.PI * 2,
    };
    nd.dir = n.dir; nd.titulo = n.titulo; nd.chunks = n.chunks || 1;
    nd.r = 5 + Math.min(13, Math.sqrt(nd.chunks) * 2.1);
    by[n.id] = nd; out.push(nd);
  });
  MAPA.nodes = out; MAPA.byId = by;
  MAPA.edges = (edges || []).filter(function(e) { return by[e.a] && by[e.b]; });
  out.forEach(function(n) { n.deg = 0; });
  MAPA.edges.forEach(function(e) { by[e.a].deg++; by[e.b].deg++; });
  MAPA.alpha = 1;
}

function mapLegend() {
  var rows = document.getElementById('legend-rows');
  if (!rows) return;
  var dirs = {};
  MAPA.nodes.forEach(function(n) { dirs[n.dir] = (dirs[n.dir] || 0) + 1; });
  rows.innerHTML = Object.keys(dirs).sort().map(function(d) {
    var col = DIR_COLORS[d] || '#8b949e';
    return '<div class="lg-row' + (MAPA.dirOff[d] ? ' off' : '') + '" onclick="mapToggleDir(\'' + d + '\')">' +
      '<span class="lg-dot" style="background:' + col + ';color:' + col + '"></span>' +
      d + ' <span style="color:#6e6a5e">(' + dirs[d] + ')</span></div>';
  }).join('');
  var vis = mapVisibleEdges().length;
  var cts = document.getElementById('map-counts');
  if (cts) cts.textContent = MAPA.nodes.length + ' piezas / ' + vis + ' filamentos / afinidad >= ' + MAPA.umbral.toFixed(2);
}

function mapToggleDir(d) {
  MAPA.dirOff[d] = !MAPA.dirOff[d];
  MAPA.alpha = 0.6;
  mapLegend();
}

function mapVisibleEdges() {
  return MAPA.edges.filter(function(e) {
    var a = MAPA.byId[e.a], b = MAPA.byId[e.b];
    return e.w >= MAPA.umbral && a && b && !MAPA.dirOff[a.dir] && !MAPA.dirOff[b.dir];
  });
}
function mapVisibleNodes() {
  return MAPA.nodes.filter(function(n) { return !MAPA.dirOff[n.dir]; });
}

function mapFit() {
  var ns = mapVisibleNodes();
  if (!ns.length) return;
  var c = document.getElementById('map-canvas');
  var W = c.clientWidth, H = c.clientHeight;
  var x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
  ns.forEach(function(n) {
    x0 = Math.min(x0, n.x); y0 = Math.min(y0, n.y);
    x1 = Math.max(x1, n.x); y1 = Math.max(y1, n.y);
  });
  var bw = Math.max(120, x1 - x0), bh = Math.max(120, y1 - y0);
  var k = Math.min(2.4, Math.max(0.3, Math.min((W - 140) / bw, (H - 140) / bh)));
  MAPA.view.k = k;
  MAPA.view.x = (W - bw * k) / 2 - x0 * k;
  MAPA.view.y = (H - bh * k) / 2 - y0 * k;
}

// ── fisica: repulsion + resortes por afinidad + gravedad suave ──
function mapPhysics() {
  var ns = mapVisibleNodes(), es = mapVisibleEdges();
  if (!ns.length) return;
  var a = Math.max(MAPA.alpha, 0.025);   // nunca congelado: organismo vivo
  var c = document.getElementById('map-canvas');
  var cx = c.clientWidth / 2, cy = c.clientHeight / 2;
  var i, j, n, m, dx, dy, d2, d, f;
  for (i = 0; i < ns.length; i++) {
    n = ns[i];
    for (j = i + 1; j < ns.length; j++) {
      m = ns[j];
      dx = n.x - m.x; dy = n.y - m.y;
      d2 = dx * dx + dy * dy + 40;
      f = Math.min(3.2, 2300 / d2) * a;
      d = Math.sqrt(d2);
      n.vx += (dx / d) * f; n.vy += (dy / d) * f;
      m.vx -= (dx / d) * f; m.vy -= (dy / d) * f;
    }
    // gravedad al centro
    n.vx += (cx - n.x) * 0.0011 * a;
    n.vy += (cy - n.y) * 0.0011 * a;
  }
  es.forEach(function(e) {
    var p = MAPA.byId[e.a], q = MAPA.byId[e.b];
    var ddx = q.x - p.x, ddy = q.y - p.y;
    var dist = Math.sqrt(ddx * ddx + ddy * ddy) + 0.01;
    var rest = 65 + (1 - e.w) * 240;      // mas afines = mas cerca
    var ff = (dist - rest) * 0.0045 * e.w * a;
    p.vx += (ddx / dist) * ff; p.vy += (ddy / dist) * ff;
    q.vx -= (ddx / dist) * ff; q.vy -= (ddy / dist) * ff;
  });
  ns.forEach(function(nn) {
    if (nn === MAPA.dragN) { nn.vx = 0; nn.vy = 0; return; }
    nn.vx *= 0.86; nn.vy *= 0.86;
    var sp = Math.sqrt(nn.vx * nn.vx + nn.vy * nn.vy);
    if (sp > 4.5) { nn.vx = nn.vx / sp * 4.5; nn.vy = nn.vy / sp * 4.5; }
    nn.x += nn.vx; nn.y += nn.vy;
  });
  MAPA.alpha *= 0.994;
}

function hexA(hex, a) {
  var r = parseInt(hex.slice(1, 3), 16), g = parseInt(hex.slice(3, 5), 16),
      b = parseInt(hex.slice(5, 7), 16);
  return 'rgba(' + r + ',' + g + ',' + b + ',' + a + ')';
}

// ── render: filamentos ondulantes, esporas viajeras, nodos que respiran ──
function mapDraw() {
  var c = document.getElementById('map-canvas');
  var ctx = c.getContext('2d');
  var dpr = window.devicePixelRatio || 1;
  var v = MAPA.view, t = MAPA.t;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.clearRect(0, 0, c.width, c.height);
  ctx.setTransform(dpr * v.k, 0, 0, dpr * v.k, dpr * v.x, dpr * v.y);

  var es = mapVisibleEdges();
  var um = MAPA.umbral;
  es.forEach(function(e, ei) {
    var p = MAPA.byId[e.a], q = MAPA.byId[e.b];
    var col = DIR_COLORS[p.dir] || '#9db67c';
    var mx = (p.x + q.x) / 2, my = (p.y + q.y) / 2;
    var ddx = q.x - p.x, ddy = q.y - p.y;
    var len = Math.sqrt(ddx * ddx + ddy * ddy) + 0.01;
    // ondulacion perpendicular: filamento vivo, cada arista con su fase
    var wave = Math.sin(t * 1.15 + ei * 1.7) * Math.min(15, len * 0.06);
    var cxp = mx - (ddy / len) * wave, cyp = my + (ddx / len) * wave;
    var rel = (e.w - um) / Math.max(0.05, 1 - um);
    ctx.strokeStyle = hexA(col, 0.14 + rel * 0.42);
    ctx.lineWidth = (0.7 + rel * 2.4) / v.k;
    ctx.beginPath();
    ctx.moveTo(p.x, p.y);
    ctx.quadraticCurveTo(cxp, cyp, q.x, q.y);
    ctx.stroke();
    // espora viajera en los filamentos fuertes
    if (e.w >= 0.72) {
      var u = (t * 0.11 + ei * 0.37) % 1;
      var iu = 1 - u;
      var sx = iu * iu * p.x + 2 * iu * u * cxp + u * u * q.x;
      var sy = iu * iu * p.y + 2 * iu * u * cyp + u * u * q.y;
      ctx.fillStyle = hexA(col, 0.85);
      ctx.beginPath();
      ctx.arc(sx, sy, 1.7 / v.k + 0.6, 0, 6.284);
      ctx.fill();
    }
  });

  mapVisibleNodes().forEach(function(n) {
    var col = DIR_COLORS[n.dir] || '#8b949e';
    var breath = 1 + 0.05 * Math.sin(t * 1.9 + n.phase);
    var r = n.r * breath;
    // halo
    var g = ctx.createRadialGradient(n.x, n.y, r * 0.4, n.x, n.y, r * 3.2);
    g.addColorStop(0, hexA(col, 0.34));
    g.addColorStop(1, hexA(col, 0));
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.arc(n.x, n.y, r * 3.2, 0, 6.284); ctx.fill();
    // cuerpo
    ctx.fillStyle = col;
    ctx.beginPath(); ctx.arc(n.x, n.y, r, 0, 6.284); ctx.fill();
    // nucleo claro
    ctx.fillStyle = hexA('#f4f1e6', 0.75);
    ctx.beginPath(); ctx.arc(n.x - r * 0.25, n.y - r * 0.3, r * 0.32, 0, 6.284); ctx.fill();
    // anillo de nacimiento (pieza nueva del archivo)
    var age = t - n.birth;
    if (age >= 0 && age < 3.2) {
      ctx.strokeStyle = hexA(col, Math.max(0, 0.8 - age / 3.2));
      ctx.lineWidth = 1.6 / v.k;
      ctx.beginPath(); ctx.arc(n.x, n.y, r + age * 24, 0, 6.284); ctx.stroke();
    }
    // seleccion / puente armado: anillo girando
    if (MAPA.sel === n.id || MAPA.bridge === n.id) {
      ctx.strokeStyle = MAPA.bridge === n.id ? '#e0c58f' : '#f4f1e6';
      ctx.lineWidth = 1.4 / v.k;
      ctx.setLineDash([5 / v.k, 4 / v.k]);
      ctx.lineDashOffset = -t * 14;
      ctx.beginPath(); ctx.arc(n.x, n.y, r + 7 / v.k, 0, 6.284); ctx.stroke();
      ctx.setLineDash([]);
    }
    // etiqueta: hover, hubs, o zoom cercano
    if (MAPA.hover === n || v.k >= 1.15 || n.deg >= 5) {
      ctx.font = (10 / v.k) + 'px ui-monospace, monospace';
      ctx.fillStyle = MAPA.hover === n ? '#f4f1e6' : hexA('#c9c5b9', 0.75);
      ctx.textAlign = 'center';
      var lbl = (n.titulo || n.id).slice(0, 30);
      ctx.fillText(lbl, n.x, n.y + r + 13 / v.k);
    }
  });
}

function mapLoop() {
  if (!MAPA.running) return;
  MAPA.t += 0.016;
  mapPhysics();
  mapDraw();
  MAPA.raf = requestAnimationFrame(mapLoop);
}

// ── investigar DESDE el micelio: los modos de arriba operan sobre el mapa ──
// click en pieza -> tarjeta de acciones (abrir / investigar con el modo
// activo / puente entre dos piezas). El resultado nace como nodo nuevo.
function limpiarTema(titulo) {
  var t = String(titulo || '');
  t = t.replace(/^(Research|Grafo|Panel|Cadena|Refutacion|Refutación|Memoria|Correlacion|Correlación|Informe|Corpus)\s*:\s*/i, '');
  t = t.replace(/^Investigacion cultural DESCRIPTIVA[^:]*:\s*/i, '');
  return t.trim().slice(0, 220);
}

function mapNodeClick(n, e) {
  // puente armado: esta es la segunda pieza -> investigar la relacion
  if (MAPA.bridge && MAPA.bridge !== n.id) {
    var a = MAPA.byId[MAPA.bridge];
    var tema = 'la relacion entre "' + limpiarTema(a.titulo) + '" y "' +
               limpiarTema(n.titulo) + '"';
    MAPA.bridge = null;
    mapCloseActions();
    mapRunDesde(tema, 'puente');
    return;
  }
  MAPA.sel = n.id;
  var card = document.getElementById('map-action');
  var modo = workflow.mode || 'single';
  card.innerHTML =
    '<div class="ma-title">' + esc(limpiarTema(n.titulo) || n.id) + '</div>' +
    '<div class="ma-meta">' + esc(n.dir) + ' &middot; ' + n.chunks + ' frag &middot; ' + n.deg + ' filamentos</div>' +
    '<div class="ma-btns">' +
      '<button onclick="verArchivo(\'' + esc(n.dir) + '\',\'' + encodeURIComponent(n.id) + '\')">&#128214; Abrir</button>' +
      '<button class="ma-go" onclick="mapInvestigar(\'' + encodeURIComponent(n.id) + '\')">&#9654; Investigar (' + esc(modo) + ')</button>' +
      '<button onclick="mapPuente(\'' + encodeURIComponent(n.id) + '\')">&#128279; Puente</button>' +
      '<button onclick="mapCloseActions()">&#10005;</button>' +
    '</div>';
  var mv = document.getElementById('map-view').getBoundingClientRect();
  card.style.left = Math.min(mv.width - 300, Math.max(8, e.clientX - mv.left + 14)) + 'px';
  card.style.top = Math.min(mv.height - 150, Math.max(8, e.clientY - mv.top + 10)) + 'px';
  card.classList.add('show');
}

function mapCloseActions() {
  MAPA.sel = null;
  var card = document.getElementById('map-action');
  if (card) card.classList.remove('show');
}

// corre el modo activo del topbar usando la pieza como semilla
function mapInvestigar(idEnc) {
  var n = MAPA.byId[decodeURIComponent(idEnc)];
  if (!n) return;
  mapCloseActions();
  mapRunDesde('profundizar: ' + limpiarTema(n.titulo), 'desde ' + n.dir);
}

function mapPuente(idEnc) {
  MAPA.bridge = decodeURIComponent(idEnc);
  mapCloseActions();
  showToast('Puente armado: elige la SEGUNDA pieza (Esc cancela)', 'info');
}

function mapRunDesde(tema, origen) {
  var modo = MODE_TO_BACKEND[workflow.mode] || 'research';
  var dens = (document.getElementById('run-densidad') || {value: 'medio'}).value;
  var body = 'tema=' + encodeURIComponent(tema) + '&modo=' + modo +
             '&densidad=' + dens;
  if (modo === 'grafo') body += '&memoria=1';   // el grafo hereda la memoria
  if (modo === 'grafo' && !chequearGrafo(true)) return;
  fetch('/run', {
    method: 'POST',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: body,
  })
  .then(function(r) { return r.json(); })
  .then(function(d) {
    if (d.ok) {
      showToast('Investigando (' + modo + ', ' + origen + ')... la pieza nueva nacera en el micelio', 'success');
      refreshJobs();
    } else showToast('Error: ' + (d.error || '?'), 'error');
  })
  .catch(function() { showToast('Error de conexion', 'error'); });
}

// ── interacciones del micelio ──
function mapWorld(e) {
  var c = document.getElementById('map-canvas');
  var r = c.getBoundingClientRect();
  return {x: (e.clientX - r.left - MAPA.view.x) / MAPA.view.k,
          y: (e.clientY - r.top - MAPA.view.y) / MAPA.view.k};
}
function mapHit(w) {
  var best = null, bd = 1e9;
  mapVisibleNodes().forEach(function(n) {
    var dx = n.x - w.x, dy = n.y - w.y, d = Math.sqrt(dx * dx + dy * dy);
    if (d < n.r + 7 && d < bd) { best = n; bd = d; }
  });
  return best;
}

function mapBind() {
  var c = document.getElementById('map-canvas');
  if (!c) return;
  var tip = document.getElementById('map-tooltip');
  c.addEventListener('mousedown', function(e) {
    var w = mapWorld(e), n = mapHit(w);
    MAPA.downAt = {x: e.clientX, y: e.clientY, n: n};
    if (n) { MAPA.dragN = n; MAPA.alpha = Math.max(MAPA.alpha, 0.4); }
    else { MAPA.panM = {mx: e.clientX, my: e.clientY, vx: MAPA.view.x, vy: MAPA.view.y}; c.classList.add('grabbing'); }
  });
  c.addEventListener('mousemove', function(e) {
    if (MAPA.dragN) {
      var w = mapWorld(e);
      MAPA.dragN.x = w.x; MAPA.dragN.y = w.y;
      MAPA.alpha = Math.max(MAPA.alpha, 0.35);
      return;
    }
    if (MAPA.panM) {
      MAPA.view.x = MAPA.panM.vx + (e.clientX - MAPA.panM.mx);
      MAPA.view.y = MAPA.panM.vy + (e.clientY - MAPA.panM.my);
      return;
    }
    var n = mapHit(mapWorld(e));
    MAPA.hover = n;
    c.classList.toggle('hot', !!n);
    if (n && tip) {
      tip.innerHTML = '<div>' + esc(n.titulo || n.id) + '</div>' +
        '<div class="mt-dir">' + esc(n.dir) + ' &middot; ' + n.chunks +
        ' frag &middot; ' + n.deg + ' filamentos</div>';
      tip.style.left = e.clientX + 'px';
      tip.style.top = e.clientY + 'px';
      tip.classList.add('show');
    } else if (tip) tip.classList.remove('show');
  });
  document.addEventListener('mouseup', function(e) {
    if (MAPA.downAt && MAPA.downAt.n) {
      var moved = Math.abs(e.clientX - MAPA.downAt.x) + Math.abs(e.clientY - MAPA.downAt.y);
      if (moved < 6) mapNodeClick(MAPA.downAt.n, e);
    } else if (MAPA.downAt && !MAPA.downAt.n) {
      mapCloseActions();
    }
    MAPA.dragN = null; MAPA.panM = null; MAPA.downAt = null;
    c.classList.remove('grabbing');
  });
  c.addEventListener('wheel', function(e) {
    e.preventDefault();
    var r = c.getBoundingClientRect();
    var px = e.clientX - r.left, py = e.clientY - r.top;
    var nk = Math.max(0.25, Math.min(3, MAPA.view.k * (e.deltaY < 0 ? 1.12 : 0.89)));
    var wx = (px - MAPA.view.x) / MAPA.view.k, wy = (py - MAPA.view.y) / MAPA.view.k;
    MAPA.view.k = nk;
    MAPA.view.x = px - wx * nk;
    MAPA.view.y = py - wy * nk;
  }, {passive: false});
  c.addEventListener('mouseleave', function() {
    if (tip) tip.classList.remove('show');
    MAPA.hover = null;
  });
}

// ── init ──
document.addEventListener('DOMContentLoaded', function() {
  renderNodes();
  drawConnections();
  selectNode(null);
  setInterval(refreshJobs, 4000);
  refreshMemStats();
  setInterval(refreshMemStats, 15000);
  window.addEventListener('resize', function() { drawConnections(); mapResize(); });
  mapBind();
  // el micelio crece solo: si esta visible, refresca cada 25s
  setInterval(function() { if (MAPA.running) mapRefresh(false); }, 25000);
  // fit to view on first load
  setTimeout(fitToView, 100);
});
"""

# ─────────────────────────────────────────────────────
#  HTML template
# ─────────────────────────────────────────────────────

HTML = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MAK Research &middot; Workflow</title>
<style>""" + CSS + """</style>
</head>
<body>

<!-- ── TOPBAR ── -->
<div class="topbar">
  <div class="topbar-left">
    <div class="logo">
      <svg viewBox="0 0 26 26" fill="none"><rect x="2" y="2" width="22" height="22" rx="6" fill="#238636"/><path d="M8 13l3 3 7-7" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
      MAK Research
    </div>
    <span class="topbar-pill"><span class="status-dot idle" id="status-dot"></span>workflow engine</span>
    <div class="view-toggle">
      <button id="vt-flujo" class="active" onclick="setView('flujo')" title="Canvas de ejecucion">
        <svg viewBox="0 0 16 16"><rect x="1" y="5" width="4" height="6" rx="1"/><rect x="11" y="5" width="4" height="6" rx="1"/><path d="M5 8h6"/></svg>
        Flujo</button>
      <button id="vt-mapa" onclick="setView('mapa')" title="Micelio semantico: el archivo vivo del departamento">
        <svg viewBox="0 0 16 16"><circle cx="4" cy="4" r="1.7"/><circle cx="12" cy="5" r="1.7"/><circle cx="7" cy="12" r="1.7"/><path d="M5.4 5 6.4 10.6M5.6 4.4 10.3 4.9M11.2 6.4 8 10.7"/></svg>
        Micelio</button>
    </div>
  </div>
  <div class="topbar-center">
    <button class="mode-btn MODE_SINGLE_CSS" data-mode="single" onclick="setMode('single')">&#9889; Single</button>
    <button class="mode-btn MODE_PIPELINE_CSS" data-mode="pipeline" onclick="setMode('pipeline')">&#128279; Pipeline</button>
    <button class="mode-btn MODE_DISCUSSION_CSS" data-mode="discussion" onclick="setMode('discussion')">&#128172; Discussion</button>
    <button class="mode-btn MODE_ADVERSARIAL_CSS" data-mode="adversarial" onclick="setMode('adversarial')">&#9877; Adversarial</button>
    <button class="mode-btn MODE_GRAFO_CSS" data-mode="grafo" onclick="setMode('grafo')" title="Las conexiones que dibujes dirigen la ejecucion">&#128376; Grafo</button>
  </div>
  <div class="topbar-right">
    <a class="topbar-pill" href="#" onclick="window.open('http://'+location.hostname+':8900/cuotas');return false" style="color:#d4a259;text-decoration:none" title="Cuotas de los modelos">&#128202; cuotas</a>
    <span class="topbar-pill">LAN</span>
    <span class="topbar-pill" id="clock-pill"></span>
  </div>
</div>

<!-- ── MAIN ── -->
<div class="main-wrap">
  <!-- canvas -->
  <div class="canvas-wrap" id="canvas-wrap">
    <div id="canvas-world">
      <svg id="canvas-svg"></svg>
    </div>
    <div class="canvas-controls">
      <div class="tool-group">
        <button onclick="zoomBy(-0.15)" title="Alejar">
          <svg viewBox="0 0 16 16"><path d="M3 8h10"/></svg></button>
        <span class="zoom-level" id="zoom-level">100%</span>
        <button onclick="zoomBy(0.15)" title="Acercar">
          <svg viewBox="0 0 16 16"><path d="M8 3v10M3 8h10"/></svg></button>
        <button onclick="zoomReset()" title="Zoom 100%">1:1</button>
        <button onclick="fitToView()" title="Encajar todo">
          <svg viewBox="0 0 16 16"><path d="M2 6V2h4M10 2h4v4M14 10v4h-4M6 14H2v-4"/></svg></button>
        <button onclick="centerView()" title="Centrar vista">
          <svg viewBox="0 0 16 16"><circle cx="8" cy="8" r="2.6"/><path d="M8 1v3M8 12v3M1 8h3M12 8h3"/></svg></button>
      </div>
      <div class="tool-group">
        <button onclick="addNode('trigger')" title="Agregar entrada (multiples permitidas)">
          <svg viewBox="0 0 16 16"><path d="M10 2h4v12h-4M2 8h8M7 5l3 3-3 3"/></svg></button>
        <button onclick="addNode('output')" title="Agregar salida (multiples permitidas)">
          <svg viewBox="0 0 16 16"><path d="M6 2H2v12h4M6 8h8M11 5l3 3-3 3"/></svg></button>
        <button onclick="addNode('nota')" title="Agregar nota">
          <svg viewBox="0 0 16 16"><path d="M3 2h7l3 3v9H3zM10 2v3h3"/></svg></button>
        <button onclick="organizar()" title="Auto-organizar nodos">
          <svg viewBox="0 0 16 16"><circle cx="3.5" cy="3.5" r="1.4"/><circle cx="8" cy="3.5" r="1.4"/><circle cx="12.5" cy="3.5" r="1.4"/><circle cx="3.5" cy="8" r="1.4"/><circle cx="8" cy="8" r="1.4"/><circle cx="12.5" cy="8" r="1.4"/><circle cx="3.5" cy="12.5" r="1.4"/><circle cx="8" cy="12.5" r="1.4"/><circle cx="12.5" cy="12.5" r="1.4"/></svg></button>
        <button onclick="resetLayout()" title="Resetear layout">
          <svg viewBox="0 0 16 16"><path d="M2.5 8a5.5 5.5 0 1 1 1.6 3.9M2.5 13.5v-3h3"/></svg></button>
      </div>
      <div class="tool-group">
        <button onclick="if(chequearGrafo(false))showToast('Grafo valido','success')" title="Validar flujo (ciclos, huerfanos, fan-out)">
          <svg viewBox="0 0 16 16"><path d="M2.5 8.5l3.5 3.5 7-8"/></svg></button>
        <button onclick="reindexarMemoria()" title="Reindexar memoria del departamento (embeddings locales)">
          <svg viewBox="0 0 16 16"><path d="M8 2c3 0 5.5 1 5.5 2.5S11 7 8 7 2.5 6 2.5 4.5 5 2 8 2z"/><path d="M2.5 4.5v7C2.5 13 5 14 8 14s5.5-1 5.5-2.5v-7"/><path d="M2.5 8C2.5 9.5 5 10.5 8 10.5S13.5 9.5 13.5 8"/></svg></button>
        <span class="zoom-level" id="mem-count" title="Fragmentos indexados en la memoria">--</span>
      </div>
    </div>
  </div>

  <!-- right panel -->
  <div class="panel">
    <div class="tabs">
      <button class="tab active" data-tab="config" onclick="switchTab('config')">&#9881; Config</button>
      <button class="tab" data-tab="run" onclick="switchTab('run')">&#9654; Run</button>
      <button class="tab" data-tab="history" onclick="switchTab('history')">&#128203; History</button>
      <button class="tab" data-tab="files" onclick="switchTab('files')">&#128193; Files</button>
    </div>

    <div class="tab-content active" id="tab-config">
      <div class="panel-header">&#128295; Modelo seleccionado</div>
      <div id="panel-body">
        <div class="panel-section">
          <p style="color:#8b949e;font-size:.85rem">Click en un nodo del canvas para editarlo</p>
        </div>
      </div>
    </div>

    <div class="tab-content" id="tab-run">
      <div class="panel-header">&#9654; Ejecutar workflow</div>
      <div class="panel-section">
        <form id="runform" onsubmit="return runWorkflow()">
          <div class="field">
            <label>Tema de investigación</label>
            <input type="text" name="tema" id="run-tema" placeholder="Ej: impacto de IA en educación" required>
          </div>
          <div class="field">
            <label>Modo</label>
            <select name="modo" id="run-modo">
              <option value="research">Single (research)</option>
              <option value="cadena">Pipeline (cadena encadenada)</option>
              <option value="panel">Discussion (panel paralelo)</option>
              <option value="refutar">Adversarial (proponer/refutar)</option>
              <option value="grafo">Grafo (conexiones dirigen la ejecucion)</option>
              <option value="memoria">Memoria (que sabe el depto de X + vacios)</option>
              <option value="corpus">Corpus (correlacionar archivo, sin tema)</option>
            </select>
          </div>
          <div class="field" style="display:flex;align-items:center;gap:8px">
            <input type="checkbox" id="run-memoria" style="width:auto">
            <label for="run-memoria" style="margin:0">Consultar memoria del depto (inyecta hallazgos previos; modo Grafo)</label>
          </div>
          <div class="field">
            <label>Profundidad (n)</label>
            <input type="number" name="n" id="run-n" placeholder="default" min="0" max="10">
          </div>
          <div class="field">
            <label>Densidad del trabajo (tokens totales estimados)</label>
            <select name="densidad" id="run-densidad">
              <option value="corto">Corto (~2k tokens)</option>
              <option value="medio" selected>Medio (~5k tokens)</option>
              <option value="largo">Largo (~10k tokens)</option>
            </select>
          </div>
          <div style="margin-top:14px">
            <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center">
              &#9654; Ejecutar workflow
            </button>
          </div>
        </form>
      </div>
    </div>

    <div class="tab-content" id="tab-history">
      <div class="panel-header">&#128203; Estado reciente</div>
      <div class="panel-section">
        <ul class="job-list" id="job-list">
          JOBS_PLACEHOLDER
        </ul>
      </div>
    </div>

    <div class="tab-content" id="tab-files">
      <div class="panel-header">&#128451; Archivo del departamento</div>
      <div class="panel-section" style="border-bottom:none;padding-bottom:4px">
        <input class="file-search" id="file-search" placeholder="Buscar en el archivo..."
               oninput="filtrarArchivo(this.value)">
      </div>
      <div class="panel-section" style="border-bottom:none;padding-top:6px">
        <ul class="file-list" id="archivo-list">ARCHIVO_PLACEHOLDER</ul>
      </div>
    </div>
  </div>

  <!-- ── MICELIO: mapa semantico del archivo (canvas 2D, fisica propia) ── -->
  <div id="map-view">
    <canvas id="map-canvas"></canvas>
    <div class="map-legend">
      <h4>&#129744; Micelio del archivo</h4>
      <div id="legend-rows"></div>
      <div class="map-counts" id="map-counts"></div>
    </div>
    <div class="map-hint">
      <b>nodo</b> = pieza de research &middot; <b>filamento</b> = afinidad
      semantica (embeddings locales) &middot; <b>click en una pieza</b> =
      abrirla o INVESTIGAR desde ella con el modo activo de arriba; con
      <b>Puente</b> eliges dos piezas y el departamento investiga la
      relacion entre ambas. El micelio <b>crece y se remodela</b> con cada
      research.
    </div>
    <div class="map-controls">
      <div class="tool-group">
        <span class="tool-label">Afinidad</span>
        <div class="mc-slider">
          <input type="range" id="map-umbral" min="35" max="90" value="55"
                 oninput="mapSetUmbral(this.value)">
          <span id="map-umbral-val">0.55</span>
        </div>
      </div>
      <div class="tool-group">
        <button onclick="mapRefresh(true)" title="Refrescar el micelio">
          <svg viewBox="0 0 16 16"><path d="M13.5 8a5.5 5.5 0 1 1-1.6-3.9M13.5 2.5v3h-3"/></svg>
        </button>
        <button onclick="mapFit()" title="Encajar">
          <svg viewBox="0 0 16 16"><path d="M2 6V2h4M10 2h4v4M14 10v4h-4M6 14H2v-4"/></svg>
        </button>
      </div>
    </div>
    <div class="map-tooltip" id="map-tooltip"></div>
    <div class="map-action" id="map-action"></div>
    <div class="map-empty" id="map-empty" style="display:none">
      <div style="font-size:2rem">&#129744;</div>
      <div>El archivo esta vacio.<br>Corre un research y el micelio nace.</div>
    </div>
  </div>
</div>

<!-- ── EXEC BAR ── -->
<div class="exec-bar">
  <span style="color:#8b949e;font-size:.82rem;white-space:nowrap">Quick run:</span>
  <input class="tema-input" id="quick-tema" placeholder="Tema rápido..." style="flex:1">
  <select id="quick-modo">
    <option value="research">research</option>
    <option value="cadena">cadena</option>
    <option value="panel">panel</option>
    <option value="refutar">refutar</option>
    <option value="grafo">grafo</option>
  </select>
  <button class="btn btn-accent" onclick="quickRun()">&#9654; Run</button>
  <button class="btn btn-secondary" onclick="location.reload()">&#8635;</button>
</div>

<div class="toast" id="toast"></div>

<!-- ── VIEW MODAL (resultado renderizado dentro de la app) ── -->
<div class="view-overlay" id="view-modal" onclick="if(event.target===this)cerrarModal()">
  <div class="view-box">
    <div class="view-box-head">
      <span id="view-modal-title">Resultado</span>
      <button class="btn btn-secondary" onclick="cerrarModal()">&#10005; Cerrar</button>
    </div>
    <div class="view-box-body" id="view-modal-body"></div>
  </div>
</div>

<script>
var ENV_DATA = ___ENV_DATA___;
var DEFAULT_WF = ___DEFAULT_WF_DATA___;
""" + JS + """

// ── mode buttons initial state ──
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.mode-btn').forEach(function(b) {
    b.classList.toggle('active', b.dataset.mode === workflow.mode);
  });
  // clock
  setInterval(function() {
    document.getElementById('clock-pill').textContent = new Date().toLocaleTimeString('es-CL');
  }, 1000);
  document.getElementById('clock-pill').textContent = new Date().toLocaleTimeString('es-CL');
});

// ── quick run ──
// Persiste el workflow YA (sin debounce). Se usa antes de correr en modo
// grafo: grafo.py lee workflow.json del disco, tiene que estar fresco.
function saveNow() {
  if (saveTimer) { clearTimeout(saveTimer); saveTimer = null; }
  return fetch('/api/workflow', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(workflow),
  }).then(function(r) { return r.json(); });
}
// dispara /run; si es grafo, guarda primero y valida
function dispararRun(modo, body, onOk) {
  function go() {
    fetch('/run', {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: body,
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.ok) { onOk(); }
      else { showToast('Error: ' + (data.error || 'desconocido'), 'error'); }
    })
    .catch(function() { showToast('Error de conexión', 'error'); });
  }
  if (modo === 'grafo') {
    if (!chequearGrafo(true)) return;
    saveNow().then(go).catch(go);
  } else { go(); }
}

function quickRun() {
  var tema = document.getElementById('quick-tema').value.trim();
  var modo = document.getElementById('quick-modo').value;
  if (!tema) return;
  dispararRun(modo, 'tema=' + encodeURIComponent(tema) + '&modo=' + modo, function() {
    document.getElementById('quick-tema').value = '';
    showToast('Job encolado: ' + tema, 'success');
    refreshJobs();
  });
}

// ── run workflow (tab) ──
function runWorkflow() {
  var tema = document.getElementById('run-tema').value.trim();
  var modo = document.getElementById('run-modo').value;
  var n = document.getElementById('run-n').value;
  var densidad = document.getElementById('run-densidad').value;
  if (!tema) return false;
  var body = 'tema=' + encodeURIComponent(tema) + '&modo=' + modo + '&densidad=' + densidad;
  if (n) body += '&n=' + n;
  var memEl = document.getElementById('run-memoria');
  if (memEl && memEl.checked) body += '&memoria=1';
  dispararRun(modo, body, function() {
    showToast('Workflow ejecutándose...', 'success');
    document.getElementById('run-tema').value = '';
    refreshJobs();
    switchTab('history');
  });
  return false;
}
</script>
</body>
</html>"""


# ─────────────────────────────────────────────────────
#  HTTP handler
# ─────────────────────────────────────────────────────

class H(BaseHTTPRequestHandler):
    server_version = "MAK-Research/2.0"

    def _html(self, body, code=200):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        # no-cache: el server sirve HTML/CSS/JS inline; sin esto el
        # navegador muestra una version vieja tras cada update
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def _json_response(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)

        # favicon: return 204 No Content
        if u.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        # API: workflow
        if u.path == "/api/workflow":
            with WORKFLOW_LOCK:
                wf = _load_workflow()
            return self._json_response(wf)

        # API: jobs
        if u.path == "/api/jobs":
            with JOBS_LOCK:
                jobs = list(reversed(JOBS[-15:]))
            return self._json_response(jobs)

        # API: memoria stats (chunks indexados)
        if u.path == "/api/memoria/stats":
            return self._json_response(_memoria_stats())

        # API: grafo semantico (nodos=productos, aristas=similitud embeddings)
        if u.path == "/api/memoria/grafo":
            try:
                import memoria
                q = urllib.parse.parse_qs(u.query)
                umbral = float((q.get("umbral") or ["0.5"])[0])
                return self._json_response(memoria.grafo_semantico(umbral=umbral))
            except Exception as e:  # noqa: BLE001 - viz es best-effort
                return self._json_response({"nodes": [], "edges": [],
                                            "error": str(e)[:200]}, 200)

        # status
        if u.path == "/status":
            try:
                with open(os.path.expanduser("~/research/.current_status.json"), "r") as f:
                    s = json.load(f)
                try:
                    os.kill(s.get("pid", 0), 0)
                except OSError:
                    s["status"] = "stale (PID muerto)"
                return self._json_response(s)
            except (OSError, json.JSONDecodeError):
                return self._json_response({"idle": True})

        # file viewer
        if u.path == "/f":
            q = urllib.parse.parse_qs(u.query)
            d = (q.get("d") or [""])[0]
            n = (q.get("n") or [""])[0]
            if d not in DIRS or not NOMBRE_OK.match(n):
                return self._html("no", 404)
            try:
                with open(os.path.join(DIRS[d], n), encoding="utf-8") as f:
                    texto = f.read()
            except OSError:
                return self._html("no existe", 404)
            data = texto.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        # ── main page ──
        with WORKFLOW_LOCK:
            wf = _load_workflow()

        env = _config_actual()

        # jobs HTML (initial render)
        with JOBS_LOCK:
            jobs_html = ""
            for j in reversed(JOBS[-15:]):
                estado_lower = j.get("estado", "").lower().replace(" ", "-")
                tema_esc = html.escape(j.get("tema", "")[:50])
                link = ""
                if j.get("path"):
                    d = MODO_DIR.get(j.get("modo"), "informes")
                    link = (
                        '<a href="#" onclick="verArchivo(\'%s\',\'%s\');return false;" '
                        'style="color:#58a6ff;font-size:.75rem">ver</a>'
                        % (d, urllib.parse.quote(j["path"]))
                    )
                elif j.get("estado") == "FALLO":
                    link = (
                        '<a href="#" onclick="verError(\'%s\',\'%s\');return false;" '
                        'style="color:#ff7b72;font-size:.75rem">error</a>'
                        % (urllib.parse.quote(j.get("tema", "")),
                           urllib.parse.quote(j.get("error", "")))
                    )
                elif j.get("estado") == "PAUSADO":
                    jid_enc = urllib.parse.quote(j.get("job_id", ""))
                    motivo_esc = html.escape((j.get("error", "") or "")[:160])
                    link = (
                        '<span style="color:#e0a458;font-size:.72rem;max-width:140px;'
                        'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'
                        'display:inline-block" title="%s">%s</span> '
                        '<a href="#" onclick="reanudar(\'%s\',\'reintentar\');return false;" '
                        'style="color:#58a6ff;font-size:.72rem">reintentar</a> '
                        '<a href="#" onclick="reanudar(\'%s\',\'editar\');return false;" '
                        'style="color:#58a6ff;font-size:.72rem">editar</a> '
                        '<a href="#" onclick="reanudar(\'%s\',\'saltar\');return false;" '
                        'style="color:#58a6ff;font-size:.72rem">saltar</a> '
                        '<a href="#" onclick="reanudar(\'%s\',\'abortar\');return false;" '
                        'style="color:#ff7b72;font-size:.72rem">abortar</a>'
                        % (motivo_esc, motivo_esc, jid_enc, jid_enc, jid_enc, jid_enc)
                    )
                jobs_html += (
                    '<li class="job-item">'
                    '<span class="job-dot %s"></span>'
                    '<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">%s</span>'
                    '<span style="color:#8b949e;font-size:.72rem">%s &middot; %s</span>'
                    '%s'
                    '</li>'
                    % (estado_lower, tema_esc, j.get("t", ""), j.get("estado", ""), link)
                )
            if not jobs_html:
                jobs_html = '<li class="job-item" style="color:#8b949e">Sin jobs</li>'

        # archivo unificado: todos los productos como cards, nuevo primero
        todos = []
        for d in DIRS:
            try:
                nombres = os.listdir(DIRS[d])
            except OSError:
                continue
            todos += [(f, d) for f in nombres if f.endswith(".md")]
        todos.sort(reverse=True)  # el nombre arranca con el stamp -> cronologico
        cards = ""
        for f, d in todos[:80]:
            m = FECHA_RE.match(f)
            if m:
                fecha = "%s-%s-%s %s:%s" % m.groups()[:5]
                titulo = m.group(7).replace("-", " ")
            else:
                fecha, titulo = "", f[:-3]
            c = DIR_COLOR.get(d, "#8b949e")
            cards += (
                '<li class="file-card" data-q="%s %s" '
                'onclick="verArchivo(\'%s\',\'%s\')">'
                '<span class="fc-dot" style="background:%s;color:%s"></span>'
                '<div class="fc-body"><div class="fc-title">%s</div>'
                '<div class="fc-meta">%s</div></div>'
                '<span class="fc-chip" style="background:%s22;color:%s">%s</span>'
                '</li>'
                % (html.escape(titulo.lower()), d, d, urllib.parse.quote(f),
                   c, c, html.escape(titulo), fecha, c, c, DIR_CHIP.get(d, d))
            )
        archivo_html = cards or (
            '<li class="file-item" style="color:#8b949e">(archivo vacio -- '
            'corre un research)</li>')

        # build page with safe replacements
        page = HTML
        wf_json = json.dumps(wf, ensure_ascii=False)
        default_wf_json = json.dumps(DEFAULT_WORKFLOW, ensure_ascii=False)
        env_json = json.dumps(env, ensure_ascii=False)

        # order: longer placeholders first to prevent substring collision
        page = page.replace("___DEFAULT_WF_DATA___", default_wf_json)
        page = page.replace("___WF_DATA___", wf_json)
        page = page.replace("___ENV_DATA___", env_json)
        page = page.replace("JOBS_PLACEHOLDER", jobs_html)
        page = page.replace("ARCHIVO_PLACEHOLDER", archivo_html)

        # mode buttons: initial active CSS class (space already in HTML template)
        page = page.replace(
            "MODE_SINGLE_CSS", "active" if wf["mode"] == "single" else ""
        )
        page = page.replace(
            "MODE_PIPELINE_CSS", "active" if wf["mode"] == "pipeline" else ""
        )
        page = page.replace(
            "MODE_DISCUSSION_CSS", "active" if wf["mode"] == "discussion" else ""
        )
        page = page.replace(
            "MODE_ADVERSARIAL_CSS", "active" if wf["mode"] == "adversarial" else ""
        )
        page = page.replace(
            "MODE_GRAFO_CSS", "active" if wf["mode"] == "grafo" else ""
        )

        self._html(page)

    def do_POST(self):
        # API: save workflow
        if self.path == "/api/workflow":
            largo = min(int(self.headers.get("Content-Length") or 0), 50000)
            body = self.rfile.read(largo).decode("utf-8")
            try:
                wf = json.loads(body)
                with WORKFLOW_LOCK:
                    _save_workflow(wf)
                self._json_response({"ok": True})
            except (json.JSONDecodeError, TypeError, KeyError) as e:
                self._json_response({"ok": False, "error": str(e)}, 400)
            except OSError as e:
                self._json_response({"ok": False, "error": str(e)}, 500)
            return

        # config form (legacy endpoint)
        if self.path == "/config":
            largo = min(int(self.headers.get("Content-Length") or 0), 20000)
            q = urllib.parse.parse_qs(self.rfile.read(largo).decode())
            _guardar_config(q)
            return self._html("Guardado", 200)

        # run workflow
        if self.path == "/run":
            largo = min(int(self.headers.get("Content-Length") or 0), 10000)
            q = urllib.parse.parse_qs(self.rfile.read(largo).decode())
            tema = (q.get("tema") or [""])[0].strip()[:300]
            modo = (q.get("modo") or ["research"])[0]
            if modo not in MODO_DIR:
                modo = "research"
            densidad = (q.get("densidad") or ["medio"])[0]
            if densidad not in ("corto", "medio", "largo"):
                densidad = "medio"
            memoria = (q.get("memoria") or ["0"])[0] in ("1", "true", "on")
            try:
                n = int((q.get("n") or [""])[0])
                n = max(0, min(n, 10))
            except (ValueError, TypeError):
                n = None
            if not tema and modo in MODO_SIN_TEMA:
                tema = "corpus"  # placeholder: corpus ignora el tema
            if tema:
                _lanzar(modo, tema, n, densidad, memoria)
                return self._json_response({"ok": True})
            return self._json_response({"ok": False, "error": "tema vacío"}, 400)

        # memoria: reindexar el archivo (background). rebuild=1 re-embeddeba todo
        if self.path == "/api/memoria/index":
            largo = min(int(self.headers.get("Content-Length") or 0), 200)
            q = urllib.parse.parse_qs(self.rfile.read(largo).decode())
            rebuild = (q.get("rebuild") or ["0"])[0] in ("1", "true", "on")
            started = _reindexar_async(rebuild=rebuild)
            return self._json_response({"ok": True, "started": started})

        # auto-repair: el modelo capaz diagnostica un job fallido
        if self.path == "/api/repair":
            largo = min(int(self.headers.get("Content-Length") or 0), 8000)
            q = urllib.parse.parse_qs(self.rfile.read(largo).decode())
            tema = (q.get("tema") or [""])[0][:300]
            error = (q.get("error") or [""])[0][:3000]
            try:
                dx = _diagnosticar(tema, error)
                return self._json_response({"ok": True, "diagnostico": dx})
            except Exception as e:  # noqa: BLE001 - el fix es best-effort
                return self._json_response({"ok": False, "error": str(e)[:300]}, 500)

        # reanudar un job PAUSADO: reintentar / editar / saltar / abortar
        if self.path == "/api/reanudar":
            largo = min(int(self.headers.get("Content-Length") or 0), 8000)
            q = urllib.parse.parse_qs(self.rfile.read(largo).decode())
            code, payload = _reanudar_logic(q)
            return self._json_response(payload, code)

        return self._html("no", 404)

    def log_message(self, fmt, *args):
        # silence request logs: worker.log handles operational logging
        pass


# ─────────────────────────────────────────────────────
#  Server with SO_REUSEADDR + signal handling
# ─────────────────────────────────────────────────────

class ReusableTCPServer(ThreadingHTTPServer):
    allow_reuse_address = True
    allow_reuse_port = True
    daemon_threads = True


def main():
    load_env()
    load_env(ENV_FILE)

    for d in DIRS.values():
        os.makedirs(d, exist_ok=True)

    # ensure workflow file
    with WORKFLOW_LOCK:
        wf = _load_workflow()
        _save_workflow(wf)

    server = ReusableTCPServer(("0.0.0.0", PORT), H)

    # graceful shutdown on SIGTERM / SIGINT
    def shutdown_handler(signum, frame):
        print("\n[interfaz] shutting down (signal %d)..." % signum, flush=True)
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    print("[interfaz] n8n-style canvas en http://0.0.0.0:%d" % PORT, flush=True)
    print("[interfaz] workflow: %s" % WORKFLOW_FILE, flush=True)
    print("[interfaz] env: %s" % ENV_FILE, flush=True)
    server.serve_forever()
    print("[interfaz] stopped.", flush=True)


if __name__ == "__main__":
    main()
