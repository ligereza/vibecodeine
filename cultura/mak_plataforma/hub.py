#!/usr/bin/env python3
"""hub.py -- LA CARA del organismo MAK (puerto 8900).

Marco fino alrededor del editor real de cada departamento, embebido a
pantalla completa via iframe. Topbar con tabs [research] [codex] que
cambian el iframe visible; franja inferior colapsable con actividad
reciente de ambos deptos y salud de proveedores. El hub proxea la
ejecucion real de research/codex: el navegador solo habla con :8900 para
el marco, pero el iframe habla directo con :8890/:8891 (LAN privada
Face A, sin token).

Rutas: / (cara) · /api/organismo · /api/micelio · /api/ejecutar (POST) ·
/pieza · /api/salud · /api/actividad · /cuotas · /doctrina · /reflexiones ·
/relevo · /genesis
"""
import html
import json
import os
import re
import signal
import sys
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import salud  # noqa: E402
import cuotas  # noqa: E402

PORT = int(os.environ.get("HUB_PORT", "8900"))
HOME = os.path.expanduser("~")
INDEX_MICELIO = os.path.join(HOME, "research/memoria/index.jsonl")
ESTADO_XIO = os.path.join(HOME, "xio_puente/estado.json")
GENESIS = os.path.join(HOME, "GENESIS.md")
DOCTRINA_DIR = os.path.join(HOME, "plataforma/doctrina")
REFLEXIONES_DIR = os.path.join(HOME, "plataforma/reflexiones")
RESEARCH_JOBS = os.path.join(HOME, "research/jobs.jsonl")
CODEX_JOBS = os.path.join(HOME, "codex/jobs.jsonl")
RELEVO = os.path.join(HOME, "RELEVO_MAK.md")
RESEARCH_URL = "http://127.0.0.1:8890"
CODEX_URL = "http://127.0.0.1:8891"
TRABAJO_STATE = os.path.join(HOME, "plataforma/.trabajo_state.json")
RED_STATE = os.path.join(HOME, "plataforma/.red_state.json")
RED_LOG = os.path.join(HOME, "plataforma/logs/red.jsonl")
TRABAJO_LOG = os.path.join(HOME, "plataforma/logs/trabajo.log")
SALUD_PROVEEDORES = os.path.join(HOME, "research/salud_proveedores.json")
SALUD_PROVEEDORES_VENTANA = 6 * 3600
try:
    import roles as _roles
    _MAXDIA = _roles.MAX_DIA
except Exception:  # noqa: BLE001
    _MAXDIA = 24

# ── LA CARA (marco fino alrededor del editor real embebido a pantalla completa) ──
PAGINA = r"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MAK — la cara del organismo</title><style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;overflow:hidden}
body{background:#080706;color:#c9c5b9;font-family:ui-monospace,SFMono-Regular,monospace;
 display:flex;flex-direction:column;height:100vh}
#topbar{flex:none;height:48px;display:flex;align-items:center;justify-content:space-between;
 padding:0 16px;background:#0d0b09;border-bottom:1px solid #211f18;gap:14px}
#topbar .izq{display:flex;align-items:center;gap:16px;min-width:0}
#topbar h1{color:#9db67c;font-size:.92rem;letter-spacing:1px;font-weight:600;white-space:nowrap}
#tabs{display:flex;gap:4px}
#tabs button{background:transparent;border:1px solid #2a2820;color:#8a8577;font-family:inherit;
 font-size:.76rem;padding:6px 13px;border-radius:6px;cursor:pointer;letter-spacing:.3px}
#tabs button:hover{color:#c3bfb2;border-color:#3a372c}
#tabs button.on{background:#1a2418;border-color:#39432c;color:#9db67c}
#topbar .der{display:flex;align-items:center;gap:12px;font-size:.72rem;white-space:nowrap}
#topbar .lk a{color:#8a8577;text-decoration:none;margin-right:11px}
#topbar .lk a:hover{color:#d4a259}
#topbar #guardia{color:#6e6a5e}
#topbar #guardia b{color:#c46d5e}#topbar #guardia i{color:#9db67c;font-style:normal}
#centro{flex:1;min-height:0;position:relative;background:#0a0908}
#centro iframe{position:absolute;inset:0;width:100%;height:100%;border:none;display:none}
#centro iframe.on{display:block}
#franja{flex:none;height:170px;display:flex;border-top:1px solid #211f18;background:#0d0b09;
 transition:height .18s ease,padding .18s ease;overflow:hidden}
#franja.colapsada{height:0;border-top-color:transparent}
#franja .col{flex:1;min-width:0;padding:10px 16px;overflow-y:auto;border-right:1px solid #17150f}
#franja .col:last-child{border-right:none}
#franja h3{font-size:.62rem;text-transform:uppercase;letter-spacing:1px;color:#6e6a5e;margin-bottom:8px}
#franja .jb{font-size:.74rem;padding:5px 0;border-bottom:1px solid #17150f;display:flex;gap:7px;align-items:baseline}
#franja .jb .d{width:7px;height:7px;border-radius:50%;flex:none;margin-top:4px}
#franja .jb .dep{color:#6e6a5e;font-size:.64rem;flex:none}
#franja .jb .t{color:#c3bfb2;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1}
#franja .jb small{color:#5f5b50}
#franja .sp-fila{display:flex;align-items:center;gap:8px;padding:4px 0;font-size:.74rem}
#franja .sp-nom{width:88px;flex:none;color:#c3bfb2;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#franja .sp-nom i{color:#d98c7e;font-style:normal;font-size:.68rem}
#franja .sp-barra{flex:1;height:6px;border-radius:3px;background:#17150f;overflow:hidden}
#franja .sp-fill{display:block;height:100%;border-radius:3px}
#franja .sp-n{width:26px;flex:none;text-align:right;color:#5f5b50;font-size:.68rem}
#franja .vacio{color:#5f5b50;font-size:.74rem}
#toggle{flex:none;background:#0d0b09;border:none;border-top:1px solid #211f18;color:#6e6a5e;
 cursor:pointer;font-family:inherit;font-size:.68rem;padding:4px;letter-spacing:.5px}
#toggle:hover{color:#c3bfb2}
</style></head><body>
<div id="topbar">
 <div class="izq">
  <h1>&#129744; MAK</h1>
  <div id="tabs">
   <button data-dep="research" class="on">🔬 research</button>
   <button data-dep="codex">💻 codex</button>
  </div>
 </div>
 <div class="der">
  <span class="lk"><a href="/doctrina">📜 doctrina</a><a href="/reflexiones">💭 reflexiones</a><a href="/cuotas">📊 cuotas</a><a href="/relevo">🪑 relevo</a><a href="/genesis">✴️ génesis</a></span>
  <span id="guardia">guardia · <b>0</b> bloqueados · <i>0</i> pasaron</span>
 </div>
</div>
<div id="centro">
 <iframe id="ifr-research" class="on"></iframe>
 <iframe id="ifr-codex"></iframe>
</div>
<button id="toggle" onclick="toggleFranja()">▾ actividad / salud</button>
<div id="franja">
 <div class="col">
  <h3>actividad reciente (research + codex)</h3>
  <div id="f-actividad">cargando…</div>
 </div>
 <div class="col">
  <h3>salud proveedores</h3>
  <div id="f-salud">cargando…</div>
 </div>
</div>
<script>
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;');}

// ── tabs de departamento: cambian el iframe visible, cargan lazy ──
var depActual='research';
var IFR_SRC={research:'http://'+location.hostname+':8890/', codex:'http://'+location.hostname+':8891/'};
function activarDep(dep){
 depActual=dep;
 document.querySelectorAll('#tabs button').forEach(function(b){
   b.classList.toggle('on', b.getAttribute('data-dep')===dep);
 });
 document.querySelectorAll('#centro iframe').forEach(function(f){
   f.classList.toggle('on', f.id==='ifr-'+dep);
 });
 var ifr=document.getElementById('ifr-'+dep);
 if(ifr && !ifr.src){ifr.src=IFR_SRC[dep];}
}
document.querySelectorAll('#tabs button').forEach(function(b){
 b.onclick=function(){activarDep(b.getAttribute('data-dep'));};
});
activarDep('research');

// ── franja inferior: colapsable ──
function toggleFranja(){
 var f=document.getElementById('franja'), t=document.getElementById('toggle');
 var colapsar=!f.classList.contains('colapsada');
 f.classList.toggle('colapsada', colapsar);
 t.textContent=(colapsar?'▸':'▾')+' actividad / salud';
}

// ── actividad (ambos deptos) ──
var COL_ESTADO={listo:'#9db67c',corriendo:'#d4a259','en cola':'#d4a259',BLOQUEADO:'#c46d5e',
 FALLO:'#8a5c52',PAUSADO:'#e0a458',abortado:'#8a8578'};
function cargarActividad(){
 fetch('/api/actividad').then(function(r){return r.json();}).then(function(d){
   var evs=(d.eventos||[]).slice(0,14);
   var g=d.guardia||{};
   document.getElementById('guardia').innerHTML=
     'guardia · <b>'+(g.bloqueados||0)+'</b> bloqueados · <i>'+(g.pasaron||0)+'</i> pasaron';
   var el=document.getElementById('f-actividad');
   if(!evs.length){el.innerHTML='<div class="vacio">sin actividad aun</div>';return;}
   el.innerHTML=evs.map(function(e){
     return '<div class="jb"><span class="d" style="background:'+(COL_ESTADO[e.estado]||'#6e6a5e')+'"></span>'+
       '<span class="dep">['+esc(e.depto)+']</span>'+
       '<span class="t">'+esc(e.texto)+'</span><small>'+esc(e.t)+'</small></div>';
   }).join('');
 }).catch(function(){});
}

// ── salud proveedores ──
function cargarSalud(){
 fetch('/api/salud').then(function(r){return r.json();}).then(function(d){
   var el=document.getElementById('f-salud');
   var provs=d.proveedores||[];
   if(!provs.length){el.innerHTML='<div class="vacio">sin datos de salud aun</div>';return;}
   el.innerHTML=provs.map(function(p){
     var pct=Math.round((p.score||0)*100);
     var col=p.degradado?'#d98c7e':'#9db67c';
     return '<div class="sp-fila">'+
       '<span class="sp-nom">'+esc(p.nombre)+(p.degradado?' <i>degradado</i>':'')+'</span>'+
       '<span class="sp-barra"><span class="sp-fill" style="width:'+pct+'%;background:'+col+'"></span></span>'+
       '<span class="sp-n">'+(p.intentos||0)+'</span></div>';
   }).join('');
 }).catch(function(){});
}

cargarActividad(); cargarSalud();
setInterval(cargarActividad, 15000);
setInterval(cargarSalud, 15000);
</script></body></html>"""


CUOTAS_PAGE = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MAK — cuotas de los modelos</title><style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:radial-gradient(ellipse at 30% 20%,#15130e 0,#0b0a09 60%);
 color:#c9c5b9;font-family:ui-monospace,SFMono-Regular,monospace;min-height:100vh;padding:32px}
h1{color:#d4a259;font-size:1.35rem}
.sub{color:#6e6a5e;font-size:.78rem;margin:6px 0 22px}
.sub a{color:#9db67c;text-decoration:none}
h2{color:#9db67c;font-size:.8rem;text-transform:uppercase;letter-spacing:1px;margin:20px 0 8px}
table{border-collapse:collapse;width:100%;max-width:1050px;background:#12100cd9;
 border:1px solid #2a2820;border-radius:12px;overflow:hidden}
th,td{text-align:left;padding:9px 13px;font-size:.8rem;border-bottom:1px solid #1c1a14}
th{color:#8a8577;font-weight:600;text-transform:uppercase;font-size:.66rem;letter-spacing:.6px}
tr:last-child td{border-bottom:none}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px}
.verde{background:#9db67c;box-shadow:0 0 7px #9db67c}
.ambar{background:#d4a259;box-shadow:0 0 7px #d4a259}
.rojo{background:#c46d5e;box-shadow:0 0 7px #c46d5e}
.local{background:#7ba6a3;box-shadow:0 0 7px #7ba6a3}
.modelo{color:#e2ddd0}
.uso{color:#d4a259;font-variant-numeric:tabular-nums}
.nota{color:#6e6a5e;font-size:.72rem;margin-top:16px;max-width:900px;line-height:1.5}
</style></head><body>
<h1>&#128202; cuotas de los modelos</h1>
<div class="sub">los 2 departamentos · <a href="/">&#8592; la cara</a> · <span id="ts"></span></div>
<div id="tablas">cargando…</div>
<div class="nota" id="nota"></div>
<script>
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;');}
function pinta(d){
  document.getElementById('ts').textContent=d.ts||'';
  document.getElementById('nota').textContent=d.nota||'';
  var deptos={};
  (d.modelos||[]).forEach(function(m){(deptos[m.depto]=deptos[m.depto]||[]).push(m);});
  var html='';
  Object.keys(deptos).forEach(function(dep){
    html+='<h2>'+esc(dep)+'</h2><table><tr><th>estado</th><th>modelo</th>'+
      '<th>proveedor</th><th>límite documentado (free)</th><th>uso hoy</th></tr>';
    deptos[dep].forEach(function(m){
      html+='<tr><td><span class="dot '+esc(m.estado)+'"></span>'+esc(m.estado)+'</td>'+
        '<td class="modelo">'+esc(m.modelo)+'</td>'+
        '<td>'+esc(m.proveedor)+'</td>'+
        '<td>'+esc(m.limite)+'</td>'+
        '<td class="uso">'+(m.usado_hoy||0)+(m.req_dia?(' / '+m.req_dia):'')+'</td></tr>';
    });
    html+='</table>';
  });
  document.getElementById('tablas').innerHTML=html||'<p>sin datos</p>';
}
function tick(){fetch('/api/cuotas').then(function(r){return r.json();}).then(pinta).catch(function(){});}
tick(); setInterval(tick, 20000);
</script></body></html>"""


def _micelio_chunks():
    try:
        with open(INDEX_MICELIO, encoding="utf-8") as f:
            return sum(1 for line in f if line.strip())
    except OSError:
        return 0


def _xio():
    try:
        with open(ESTADO_XIO, encoding="utf-8") as f:
            e = json.load(f)
        e["edad_s"] = int(time.time() - e.get("ts_epoch", time.time()))
        return e
    except (OSError, json.JSONDecodeError):
        return None


def _http_json(url, timeout=2.0):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read(3_000_000).decode("utf-8", "replace"))
    except Exception:  # noqa: BLE001
        return None


# ── feed de actividad (los dos departamentos, con la guardia inline) ──
def _tail_jsonl(path, n=40):
    try:
        with open(path, encoding="utf-8") as f:
            lineas = f.readlines()[-n:]
    except OSError:
        return []
    out = []
    for ln in lineas:
        ln = ln.strip()
        if not ln:
            continue
        try:
            out.append(json.loads(ln))
        except json.JSONDecodeError:
            continue
    return out


def _norm(j, depto):
    texto = j.get("tema") or j.get("pedido") or "(sin titulo)"
    est = j.get("estado", "")
    rz = ""
    if est == "BLOQUEADO":
        rz = j.get("error", "") or "guardia: bloqueado"
    elif est == "FALLO":
        e = (j.get("error", "") or "").strip().replace("\n", " ")
        rz = ("fallo: " + e[-160:]) if e else "fallo"
    elif est == "PAUSADO":
        e = (j.get("error", "") or "").strip().replace("\n", " ")
        rz = "pausado: " + (e[-160:] if e else "esperando humano")
    elif est == "abortado":
        rz = "abortado"
    return {"depto": depto, "texto": texto[:130], "estado": est,
            "t": j.get("t", ""), "job_id": j.get("job_id", ""), "seg": round(j.get("ms", 0) / 1000) or "", "rz": rz[:200]}


def _jobs_depto(port, jsonl, depto):
    live = _http_json("http://127.0.0.1:%d/api/jobs" % port)
    fuente = list(live) if isinstance(live, list) else []
    fuente += _tail_jsonl(jsonl)
    vistos, evs = set(), []
    for j in fuente:
        e = _norm(j, depto)
        k = (e["t"], e["texto"][:60], e["estado"])
        if k in vistos:
            continue
        vistos.add(k)
        evs.append(e)
    return evs


def _eventos_depto(depto, n=40):
    """Lee eventos.jsonl del depto. Linea mala se salta, no vacia todo (mimica _tail_jsonl)."""
    ruta = os.path.join(HOME, depto, "eventos.jsonl")
    try:
        with open(ruta, encoding="utf-8") as f:
            lineas = f.readlines()[-n:]
    except OSError:
        return []
    evs = []
    for ln in lineas:
        ln = ln.strip()
        if not ln:
            continue
        try:
            evs.append(json.loads(ln))
        except json.JSONDecodeError:
            continue
    return evs


def _job_ids_conocidos(depto):
    """Union de job_id conocidos: (a) jobs.jsonl local, (b) /api/jobs en vivo del depto.
    Retorna (ids_set, alguna_fuente_ok_bool) -- ok indica si al menos una fuente respondio."""
    jsonl = RESEARCH_JOBS if depto == "research" else CODEX_JOBS
    port = 8890 if depto == "research" else 8891
    ids = set()
    try:
        with open(jsonl, encoding="utf-8"):
            ok = True
    except OSError:
        ok = False
    for j in _tail_jsonl(jsonl, 200):
        jid = j.get("job_id")
        if jid:
            ids.add(jid)
    live = _http_json("http://127.0.0.1:%d/api/jobs" % port)
    if live is not None:
        ok = True
        fuente = list(live) if isinstance(live, list) else []
        for j in fuente:
            jid = j.get("job_id")
            if jid:
                ids.add(jid)
    return ids, ok


def _marcar_sin_job(evs, ids, ok):
    """Marca (additivo, solo si True) sin_job=True en eventos cuyo job_id no se reconoce.
    Si ok es False (ninguna fuente respondio), no marca nada -- evita falsos positivos."""
    if not ok:
        return evs
    for ev in evs:
        jid = ev.get("job_id")
        if not jid or jid not in ids:
            ev["sin_job"] = True
    return evs


def _actividad():
    evs = _jobs_depto(8890, RESEARCH_JOBS, "research") + \
          _jobs_depto(8891, CODEX_JOBS, "codex")
    evs.sort(key=lambda e: e.get("job_id") or e["t"], reverse=True)
    evs = evs[:26]
    bloq = sum(1 for e in evs if e["estado"] == "BLOQUEADO")
    pausados = sum(1 for e in evs if e["estado"] == "PAUSADO")
    abortados = sum(1 for e in evs if e["estado"] == "abortado")
    pasaron = len(evs) - bloq - pausados - abortados
    return {"eventos": evs, "guardia": {"bloqueados": bloq, "pasaron": pasaron}}


# ── micelio (proxy cacheado del grafo semantico de research) ──
_MIC_CACHE = {"t": 0.0, "data": {"nodes": [], "edges": []}}


def _micelio():
    ahora = time.time()
    if ahora - _MIC_CACHE["t"] < 12 and _MIC_CACHE["data"]["nodes"]:
        return _MIC_CACHE["data"]
    g = _http_json(RESEARCH_URL + "/api/memoria/grafo?umbral=0.5", timeout=5.0)
    if g and "nodes" in g:
        _MIC_CACHE["data"] = g
        _MIC_CACHE["t"] = ahora
    return _MIC_CACHE["data"]


def _trabajo():
    st = {}
    try:
        with open(TRABAJO_STATE) as f:
            st = json.load(f)
    except (OSError, ValueError):
        pass
    ult = ""
    try:
        with open(TRABAJO_LOG, encoding="utf-8") as f:
            ls = [x.strip() for x in f if x.strip()]
        if ls:
            ult = ls[-1][:130]
    except OSError:
        pass
    return {"hoy": st.get("count", 0), "max": _MAXDIA, "ultimo": ult}


def _internet():
    up, since = True, None
    try:
        with open(RED_STATE) as f:
            rs = json.load(f)
        up = bool(rs.get("up", True))
        since = rs.get("since")
    except (OSError, ValueError):
        pass
    out = {"up": up}
    if not up and since:
        out["caido_hace_s"] = int(time.time() - since)
    try:
        with open(RED_LOG, encoding="utf-8") as f:
            evs = [json.loads(x) for x in f if x.strip()]
        vueltas = [e for e in evs if e.get("estado") == "volvio"]
        if vueltas:
            out["ultimo_corte"] = {"ts": vueltas[-1].get("ts"),
                                   "dur_s": vueltas[-1].get("duracion_s")}
    except (OSError, ValueError):
        pass
    return out


def _salud_proveedores():
    """Salud de proveedores LLM (registro de research_lib._salud_registrar).
    Devuelve {"proveedores": [{"nombre","score","intentos","degradado"} ...],
    "desde": ts|null}, orden por score descendente. Lista vacia si el
    archivo no existe, esta corrupto, tiene forma invalida o la ventana
    (6h) ya vencio. Nunca lanza."""
    try:
        with open(SALUD_PROVEEDORES, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {"proveedores": [], "desde": None}
    if not isinstance(data, dict):
        return {"proveedores": [], "desde": None}
    desde = data.get("desde")
    proveedores_raw = data.get("proveedores")
    if not isinstance(desde, (int, float)) or not isinstance(proveedores_raw, dict):
        return {"proveedores": [], "desde": None}
    if time.time() - desde > SALUD_PROVEEDORES_VENTANA:
        return {"proveedores": [], "desde": None}
    out = []
    for nombre, c in proveedores_raw.items():
        if not isinstance(c, dict):
            continue
        successes = c.get("successes", 0) or 0
        timeouts = c.get("timeouts", 0) or 0
        api_errors = c.get("api_errors", 0) or 0
        errors = c.get("errors", 0) or 0
        intentos = successes + timeouts + api_errors + errors
        score = (successes / intentos) if intentos > 0 else 0.0
        degradado = intentos >= 3 and score < 0.5
        out.append({"nombre": nombre, "score": score, "intentos": intentos,
                    "degradado": degradado})
    out.sort(key=lambda p: p["score"], reverse=True)
    return {"proveedores": out, "desde": desde}


def _organismo():
    return {"salud": salud.snapshot(),
            "micelio_chunks": _micelio_chunks(),
            "actividad": _actividad(),
            "trabajo": _trabajo(),
            "internet": _internet(),
            "xio": _xio()}


# ── ejecucion proxeada (research y codex corren abiertos en la LAN Face A) ──
def _ejecutar(depto, modo, texto, densidad):
    texto = (texto or "").strip()
    if not texto:
        return {"ok": False, "error": "texto vacio"}
    if depto == "research":
        url, data = RESEARCH_URL + "/run", {"modo": modo, "tema": texto, "densidad": densidad}
    elif depto == "codex":
        url = CODEX_URL + "/run"
        data = {"modo": modo, "pedido": texto, "densidad": densidad}
    else:
        return {"ok": False, "error": "departamento no ejecutable"}
    try:
        body = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(
            url, data=body, method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, timeout=6) as r:
            return json.loads(r.read(20000).decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:160]}


_RESEARCH_DIRS = ("informes", "paneles", "cadenas", "refutaciones",
                  "correlaciones", "grafos", "memoria")
_CODEX_DIRS = ("piezas", "revisiones")


def _pieza(dir_, id_):
    """Lee el archivo directo del disco (el hub vive en MAK). Busca el id
    entre los dirs conocidos, sin importar el mapeo exacto. id saneado."""
    if not id_ or ".." in id_ or "/" in id_ or "\\" in id_:
        return None
    cands = []
    if dir_ and re.match(r"^[\w.-]+$", dir_):
        cands.append(os.path.join(HOME, "codex", dir_) if dir_ in _CODEX_DIRS
                     else os.path.join(HOME, "research", dir_))
    cands += [os.path.join(HOME, "research", d) for d in _RESEARCH_DIRS]
    cands += [os.path.join(HOME, "codex", d) for d in _CODEX_DIRS]
    for base in cands:
        path = os.path.join(base, id_)
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as f:
                    return f.read(400000)
            except OSError:
                pass
    return None


# ── doctrina / reflexiones / relevo (markdown vivo -> html) ──
def _inline_md(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def _md_html(md):
    out, in_list = [], None

    def cerrar():
        nonlocal in_list
        if in_list:
            out.append("</%s>" % in_list)
            in_list = None

    for raw in md.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            cerrar()
            continue
        if in_list and (raw.startswith("  ") or raw.startswith("\t")) \
                and out and out[-1].endswith("</li>"):
            out[-1] = out[-1][:-5] + " " + _inline_md(line.strip()) + "</li>"
            continue
        if line.startswith("### "):
            cerrar(); out.append("<h3>" + _inline_md(line[4:]) + "</h3>")
        elif line.startswith("## "):
            cerrar(); out.append("<h2>" + _inline_md(line[3:]) + "</h2>")
        elif line.startswith("# "):
            cerrar(); out.append("<h1>" + _inline_md(line[2:]) + "</h1>")
        elif line.strip() == "---":
            cerrar(); out.append("<hr>")
        elif line.startswith("> "):
            cerrar(); out.append("<blockquote>" + _inline_md(line[2:]) + "</blockquote>")
        else:
            m_ol = re.match(r"^(\d+)\.\s+(.*)", line)
            m_ul = re.match(r"^[-*]\s+(.*)", line)
            if m_ol:
                if in_list != "ol":
                    cerrar(); out.append("<ol>"); in_list = "ol"
                out.append("<li>" + _inline_md(m_ol.group(2)) + "</li>")
            elif m_ul:
                if in_list != "ul":
                    cerrar(); out.append("<ul>"); in_list = "ul"
                out.append("<li>" + _inline_md(m_ul.group(1)) + "</li>")
            else:
                cerrar(); out.append("<p>" + _inline_md(line) + "</p>")
    cerrar()
    return "\n".join(out)


_ARTICULO_CSS = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MAK — %s</title><style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:radial-gradient(ellipse at 30%% 15%%,#15130e 0,#0b0a09 62%%);
 color:#c9c5b9;font-family:ui-monospace,SFMono-Regular,monospace;min-height:100vh;padding:40px}
.wrap{max-width:820px;margin:0 auto}
.top{color:#6e6a5e;font-size:.76rem;margin-bottom:26px}
.top a{color:#9db67c;text-decoration:none}
article h1{color:#c98f6a;font-size:1.5rem;margin:26px 0 6px;line-height:1.3}
article h2{color:#9db67c;font-size:1rem;margin:26px 0 8px;text-transform:none;letter-spacing:0}
article h3{color:#b7936f;font-size:.9rem;margin:18px 0 6px}
article p{line-height:1.65;margin:9px 0;color:#c3bfb2;font-size:.9rem}
article ul,article ol{margin:8px 0 8px 22px}
article li{line-height:1.6;margin:5px 0;color:#c3bfb2;font-size:.9rem}
article blockquote{border-left:2px solid #39432c;padding:2px 0 2px 15px;margin:10px 0;
 color:#8a8577;font-style:italic;font-size:.86rem}
article hr{border:none;border-top:1px solid #2a2820;margin:24px 0}
article strong{color:#e2ddd0}article em{color:#b7936f;font-style:italic}
article code{background:#1c1a12;color:#9db67c;padding:1px 5px;border-radius:4px;font-size:.85em}
</style></head><body><div class="wrap">
<div class="top">%s</div>
<article>%s</article>
</div></body></html>"""


def _articulo(titulo, top_html, cuerpo_html):
    return _ARTICULO_CSS % (titulo, top_html, cuerpo_html)


def _md_carpeta_page(carpeta, ruta, etiqueta, sel):
    try:
        docs = sorted(f for f in os.listdir(carpeta) if f.endswith(".md"))
    except OSError:
        docs = []
    if sel not in docs:
        sel = docs[0] if docs else ""
    cuerpo = "(vacío)"
    if sel:
        try:
            with open(os.path.join(carpeta, sel), encoding="utf-8") as f:
                cuerpo = _md_html(f.read())
        except OSError:
            cuerpo = "<p>(no se pudo leer %s)</p>" % html.escape(sel)

    def nombre(d):
        return html.escape(d.replace("doctrina_", "").replace("reflexion_", "")
                           .replace(".md", "").replace("_", " "))
    nav = " · ".join(
        '<a href="%s?d=%s" style="color:%s">%s</a>' % (
            ruta, urllib.parse.quote(d), "#c98f6a" if d == sel else "#6e6a5e", nombre(d))
        for d in docs) or "<span style='color:#5f5b50'>—</span>"
    top = '<a href="/">&#8592; la cara</a> &middot; %s: %s' % (etiqueta, nav)
    return _articulo(etiqueta, top, cuerpo)


def _relevo_page():
    try:
        with open(RELEVO, encoding="utf-8") as f:
            cuerpo = _md_html(f.read())
    except OSError:
        cuerpo = "<p>(RELEVO_MAK.md no encontrado en ~)</p>"
    top = ('<a href="/">&#8592; la cara</a> &middot; relevo del rol &middot; '
           '<a href="/doctrina">doctrina</a> &middot; <a href="/reflexiones">reflexiones</a>')
    return _articulo("relevo", top, cuerpo)


class H(BaseHTTPRequestHandler):
    server_version = "MAK-Hub/2.0"

    def _send(self, body, ctype="text/html; charset=utf-8", code=200):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, obj, code=200):
        self._send(json.dumps(obj, ensure_ascii=False),
                   "application/json; charset=utf-8", code)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        p = u.path
        if p == "/api/organismo":
            try:
                return self._json(_organismo())
            except Exception as e:  # noqa: BLE001
                return self._json({"error": str(e)[:200]})
        if p == "/api/micelio":
            return self._json(_micelio())
        if p == "/api/eventos":
            q = urllib.parse.parse_qs(u.query)
            depto = (q.get("depto") or [""])[0]
            if depto not in ("research", "codex"):
                return self._json({"eventos": []})
            evs = _eventos_depto(depto)
            ids, ok = _job_ids_conocidos(depto)
            evs = _marcar_sin_job(evs, ids, ok)
            return self._json({"eventos": evs})
        if p == "/api/actividad":
            try:
                return self._json(_actividad())
            except Exception as e:  # noqa: BLE001
                return self._json({"error": str(e)[:200], "eventos": [], "guardia": {}})
        if p == "/api/salud":
            try:
                return self._json(_salud_proveedores())
            except Exception as e:  # noqa: BLE001
                return self._json({"error": str(e)[:200], "proveedores": [], "desde": None})
        if p == "/api/cuotas":
            try:
                return self._json(cuotas.snapshot())
            except Exception as e:  # noqa: BLE001
                return self._json({"error": str(e)[:200], "modelos": []})
        if p == "/pieza":
            q = urllib.parse.parse_qs(u.query)
            txt = _pieza((q.get("dir") or [""])[0], (q.get("id") or [""])[0])
            return self._send(txt if txt is not None else "(no se pudo abrir)",
                              "text/plain; charset=utf-8", 200 if txt is not None else 404)
        if p == "/cuotas":
            return self._send(CUOTAS_PAGE)
        if p == "/doctrina":
            sel = (urllib.parse.parse_qs(u.query).get("d") or [""])[0]
            return self._send(_md_carpeta_page(DOCTRINA_DIR, "/doctrina", "doctrina viva", sel))
        if p == "/reflexiones":
            sel = (urllib.parse.parse_qs(u.query).get("d") or [""])[0]
            return self._send(_md_carpeta_page(REFLEXIONES_DIR, "/reflexiones", "reflexiones", sel))
        if p == "/relevo":
            return self._send(_relevo_page())
        if p == "/genesis":
            try:
                with open(GENESIS, encoding="utf-8") as f:
                    texto = f.read()
            except OSError:
                texto = "(GENESIS.md no encontrado)"
            cuerpo = ("<body style='background:#0b0a09;color:#c9c5b9;font-family:"
                      "ui-monospace,monospace;padding:40px'><pre style='white-space:"
                      "pre-wrap;max-width:860px;line-height:1.55'>"
                      + html.escape(texto) + "</pre></body>")
            return self._send("<!doctype html><meta charset='utf-8'>" + cuerpo)
        if p == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        return self._send(PAGINA)

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/api/ejecutar":
            largo = min(int(self.headers.get("Content-Length") or 0), 12000)
            try:
                body = json.loads(self.rfile.read(largo).decode("utf-8", "replace"))
            except (ValueError, TypeError):
                return self._json({"ok": False, "error": "json invalido"}, 400)
            depto = str(body.get("depto", ""))
            modo = str(body.get("modo", ""))[:40]
            texto = str(body.get("texto", ""))[:2000]
            densidad = body.get("densidad", "medio")
            if densidad not in ("corto", "medio", "largo"):
                densidad = "medio"
            return self._json(_ejecutar(depto, modo, texto, densidad))
        return self._send("no", "text/plain", 404)

    def log_message(self, fmt, *args):
        pass


class Servidor(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    server = Servidor(("0.0.0.0", PORT), H)

    def apagar(signum, frame):
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, apagar)
    signal.signal(signal.SIGINT, apagar)
    print("[hub] la cara del organismo en http://0.0.0.0:%d" % PORT, flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
