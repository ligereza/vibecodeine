"""Foreground contract tests for the MAK 8900 diagnostic surface."""

import json
import sys
import threading
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cultura" / "mak_plataforma"))

import hub  # noqa: E402


def _read_json(request):
    with urllib.request.urlopen(request, timeout=3) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def test_hub_contains_diagnostic_panel_and_routes():
    assert 'data-dep="diagnostics"' in hub.PAGINA
    assert 'id="pan-diagnostics"' in hub.PAGINA
    assert "generarDiagnostico" in hub.PAGINA
    assert "/api/diagnostics" in hub.PAGINA


def test_hub_diagnostic_get_and_post_are_read_only_contracts():
    server = hub.Servidor(("127.0.0.1", 0), hub.H)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = "http://127.0.0.1:%d" % server.server_address[1]
    try:
        query = urllib.parse.urlencode({
            "area": "research",
            "idea": "scraping de manuales para una propuesta",
        })
        status, get_payload = _read_json(
            urllib.request.Request(base + "/api/diagnostics?" + query))
        assert status == 200
        assert get_payload["ok"] is True
        assert get_payload["report"]["area"] == "research"

        body = json.dumps({
            "area": "cultura",
            "idea": "obra 3D con plantas",
            "error": "Authorization: Bearer topsecret user@example.com",
            "command": "python tool.py --token=secret",
        }).encode("utf-8")
        status, post_payload = _read_json(urllib.request.Request(
            base + "/api/diagnostics", data=body,
            headers={"Content-Type": "application/json"}, method="POST"))
        assert status == 200
        assert post_payload["ok"] is True
        assert post_payload["report"]["area"] == "cultura"
        assert "topsecret" not in post_payload["markdown"]
        assert "user@example.com" not in post_payload["markdown"]
        assert post_payload["report"]["safety"]["read_only"] is True
        assert post_payload["report"]["safety"]["raw_win_read"] is False
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
