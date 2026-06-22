"""Servidor para el workspace HTML del hub (flujo_hub.html + visualizadores).

Este es el paso de "HTMLs estáticos" a una aplicación real lanzable.

Características:
- Sirve los archivos de context/ como frontend pro.
- API básica para integrar lógica real de Python (parser, brand, etc.).
- Soporte para --desktop con pywebview (ventana nativa, gratis con BSD license).
- Se lanza con `flujo app` o `flujo serve`.

Todo es gratis y local. pywebview usa WebView2 de Windows (gratis).

Uso:
    flujo app
    flujo app --desktop   # ventana tipo app
"""

from __future__ import annotations

import json
import os
import sys
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread
import time
from urllib.parse import urlparse, parse_qs

from ..paths import context_dir, repo_root
from ..brand import load_styles
from ..intake.email_parser import parse_pedido_text  # usa el parser real si existe


class HubRequestHandler(BaseHTTPRequestHandler):
    """Sirve estáticos + API ligera para hacer que el hub sea una app real."""

    def __init__(self, *args, **kwargs):
        self.context_path = context_dir()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/hub", "/index.html"):
            path = "/flujo_hub.html"
        elif path == "/visualizer":
            path = "/svg_visualizer.html"
        elif path == "/plano":
            path = "/plano_demo.html"

        # API endpoints
        if path == "/api/brand":
            self._send_json(load_styles())
            return
        if path == "/api/ping":
            self._send_json({"status": "ok", "workspace": "flujo"})
            return

        # Servir archivos estáticos
        file_path = self.context_path / path.lstrip("/")
        if file_path.is_file():
            self._serve_file(file_path)
        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/parse-pedido":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
                text = data.get("text", "")
                # Usa parser real si disponible, sino fallback simple
                try:
                    result = parse_pedido_text(text)
                except Exception:
                    result = self._simple_parse(text)
                self._send_json(result)
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        self.send_error(404)

    def _serve_file(self, file_path: Path):
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            if file_path.suffix == ".html":
                self.send_header("Content-type", "text/html")
            elif file_path.suffix == ".js":
                self.send_header("Content-type", "application/javascript")
            elif file_path.suffix == ".css":
                self.send_header("Content-type", "text/css")
            elif file_path.suffix == ".svg":
                self.send_header("Content-type", "image/svg+xml")
            else:
                self.send_header("Content-type", "application/octet-stream")
            self.end_headers()
            self.wfile.write(content)
        except Exception:
            self.send_error(500)

    def _send_json(self, data: dict, status: int = 200):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _simple_parse(self, text: str) -> dict:
        """Fallback simple si el parser real no está disponible."""
        low = text.lower()
        tipo = "desconocido"
        if "flyer" in low:
            tipo = "flyer"
        elif "etiqueta" in low:
            tipo = "etiqueta"
        elif "plano" in low or "stand" in low:
            tipo = "plano"
        return {
            "tipo": tipo,
            "voluntarios": 7,
            "medidas": "por definir",
            "sugerencia": "Usar formato existente o crear en projects/flujo/",
            "nota": "Parser simplificado - backend real disponible vía API"
        }

    def log_message(self, format, *args):
        if os.environ.get("FLUJO_WEB_DEBUG"):
            super().log_message(format, *args)


def run_server(host: str = "127.0.0.1", port: int = 8765):
    os.chdir(context_dir())
    server = HTTPServer((host, port), HubRequestHandler)
    print(f"[flujo] Workspace app en http://{host}:{port}")
    print("  - Hub:      /flujo_hub.html")
    print("  - SVG Viz:  /svg_visualizer.html")
    print("  - Plano:    /plano_demo.html")
    print("  - API:      /api/brand , /api/parse-pedido (POST)")
    server.serve_forever()


def launch(
    host: str = "127.0.0.1",
    port: int = 8765,
    desktop: bool = False,
    open_browser: bool = True,
):
    thread = Thread(target=run_server, args=(host, port), daemon=True)
    thread.start()

    url = f"http://{host}:{port}/flujo_hub.html"

    if desktop:
        try:
            import webview
            webview.create_window(
                "flujo • Workspace",
                url,
                width=1400,
                height=900,
                resizable=True,
                min_size=(1000, 700),
            )
            webview.start()
            return
        except ImportError:
            print("[flujo] pywebview no instalado → usando navegador.")
            print("        pip install pywebview   (gratis, BSD)")

    if open_browser:
        time.sleep(0.7)
        webbrowser.open(url)
        print(f"[flujo] Abierto: {url}")
        print("        (Ctrl+C para cerrar)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[flujo] App detenida.")


if __name__ == "__main__":
    launch()
