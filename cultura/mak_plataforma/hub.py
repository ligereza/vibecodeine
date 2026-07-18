#!/usr/bin/env python3
"""hub.py -- LA CARA del organismo MAK (puerto 8900).

No es un tablero de analisis: es un canvas vivo de NODOS y CIRCUITOS que UNE
los departamentos. El nucleo MAK al centro; research y codex como nodos
ejecutables cableados al nucleo; las piezas de ambos forman el micelio (cada
una gravita a su departamento). Desde la cara se ANALIZA (ver la data) y se
EJECUTA (lanzar tareas). El hub proxea la ejecucion: el navegador solo habla
con :8900. research y codex corren abiertos (LAN privada Face A, sin token).

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
try:
    import roles as _roles
    _MAXDIA = _roles.MAX_DIA
except Exception:  # noqa: BLE001
    _MAXDIA = 24

# ── LA CARA (canvas de nodos y circuitos) ──
PAGINA = r"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MAK — la cara del organismo</title><style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;overflow:hidden}
body{background:#080706;color:#c9c5b9;font-family:ui-monospace,SFMono-Regular,monospace}
#circuitos{position:fixed;inset:0;z-index:1;pointer-events:none}
#nodos{position:fixed;inset:0;z-index:2;pointer-events:none}
.nodo{position:absolute;transform:translate(-50%,-50%);border-radius:50%;
 display:flex;align-items:center;justify-content:center;pointer-events:auto;
 background:#0d0b09;border:1.8px solid #5a564a;transition:transform .15s,border-color .15s}
.nodo-core{width:64px;height:64px;font-size:28px;border-color:#9db67c}
.nodo-dep{width:52px;height:52px;font-size:22px;cursor:pointer}
.nodo-dep:hover{transform:translate(-50%,-50%) scale(1.14)}
.nodo-dep .lbl{position:absolute;top:-21px;left:50%;transform:translateX(-50%);
 font-size:.72rem;font-weight:600;white-space:nowrap;opacity:0;transition:opacity .15s;pointer-events:none}
.nodo-dep:hover .lbl{opacity:1}
.nodo-dep .go{position:absolute;bottom:-16px;left:50%;transform:translateX(-50%);
 font-size:.62rem;color:#d4a259;white-space:nowrap;pointer-events:none}
.nodo-dep.activo{animation:pulso 1.4s ease-in-out infinite}
@keyframes pulso{0%,100%{box-shadow:0 0 0 0 rgba(212,162,89,.55)}50%{box-shadow:0 0 0 10px rgba(212,162,89,0)}}
.nodo-mic{border:none;cursor:pointer;background:#9db67c}
.nodo-mic .lbl{position:absolute;bottom:100%;left:50%;transform:translateX(-50%);
 font-size:.68rem;color:#e8e3d6;white-space:nowrap;opacity:0;pointer-events:none;margin-bottom:3px}
.nodo-mic:hover{z-index:3}
.nodo-mic:hover .lbl{opacity:1}
.linea-core{stroke:rgba(90,86,74,.32);stroke-width:1.1;transition:stroke .3s,stroke-width .3s}
.linea-core.activo{stroke:rgba(212,162,89,.75);stroke-width:2.2}
.linea-mic{stroke:rgba(157,182,124,.12)}
.hud{position:fixed;z-index:5;pointer-events:none}
#top{top:16px;left:20px;pointer-events:auto}
#top h1{color:#9db67c;font-size:1.02rem;letter-spacing:1px;font-weight:600}
#top .lk{margin-top:5px;font-size:.72rem;color:#5c584d;line-height:1.8}
#top .lk a{color:#8a8577;text-decoration:none;margin-right:11px}
#top .lk a:hover{color:#d4a259}
#salud{top:16px;right:20px;text-align:right;font-size:.7rem;color:#6e6a5e;line-height:1.65}
#salud b{color:#c2beb2;font-weight:600}
#guardia{bottom:14px;left:20px;font-size:.72rem;color:#6e6a5e}
#guardia b{color:#c46d5e}#guardia i{color:#9db67c;font-style:normal}
#hint{bottom:14px;right:20px;font-size:.68rem;color:#4d4a40;text-align:right}
/* panel de ejecucion */
#panel{position:fixed;z-index:9;top:0;right:0;height:100%;width:360px;max-width:88vw;
 background:#0d0b09f2;border-left:1px solid #2a2820;padding:22px 22px 26px;
 transform:translateX(100%);transition:transform .22s ease;overflow-y:auto;
 backdrop-filter:blur(3px)}
#panel.open{transform:translateX(0)}
#panel.wide{width:min(94vw,960px)}
#panel .embed{width:100%;height:56vh;border:1px solid #2a2820;border-radius:8px;background:#0a0908;margin-top:6px}
#panel .x{position:absolute;top:12px;right:16px;color:#6e6a5e;cursor:pointer;font-size:1.1rem}
#panel .x:hover{color:#d98c7e}
#panel h2{font-size:.95rem;letter-spacing:.5px;margin-bottom:2px}
#panel .cap{font-size:.68rem;color:#6e6a5e;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px}
#panel label{display:block;font-size:.66rem;text-transform:uppercase;letter-spacing:.7px;
 color:#8a8577;margin:14px 0 5px}
#panel select,#panel textarea{width:100%;background:#15130e;border:1px solid #2f2c22;
 color:#d3cfc2;border-radius:8px;padding:9px 11px;font-family:inherit;font-size:.82rem}
#panel textarea{min-height:90px;resize:vertical;line-height:1.5}
#panel .row{display:flex;gap:9px}#panel .row>*{flex:1}
#panel button.go{margin-top:16px;width:100%;background:#1a2418;border:1px solid #39432c;
 color:#9db67c;padding:11px;border-radius:8px;font-family:inherit;font-size:.84rem;
 cursor:pointer;letter-spacing:.5px}
#panel button.go:hover{background:#22301f;color:#b6cf92}
#panel button.go:disabled{opacity:.5;cursor:wait}
#panel .jobs{margin-top:22px;border-top:1px solid #211f18;padding-top:14px}
#panel .jobs h3{font-size:.62rem;text-transform:uppercase;letter-spacing:1px;color:#6e6a5e;margin-bottom:9px}
#panel .jb{font-size:.74rem;padding:6px 0;border-bottom:1px solid #17150f;display:flex;gap:7px;align-items:baseline}
#panel .jb .d{width:7px;height:7px;border-radius:50%;flex:none;margin-top:4px}
#panel .jb .t{color:#c3bfb2;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1}
#panel .jb small{color:#5f5b50}
#panel .vivo{max-height:220px;overflow-y:auto;background:#0a0908;border:1px solid #211f18;
 border-radius:8px;padding:8px 10px;font-size:.74rem;line-height:1.6}
#panel .vl{padding:2px 0;color:#8a8577;border-bottom:1px solid #14120d}
#panel .vl:last-child{border-bottom:none}
#panel .vl.ev-real{color:#d3cfc2}
#panel .vl.ev-error{color:#d98c7e}
#panel .vl.ev-paso{color:#5f5b50;font-style:italic}
#panel .vl.ev-nojob{opacity:.55;border-left:2px solid #6d5e8a;padding-left:6px}
#toast{position:fixed;z-index:12;bottom:26px;left:50%;transform:translateX(-50%) translateY(30px);
 background:#12100c;border:1px solid #2f2c22;color:#d3cfc2;padding:10px 18px;border-radius:9px;
 font-size:.8rem;opacity:0;transition:.25s;pointer-events:none}
#toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
/* visor de pieza */
#modal{position:fixed;z-index:14;inset:0;background:#05040399;display:none;padding:5vh 4vw}
#modal.open{display:block}
#modal .box{max-width:820px;margin:0 auto;background:#0d0b09;border:1px solid #2a2820;
 border-radius:12px;height:90vh;overflow-y:auto;padding:26px 30px}
#modal .box pre{white-space:pre-wrap;line-height:1.55;font-size:.82rem;color:#c3bfb2}
#modal .cerrar{color:#6e6a5e;cursor:pointer;float:right}#modal .cerrar:hover{color:#d98c7e}
</style></head><body>
<svg id="circuitos"></svg>
<div id="nodos"></div>
<div class="hud" id="top">
 <h1>&#129744; MAK &mdash; la cara del organismo</h1>
 <div class="lk"><a href="/doctrina" title="doctrina">📜 doctrina</a><a href="/reflexiones" title="reflexiones">💭 reflexiones</a>
 <a href="/cuotas" title="cuotas">📊 cuotas</a><a href="/relevo" title="relevo">🪑 relevo</a><a href="/genesis" title="génesis">✴️ génesis</a></div>
</div>
<div class="hud" id="salud">cuerpo…</div>
<div class="hud" id="guardia"></div>
<div class="hud" id="hint">click o teclas <b style="color:#8a8577">r c l p x</b> &rarr; departamento (editor real embebido) · click en pieza &rarr; abrir</div>
<div id="panel">
 <span class="x" onclick="cerrarPanel()">&times;</span>
 <h2 id="p-nom">·</h2><div class="cap" id="p-cap">departamento</div>
 <div id="p-run"></div>
 <div class="jobs" id="p-jobs"></div>
</div>
<div id="toast"></div>
<div id="modal" onclick="if(event.target===this)cerrarModal()">
 <div class="box"><span class="cerrar" onclick="cerrarModal()">cerrar &times;</span>
 <pre id="modal-txt">…</pre></div>
</div>
<script>
var DEPTOS=[
 {key:'research',label:'research',icon:'🔬',color:'#9db67c',port:8890,run:true},
 {key:'codex',label:'codex',icon:'💻',color:'#7ba6a3',port:8891,run:true},
 {key:'lenguaje',label:'lenguaje',icon:'🔤',color:'#c98f6a',run:false},
 {key:'plataforma',label:'plataforma',icon:'⚙️',color:'#8a8577',run:false},
 {key:'xio',label:'xio',icon:'📱',color:'#7f9bb3',run:false}
];
var DIR2DEP={informes:'research',paneles:'research',cadenas:'research',refutaciones:'research',
 correlaciones:'research',grafos:'research',memoria:'research',piezas:'codex',revisiones:'codex'};

var W=0,H=0,core={x:0,y:0},nodes=[],byId={},mic=[],edges=[];
var ORG=null, running={};
var svgNS='http://www.w3.org/2000/svg';
var svg=document.getElementById('circuitos'), nodosEl=document.getElementById('nodos');
var domCore=null, lineasCore={}, gMic=null;

function resize(){W=window.innerWidth;H=window.innerHeight;
 svg.setAttribute('viewBox','0 0 '+W+' '+H);svg.setAttribute('width',W);svg.setAttribute('height',H);}
window.addEventListener('resize',function(){resize();layout();});

function layout(){
 core.x=W/2; core.y=H/2;
 var R=Math.min(W,H)*0.30, n=DEPTOS.length;
 nodes.forEach(function(nd,i){
   var a=-Math.PI/2 + i*2*Math.PI/n;
   nd.tx=core.x+R*Math.cos(a); nd.ty=core.y+R*Math.sin(a);
   if(nd.x==null){nd.x=nd.tx;nd.y=nd.ty;}
 });
 var depByKey={}; nodes.forEach(function(nd){depByKey[nd.d.key]=nd;});
 window._depByKey=depByKey;
}

// ── elementos reales del DOM/SVG (creados UNA vez; nunca redibujados a mano) ──
function crearEstatico(){
 domCore=document.createElement('div');
 domCore.className='nodo nodo-core'; domCore.textContent='🍄';
 nodosEl.appendChild(domCore);
 nodes=DEPTOS.map(function(d){
   var l=document.createElementNS(svgNS,'line'); l.setAttribute('class','linea-core');
   svg.appendChild(l);
   var el=document.createElement('div');
   el.className='nodo nodo-dep'; el.style.borderColor=d.color;
   el.innerHTML='<span>'+d.icon+'</span>'+
     '<span class="lbl" style="color:'+d.color+'">'+esc(d.label)+'</span>'+
     (d.run?'<span class="go">▷ editor</span>':'');
   el.onclick=(function(dep){return function(){abrirDepto(dep);};})(d);
   nodosEl.appendChild(el);
   return {d:d, el:el, linea:l, x:null,y:null,vx:0,vy:0};
 });
 gMic=document.createElementNS(svgNS,'g'); svg.appendChild(gMic);
}

function setMic(g){
 var depByKey=window._depByKey||{};
 var prev={}; mic.forEach(function(m){prev[m.id]=m;});
 mic.forEach(function(m){if(m.el&&m.el.parentNode)m.el.parentNode.removeChild(m.el);});
 while(gMic.firstChild)gMic.removeChild(gMic.firstChild);
 byId={};
 mic=(g.nodes||[]).slice(0,70).map(function(nn){
   var dep=DIR2DEP[nn.dir]||'research';
   var anc=depByKey[dep]||{x:core.x,y:core.y};
   var p=prev[nn.id];
   var r=3+Math.min(nn.chunks||1,22)*0.42;
   var d=DEPTOS.find(function(x){return x.key===dep;})||DEPTOS[0];
   var el=document.createElement('div');
   el.className='nodo nodo-mic';
   el.style.width=el.style.height=(r*2)+'px';
   el.style.background=d.color;
   el.innerHTML='<span class="lbl">'+esc((nn.titulo||nn.id||'').slice(0,42))+'</span>';
   var m={id:nn.id,dir:nn.dir,dep:dep,titulo:nn.titulo||nn.id,chunks:nn.chunks||1,r:r,el:el,
     x:p?p.x:anc.x+(Math.random()*80-40), y:p?p.y:anc.y+(Math.random()*80-40), vx:0,vy:0};
   el.onclick=(function(mm){return function(){abrirPieza(mm);};})(m);
   nodosEl.appendChild(el);
   byId[m.id]=m; return m;
 });
 edges=(g.edges||[]).filter(function(e){return byId[e.a]&&byId[e.b];}).map(function(e){
   var l=document.createElementNS(svgNS,'line'); l.setAttribute('class','linea-mic'); gMic.appendChild(l);
   return {a:e.a,b:e.b,w:e.w,el:l};
 });
}

function step(){
 var depByKey=window._depByKey||{};
 for(var i=0;i<mic.length;i++){var m=mic[i];
   for(var j=i+1;j<mic.length;j++){var o=mic[j];
     var dx=m.x-o.x,dy=m.y-o.y,d2=dx*dx+dy*dy+0.01;
     if(d2<9000){var f=140/d2;m.vx+=dx*f;m.vy+=dy*f;o.vx-=dx*f;o.vy-=dy*f;}}
   var anc=depByKey[m.dep]||core;
   m.vx+=(anc.x-m.x)*0.006; m.vy+=(anc.y-m.y)*0.006;
 }
 edges.forEach(function(e){var a=byId[e.a],b=byId[e.b];
   var dx=b.x-a.x,dy=b.y-a.y,dist=Math.sqrt(dx*dx+dy*dy)||1,tgt=46+(1-e.w)*90;
   var f=(dist-tgt)*0.008/dist;a.vx+=dx*f;a.vy+=dy*f;b.vx-=dx*f;b.vy-=dy*f;});
 // damping fuerte + tope de velocidad: sigue vivo (nunca frena del todo) pero
 // se asienta cerca de un equilibrio -- sin esto los puntos tiemblan sin
 // parar y un click real puede fallar (probado: Playwright reporta el
 // elemento "not stable" con el damping viejo de 0.86).
 mic.forEach(function(m){
   m.vx*=0.55; m.vy*=0.55;
   var sp=Math.hypot(m.vx,m.vy), max=0.6;
   if(sp>max){m.vx=m.vx/sp*max; m.vy=m.vy/sp*max;}
   m.x+=m.vx; m.y+=m.vy;
 });
 nodes.forEach(function(nd){nd.vx+=(nd.tx-nd.x)*0.02;nd.vy+=(nd.ty-nd.y)*0.02;
   nd.vx*=0.8;nd.vy*=0.8;nd.x+=nd.vx;nd.y+=nd.vy;});
}

function pintar(){
 if(domCore){domCore.style.left=core.x+'px';domCore.style.top=core.y+'px';
   domCore.style.borderColor=window.OFFLINE?'#d4a259':'#9db67c';}
 nodes.forEach(function(nd){
   nd.el.style.left=nd.x+'px'; nd.el.style.top=nd.y+'px';
   var act=!!running[nd.d.key];
   nd.el.classList.toggle('activo',act);
   nd.linea.setAttribute('x1',core.x); nd.linea.setAttribute('y1',core.y);
   nd.linea.setAttribute('x2',nd.x); nd.linea.setAttribute('y2',nd.y);
   nd.linea.classList.toggle('activo',act);
 });
 mic.forEach(function(m){m.el.style.left=m.x+'px'; m.el.style.top=m.y+'px';});
 edges.forEach(function(e){var a=byId[e.a],b=byId[e.b];
   e.el.setAttribute('x1',a.x); e.el.setAttribute('y1',a.y);
   e.el.setAttribute('x2',b.x); e.el.setAttribute('y2',b.y);
   e.el.setAttribute('stroke-width',0.5+e.w*1.3);
 });
}
function loop(){step();pintar();requestAnimationFrame(loop);}

// ── panel: para research/codex embebe el editor REAL (iframe); nada de formulario propio ──
var panelDep=null;
function abrirDepto(d){panelDep=d;
 document.getElementById('panel').classList.toggle('wide',!!d.run);
 document.getElementById('p-nom').textContent=(d.icon||'')+' '+d.label;
 document.getElementById('p-nom').style.color=d.color;
 document.getElementById('p-cap').textContent=d.run?'editor real, embebido':'solo lectura';
 var run=document.getElementById('p-run');
 if(d.run){
   run.innerHTML='<iframe class="embed" id="p-iframe"></iframe>';
   var ifr=document.getElementById('p-iframe');
   if(d.key==='research'){ifr.src='http://'+location.hostname+':8890/';}
   else if(d.key==='codex'){ifr.src='http://'+location.hostname+':8891/';}
 }else{
   run.innerHTML='<p style="color:#6e6a5e;font-size:.8rem;line-height:1.6;margin-top:8px">'+
     'Este nodo no tiene interfaz web propia todavía. Su actividad se refleja en el micelio y la salud.</p>';
 }
 pintarJobs(d.key);
 document.getElementById('panel').classList.add('open');
}
function cerrarPanel(){document.getElementById('panel').classList.remove('open','wide');panelDep=null;
 vivoDep=null;clearTimeout(vivoTimer);}
function pintarJobs(key){var box=document.getElementById('p-jobs');
 var evs=((ORG&&ORG.actividad&&ORG.actividad.eventos)||[]).filter(function(e){return e.depto===key;}).slice(0,8);
 var col={listo:'#9db67c',corriendo:'#d4a259','en cola':'#d4a259',BLOQUEADO:'#c46d5e',FALLO:'#8a5c52',PAUSADO:'#e0a458',abortado:'#8a8578'};
 var h='';
 if(evs.length)h='<h3>actividad reciente</h3>'+evs.map(function(e){
   return '<div class="jb"><span class="d" style="background:'+(col[e.estado]||'#6e6a5e')+'"></span>'+
     '<span class="t">'+esc(e.texto)+'</span><small>'+esc(e.t)+'</small></div>';}).join('');
 h+='<h3 style="margin-top:16px">en vivo (contenido real)</h3><div id="p-vivo" class="vivo"></div>';
 box.innerHTML=h;
 cargarVivo(key);
}
var vivoTimer=null, vivoDep=null;
function cargarVivo(depto){
 vivoDep=depto;
 fetch('/api/eventos?depto='+depto).then(function(r){return r.json();}).then(function(d){
   if(vivoDep!==depto)return;
   var el=document.getElementById('p-vivo'); if(!el)return;
   var evs=(d.eventos||[]).slice(-14);
   el.innerHTML=evs.map(function(e){
     var cls=e.tipo==='error'?'ev-error':(e.tipo==='llm_result'?'ev-real':'ev-paso');
     if(e.sin_job)cls+=' ev-nojob';
     var txt=e.resumen||e.detalle||e.contexto||e.estado||'';
     if(e.sin_job)txt+=' [sin job]';
     return '<div class="vl '+cls+'">'+esc(txt)+'</div>';
   }).join('') || '<div class="vl ev-paso">sin eventos aun</div>';
   el.scrollTop=el.scrollHeight;
 }).catch(function(){});
 clearTimeout(vivoTimer);
 vivoTimer=setTimeout(function(){if(vivoDep===depto)cargarVivo(depto);},2000);
}
function toast(m){var t=document.getElementById('toast');t.textContent=m;t.classList.add('show');
 clearTimeout(window._tt);window._tt=setTimeout(function(){t.classList.remove('show');},2600);}

// ── visor de pieza ──
function abrirPieza(m){var mo=document.getElementById('modal');
 document.getElementById('modal-txt').textContent='cargando…';mo.classList.add('open');
 fetch('/pieza?dir='+encodeURIComponent(m.dir)+'&id='+encodeURIComponent(m.id))
  .then(function(r){return r.text();}).then(function(t){document.getElementById('modal-txt').textContent=t;})
  .catch(function(){document.getElementById('modal-txt').textContent='(no se pudo abrir)';});
}
function cerrarModal(){document.getElementById('modal').classList.remove('open');}
document.addEventListener('keydown',function(e){
 if(e.key==='Escape'){cerrarModal();cerrarPanel();return;}
 var tag=(e.target.tagName||'').toLowerCase();
 if(tag==='textarea'||tag==='select'||tag==='input'||tag==='iframe')return;
 var map={r:'research',c:'codex',l:'lenguaje',p:'plataforma',x:'xio'};
 var k=map[(e.key||'').toLowerCase()];
 if(k){var dd=DEPTOS.find(function(z){return z.key===k;});if(dd)abrirDepto(dd);}
});

// ── datos ──
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;');}
function cargar(){
 fetch('/api/organismo').then(function(r){return r.json();}).then(function(d){
   ORG=d; running={};
   ((d.actividad&&d.actividad.eventos)||[]).forEach(function(e){
     if(e.estado==='corriendo'||e.estado==='en cola')running[e.depto]=true;});
   var s=d.salud||{},sv=s.servicios||{};
   var net=d.internet||{}, tr=d.trabajo||{};
   window.OFFLINE = net.up===false;
   var netstr = net.up===false
     ? '<span style="color:#d98c7e">○ internet caído'+(net.caido_hace_s?(' '+Math.floor(net.caido_hace_s/60)+'min · en local'):'')+'</span>'
     : '<span style="color:#8a8577">● internet</span>';
   document.getElementById('salud').innerHTML=
     'load <b>'+((s.load||[])[0]||'?')+'</b> · mem <b>'+(s.mem_disponible_mb||0)+'</b>MB · '+
     'disco <b>'+(s.disco_libre_gb||0)+'</b>GB<br>'+
     Object.keys(sv).map(function(k){return (sv[k]&&sv[k].vivo?'●':'○')+' '+k;}).join('  ')+'<br>'+
     netstr+' · <span style="color:#8a8577">autónomo '+(tr.hoy||0)+'/'+(tr.max||24)+' hoy</span>';
   var g=(d.actividad&&d.actividad.guardia)||{};
   document.getElementById('guardia').innerHTML='guardia · <b>'+(g.bloqueados||0)+'</b> bloqueados · <i>'+(g.pasaron||0)+'</i> pasaron';
   if(panelDep)pintarJobs(panelDep.key);
 }).catch(function(){});
}
function cargarMic(){fetch('/api/micelio').then(function(r){return r.json();}).then(function(g){
   if(g&&g.nodes)setMic(g);}).catch(function(){});}

resize(); crearEstatico(); layout();
cargar();cargarMic();
setInterval(cargar,5000);setInterval(cargarMic,20000);
requestAnimationFrame(loop);
// deep-link de diagnostico: /?abrir=research abre el panel sin click
(function(){var a=new URLSearchParams(location.search).get('abrir');
 if(a){var dd=DEPTOS.find(function(x){return x.key===a;});
   if(dd)setTimeout(function(){abrirDepto(dd);},500);}})();
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
            "t": j.get("t", ""), "seg": round(j.get("ms", 0) / 1000) or "", "rz": rz[:200]}


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
    evs.sort(key=lambda e: e["t"], reverse=True)
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
            return self._json(_organismo())
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
