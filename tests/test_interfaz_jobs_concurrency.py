import json
import http.client
import io
import sys
import threading
import urllib.error
from pathlib import Path

import pytest

pytest.importorskip("fcntl")

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "cultura" / "mak_research"))
import interfaz  # noqa: E402


def _call(server, method, path, body=b""):
    connection = http.client.HTTPConnection(
        "127.0.0.1", server.server_port, timeout=3)
    headers = {"Content-Length": str(len(body))}
    if body:
        headers["Content-Type"] = "application/json"
    try:
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        return response.status, response.getheaders(), response.read()
    finally:
        connection.close()


def _serve_interfaz():
    server = interfaz.ReusableTCPServer(("127.0.0.1", 0), interfaz.H)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    return server, thread


def test_interface_serializes_concurrent_job_appends(tmp_path, monkeypatch):
    path = str(tmp_path / "jobs.jsonl")
    monkeypatch.setattr(interfaz, "JOBS_FILE", path)
    barrier = threading.Barrier(12)

    def write_record(index):
        barrier.wait(timeout=3)
        interfaz._append_job_record({"job_id": "job-%d" % index,
                                     "estado": "listo"})

    threads = [threading.Thread(target=write_record, args=(i,))
               for i in range(12)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    records = [json.loads(line) for line in
               Path(path).read_text(encoding="utf-8").splitlines()]
    assert len(records) == 12
    assert {record["job_id"] for record in records} == {
        "job-%d" % index for index in range(12)}


def test_interface_serializes_configuration_writes(tmp_path, monkeypatch):
    path = str(tmp_path / "research.env")
    monkeypatch.setattr(interfaz, "ENV_FILE", path)
    active = {"now": 0, "max": 0}
    guard = threading.Lock()
    barrier = threading.Barrier(2)

    def touch_config():
        barrier.wait(timeout=3)
        with interfaz._exclusive_config_lock():
            with guard:
                active["now"] += 1
                active["max"] = max(active["max"], active["now"])
            import time
            time.sleep(0.03)
            with guard:
                active["now"] -= 1

    threads = [threading.Thread(target=touch_config) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    assert active["max"] == 1


def test_interface_config_replace_failure_preserves_previous_file(
        tmp_path, monkeypatch):
    path = tmp_path / "research.env"
    path.write_text("GROQ_MODEL=old\n", encoding="utf-8")
    monkeypatch.setattr(interfaz, "ENV_FILE", str(path))
    original_replace = interfaz.os.replace

    def fail_install(source, destination):
        if destination == str(path):
            raise OSError("simulated replace failure")
        return original_replace(source, destination)

    monkeypatch.setattr(interfaz.os, "replace", fail_install)
    with pytest.raises(OSError, match="simulated replace failure"):
        interfaz._guardar_config({"GROQ_MODEL": ["new"]})

    assert path.read_text(encoding="utf-8") == "GROQ_MODEL=old\n"
    assert not list(tmp_path.glob(".research.env-*.tmp"))


def test_interface_reloads_persisted_jobs_after_restart(tmp_path, monkeypatch):
    path = tmp_path / "jobs.jsonl"
    path.write_text(
        '{"job_id":"old-1","estado":"listo"}\n'
        'linea rota\n'
        '{"job_id":"old-2","estado":"FALLO"}\n',
        encoding="utf-8")
    monkeypatch.setattr(interfaz, "JOBS_FILE", str(path))
    monkeypatch.setattr(interfaz, "JOBS", [])

    interfaz._load_jobs()

    assert [job["job_id"] for job in interfaz.JOBS] == ["old-1", "old-2"]
    source = path.read_text(encoding="utf-8")
    assert "linea rota" in source  # recovery never rewrites the append-only ledger


def test_interface_api_unknown_and_head_contract():
    server, thread = _serve_interfaz()
    try:
        status, headers, body = _call(server, "GET", "/api/unknown")
        assert status == 404
        assert dict(headers)["Content-Type"].startswith("application/json")
        assert json.loads(body)["error"] == "ruta_api_no_encontrada"

        status, _, body = _call(server, "POST", "/api/unknown", b"{}")
        assert status == 404
        assert json.loads(body)["error"] == "ruta_api_no_encontrada"

        status, _, body = _call(server, "HEAD", "/api/jobs")
        assert status == 200
        assert body == b""
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()


def test_interface_rejects_invalid_json_before_domain_logic():
    server, thread = _serve_interfaz()
    try:
        for path in ("/api/fructificacion", "/api/fusion"):
            status, _, body = _call(server, "POST", path, b"{")
            assert status == 400
            assert json.loads(body)["error"] == "json invalido"
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()


def test_interface_preserves_upstream_http_error_status(monkeypatch):
    def fail_upstream(request, timeout=0):
        raise urllib.error.HTTPError(
            request.full_url, 400, "Bad Request", {},
            io.BytesIO(b'{"ok":false,"error":"upstream rejected"}'))

    monkeypatch.setattr(interfaz.urllib.request, "urlopen", fail_upstream)
    server, thread = _serve_interfaz()
    try:
        for path in ("/api/codex/experimentar", "/api/ideas/anotar"):
            status, _, body = _call(server, "POST", path, b"{}")
            assert status == 400
            assert json.loads(body)["error"] == "upstream rejected"
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()
