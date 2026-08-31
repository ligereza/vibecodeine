"""HTTP-endpoint tests for interfaz.py's request handler `H`.

Follows the pattern in tests/test_interfaz_jobs_concurrency.py: a real
`interfaz.ReusableTCPServer` bound to an OS-assigned ephemeral port (port 0),
never the production port (8890) and never a real network call to a
provider. All disk paths the handler touches (DIRS, WORKFLOW_FILE, ENV_FILE,
JOBS_FILE) are monkeypatched to tmp_path so nothing here reads or writes
under ~/research or ~/plataforma.
"""
from __future__ import annotations

import http.client
import io
import json
import sys
import threading
import urllib.error
import urllib.parse
from pathlib import Path
from unittest.mock import MagicMock

import pytest

pytest.importorskip("fcntl", reason="interfaz.py importa fcntl (Linux-only)")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "cultura" / "mak_research"))

import interfaz  # noqa: E402


def _call(server, method, path, body=b"", content_type=None):
    conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    headers = {"Content-Length": str(len(body))}
    if content_type:
        headers["Content-Type"] = content_type
    try:
        conn.request(method, path, body=body, headers=headers)
        resp = conn.getresponse()
        return resp.status, resp.getheaders(), resp.read()
    finally:
        conn.close()


@pytest.fixture
def server():
    srv = interfaz.ReusableTCPServer(("127.0.0.1", 0), interfaz.H)
    thread = threading.Thread(target=srv.serve_forever)
    thread.start()
    try:
        yield srv
    finally:
        srv.shutdown()
        thread.join(timeout=5)
        srv.server_close()


@pytest.fixture
def isolated_dirs(tmp_path, monkeypatch):
    """Point every product directory at tmp_path so nothing touches ~/research."""
    dirs = {name: str(tmp_path / name) for name in interfaz.DIRS}
    for path in dirs.values():
        Path(path).mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(interfaz, "DIRS", dirs)
    return dirs


@pytest.fixture
def isolated_workflow(tmp_path, monkeypatch):
    path = tmp_path / "workflow.json"
    monkeypatch.setattr(interfaz, "WORKFLOW_FILE", str(path))
    return path


@pytest.fixture
def isolated_env(tmp_path, monkeypatch):
    path = tmp_path / "research.env"
    monkeypatch.setattr(interfaz, "ENV_FILE", str(path))
    return path


@pytest.fixture
def isolated_jobs_file(tmp_path, monkeypatch):
    path = tmp_path / "jobs.jsonl"
    monkeypatch.setattr(interfaz, "JOBS_FILE", str(path))
    return path


def _patch_expanduser_for(monkeypatch, mapping):
    original = interfaz.os.path.expanduser

    def fake(value):
        return mapping.get(value, original(value))

    monkeypatch.setattr(interfaz.os.path, "expanduser", fake)


# ---------------------------------------------------------------------------
# GET: rutas simples
# ---------------------------------------------------------------------------

def test_get_favicon_returns_no_content(server):
    status, _headers, body = _call(server, "GET", "/favicon.ico")
    assert status == 204
    assert body == b""


def test_get_unknown_api_path_is_404_json(server):
    status, _headers, body = _call(server, "GET", "/api/no-existe")
    assert status == 404
    payload = json.loads(body)
    assert payload["ok"] is False


def test_get_unknown_non_api_path_falls_back_to_the_spa_shell(
        server, isolated_dirs, isolated_workflow, isolated_env, monkeypatch):
    # do_GET has no catch-all 404: only /api/* paths are rejected explicitly.
    # Any other unmatched path (typos, stray client routes) renders the same
    # 200 main page instead of failing -- worth pinning since it means a
    # broken client-side link never surfaces as a 404 in the network tab.
    monkeypatch.setattr(interfaz, "JOBS", [])
    status, _headers, body = _call(server, "GET", "/algo-que-no-existe")
    assert status == 200
    assert b"___WF_DATA___" not in body


def test_get_api_workflow_returns_current_workflow(
        server, isolated_workflow, monkeypatch):
    status, _headers, body = _call(server, "GET", "/api/workflow")
    assert status == 200
    payload = json.loads(body)
    assert payload["mode"] == interfaz.DEFAULT_WORKFLOW["mode"]


def test_get_api_jobs_returns_last_fifteen_reversed(server, monkeypatch):
    jobs = [{"job_id": "j-%d" % i} for i in range(20)]
    monkeypatch.setattr(interfaz, "JOBS", jobs)
    status, _headers, body = _call(server, "GET", "/api/jobs")
    assert status == 200
    payload = json.loads(body)
    assert len(payload) == 15
    assert payload[0]["job_id"] == "j-19"  # most recent first


def test_get_api_organos_delegates_to_organos_snapshot(server, monkeypatch):
    monkeypatch.setattr(interfaz, "_organos", lambda: {"organos": ["fake"]})
    status, _headers, body = _call(server, "GET", "/api/organos")
    assert status == 200
    assert json.loads(body) == {"organos": ["fake"]}


def test_get_api_memoria_stats_delegates(server, monkeypatch):
    monkeypatch.setattr(interfaz, "_memoria_stats", lambda: {"chunks": 42})
    status, _headers, body = _call(server, "GET", "/api/memoria/stats")
    assert json.loads(body) == {"chunks": 42}


def test_get_api_memoria_grafo_success(server, monkeypatch):
    fake_memoria = MagicMock()
    fake_memoria.grafo_semantico.return_value = {"nodes": [{"id": "a"}], "edges": []}
    fake_memoria.limitar_grafo.side_effect = lambda g, limite: g
    monkeypatch.setitem(sys.modules, "memoria", fake_memoria)
    status, _headers, body = _call(server, "GET", "/api/memoria/grafo?umbral=0.6&limite=0")
    assert status == 200
    payload = json.loads(body)
    assert payload["nodes"] == [{"id": "a"}]
    fake_memoria.grafo_semantico.assert_called_once_with(umbral=0.6)


def test_get_api_memoria_grafo_failure_degrades_to_empty_graph_not_an_error_status(
        server, monkeypatch):
    """The graph endpoint swallows any failure into a 200 + empty graph +
    an 'error' string. That is a deliberate degrade-gracefully choice for a
    best-effort visualization, but it means a broken embeddings index or a
    down provider reads exactly like 'no relations yet' to the browser."""
    fake_memoria = MagicMock()
    fake_memoria.grafo_semantico.side_effect = RuntimeError("index corrupto")
    monkeypatch.setitem(sys.modules, "memoria", fake_memoria)
    status, _headers, body = _call(server, "GET", "/api/memoria/grafo")
    assert status == 200
    payload = json.loads(body)
    assert payload["nodes"] == [] and payload["edges"] == []
    assert "index corrupto" in payload["error"]


# ---------------------------------------------------------------------------
# GET /status: un status file con un PID muerto no debe leerse como vivo
# ---------------------------------------------------------------------------

def test_get_status_idle_when_no_status_file(server, tmp_path, monkeypatch):
    _patch_expanduser_for(
        monkeypatch,
        {"~/research/.current_status.json": str(tmp_path / "no-existe.json")})
    status, _headers, body = _call(server, "GET", "/status")
    assert status == 200
    assert json.loads(body) == {"idle": True}


def test_get_status_marks_dead_pid_as_stale(server, tmp_path, monkeypatch):
    status_path = tmp_path / ".current_status.json"
    # A PID essentially guaranteed not to exist.
    status_path.write_text(
        json.dumps({"pid": 999999, "status": "corriendo"}), encoding="utf-8")
    _patch_expanduser_for(
        monkeypatch, {"~/research/.current_status.json": str(status_path)})
    status, _headers, body = _call(server, "GET", "/status")
    payload = json.loads(body)
    assert payload["status"] == "stale (PID muerto)"


def test_get_status_keeps_reported_status_for_live_pid(server, tmp_path, monkeypatch):
    status_path = tmp_path / ".current_status.json"
    status_path.write_text(
        json.dumps({"pid": interfaz.os.getpid(), "status": "corriendo"}),
        encoding="utf-8")
    _patch_expanduser_for(
        monkeypatch, {"~/research/.current_status.json": str(status_path)})
    status, _headers, body = _call(server, "GET", "/status")
    payload = json.loads(body)
    assert payload["status"] == "corriendo"


# ---------------------------------------------------------------------------
# GET /f: visor de archivos, nunca fuera de DIRS ni con nombres raros
# ---------------------------------------------------------------------------

def test_get_file_viewer_rejects_unknown_dir_key(server, isolated_dirs):
    status, _headers, body = _call(server, "GET", "/f?d=%2Fetc&n=passwd.md")
    assert status == 404
    assert body == b"no"


def test_get_file_viewer_rejects_name_outside_allowed_pattern(server, isolated_dirs):
    status, _headers, body = _call(
        server, "GET", "/f?d=informes&" + urllib.parse.urlencode({"n": "../evil.md"}))
    assert status == 404


def test_get_file_viewer_serves_existing_file(server, isolated_dirs):
    (Path(isolated_dirs["informes"]) / "prueba.md").write_text(
        "# Hola\ncontenido", encoding="utf-8")
    status, headers, body = _call(server, "GET", "/f?d=informes&n=prueba.md")
    assert status == 200
    assert b"contenido" in body


def test_get_file_viewer_missing_file_is_404(server, isolated_dirs):
    status, _headers, body = _call(server, "GET", "/f?d=informes&n=no-existe.md")
    assert status == 404


# ---------------------------------------------------------------------------
# GET /: el render completo con jobs en cada estado y productos en disco
# ---------------------------------------------------------------------------

def test_get_root_renders_jobs_and_file_cards(
        server, isolated_dirs, isolated_workflow, isolated_env, monkeypatch):
    jobs = [
        {"tema": "tema listo", "modo": "research", "estado": "listo",
         "path": "20260830-100000-tema-listo.md", "t": "10:00:00", "job_id": "j1"},
        {"tema": "tema roto", "modo": "research", "estado": "FALLO",
         "error": "boom", "t": "10:05:00", "job_id": "j2"},
        {"tema": "tema pausado", "modo": "research", "estado": "PAUSADO",
         "error": "esperando revision", "t": "10:10:00", "job_id": "j3"},
    ]
    monkeypatch.setattr(interfaz, "JOBS", jobs)
    (Path(isolated_dirs["informes"]) /
     "20260830-100000-tema-listo.md").write_text("cuerpo", encoding="utf-8")

    status, headers, body = _call(server, "GET", "/")

    assert status == 200
    content_type = dict(headers)["Content-Type"]
    assert "text/html" in content_type
    text = body.decode("utf-8")
    assert "tema listo" in text
    assert "tema roto" in text
    assert "reintentar" in text  # PAUSADO renders resume actions
    assert "verArchivo" in text  # file card is clickable
    assert "___WF_DATA___" not in text  # placeholder actually substituted


def test_head_root_matches_get_but_no_body(server, isolated_dirs, isolated_workflow,
                                           isolated_env, monkeypatch):
    monkeypatch.setattr(interfaz, "JOBS", [])
    status, _headers, body = _call(server, "HEAD", "/")
    assert status == 200
    assert body == b""


# ---------------------------------------------------------------------------
# POST /run: enrutamiento de modo/tema antes de lanzar cualquier trabajo
# ---------------------------------------------------------------------------

def _form(**fields):
    return urllib.parse.urlencode(fields).encode("utf-8")


def test_post_run_rejects_unknown_mode(server):
    status, _headers, body = _call(
        server, "POST", "/run", _form(tema="x", modo="modo-fantasma"),
        "application/x-www-form-urlencoded")
    assert status == 400
    assert "modo invalido" in json.loads(body)["error"]


def test_post_run_rejects_empty_topic(server):
    status, _headers, body = _call(
        server, "POST", "/run", _form(tema="", modo="research"),
        "application/x-www-form-urlencoded")
    assert status == 400
    assert "vac" in json.loads(body)["error"]


def test_post_run_accepts_topicless_mode_that_does_not_need_one(server, monkeypatch):
    captured = {}

    def fake_lanzar(modo, tema, n, densidad="medio", memoria=False, formato=None,
                    work_contract=None, trigger="api:research"):
        captured.update(modo=modo, tema=tema)
    monkeypatch.setattr(interfaz, "_lanzar", fake_lanzar)

    status, _headers, body = _call(
        server, "POST", "/run", _form(tema="", modo="corpus"),
        "application/x-www-form-urlencoded")
    assert status == 200
    assert json.loads(body) == {"ok": True}
    assert captured == {"modo": "corpus", "tema": "corpus"}


def test_post_run_launches_with_resolved_alias_and_bounded_n(server, monkeypatch):
    captured = {}

    def fake_lanzar(modo, tema, n, densidad="medio", memoria=False, formato=None,
                    work_contract=None, trigger="api:research"):
        captured.update(modo=modo, tema=tema, n=n, densidad=densidad,
                        memoria=memoria, formato=formato, trigger=trigger)
    monkeypatch.setattr(interfaz, "_lanzar", fake_lanzar)

    status, _headers, body = _call(
        server, "POST", "/run",
        _form(tema="mi tema", modo="adversarial", densidad="largo", n="999",
             memoria="1", formato="formato-invalido-no-existe"),
        "application/x-www-form-urlencoded")

    assert status == 200
    assert captured["modo"] == "refutar"  # alias resolved
    assert captured["n"] == 10  # clamped to the [0, 10] range
    assert captured["memoria"] is True
    assert captured["formato"] is None  # unknown formats are ignored, not fatal


# ---------------------------------------------------------------------------
# POST /api/workflow y /config
# ---------------------------------------------------------------------------

def test_post_api_workflow_persists_and_reloads(server, isolated_workflow):
    wf = interfaz._deep_copy_default()
    wf["mode"] = "discussion"
    status, _headers, body = _call(
        server, "POST", "/api/workflow", json.dumps(wf).encode("utf-8"),
        "application/json")
    assert status == 200
    assert json.loads(body) == {"ok": True}
    assert json.loads(isolated_workflow.read_text(encoding="utf-8"))["mode"] == \
        "discussion"


def test_post_api_workflow_rejects_invalid_json(server, isolated_workflow):
    status, _headers, body = _call(
        server, "POST", "/api/workflow", b"{not json",
        "application/json")
    assert status == 400
    assert json.loads(body)["ok"] is False


def test_post_config_preserves_unknown_keys_like_credentials(server, isolated_env):
    isolated_env.write_text("GROQ_MODEL=old\nCUSTOM_SECRET=keepme\n", encoding="utf-8")
    status, _headers, body = _call(
        server, "POST", "/config", _form(GROQ_MODEL="nuevo-modelo"),
        "application/x-www-form-urlencoded")
    assert status == 200
    saved = isolated_env.read_text(encoding="utf-8")
    assert "GROQ_MODEL=nuevo-modelo" in saved
    assert "CUSTOM_SECRET=keepme" in saved


# ---------------------------------------------------------------------------
# POST /api/memoria/index, /api/repair, /api/reanudar
# ---------------------------------------------------------------------------

def test_post_memoria_index_reports_whether_it_actually_started(server, monkeypatch):
    monkeypatch.setattr(interfaz, "_reindexar_async", lambda rebuild=False: False)
    status, _headers, body = _call(
        server, "POST", "/api/memoria/index", _form(rebuild="1"),
        "application/x-www-form-urlencoded")
    assert status == 200
    assert json.loads(body) == {"ok": True, "started": False}


def test_post_repair_returns_diagnosis(server, monkeypatch):
    monkeypatch.setattr(interfaz, "_diagnosticar", lambda tema, error: "usa retry")
    status, _headers, body = _call(
        server, "POST", "/api/repair", _form(tema="t", error="e"),
        "application/x-www-form-urlencoded")
    assert status == 200
    assert json.loads(body) == {"ok": True, "diagnostico": "usa retry"}


def test_post_repair_failure_is_a_500_not_a_silent_empty_diagnosis(server, monkeypatch):
    def boom(tema, error):
        raise RuntimeError("todos los proveedores fallaron")
    monkeypatch.setattr(interfaz, "_diagnosticar", boom)
    status, _headers, body = _call(
        server, "POST", "/api/repair", _form(tema="t", error="e"),
        "application/x-www-form-urlencoded")
    assert status == 500
    assert json.loads(body)["ok"] is False


def test_post_reanudar_unknown_job_via_http(server, monkeypatch):
    monkeypatch.setattr(interfaz, "JOBS", [])
    status, _headers, body = _call(
        server, "POST", "/api/reanudar", _form(job_id="x", accion="reintentar"),
        "application/x-www-form-urlencoded")
    assert status == 404


# ---------------------------------------------------------------------------
# POST /api/fructificacion y /api/fusion
# ---------------------------------------------------------------------------

def test_post_fructificacion_rejects_invalid_json(server):
    status, _headers, body = _call(
        server, "POST", "/api/fructificacion", b"{not json", "application/json")
    assert status == 400


def test_post_fructificacion_rejects_non_object_json(server):
    status, _headers, body = _call(
        server, "POST", "/api/fructificacion", b"[1,2,3]", "application/json")
    assert status == 400


def test_post_fructificacion_invalidates_graph_cache_best_effort(server, monkeypatch):
    fake_fruct = MagicMock()
    fake_fruct.decidir.return_value = {"ok": True}
    monkeypatch.setitem(sys.modules, "fructificacion", fake_fruct)
    fake_memoria = MagicMock()
    fake_memoria.invalidate_grafo_cache.side_effect = RuntimeError("lock ocupado")
    monkeypatch.setitem(sys.modules, "memoria", fake_memoria)

    status, _headers, body = _call(
        server, "POST", "/api/fructificacion",
        json.dumps({"id": "a", "accion": "aceptar"}).encode("utf-8"),
        "application/json")

    assert status == 200  # a cache-invalidation failure never breaks the decision
    assert json.loads(body) == {"ok": True}


def test_post_fusion_requires_at_least_two_sources(server):
    status, _headers, body = _call(
        server, "POST", "/api/fusion",
        json.dumps({"tema": "x", "fuentes": ["solo-una"]}).encode("utf-8"),
        "application/json")
    assert status == 400
    assert "faltan fuentes" in json.loads(body)["error"]


def test_post_fusion_creates_primordio_and_launches_panel(server, monkeypatch):
    fake_fusion = MagicMock()
    fake_fusion.crear.return_value = {"id": "primordio-1"}
    monkeypatch.setitem(sys.modules, "fusion", fake_fusion)
    fake_memoria = MagicMock()
    monkeypatch.setitem(sys.modules, "memoria", fake_memoria)
    lanzar_calls = []
    monkeypatch.setattr(
        interfaz, "_lanzar",
        lambda *a, **k: lanzar_calls.append(a))

    status, _headers, body = _call(
        server, "POST", "/api/fusion",
        json.dumps({"tema": "sintesis", "fuentes": ["a.md", "b.md"]}).encode("utf-8"),
        "application/json")

    assert status == 200
    payload = json.loads(body)
    assert payload == {"ok": True, "primordio": {"id": "primordio-1"}}
    assert lanzar_calls and lanzar_calls[0][0] == "panel"


# ---------------------------------------------------------------------------
# POST /api/intake: solo el enrutamiento; la validacion ya se prueba aparte
# ---------------------------------------------------------------------------

def test_post_intake_invalid_json_body(server):
    status, _headers, body = _call(
        server, "POST", "/api/intake", b"{not json", "application/json")
    assert status == 400


def test_post_intake_routes_into_validation(server):
    status, _headers, body = _call(
        server, "POST", "/api/intake", b"{}", "application/json")
    assert status == 400
    assert "source_index o source_root" in json.loads(body)["error"]


# ---------------------------------------------------------------------------
# POST /api/codex/experimentar y /api/ideas/anotar: bridges same-origin,
# nunca deben pegarle a la red real en un test.
# ---------------------------------------------------------------------------

def test_post_codex_experimentar_relays_upstream_json(server, monkeypatch):
    fake_response = MagicMock()
    fake_response.read.return_value = json.dumps({"ok": True, "out": 1}).encode()
    fake_response.__enter__ = lambda self: fake_response
    fake_response.__exit__ = lambda self, *a: False
    monkeypatch.setattr(interfaz.urllib.request, "urlopen",
                        lambda *a, **k: fake_response)

    status, _headers, body = _call(
        server, "POST", "/api/codex/experimentar", b"tema=x",
        "application/x-www-form-urlencoded")
    assert status == 200
    assert json.loads(body) == {"ok": True, "out": 1}


def test_post_codex_experimentar_preserves_upstream_error_status(server, monkeypatch):
    def boom(*a, **k):
        fp = io.BytesIO(json.dumps({"ok": False, "error": "detalle real"}).encode())
        raise urllib.error.HTTPError("http://x", 422, "Unprocessable", {}, fp)
    monkeypatch.setattr(interfaz.urllib.request, "urlopen", boom)

    status, _headers, body = _call(
        server, "POST", "/api/codex/experimentar", b"tema=x",
        "application/x-www-form-urlencoded")
    assert status == 422  # not relabeled as a generic 502
    assert json.loads(body)["error"] == "detalle real"


def test_post_ideas_anotar_relays_upstream_success(server, monkeypatch):
    fake_response = MagicMock()
    fake_response.read.return_value = json.dumps({"ok": True, "id": "idea-1"}).encode()
    fake_response.__enter__ = lambda self: fake_response
    fake_response.__exit__ = lambda self, *a: False
    monkeypatch.setattr(interfaz.urllib.request, "urlopen",
                        lambda *a, **k: fake_response)

    status, _headers, body = _call(
        server, "POST", "/api/ideas/anotar",
        json.dumps({"texto": "una idea"}).encode("utf-8"), "application/json")
    assert status == 200
    assert json.loads(body) == {"ok": True, "id": "idea-1"}


def test_post_ideas_anotar_network_failure_is_502_not_a_crash(server, monkeypatch):
    def boom(*a, **k):
        raise OSError("connection refused")
    monkeypatch.setattr(interfaz.urllib.request, "urlopen", boom)

    status, _headers, body = _call(
        server, "POST", "/api/ideas/anotar", b"{}", "application/json")
    assert status == 502
    assert json.loads(body)["ok"] is False


def test_post_codex_experimentar_generic_failure_is_502(server, monkeypatch):
    def boom(*a, **k):
        raise OSError("connection refused")
    monkeypatch.setattr(interfaz.urllib.request, "urlopen", boom)

    status, _headers, body = _call(
        server, "POST", "/api/codex/experimentar", b"tema=x",
        "application/x-www-form-urlencoded")
    assert status == 502
    assert json.loads(body)["ok"] is False


def test_upstream_error_falls_back_to_raw_text_on_non_json_body(server, monkeypatch):
    def boom(*a, **k):
        fp = io.BytesIO(b"<html>gateway down</html>")
        raise urllib.error.HTTPError("http://x", 503, "Service Unavailable", {}, fp)
    monkeypatch.setattr(interfaz.urllib.request, "urlopen", boom)

    status, _headers, body = _call(
        server, "POST", "/api/codex/experimentar", b"tema=x",
        "application/x-www-form-urlencoded")
    assert status == 503
    payload = json.loads(body)
    assert payload["ok"] is False
    assert "gateway down" in payload["error"]


# ---------------------------------------------------------------------------
# huecos adicionales: rutas de fallo dentro de las mismas rutas ya probadas
# ---------------------------------------------------------------------------

def test_get_root_skips_directory_that_cannot_be_listed(
        server, isolated_dirs, isolated_workflow, isolated_env, monkeypatch):
    monkeypatch.setattr(interfaz, "JOBS", [])
    # remove one product directory after creation: os.listdir() on it raises
    import shutil
    shutil.rmtree(isolated_dirs["grafos"])
    status, _headers, body = _call(server, "GET", "/")
    assert status == 200  # a single unreadable product folder never breaks the page


def test_get_root_renders_file_card_for_name_without_date_stamp(
        server, isolated_dirs, isolated_workflow, isolated_env, monkeypatch):
    monkeypatch.setattr(interfaz, "JOBS", [])
    (Path(isolated_dirs["informes"]) / "sin-fecha-en-el-nombre.md").write_text(
        "cuerpo", encoding="utf-8")
    status, _headers, body = _call(server, "GET", "/")
    assert status == 200
    assert b"sin-fecha-en-el-nombre" in body


def test_post_fructificacion_module_failure_is_500(server, monkeypatch):
    fake_fruct = MagicMock()
    fake_fruct.decidir.side_effect = RuntimeError("regla rota")
    monkeypatch.setitem(sys.modules, "fructificacion", fake_fruct)

    status, _headers, body = _call(
        server, "POST", "/api/fructificacion",
        json.dumps({"id": "a", "accion": "aceptar"}).encode("utf-8"),
        "application/json")
    assert status == 500
    assert json.loads(body)["ok"] is False


def test_post_fusion_rejects_non_object_json(server):
    status, _headers, body = _call(
        server, "POST", "/api/fusion", b"[1,2,3]", "application/json")
    assert status == 400


def test_post_fusion_swallows_graph_cache_invalidation_failure(server, monkeypatch):
    fake_fusion = MagicMock()
    fake_fusion.crear.return_value = {"id": "primordio-1"}
    monkeypatch.setitem(sys.modules, "fusion", fake_fusion)
    fake_memoria = MagicMock()
    fake_memoria.invalidate_grafo_cache.side_effect = RuntimeError("lock ocupado")
    monkeypatch.setitem(sys.modules, "memoria", fake_memoria)
    monkeypatch.setattr(interfaz, "_lanzar", lambda *a, **k: None)

    status, _headers, body = _call(
        server, "POST", "/api/fusion",
        json.dumps({"tema": "x", "fuentes": ["a.md", "b.md"]}).encode("utf-8"),
        "application/json")
    assert status == 200


def test_post_fusion_module_failure_is_500(server, monkeypatch):
    fake_fusion = MagicMock()
    fake_fusion.crear.side_effect = RuntimeError("motor de fusion caido")
    monkeypatch.setitem(sys.modules, "fusion", fake_fusion)

    status, _headers, body = _call(
        server, "POST", "/api/fusion",
        json.dumps({"tema": "x", "fuentes": ["a.md", "b.md"]}).encode("utf-8"),
        "application/json")
    assert status == 500
    assert json.loads(body)["ok"] is False


def test_post_workflow_save_oserror_is_500_not_a_crash(server, isolated_workflow,
                                                        monkeypatch):
    def boom(wf):
        raise OSError("disco lleno")
    monkeypatch.setattr(interfaz, "_save_workflow", boom)

    status, _headers, body = _call(
        server, "POST", "/api/workflow", b"{}", "application/json")
    assert status == 500
    assert json.loads(body)["ok"] is False


def test_post_run_normalizes_invalid_densidad_to_medio(server, monkeypatch):
    captured = {}

    def fake_lanzar(modo, tema, n, densidad="medio", memoria=False, formato=None,
                    work_contract=None, trigger="api:research"):
        captured["densidad"] = densidad
    monkeypatch.setattr(interfaz, "_lanzar", fake_lanzar)
    status, _headers, body = _call(
        server, "POST", "/run", _form(tema="x", modo="research", densidad="urgentisimo"),
        "application/x-www-form-urlencoded")
    assert status == 200
    assert captured["densidad"] == "medio"


def test_post_run_ignores_valid_json_work_contract_that_is_not_an_object(
        server, monkeypatch):
    captured = {}

    def fake_lanzar(modo, tema, n, densidad="medio", memoria=False, formato=None,
                    work_contract=None, trigger="api:research"):
        captured["work_contract"] = work_contract
    monkeypatch.setattr(interfaz, "_lanzar", fake_lanzar)

    status, _headers, body = _call(
        server, "POST", "/run",
        _form(tema="x", modo="research", work_contract="[1,2,3]"),
        "application/x-www-form-urlencoded")
    assert status == 200
    assert captured["work_contract"] is None


def test_post_run_forwards_a_valid_work_contract_object(server, monkeypatch):
    captured = {}

    def fake_lanzar(modo, tema, n, densidad="medio", memoria=False, formato=None,
                    work_contract=None, trigger="api:research"):
        captured["work_contract"] = work_contract
    monkeypatch.setattr(interfaz, "_lanzar", fake_lanzar)

    status, _headers, body = _call(
        server, "POST", "/run",
        _form(tema="x", modo="research",
             work_contract=json.dumps({"format": "informe"})),
        "application/x-www-form-urlencoded")
    assert status == 200
    assert captured["work_contract"] == {"format": "informe"}


def test_post_unknown_non_api_path_is_404_no(server):
    # Unlike GET, do_POST has an explicit catch-all 404 for stray routes.
    status, _headers, body = _call(server, "POST", "/algo-que-no-existe", b"")
    assert status == 404
    assert body == b"no"


def test_post_run_ignores_malformed_work_contract_instead_of_failing(server, monkeypatch):
    captured = {}

    def fake_lanzar(modo, tema, n, densidad="medio", memoria=False, formato=None,
                    work_contract=None, trigger="api:research"):
        captured["work_contract"] = work_contract
    monkeypatch.setattr(interfaz, "_lanzar", fake_lanzar)

    status, _headers, body = _call(
        server, "POST", "/run",
        _form(tema="x", modo="research", work_contract="{not json"),
        "application/x-www-form-urlencoded")
    assert status == 200
    assert captured["work_contract"] is None
