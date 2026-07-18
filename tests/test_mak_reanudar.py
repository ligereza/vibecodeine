#!/usr/bin/env python3
"""test_mak_reanudar.py -- tests para la UI de reanudar (pausa-en-error, mitad
UI). interfaz.py importa worker.py -> fcntl (Linux-only): las clases que
requieren importarlo se gatean con pytest.importorskip("fcntl") para que
corran en CI (ubuntu) y se salteen limpio en Windows."""
import sys
from pathlib import Path

import pytest

TEST_DIR = Path(__file__).parent
PROYECTO_DIR = TEST_DIR.parent
MAK_PLATAFORMA = PROYECTO_DIR / "cultura" / "mak_plataforma"
MAK_RESEARCH = PROYECTO_DIR / "cultura" / "mak_research"

sys.path.insert(0, str(MAK_PLATAFORMA))
import hub  # noqa: E402 -- stdlib-only, importable en Windows

INTERFAZ_SRC = (MAK_RESEARCH / "interfaz.py").read_text(encoding="utf-8")


# ── hub.py: _norm y el conteo de la guardia (sin fcntl, corre en Windows) ──

class TestHubNorm:
    def test_norm_pausado_prefix(self):
        j = {"tema": "x", "estado": "PAUSADO", "error": "sin proveedores"}
        e = hub._norm(j, "research")
        assert e["rz"].startswith("pausado: ")
        assert "sin proveedores" in e["rz"]

    def test_norm_pausado_sin_error_usa_default(self):
        j = {"tema": "x", "estado": "PAUSADO", "error": ""}
        e = hub._norm(j, "research")
        assert e["rz"] == "pausado: esperando humano"

    def test_norm_abortado(self):
        j = {"tema": "x", "estado": "abortado"}
        e = hub._norm(j, "research")
        assert e["rz"] == "abortado"

    def test_norm_fallo_unchanged(self):
        j = {"tema": "x", "estado": "FALLO", "error": "boom"}
        e = hub._norm(j, "research")
        assert e["rz"] == "fallo: boom"

    def test_norm_bloqueado_unchanged(self):
        j = {"tema": "x", "estado": "BLOQUEADO", "error": "guardia: nel"}
        e = hub._norm(j, "research")
        assert e["rz"] == "guardia: nel"

    def test_norm_listo_passthrough(self):
        j = {"tema": "x", "estado": "listo"}
        e = hub._norm(j, "research")
        assert e["rz"] == ""
        assert e["estado"] == "listo"

    def test_actividad_pasaron_excluye_pausado_y_abortado(self, monkeypatch):
        evs = [
            {"depto": "research", "texto": "a", "estado": "listo", "t": "3", "seg": 1, "rz": ""},
            {"depto": "research", "texto": "b", "estado": "PAUSADO", "t": "2", "seg": 1, "rz": "pausado: x"},
            {"depto": "research", "texto": "c", "estado": "abortado", "t": "1", "seg": 1, "rz": "abortado"},
            {"depto": "research", "texto": "d", "estado": "BLOQUEADO", "t": "0", "seg": 1, "rz": "guardia"},
        ]
        monkeypatch.setattr(hub, "_jobs_depto", lambda port, jsonl, depto: evs if depto == "research" else [])
        r = hub._actividad()
        assert r["guardia"]["bloqueados"] == 1
        # 4 eventos: 1 bloqueado, 1 pausado, 1 abortado, 1 listo -> solo "listo" pasa
        assert r["guardia"]["pasaron"] == 1


# ── interfaz.py fuente: markers de UI presentes (string check, sin importar) ──

class TestInterfazFuenteMarkers:
    def test_endpoint_reanudar_presente(self):
        assert '"/api/reanudar"' in INTERFAZ_SRC

    def test_css_job_dot_pausado(self):
        assert ".job-dot.pausado{background:#e0a458}" in INTERFAZ_SRC

    def test_css_job_dot_abortado(self):
        assert ".job-dot.abortado{background:#8a8578}" in INTERFAZ_SRC

    def test_js_funcion_reanudar_presente(self):
        assert "function reanudar(jobIdEnc, accion)" in INTERFAZ_SRC

    def test_cuatro_acciones_en_ambos_render_paths(self):
        # el marcador 'reanudar(...reintentar...' debe aparecer 2 veces:
        # una en el render server-side (jobs_html) y otra en el JS (refreshJobs)
        for accion in ("reintentar", "editar", "saltar", "abortar"):
            marcador = "\\',\\'%s\\');return false;" % accion
            assert INTERFAZ_SRC.count(marcador) == 2, (
                "accion %r no aparece 2 veces (server + JS)" % accion
            )


# ── interfaz.py logica: requiere importar (fcntl, solo Linux/CI) ──
# ojo: NO usar pytest.importorskip a nivel de modulo -- eso saltea TODO el
# archivo (incluidos los tests de hub.py y los de fuente de arriba). El
# guard va por clase, asi en Windows solo se saltean estas 3 clases.

try:
    import fcntl  # noqa: F401
    sys.path.insert(0, str(MAK_RESEARCH))
    import interfaz
    HAY_FCNTL = True
except ImportError:
    HAY_FCNTL = False

requiere_fcntl = pytest.mark.skipif(not HAY_FCNTL, reason="interfaz.py importa worker->fcntl (Linux-only)")


@requiere_fcntl
class TestAplicarResultadoJob:
    def test_listo(self):
        job = {}
        interfaz._aplicar_resultado_job(job, {"ok": True, "path": "/x/y/out.md"})
        assert job["estado"] == "listo"
        assert job["path"] == "out.md"

    def test_fallo(self):
        job = {}
        interfaz._aplicar_resultado_job(job, {"ok": False, "tail": "traceback boom"})
        assert job["estado"] == "FALLO"
        assert job["error"] == "traceback boom"

    def test_pausado(self):
        job = {}
        r = {"ok": False, "pausado": True, "checkpoint": "/home/mak/research/checkpoints/j1.json",
             "path": "", "tail": "sin proveedores disponibles"}
        interfaz._aplicar_resultado_job(job, r)
        assert job["estado"] == "PAUSADO"
        assert job["checkpoint"] == r["checkpoint"]
        assert job["error"] == "sin proveedores disponibles"


@requiere_fcntl
class TestCerrarJob:
    def test_escribe_jobs_file_y_calcula_ms(self, tmp_path, monkeypatch):
        jf = tmp_path / "jobs.jsonl"
        monkeypatch.setattr(interfaz, "JOBS_FILE", str(jf))
        monkeypatch.setattr(interfaz, "_reindexar_async", lambda *a, **k: None)
        job = {"job_id": "j1", "estado": "listo"}
        interfaz._cerrar_job(job, __import__("time").time())
        assert "ms" in job
        assert jf.exists()
        contenido = jf.read_text(encoding="utf-8")
        assert '"job_id": "j1"' in contenido


@requiere_fcntl
class TestReanudarLogic:
    def _fake_thread(self, monkeypatch):
        """threading.Thread sincronico: corre el target al llamar start()."""
        class HiloFalso:
            def __init__(self, target=None, daemon=None):
                self._target = target

            def start(self):
                self._target()

        monkeypatch.setattr(interfaz.threading, "Thread", HiloFalso)

    def _job_pausado(self, monkeypatch, checkpoint="/tmp/cp.json"):
        job = {"job_id": "j1", "estado": "PAUSADO", "modo": "research",
               "tema": "algo", "checkpoint": checkpoint, "t": "10:00:00"}
        monkeypatch.setattr(interfaz, "JOBS", [job])
        return job

    def test_job_no_encontrado(self):
        code, payload = interfaz._reanudar_logic({"job_id": ["nope"], "accion": ["reintentar"]})
        assert code == 404
        assert payload["ok"] is False

    def test_job_no_pausado(self, monkeypatch):
        job = {"job_id": "j1", "estado": "corriendo"}
        monkeypatch.setattr(interfaz, "JOBS", [job])
        code, payload = interfaz._reanudar_logic({"job_id": ["j1"], "accion": ["reintentar"]})
        assert code == 400
        assert "no esta PAUSADO" in payload["error"]

    def test_accion_invalida(self, monkeypatch):
        self._job_pausado(monkeypatch)
        code, payload = interfaz._reanudar_logic({"job_id": ["j1"], "accion": ["bailar"]})
        assert code == 400
        assert payload["ok"] is False

    def test_abortar(self, monkeypatch, tmp_path):
        job = self._job_pausado(monkeypatch)
        jf = tmp_path / "jobs.jsonl"
        monkeypatch.setattr(interfaz, "JOBS_FILE", str(jf))
        eventos = []
        monkeypatch.setattr(interfaz, "emitir_evento", lambda *a, **k: eventos.append((a, k)))
        code, payload = interfaz._reanudar_logic({"job_id": ["j1"], "accion": ["abortar"]})
        assert code == 200
        assert payload == {"ok": True, "estado": "abortado"}
        assert job["estado"] == "abortado"
        assert eventos and eventos[0][0][2] == "node_end"
        assert jf.exists()

    def test_reintentar_relanza_y_actualiza_job(self, monkeypatch, tmp_path):
        job = self._job_pausado(monkeypatch)
        self._fake_thread(monkeypatch)
        jf = tmp_path / "jobs.jsonl"
        monkeypatch.setattr(interfaz, "JOBS_FILE", str(jf))
        monkeypatch.setattr(interfaz, "_reindexar_async", lambda *a, **k: None)

        aplicado = {}
        monkeypatch.setattr(interfaz.pausa, "aplicar_accion",
                            lambda path, accion, texto="": aplicado.setdefault("ok", (path, accion, texto)))

        llamado = {}
        def fake_run_tema(modo, tema, ntfy=True, job_id=None, extra=None):
            llamado["args"] = (modo, tema, ntfy, job_id, extra)
            return {"ok": True, "path": "/x/out.md"}
        monkeypatch.setattr(interfaz, "run_tema", fake_run_tema)

        code, payload = interfaz._reanudar_logic({"job_id": ["j1"], "accion": ["reintentar"]})
        assert code == 200
        assert payload == {"ok": True, "estado": "corriendo"}
        # el hilo (sincronico via HiloFalso) ya corrio y dejo el job en listo
        assert job["estado"] == "listo"
        assert job["path"] == "out.md"
        assert llamado["args"][4] == ["--resume", "/tmp/cp.json"]
        assert aplicado["ok"] == ("/tmp/cp.json", "reintentar", "")

    def test_editar_pasa_texto_a_aplicar_accion(self, monkeypatch, tmp_path):
        self._job_pausado(monkeypatch)
        self._fake_thread(monkeypatch)
        jf = tmp_path / "jobs.jsonl"
        monkeypatch.setattr(interfaz, "JOBS_FILE", str(jf))
        monkeypatch.setattr(interfaz, "_reindexar_async", lambda *a, **k: None)
        monkeypatch.setattr(interfaz, "run_tema", lambda *a, **k: {"ok": True, "path": ""})

        recibido = {}
        monkeypatch.setattr(interfaz.pausa, "aplicar_accion",
                            lambda path, accion, texto="": recibido.setdefault("v", (accion, texto)))

        code, payload = interfaz._reanudar_logic(
            {"job_id": ["j1"], "accion": ["editar"], "texto": ["consulta nueva"]})
        assert code == 200
        assert recibido["v"] == ("editar", "consulta nueva")

    def test_aplicar_accion_valueerror_es_400(self, monkeypatch):
        self._job_pausado(monkeypatch)

        def revienta(path, accion, texto=""):
            raise ValueError("accion desconocida")
        monkeypatch.setattr(interfaz.pausa, "aplicar_accion", revienta)

        code, payload = interfaz._reanudar_logic({"job_id": ["j1"], "accion": ["saltar"]})
        assert code == 400
        assert payload["ok"] is False

    def test_relanzamiento_pausa_de_nuevo(self, monkeypatch, tmp_path):
        """Si run_tema vuelve a pausar (segundo checkpoint), el job queda
        PAUSADO otra vez -- no se pierde el estado intermedio."""
        job = self._job_pausado(monkeypatch)
        self._fake_thread(monkeypatch)
        jf = tmp_path / "jobs.jsonl"
        monkeypatch.setattr(interfaz, "JOBS_FILE", str(jf))
        monkeypatch.setattr(interfaz, "_reindexar_async", lambda *a, **k: None)
        monkeypatch.setattr(interfaz.pausa, "aplicar_accion", lambda *a, **k: None)
        monkeypatch.setattr(interfaz, "run_tema", lambda *a, **k: {
            "ok": False, "pausado": True, "checkpoint": "/tmp/cp2.json",
            "path": "", "tail": "otra vez sin proveedores",
        })

        code, payload = interfaz._reanudar_logic({"job_id": ["j1"], "accion": ["reintentar"]})
        assert code == 200
        assert job["estado"] == "PAUSADO"
        assert job["checkpoint"] == "/tmp/cp2.json"
