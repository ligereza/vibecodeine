#!/usr/bin/env python3
"""interfaz.py -- interfaz web LAN del research MAK (puerto 8890).

Formulario: tema X + modo (research/panel) + n. Encola el job (un solo
job a la vez, lock de worker.py) y lista los informes generados.
Solo LAN (red del equipo); sin auth: no exponer a internet.

    python3 interfaz.py   # http://192.168.50.2:8890
"""
import html
import json
import os
import re
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from research_lib import load_env
from worker import run_tema

PORT = int(os.environ.get("INTERFAZ_PORT", "8890"))
DIRS = {"informes": os.path.expanduser("~/research/informes"),
        "paneles": os.path.expanduser("~/research/paneles")}
JOBS = []  # historial en memoria: {tema, modo, estado, path, t}
JOBS_LOCK = threading.Lock()
NOMBRE_OK = re.compile(r"^[A-Za-z0-9._-]+\.(md|json)$")


def _lanzar(modo, tema, n):
    job = {"tema": tema, "modo": modo, "estado": "en cola",
           "path": "", "t": time.strftime("%H:%M:%S")}
    with JOBS_LOCK:
        JOBS.append(job)

    def correr():
        job["estado"] = "corriendo"
        r = run_tema(modo, tema, n=n, ntfy=True)
        job["estado"] = "listo" if r["ok"] else "FALLO"
        job["path"] = os.path.basename(r["path"]) if r["path"] else ""

    threading.Thread(target=correr, daemon=True).start()


def _listar(d):
    try:
        files = sorted(os.listdir(DIRS[d]), reverse=True)
    except OSError:
        files = []
    return [f for f in files if f.endswith(".md")][:15]


PAGINA = """<!doctype html><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MAK research</title>
<style>body{{background:#0b0a09;color:#d8d3c8;font-family:monospace;
max-width:720px;margin:2rem auto;padding:0 1rem}}
a{{color:#9db67c}}input,select,button{{background:#171512;color:#d8d3c8;
border:1px solid #3a362f;padding:.5rem;font-family:monospace}}
input[name=tema]{{width:100%}}button{{cursor:pointer;border-color:#9db67c}}
li{{margin:.2rem 0}}small{{color:#7a7468}}</style>
<h2>MAK research <small>4 APIs + ollama local</small></h2>
<form method="post" action="/run">
<p><input name="tema" placeholder="tema X..." required></p>
<p><select name="modo"><option value="research">research (loop iterativo)</option>
<option value="panel">panel (debate 4 modelos)</option></select>
n=<input name="n" value="" size="2" placeholder="def">
<button>investigar</button></p></form>
<h3>jobs</h3><ul>{jobs}</ul>
<h3>informes</h3><ul>{informes}</ul>
<h3>paneles</h3><ul>{paneles}</ul>"""


class H(BaseHTTPRequestHandler):
    def _html(self, body, code=200):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/f":
            q = urllib.parse.parse_qs(u.query)
            d = (q.get("d") or [""])[0]
            n = (q.get("n") or [""])[0]
            # basename estricto: sin path traversal
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
        with JOBS_LOCK:
            jobs = "".join(
                "<li>%s [%s] %s (%s) %s</li>" % (
                    j["t"], j["modo"], html.escape(j["tema"][:70]),
                    j["estado"],
                    ('<a href="/f?d=%s&n=%s">ver</a>' % (
                        "paneles" if j["modo"] == "panel" else "informes",
                        urllib.parse.quote(j["path"]))) if j["path"] else "")
                for j in reversed(JOBS[-15:])) or "<li>(ninguno)</li>"
        listas = {}
        for d in DIRS:
            listas[d] = "".join(
                '<li><a href="/f?d=%s&n=%s">%s</a></li>'
                % (d, urllib.parse.quote(f), html.escape(f))
                for f in _listar(d)) or "<li>(vacio)</li>"
        self._html(PAGINA.format(jobs=jobs, informes=listas["informes"],
                                 paneles=listas["paneles"]))

    def do_POST(self):
        if self.path != "/run":
            return self._html("no", 404)
        largo = min(int(self.headers.get("Content-Length") or 0), 10000)
        q = urllib.parse.parse_qs(self.rfile.read(largo).decode())
        tema = (q.get("tema") or [""])[0].strip()[:300]
        modo = (q.get("modo") or ["research"])[0]
        if modo not in ("research", "panel"):
            modo = "research"
        try:
            n = int((q.get("n") or [""])[0])
            n = max(0, min(n, 10))
        except ValueError:
            n = None
        if tema:
            _lanzar(modo, tema, n)
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def log_message(self, fmt, *args):  # silencio: cola.log ya basta
        pass


if __name__ == "__main__":
    load_env()
    for d in DIRS.values():
        os.makedirs(d, exist_ok=True)
    print("interfaz en http://0.0.0.0:%d" % PORT, flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
