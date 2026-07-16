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

from research_lib import load_env
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
}
# modo (backend script) -> carpeta de salida; single reusa el motor de research
MODO_DIR = {"research": "informes", "panel": "paneles",
            "cadena": "cadenas", "refutar": "refutaciones",
            "corpus": "correlaciones", "grafo": "grafos"}
# modos que NO requieren tema (correlacionan el archivo entero)
MODO_SIN_TEMA = {"corpus"}
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


def _lanzar(modo, tema, n, densidad="medio"):
    job = {
        "tema": tema, "modo": modo, "estado": "en cola",
        "path": "", "error": "", "t": time.strftime("%H:%M:%S"),
    }
    with JOBS_LOCK:
        JOBS.append(job)

    def correr():
        t0 = time.time()
        job["estado"] = "corriendo"
        try:
            orden = _orden_canvas() if modo in ("cadena", "refutar") else None
            r = run_tema(modo, tema, n=n, ntfy=True, densidad=densidad, orden=orden)
            job["estado"] = "listo" if r.get("ok") else "FALLO"
            job["path"] = os.path.basename(r["path"]) if r.get("path") else ""
            if not r.get("ok"):
                # log explicito: ultimas lineas reales del proceso, no solo "FALLO"
                job["error"] = (r.get("tail") or "").strip()[-2000:]
        except Exception as e:
            job["estado"] = "FALLO"
            job["path"] = ""
            job["error"] = str(e)[:2000]
            print(f"[interfaz] job error: {e}", file=sys.stderr)
        job["ms"] = int((time.time() - t0) * 1000)
        try:
            with open(JOBS_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(job) + "\n")
        except OSError:
            pass

    threading.Thread(target=correr, daemon=True).start()


# ── utilidades ──

def _listar(d):
    try:
        files = sorted(os.listdir(DIRS[d]), reverse=True)
    except OSError:
        files = []
    return [f for f in files if f.endswith(".md")][:15]


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
      // ── conexiones manuales por los puertos (dos clicks) ──
      // click en salida = arma; click en entrada de otro nodo = cierra.
      var pOut = nodeEl.querySelector('.port-out');
      if (pOut) pOut.addEventListener('click', function(e) {
        e.stopPropagation();
        if (connectFrom === nodeId) { connectFrom = null; drawConnections(); return; }
        connectFrom = nodeId;
        mousePos.x = workflow.nodes[nodeId].x + 210;
        mousePos.y = workflow.nodes[nodeId].y + 40;
        drawConnections();
        showToast('Origen ' + nodeId + ': click en la entrada de otro nodo (Esc cancela)', 'info');
      });
      var pIn = nodeEl.querySelector('.port-in');
      if (pIn) pIn.addEventListener('click', function(e) {
        e.stopPropagation();
        if (!connectFrom) { showToast('Primero click en una salida (puerto derecho)', 'info'); return; }
        addConnection(connectFrom, nodeId);
        connectFrom = null;
      });
      // que agarrar un puerto no arrastre el nodo ni panee el fondo
      if (pOut) pOut.addEventListener('mousedown', function(e) { e.stopPropagation(); });
      if (pIn) pIn.addEventListener('mousedown', function(e) { e.stopPropagation(); });
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
  if (connectFrom) { connectFrom = null; drawConnections(); return; }
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

document.addEventListener('mouseup', function() {
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
                            corpus: 'correlaciones', grafo: 'grafos'};
          var dir = MODO_DIR_JS[j.modo] || 'informes';
          link = '<a href="#" onclick="verArchivo(\'' + dir + '\',\'' +
            encodeURIComponent(j.path) + '\');return false;" style="color:#58a6ff;font-size:.75rem">ver</a>';
        } else if (j.estado === 'FALLO') {
          link = '<a href="#" onclick="verError(\'' + encodeURIComponent(j.tema) + '\',\'' +
            encodeURIComponent(j.error || '') + '\');return false;" style="color:#ff7b72;font-size:.75rem">error</a>';
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

// ── keyboard shortcuts ──
document.addEventListener('keydown', function(e) {
  // Escape: cancela conexion a medio trazar; si no, deselecciona
  if (e.key === 'Escape') {
    if (connectFrom) { connectFrom = null; drawConnections(); }
    else selectNode(null);
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

// ── init ──
document.addEventListener('DOMContentLoaded', function() {
  renderNodes();
  drawConnections();
  selectNode(null);
  setInterval(refreshJobs, 4000);
  window.addEventListener('resize', function() { drawConnections(); });
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
  </div>
  <div class="topbar-center">
    <button class="mode-btn MODE_SINGLE_CSS" data-mode="single" onclick="setMode('single')">&#9889; Single</button>
    <button class="mode-btn MODE_PIPELINE_CSS" data-mode="pipeline" onclick="setMode('pipeline')">&#128279; Pipeline</button>
    <button class="mode-btn MODE_DISCUSSION_CSS" data-mode="discussion" onclick="setMode('discussion')">&#128172; Discussion</button>
    <button class="mode-btn MODE_ADVERSARIAL_CSS" data-mode="adversarial" onclick="setMode('adversarial')">&#9877; Adversarial</button>
    <button class="mode-btn MODE_GRAFO_CSS" data-mode="grafo" onclick="setMode('grafo')" title="Las conexiones que dibujes dirigen la ejecucion">&#128376; Grafo</button>
  </div>
  <div class="topbar-right">
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
        <span class="tool-label">Zoom</span>
        <button onclick="zoomBy(-0.15)" title="Alejar">&#8722;</button>
        <span class="zoom-level" id="zoom-level">100%</span>
        <button onclick="zoomBy(0.15)" title="Acercar">&#43;</button>
        <button onclick="zoomReset()" title="Zoom 100%">1:1</button>
      </div>
      <div class="tool-group">
        <span class="tool-label">Vista</span>
        <button onclick="fitToView()" title="Encajar todo">&#8982; Encajar</button>
        <button onclick="centerView()" title="Centrar">&#10021; Centrar</button>
      </div>
      <div class="tool-group">
        <span class="tool-label">Nodos</span>
        <button onclick="addNode('trigger')" title="Agregar entrada (multiples entradas permitidas)">&#43; In</button>
        <button onclick="addNode('output')" title="Agregar salida (multiples salidas permitidas)">&#43; Out</button>
        <button onclick="addNode('nota')" title="Agregar nota">&#43; Nota</button>
        <button onclick="organizar()" title="Auto-organizar">&#9783; Organizar</button>
        <button onclick="resetLayout()" title="Resetear layout">&#8634; Reset</button>
      </div>
      <div class="tool-group">
        <span class="tool-label">Grafo</span>
        <button onclick="if(chequearGrafo(false))showToast('Grafo valido','success')" title="Validar flujo (ciclos, huerfanos, fan-out)">&#10003; Validar</button>
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
              <option value="corpus">Corpus (correlacionar archivo, sin tema)</option>
            </select>
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
      <div class="panel-header">&#128193; Informes recientes</div>
      <div class="panel-section">
        <ul class="file-list">INFORMES_PLACEHOLDER</ul>
      </div>
      <div class="panel-header">&#128193; Paneles recientes</div>
      <div class="panel-section">
        <ul class="file-list">PANELES_PLACEHOLDER</ul>
      </div>
      <div class="panel-header">&#128193; Cadenas recientes</div>
      <div class="panel-section">
        <ul class="file-list">CADENAS_PLACEHOLDER</ul>
      </div>
      <div class="panel-header">&#128193; Refutaciones recientes</div>
      <div class="panel-section">
        <ul class="file-list">REFUTACIONES_PLACEHOLDER</ul>
      </div>
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

    def _check_auth(self):
        token = os.environ.get("INTERFAZ_TOKEN")
        if not token:
            return True
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        t = (q.get("t") or [""])[0]
        if t == token or self.headers.get("X-Token") == token:
            return True
        self._html("No autorizado", 401)
        return False

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
        if not self._check_auth():
            return
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

        # file lists
        listas = {}
        for d in DIRS:
            items = ""
            for f in _listar(d):
                items += (
                    '<li class="file-item"><a href="#" '
                    'onclick="verArchivo(\'%s\',\'%s\');return false;">%s</a></li>'
                    % (d, urllib.parse.quote(f), html.escape(f))
                )
            listas[d] = items or '<li class="file-item" style="color:#8b949e">(vacío)</li>'

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
        page = page.replace("INFORMES_PLACEHOLDER", listas["informes"])
        page = page.replace("PANELES_PLACEHOLDER", listas["paneles"])
        page = page.replace("CADENAS_PLACEHOLDER", listas["cadenas"])
        page = page.replace("REFUTACIONES_PLACEHOLDER", listas["refutaciones"])

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
        if not self._check_auth():
            return

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
            try:
                n = int((q.get("n") or [""])[0])
                n = max(0, min(n, 10))
            except (ValueError, TypeError):
                n = None
            if not tema and modo in MODO_SIN_TEMA:
                tema = "corpus"  # placeholder: corpus ignora el tema
            if tema:
                _lanzar(modo, tema, n, densidad)
                return self._json_response({"ok": True})
            return self._json_response({"ok": False, "error": "tema vacío"}, 400)

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
