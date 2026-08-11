#!/usr/bin/env python3
"""hub.py -- LA CARA del organismo MAK (puerto 8900).

Marco fino alrededor del editor real de cada departamento, embebido a
pantalla completa via iframe. Topbar con tabs [research] [codex] que
cambian el iframe visible; franja inferior colapsable con actividad
reciente de ambos deptos y salud de proveedores. El hub proxea la
ejecucion real de research/codex: el navegador solo habla con :8900 para
el marco, pero el iframe habla directo con :8890/:8891 (LAN privada
Face A, sin token).

Rutas: / (cara) · /api/organismo · /api/micelio · /api/archivo · /api/ejecutar (POST) ·
/api/ideas (GET+POST) · /pieza · /api/salud · /api/actividad · /cuotas ·
/doctrina · /reflexiones · /relevo · /genesis
"""
import html
import json
import math
import mimetypes
import os
import re
import signal
import sys
import threading
import time
import urllib.parse
import urllib.request
import uuid
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import salud  # noqa: E402
import copilot  # noqa: E402
import providers  # noqa: E402
import discernment  # noqa: E402
import cuotas  # noqa: E402
import ideas  # noqa: E402
import contrato_archivo  # noqa: E402
try:
    import ledger as _ledger  # noqa: E402
except Exception:  # noqa: BLE001 - hub stays alive without ledger data
    _ledger = None
try:
    import backlog as _backlog  # noqa: E402
except Exception:  # noqa: BLE001 - hub must stay alive if audit is unavailable
    _backlog = None
try:
    import revision as _revision  # noqa: E402
except Exception:  # noqa: BLE001 - visual review is optional
    _revision = None
try:
    import revision_episodios as _episode_revision  # noqa: E402
except Exception:  # noqa: BLE001 - episode review is optional
    _episode_revision = None
try:
    import visual_index as _visual_index  # noqa: E402
except Exception:  # noqa: BLE001 - visual layer is an optional projection
    _visual_index = None
try:
    import xio_evidence as _xio_evidence  # noqa: E402
except Exception:  # noqa: BLE001 - XIO evidence remains optional
    _xio_evidence = None

PORT = int(os.environ.get("HUB_PORT", "8900"))
HOME = os.path.expanduser("~")
_percepcion = None
_percepcion_root = os.path.join(HOME, "flujo", "cultura", "mak_curatoria")
if os.path.isdir(_percepcion_root):
    try:
        sys.path.insert(0, _percepcion_root)
        import percepcion as _percepcion  # noqa: E402
    except Exception:  # noqa: BLE001 - vision remains optional
        _percepcion = None
INDEX_MICELIO = os.path.join(HOME, "research/memoria/index.jsonl")
ESTADO_XIO = os.path.join(HOME, "xio_puente/estado.json")
GENESIS = os.path.join(HOME, "GENESIS.md")
DOCTRINA_DIR = os.path.join(HOME, "plataforma/doctrina")
REFLEXIONES_DIR = os.path.join(HOME, "plataforma/reflexiones")
RESEARCH_JOBS = os.path.join(HOME, "research/jobs.jsonl")
CODEX_JOBS = os.path.join(HOME, "codex/jobs.jsonl")
RELEVO = os.path.join(HOME, "RELEVO_MAK.md")
PORTFOLIO_ROOT = os.path.abspath(os.environ.get(
    "MAK_PORTFOLIO_ROOT", os.path.join(HOME, "flujo", "iskvw")))
PORTFOLIO_INBOX = os.path.join(
    HOME, "plataforma/director_runs/portfolio-editor-20260808/PORTFOLIO_INBOX.json")
PORTFOLIO_MEDIA_ROOT = os.path.join(HOME, "portfolio_media/media")
PORTFOLIO_CONTACT_SHEETS = os.path.join(PORTFOLIO_MEDIA_ROOT, "_contact_sheets")
PORTFOLIO_SELECTIONS = os.path.join(
    HOME, "plataforma/director_runs/portfolio-editor-20260808/selections.jsonl")
PORTFOLIO_CLASSIFICATIONS = os.path.join(
    HOME, "plataforma/director_runs/portfolio-editor-20260808/classifications.jsonl")
MESA_INBOX_FIELDS = (
    "id", "tipo_contenido", "fecha", "publicacion_id", "asset_path",
    "asset_available", "selection", "classification",
)
PORTFOLIO_BOARDS = os.path.join(
    HOME, "plataforma/director_runs/portfolio-editor-20260808/boards.json")
PORTFOLIO_CONNECTIONS = os.path.join(
    HOME, "plataforma/director_runs/portfolio-editor-20260808/connections.jsonl")
PORTFOLIO_FEEDBACK = os.path.join(
    HOME, "plataforma/director_runs/portfolio-editor-20260808/copilot_feedback.jsonl")
PORTFOLIO_EXTERNAL = os.path.join(
    HOME, "plataforma/director_runs/portfolio-editor-20260808/copilot_external.jsonl")
PORTFOLIO_EXTERNAL_REVIEW = os.path.join(
    HOME, "plataforma/derived/instagram-external/round-20260810.jsonl")
PORTFOLIO_VISION = os.path.join(
    HOME, "plataforma/director_runs/portfolio-editor-20260808/vision_features.jsonl")
PORTFOLIO_TRIANGULATION = os.path.join(
    HOME, "plataforma/director_runs/instagram-triangulacion-20260807/faro-triangulation-watsonx.normalized.json")
PORTFOLIO_TRIANGULATION_REVIEW = os.path.join(
    HOME, "plataforma/director_runs/instagram-triangulacion-20260807/human_resolutions.jsonl")
PORTFOLIO_VISUAL_INDEX_ROOT = os.path.abspath(os.environ.get(
    "MAK_VISUAL_INDEX_ROOT", os.path.join(HOME, "plataforma/derived/visual-index")))
PORTFOLIO_XIO_SHOW_ROOT = os.path.abspath(os.environ.get(
    "MAK_XIO_SHOW_ROOT", os.path.join(HOME, "flujo", "xio", "show_kit")))
LEGACY_RESCUE_REVIEW = os.path.join(
    HOME, "plataforma/director_runs/faro-report-action-queue-20260808/RESCUE_ADJUDICATED.json")
LEGACY_REPORT_RUNS = os.path.join(HOME, "plataforma/director_runs")
RESEARCH_URL = "http://127.0.0.1:8890"
CODEX_URL = "http://127.0.0.1:8891"
TRABAJO_STATE = os.path.join(HOME, "plataforma/.trabajo_state.json")
RED_STATE = os.path.join(HOME, "plataforma/.red_state.json")
RED_LOG = os.path.join(HOME, "plataforma/logs/red.jsonl")
TRABAJO_LOG = os.path.join(HOME, "plataforma/logs/trabajo.log")
COMMON_LEDGER = os.path.join(HOME, "plataforma/common_ledger.jsonl")
SALUD_PROVEEDORES = os.path.join(HOME, "research/salud_proveedores.json")
SALUD_PROVEEDORES_VENTANA = 6 * 3600
PORTFOLIO_CLASSIFICATION_ALLOWED = {
    "triage": {"work", "record", "review", "discard"},
    "lane": {"rd", "iskvw", "mak", "personal", "research", "system"},
    "ownership": {"personal", "client"},
    "purpose": {"expression", "research", "narrative", "commercial",
                 "expositive", "editorial"},
    "nature": {"2d", "3d", "hybrid"},
    "format": {"video", "illustration", "print", "web"},
    "context_kind": {"artist", "venue", "event", "client", "collab", "record"},
}
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
#pan-ideas{position:absolute;inset:0;overflow-y:auto;padding:26px 30px;display:none}
#pan-ideas.on{display:block}
#pan-ideas .intro{color:#6e6a5e;font-size:.74rem;margin-bottom:14px;max-width:640px;line-height:1.5}
#pan-ideas .caja{display:flex;gap:8px;margin-bottom:8px;max-width:820px}
#pan-ideas textarea{flex:1;background:#0d0b09;border:1px solid #2a2820;border-radius:6px;
 color:#c9c5b9;font-family:inherit;font-size:.8rem;padding:10px;resize:vertical;min-height:62px}
#pan-ideas textarea:focus{outline:none;border-color:#39432c}
#pan-ideas button{background:#1a2418;border:1px solid #39432c;color:#9db67c;font-family:inherit;
 font-size:.74rem;padding:7px 14px;border-radius:6px;cursor:pointer;height:fit-content}
#pan-ideas button:hover{border-color:#5a6a44}
#pan-ideas button.sec{background:transparent;border-color:#2a2820;color:#8a8577;
 font-size:.66rem;padding:3px 9px}
#pan-ideas #aviso{color:#d4a259;font-size:.72rem;margin-bottom:16px;min-height:1em;max-width:820px}
#pan-ideas .idea{border:1px solid #211f18;border-radius:8px;padding:13px 15px;margin-bottom:11px;
 background:#0c0a09;max-width:820px}
#pan-ideas .idea .txt{font-size:.84rem;color:#c9c5b9;line-height:1.45}
#pan-ideas .idea .meta{color:#5f5b50;font-size:.66rem;margin-top:5px;display:flex;gap:10px;
 align-items:center;flex-wrap:wrap}
#pan-ideas .idea .meta .est{color:#9db67c}
#pan-ideas .rel{margin-top:10px;border-top:1px solid #17150f;padding-top:8px}
#pan-ideas .rel h4{color:#6e6a5e;font-size:.6rem;text-transform:uppercase;letter-spacing:1px;
 margin-bottom:6px}
#pan-ideas .rel .r{font-size:.73rem;padding:3px 0;display:flex;gap:8px;align-items:baseline}
#pan-ideas .rel .r .obra{color:#d4a259;flex:none;font-size:.62rem}
#pan-ideas .rel .r .ens{color:#5f5b50;flex:none;font-size:.62rem}
#pan-ideas .rel .r .ti{color:#c3bfb2;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#pan-ideas .rel .r .sc{color:#5f5b50;font-size:.64rem;margin-left:auto;flex:none}
#pan-ideas .vacio{color:#5f5b50;font-size:.76rem}
@media(max-width:700px){#pan-ideas{padding:16px 14px}#pan-ideas .caja{flex-direction:column}}
#pan-render{position:absolute;inset:0;overflow-y:auto;padding:26px 30px;display:none}
#pan-render.on{display:block}
#pan-render .intro{color:#6e6a5e;font-size:.74rem;margin-bottom:14px;max-width:680px;line-height:1.5}
#pan-render .cfg{border:1px solid #211f18;border-radius:8px;padding:13px 15px;
 margin-bottom:14px;background:#0c0a09;max-width:820px;display:flex;flex-wrap:wrap;
 gap:14px;align-items:center}
#pan-render .cfg label{font-size:.72rem;color:#8a8577;display:flex;gap:6px;align-items:center}
#pan-render .cfg input[type=text]{background:#0b0a08;border:1px solid #2a2820;border-radius:5px;
 color:#c9c5b9;font-family:inherit;font-size:.74rem;padding:5px 8px;width:150px}
#pan-render .cfg input[type=text]:focus{outline:none;border-color:#39432c}
#pan-render button{background:#1a2418;border:1px solid #39432c;color:#9db67c;font-family:inherit;
 font-size:.72rem;padding:6px 13px;border-radius:6px;cursor:pointer}
#pan-render button:hover{border-color:#5a6a44}
#pan-render #r-aviso{color:#d4a259;font-size:.72rem;margin-bottom:14px;min-height:1em}
#pan-render .rd{border:1px solid #211f18;border-radius:8px;padding:13px 15px;
 margin-bottom:11px;background:#0c0a09;max-width:820px}
#pan-render .rd .cab{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
#pan-render .rd .num{color:#9db67c;font-size:.8rem}
#pan-render .rd .mal{color:#c46d5e}
#pan-render .rd .ts{color:#5f5b50;font-size:.66rem;margin-left:auto}
#pan-render .rd .dest{color:#d4a259;font-size:.72rem;margin-top:5px;word-break:break-all}
#pan-render .rd .link{color:#6e6a5e;font-size:.68rem;margin-top:3px;word-break:break-all}
#pan-render .datos{margin-top:9px;border-top:1px solid #17150f;padding-top:8px;font-size:.73rem}
#pan-render .datos h4{color:#6e6a5e;font-size:.6rem;text-transform:uppercase;
 letter-spacing:1px;margin-bottom:5px}
#pan-render .datos .f{color:#c3bfb2;padding:2px 0}
#pan-render .datos .f b{color:#8a8577;font-weight:400}
#pan-render .vacio{color:#5f5b50;font-size:.74rem}
#pan-decisiones{position:absolute;inset:0;overflow-y:auto;padding:26px 30px;display:none}
#pan-decisiones.on{display:block}
#pan-decisiones .intro{color:#6e6a5e;font-size:.74rem;margin-bottom:14px;max-width:680px;line-height:1.5}
#pan-decisiones .metricas{display:flex;gap:9px;flex-wrap:wrap;max-width:820px;margin-bottom:16px}
#pan-decisiones .metrica{border:1px solid #211f18;border-radius:7px;padding:9px 12px;background:#0c0a09;
 min-width:112px;color:#8a8577;font-size:.68rem}
#pan-decisiones .metrica b{display:block;color:#9db67c;font-size:1.05rem;margin-top:3px}
#pan-decisiones .fila{border:1px solid #211f18;border-radius:8px;padding:11px 13px;margin-bottom:9px;
 background:#0c0a09;max-width:820px;font-size:.73rem}
#pan-decisiones .fila .cab{display:flex;gap:9px;align-items:baseline;flex-wrap:wrap}
#pan-decisiones .fila .lane{color:#d4a259}
#pan-decisiones .fila .decision{color:#9db67c}
#pan-decisiones .fila .owner{color:#5f5b50;margin-left:auto}
#pan-decisiones .fila .accion{color:#c3bfb2;margin-top:6px;line-height:1.4}
#pan-render .pend-cab{color:#d4a259;font-size:.7rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px}
#pan-render .rd.pend{border-color:#4a3a26;background:#100c08}
#pan-render .rd.pend .motivo{color:#d4a259;font-size:.75rem;margin-top:6px;line-height:1.45}
#pan-render #r-pendientes{margin-bottom:20px}
@media(max-width:700px){#pan-render{padding:16px 14px}}
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
   <button data-dep="ideas">💡 ideas</button>
   <button data-dep="render">🖼 render</button>
  <button data-dep="decisiones">◈ decisiones</button>
  <button data-dep="portafolio">✦ portafolio</button>
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
 <iframe id="ifr-portafolio"></iframe>
 <div id="pan-ideas">
  <div class="intro">Escribí lo que estás pensando. El archivo te dice con qué se
   relaciona — tus obras van marcadas aparte de los ensayos de MAK. Si te sirve,
   mandalo a la cola: una idea tuya entra adelante de todo lo automático.</div>
  <div class="caja">
   <textarea id="i-texto" placeholder="una idea, una pregunta, algo que querés empezar…"></textarea>
   <button onclick="anotarIdea()">anotar</button>
  </div>
  <div id="aviso"></div>
  <div id="i-lista">cargando…</div>
 </div>
 <div id="pan-render">
  <div class="intro">El puente atiende los issues de flyer solo, por cron.
   Acá se configura, se ve qué renderizó y qué data sacó el departamento de
   cada flyer. Si una pieza no muestra data, es que la curatoría todavía no
   la percibió — no que no exista.</div>
  <div id="r-config" class="cfg">cargando…</div>
  <div id="r-aviso"></div>
  <div id="r-pendientes"></div>
  <div id="r-lista">cargando…</div>
 </div>
 <div id="pan-decisiones">
  <div class="intro">La cola no mide actividad: muestra decisiones utilizables. Las entradas históricas se proyectan a Obra, Trabajo o Sistema sin reescribirlas. Solo lo que tiene siguiente acción puede avanzar.</div>
  <div id="d-metricas" class="metricas">cargando…</div>
  <div id="d-lista">cargando…</div>
 </div>
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
var IFR_SRC={research:'http://'+location.hostname+':8890/', codex:'http://'+location.hostname+':8891/', portafolio:'/portafolio/'};
function activarDep(dep){
 depActual=dep;
 document.querySelectorAll('#tabs button').forEach(function(b){
   b.classList.toggle('on', b.getAttribute('data-dep')===dep);
 });
 document.querySelectorAll('#centro iframe').forEach(function(f){
   f.classList.toggle('on', f.id==='ifr-'+dep);
 });
 // 'ideas', 'render' y 'decisiones' son paneles propios del hub.
 document.getElementById('pan-ideas').classList.toggle('on', dep==='ideas');
 document.getElementById('pan-render').classList.toggle('on', dep==='render');
 document.getElementById('pan-decisiones').classList.toggle('on', dep==='decisiones');
 if(dep==='ideas'){cargarIdeas();return;}
 if(dep==='render'){cargarRender();return;}
 if(dep==='decisiones'){cargarDecisiones();return;}
 var ifr=document.getElementById('ifr-'+dep);
 if(ifr && !ifr.src){ifr.src=IFR_SRC[dep];}
}
document.querySelectorAll('#tabs button').forEach(function(b){
 b.onclick=function(){activarDep(b.getAttribute('data-dep'));};
});
activarDep('research');

// ── ideas: intervenir, no mirar ──
function pintarIdeas(ds){
 var el=document.getElementById('i-lista');
 if(!ds.length){el.innerHTML='<div class="vacio">Todavía no hay ideas anotadas.</div>';return;}
 el.innerHTML=ds.map(function(d){
   var rel=(d.relacionadas||[]);
   // Sin relaciones no se inventa una vecindad: se dice que no hubo.
   var relHtml = rel.length
     ? '<div class="rel"><h4>se relaciona con</h4>'+rel.map(function(r){
         return '<div class="r">'+(r.es_obra
             ? '<span class="obra">obra tuya</span>'
             : '<span class="ens">MAK</span>')+
           '<span class="ti">'+esc(r.titulo)+'</span>'+
           '<span class="sc">'+esc(r.score)+'</span></div>';
       }).join('')+'</div>'
     : '<div class="rel"><h4>se relaciona con</h4><div class="vacio">'+
       'El micelio no devolvió nada para esta idea.</div></div>';
   var acc = d.estado==='encargada'
     ? ''
     : '<button class="sec" onclick="encargarIdea(\''+esc(d.id)+'\',\'research\')">'+
       'mandar a research</button>'+
       '<button class="sec" onclick="encargarIdea(\''+esc(d.id)+'\',\'codex\')">'+
       'mandar a codex</button>';
   return '<div class="idea"><div class="txt">'+esc(d.texto)+'</div>'+
     '<div class="meta"><span class="est">'+esc(d.estado||'')+'</span>'+
     '<span>'+esc(d.ts||'')+'</span>'+acc+'</div>'+relHtml+'</div>';
 }).join('');
}
function cargarIdeas(){
 fetch('/api/ideas').then(function(r){return r.json();}).then(function(d){
   if(d.error){document.getElementById('i-lista').innerHTML=
     '<div class="vacio">No se pudo leer las ideas: '+esc(d.error)+'</div>';return;}
   pintarIdeas(d.ideas||[]);
 }).catch(function(){document.getElementById('i-lista').innerHTML=
   '<div class="vacio">No se pudo leer las ideas.</div>';});
}
function _post(cuerpo){
 return fetch('/api/ideas',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify(cuerpo)}).then(function(r){return r.json();});
}
function anotarIdea(){
 var ta=document.getElementById('i-texto'), av=document.getElementById('aviso');
 var t=ta.value.trim();
 if(!t){av.textContent='Escribí algo primero.';return;}
 av.textContent='anotando…';
 _post({accion:'anotar',texto:t}).then(function(d){
   // El aviso de ideas.py se muestra tal cual: si no se pudo relacionar, se dice.
   av.textContent = d.ok ? (d.aviso||'') : ('No se anotó: '+(d.error||''));
   if(d.ok){ta.value='';}
   cargarIdeas();
 }).catch(function(){av.textContent='No se pudo hablar con el hub.';});
}
function encargarIdea(id,depto){
 var av=document.getElementById('aviso');
 _post({accion:'encargar',id:id,depto:depto}).then(function(d){
   av.textContent = d.ok
     ? ('A la cola de '+depto+', al frente: '+(d.encargada||''))
     : ('No se encargó: '+(d.error||''));
   cargarIdeas();
 }).catch(function(){av.textContent='No se pudo hablar con el hub.';});
}

// ── departamento de render ──
function pintarConfigRender(c, pend){
 document.getElementById('r-config').innerHTML =
  '<label><input type="checkbox" id="rc-activo"'+(c.activo?' checked':'')+'> atiende issues</label>'+
  '<label>destino <input type="text" id="rc-remoto" value="'+esc(c.remoto)+'">:'+
  '<input type="text" id="rc-carpeta" value="'+esc(c.carpeta)+'"></label>'+
  '<label>etiqueta <input type="text" id="rc-etiqueta" value="'+esc(c.etiqueta)+'"></label>'+
  '<label><input type="checkbox" id="rc-depto"'+(c.al_departamento?' checked':'')+
    '> manda el flyer al departamento</label>'+
  '<label><input type="checkbox" id="rc-pausa"'+(c.pausar_percepcion?' checked':'')+
    '> pausa la percepción para renderizar</label>'+
  '<button onclick="guardarConfigRender()">guardar</button>'+
  '<span style="color:#5f5b50;font-size:.7rem">'+pend+' en la bandeja</span>';
}
// Lo pendiente va ARRIBA y con su motivo. Es lo unico que necesita al usuario:
// lo hecho ya esta en su Drive.
function pintarPendientes(ps){
 var el=document.getElementById('r-pendientes');
 if(!ps.length){el.innerHTML='';return;}
 el.innerHTML='<div class="pend-cab">'+ps.length+' pendiente'+(ps.length>1?'s':'')+
   ' — necesitan Windows</div>'+ps.map(function(p){
   return '<div class="rd pend"><div class="cab">'+
     '<span class="num mal">#'+esc(p.issue)+' · '+esc(p.code||'')+'</span>'+
     (p.imagen>1?'<span style="color:#5f5b50;font-size:.68rem">imagen '+esc(p.imagen)+'</span>':'')+
     '<span class="ts">'+esc(p.ts)+'</span></div>'+
     '<div class="motivo">'+esc(p.pendiente||'sin motivo')+'</div>'+
     '<div class="link">'+esc(p.url)+'</div></div>';
 }).join('');
}
function pintarRenders(hs){
 var el=document.getElementById('r-lista');
 if(!hs.length){el.innerHTML='<div class="vacio">Todavía no renderizó ningún issue.</div>';return;}
 el.innerHTML=hs.map(function(h){
   var d=h.datos;
   // Sin ficha no se afirma que la data entro: se dice que falta percibirla.
   var datos = d
     ? '<div class="datos"><h4>data extraída del flyer</h4>'+
       (d.headliners&&d.headliners.length?'<div class="f"><b>artistas:</b> '+
          esc(d.headliners.join(', '))+'</div>':'')+
       (d.fecha?'<div class="f"><b>fecha:</b> '+esc(d.fecha)+'</div>':'')+
       (d.lugar?'<div class="f"><b>lugar:</b> '+esc(d.lugar)+'</div>':'')+
       (d.productora?'<div class="f"><b>productora:</b> '+esc(d.productora)+'</div>':'')+
       (d.descripcion?'<div class="f">'+esc(d.descripcion)+'</div>':'')+
       '</div>'
     : '<div class="datos"><h4>data extraída del flyer</h4>'+
       '<div class="vacio">La curatoría todavía no percibió este flyer.</div></div>';
   return '<div class="rd"><div class="cab">'+
     '<span class="num">#'+esc(h.issue)+' · '+esc(h.code||'')+'</span>'+
     (h.imagen>1?'<span style="color:#5f5b50;font-size:.68rem">imagen '+esc(h.imagen)+
       ' del carrusel</span>':'')+
     '<span class="ts">'+esc(h.ts)+'</span></div>'+
     (h.destino?'<div class="dest">'+esc(h.destino)+'</div>':'')+
     '<div class="link">'+esc(h.url)+'</div>'+datos+'</div>';
 }).join('');
}
function cargarRender(){
 fetch('/api/render').then(function(r){return r.json();}).then(function(d){
   if(d.error){document.getElementById('r-lista').innerHTML=
     '<div class="vacio">No se pudo leer el departamento: '+esc(d.error)+'</div>';return;}
   pintarConfigRender(d.config||{}, d.pendientes_bandeja||0);
   pintarPendientes(d.pendientes||[]);
   pintarRenders(d.hechos||[]);
 }).catch(function(){document.getElementById('r-lista').innerHTML=
   '<div class="vacio">No se pudo hablar con el hub.</div>';});
}
function guardarConfigRender(){
 var av=document.getElementById('r-aviso');
 var cuerpo={
   activo:document.getElementById('rc-activo').checked,
   remoto:document.getElementById('rc-remoto').value.trim(),
   carpeta:document.getElementById('rc-carpeta').value.trim(),
   etiqueta:document.getElementById('rc-etiqueta').value.trim(),
   al_departamento:document.getElementById('rc-depto').checked,
   pausar_percepcion:document.getElementById('rc-pausa').checked
 };
 av.textContent='guardando…';
 fetch('/api/render',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify(cuerpo)}).then(function(r){return r.json();}).then(function(d){
   av.textContent = d.ok ? 'Guardado. Vale desde la próxima pasada del cron.'
                         : ('No se guardó: '+(d.error||''));
   cargarRender();
 }).catch(function(){av.textContent='No se pudo hablar con el hub.';});
}

function cargarDecisiones(){
 fetch('/api/decisiones').then(function(r){return r.json();}).then(function(d){
   if(d.error){throw new Error(d.error);}
   var lanes=d.by_lane||{}, decs=d.by_decision||{};
   document.getElementById('d-metricas').innerHTML=
     '<div class="metrica">total<b>'+esc(d.total||0)+'</b></div>'+
     '<div class="metrica">obra<b>'+esc(lanes.obra||0)+'</b></div>'+
     '<div class="metrica">trabajo<b>'+esc(lanes.trabajo||0)+'</b></div>'+
     '<div class="metrica">sistema<b>'+esc(lanes.sistema||0)+'</b></div>'+
     '<div class="metrica">revisar<b>'+esc(decs.revisar||0)+'</b></div>'+
     '<div class="metrica">humano<b>'+esc(d.pending_human||0)+'</b></div>';
   var rows=d.last||[];
   document.getElementById('d-lista').innerHTML=rows.length ? rows.map(function(row){
     var reviewLink = row.lane==='obra'
       ? '<a href="/portafolio/" target="_blank" rel="noreferrer" style="color:#d4a259;margin-left:8px">abrir editor</a>'
       : '';
     return '<div class="fila"><div class="cab"><span class="lane">'+esc(row.lane||'sistema')+
       '</span><span class="decision">'+esc(row.decision||'revisar')+'</span>'+
       '<span class="owner">'+esc(row.owner||'MAK')+'</span></div>'+
       '<div class="accion">'+esc(row.next_action||row.purpose||'sin siguiente accion documentada')+
       reviewLink+'</div></div>';
   }).join('') : '<div class="vacio">La cola todavía está vacía.</div>';
 }).catch(function(){
   document.getElementById('d-lista').innerHTML='<div class="vacio">No se pudo leer la cola de decisiones.</div>';
 });
}

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


def _portfolio_file(relative):
    """Resolve one read-only portfolio asset under the iskvw root."""
    root = os.path.realpath(PORTFOLIO_ROOT)
    candidate = os.path.realpath(os.path.join(root, urllib.parse.unquote(relative)))
    try:
        inside = os.path.commonpath((root, candidate)) == root
    except ValueError:
        inside = False
    if not inside or not os.path.isfile(candidate):
        return None
    return candidate


def _portfolio_selections():
    result = {}
    try:
        with open(PORTFOLIO_SELECTIONS, encoding="utf-8") as fh:
            for line in fh:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                item_id = str(row.get("item_id", "")).strip()
                if item_id:
                    result[item_id] = row
    except OSError:
        pass
    return result


def _portfolio_classifications():
    result = {}
    try:
        with open(PORTFOLIO_CLASSIFICATIONS, encoding="utf-8") as fh:
            for line in fh:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                item_id = str(row.get("item_id", "")).strip()
                if item_id and isinstance(row.get("fields"), dict):
                    result[item_id] = row
    except OSError:
        pass
    return result


def _portfolio_selection_history(item_id=""):
    requested = str(item_id or "").strip()
    return [row for row in _portfolio_jsonl(PORTFOLIO_SELECTIONS)
            if row.get("item_id")
            and (not requested or str(row.get("item_id")) == requested)]


def _portfolio_classification_history(item_id=""):
    requested = str(item_id or "").strip()
    return [row for row in _portfolio_jsonl(PORTFOLIO_CLASSIFICATIONS)
            if row.get("item_id")
            and (not requested or str(row.get("item_id")) == requested)]


def _portfolio_vision():
    result = {}
    try:
        with open(PORTFOLIO_VISION, encoding="utf-8") as fh:
            for line in fh:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                item_id = str(row.get("item_id", "")).strip()
                features = row.get("features")
                if item_id and isinstance(features, dict):
                    result[item_id] = row
    except OSError:
        pass
    return result


def _portfolio_inbox(compact=False):
    try:
        with open(PORTFOLIO_INBOX, encoding="utf-8") as fh:
            payload = json.load(fh)
    except (OSError, ValueError):
        return {"schema": "faro-portfolio-inbox-v1", "total": 0,
                "available_assets": 0, "items": [], "error": "inbox_no_disponible"}
    if not isinstance(payload, dict):
        return {"schema": "faro-portfolio-inbox-v1", "total": 0,
                "available_assets": 0, "items": [], "error": "inbox_invalido"}
    raw_items = payload.get("items")
    if not isinstance(raw_items, list):
        raw_items = []
    items = []
    for raw_item in raw_items:
        if not isinstance(raw_item, dict):
            continue
        item = dict(raw_item)
        item_id = str(item.get("id", "")).strip()
        if not item_id:
            continue
        item["id"] = item_id
        items.append(item)
    payload["items"] = items
    selections = _portfolio_selections()
    classifications = _portfolio_classifications()
    vision = _portfolio_vision()
    for item in payload.get("items", []):
        item["selection"] = (selections.get(item.get("id")) or {}).get(
            "decision", "pendiente")
        item["classification"] = (classifications.get(item.get("id")) or {}).get(
            "fields", {})
        item["vision_features"] = (vision.get(item.get("id")) or {}).get(
            "features", {})
    payload["selected_count"] = sum(
        1 for item in payload.get("items", []) if item["selection"] == "seleccionar")
    if compact:
        payload["items"] = [
            {field: item.get(field) for field in MESA_INBOX_FIELDS}
            for item in payload.get("items", [])
        ]
        payload["surface"] = "mesa_compact"
    return payload


def _portfolio_item(item_id):
    return next((item for item in _portfolio_inbox().get("items", [])
                 if item.get("id") == str(item_id or "")), None)


def _portfolio_metadata_index():
    return contrato_archivo.portfolio_metadata_index(
        _portfolio_inbox().get("items", []))


def _portfolio_identity_graph():
    return contrato_archivo.portfolio_identity_graph(
        _portfolio_inbox().get("items", []),
        connections=_portfolio_jsonl(PORTFOLIO_CONNECTIONS),
        context_links=_portfolio_context_link_rows())


def _director_capabilities():
    routes = {}
    for task_kind in ("visual", "research", "curation", "review", "judge"):
        routes[task_kind] = providers.route_task(task_kind)
    return {
        "ok": True,
        "schema": "faro-director-capabilities-v1",
        "work_schema": "mak-work-v1",
        "lanes": list(_ledger.LANES) if _ledger is not None else ["obra", "trabajo", "sistema"],
        "decisions": list(_ledger.DECISIONS) if _ledger is not None else [
            "hacer", "revisar", "refutar", "archivar", "descartar"],
        "providers": providers.provider_registry(),
        "routes": routes,
        "policy": {
            "models_write_candidates_only": True,
            "public_promotion_requires_human": True,
            "free_text_is_not_identity": True,
        },
    }


def _director_work(body):
    work = body.get("work") if isinstance(body.get("work"), dict) else body
    if _ledger is None:
        return {"ok": False, "error": "ledger_unavailable"}
    valid, errors = _ledger.validate_work_envelope(work)
    if not valid:
        return {"ok": False, "error": "work_contract_invalid", "errors": errors}
    if not body.get("persist"):
        return {"ok": True, "status": "validated", "work": work,
                "persisted": False}
    row = {
        "id": "work:%s" % work["work_id"], "domain": "mak", "type": "task",
        "claim": "typed work envelope %s" % work["work_id"],
        "evidence": work.get("sources", []), "files": [], "confidence": "medium",
        "action": "review", "decision": "revisar", "purpose": work.get("purpose"),
        "next_action": work.get("next_action"), "owner": work.get("owner", "MAK"),
        "work": work,
    }
    ok, errors, saved = _ledger.append_item(row, path=COMMON_LEDGER,
                                            source="director_work")
    return {"ok": ok, "status": "persisted" if ok else "rejected",
            "errors": errors, "work": saved.get("work") if saved else work}


def _director_decision(body):
    area = str(body.get("area") or "").strip()
    payload = body.get("payload") if isinstance(body.get("payload"), dict) else {}
    record = discernment.decision_record(
        area, payload, work=body.get("work"),
        provider=str(body.get("provider") or "local_deterministic"))
    if not body.get("persist") or _ledger is None:
        return {"ok": True, "record": record, "persisted": False}
    domain = {
        "mak_quality": "mak", "rd_evidence": "rd", "iskvw_curation": "iskvw",
        "portfolio_record": "portfolio", "tool_archaeology": "repo",
        "svg_pipeline": "svg", "adobe_rescue": "adobe",
        "opportunity_radar": "opportunities",
    }.get(area, "mak")
    row = {
        "id": "decision:%s:%s" % (area, time.strftime("%Y%m%d%H%M%S")),
        "domain": domain, "type": "reject" if record["verdict"] == "reject" else "decision",
        "claim": record["reason"], "evidence": record["missing_evidence"], "files": [],
        "confidence": "medium", "action": "reject" if record["verdict"] == "reject" else "review",
        "decision": record["decision"], "reject_reason": record["reason"] if record["verdict"] == "reject" else "",
        "next_action": record["next_action"], "owner": record["owner"],
        "metadata": {"decision_record": record}, "work": record.get("work") or {},
    }
    ok, errors, saved = _ledger.append_item(row, path=COMMON_LEDGER,
                                            source="director_decision")
    return {"ok": ok, "record": record, "persisted": ok,
            "errors": errors, "ledger_id": saved.get("id") if saved else ""}


def _portfolio_triangulation():
    try:
        with open(PORTFOLIO_TRIANGULATION, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {"schema": "mak-triangulation-v1", "status": "unavailable",
                "groups": [], "candidate_count": 0}
    groups = data.get("groups") if isinstance(data, dict) else []
    reviews = _portfolio_jsonl(PORTFOLIO_TRIANGULATION_REVIEW)
    return {"schema": data.get("schema", "mak-triangulation-v1"),
            "status": "candidate_only", "source": data.get("source"),
            "candidate_count": data.get("candidate_count", 0),
            "groups": groups if isinstance(groups, list) else [],
            "rules": data.get("rules", []), "human_resolutions": reviews,
            "human_context": _portfolio_human_context_records(),
            "human_context_links": _portfolio_context_link_rows()}


def _latest_legacy_report_run():
    try:
        names = sorted(name for name in os.listdir(LEGACY_REPORT_RUNS)
                       if name.startswith("faro-report-metadata-"))
    except OSError:
        return ""
    for name in reversed(names):
        path = os.path.join(LEGACY_REPORT_RUNS, name)
        if os.path.isfile(os.path.join(path, "reports.jsonl")):
            return path
    return ""


def _legacy_report_index(limit=100, classification=""):
    run = _latest_legacy_report_run()
    if not run:
        return {"ok": True, "schema": "mak-legacy-report-index-v1",
                "status": "unavailable", "total": 0, "items": [],
                "promotion": "none"}
    summary_path = os.path.join(run, "SUMMARY.json")
    try:
        with open(summary_path, encoding="utf-8") as fh:
            summary = json.load(fh)
    except (OSError, ValueError):
        summary = {}
    rows = _portfolio_jsonl(os.path.join(run, "reports.jsonl"))
    counts = Counter()
    metadata_counts = Counter()
    normalized = []
    for row in rows:
        try:
            family_size = int(row.get("duplicate_family_size") or 0)
        except (TypeError, ValueError):
            family_size = 0
        if row.get("sfera_quarantine") is True:
            current = "quarantine"
            next_action = "revisar en cuarentena; no promover"
        elif family_size <= 1:
            current = "orphan_candidate"
            next_action = "investigar por qué no tiene familia emparejada"
        else:
            current = "paired_family"
            next_action = "revisar la familia como unidad; no confundir sidecars con duplicados"
        counts[current] += 1
        metadata_state = str(row.get("metadata_quality") or "legacy_unknown")
        metadata_counts[metadata_state] += 1
        if classification and current != classification:
            continue
        normalized.append({
            "schema": "mak-work-v1",
            "work_id": str(row.get("work_id") or ""),
            "parent_task": "legacy_report_index",
            "lane": "sistema",
            "purpose": "clasificacion estructural de archivo historico",
            "format": "research_report",
            "created_at": str(row.get("timestamp_from_name") or ""),
            "provider": "deterministic_index",
            "sources": [str(row.get("path") or "")],
            "status": "candidate_only",
            "classification": current,
            "metadata_state": metadata_state,
            "duplicate_status": "not_proven",
            "sfera_quarantine": bool(row.get("sfera_quarantine")),
            "basename": row.get("basename", ""),
            "path": row.get("path", ""),
            "paired_stem": row.get("paired_stem", ""),
            "paired_files": list(row.get("paired_files") or [])[:8],
            "has_markdown": bool(row.get("has_markdown")),
            "has_json": bool(row.get("has_json")),
            "has_concepts": bool(row.get("has_concepts")),
            "evidence": ["path", "filename", "mtime", "pairing"],
            "next_action": next_action,
            "promotion": "none",
        })
    try:
        limit = max(1, min(int(limit), 500))
    except (TypeError, ValueError):
        limit = 100
    external = summary.get("external_review") if isinstance(
        summary.get("external_review"), dict) else {}
    return {
        "ok": True,
        "schema": "mak-legacy-report-index-v1",
        "status": "candidate_only",
        "source_run": os.path.basename(run),
        "source_root": summary.get("root", ""),
        "total": len(rows),
        "returned": min(len(normalized), limit),
        "sampled": len(normalized) > limit,
        "counts": dict(counts),
        "metadata_counts": dict(metadata_counts),
        "rules": [
            "quarantine precedes structural grouping",
            "paired_family is not duplicate proof",
            "legacy_unknown remains until provenance is proven",
            "provider raw output is a hint and never overrides this index",
        ],
        "external_review": {
            "provider": external.get("provider", ""),
            "sample_items": external.get("sample_items", 0),
            "status": external.get("status", "not_applied"),
            "promotion": "none",
        },
        "promotion": "none",
        "items": normalized[:limit],
        "next": "revisar familias y cuarentena por lotes pequeños; no rehacer los 950 informes",
    }


def _legacy_rescue_queue():
    try:
        with open(LEGACY_RESCUE_REVIEW, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {"schema": "mak-rescue-review-v1", "status": "unavailable",
                "items": [], "counts": {"total": 0}}
    items = data.get("items") if isinstance(data, dict) else []
    counts = data.get("counts") if isinstance(data, dict) else {}
    normalized = []
    for item in items if isinstance(items, list) else []:
        item = dict(item)
        item["canonical_decision"] = item.get("decision", "review")
        item["next_action"] = {
            "rescue": "rescatar_con_revision_humana",
            "review": "revisar_manual",
            "retire_without_deleting": "retirar_sin_borrar",
        }.get(item["canonical_decision"], "revisar_manual")
        normalized.append(item)
    return {"schema": data.get("schema", "mak-rescue-review-v1"),
            "status": "candidate_only", "promotion": "none",
            "items": normalized,
            "counts": counts if isinstance(counts, dict) else {"total": 0}}


def _portfolio_triage_record(body):
    group = str(body.get("group_key", "")).strip()[:120]
    if not group:
        return {"ok": False, "error": "grupo_vacio"}
    known = {str(row.get("key", "")) for row in _portfolio_triangulation().get("groups", [])}
    if group not in known:
        return {"ok": False, "error": "grupo_no_encontrado"}
    allowed = ("artist", "event", "venue", "date", "record_kind", "confidence")
    row = {field: str(body.get(field, "")).strip()[:240] for field in allowed}
    row.update({"schema": "mak-triangulation-review-v1", "group_key": group,
                "status": "human_reviewed", "promotion": "none",
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z")})
    os.makedirs(os.path.dirname(PORTFOLIO_TRIANGULATION_REVIEW), exist_ok=True)
    with open(PORTFOLIO_TRIANGULATION_REVIEW, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"ok": True, "resolution": row}


def _portfolio_context_links():
    links = {}
    rows = _portfolio_jsonl(PORTFOLIO_TRIANGULATION_REVIEW)
    for row in rows:
        if not isinstance(row, dict) or row.get("schema") != "mak-triangulation-context-link-v1":
            continue
        source_id = str(row.get("source_id", "")).strip()
        group_key = str(row.get("group_key", "")).strip()
        if source_id and group_key and group_key not in links.setdefault(source_id, []):
            links[source_id].append(group_key)
    return links


def _portfolio_context_link_rows():
    links = []
    rows = _portfolio_jsonl(PORTFOLIO_TRIANGULATION_REVIEW)
    for row in rows:
        if isinstance(row, dict) and row.get("schema") == "mak-triangulation-context-link-v1":
            links.append(row)
    return links


def _portfolio_context_link(body):
    source_id = str(body.get("source_id", "")).strip()[:240]
    group = str(body.get("group_key", "")).strip()[:120]
    if not source_id:
        return {"ok": False, "error": "contexto_vacio"}
    if not group:
        return {"ok": False, "error": "grupo_vacio"}
    known = {str(row.get("key", "")) for row in
             _portfolio_triangulation().get("groups", [])}
    if group not in known:
        return {"ok": False, "error": "grupo_no_encontrado"}
    context = next((row for row in _portfolio_human_context_records()
                    if row.get("source_id") == source_id), None)
    if not context:
        return {"ok": False, "error": "contexto_humano_no_encontrado"}
    for row in _portfolio_context_link_rows():
        if row.get("source_id") == source_id and row.get("group_key") == group:
            return {"ok": True, "resolution": row, "already_linked": True}
    row = {
        "schema": "mak-triangulation-context-link-v1",
        "record_kind": "context_to_group",
        "source_id": source_id,
        "group_key": group,
        "status": "human_reviewed",
        "origin": "human_context",
        "context_fields": context.get("context_fields", {}),
        "human_note": context.get("human_note", ""),
        "confidence": "human_confirmed",
        "promotion": "none",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    os.makedirs(os.path.dirname(PORTFOLIO_TRIANGULATION_REVIEW), exist_ok=True)
    with open(PORTFOLIO_TRIANGULATION_REVIEW, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"ok": True, "resolution": row, "already_linked": False}


def _portfolio_item_context(item_id):
    external = _portfolio_external_candidates(item_id)
    accepted = [
        {
            "source_id": row.get("source_id", ""),
            "provider": row.get("provider", "unknown"),
            "candidate_relations": row.get("candidate_relations", {}),
            "context_fields": row.get("context_fields", {}),
            "context_state": row.get("context_state", "note_only"),
            "evidence_basis": row.get("evidence_basis", []),
            "human_note": row.get("human_note", ""),
            "reviewed_at": row.get("reviewed_at", ""),
            "status": "human_accepted_candidate",
            "public_promotion": False,
        }
        for row in external.get("items", [])
        if row.get("human_decision") == "accept"
    ]
    context = {"human_evidence": {
        "schema": "faro-portfolio-human-context-v1",
        "accepted": accepted,
        "count": len(accepted),
        "promotion": "none",
    }}
    data = _portfolio_triangulation()
    for group in data.get("groups", []):
        if str(item_id) not in {str(value) for value in group.get("items", [])}:
            continue
        reviews = [row for row in data.get("human_resolutions", [])
                   if row.get("group_key") == group.get("key")]
        context.update({"triangulation_group": group,
                        "human_resolution": reviews[-1] if reviews else {}})
        break
    return context


def _portfolio_select(item_id, decision, board_id="", session_id="", pass_size=0,
                      decision_scope="selection", reason_code="", target_id="",
                      note=""):
    if decision not in ("seleccionar", "deseleccionar", "descartar"):
        return {"ok": False, "error": "decision_invalida"}
    item = _portfolio_item(item_id)
    if not item:
        return {"ok": False, "error": "item_no_encontrado"}
    os.makedirs(os.path.dirname(PORTFOLIO_SELECTIONS), exist_ok=True)
    try:
        pass_size = int(pass_size)
    except (TypeError, ValueError):
        pass_size = 0
    pass_size = pass_size if pass_size in (10, 20) else 0
    session_id = str(session_id or "").strip()[:120]
    decision_scope = str(decision_scope or "selection").strip()[:60]
    reason_code = str(reason_code or "").strip()[:120]
    target_id = str(target_id or "").strip()[:160]
    note = str(note or "").strip()[:1000]
    previous = _portfolio_selections().get(item["id"])
    if (previous
            and previous.get("decision") == decision
            and previous.get("decision_scope", "selection") == decision_scope
            and previous.get("reason_code", "") == reason_code
            and previous.get("target_id", "") == target_id
            and previous.get("note", "") == note):
        result = {"ok": True, "row": previous, "duplicate": True}
        if (decision == "descartar" and decision_scope == "record"
                and reason_code == "no_es_obra"):
            triage = _portfolio_classify({
                "item_id": item["id"],
                "fields": {"triage": "discard"},
                "source": {"kind": "human_selection",
                           "decision": decision,
                           "reason_code": reason_code},
            })
            result["triage"] = triage
            result["triage_saved"] = bool(triage.get("ok"))
            if not triage.get("ok"):
                return {"ok": False, "error": "triage_rechazo",
                        "selection": previous, "selection_saved": True,
                        "triage_saved": False, "details": triage}
        return result
    row = {"item_id": item["id"], "decision": decision,
           "board_id": str(board_id or "")[:100],
           "session_id": session_id, "pass_size": pass_size,
           "decision_scope": decision_scope, "reason_code": reason_code,
           "target_id": target_id, "note": note,
           "work": {"schema": "mak-work-v1",
                     "work_id": "portfolio:%s" % item["id"],
                     "parent_task": "portfolio-curation",
                     "lane": "obra", "purpose": "human portfolio selection",
                     "format": item.get("tipo_contenido", "media"),
                     "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                     "provider": "human", "sources": [item["id"]],
                     "status": "human_decision", "session_id": session_id,
                     "pass_size": pass_size, "decision_scope": decision_scope,
                     "reason_code": reason_code, "target_id": target_id},
           "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    if _ledger is not None:
        action = "curate" if decision == "seleccionar" else (
            "reject" if decision == "descartar" else "archive")
        ledger_ok, ledger_errors, _ledger_row = _ledger.append_unique({
            "id": "portfolio-selection:%s:%s:%s" % (
                item["id"], decision, row["ts"]),
            "domain": "iskvw", "type": "decision", "claim":
                "%s portfolio item %s" % (decision, item["id"]),
            "evidence": [item.get("asset_path", ""),
                         item.get("publicacion_id", "")],
            "confidence": "high", "action": action,
            "decision": ("hacer" if decision == "seleccionar" else
                          "descartar" if decision == "descartar" else "archivar"),
            "purpose": ("record the artist selection without public promotion"
                        if decision != "descartar" else
                        "record that this portfolio candidate is not an artwork"),
            "next_action": ("curate selected item" if decision == "seleccionar"
                            else "keep excluded item out of public curation"),
            "metadata": {"decision_scope": decision_scope,
                         "reason_code": reason_code, "target_id": target_id,
                         "note": note},
            "owner": "human", "work": row["work"]},
            path=COMMON_LEDGER, source="portfolio_editor")
        if not ledger_ok:
            return {"ok": False, "error": "ledger_rechazo", "details": ledger_errors}
    with open(PORTFOLIO_SELECTIONS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    result = {"ok": True, "row": row}
    if (decision == "descartar" and decision_scope == "record"
            and reason_code == "no_es_obra"):
        triage = _portfolio_classify({
            "item_id": item["id"],
            "fields": {"triage": "discard"},
            "source": {"kind": "human_selection",
                       "decision": decision,
                       "reason_code": reason_code},
        })
        result["triage"] = triage
        result["selection_saved"] = True
        result["triage_saved"] = bool(triage.get("ok"))
        if not triage.get("ok"):
            return {"ok": False, "error": "triage_rechazo",
                    "selection": row, "selection_saved": True,
                    "triage_saved": False, "details": triage}
    return result


def _portfolio_classify(body):
    item_id = str(body.get("item_id", "")).strip()
    item = _portfolio_item(item_id)
    if not item:
        return {"ok": False, "error": "item_no_encontrado"}
    allowed = PORTFOLIO_CLASSIFICATION_ALLOWED
    fields = body.get("fields") if isinstance(body.get("fields"), dict) else {}
    previous = (_portfolio_classifications().get(item["id"]) or {}).get("fields", {})
    normalized = dict(previous) if isinstance(previous, dict) else {}
    clear_fields = body.get("clear_fields")
    clear_fields = clear_fields if isinstance(clear_fields, list) else []
    for key in clear_fields:
        if str(key) in allowed or str(key) == "context_value":
            normalized.pop(str(key), None)
    for key, values in allowed.items():
        value = str(fields.get(key, "")).strip().lower()
        if not value:
            continue
        if value not in values:
            return {"ok": False, "error": "valor_de_clasificacion_invalido",
                    "field": key}
        normalized[key] = value
    if ("context_kind" in fields
            and str(fields.get("context_kind") or "").strip().lower()
            != str(previous.get("context_kind") or "").strip().lower()
            and not str(fields.get("context_value") or "").strip()):
        normalized.pop("context_value", None)
    if "context_kind" in clear_fields:
        normalized.pop("context_value", None)
    context_value = str(fields.get("context_value", "")).strip()[:120]
    if context_value:
        normalized["context_value"] = context_value
    if not normalized:
        return {"ok": False, "error": "clasificacion_vacia"}
    previous_row = _portfolio_classifications().get(item["id"])
    previous_fields = (previous_row or {}).get("fields", {})
    if previous_fields == normalized:
        return {"ok": True, "classification": normalized,
                "row": previous_row, "duplicate": True}
    row = {
        "schema": "faro-portfolio-classification-v1",
        "item_id": item["id"], "fields": normalized,
        "status": "human_draft", "promotion": "none", "owner": "human",
        "source": {"publicacion_id": item.get("publicacion_id", ""),
                   "fecha": item.get("fecha", ""),
                   "asset_path": item.get("asset_path", "")},
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    if isinstance(body.get("source"), dict):
        row["evidence"] = dict(body["source"])
    os.makedirs(os.path.dirname(PORTFOLIO_CLASSIFICATIONS), exist_ok=True)
    with open(PORTFOLIO_CLASSIFICATIONS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"ok": True, "classification": normalized, "row": row}


def _portfolio_classify_batch(body):
    """Persist one ordering signal for a bounded group of records."""
    item_ids = body.get("item_ids") if isinstance(body.get("item_ids"), list) else []
    item_ids = [str(item_id).strip()[:160] for item_id in item_ids]
    item_ids = list(dict.fromkeys(item_id for item_id in item_ids if item_id))[:40]
    fields = body.get("fields") if isinstance(body.get("fields"), dict) else {}
    if not item_ids or not fields:
        return {"ok": False, "error": "grupo_o_clasificacion_vacios"}
    missing = [item_id for item_id in item_ids if not _portfolio_item(item_id)]
    if missing:
        return {"ok": False, "error": "items_no_encontrados", "item_ids": missing}
    for key, values in PORTFOLIO_CLASSIFICATION_ALLOWED.items():
        value = str(fields.get(key, "")).strip().lower()
        if value and value not in values:
            return {"ok": False, "error": "valor_de_clasificacion_invalido",
                    "field": key}
    results = []
    for item_id in item_ids:
        results.append(_portfolio_classify({"item_id": item_id, "fields": fields}))
    saved = sum(1 for row in results if row.get("ok"))
    return {
        "ok": saved == len(results),
        "schema": "faro-portfolio-batch-classification-v1",
        "count": len(results),
        "saved": saved,
        "partial": 0 < saved < len(results),
        "results": results,
    }


def _portfolio_boards():
    try:
        with open(PORTFOLIO_BOARDS, encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict) and isinstance(data.get("boards"), list):
            return data
    except (OSError, ValueError):
        pass
    return {"schema": "faro-portfolio-boards-v1", "boards": []}


def _portfolio_save_boards(data):
    os.makedirs(os.path.dirname(PORTFOLIO_BOARDS), exist_ok=True)
    tmp = PORTFOLIO_BOARDS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, PORTFOLIO_BOARDS)


def _portfolio_board_action(body):
    action = str(body.get("action", ""))
    data = _portfolio_boards()
    boards = data["boards"]
    board_id = str(body.get("board_id", ""))[:100]
    board = next((b for b in boards if b.get("id") == board_id), None)
    if action == "create":
        name = str(body.get("name", "")).strip()[:120]
        if not name:
            return {"ok": False, "error": "nombre_vacio"}
        board = {"id": "tablero-" + uuid.uuid4().hex[:12],
                 "name": name, "item_ids": [],
                 "facet": str(body.get("facet", "general"))[:40],
                 "value": str(body.get("value", ""))[:120],
                 "created": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
        boards.append(board)
    elif not board:
        return {"ok": False, "error": "tablero_no_encontrado"}
    elif action in ("add", "remove"):
        raw_ids = list(dict.fromkeys(str(item_id).strip() for item_id in
                                     (body.get("item_ids") or []) if str(item_id).strip()))
        missing = [item_id for item_id in raw_ids if not _portfolio_item(item_id)]
        if missing:
            return {"ok": False, "error": "items_invalidos", "item_ids": missing}
        ids = raw_ids
        current = list(dict.fromkeys(str(item_id) for item_id in
                                     (board.get("item_ids") or [])
                                     if _portfolio_item(item_id)))
        if action == "add":
            additions = [item_id for item_id in ids if item_id not in current]
            board["item_ids"] = current + additions
            # Board composition is a real human signal. Record only new
            # pairings, scoped to this board; it never publishes anything.
            facet = str(board.get("facet") or "board").lower()
            feedback_results = []
            for existing in current:
                for added in additions:
                    feedback = _portfolio_feedback_record({
                        "source_id": existing, "target_id": added,
                        "action": "accept", "facet": facet,
                        "relation": "same_board:%s" % board["id"],
                        "board_id": board["id"]})
                    feedback_results.append(feedback)
                    if not feedback.get("ok"):
                        return {"ok": False, "error": "feedback_tablero_rechazado",
                                "board": board, "board_saved": False,
                                "feedback_results": feedback_results,
                                "partial": any(row.get("ok") for row in feedback_results)}
        else:
            board["item_ids"] = [item_id for item_id in current if item_id not in ids]
    else:
        return {"ok": False, "error": "accion_invalida"}
    _portfolio_save_boards(data)
    return {"ok": True, "board": board, "boards": boards}


def _portfolio_connect(body):
    source = str(body.get("source_id", ""))
    target = str(body.get("target_id", ""))
    relation = str(body.get("relation", "relacionada")).strip()[:80]
    if source == target or not _portfolio_item(source) or not _portfolio_item(target):
        return {"ok": False, "error": "items_invalidos"}
    existing = next((row for row in _portfolio_jsonl(PORTFOLIO_CONNECTIONS)
                     if str(row.get("source_id")) == source
                     and str(row.get("target_id")) == target
                     and str(row.get("relation")) == relation), None)
    if existing:
        return {"ok": True, "connection": existing, "duplicate": True}
    os.makedirs(os.path.dirname(PORTFOLIO_CONNECTIONS), exist_ok=True)
    row = {"source_id": source, "target_id": target, "relation": relation,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    with open(PORTFOLIO_CONNECTIONS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"ok": True, "connection": row}


def _portfolio_feedback():
    rows = []
    try:
        with open(PORTFOLIO_FEEDBACK, encoding="utf-8") as fh:
            for line in fh:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if row.get("source_id") and row.get("target_id"):
                    rows.append(row)
    except OSError:
        pass
    return rows


def _portfolio_jsonl(path):
    rows = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict):
                    rows.append(row)
    except OSError:
        pass
    return rows


def _portfolio_organism_projection():
    """Project existing portfolio data as blocks, channels and connections.

    This is an Are.na-like view, not a second store. The inbox remains the
    source for blocks, boards become channels, and the existing connection
    log becomes connections. Human feedback annotates those links without
    turning a candidate relation into a fact.
    """
    inbox_items = _portfolio_inbox().get("items", [])
    valid_items = {
        str(item.get("id")): item for item in inbox_items
        if item.get("id")
    }
    blocks = []
    for item_id, item in valid_items.items():
        content_type = str(item.get("tipo_contenido") or "media")
        contract = contrato_archivo.desde_portfolio_item(item)
        blocks.append({
            "id": item_id,
            "kind": "block",
            "record_kind": contract["record_kind"],
            "content_type": content_type,
            "date": item.get("fecha"),
            "publication_id": item.get("publicacion_id"),
            "description_original": item.get("descripcion_original", ""),
            "asset_path": item.get("asset_path"),
            "asset_available": bool(item.get("asset_available")),
            "selection": item.get("selection", "pendiente"),
            "contract": contract,
        })

    channels = []
    for board in _portfolio_boards().get("boards", []):
        board_id = str(board.get("id") or "")
        if not board_id:
            continue
        block_ids = [str(item_id) for item_id in board.get("item_ids", [])
                     if str(item_id) in valid_items]
        channels.append({
            "id": board_id,
            "kind": "channel",
            "name": board.get("name", ""),
            "facet": board.get("facet", "general"),
            "value": board.get("value", ""),
            "block_ids": block_ids,
        })

    feedback_by_pair = {}
    feedback_by_relation = {}
    for row in _portfolio_feedback():
        key = (str(row.get("source_id")), str(row.get("target_id")))
        if key[0] in valid_items and key[1] in valid_items and key[0] != key[1]:
            feedback_by_pair[key] = row
            relation = str(row.get("relation") or "relacionada")
            feedback_by_relation[(*key, relation)] = row

    connections = []
    for row in _portfolio_jsonl(PORTFOLIO_CONNECTIONS):
        source_id = str(row.get("source_id") or "")
        target_id = str(row.get("target_id") or "")
        if (source_id not in valid_items or target_id not in valid_items
                or source_id == target_id):
            continue
        relation = str(row.get("relation") or "relacionada")
        feedback = (feedback_by_relation.get((source_id, target_id, relation))
                    or feedback_by_relation.get((target_id, source_id, relation)))
        if not feedback and relation in {"relacionada", "related"}:
            feedback = (feedback_by_pair.get((source_id, target_id), {})
                        or feedback_by_pair.get((target_id, source_id), {}))
        feedback = feedback or {}
        action = str(feedback.get("action") or "")
        if action == "reject":
            continue
        connections.append({
            "id": "connection:%s:%s:%s" % (
                source_id, target_id, str(row.get("relation") or "related")),
            "kind": "connection",
            "source_id": source_id,
            "target_id": target_id,
            "relation": relation,
            "origin": "human" if action in ("accept", "correct")
            else "connection_log",
            "decision": action or "candidate",
            "confidence": "high" if action in ("accept", "correct") else "unknown",
            "evidence": (["human_feedback:%s" % action] if action else []),
            "board_id": feedback.get("board_id", ""),
        })

    decisions = []
    for row in feedback_by_pair.values():
        decisions.append({
            "source_id": str(row.get("source_id")),
            "target_id": str(row.get("target_id")),
            "action": row.get("action", "ignore"),
            "facet": row.get("facet", "unknown"),
            "relation": row.get("relation", "relacionada"),
            "board_id": row.get("board_id", ""),
        })
    return {
        "ok": True,
        "schema": "faro-portfolio-organism-v1",
        "mode": "projection_only",
        "source_of_truth": ["portfolio_inbox", "classifications", "vision_features",
                             "boards", "connections", "copilot_feedback"],
        **_portfolio_contract_surface(),
        "blocks": blocks,
        "channels": channels,
        "connections": connections,
        "decisions": decisions,
        "counts": {
            "blocks": len(blocks), "channels": len(channels),
            "connections": len(connections), "decisions": len(decisions),
        },
    }


def _portfolio_contract_surface():
    """Return only the small contract envelope used by lightweight clients."""
    return {
        "projection_contract": {
            "schema": contrato_archivo.PORTFOLIO_ENTITY_SCHEMA,
            "required": ["entity_id", "source_id", "lane", "purpose", "format",
                          "evidence_kind", "status", "next_action", "owner",
                          "consent", "publication"],
            "layers": {"archive": "source_of_truth", "organism": "projection_only"},
        },
        "publication_policy": {
            "default_status": "private_candidate",
            "requires_recorded_consent": True,
            "requires_human_gate": True,
        },
    }


def _portfolio_suggestions(item_id, board_id="", include_map=False,
                           focus_facet="", shuffle=False, shuffle_seed=""):
    source = _portfolio_item(item_id)
    if not source:
        return {"ok": False, "error": "item_no_encontrado", "suggestions": []}
    board = next((b for b in _portfolio_boards().get("boards", [])
                  if b.get("id") == str(board_id)), {})
    context = dict(board)
    context.update(_portfolio_item_context(item_id))
    inbox_items = _portfolio_apply_human_context(
        _portfolio_inbox().get("items", []))
    source = next((item for item in inbox_items
                   if item.get("id") == str(item_id)), source)
    feedback = _portfolio_feedback()
    visual_surface = _portfolio_visual_surface(item_id)
    result, suppressed = copilot.build_suggestions(
        source, inbox_items, selections=_portfolio_selections(),
        feedback=feedback, context=context, limit=24,
        focus_facet=focus_facet, shuffle=shuffle, shuffle_seed=shuffle_seed,
        visual_relations=visual_surface.get("relations", []))
    map_surface = {"schema": copilot.GTM_SCHEMA,
                   "engine": "not_requested", "fit": {},
                   "source_position": None}
    map_by_id = {}
    source_position = None
    if include_map:
        map_surface = copilot.build_gtm_map(
            inbox_items, feedback=feedback, stable_topology=True)
        map_by_id = {row["item_id"]: row for row in map_surface.get("items", [])}
        source_position = map_by_id.get(str(item_id))
        for row in result:
            target_position = map_by_id.get(str(row.get("item_id")))
            if not source_position or not target_position:
                continue
            distance = math.sqrt(
                (source_position["x"] - target_position["x"]) ** 2
                + (source_position["y"] - target_position["y"]) ** 2)
            row["map_distance"] = round(distance, 6)
            row["map_position"] = {
                "x": target_position["x"], "y": target_position["y"]}
            row["reasons"].append("vecindad GTM: %.3f" % distance)
            row["score"] += max(0.0, 3.0 - (distance * 6.0))
    result.sort(key=lambda row: (-row["score"], row["item_id"], row["relation_type"]))
    map_item_ids = [str(item_id)] + [str(row.get("item_id")) for row in result]
    map_items = []
    seen_map_items = set()
    for map_item_id in map_item_ids:
        if map_item_id in seen_map_items:
            continue
        map_row = map_by_id.get(map_item_id)
        if map_row:
            map_items.append(map_row)
            seen_map_items.add(map_item_id)
    return {"ok": True, "schema": "faro-portfolio-copilot-v4", "source_id": source.get("id"),
            "provider": "local_hypothesis_engine", "context": context,
            "map": {"schema": map_surface["schema"], "engine": map_surface["engine"],
                    "fit": map_surface.get("fit", {}),
                    "ordering": map_surface.get("ordering", {}),
                    "source_position": source_position, "items": map_items},
            "relation_policy": {
                "declared": "metadata exacta; pesa mas y muestra evidencia estructurada",
                "exploratory": "concepto compartido; solo pista, nunca identidad",
                "spaces": {
                    "evidence": "relacion factual respaldada; candidata a verificacion",
                    "resonance": "lectura poetica o conceptual; nunca modifica identidad",
                },
                "promotion": "none",
            },
            "suggestion_groups": copilot.group_suggestions(result),
            "learning": copilot.learning_profile(_portfolio_feedback()),
            "candidate_learning": copilot.review_profile(
                _portfolio_external_review_rows()),
            "visual_similarity": visual_surface,
            "xio_evidence": _portfolio_xio_evidence(),
            "suggestion_mode": "shuffle" if shuffle else focus_facet or "copilot",
            "suppressed_redundant": suppressed, "suggestions": result}


def _portfolio_order_groups(source, inbox_items, map_surface, limit=10):
    positions = {
        str(row.get("item_id")): row for row in map_surface.get("items", [])
        if isinstance(row, dict) and row.get("item_id")
    }
    source_id = str(source.get("id") or "")
    source_position = positions.get(source_id)
    if not source_position:
        return []
    by_id = {str(item.get("id")): item for item in inbox_items
             if isinstance(item, dict) and item.get("id")}
    source_publication = str(source.get("publicacion_id") or "")
    ranked = []
    for item_id, item in by_id.items():
        if item_id == source_id or str(item.get("selection") or "") == "descartar":
            continue
        if not item.get("asset_available"):
            continue
        position = positions.get(item_id)
        if not position:
            continue
        publication_id = str(item.get("publicacion_id") or "")
        if source_publication and publication_id == source_publication:
            continue
        distance = math.sqrt(
            (source_position["x"] - position["x"]) ** 2
            + (source_position["y"] - position["y"]) ** 2)
        ranked.append((distance, publication_id or item_id, item_id))
    selected = []
    seen_units = set()
    for distance, unit_id, item_id in sorted(ranked):
        if unit_id in seen_units:
            continue
        seen_units.add(unit_id)
        selected.append({
            "item_id": item_id,
            "selection": by_id[item_id].get("selection", "pendiente"),
            "source_role": "active",
            "candidate_role": "map_neighbor",
            "score": max(0.0, 1.0 - distance),
            "confidence": "baja",
            "scope": "exploratory",
            "space": "topology",
            "spaces": ["topology"],
            "facets": [],
            "relations": [],
            "evidence": [],
            "reasons": ["vecindad GTM: %.3f" % distance],
            "relation_type": "map_neighbor",
        })
        if len(selected) >= max(1, int(limit) - 1):
            break
    return selected


def _portfolio_scene(item_id, limit=10, focus_facet="", shuffle=False,
                     shuffle_seed="", surface=""):
    """Return one deduplicated scene for the active portfolio record."""
    inbox_items = _portfolio_apply_human_context(
        _portfolio_inbox().get("items", []))
    source = next((item for item in inbox_items
                   if str(item.get("id")) == str(item_id)), None)
    if not source:
        return {"ok": False, "error": "item_no_encontrado", "records": [],
                "relations": []}
    if str(source.get("selection") or "") == "descartar":
        return {"ok": False, "error": "item_descartado", "records": [],
                "relations": []}
    feedback_rows = _portfolio_feedback()
    source = next((item for item in inbox_items
                   if str(item.get("id")) == str(item_id)), source)
    if str(source.get("selection") or "") == "descartar":
        return {"ok": False, "error": "item_descartado", "records": [],
                "relations": []}
    if surface == "order":
        map_surface = copilot.build_gtm_map(
            inbox_items, feedback=feedback_rows, stable_topology=True)
        visual_surface = _portfolio_visual_surface(item_id)
        suggestion_surface = {
            "provider": "gtm_order_projection",
            "learning": {"ordering": map_surface.get("ordering", {})},
            "map": map_surface,
            # The order surface is the active editor surface; keep the
            # derived visual channel visible there without loading the model.
            "visual_similarity": visual_surface,
            "suggestion_groups": _portfolio_order_groups(
                source, inbox_items, map_surface, limit=limit),
        }
    elif focus_facet or shuffle or shuffle_seed:
        suggestion_surface = _portfolio_suggestions(
            item_id, include_map=True, focus_facet=focus_facet,
            shuffle=shuffle, shuffle_seed=shuffle_seed)
    else:
        suggestion_surface = _portfolio_suggestions(item_id, include_map=True)
    groups = [dict(group) for group in suggestion_surface.get(
        "suggestion_groups", [])]
    for group in groups:
        target_id = str(group.get("item_id") or "")
        group_facets = {str(facet).lower() for facet in group.get("facets", [])}
        relation_type = str(group.get("relation_type") or "related")
        matching = [row for row in feedback_rows
                    if str(row.get("source_id")) == str(item_id)
                    and str(row.get("target_id")) == target_id
                    and (str(row.get("facet") or "unknown").lower() in group_facets
                         or str(row.get("relation") or "related") == relation_type
                         or str(row.get("facet") or "unknown").lower() == "unknown")]
        if matching:
            matching.sort(key=lambda row: str(row.get("ts") or ""))
            group["feedback_channels"] = [dict(row) for row in matching]
            latest = matching[-1]
            group["note"] = str(latest.get("note") or group.get("note") or "")
            group["feedback_facet"] = str(
                latest.get("facet") or group.get("feedback_facet") or "").strip()
            group["feedback"] = latest.get("action", "")
    scene = contrato_archivo.mesa_scene(source, inbox_items, groups, limit=limit)
    scene["ok"] = True
    scene["provider"] = suggestion_surface.get("provider", "local_hypothesis_engine")
    map_surface = suggestion_surface.get("map") or {}
    scene["learning"] = dict(suggestion_surface.get("learning", {}))
    scene["learning"]["ordering"] = map_surface.get("ordering", {})
    scene["visual_similarity"] = suggestion_surface.get(
        "visual_similarity", {"available": False, "relations": []})
    scene["xio_evidence"] = suggestion_surface.get(
        "xio_evidence", _portfolio_xio_evidence())
    map_by_id = {
        str(row.get("item_id")): row
        for row in map_surface.get("items", [])
        if isinstance(row, dict) and row.get("item_id")
    }
    scene["map"] = {
        "schema": map_surface.get("schema", copilot.GTM_SCHEMA),
        "engine": map_surface.get("engine", "not_requested"),
        "grid": map_surface.get("grid", {}),
        "fit": map_surface.get("fit", {}),
        "items": [map_by_id[row["source_id"]]
                  for row in scene.get("records", [])
                  if row.get("source_id") in map_by_id],
    }
    return scene


def _portfolio_external_review_rows():
    if _ledger is None:
        return []
    latest = {}
    for row in _ledger.read_items(COMMON_LEDGER, limit=10000):
        review = (row.get("metadata") or {}).get("external_candidate_review")
        if not isinstance(review, dict):
            continue
        candidate_id = str(review.get("candidate_id") or "").strip()
        source_id = str(review.get("source_id") or "").strip()
        if not candidate_id or not source_id:
            continue
        key = (candidate_id, source_id)
        review = dict(review)
        if not review.get("work_id"):
            review["work_id"] = "legacy-portfolio-review:%s:%s" % (
                candidate_id, source_id)
            review["traceability"] = "derived_from_legacy_review"
        else:
            review["traceability"] = "human_review_work"
        prior = latest.get(key)
        if prior is None or str(review.get("ts") or "") >= str(
                prior.get("ts") or ""):
            latest[key] = review
    return list(latest.values())


def _portfolio_external_review_history(source_id=""):
    """Return append-only external review evidence with its ledger identity."""
    requested = str(source_id or "").strip()
    if _ledger is None:
        return []
    history = []
    for ledger_row in _ledger.read_items(COMMON_LEDGER, limit=10000):
        review = (ledger_row.get("metadata") or {}).get(
            "external_candidate_review")
        if not isinstance(review, dict):
            continue
        review_source = str(review.get("source_id") or "").strip()
        candidate_id = str(review.get("candidate_id") or "").strip()
        if not review_source or not candidate_id:
            continue
        if requested and review_source != requested:
            continue
        entry = dict(review)
        entry["ledger_id"] = str(ledger_row.get("id") or "")
        if not entry.get("ts"):
            entry["ts"] = ledger_row.get("ts", "")
        history.append(entry)
    return history


def _portfolio_value_counts(rows, key, default="unknown"):
    counts = Counter()
    for row in rows or []:
        value = str(row.get(key) or default).strip().lower() or default
        counts[value] += 1
    return dict(sorted(counts.items()))


def _portfolio_feedback_counts(rows):
    return {
        "by_action": _portfolio_value_counts(rows, "action"),
        "by_facet": _portfolio_value_counts(rows, "facet"),
        "by_relation": _portfolio_value_counts(rows, "relation"),
    }


def _portfolio_ordering_audit(items):
    """Build only the ordering evidence needed by the read-only audit.

    The full GTM map is intentionally not part of the audit response. Calling
    build_gtm_map here made the first audit request pay the complete cold map
    fit even though the UI only needs counts and the leave-one-out metrics.
    Stable vectors preserve the same geometry-independent baseline used by the
    GTM stable surface without warming or rebuilding that surface.
    """
    original_items = [item for item in items or [] if item.get("id")]
    stable_items = copilot._stable_topology_items(original_items)
    vectors = {
        str(item.get("id")): copilot.portfolio_vector(item)
        for item in stable_items if item.get("id")
    }
    ordering = copilot.ordering_profile(original_items)
    ordering["evaluation"] = copilot._ordering_evaluation(
        original_items, vectors)
    ordering["promotion"] = "none"
    return ordering


def _portfolio_audit(source_id=""):
    """Expose one auditable view without conflating current state and history."""
    requested = str(source_id or "").strip()
    inbox = _portfolio_inbox()
    items = inbox.get("items", [])
    item_by_id = {str(item.get("id")): item for item in items if item.get("id")}
    requested_item = item_by_id.get(requested)
    if requested and not requested_item:
        return {"ok": False, "error": "item_no_encontrado", "source_id": requested}
    selections = _portfolio_selections()
    classifications = _portfolio_classifications()
    selection_history = _portfolio_selection_history()
    classification_history = _portfolio_classification_history()
    feedback_history = _portfolio_feedback()
    feedback_learning = copilot.dedupe_feedback(feedback_history)
    current_reviews = _portfolio_external_review_rows()
    review_history = _portfolio_external_review_history()
    visual_history = [row for row in feedback_history
                      if str(row.get("facet") or "").lower() == "visual_similarity"
                      or str(row.get("relation") or "") == "visual_similarity"]
    visual_learning = [row for row in feedback_learning
                       if str(row.get("facet") or "").lower() == "visual_similarity"
                       or str(row.get("relation") or "") == "visual_similarity"]
    valid_item_ids = set(item_by_id)
    current_selection_rows = [row for item_id, row in selections.items()
                              if item_id in valid_item_ids]
    current_selection_counts = _portfolio_value_counts(
        current_selection_rows, "decision", default="unknown")
    current_classification_rows = [row for item_id, row in classifications.items()
                                   if item_id in valid_item_ids]
    if requested:
        ordering = copilot.ordering_profile(items)
    else:
        ordering = _portfolio_ordering_audit(items)
    source_counts = Counter()
    for item in items:
        label, source = copilot._triage_label_source(item)
        if label:
            source_counts[source] += 1
    current_selected = current_selection_counts.get("seleccionar", 0)
    current_deselected = current_selection_counts.get("deseleccionar", 0)
    current_discarded = current_selection_counts.get("descartar", 0)
    current_labeled = len(current_selection_rows)
    audit = {
        "ok": True,
        "schema": "faro-portfolio-audit-v1",
        "read_only": True,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "contract": {
            "current_selection": "ultima decision de seleccion por pieza dentro del inbox",
            "triage_labels": "ultima clasificacion.triage; si falta, deriva seleccionar o descartar",
            "selection_history": "historial append-only; no se borra al deseleccionar",
            "relation_feedback": "historial append-only; learning deduplica por par, accion, faceta y relacion",
            "candidate_reviews": "historial de ledger; current es la ultima revision por candidato y source_id",
            "visual_feedback": "feedback de relaciones filtrado por facet o relation visual_similarity",
            "promotion": "ninguna capa de auditoria publica automaticamente",
        },
        "sources": [
            "portfolio_inbox",
            "portfolio_selections",
            "portfolio_classifications",
            "copilot_feedback",
            "common_ledger.external_candidate_review",
        ],
        "counts": {
            "inbox": {
                "total": len(items),
                "available_assets": sum(1 for item in items
                                         if item.get("asset_available")),
            },
            "current_selection": {
                "selected": current_selected,
                "deselected": current_deselected,
                "discarded": current_discarded,
                "pending": max(0, len(items) - current_labeled),
                "labeled": current_labeled,
                "unmatched_history_rows": max(0, len(selections) - current_labeled),
                "by_decision": current_selection_counts,
            },
            "selection_history": {
                "total": len(selection_history),
                "by_decision": _portfolio_value_counts(selection_history, "decision"),
            },
            "classification_history": {
                "total": len(classification_history),
                "current": len(current_classification_rows),
                "by_triage": _portfolio_value_counts(
                    [row.get("fields", {}) for row in classification_history
                     if isinstance(row.get("fields"), dict)], "triage"),
            },
            "triage_labels": {
                "total": ordering.get("labeled", 0),
                "by_label": dict(ordering.get("counts") or {}),
                "by_source": dict(sorted(source_counts.items())),
                "unlabeled": ordering.get("unlabeled", len(items)),
            },
            "relation_feedback": {
                "history_total": len(feedback_history),
                "learning_total": len(feedback_learning),
                "history": _portfolio_feedback_counts(feedback_history),
                "learning": _portfolio_feedback_counts(feedback_learning),
            },
            "candidate_reviews": {
                "history_total": len(review_history),
                "current_total": len(current_reviews),
                "history_by_decision": _portfolio_value_counts(review_history, "decision"),
                "current_by_decision": _portfolio_value_counts(current_reviews, "decision"),
            },
            "visual_feedback": {
                "history_total": len(visual_history),
                "learning_total": len(visual_learning),
                "history_by_action": _portfolio_value_counts(visual_history, "action"),
                "learning_by_action": _portfolio_value_counts(visual_learning, "action"),
            },
            "ordering_model": {
                "automation_ready": bool(
                    (ordering.get("evaluation") or {}).get(
                        "automation_ready", ordering.get("automation_ready", False))),
                "evaluation": ordering.get("evaluation", {}),
                "promotion": ordering.get("promotion", "none"),
            },
        },
        "next": "usar esta auditoria para distinguir estado actual, historial y aprendizaje antes de pedir otra decision",
    }
    if not requested:
        return audit
    item = requested_item
    current_selection = selections.get(requested) or {}
    current_classification = classifications.get(requested) or {}
    timeline = []
    for row in _portfolio_selection_history(requested):
        timeline.append({
            "kind": "selection", "ts": row.get("ts", ""),
            "decision": row.get("decision", ""),
            "board_id": row.get("board_id", ""),
            "work_id": (row.get("work") or {}).get("work_id", ""),
        })
    for row in _portfolio_classification_history(requested):
        timeline.append({
            "kind": "classification", "ts": row.get("ts", ""),
            "fields": row.get("fields", {}),
            "status": row.get("status", ""),
            "work_id": (row.get("work") or {}).get("work_id", ""),
        })
    for row in feedback_history:
        if requested not in (str(row.get("source_id")), str(row.get("target_id"))):
            continue
        other = (row.get("target_id") if str(row.get("source_id")) == requested
                 else row.get("source_id"))
        timeline.append({
            "kind": "relation_feedback", "ts": row.get("ts", ""),
            "action": row.get("action", ""),
            "facet": row.get("facet", "unknown"),
            "relation": row.get("relation", ""),
            "other_source_id": other, "note": row.get("note", ""),
            "work_id": (row.get("work") or {}).get("work_id", ""),
        })
    for row in _portfolio_external_review_history(requested):
        timeline.append({
            "kind": "candidate_review", "ts": row.get("ts", ""),
            "candidate_id": row.get("candidate_id", ""),
            "decision": row.get("decision", ""),
            "note": row.get("note", ""), "relation": row.get("relation", ""),
            "ledger_id": row.get("ledger_id", ""),
            "work_id": row.get("work_id", ""),
        })
    timeline.sort(key=lambda row: str(row.get("ts") or ""))
    triage_label, triage_source = copilot._triage_label_source(item)
    audit["item"] = {
        "source_id": requested,
        "date": item.get("fecha", ""),
        "content_type": item.get("tipo_contenido", ""),
        "asset_available": bool(item.get("asset_available")),
        "current": {
            "selection": current_selection.get("decision", "pendiente"),
            "classification": current_classification.get("fields", {}),
            "triage_label": triage_label or "unlabeled",
            "triage_source": triage_source if triage_label else "none",
        },
        "timeline": timeline,
        "timeline_total": len(timeline),
    }
    return audit


def _portfolio_isolated_external_rows():
    """Read quarantined provider hypotheses without treating them as ledger facts."""
    rows = []
    for row in _portfolio_jsonl(PORTFOLIO_EXTERNAL_REVIEW):
        if row.get("schema") != "mak-external-evidence-v1":
            continue
        if not row.get("work_id") or not row.get("source_id"):
            continue
        rows.append(row)
    return rows


def _portfolio_apply_human_context(items):
    context_by_source = {
        str(row.get("source_id") or ""): row.get("context_fields") or {}
        for row in _portfolio_human_context_records()
        if row.get("source_id") and row.get("context_fields")
    }
    enriched = []
    for item in items or []:
        clone = dict(item)
        fields = context_by_source.get(str(item.get("id") or ""), {})
        if fields:
            human_context = {}
            for field, values in fields.items():
                values = values if isinstance(values, list) else [values]
                existing = clone.get(field)
                existing = existing if isinstance(existing, list) else (
                    [existing] if existing else [])
                merged = []
                for value in [*existing, *values]:
                    value = str(value or "").strip()
                    if value and value not in merged:
                        merged.append(value)
                if merged:
                    clone[field] = merged
                    human_context[field] = merged
            if human_context:
                clone["human_context"] = human_context
        enriched.append(clone)
    return enriched


def _portfolio_external_candidates(item_id=""):
    """Expose traceable external candidates without exposing raw model output."""
    if _ledger is None:
        return {"ok": True, "schema": "faro-portfolio-external-candidate-surface-v1",
                "total": 0, "items": [], "public_promotion": False}
    requested = str(item_id or "").strip()
    items = []
    # Index the inbox once.  Calling _portfolio_item() inside the ledger loop
    # rereads the 7k-item inbox and its sidecars once per candidate row.
    source_items = {
        str(item.get("id")): item
        for item in _portfolio_inbox().get("items", [])
        if isinstance(item, dict) and item.get("id")
    }
    rows = _ledger.read_items(COMMON_LEDGER, limit=10000)
    reviews = {(str(review.get("candidate_id") or "").strip(),
                str(review.get("source_id") or "").strip()): review
               for review in _portfolio_external_review_rows()}
    unique_items = {}
    for row in rows:
        if row.get("domain") != "portfolio":
            continue
        candidate = (row.get("metadata") or {}).get("portfolio_candidate")
        if not isinstance(candidate, dict):
            continue
        source_id = str(candidate.get("entity_id") or
                        (row.get("work") or {}).get("identity", {}).get(
                            "source_id", "")).strip()
        if not source_id:
            continue
        if requested and source_id != requested:
            continue
        triage = candidate.get("triage") or {}
        review = reviews.get((str(row.get("id", "")), source_id), {})
        human_decision = review.get("decision", "pending")
        context_fields = review.get("context_fields", {})
        if not isinstance(context_fields, dict):
            context_fields = {}
        source_item = source_items.get(source_id) or {}
        if not source_item:
            continue
        candidate_item = {
            "ledger_id": row.get("id", ""),
            "source_id": source_id,
            "provider": triage.get("provider", "unknown"),
            "verdict": triage.get("verdict", "revise"),
            "candidate_relations": triage.get("candidate_relations", {}),
            "evidence_basis": triage.get("evidence_basis", []),
            "decision": row.get("decision", "revisar"),
            "next_action": row.get("next_action", "human_review"),
            "human_decision": human_decision,
            "review_state": "pending" if human_decision in ("pending", "revise") else human_decision,
            "context_fields": context_fields,
            "context_state": "structured" if context_fields else "note_only",
            "human_note": review.get("note", ""),
            "reviewed_at": review.get("ts", ""),
            "review_work_id": review.get("work_id", ""),
            "review_traceability": review.get("traceability", ""),
            "item": {
                "tipo_contenido": source_item.get("tipo_contenido", ""),
                "fecha": source_item.get("fecha", ""),
                "publicacion_id": source_item.get("publicacion_id", ""),
                "descripcion_original": source_item.get("descripcion_original", ""),
                "asset_path": source_item.get("asset_path", ""),
                "asset_available": bool(source_item.get("asset_available")),
            },
            "public_promotion": False,
            "candidate_occurrences": 1,
        }
        previous = unique_items.get(source_id)
        if previous is None:
            unique_items[source_id] = candidate_item
            continue
        previous["candidate_occurrences"] = int(
            previous.get("candidate_occurrences") or 1) + 1
        evidence = list(previous.get("evidence_basis") or [])
        for value in candidate_item.get("evidence_basis") or []:
            if value not in evidence:
                evidence.append(value)
        previous["evidence_basis"] = evidence
    for external in _portfolio_isolated_external_rows():
        source_id = str(external.get("source_id") or "").strip()
        if requested and source_id != requested:
            continue
        source_item = source_items.get(source_id) or {}
        if not source_item:
            continue
        evidence = external.get("evidence") or {}
        candidate_id = "instagram-external:" + str(external.get("work_id"))
        review = reviews.get((candidate_id, source_id), {})
        human_decision = review.get("decision", "pending")
        hypothesis = str(external.get("hypothesis") or "").strip()
        evidence_basis = [
            "provider:%s" % str(external.get("provider") or "unknown"),
            "confidence:%s" % str(external.get("confidence") or 0),
            "source:%s" % str(evidence.get("source_ref") or "instagram_export"),
        ]
        candidate_item = {
            "ledger_id": candidate_id,
            "source_id": source_id,
            "provider": external.get("provider", "unknown"),
            "verdict": "hypothesis",
            "candidate_relations": {"visual_similarity": [hypothesis]} if hypothesis else {},
            "evidence_basis": evidence_basis,
            "decision": "revisar",
            "next_action": "human_review",
            "human_decision": human_decision,
            "review_state": "pending" if human_decision in ("pending", "revise") else human_decision,
            "context_fields": review.get("context_fields", {}),
            "context_state": "structured" if review.get("context_fields") else "note_only",
            "human_note": review.get("note", ""),
            "reviewed_at": review.get("ts", ""),
            "review_work_id": review.get("work_id", ""),
            "review_traceability": review.get("traceability", "isolated_provider_evidence"),
            "hypothesis": hypothesis,
            "explanation": str(external.get("explanation") or "").strip(),
            "confidence": external.get("confidence", 0),
            "record_kind": evidence.get("record_kind", "media_candidate"),
            "grouping": evidence.get("grouping", {}),
            "promotion": "not_promoted",
            "item": {
                "tipo_contenido": source_item.get("tipo_contenido", ""),
                "fecha": source_item.get("fecha", ""),
                "publicacion_id": source_item.get("publicacion_id", ""),
                "descripcion_original": source_item.get("descripcion_original", ""),
                "asset_path": source_item.get("asset_path", ""),
                "asset_available": bool(source_item.get("asset_available")),
            },
            "public_promotion": False,
            "candidate_occurrences": 1,
        }
        previous = unique_items.get(source_id)
        if previous is None:
            unique_items[source_id] = candidate_item
            continue
        previous["candidate_occurrences"] = int(
            previous.get("candidate_occurrences") or 1) + 1
        for value in evidence_basis:
            if value not in previous.setdefault("evidence_basis", []):
                previous["evidence_basis"].append(value)
        if hypothesis:
            previous.setdefault("candidate_relations", {}).setdefault(
                "visual_similarity", []).append(hypothesis)
    items = list(unique_items.values())
    return {
        "ok": True,
        "schema": "faro-portfolio-external-candidate-surface-v1",
        "total": len(items),
        "items": items,
        "public_promotion": False,
        "next": "human review before board or publication",
    }


HUMAN_CONTEXT_FIELDS = ("artist", "client", "venue", "event", "festival",
                        "collab", "date", "process")


def _normalize_human_context(value):
    if not isinstance(value, dict):
        return {}
    result = {}
    for field in HUMAN_CONTEXT_FIELDS:
        raw = value.get(field)
        if isinstance(raw, (list, tuple, set)):
            values = raw
        elif raw is None:
            values = []
        else:
            values = [raw]
        clean = []
        for part in values:
            text = str(part or "").strip()[:240]
            if text and text not in clean:
                clean.append(text)
        if clean:
            result[field] = clean[:8]
    return result


def _portfolio_human_context_records():
    surface = _portfolio_external_candidates()
    links = _portfolio_context_links()
    records = []
    for row in surface.get("items", []):
        if row.get("human_decision") != "accept":
            continue
        fields = row.get("context_fields") or {}
        if not fields:
            continue
        records.append({
            "source_id": row.get("source_id", ""),
            "item": row.get("item", {}),
            "context_fields": fields,
            "context_state": "human_confirmed_context",
            "candidate_relations": row.get("candidate_relations", {}),
            "evidence_basis": row.get("evidence_basis", []),
            "human_note": row.get("human_note", ""),
            "reviewed_at": row.get("reviewed_at", ""),
            "promotion": "none",
            "next_action": "link manually to event or venue group",
            "linked_groups": links.get(row.get("source_id", ""), []),
        })
    return records


def _portfolio_review_queue(source_id=""):
    requested = str(source_id or "").strip()
    surface = _portfolio_external_candidates(requested)
    items = [item for item in surface.get("items", [])
             if item.get("review_state") == "pending"]
    return {
        "ok": True,
        "schema": "faro-portfolio-review-queue-v1",
        "status": "human_review_required",
        "total": len(items),
        "items": items,
        "public_promotion": False,
        "next": "human decision required before board or publication",
    }


def _portfolio_external_candidate_review(body):
    """Record a human decision without mutating the original candidate."""
    if _ledger is None:
        return {"ok": False, "error": "ledger_no_disponible"}
    ledger_id = str(body.get("ledger_id") or "").strip()
    decision = str(body.get("decision") or "").strip().lower()
    if decision not in ("accept", "revise", "reject"):
        return {"ok": False, "error": "decision_invalida"}
    requested_source_id = str(body.get("source_id") or "").strip()
    ledger_rows = _ledger.read_items(COMMON_LEDGER, limit=10000)
    source = None
    candidate = None
    if ledger_id.startswith("instagram-external:"):
        external = next((row for row in _portfolio_isolated_external_rows()
                         if "instagram-external:" + str(row.get("work_id")) == ledger_id), None)
        source_id = requested_source_id or str((external or {}).get("source_id") or "").strip()
        if not external or not source_id or str(external.get("source_id")) != source_id:
            return {"ok": False, "error": "candidato_no_encontrado"}
        candidate = {
            "entity_id": source_id,
            "triage": {
                "provider": external.get("provider", "unknown"),
                "verdict": "hypothesis",
                "candidate_relations": {"visual_similarity": [external.get("hypothesis", "")]},
                "evidence_basis": [
                    "source:%s" % str((external.get("evidence") or {}).get("source_ref") or "instagram_export"),
                    "confidence:%s" % str(external.get("confidence") or 0),
                ],
            },
        }
        source = {"work": {"work_id": external.get("work_id", "")},
                  "metadata": {"portfolio_candidate": candidate}}
    else:
        matching_sources = [row for row in ledger_rows
                            if row.get("id") == ledger_id
                            and row.get("domain") == "portfolio"
                            and isinstance((row.get("metadata") or {}).get(
                                "portfolio_candidate"), dict)]
        if requested_source_id:
            matching_sources = [row for row in matching_sources
                                if str(((row.get("metadata") or {}).get(
                                    "portfolio_candidate") or {}).get(
                                    "entity_id") or "").strip()
                                == requested_source_id]
        elif len(matching_sources) > 1:
            return {"ok": False, "error": "source_id_requerido",
                    "details": {"ledger_id": ledger_id,
                                 "candidate_count": len(matching_sources)}}
        source = matching_sources[0] if matching_sources else None
        if not source:
            return {"ok": False, "error": "candidato_no_encontrado"}
        candidate = source["metadata"]["portfolio_candidate"]
    prior_context = {}
    for row in ledger_rows:
        prior = (row.get("metadata") or {}).get("external_candidate_review")
        if (isinstance(prior, dict)
                and prior.get("candidate_id") == ledger_id
                and (not requested_source_id
                     or str(prior.get("source_id") or "").strip()
                     == requested_source_id)):
            prior_context = _normalize_human_context(prior.get("context_fields"))
    context_fields = _normalize_human_context(body.get("context_fields")) or prior_context
    note = str(body.get("note") or "").strip()[:1000]
    relation = str(body.get("relation") or "").strip()[:120]
    # A transport retry of the same human decision must not create a second
    # history row. Different decisions or notes remain append-only history.
    for row in ledger_rows:
        prior = (row.get("metadata") or {}).get("external_candidate_review")
        if (isinstance(prior, dict)
                and prior.get("candidate_id") == ledger_id
                and str(prior.get("source_id") or "").strip()
                == str(candidate.get("entity_id") or "").strip()
                and prior.get("decision") == decision
                and str(prior.get("note") or "") == note
                and str(prior.get("relation") or "") == relation
                and _normalize_human_context(prior.get("context_fields"))
                == context_fields):
            return {"ok": True, "review": dict(prior),
                    "ledger_id": row.get("id", ""), "duplicate": True}
    ts = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    next_action = "continue triangulation or add to board" if decision == "accept" \
        else "revisit candidate evidence" if decision == "revise" \
        else "retain rejected candidate without promotion"
    candidate_work = source.get("work") if isinstance(source.get("work"), dict) else {}
    work_id = "portfolio-review:%s:%s" % (candidate.get("entity_id", ""),
                                           ts.replace(":", "").replace("+", "p").replace("-", "m"))
    identity = {
        "kind": "portfolio_review",
        "source_id": candidate.get("entity_id", ""),
        "parent_id": candidate_work.get("work_id", ""),
        "entities": context_fields,
        "event_date": next(iter(context_fields.get("date", [])), ""),
    }
    build_work = getattr(_ledger, "build_work_envelope", None)
    if callable(build_work):
        review_work = build_work(
            work_id, candidate_work.get("work_id") or "portfolio_visual_triage",
            "obra", "human adjudication of an external portfolio candidate",
            "human-review", "human",
            sources=["portfolio_inbox:%s" % candidate.get("entity_id", ""), ledger_id],
            status=decision, identity=identity, owner="human",
            next_action=next_action, evidence_required=["source", "human_decision"],
            fallback_chain=["local_deterministic"], created_at=ts)
    else:
        review_work = {
            "schema": "mak-work-v1", "work_id": work_id,
            "parent_task": candidate_work.get("work_id") or "portfolio_visual_triage",
            "lane": "obra", "purpose": "human adjudication of an external portfolio candidate",
            "format": "human-review", "created_at": ts, "provider": "human",
            "sources": ["portfolio_inbox:%s" % candidate.get("entity_id", ""), ledger_id],
            "status": decision, "owner": "human", "next_action": next_action,
            "evidence_required": ["source", "human_decision"],
            "allowed_decisions": ["hacer", "revisar", "refutar", "archivar", "descartar"],
            "fallback_chain": ["local_deterministic"],
            "identity": {"schema": "mak-identity-v1", **identity},
        }
    review = {
        "candidate_id": ledger_id,
        "source_id": candidate.get("entity_id", ""),
        "decision": decision,
        "note": note,
        "relation": relation,
        "context_fields": context_fields,
        "context_state": "structured" if context_fields else "note_only",
        "work_id": review_work["work_id"],
        "ts": ts,
    }
    action = "reject" if decision == "reject" else "review"
    ledger_decision = "descartar" if decision == "reject" else (
        "hacer" if decision == "accept" else "revisar")
    ok, errors, row = _ledger.append_unique({
        "id": "portfolio-external-review:%s:%s" % (ledger_id, review["ts"]),
        "domain": "portfolio",
        "type": "reject" if decision == "reject" else "decision",
        "claim": "Human review of external portfolio candidate %s" % ledger_id,
        "evidence": [ledger_id, candidate.get("entity_id", "")],
        "files": [],
        "confidence": "high",
        "action": action,
        "reject_reason": review["note"] if decision == "reject" else "",
        "lane": "obra",
        "decision": ledger_decision,
        "purpose": "human adjudication without automatic publication",
        "next_action": next_action,
        "owner": "human",
        "work": review_work,
        "metadata": {"external_candidate_review": review},
    }, path=COMMON_LEDGER, source="portfolio_external_review")
    if not ok:
        return {"ok": False, "error": "ledger_rechazo", "details": errors}
    return {"ok": True, "review": review, "ledger_id": row.get("id") if row else ""}


def _portfolio_decision_index():
    candidate_reviews = []
    for review in _portfolio_external_review_rows():
        candidate_reviews.append({
            "candidate_id": review.get("candidate_id", ""),
            "source_id": review.get("source_id", ""),
            "decision": review.get("decision", ""),
            "relation": review.get("relation", ""),
            "context_fields": review.get("context_fields", {}),
            "context_state": review.get("context_state", "note_only"),
            "note": review.get("note", ""),
            "work_id": review.get("work_id", ""),
            "owner": "human",
            "promotion": "none",
            "ts": review.get("ts", ""),
        })
    relation_feedback = [{
        "source_id": row.get("source_id", ""),
        "target_id": row.get("target_id", ""),
        "action": row.get("action", ""),
        "facet": row.get("facet", "unknown"),
        "relation": row.get("relation", ""),
        "board_id": row.get("board_id", ""),
        "note": row.get("note", ""),
        "work_id": (row.get("work") or {}).get("work_id", ""),
        "ts": row.get("ts", ""),
    } for row in _portfolio_feedback()]
    selections = [{
        "item_id": row.get("item_id", ""),
        "decision": row.get("decision", ""),
        "board_id": row.get("board_id", ""),
        "work_id": (row.get("work") or {}).get("work_id", ""),
        "ts": row.get("ts", ""),
    } for row in _portfolio_selections().values()]
    return {
        "ok": True,
        "schema": "faro-portfolio-decision-index-v1",
        "source_of_truth": ["common_ledger", "copilot_feedback", "portfolio_selections"],
        "promotion": "none",
        "candidate_reviews": candidate_reviews,
        "relation_feedback": relation_feedback,
        "selections": selections,
        "counts": {
            "candidate_reviews": len(candidate_reviews),
            "relation_feedback": len(relation_feedback),
            "selections": len(selections),
        },
        "next": "usar work_id y source_id para continuar cada hilo sin mezclar decisiones",
    }


def _portfolio_learning():
    """Expose the learning state, not raw history, to the editor."""
    feedback = _portfolio_feedback()
    candidate_reviews = _portfolio_external_review_rows()
    selections = _portfolio_selections()
    boards = _portfolio_boards().get("boards", [])
    items = _portfolio_apply_human_context(_portfolio_inbox().get("items", []))
    atlas = copilot.build_gtm_map(items, feedback=feedback, stable_topology=True)
    ordering = dict(atlas.get("ordering") or copilot.ordering_profile(items))
    ordering["human_seed"] = copilot.active_ordering_seed(items, atlas)
    ordering["atlas"] = atlas.get("atlas", {})
    external = _portfolio_jsonl(PORTFOLIO_EXTERNAL)
    vision = list(_portfolio_vision().values())
    visual_surface = _portfolio_visual_surface()
    visual_feedback = [row for row in feedback
                       if str(row.get("facet") or "").lower() == "visual_similarity"
                       or str(row.get("relation") or "") == "visual_similarity"]
    return {
        "ok": True,
        "schema": "faro-portfolio-learning-surface-v1",
        "profile": copilot.learning_profile(feedback),
        "ordering": ordering,
        "external_evidence": copilot.external_evidence_profile(external, vision),
        "visual_similarity": {
            **visual_surface.get("profile", {"available": False}),
            "feedback_total": len(visual_feedback),
            "feedback_accept": sum(1 for row in visual_feedback
                                    if row.get("action") in ("accept", "correct")),
            "feedback_reject": sum(1 for row in visual_feedback
                                    if row.get("action") == "reject"),
        },
        "candidate_reviews": copilot.review_profile(candidate_reviews),
        "selections": {
            "selected": sum(1 for row in selections.values()
                            if row.get("decision") == "seleccionar"),
            "excluded": sum(1 for row in selections.values()
                             if row.get("decision") == "deseleccionar"),
        },
        "boards": [{"id": row.get("id"), "name": row.get("name"),
                    "facet": row.get("facet", "general"),
                    "items": len(row.get("item_ids") or [])}
                   for row in boards],
        "next": "seguir seleccionando; las sugerencias cambian por faceta, no por una palabra aislada",
    }


def _portfolio_feedback_record(body):
    action = str(body.get("action", ""))
    if action not in ("accept", "reject", "ignore", "correct"):
        return {"ok": False, "error": "feedback_invalido"}
    source = str(body.get("source_id", ""))
    target = str(body.get("target_id", ""))
    if not _portfolio_item(source) or not _portfolio_item(target) or source == target:
        return {"ok": False, "error": "items_invalidos"}
    facet = str(body.get("facet", "unknown")).lower()[:40]
    relation = str(body.get("relation", "relacionada"))[:80]
    raw_visual = body.get("visual") if isinstance(body.get("visual"), dict) else {}
    visual = {}
    if facet == "visual_similarity" or relation == "visual_similarity":
        try:
            score = float(raw_visual.get("score", body.get("visual_score", 0)))
            margin = float(raw_visual.get("margin", body.get("visual_margin", 0)))
        except (TypeError, ValueError):
            score, margin = 0.0, 0.0
        if math.isfinite(score) and math.isfinite(margin):
            visual = {
                "score": round(max(-1.0, min(1.0, score)), 6),
                "margin": round(max(0.0, min(1.0, margin)), 6),
                "model": str(raw_visual.get("model") or body.get(
                    "visual_model", "MobileCLIP-S0"))[:100],
                "model_version": str(raw_visual.get("model_version") or body.get(
                    "visual_version", ""))[:120],
                "evidence_kind": "visual_similarity",
            }
    note = str(body.get("note") or body.get("comment") or "").strip()[:1000]
    existing = next((row for row in reversed(_portfolio_feedback())
                     if str(row.get("source_id")) == source
                     and str(row.get("target_id")) == target
                     and str(row.get("action")) == action
                     and str(row.get("facet")) == facet
                     and str(row.get("relation")) == relation
                     and (row.get("visual") or {}) == visual
                     and str(row.get("note") or "") == note), None)
    if existing:
        result = {"ok": True, "feedback": existing, "duplicate": True}
        if action in ("accept", "correct"):
            connection = _portfolio_connect({
                "source_id": source, "target_id": target,
                "relation": relation,
            })
            result["connection"] = connection
            result["connection_saved"] = bool(connection.get("ok"))
            if not connection.get("ok"):
                return {"ok": False, "error": "conexion_no_guardada",
                        "feedback": existing, "feedback_saved": True,
                        "connection_saved": False, "details": connection}
        return result
    row = {"source_id": source, "target_id": target, "action": action,
           "facet": facet,
           "board_id": str(body.get("board_id", ""))[:100],
           "relation": relation,
           "note": note,
           "evidence_kind": "visual_similarity" if visual else "",
           "visual": visual,
           "work": {"schema": "mak-work-v1",
                     "work_id": "portfolio-relation:%s:%s" % (source, target),
                     "parent_task": "portfolio-curation",
                     "lane": "obra", "purpose": "human relation feedback",
                     "format": "relationship", "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                     "provider": "human", "sources": [source, target],
                     "status": "candidate_feedback",
                     "evidence_kind": "visual_similarity" if visual else "",
                     "model": visual.get("model", ""),
                     "model_version": visual.get("model_version", "")},
           "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    if _ledger is not None:
        action_name = "curate" if action in ("accept", "correct") else "reject"
        decision = "revisar" if action in ("accept", "correct", "ignore") else "descartar"
        ledger_ok, ledger_errors, _ledger_row = _ledger.append_unique({
            "id": "portfolio-feedback:%s:%s:%s:%s" % (
                source, target, action, row["ts"]),
            "domain": "iskvw", "type": "reject" if action == "reject" else "decision",
            "claim": "portfolio relation %s -> %s" % (source, target),
            "evidence": [source, target, row["relation"]]
            + (["visual_score:%s" % visual["score"],
                "visual_margin:%s" % visual["margin"],
                "visual_model:%s" % visual["model"]] if visual else []),
            "confidence": "high" if action in ("accept", "correct", "reject") else "medium",
            "action": action_name, "decision": decision,
            "purpose": "learn from human curation without promoting a fact",
            "next_action": "retain as candidate relation for review",
            "owner": "human", "work": row["work"],
            "reject_reason": "artist rejected relation" if action == "reject" else "",
            "note": note},
            path=COMMON_LEDGER, source="portfolio_copilot")
        if not ledger_ok:
            return {"ok": False, "error": "ledger_rechazo", "details": ledger_errors}
    os.makedirs(os.path.dirname(PORTFOLIO_FEEDBACK), exist_ok=True)
    with open(PORTFOLIO_FEEDBACK, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    connection = {"ok": True, "skipped": True}
    if action in ("accept", "correct"):
        connection = _portfolio_connect({"source_id": source, "target_id": target,
                                         "relation": row["relation"]})
        if not connection.get("ok"):
            return {"ok": False, "error": "conexion_no_guardada",
                    "feedback": row, "feedback_saved": True,
                    "connection_saved": False, "details": connection}
    return {"ok": True, "feedback": row, "connection": connection,
            "feedback_saved": True, "connection_saved": bool(connection.get("ok"))}


def _portfolio_external_review(body):
    item_id = str(body.get("item_id", ""))
    provider = str(body.get("provider", "")).lower()
    if provider not in ("watsonx", "aws", "ollama", "groq", "cerebras"):
        return {"ok": False, "error": "proveedor_invalido"}
    source = _portfolio_item(item_id)
    if not source:
        return {"ok": False, "error": "item_no_encontrado"}
    candidates = [item for item in _portfolio_inbox().get("items", [])
                  if item.get("id") != item_id
                  and item.get("selection") != "descartar"
                  and item.get("publicacion_id") != source.get("publicacion_id")][:96]
    board_id = str(body.get("board_id", ""))
    board = next((row for row in _portfolio_boards().get("boards", [])
                  if row.get("id") == board_id), {})
    board = dict(board)
    board.update(_portfolio_item_context(item_id))
    prompt = {
        "prompt": copilot.inference_prompt(source, candidates, context=board),
        "source_manifest": copilot.media_manifest(source),
        "candidate_count": len(candidates),
    }
    try:
        providers.load_env()
        raw = providers.call(provider, json.dumps(prompt, ensure_ascii=False),
                             max_tokens=1400, temperature=0.1)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": "provider_error", "detail": str(exc)[:180]}
    normalized = copilot.normalize_inference(
        raw, item_id, [item.get("id") for item in candidates])
    quality = copilot.inference_quality(normalized)
    row = {"item_id": item_id, "provider": provider, "inference": normalized,
           "quality": quality,
           "raw": raw,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    os.makedirs(os.path.dirname(PORTFOLIO_EXTERNAL), exist_ok=True)
    with open(PORTFOLIO_EXTERNAL, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"ok": True, "provider": provider, "inference": normalized,
            "quality": quality,
            "raw": raw,
            "stored": PORTFOLIO_EXTERNAL}


def _portfolio_media_reference(value):
    value = str(value or "")
    for prefix in ("/portfolio-media/", "portfolio-media/"):
        if value.startswith(prefix):
            value = value[len(prefix):]
            break
    return _portfolio_media(value)


def _portfolio_visual_asset(item):
    """Resolve an existing still or one cached contact sheet for a video."""
    candidates = []
    for field in ("preview_path", "poster_path", "thumbnail_path", "asset_path"):
        value = str(item.get(field) or "").strip()
        if value:
            candidates.append(value)
    for value in candidates:
        asset = _portfolio_media_reference(value)
        if asset and os.path.splitext(asset)[1].lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            return asset, value
    for value in candidates:
        suffix = os.path.splitext(value.split("?", 1)[0])[1].lower()
        if suffix not in {".mp4", ".mov", ".webm", ".m4v"}:
            continue
        video_asset = _portfolio_media_reference(value)
        if not video_asset:
            continue
        directory, filename = value.rsplit("/", 1) if "/" in value else ("", value)
        stem = os.path.splitext(filename)[0]
        for extension in (".jpg", ".jpeg", ".png", ".webp"):
            relative = "%s/%s%s" % (directory, stem, extension) if directory else stem + extension
            asset = _portfolio_media_reference(relative)
            if asset:
                return asset, relative
        if _percepcion is None:
            continue
        item_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(item.get("id") or stem))
        sheet_name = "%s.contact.jpg" % os.path.splitext(item_id)[0]
        os.makedirs(PORTFOLIO_CONTACT_SHEETS, exist_ok=True)
        sheet_path = os.path.join(PORTFOLIO_CONTACT_SHEETS, sheet_name)
        if not os.path.isfile(sheet_path):
            ok, _reason = _percepcion.generar_contact_sheet(
                video_asset, sheet_path, timeout=90)
            if not ok:
                continue
        relative = "/portfolio-media/_contact_sheets/%s" % sheet_name
        return sheet_path, relative
    return None, ""


def _portfolio_visual_surface(item_id="", limit=8):
    """Read derived neighbors without loading torch or reserving the GPU."""
    if _visual_index is None:
        return {"available": False, "reason": "visual_adapter_unavailable",
                "relations": [], "profile": {"available": False}}
    try:
        surface = _visual_index.read_surface(PORTFOLIO_VISUAL_INDEX_ROOT)
        profile = _visual_index.surface_profile(surface)
        relations = _visual_index.visual_relations(item_id, surface, limit=limit)
        return {"available": bool(surface.get("available")),
                "reason": surface.get("reason", ""), "relations": relations,
                "profile": profile}
    except Exception as exc:  # noqa: BLE001 - metadata copilot must survive it
        return {"available": False, "reason": "visual_index_error:%s" % str(exc)[:120],
                "relations": [], "profile": {"available": False}}


def _portfolio_xio_evidence(limit=24):
    """Expose bounded XIO show-kit evidence without linking it to media."""
    if _xio_evidence is None:
        return {"ok": True, "available": False, "schema": "faro-xio-evidence-v1",
                "source": "xio/show_kit", "reason": "xio_adapter_unavailable",
                "evidence": [], "segments": []}
    try:
        return _xio_evidence.load_show_evidence(PORTFOLIO_XIO_SHOW_ROOT, limit=limit)
    except Exception as exc:  # noqa: BLE001 - portfolio must keep serving
        return {"ok": True, "available": False, "schema": "faro-xio-evidence-v1",
                "source": "xio/show_kit", "reason": "xio_evidence_error:%s" % str(exc)[:120],
                "evidence": [], "segments": []}


def _portfolio_vision_read(body):
    item_id = str(body.get("item_id", "")).strip()
    provider = str(body.get("provider", "aws")).lower().strip()
    if provider != "aws":
        return {"ok": False, "error": "vision_requiere_aws",
                "detail": "Watsonx y los modelos de texto pueden adjudicar la lectura, pero no reciben la imagen en este puente."}
    source = _portfolio_item(item_id)
    if not source:
        return {"ok": False, "error": "item_no_encontrado"}
    asset, evidence_path = _portfolio_visual_asset(source)
    if not asset:
        return {"ok": False, "error": "media_visual_no_disponible",
                "detail": "No existe un still sincronizado para esta pieza; el video no se envia sin fotograma."}
    evidence_kind = "video_contact_sheet" if evidence_path.endswith(".contact.jpg") else "still_image"
    previous = _portfolio_vision().get(item_id)
    if (previous and previous.get("provider") == provider
            and evidence_path in (previous.get("evidence") or [])):
        return {"ok": True, "schema": copilot.VISION_SCHEMA, "provider": provider,
                "item_id": item_id, "features": previous.get("features", {}),
                "unknowns": previous.get("unknowns", []),
                "confidence": previous.get("confidence", "low"),
                "evidence": previous.get("evidence", []),
                "evidence_kind": previous.get("evidence_kind", evidence_kind),
                "stored": PORTFOLIO_VISION, "duplicate": True}
    prompt = json.dumps({
        "task": "Describir solo lo visible en la imagen adjunta para apoyar una curatoria.",
        "evidence_kind": evidence_kind,
        "rules": [
            "No identifiques ni inventes artista, venue, evento, cliente o fecha.",
            "No conviertas una semejanza visual en una entidad.",
            "Separa observaciones de desconocidos.",
            "Si evidence_kind es video_contact_sheet, describe motion_or_media como fotogramas muestreados del video y no como una imagen fija original.",
            "Devuelve solo JSON con visual_terms, dominant_colors, composition, motion_or_media, unknowns y confidence.",
        ],
        "item": {"item_id": item_id, "content_type": source.get("tipo_contenido")},
    }, ensure_ascii=False)
    try:
        providers.load_env()
        raw = providers.call("aws", prompt, model=body.get("model") or None,
                             max_tokens=900, temperature=0.1, image_paths=[asset])
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": "provider_error", "detail": str(exc)[:180]}
    normalized = copilot.normalize_vision(raw, item_id, provider, [evidence_path])
    row = dict(normalized)
    row["asset_path"] = evidence_path
    row["evidence_kind"] = evidence_kind
    row["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    os.makedirs(os.path.dirname(PORTFOLIO_VISION), exist_ok=True)
    with open(PORTFOLIO_VISION, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"ok": True, "schema": copilot.VISION_SCHEMA, "provider": provider,
            "item_id": item_id, "features": normalized["features"],
            "unknowns": normalized["unknowns"], "confidence": normalized["confidence"],
            "evidence": normalized["evidence"], "evidence_kind": evidence_kind,
            "stored": PORTFOLIO_VISION}


def _portfolio_media(relative):
    value = str(relative or "").lstrip("/")
    if not value or ".." in value.split("/"):
        return None
    root = os.path.realpath(PORTFOLIO_MEDIA_ROOT)
    candidate = os.path.realpath(os.path.join(root, value))
    try:
        if os.path.commonpath((root, candidate)) != root:
            return None
    except ValueError:
        return None
    return candidate if os.path.isfile(candidate) else None


def _portfolio_dispatch(item_id, depto, texto):
    item = _portfolio_item(item_id)
    if depto not in ("research", "codex"):
        return {"ok": False, "error": "departamento_invalido"}
    if not item:
        return {"ok": False, "error": "item_no_encontrado"}
    return _ejecutar(depto, "revision_portafolio", texto, "medio")


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
_ARCHIVO_CACHE = {"t": 0.0, "data": None}


def _micelio():
    ahora = time.time()
    if ahora - _MIC_CACHE["t"] < 12 and _MIC_CACHE["data"]["nodes"]:
        return _MIC_CACHE["data"]
    g = _http_json(RESEARCH_URL + "/api/memoria/grafo?umbral=0.5&limite=600", timeout=5.0)
    if g and "nodes" in g:
        _MIC_CACHE["data"] = g
        _MIC_CACHE["t"] = ahora
    return _MIC_CACHE["data"]


def _archivo_publico():
    """Cache the converted public graph instead of rebuilding it per request."""
    ahora = time.time()
    if ahora - _ARCHIVO_CACHE["t"] < 30 and _ARCHIVO_CACHE["data"]:
        return _ARCHIVO_CACHE["data"]
    cuerpo = contrato_archivo.sustrato_publico(contrato_archivo.convertir(_micelio()))
    _ARCHIVO_CACHE["data"] = cuerpo
    _ARCHIVO_CACHE["t"] = ahora
    return cuerpo


def _decisiones():
    """Expose the compact decision queue without exposing raw ledger history."""
    if _ledger is None:
        return {"total": 0, "by_lane": {}, "by_decision": {}, "pending_human": 0}
    resumen = _ledger.summarize(COMMON_LEDGER, limit=200)
    return {
        "total": resumen["total"],
        "by_lane": resumen["by_lane"],
        "by_decision": resumen["by_decision"],
        "pending_human": resumen["pending_human"],
        "last": [{key: row.get(key, "") for key in (
            "id", "lane", "decision", "purpose", "next_action", "owner")}
                 for row in resumen["last"]],
    }


def _oportunidades():
    """Expose opportunity candidates without exposing raw ledger history."""
    if _ledger is None:
        return {"schema": "faro-opportunity-surface-v1", "items": [],
                "counts": {"total": 0, "unverified": 0}}
    items = []
    for row in _ledger.read_items(COMMON_LEDGER, limit=5000):
        if row.get("domain") != "opportunities":
            continue
        card = row.get("metadata", {}).get("opportunity_card", {})
        if not isinstance(card, dict):
            continue
        item = dict(card)
        item.update({
            "ledger_id": row.get("id", ""),
            "decision": row.get("decision", "revisar"),
            "owner": row.get("owner", "human"),
        })
        items.append(item)
    items.reverse()
    return {
        "schema": "faro-opportunity-surface-v1",
        "source": "common_ledger",
        "items": items,
        "counts": {
            "total": len(items),
            "unverified": sum(item.get("status") == "unverified"
                               for item in items),
        },
    }


# ── departamento de render (el puente issue -> flyer) ──
PUENTE_ESTADO = os.path.join(HOME, "plataforma/puente_issues_estado.json")
RENDER_CONFIG = os.path.join(HOME, "plataforma/render_config.json")
FICHAS = os.path.join(HOME, "curatoria/fichas/fichas.jsonl")


def _config_render():
    base = {"activo": True, "remoto": "gdrive", "carpeta": "RD/renders",
            "etiqueta": "instagram", "al_departamento": True,
            "pausar_percepcion": True}
    try:
        with open(RENDER_CONFIG, encoding="utf-8") as fh:
            base.update(json.load(fh))
    except (OSError, ValueError):
        pass
    return base


def _data_extraida(nombre_bandeja):
    """Lo que el departamento saco del flyer, si ya lo percibio.

    Une los dos lados que hasta ahora no se veian juntos: el render entregado
    y la ficha que la curatoria produjo del mismo archivo. Sin esto el usuario
    veia una imagen y tenia que creer que "la data entro"; aca se ve o no se ve.
    """
    if not nombre_bandeja:
        return None
    try:
        with open(FICHAS, encoding="utf-8", errors="replace") as fh:
            for linea in fh:
                if nombre_bandeja not in linea:
                    continue
                f = json.loads(linea)
                v = f.get("vision") or {}
                return {
                    "headliners": v.get("headliners") or [],
                    "fecha": v.get("fecha") or "",
                    "lugar": v.get("lugar") or v.get("venue") or "",
                    "productora": v.get("productora") or "",
                    "descripcion": (v.get("descripcion") or "")[:220],
                }
    except (OSError, ValueError):
        pass
    return None


def _render_estado():
    cfg = _config_render()
    hechos = []
    try:
        with open(PUENTE_ESTADO, encoding="utf-8") as fh:
            crudo = (json.load(fh) or {}).get("hechos") or {}
    except (OSError, ValueError):
        crudo = {}
    pendientes = []
    for numero, d in sorted(crudo.items(), key=lambda kv: kv[1].get("ts", ""),
                            reverse=True):
        # Un issue puede traer VARIOS links: la jefa manda mas de un evento en
        # el mismo correo. Cada uno es una pieza con su propio destino.
        piezas = d.get("piezas")
        if piezas is None:                      # forma vieja, un solo link
            piezas = [{"url": d.get("url", ""), "code": "",
                       "imagen": d.get("imagen") or 1, "ok": bool(d.get("ok")),
                       "destino": d.get("destino") or "",
                       "en_departamento": d.get("en_departamento"),
                       "pendiente": None}]
        for p in piezas:
            p = dict(p)
            p["datos"] = _data_extraida(p.get("en_departamento"))
            p["issue"] = numero
            p["ts"] = d.get("ts", "")
            if p.get("ok"):
                hechos.append(p)
            else:
                pendientes.append(p)
    return {"config": cfg, "hechos": hechos[:40], "pendientes": pendientes[:20],
            "pendientes_bandeja": _cuenta_bandeja()}


def _cuenta_bandeja():
    ruta = os.path.join(HOME, "RD", "desde_issues")
    try:
        return len([n for n in os.listdir(ruta) if n.lower().endswith(".jpg")])
    except OSError:
        return 0


def _guardar_config_render(nueva):
    cfg = _config_render()
    for clave in ("activo", "remoto", "carpeta", "etiqueta",
                  "al_departamento", "pausar_percepcion"):
        if clave in nueva:
            cfg[clave] = nueva[clave]
    tmp = RENDER_CONFIG + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, RENDER_CONFIG)
    return cfg


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


def _memoria():
    """Expose deterministic backlog health without exposing report contents."""
    if _backlog is None or not hasattr(_backlog, "auditar_memoria"):
        return {"accion": "auditoria_no_disponible"}
    dirs = [os.path.join(HOME, "research", d) for d in
            ("informes", "cadenas", "paneles", "refutaciones", "grafos", "memoria")]
    try:
        return _backlog.auditar_memoria(
            dirs, os.path.join(HOME, "plataforma", "backlog.jsonl"))
    except Exception:  # noqa: BLE001 - health endpoint must never fail
        return {"accion": "auditoria_no_disponible"}


def _organismo():
    return {"salud": salud.snapshot(),
            "micelio_chunks": _micelio_chunks(),
            "actividad": _actividad(),
            "trabajo": _trabajo(),
            "memoria": _memoria(),
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
            cerrar()
            out.append("<h3>" + _inline_md(line[4:]) + "</h3>")
        elif line.startswith("## "):
            cerrar()
            out.append("<h2>" + _inline_md(line[3:]) + "</h2>")
        elif line.startswith("# "):
            cerrar()
            out.append("<h1>" + _inline_md(line[2:]) + "</h1>")
        elif line.strip() == "---":
            cerrar()
            out.append("<hr>")
        elif line.startswith("> "):
            cerrar()
            out.append("<blockquote>" + _inline_md(line[2:]) + "</blockquote>")
        else:
            m_ol = re.match(r"^(\d+)\.\s+(.*)", line)
            m_ul = re.match(r"^[-*]\s+(.*)", line)
            if m_ol:
                if in_list != "ol":
                    cerrar()
                    out.append("<ol>")
                    in_list = "ol"
                out.append("<li>" + _inline_md(m_ol.group(2)) + "</li>")
            elif m_ul:
                if in_list != "ul":
                    cerrar()
                    out.append("<ul>")
                    in_list = "ul"
                out.append("<li>" + _inline_md(m_ul.group(1)) + "</li>")
            else:
                cerrar()
                out.append("<p>" + _inline_md(line) + "</p>")
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
        self._send_bytes(data, ctype=ctype, code=code)

    def _send_bytes(self, data, ctype="application/octet-stream", code=200):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            # A browser/client may cancel a media or JSON request after the
            # current scene changes. This is not a Hub failure and should not
            # pollute the service log with a traceback.
            return

    def _json(self, obj, code=200):
        self._send(json.dumps(obj, ensure_ascii=False),
                   "application/json; charset=utf-8", code)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        p = u.path
        if p == "/api/director/capabilities":
            return self._json(_director_capabilities())
        if p == "/api/portfolio/identity-graph":
            return self._json(_portfolio_identity_graph())
        if p == "/revision":
            self.send_response(301)
            self.send_header("Location", "/revision/")
            self.end_headers()
            return
        if p == "/revision/" and _revision is not None:
            return self._send(_revision.PAGE)
        if p.startswith("/revision/media/") and _revision is not None:
            asset = _revision.media_path("/" + p[len("/revision/media/"):])
            if asset is None:
                return self._send("(imagen no encontrada)", "text/plain", 404)
            return self._send_bytes(asset.read_bytes(), "image/jpeg")
        if p == "/api/revision" and _revision is not None:
            return self._json(_revision.api())
        if p == "/revision/episodios" and _episode_revision is not None:
            return self._send(_episode_revision.PAGE)
        if p == "/api/revision/episodios" and _episode_revision is not None:
            return self._json(_episode_revision.api())
        if p == "/api/revision/evidencia" and _episode_revision is not None:
            return self._json(_episode_revision.evidence())
        if p == "/api/portfolio/inbox":
            query = urllib.parse.parse_qs(u.query)
            compact = (query.get("surface") or [""])[0] == "mesa"
            return self._json(_portfolio_inbox(compact=compact))
        if p == "/api/portfolio/index":
            return self._json(_portfolio_metadata_index())
        if p == "/api/portfolio/decision-index":
            return self._json(_portfolio_decision_index())
        if p == "/api/portfolio/audit":
            query = urllib.parse.parse_qs(u.query)
            source_id = (query.get("source_id") or query.get("item_id") or [""])[0]
            audit = _portfolio_audit(source_id)
            return self._json(audit, 404 if not audit.get("ok") else 200)
        if p == "/api/portfolio/classifications":
            return self._json({"ok": True,
                               "schema": "faro-portfolio-classification-v1",
                               "items": list(_portfolio_classifications().values())})
        if p == "/api/portfolio/boards":
            return self._json(_portfolio_boards())
        if p == "/api/portfolio/triangulation":
            return self._json(_portfolio_triangulation())
        if p == "/api/portfolio/organism":
            return self._json(_portfolio_organism_projection())
        if p == "/api/portfolio/contract":
            return self._json({
                "schema": "faro-portfolio-contract-surface-v1",
                "source_of_truth": ["portfolio_inbox", "classifications", "vision_features",
                                     "boards", "connections", "copilot_feedback", "common_ledger"],
                **_portfolio_contract_surface(),
            })
        if p == "/api/portfolio/review-queue":
            item_id = (urllib.parse.parse_qs(u.query).get("source_id") or [""])[0]
            return self._json(_portfolio_review_queue(item_id))
        if p == "/api/portfolio/external-candidates":
            item_id = (urllib.parse.parse_qs(u.query).get("item_id") or [""])[0]
            return self._json(_portfolio_external_candidates(item_id))
        if p == "/api/research/legacy-reports":
            query = urllib.parse.parse_qs(u.query)
            limit = (query.get("limit") or [100])[0]
            current = (query.get("classification") or [""])[0]
            return self._json(_legacy_report_index(limit, current))
        if p == "/api/research/rescue":
            return self._json(_legacy_rescue_queue())
        if p == "/api/portfolio/copilot/suggestions":
            query = urllib.parse.parse_qs(u.query)
            item_id = (query.get("item_id") or [""])[0]
            board_id = (query.get("board_id") or [""])[0]
            include_map = (query.get("map") or ["0"])[0] == "1"
            focus_facet = (query.get("facet") or [""])[0]
            shuffle = (query.get("mode") or [""])[0] == "shuffle"
            shuffle_seed = (query.get("seed") or [""])[0]
            return self._json(_portfolio_suggestions(
                item_id, board_id, include_map, focus_facet, shuffle, shuffle_seed))
        if p == "/api/portfolio/copilot/scene":
            query = urllib.parse.parse_qs(u.query)
            item_id = (query.get("item_id") or [""])[0]
            raw_limit = (query.get("limit") or [10])[0]
            try:
                limit = int(raw_limit)
            except (TypeError, ValueError):
                limit = 10
            focus_facet = (query.get("facet") or [""])[0]
            shuffle = (query.get("mode") or [""])[0] == "shuffle"
            shuffle_seed = (query.get("seed") or [""])[0]
            surface = (query.get("surface") or [""])[0]
            return self._json(_portfolio_scene(
                item_id, limit=limit, focus_facet=focus_facet,
                shuffle=shuffle, shuffle_seed=shuffle_seed, surface=surface))
        if p == "/api/portfolio/copilot/map":
            query = urllib.parse.parse_qs(u.query)
            width = (query.get("width") or [8])[0]
            height = (query.get("height") or [6])[0]
            try:
                width, height = int(width), int(height)
            except (TypeError, ValueError):
                width, height = 8, 6
            return self._json(copilot.build_gtm_map(
                _portfolio_inbox().get("items", []),
                feedback=_portfolio_feedback(), width=width, height=height))
        if p == "/api/portfolio/copilot/vision":
            item_id = (urllib.parse.parse_qs(u.query).get("item_id") or [""])[0]
            item = _portfolio_item(item_id)
            if not item:
                return self._json({"ok": False, "error": "item_no_encontrado"}, 404)
            record = _portfolio_vision().get(item_id)
            return self._json({"ok": True, "schema": copilot.VISION_SCHEMA,
                               "item_id": item_id,
                               "features": (record or {}).get("features", {}),
                               "unknowns": (record or {}).get("unknowns", []),
                               "confidence": (record or {}).get("confidence", "low"),
                               "available": bool(record)})
        if p == "/api/portfolio/copilot/manifest":
            item_id = (urllib.parse.parse_qs(u.query).get("item_id") or [""])[0]
            item = _portfolio_item(item_id)
            if not item:
                return self._json({"ok": False, "error": "item_no_encontrado"}, 404)
            suggestions = _portfolio_suggestions(item_id).get("suggestions", [])
            candidates = [_portfolio_item(row["item_id"]) for row in suggestions]
            return self._json({"ok": True, "schema": "faro-portfolio-learning-manifest-v1",
                               "source": copilot.media_manifest(item),
                               "candidates": [copilot.media_manifest(x) for x in candidates if x]})
        if p == "/api/portfolio/copilot/visual-index":
            item_id = (urllib.parse.parse_qs(u.query).get("item_id") or [""])[0]
            surface = _portfolio_visual_surface(item_id)
            return self._json({"ok": True, "schema": "faro-portfolio-visual-index-surface-v1",
                               "profile": surface.get("profile", {}),
                               "relations": surface.get("relations", []),
                               "reason": surface.get("reason", "")})
        if p == "/api/portfolio/copilot/xio-evidence":
            return self._json(_portfolio_xio_evidence())
        if p == "/api/portfolio/copilot/status":
            providers.load_env()
            visual = _portfolio_visual_surface()
            return self._json({"ok": True, "provider_status": copilot.provider_status(os.environ),
                               "active": "local_hypothesis_engine",
                               "visual_similarity": visual.get("profile", {})})
        if p == "/api/portfolio/copilot/learning":
            return self._json(_portfolio_learning())
        if p.startswith("/api/"):
            return self._json({"ok": False, "error": "ruta_api_no_encontrada",
                               "path": p}, 404)
        if p.startswith("/portfolio-media/"):
            asset = _portfolio_media(p[len("/portfolio-media/"):])
            if asset is None:
                return self._send("(media no disponible en MAK)", "text/plain", 404)
            return self._send_bytes(open(asset, "rb").read(),
                                    mimetypes.guess_type(asset)[0] or "application/octet-stream")
        if p == "/portafolio":
            self.send_response(301)
            self.send_header("Location", "/portafolio/")
            self.end_headers()
            return
        if p.startswith("/portafolio/"):
            relative = p[len("/portafolio/"): ] or "editor.html"
            asset = _portfolio_file(relative)
            if asset is None:
                return self._send("(recurso de portafolio no encontrado)",
                                  "text/plain; charset=utf-8", 404)
            try:
                with open(asset, "rb") as fh:
                    data = fh.read()
            except OSError:
                return self._send("(no se pudo leer el recurso)",
                                  "text/plain; charset=utf-8", 404)
            ctype = mimetypes.guess_type(asset)[0] or "application/octet-stream"
            if ctype == "text/html":
                ctype += "; charset=utf-8"
            return self._send_bytes(data, ctype=ctype)
        if p == "/api/organismo":
            try:
                return self._json(_organismo())
            except Exception as e:  # noqa: BLE001
                return self._json({"error": str(e)[:200]})
        if p == "/api/micelio":
            return self._json(_micelio())
        if p == "/api/archivo":
            # The substrate contract (iskvw/ESQUEMA_ARCHIVO.md): the same
            # micelio, served as pieces + relations so a skin or an external
            # agent never needs to know the internal node schema. Conversion
            # is shared with tools/gen_archivo_iskvw.py (contrato_archivo).
            try:
                cuerpo = _archivo_publico()
                return self._json({
                    "version": 1,
                    "fuente": "micelio",
                    "generado": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "piezas": cuerpo["piezas"],
                    "vinculos": cuerpo["vinculos"],
                    "meta": {"piezas": len(cuerpo["piezas"]),
                             "vinculos": len(cuerpo["vinculos"])},
                })
            except Exception as e:  # noqa: BLE001
                return self._json({"error": str(e)[:200],
                                   "piezas": [], "vinculos": []})
        if p == "/api/decisiones":
            try:
                return self._json(_decisiones())
            except Exception as e:  # noqa: BLE001
                return self._json({"error": str(e)[:200], "total": 0,
                                   "by_lane": {}, "by_decision": {},
                                   "pending_human": 0})
        if p == "/api/oportunidades":
            try:
                return self._json(_oportunidades())
            except Exception as e:  # noqa: BLE001
                return self._json({"error": str(e)[:200],
                                   "schema": "faro-opportunity-surface-v1",
                                   "items": [],
                                   "counts": {"total": 0, "unverified": 0}})
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
        if p == "/api/ideas":
            try:
                return self._json({"ideas": list(reversed(ideas.cargar()))})
            except Exception as e:  # noqa: BLE001
                return self._json({"error": str(e)[:200], "ideas": []})
        if p == "/api/render":
            try:
                return self._json(_render_estado())
            except Exception as e:  # noqa: BLE001
                return self._json({"error": str(e)[:200], "hechos": [],
                                   "config": {}})
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
        if u.path == "/api/revision/episodios" and _episode_revision is not None:
            largo = min(int(self.headers.get("Content-Length") or 0), 12000)
            try:
                body = json.loads(self.rfile.read(largo).decode("utf-8", "replace"))
            except (ValueError, TypeError):
                return self._json({"ok": False, "error": "json invalido"}, 400)
            return self._json(_episode_revision.record(
                body.get("episodio", ""), body.get("decision", ""), body.get("note", "")))
        if u.path in ("/api/director/work", "/api/director/decision",
                      "/api/portfolio/select", "/api/portfolio/classify",
                      "/api/portfolio/classify-batch",
                      "/api/portfolio/dispatch",
                      "/api/portfolio/board", "/api/portfolio/connect",
                      "/api/portfolio/feedback", "/api/portfolio/triangulation/review",
                      "/api/portfolio/triangulation/context-link",
                      "/api/portfolio/copilot/external",
                      "/api/portfolio/copilot/vision",
                      "/api/portfolio/external-candidates/review"):
            largo = min(int(self.headers.get("Content-Length") or 0), 12000)
            try:
                body = json.loads(self.rfile.read(largo).decode("utf-8", "replace"))
            except (ValueError, TypeError):
                return self._json({"ok": False, "error": "json invalido"}, 400)
            if u.path == "/api/director/work":
                return self._json(_director_work(body))
            if u.path == "/api/director/decision":
                return self._json(_director_decision(body))
            if u.path.endswith("/select"):
                return self._json(_portfolio_select(
                    body.get("item_id"), body.get("decision"),
                    body.get("board_id", ""), body.get("session_id", ""),
                    body.get("pass_size", 0), body.get("decision_scope", "selection"),
                    body.get("reason_code", ""), body.get("target_id", ""),
                    body.get("note", "")))
            if u.path.endswith("/classify"):
                return self._json(_portfolio_classify(body))
            if u.path.endswith("/classify-batch"):
                return self._json(_portfolio_classify_batch(body))
            if u.path.endswith("/board"):
                return self._json(_portfolio_board_action(body))
            if u.path.endswith("/connect"):
                return self._json(_portfolio_connect(body))
            if u.path.endswith("/feedback"):
                return self._json(_portfolio_feedback_record(body))
            if u.path.endswith("/triangulation/review"):
                return self._json(_portfolio_triage_record(body))
            if u.path.endswith("/triangulation/context-link"):
                return self._json(_portfolio_context_link(body))
            if u.path.endswith("/external"):
                return self._json(_portfolio_external_review(body))
            if u.path.endswith("/vision"):
                return self._json(_portfolio_vision_read(body))
            if u.path.endswith("/external-candidates/review"):
                return self._json(_portfolio_external_candidate_review(body))
            return self._json(_portfolio_dispatch(body.get("item_id"), body.get("depto"),
                                                   body.get("texto", "")))
        if u.path == "/api/revision" and _revision is not None:
            largo = min(int(self.headers.get("Content-Length") or 0), 5000)
            try:
                body = json.loads(self.rfile.read(largo).decode("utf-8", "replace"))
            except (ValueError, TypeError):
                return self._json({"ok": False, "error": "json invalido"}, 400)
            return self._json(_revision.record(body.get("video"),
                                               body.get("decision"),
                                               body.get("note", "")))
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
        if u.path == "/api/ideas":
            largo = min(int(self.headers.get("Content-Length") or 0), 12000)
            try:
                body = json.loads(self.rfile.read(largo).decode("utf-8", "replace"))
            except (ValueError, TypeError):
                return self._json({"ok": False, "error": "json invalido"}, 400)
            accion = str(body.get("accion", ""))
            texto = str(body.get("texto", ""))[:2000]
            try:
                if accion == "anotar":
                    return self._json(ideas.anotar(
                        texto, origen_id=body.get("origen_id"),
                        origen_dir=body.get("origen_dir")))
                if accion == "encargar":
                    depto = str(body.get("depto", "research"))
                    return self._json(ideas.encargar(str(body.get("id", "")), depto))
                if accion == "priorizar":
                    return self._json(ideas.priorizar(texto))
            except Exception as e:  # noqa: BLE001
                return self._json({"ok": False, "error": str(e)[:200]}, 500)
            return self._json({"ok": False, "error": "accion desconocida"}, 400)
        if u.path == "/api/render":
            largo = min(int(self.headers.get("Content-Length") or 0), 4000)
            try:
                body = json.loads(self.rfile.read(largo).decode("utf-8", "replace"))
            except (ValueError, TypeError):
                return self._json({"ok": False, "error": "json invalido"}, 400)
            try:
                return self._json({"ok": True, "config": _guardar_config_render(body)})
            except Exception as e:  # noqa: BLE001
                return self._json({"ok": False, "error": str(e)[:200]}, 500)
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
