import json
import threading
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from cultura.mak_plataforma import hub


def test_hub_jsonl_writer_flushes_and_syncs(tmp_path, monkeypatch):
    path = tmp_path / "nested" / "decision.jsonl"
    synced = []
    monkeypatch.setattr(hub.os, "fsync", lambda fd: synced.append(fd))

    hub._portfolio_append_jsonl(str(path), {"schema": "probe", "ok": True})

    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert rows == [{"schema": "probe", "ok": True}]
    assert len(synced) == 1


def test_service_proxy_keeps_fixed_internal_targets():
    assert hub._service_proxy_target(
        "research", "/research/api/jobs", "limit=2") == (
            "http://127.0.0.1:8890/api/jobs?limit=2")
    assert hub._service_proxy_target("codex", "/codex/run") == (
        "http://127.0.0.1:8891/run")


def test_service_html_rewrites_fetch_calls_into_same_origin():
    page = b"<html><head></head><body><script>fetch('/api/jobs')</script></body></html>"
    rewritten = hub._rewrite_service_html(page, "research").decode("utf-8")
    assert "var p='/research'" in rewritten
    assert rewritten.count("var p='/research'") == 1


def test_hub_tabs_use_same_origin_service_paths():
    assert "research:'/research/'" in hub.PAGINA
    assert "codex:'/codex/'" in hub.PAGINA
    assert "location.hostname+':8890'" not in hub.PAGINA
    assert "location.hostname+':8891'" not in hub.PAGINA


def test_service_entrypoints_default_to_loopback():
    research = (Path(__file__).resolve().parents[1] /
                "cultura" / "mak_research" / "interfaz.py").read_text(
                    encoding="utf-8")
    codex = (Path(__file__).resolve().parents[1] /
             "cultura" / "mak_codex" / "interfaz_codex.py").read_text(
                 encoding="utf-8")
    assert 'os.environ.get("MAK_SERVICE_HOST", "127.0.0.1")' in research
    assert 'os.environ.get("MAK_SERVICE_HOST", "127.0.0.1")' in codex
    assert '(BIND_HOST, PORT)' in research
    assert '(BIND_HOST, PORT)' in codex


def test_service_proxy_forwards_html_and_post_contract(monkeypatch):
    class UpstreamHandler(BaseHTTPRequestHandler):
        post_body = b""
        head_count = 0

        def do_GET(self):
            body = b"<html><head></head><body>research</body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            length = int(self.headers.get("Content-Length") or 0)
            type(self).post_body = self.rfile.read(length)
            body = b'{"ok":true}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_HEAD(self):
            type(self).head_count += 1
            body = b"head"
            self.send_response(204)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()

        def log_message(self, *_args):
            return

    upstream = ThreadingHTTPServer(("127.0.0.1", 0), UpstreamHandler)
    hub_server = hub.Servidor(("127.0.0.1", 0), hub.H)
    upstream_thread = threading.Thread(target=upstream.serve_forever)
    hub_thread = threading.Thread(target=hub_server.serve_forever)
    upstream_thread.start()
    hub_thread.start()
    monkeypatch.setattr(
        hub, "SERVICE_PROXY_PREFIXES",
        {"research": "http://127.0.0.1:%d" % upstream.server_port,
         "codex": "http://127.0.0.1:%d" % upstream.server_port})
    try:
        root = "http://127.0.0.1:%d" % hub_server.server_port
        with urllib.request.urlopen(root + "/research/", timeout=3) as response:
            html = response.read().decode("utf-8")
        assert "var p='/research'" in html

        head_request = urllib.request.Request(
            root + "/research/api/jobs", method="HEAD")
        with urllib.request.urlopen(head_request, timeout=3) as response:
            assert response.status == 204
            assert response.read() == b""
        assert UpstreamHandler.head_count == 1

        payload = urllib.parse.urlencode({"pedido": "probe"}).encode("utf-8")
        request = urllib.request.Request(
            root + "/codex/run", data=payload, method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(request, timeout=3) as response:
            assert response.read() == b'{"ok":true}'
        assert UpstreamHandler.post_body == payload
    finally:
        hub_server.shutdown()
        upstream.shutdown()
        hub_thread.join(timeout=3)
        upstream_thread.join(timeout=3)
        hub_server.server_close()
        upstream.server_close()
