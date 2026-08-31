"""Unit tests for interfaz.py's pure/mockable logic (no real HTTP socket,
no network, no writes under ~/research or ~/plataforma).

Coverage target: interfaz.py was measured at 45% (762 stmts, 420 missing)
before this file. These tests hit the request-routing and job-lifecycle
helper functions directly, following the sys.path + `import interfaz`
pattern already used by tests/test_mak_interfaz_config.py and
tests/test_interfaz_jobs_concurrency.py.
"""
from __future__ import annotations

import importlib
import importlib.util
import json
import sys
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

pytest.importorskip("fcntl", reason="interfaz.py importa fcntl (Linux-only)")

REPO_ROOT = Path(__file__).resolve().parents[1]
MAK_RESEARCH = REPO_ROOT / "cultura" / "mak_research"
sys.path.insert(0, str(MAK_RESEARCH))

import interfaz  # noqa: E402
import research_lib  # noqa: E402


# ---------------------------------------------------------------------------
# _resolver_modo: alias vs. clave real vs. modo desconocido
# ---------------------------------------------------------------------------

def test_resolver_modo_accepts_real_backend_key():
    modo, err = interfaz._resolver_modo("research")
    assert modo == "research"
    assert err is None


def test_resolver_modo_translates_frontend_alias_adversarial():
    # Regression: "modo=adversarial corria como research" (comment in source)
    # was a real production bug where an unknown alias fell through to a
    # default backend instead of failing loudly.
    modo, err = interfaz._resolver_modo("adversarial")
    assert modo == "refutar"
    assert err is None


def test_resolver_modo_translates_all_frontend_aliases():
    for alias, backend in interfaz.MODO_ALIAS_FRONTEND.items():
        modo, err = interfaz._resolver_modo(alias)
        assert modo == backend
        assert err is None


def test_resolver_modo_unknown_mode_never_falls_back_silently():
    modo, err = interfaz._resolver_modo("no-existe-este-modo")
    assert modo is None
    assert err["ok"] is False
    assert "modo invalido" in err["error"]
    assert "no-existe-este-modo" in err["error"]


# ---------------------------------------------------------------------------
# _guardia_contenido: fails open when the content filter is unavailable
# ---------------------------------------------------------------------------

def test_guardia_contenido_fails_open_when_filtro_module_missing(monkeypatch):
    # filtro_entrada does not exist on sys.path in the test environment, so
    # this exercises the real ImportError branch, not a simulated one.
    monkeypatch.setitem(sys.modules, "filtro_entrada", None)
    veredicto = interfaz._guardia_contenido("cualquier tema")
    assert veredicto is None


def test_guardia_contenido_uses_filtro_when_available(monkeypatch):
    fake = MagicMock()
    fake.clasificar.return_value = {"veredicto": "BLOQUEADO", "razon": "test"}
    monkeypatch.setitem(sys.modules, "filtro_entrada", fake)
    veredicto = interfaz._guardia_contenido("tema sensible")
    assert veredicto == {"veredicto": "BLOQUEADO", "razon": "test"}
    fake.clasificar.assert_called_once_with("tema sensible")


# ---------------------------------------------------------------------------
# _verify_result_contract: un job "ok" puede seguir siendo un defecto
# ---------------------------------------------------------------------------

def test_verify_result_contract_empty_when_no_contract_requested():
    assert interfaz._verify_result_contract({}, {"ok": True, "path": "x.md"}) == ""


def test_verify_result_contract_empty_when_result_not_ok():
    job = {"work_contract": {"format": "informe"}}
    assert interfaz._verify_result_contract(job, {"ok": False, "path": "x.md"}) == ""


def test_verify_result_contract_flags_missing_json_sidecar(tmp_path):
    job = {"work_contract": {"format": "informe"}}
    md_path = tmp_path / "producto.md"
    md_path.write_text("cuerpo", encoding="utf-8")
    result = {"ok": True, "path": str(md_path)}
    assert interfaz._verify_result_contract(job, result) == \
        "work_contract_output_json_missing"


def test_verify_result_contract_flags_format_mismatch(tmp_path):
    job = {"work_contract": {"format": "informe"}}
    md_path = tmp_path / "producto.md"
    md_path.write_text("cuerpo", encoding="utf-8")
    (tmp_path / "producto.json").write_text(
        json.dumps({"formato": "curatoria"}), encoding="utf-8")
    result = {"ok": True, "path": str(md_path)}
    assert interfaz._verify_result_contract(job, result) == \
        "work_contract_output_format_mismatch"


def test_verify_result_contract_passes_when_format_matches(tmp_path):
    job = {"work_contract": {"format": "informe"}}
    md_path = tmp_path / "producto.md"
    md_path.write_text("cuerpo", encoding="utf-8")
    (tmp_path / "producto.json").write_text(
        json.dumps({"formato": "informe"}), encoding="utf-8")
    result = {"ok": True, "path": str(md_path)}
    assert interfaz._verify_result_contract(job, result) == ""


# ---------------------------------------------------------------------------
# _aplicar_resultado_job: an "ok=True" from the worker is not always success
# ---------------------------------------------------------------------------

def test_aplicar_resultado_job_pausado():
    job = {}
    interfaz._aplicar_resultado_job(
        job, {"pausado": True, "checkpoint": "cp.json", "tail": "esperando input\n"})
    assert job["estado"] == "PAUSADO"
    assert job["checkpoint"] == "cp.json"
    assert job["error"] == "esperando input"


def test_aplicar_resultado_job_review():
    job = {}
    interfaz._aplicar_resultado_job(
        job, {"review": True, "path": "/x/informe.md", "tail": "calidad baja"})
    assert job["estado"] == "REVISAR"
    assert job["path"] == "informe.md"
    assert job["error"] == "calidad baja"


def test_aplicar_resultado_job_ok_marks_listo():
    job = {}
    interfaz._aplicar_resultado_job(job, {"ok": True, "path": "/x/informe.md"})
    assert job["estado"] == "listo"
    assert job["path"] == "informe.md"


def test_aplicar_resultado_job_not_ok_keeps_error_tail():
    job = {}
    interfaz._aplicar_resultado_job(
        job, {"ok": False, "path": "", "tail": "Traceback (most recent call last)\nboom"})
    assert job["estado"] == "FALLO"
    assert "boom" in job["error"]


def test_aplicar_resultado_job_ok_but_contract_broken_is_still_a_failure(tmp_path):
    """Regression-shaped: a worker that reports ok=True while its declared
    output contract is broken must not read as a healthy 'listo' job."""
    job = {"work_contract": {"format": "curatoria"}}
    md_path = tmp_path / "informe.md"
    md_path.write_text("cuerpo", encoding="utf-8")
    (tmp_path / "informe.json").write_text(
        json.dumps({"formato": "informe"}), encoding="utf-8")
    interfaz._aplicar_resultado_job(job, {"ok": True, "path": str(md_path)})
    assert job["estado"] == "FALLO"
    assert job["error"] == "work_contract_output_format_mismatch"


# ---------------------------------------------------------------------------
# _diagnosticar: auto-repair, mockeando el LLM
# ---------------------------------------------------------------------------

def test_diagnosticar_returns_llm_text(monkeypatch):
    monkeypatch.setattr(
        research_lib, "diagnosticar_error",
        lambda llm, contexto, error: ("diagnostico de prueba", "gemini"))
    texto = interfaz._diagnosticar("mi tema", "algun traceback")
    assert texto == "diagnostico de prueba"


# ---------------------------------------------------------------------------
# _memoria_stats: counts chunks without touching the real production index
# ---------------------------------------------------------------------------

def _patch_expanduser_for(monkeypatch, mapping):
    original = interfaz.os.path.expanduser

    def fake(value):
        return mapping.get(value, original(value))

    monkeypatch.setattr(interfaz.os.path, "expanduser", fake)


def test_memoria_stats_counts_nonblank_lines(tmp_path, monkeypatch):
    index_path = tmp_path / "index.jsonl"
    index_path.write_text('{"a":1}\n\n{"b":2}\n', encoding="utf-8")
    _patch_expanduser_for(
        monkeypatch, {"~/research/memoria/index.jsonl": str(index_path)})
    assert interfaz._memoria_stats() == {"chunks": 2}


def test_memoria_stats_missing_file_reports_zero(tmp_path, monkeypatch):
    _patch_expanduser_for(
        monkeypatch,
        {"~/research/memoria/index.jsonl": str(tmp_path / "no-existe.jsonl")})
    assert interfaz._memoria_stats() == {"chunks": 0}


# ---------------------------------------------------------------------------
# _procesos_vivos: subprocess ausente/fallando no debe tumbar el request
# ---------------------------------------------------------------------------

def test_procesos_vivos_returns_lowercased_stdout(monkeypatch):
    fake_result = MagicMock(stdout="INTERFAZ.PY corriendo\n")
    monkeypatch.setattr(
        interfaz.subprocess, "run", lambda *a, **k: fake_result)
    assert interfaz._procesos_vivos() == "interfaz.py corriendo\n"


def test_procesos_vivos_swallows_subprocess_failure(monkeypatch):
    def boom(*a, **k):
        raise OSError("pgrep no encontrado")
    monkeypatch.setattr(interfaz.subprocess, "run", boom)
    assert interfaz._procesos_vivos() == ""


# ---------------------------------------------------------------------------
# _reindexar_async: un solo reindex a la vez
# ---------------------------------------------------------------------------

class _FakeLock:
    def __init__(self, can_acquire):
        self._can_acquire = can_acquire

    def acquire(self, blocking=True):
        return self._can_acquire

    def release(self):
        pass


def test_reindexar_async_refuses_second_run_while_locked(monkeypatch):
    monkeypatch.setattr(interfaz, "_REINDEX_LOCK", _FakeLock(False))
    assert interfaz._reindexar_async() is False


def test_reindexar_async_runs_indexer_in_background(monkeypatch):
    fake_memoria = MagicMock()
    called = threading.Event()

    def fake_indexar(rebuild=False):
        called.set()
        return {"archivos": 0, "chunks": 0, "nuevos": 0}

    fake_memoria.indexar = fake_indexar
    monkeypatch.setitem(sys.modules, "memoria", fake_memoria)

    started = interfaz._reindexar_async(rebuild=True)
    assert started is True
    assert called.wait(timeout=2)


# ---------------------------------------------------------------------------
# _orden_canvas: execution order follows the priority drawn on the canvas
# ---------------------------------------------------------------------------

def test_orden_canvas_sorts_active_nodes_by_priority(monkeypatch):
    wf = {
        "nodes": {
            "groq": {"active": True, "priority": 3},
            "gemini": {"active": True, "priority": 1},
            "cerebras": {"active": False, "priority": 2},
            "ollama": {"active": True, "priority": 2},
        }
    }
    monkeypatch.setattr(interfaz, "_load_workflow", lambda: wf)
    assert interfaz._orden_canvas() == "gemini,ollama,groq"


def test_orden_canvas_none_when_no_provider_active(monkeypatch):
    wf = {"nodes": {p: {"active": False}
                    for p in ("groq", "gemini", "cerebras", "ollama")}}
    monkeypatch.setattr(interfaz, "_load_workflow", lambda: wf)
    assert interfaz._orden_canvas() is None


# ---------------------------------------------------------------------------
# _load_workflow / _save_workflow: fusion con el default, nunca un crash
# ---------------------------------------------------------------------------

def test_load_workflow_falls_back_to_default_on_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(interfaz, "WORKFLOW_FILE", str(tmp_path / "no-existe.json"))
    wf = interfaz._load_workflow()
    assert wf == interfaz.DEFAULT_WORKFLOW


def test_load_workflow_falls_back_to_default_on_corrupt_json(tmp_path, monkeypatch):
    path = tmp_path / "workflow.json"
    path.write_text("{not json", encoding="utf-8")
    monkeypatch.setattr(interfaz, "WORKFLOW_FILE", str(path))
    wf = interfaz._load_workflow()
    assert wf == interfaz.DEFAULT_WORKFLOW


def test_load_workflow_merges_partial_node_overrides(tmp_path, monkeypatch):
    path = tmp_path / "workflow.json"
    path.write_text(json.dumps({
        "mode": "grafo",
        "nodes": {"groq": {"model": "custom-model"}},
        "connections": [],
    }), encoding="utf-8")
    monkeypatch.setattr(interfaz, "WORKFLOW_FILE", str(path))
    wf = interfaz._load_workflow()
    assert wf["mode"] == "grafo"
    assert wf["nodes"]["groq"]["model"] == "custom-model"
    # unspecified default fields survive the merge
    assert wf["nodes"]["groq"]["priority"] == 1
    # empty connections list is itself a valid state (grafo sin aristas)
    assert wf["connections"] == []


def test_save_then_load_workflow_roundtrip(tmp_path, monkeypatch):
    path = tmp_path / "workflow.json"
    monkeypatch.setattr(interfaz, "WORKFLOW_FILE", str(path))
    wf = interfaz._deep_copy_default()
    wf["mode"] == "single"
    interfaz._save_workflow(wf)
    assert interfaz._load_workflow()["mode"] == wf["mode"]


# ---------------------------------------------------------------------------
# _load_jobs: corrupt lines do not break the load, and only 15 are kept
# ---------------------------------------------------------------------------

def test_load_jobs_skips_corrupt_lines_and_caps_at_fifteen(tmp_path, monkeypatch):
    path = tmp_path / "jobs.jsonl"
    lines = ["linea rota"] + [
        json.dumps({"job_id": "j-%d" % i}) for i in range(20)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    monkeypatch.setattr(interfaz, "JOBS_FILE", str(path))
    monkeypatch.setattr(interfaz, "JOBS", [])
    interfaz._load_jobs()
    assert len(interfaz.JOBS) == 15
    assert interfaz.JOBS[-1]["job_id"] == "j-19"


def test_load_jobs_missing_file_leaves_jobs_untouched(tmp_path, monkeypatch):
    monkeypatch.setattr(interfaz, "JOBS_FILE", str(tmp_path / "no-existe.jsonl"))
    monkeypatch.setattr(interfaz, "JOBS", [])
    interfaz._load_jobs()
    assert interfaz.JOBS == []


# ---------------------------------------------------------------------------
# _lanzar: the content guard blocks before anything runs
# ---------------------------------------------------------------------------

def test_lanzar_blocks_on_content_guard_verdict(monkeypatch):
    monkeypatch.setattr(interfaz, "JOBS", [])
    monkeypatch.setattr(interfaz, "_guardia_contenido",
                        lambda tema: {"veredicto": "OPERATIVO", "razon": "no"})
    monkeypatch.setattr(interfaz, "_append_job_record", lambda job: None)
    run_tema_mock = MagicMock()
    monkeypatch.setattr(interfaz, "run_tema", run_tema_mock)

    interfaz._lanzar("research", "tema riesgoso", None)
    deadline = time.time() + 2
    while time.time() < deadline and interfaz.JOBS[-1]["estado"] != "BLOQUEADO":
        time.sleep(0.01)

    job = interfaz.JOBS[-1]
    assert job["estado"] == "BLOQUEADO"
    assert "OPERATIVO" in job["error"]
    run_tema_mock.assert_not_called()


def test_lanzar_runs_and_records_success(monkeypatch):
    monkeypatch.setattr(interfaz, "JOBS", [])
    monkeypatch.setattr(interfaz, "_guardia_contenido", lambda tema: None)
    recorded = []
    monkeypatch.setattr(interfaz, "_append_job_record", recorded.append)
    monkeypatch.setattr(
        interfaz, "run_tema",
        lambda *a, **k: {"ok": True, "path": "/x/informe.md"})

    interfaz._lanzar("research", "tema tranquilo", None)
    deadline = time.time() + 2
    while time.time() < deadline and interfaz.JOBS[-1]["estado"] == "en cola":
        time.sleep(0.01)

    job = interfaz.JOBS[-1]
    assert job["estado"] == "listo"
    assert job["path"] == "informe.md"
    assert recorded and recorded[-1]["job_id"] == job["job_id"]


def test_lanzar_records_exception_from_worker_as_fallo(monkeypatch):
    monkeypatch.setattr(interfaz, "JOBS", [])
    monkeypatch.setattr(interfaz, "_guardia_contenido", lambda tema: None)
    monkeypatch.setattr(interfaz, "_append_job_record", lambda job: None)

    def boom(*a, **k):
        raise RuntimeError("provider unreachable")
    monkeypatch.setattr(interfaz, "run_tema", boom)

    interfaz._lanzar("research", "tema con falla", None)
    deadline = time.time() + 2
    while time.time() < deadline and interfaz.JOBS[-1]["estado"] in ("en cola", "corriendo"):
        time.sleep(0.01)

    job = interfaz.JOBS[-1]
    assert job["estado"] == "FALLO"
    assert "provider unreachable" in job["error"]


# ---------------------------------------------------------------------------
# _reanudar_logic: reanudar un job PAUSADO, sin abrir un servidor HTTP
# ---------------------------------------------------------------------------

def _q(**kwargs):
    """Build a urllib.parse.parse_qs-shaped dict (values are lists)."""
    return {k: [v] for k, v in kwargs.items()}


def test_reanudar_logic_job_not_found(monkeypatch):
    monkeypatch.setattr(interfaz, "JOBS", [])
    code, payload = interfaz._reanudar_logic(_q(job_id="nope", accion="reintentar"))
    assert code == 404
    assert payload["ok"] is False


def test_reanudar_logic_job_not_paused(monkeypatch):
    monkeypatch.setattr(interfaz, "JOBS", [{"job_id": "j1", "estado": "corriendo"}])
    code, payload = interfaz._reanudar_logic(_q(job_id="j1", accion="reintentar"))
    assert code == 400
    assert "no esta PAUSADO" in payload["error"]


def test_reanudar_logic_invalid_accion(monkeypatch):
    monkeypatch.setattr(interfaz, "JOBS", [{"job_id": "j1", "estado": "PAUSADO"}])
    code, payload = interfaz._reanudar_logic(_q(job_id="j1", accion="volar"))
    assert code == 400
    assert payload["ok"] is False


def test_reanudar_logic_abortar_does_not_touch_real_event_log(monkeypatch):
    events = []
    monkeypatch.setattr(interfaz, "emitir_evento",
                        lambda *a, **k: events.append((a, k)))
    recorded = []
    monkeypatch.setattr(interfaz, "_append_job_record", recorded.append)
    jobs = [{"job_id": "j1", "estado": "PAUSADO"}]
    monkeypatch.setattr(interfaz, "JOBS", jobs)

    code, payload = interfaz._reanudar_logic(_q(job_id="j1", accion="abortar"))

    assert code == 200
    assert payload == {"ok": True, "estado": "abortado"}
    assert jobs[0]["estado"] == "abortado"
    assert events and events[0][0][:3] == ("research", "j1", "node_end")
    assert recorded and recorded[0]["estado"] == "abortado"


def test_reanudar_logic_invalid_checkpoint_reverts_to_paused(monkeypatch):
    def boom(*a, **k):
        raise ValueError("checkpoint invalido")
    monkeypatch.setattr(interfaz.pausa, "aplicar_accion", boom)
    jobs = [{"job_id": "j1", "estado": "PAUSADO", "checkpoint": "cp.json"}]
    monkeypatch.setattr(interfaz, "JOBS", jobs)

    code, payload = interfaz._reanudar_logic(
        _q(job_id="j1", accion="editar", texto="nuevo texto"))

    assert code == 400
    assert payload["ok"] is False
    assert jobs[0]["estado"] == "PAUSADO"


def test_reanudar_logic_checkpoint_io_error_reverts_to_paused(monkeypatch):
    def boom(*a, **k):
        raise OSError("disco lleno")
    monkeypatch.setattr(interfaz.pausa, "aplicar_accion", boom)
    jobs = [{"job_id": "j1", "estado": "PAUSADO", "checkpoint": "cp.json"}]
    monkeypatch.setattr(interfaz, "JOBS", jobs)

    code, payload = interfaz._reanudar_logic(_q(job_id="j1", accion="saltar"))

    assert code == 500
    assert jobs[0]["estado"] == "PAUSADO"


def test_reanudar_logic_success_relaunches_and_applies_result(monkeypatch):
    monkeypatch.setattr(interfaz.pausa, "aplicar_accion",
                        lambda *a, **k: {"current": "editado"})
    recorded = []
    monkeypatch.setattr(interfaz, "_append_job_record", recorded.append)
    finished = threading.Event()

    def fake_run_tema(*a, **k):
        return {"ok": True, "path": "/x/reanudado.md"}

    monkeypatch.setattr(interfaz, "run_tema", fake_run_tema)
    orig_cerrar = interfaz._cerrar_job

    def cerrar_and_signal(job, t0):
        orig_cerrar(job, t0)
        finished.set()
    monkeypatch.setattr(interfaz, "_cerrar_job", cerrar_and_signal)

    jobs = [{"job_id": "j1", "estado": "PAUSADO", "checkpoint": "cp.json",
            "modo": "research", "tema": "tema x"}]
    monkeypatch.setattr(interfaz, "JOBS", jobs)

    code, payload = interfaz._reanudar_logic(_q(job_id="j1", accion="reintentar"))
    assert code == 200
    assert payload["estado"] == "corriendo"
    assert finished.wait(timeout=2)
    assert jobs[0]["estado"] == "listo"
    assert jobs[0]["path"] == "reanudado.md"


# ---------------------------------------------------------------------------
# _run_intake_request: validaciones que nunca llegan a tocar disco de verdad
# ---------------------------------------------------------------------------

def test_run_intake_request_rejects_non_dict_body():
    payload, code = interfaz._run_intake_request("no soy un dict")
    assert code == 400


def test_run_intake_request_rejects_both_sources_given():
    payload, code = interfaz._run_intake_request(
        {"source_index": "a", "source_root": "b"})
    assert code == 400
    assert "no ambos" in payload["error"]


def test_run_intake_request_rejects_neither_source_given():
    payload, code = interfaz._run_intake_request({})
    assert code == 400


def test_run_intake_request_rejects_forbidden_root_names():
    payload, code = interfaz._run_intake_request(
        {"source_root": "/home/mak/PortableSSD"})
    assert code == 400
    assert "indice SSD" in payload["error"]


def test_run_intake_request_rejects_source_index_outside_allowed_roots(tmp_path):
    outside = tmp_path / "evil.sqlite"
    outside.write_text("x", encoding="utf-8")
    payload, code = interfaz._run_intake_request(
        {"source_index": str(outside)})
    assert code == 400
    assert "fuera de las raices" in payload["error"]


def test_run_intake_request_rejects_source_root_not_a_directory():
    payload, code = interfaz._run_intake_request(
        {"source_root": "/home/mak/este-directorio-no-existe-para-el-test"})
    assert code == 400
    assert "carpeta local" in payload["error"]


def test_run_intake_request_rejects_existing_intake_without_reprocessing(
        tmp_path, monkeypatch):
    monkeypatch.setattr(interfaz, "INTAKE_ROOT", tmp_path)
    # Pre-seed the marker the function checks for, instead of calling it
    # twice: a first call would fall through to the real intake tooling.
    output_dir = tmp_path / "api-flujo-repo-smoke-test"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "intake.sqlite").write_text("x", encoding="utf-8")

    payload, code = interfaz._run_intake_request(
        {"source_root": str(REPO_ROOT), "project_path": "flujo-repo-smoke-test"})
    assert code == 409
    assert payload["ok"] is False


# ---------------------------------------------------------------------------
# _organos: frutos.json y material.jsonl, cada uno con su propio fail-safe
# ---------------------------------------------------------------------------

def test_organos_counts_only_fructifero_entries_and_ignores_bad_json(
        tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(interfaz, "_procesos_vivos", lambda: "")
    for d in interfaz.DIRS.values():
        Path(d).mkdir(parents=True, exist_ok=True)
    plataforma = tmp_path / "plataforma"
    plataforma.mkdir(parents=True, exist_ok=True)
    (plataforma / "fructificaciones.json").write_text(json.dumps({
        "a": {"estatuto": "fructifero"},
        "b": {"estatuto": "latente"},
        "c": "no es un dict",
    }), encoding="utf-8")
    (plataforma / "material.jsonl").write_text(
        json.dumps({"estado": "pendiente"}) + "\n"
        "linea rota, no es json\n"
        + json.dumps({"estado": "despachada"}) + "\n",
        encoding="utf-8")

    data = interfaz._organos()["organos"]

    assert next(x for x in data if x["id"] == "emerge")["cantidad"] == 1
    assert next(x for x in data if x["id"] == "plataforma")["cantidad"] == 1


def test_organos_survives_missing_platform_files(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(interfaz, "_procesos_vivos", lambda: "")
    for d in interfaz.DIRS.values():
        Path(d).mkdir(parents=True, exist_ok=True)
    data = interfaz._organos()["organos"]
    assert next(x for x in data if x["id"] == "emerge")["cantidad"] == 0
    assert next(x for x in data if x["id"] == "plataforma")["cantidad"] == 0


# ---------------------------------------------------------------------------
# _path_is_under: a symlink loop must not break the root check
# ---------------------------------------------------------------------------

def test_path_is_under_raises_on_symlink_loop_instead_of_returning_false(tmp_path):
    """DEFECT, left unfixed here (cultura/ is out of this pass's zone):
    _path_is_under() only catches OSError, but on this Python (3.11)
    pathlib's Path.resolve() wraps an ELOOP into a bare RuntimeError, not
    an OSError. A source_index/source_root value that loops back on itself
    reaches do_POST's /api/intake with no surrounding try/except around
    _run_intake_request(), so instead of the clean 400 every other invalid
    path gets, the request crashes. Pinned here so a future fix changes
    this deliberately instead of by accident."""
    looped = tmp_path / "loop_a"
    other = tmp_path / "loop_b"
    looped.symlink_to(other)
    other.symlink_to(looped)
    with pytest.raises(RuntimeError, match="Symlink loop"):
        interfaz._path_is_under(looped, [tmp_path])


def test_path_is_under_returns_false_on_oserror_from_resolve(monkeypatch):
    class _FakePath:
        def __init__(self, *_a, **_k):
            pass

        def resolve(self):
            raise OSError("nombre de archivo demasiado largo")
    monkeypatch.setattr(interfaz, "Path", _FakePath)
    assert interfaz._path_is_under("cualquier/cosa", ["root"]) is False


# ---------------------------------------------------------------------------
# _lanzar: the declared work_contract travels with the job
# ---------------------------------------------------------------------------

def test_lanzar_attaches_work_contract_to_the_job(monkeypatch):
    monkeypatch.setattr(interfaz, "JOBS", [])
    monkeypatch.setattr(interfaz, "_guardia_contenido", lambda tema: None)
    monkeypatch.setattr(interfaz, "_append_job_record", lambda job: None)
    monkeypatch.setattr(interfaz, "run_tema", lambda *a, **k: {"ok": True, "path": ""})

    interfaz._lanzar("research", "tema", None, work_contract={"format": "informe"})

    assert interfaz.JOBS[-1]["work_contract"] == {"format": "informe"}


# ---------------------------------------------------------------------------
# _append_job_record: un fallo de disco nunca debe tumbar el request
# ---------------------------------------------------------------------------

def test_append_job_record_swallows_oserror(tmp_path, monkeypatch):
    # JOBS_FILE pointing at a directory makes open(..., "a") raise OSError.
    directory_as_file = tmp_path / "jobs-is-actually-a-dir"
    directory_as_file.mkdir()
    monkeypatch.setattr(interfaz, "JOBS_FILE", str(directory_as_file))
    interfaz._append_job_record({"job_id": "x"})  # must not raise


# ---------------------------------------------------------------------------
# _load_workflow: a canvas node absent from the default is preserved
# ---------------------------------------------------------------------------

def test_load_workflow_keeps_unknown_custom_node_verbatim(tmp_path, monkeypatch):
    path = tmp_path / "workflow.json"
    path.write_text(json.dumps({
        "nodes": {"nodo_custom": {"x": 1, "y": 2, "tipo": "custom"}},
    }), encoding="utf-8")
    monkeypatch.setattr(interfaz, "WORKFLOW_FILE", str(path))
    wf = interfaz._load_workflow()
    assert wf["nodes"]["nodo_custom"] == {"x": 1, "y": 2, "tipo": "custom"}


# ---------------------------------------------------------------------------
# _reindexar_async: el reindex en background tambien puede fallar
# ---------------------------------------------------------------------------

def test_reindexar_async_logs_indexer_failure_without_raising(monkeypatch, capsys):
    fake_memoria = MagicMock()
    fake_memoria.indexar.side_effect = RuntimeError("index corrupto")
    monkeypatch.setitem(sys.modules, "memoria", fake_memoria)
    released = threading.Event()

    class _SignalingLock(_FakeLock):
        def release(self):
            released.set()
    monkeypatch.setattr(interfaz, "_REINDEX_LOCK", _SignalingLock(True))

    assert interfaz._reindexar_async() is True
    assert released.wait(timeout=2)
    err = capsys.readouterr().err
    assert "reindex error" in err


# ---------------------------------------------------------------------------
# _cerrar_job: the post-job reindex is opt-in and best-effort
# ---------------------------------------------------------------------------

def test_cerrar_job_reindex_after_job_failure_does_not_propagate(
        tmp_path, monkeypatch):
    monkeypatch.setattr(interfaz, "JOBS_FILE", str(tmp_path / "jobs.jsonl"))
    monkeypatch.setenv("MAK_REINDEX_AFTER_JOB", "1")

    def boom():
        raise RuntimeError("reindex ocupado")
    monkeypatch.setattr(interfaz, "_reindexar_async", boom)

    interfaz._cerrar_job({"job_id": "x", "estado": "listo"}, time.time())  # no raise


def test_cerrar_job_does_not_reindex_by_default(tmp_path, monkeypatch):
    monkeypatch.setattr(interfaz, "JOBS_FILE", str(tmp_path / "jobs.jsonl"))
    monkeypatch.delenv("MAK_REINDEX_AFTER_JOB", raising=False)
    calls = []
    monkeypatch.setattr(interfaz, "_reindexar_async", lambda: calls.append(1))
    interfaz._cerrar_job({"job_id": "x", "estado": "listo"}, time.time())
    assert calls == []


# ---------------------------------------------------------------------------
# _reanudar_logic: los dos best-effort restantes (evento de abortar, relanzar)
# ---------------------------------------------------------------------------

def test_reanudar_logic_abortar_survives_event_log_failure(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("disco de eventos no disponible")
    monkeypatch.setattr(interfaz, "emitir_evento", boom)
    monkeypatch.setattr(interfaz, "_append_job_record", lambda job: None)
    jobs = [{"job_id": "j1", "estado": "PAUSADO"}]
    monkeypatch.setattr(interfaz, "JOBS", jobs)

    code, payload = interfaz._reanudar_logic(_q(job_id="j1", accion="abortar"))

    assert code == 200
    assert payload == {"ok": True, "estado": "abortado"}


def test_reanudar_logic_relanzar_failure_marks_fallo(monkeypatch):
    monkeypatch.setattr(interfaz.pausa, "aplicar_accion",
                        lambda *a, **k: {"current": "x"})
    monkeypatch.setattr(interfaz, "_append_job_record", lambda job: None)
    finished = threading.Event()

    def boom(*a, **k):
        raise RuntimeError("proveedor no disponible")
    monkeypatch.setattr(interfaz, "run_tema", boom)

    orig_cerrar = interfaz._cerrar_job

    def cerrar_and_signal(job, t0):
        orig_cerrar(job, t0)
        finished.set()
    monkeypatch.setattr(interfaz, "_cerrar_job", cerrar_and_signal)

    jobs = [{"job_id": "j1", "estado": "PAUSADO", "checkpoint": "cp.json",
            "modo": "research", "tema": "tema x"}]
    monkeypatch.setattr(interfaz, "JOBS", jobs)

    code, payload = interfaz._reanudar_logic(_q(job_id="j1", accion="reintentar"))
    assert code == 200
    assert finished.wait(timeout=2)
    assert jobs[0]["estado"] == "FALLO"
    assert "proveedor no disponible" in jobs[0]["error"]
