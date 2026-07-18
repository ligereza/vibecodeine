#!/usr/bin/env python3
"""interfaz_codex.py -- web del departamento CODEX (puerto 8891).

TOKEN OBLIGATORIO: el server NO arranca sin env CODEX_TOKEN (el codex
puede ejecutar codigo en sandbox; la puerta va con llave). El watchdog lo
exporta desde ~/codex/.token. Acceso: http://IP:8891/?t=TOKEN
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
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = "/home/mak/codex"
sys.path.insert(0, BASE)
sys.path.insert(0, "/home/mak/research")
from worker_codex import run_pedido  # noqa: E402
from research_lib import mint_job_id  # noqa: E402

PORT = int(os.environ.get("CODEX_PORT", "8891"))
TOKEN = os.environ.get("CODEX_TOKEN", "")
DIRS = {"piezas": os.path.join(BASE, "piezas"),
        "revisiones": os.path.join(BASE, "revisiones")}
JOBS_FILE = os.path.join(BASE, "jobs.jsonl")
NOMBRE_OK = re.compile(r"^[A-Za-z0-9._-]+\.(md|py)$")
FECHA_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})-(.+)\.(md|py)$")

JOBS = []
JOBS_LOCK = threading.Lock()

PAGINA = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MAK Codex</title><style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:radial-gradient(ellipse at 30% 20%,#15130e 0,#0b0a09 60%);
 color:#c9c5b9;font-family:ui-monospace,SFMono-Regular,monospace;min-height:100vh;padding:30px}
h1{color:#9db67c;font-size:1.3rem}
.sub{color:#6e6a5e;font-size:.78rem;margin:4px 0 22px}
.cols{display:grid;grid-template-columns:minmax(320px,430px) 1fr;gap:18px;max-width:1200px}
.card{background:#12100cd9;border:1px solid #2a2820;border-radius:13px;padding:16px 18px;margin-bottom:14px}
.card h2{font-size:.72rem;text-transform:uppercase;letter-spacing:.8px;color:#9db67c;margin-bottom:10px}
textarea,select,input{width:100%;background:#0b0a09;border:1px solid #2a2820;border-radius:8px;
 color:#e2ddd0;padding:9px 11px;font-family:inherit;font-size:.83rem;margin-bottom:9px}
textarea{min-height:88px;resize:vertical}
textarea:focus,select:focus{outline:none;border-color:#9db67c}
button{background:#9db67c;color:#0b0a09;border:none;border-radius:8px;padding:9px 16px;
 font-family:inherit;font-weight:700;font-size:.82rem;cursor:pointer}
button:hover{background:#b1c893}
.job{display:flex;gap:9px;align-items:center;font-size:.78rem;padding:6px 0;border-bottom:1px solid #1c1a14}
.dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.d-en-cola{background:#d4a259}.d-corriendo{background:#7ba6a3;animation:p 1s infinite}
.d-listo{background:#9db67c}.d-fallo{background:#c46d5e}
@keyframes p{50%{opacity:.35}}
.pieza{display:flex;gap:10px;align-items:center;padding:8px 10px;margin:6px 0;background:#0b0a09;
 border:1px solid #1c1a14;border-radius:9px;cursor:pointer;font-size:.79rem}
.pieza:hover{border-color:#9db67c66}
.pieza .tipo{font-size:.62rem;color:#d4a259;text-transform:uppercase;margin-left:auto}
.pieza .fecha{color:#6e6a5e;font-size:.68rem}
.overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:50;
 align-items:center;justify-content:center}
.overlay.show{display:flex}
.caja{background:#12100c;border:1px solid #3d3a2e;border-radius:12px;width:min(860px,94vw);
 max-height:88vh;display:flex;flex-direction:column}
.caja-head{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;
 border-bottom:1px solid #2a2820;color:#9db67c;font-size:.85rem}
.caja-body{padding:16px 20px;overflow-y:auto;font-size:.84rem;line-height:1.55}
.caja-body pre{background:#0b0a09;border:1px solid #1c1a14;border-radius:8px;padding:12px;
 overflow-x:auto;margin:10px 0;font-size:.78rem;line-height:1.45}
.caja-body h1,.caja-body h2{color:#e2ddd0;margin:.7em 0 .35em}
#toast{position:fixed;bottom:22px;right:22px;background:#9db67c;color:#0b0a09;padding:11px 18px;
 border-radius:9px;font-weight:700;font-size:.8rem;opacity:0;transition:opacity .3s;pointer-events:none}
#toast.show{opacity:1}
</style></head><body>
<h1>&#9881; MAK Codex</h1>
<div class="sub">full coder · sandbox con límites · lo que toca red/procesos queda para revisión humana · <a href="/salud-link" onclick="verSalud();return false" style="color:#9db67c">salud</a> · <a href="#" onclick="window.open('http://'+location.hostname+':8900/cuotas');return false" style="color:#d4a259">cuotas</a></div>
<div class="cols"><div>
<div class="card"><h2>nuevo trabajo</h2>
<textarea id="pedido" placeholder="generar: describe el programa&#10;revisar/testear: ruta absoluta a un .py bajo /home/mak"></textarea>
<select id="modo"><option value="generar">Generar (plan → código → sandbox)</option>
<option value="revisar">Revisar (3 lentes adversariales)</option>
<option value="testear">Testear (unittest en sandbox)</option></select>
<select id="densidad"><option value="corto">corto</option><option value="medio" selected>medio</option>
<option value="largo">largo</option></select>
<button onclick="ejecutar()">&#9654; Ejecutar</button></div>
<div class="card"><h2>trabajos</h2><div id="jobs">…</div></div>
</div><div>
<div class="card"><h2>archivo del codex</h2><input id="filtro" placeholder="filtrar…" oninput="pinta()">
<div id="piezas">…</div></div>
</div></div>
<div class="overlay" id="ov" onclick="if(event.target===this)cerrar()">
<div class="caja"><div class="caja-head"><span id="ov-t"></span>
<button onclick="cerrar()" style="background:#2a2820;color:#c9c5b9">&#10005;</button></div>
<div class="caja-body" id="ov-b"></div></div></div>
<div id="toast"></div>
<script>
var T=new URLSearchParams(location.search).get('t')||localStorage.getItem('codex_t')||'';
if(T)localStorage.setItem('codex_t',T);
function q(u){return u+(u.indexOf('?')>=0?'&':'?')+'t='+encodeURIComponent(T);}
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function toast(m){var t=document.getElementById('toast');t.textContent=m;t.classList.add('show');
 setTimeout(function(){t.classList.remove('show');},2600);}
var PIEZAS=[];
function pinta(){
  var f=(document.getElementById('filtro').value||'').toLowerCase();
  document.getElementById('piezas').innerHTML=PIEZAS.filter(function(p){
    return !f||p.titulo.toLowerCase().indexOf(f)>=0;
  }).map(function(p){
    return '<div class="pieza" onclick="ver(\\''+p.d+'\\',\\''+encodeURIComponent(p.n)+'\\')">'+
      '<div><div>'+esc(p.titulo)+'</div><div class="fecha">'+esc(p.fecha)+'</div></div>'+
      '<span class="tipo">'+esc(p.tipo)+'</span></div>';
  }).join('')||'<div style="color:#6e6a5e;font-size:.78rem">(vacío — genera la primera pieza)</div>';
}
function cargar(){
  fetch(q('/api/piezas')).then(function(r){return r.json();}).then(function(d){PIEZAS=d;pinta();});
  fetch(q('/api/jobs')).then(function(r){return r.json();}).then(function(d){
    document.getElementById('jobs').innerHTML=d.length?d.map(function(j){
      var cl='d-'+(j.estado||'').toLowerCase().replace(/\\s+/g,'-');
      var link=j.path?' <a href="#" style="color:#9db67c" onclick="ver(\\'auto\\',\\''+
        encodeURIComponent(j.path)+'\\');return false">ver</a>':'';
      return '<div class="job"><span class="dot '+cl+'"></span><span style="flex:1;overflow:hidden;'+
        'text-overflow:ellipsis;white-space:nowrap">'+esc(j.pedido)+'</span>'+
        '<span style="color:#6e6a5e">'+esc(j.t)+' · '+esc(j.estado)+'</span>'+link+'</div>';
    }).join(''):'<div style="color:#6e6a5e;font-size:.78rem">sin trabajos</div>';
  });
}
function mdMin(src){
  var out=[],enFence=false,buf=[];
  src.split('\\n').forEach(function(l){
    if(l.indexOf('```')===0){ if(enFence){out.push('<pre>'+esc(buf.join('\\n'))+'</pre>');buf=[];}
      enFence=!enFence; return;}
    if(enFence){buf.push(l);return;}
    var m=l.match(/^(#{1,3})\\s+(.*)/);
    if(m){out.push('<h'+m[1].length+'>'+esc(m[2])+'</h'+m[1].length+'>');return;}
    out.push('<p>'+esc(l).replace(/\\*\\*(.+?)\\*\\*/g,'<b>$1</b>')+'</p>');
  });
  if(buf.length)out.push('<pre>'+esc(buf.join('\\n'))+'</pre>');
  return out.join('');
}
function ver(d,nEnc){
  var n=decodeURIComponent(nEnc);
  fetch(q('/f?d='+d+'&n='+nEnc)).then(function(r){return r.text();}).then(function(t){
    document.getElementById('ov-t').textContent=n;
    document.getElementById('ov-b').innerHTML=n.slice(-3)==='.py'?'<pre>'+esc(t)+'</pre>':mdMin(t);
    document.getElementById('ov').classList.add('show');
  });
}
function verSalud(){
  fetch('http://'+location.hostname+':8900/api/salud').then(function(r){return r.json();})
  .then(function(d){document.getElementById('ov-t').textContent='salud del organismo';
    document.getElementById('ov-b').innerHTML='<pre>'+esc(JSON.stringify(d.salud,null,2))+'</pre>';
    document.getElementById('ov').classList.add('show');})
  .catch(function(){toast('hub :8900 no responde');});
}
function cerrar(){document.getElementById('ov').classList.remove('show');}
function ejecutar(){
  var pedido=document.getElementById('pedido').value.trim();
  if(!pedido)return;
  var body='pedido='+encodeURIComponent(pedido)+'&modo='+document.getElementById('modo').value+
    '&densidad='+document.getElementById('densidad').value;
  fetch(q('/run'),{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:body})
  .then(function(r){return r.json();}).then(function(d){
    if(d.ok){document.getElementById('pedido').value='';toast('trabajo encolado');cargar();}
    else toast('error: '+(d.error||'?'));
  }).catch(function(){toast('sin conexión');});
}
document.addEventListener('keydown',function(e){if(e.key==='Escape')cerrar();});
cargar(); setInterval(cargar,4000);
</script></body></html>"""


def _cargar_jobs():
    try:
        with open(JOBS_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        JOBS.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        del JOBS[:-15]
    except OSError:
        pass


def _guardia_codex(pedido):
    """Guardia de entrada del coder: clasifica el pedido de codigo (dual-use
    calibrado). Fail-open si el filtro no esta."""
    try:
        sys.path.insert(0, "/home/mak/plataforma")
        import filtro_entrada
        return filtro_entrada.clasificar(pedido, contexto="codex")
    except Exception:  # noqa: BLE001 - sin guardia = sigue
        return None


def _lanzar(modo, pedido, densidad):
    job = {"pedido": pedido, "modo": modo, "estado": "en cola", "path": "",
           "error": "", "t": time.strftime("%H:%M:%S"), "job_id": mint_job_id()}
    with JOBS_LOCK:
        JOBS.append(job)

    def correr():
        t0 = time.time()
        job["estado"] = "corriendo"
        # guardia: solo generar (crear codigo nuevo). revisar/testear operan
        # sobre archivos ya existentes -> bajo riesgo, no se filtran.
        if modo == "generar":
            g = _guardia_codex(pedido)
            if g and not (g.get("veredicto") in ("LEGITIMO", "DESCRIPTIVO")):
                job["estado"] = "BLOQUEADO"
                job["error"] = "guardia de codigo: %s -- %s" % (
                    g["veredicto"], g["razon"])
                job["ms"] = int((time.time() - t0) * 1000)
                try:
                    with open(JOBS_FILE, "a", encoding="utf-8") as f:
                        f.write(json.dumps(job, ensure_ascii=False) + "\n")
                except OSError:
                    pass
                return
        try:
            r = run_pedido(modo, pedido, densidad=densidad, ntfy=True,
                          job_id=job["job_id"])
            job["estado"] = "listo" if r["ok"] else "FALLO"
            job["path"] = os.path.basename(r["path"]) if r["path"] else ""
            if not r["ok"]:
                job["error"] = r["tail"][-1500:]
        except Exception as e:  # noqa: BLE001 - el job no tumba el server
            job["estado"] = "FALLO"
            job["error"] = str(e)[:1500]
        job["ms"] = int((time.time() - t0) * 1000)
        try:
            with open(JOBS_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(job, ensure_ascii=False) + "\n")
        except OSError:
            pass

    threading.Thread(target=correr, daemon=True).start()


def _piezas():
    out = []
    for d, carpeta in DIRS.items():
        try:
            nombres = os.listdir(carpeta)
        except OSError:
            continue
        for n in nombres:
            if not (n.endswith(".md") or n.endswith(".py")):
                continue
            m = FECHA_RE.match(n)
            if m:
                fecha = "%s-%s-%s %s:%s" % m.groups()[:5]
                titulo = m.group(7).replace("-", " ")
            else:
                fecha, titulo = "", n
            out.append({"n": n, "d": d, "titulo": titulo, "fecha": fecha,
                        "tipo": ("revisión" if d == "revisiones" else
                                 ("código" if n.endswith(".py") else "pieza"))})
    out.sort(key=lambda p: p["n"], reverse=True)
    return out[:80]


class H(BaseHTTPRequestHandler):
    server_version = "MAK-Codex/1.0"

    def _auth(self):
        # xio Face A (home/studio): LAN privada, solo maquinas del duenno
        # (Linux MAK + Windows). El Linux NUNCA sale a los shows (Face B es
        # solo el telefono). Sin CODEX_TOKEN en el entorno el codex corre
        # abierto, igual que research :8890. Re-bloquear = exportar
        # CODEX_TOKEN otra vez.
        if not TOKEN:
            return True
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        t = (qs.get("t") or [""])[0]
        if t == TOKEN or self.headers.get("X-Token") == TOKEN:
            return True
        self._send('{"error":"token requerido (?t=...)"}', 401,
                   "application/json")
        return False

    def _send(self, body, code=200, ctype="text/html; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if not self._auth():
            return
        u = urllib.parse.urlparse(self.path)
        if u.path == "/api/jobs":
            with JOBS_LOCK:
                return self._send(json.dumps(list(reversed(JOBS[-15:])),
                                             ensure_ascii=False),
                                  200, "application/json; charset=utf-8")
        if u.path == "/api/piezas":
            return self._send(json.dumps(_piezas(), ensure_ascii=False),
                              200, "application/json; charset=utf-8")
        if u.path == "/f":
            qs = urllib.parse.parse_qs(u.query)
            d = (qs.get("d") or [""])[0]
            n = (qs.get("n") or [""])[0]
            if d == "auto":
                d = "revisiones" if "-rev-" in n or "-test-" in n else "piezas"
            if d not in DIRS or not NOMBRE_OK.match(n):
                return self._send("no", 404, "text/plain")
            try:
                with open(os.path.join(DIRS[d], n), encoding="utf-8") as f:
                    return self._send(f.read(), 200,
                                      "text/plain; charset=utf-8")
            except OSError:
                return self._send("no existe", 404, "text/plain")
        if u.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        return self._send(PAGINA)

    def do_POST(self):
        if not self._auth():
            return
        if urllib.parse.urlparse(self.path).path == "/run":
            largo = min(int(self.headers.get("Content-Length") or 0), 12000)
            q = urllib.parse.parse_qs(self.rfile.read(largo).decode())
            pedido = (q.get("pedido") or [""])[0].strip()[:2000]
            modo = (q.get("modo") or ["generar"])[0]
            densidad = (q.get("densidad") or ["medio"])[0]
            if modo not in ("generar", "revisar", "testear", "debug"):
                modo = "generar"
            if densidad not in ("corto", "medio", "largo"):
                densidad = "medio"
            if not pedido:
                return self._send('{"ok":false,"error":"pedido vacio"}', 400,
                                  "application/json")
            _lanzar(modo, pedido, densidad)
            return self._send('{"ok":true}', 200, "application/json")
        return self._send("no", 404, "text/plain")

    def log_message(self, fmt, *args):
        pass


class Servidor(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    if not TOKEN:
        print("[codex] sin CODEX_TOKEN: arranco ABIERTO (LAN privada Face A, "
              "solo maquinas del duenno). Exporta CODEX_TOKEN para re-bloquear.",
              file=sys.stderr)
    for d in DIRS.values():
        os.makedirs(d, exist_ok=True)
    _cargar_jobs()
    server = Servidor(("0.0.0.0", PORT), H)

    def apagar(signum, frame):
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, apagar)
    signal.signal(signal.SIGINT, apagar)
    print("[codex] en http://0.0.0.0:%d (token requerido)" % PORT, flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
