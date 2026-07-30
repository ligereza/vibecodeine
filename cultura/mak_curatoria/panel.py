#!/usr/bin/env python3
"""Panel web de curatoria MAK (puerto 8901). Muestra procesos ACTIVOS
reales (percepcion, blender, runner, ollama) + estado + reporte.
Refresco automatico cada 20s. Solo lectura, LAN."""
import json
import subprocess
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

BASE = Path.home() / "curatoria"


def procesos() -> list[tuple[str, str]]:
    filas = []
    for nombre, patron in [
        ("percepcion (curatoria)", "percepcion.py correr"),
        ("blender (render)", "blender -b"),
        ("runner GitHub", "Runner.Listener"),
        ("ollama (vision)", "llama-server"),
        ("extraccion DB", "extraccion_db.py"),
    ]:
        r = subprocess.run(["pgrep", "-f", patron], capture_output=True, text=True)
        pids = [p for p in r.stdout.split() if p.strip()]
        filas.append((nombre, f"ACTIVO pid {pids[0]}" if pids else "inactivo"))
    return filas


def gpu() -> str:
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
             "--format=csv,noheader"], capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except Exception:
        return "n/d"


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        estado = {}
        try:
            estado = json.loads((BASE / "estado.json").read_text())
        except Exception:
            pass
        reporte = ""
        try:
            reporte = (BASE / "reportes" / "REPORTE_CURATORIA.md").read_text()
        except Exception:
            pass
        def barra(pct: float, texto: str) -> str:
            pct = max(0.0, min(100.0, pct))
            return (f"<div class='bar'><div class='fill' style='width:{pct:.1f}%'></div>"
                    f"<span>{texto} — {pct:.1f}%</span></div>")

        tot = estado.get("total_trabajo") or 0
        proc = estado.get("procesados") or 0
        fu = estado.get("por_fuente") or {}
        barras = ""
        if tot:
            barras += barra(100 * proc / tot, f"percepcion total {proc}/{tot}")
            barras += barra(100 * min(fu.get('rd', 0), 1731) / 1731, f"rd {fu.get('rd', 0)}/1731")
            barras += barra(100 * fu.get('ig', 0) / 1401, f"ig {fu.get('ig', 0)}/1401")
        try:
            util = int(gpu().split('%')[0].strip())
            barras += barra(util, "gpu util")
        except Exception:
            pass
        filas = "".join(
            f"<tr><td>{n}</td><td class='{ 'on' if 'ACTIVO' in s else 'off'}'>{s}</td></tr>"
            for n, s in procesos())
        html = f"""<html><head><meta charset='utf-8'>
<meta http-equiv='refresh' content='20'><title>CURATORIA MAK</title><style>
body{{background:#0a0f0a;color:#cde;font-family:monospace;padding:24px}}
h1{{color:#0f6;letter-spacing:.2em}} table{{border-collapse:collapse;margin:12px 0}}
td{{border:1px solid #1f3;padding:6px 14px}} .on{{color:#0f6}} .off{{color:#666}}
pre{{background:#050805;padding:14px;border:1px solid #143;white-space:pre-wrap}}
small{{color:#586}}
.bar{{position:relative;background:#0d180d;border:1px solid #1f3;height:26px;margin:6px 0;max-width:640px}}
.fill{{background:linear-gradient(90deg,#0a4,#0f6);height:100%}}
.bar span{{position:absolute;inset:0;display:flex;align-items:center;padding-left:10px;font-size:13px;color:#dfe}}</style></head><body>
<h1>CURATORIA MAK</h1>
<small>{time.strftime('%Y-%m-%d %H:%M:%S')} — refresco 20s — gpu: {gpu()}</small>
<h3>progreso</h3>{barras}
<h3>procesos activos</h3><table>{filas}</table>
<h3>estado percepcion</h3>
<pre>{json.dumps({k: estado.get(k) for k in ('procesados','total_trabajo','por_fuente','errores_totales','errores_seguidos','pausado_por')}, ensure_ascii=False, indent=1)}</pre>
<h3>ultimo reporte</h3><pre>{reporte[:4000]}</pre>
</body></html>"""
        cuerpo = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8901), H).serve_forever()
