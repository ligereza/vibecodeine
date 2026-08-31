#!/usr/bin/env python3
"""tests/test_hub_execution_routes.py -- POST /api/ejecutar and POST/GET
/api/render, neither of which had a witness anywhere in the suite (grep for
`_ejecutar`, `_render_estado`, `_guardar_config_render` and the two literal
paths across tests/*.py turns up nothing outside this file).

/api/ejecutar forwards a request to the research or codex service over a
real loopback HTTP call; no test service is running in this sandbox, so the
"successful dispatch" branch is out of reach here and only the three
in-process branches (empty text, unknown department, network failure) are
covered.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cultura", "mak_plataforma"))

import hub  # noqa: E402


class FakeHandler:
    def __init__(self, body=b""):
        self.rfile = io.BytesIO(body)
        self.headers = {"Content-Length": str(len(body))}
        self.calls = []

    def _json(self, obj, code=200):
        self.calls.append(("json", obj, code))

    @property
    def last(self):
        return self.calls[-1]


def _post_ejecutar(body):
    handler = FakeHandler(json.dumps(body).encode("utf-8"))
    handler.path = "/api/ejecutar"
    hub.H.do_POST(handler)
    _, payload, code = handler.last
    return payload, code


def _post_render(body):
    handler = FakeHandler(json.dumps(body).encode("utf-8"))
    handler.path = "/api/render"
    hub.H.do_POST(handler)
    _, payload, code = handler.last
    return payload, code


class TestEjecutarValidation:
    def test_empty_text_is_rejected_without_reaching_the_network(self):
        payload, code = _post_ejecutar({"depto": "research", "texto": "   "})

        assert code == 200
        assert payload == {"ok": False, "error": "texto vacio"}

    def test_unknown_department_is_rejected(self):
        payload, code = _post_ejecutar({"depto": "no-such-department", "texto": "hola"})

        assert code == 200
        assert payload == {"ok": False, "error": "departamento no ejecutable"}

    def test_unreachable_service_reports_the_error_instead_of_raising(self, monkeypatch):
        # Port 1 is privileged and unbound in a test sandbox: the connection
        # is refused immediately, exercising the network except-branch
        # without depending on a live research/codex service.
        monkeypatch.setattr(hub, "RESEARCH_URL", "http://127.0.0.1:1")

        payload, code = _post_ejecutar({"depto": "research", "texto": "hola"})

        assert code == 200
        assert payload["ok"] is False
        assert "error" in payload and payload["error"]

    def test_codex_department_targets_the_codex_url(self, monkeypatch):
        monkeypatch.setattr(hub, "CODEX_URL", "http://127.0.0.1:1")

        payload, code = _post_ejecutar({"depto": "codex", "texto": "hola"})

        assert code == 200
        assert payload["ok"] is False


class TestRenderConfigRoute:
    def test_post_persists_only_known_keys_atomically(self, tmp_path, monkeypatch):
        config_path = tmp_path / "render_config.json"
        monkeypatch.setattr(hub, "RENDER_CONFIG", str(config_path))

        payload, code = _post_render({
            "etiqueta": "tiktok", "activo": False, "unknown_key": "ignored"})

        assert code == 200
        assert payload["ok"] is True
        assert payload["config"]["etiqueta"] == "tiktok"
        assert payload["config"]["activo"] is False
        assert "unknown_key" not in payload["config"]
        on_disk = json.loads(config_path.read_text(encoding="utf-8"))
        assert on_disk == payload["config"]
        assert not (tmp_path / "render_config.json.tmp").exists()

    def test_post_merges_onto_existing_config_instead_of_overwriting_it(
            self, tmp_path, monkeypatch):
        config_path = tmp_path / "render_config.json"
        config_path.write_text(json.dumps({"remoto": "gdrive", "carpeta": "RD/old"}),
                               encoding="utf-8")
        monkeypatch.setattr(hub, "RENDER_CONFIG", str(config_path))

        payload, code = _post_render({"carpeta": "RD/new"})

        assert code == 200
        assert payload["config"]["carpeta"] == "RD/new"
        assert payload["config"]["remoto"] == "gdrive"
