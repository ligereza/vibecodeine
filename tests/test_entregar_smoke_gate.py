#!/usr/bin/env python3
"""test_entregar_smoke_gate.py -- tests para el gate de smoke-run de
entregar.py (F2b/#139): leer_jobs_listos() debe filtrar por smoke_ok
(enriquecido desde el meta JSON de la pieza .md, ver leer_smoke_meta) y
--sin-smoke debe poder bypasear ese filtro."""
import json
import sys
from pathlib import Path

import pytest

TEST_DIR = Path(__file__).parent
PROYECTO_DIR = TEST_DIR.parent
MAK_PLATAFORMA = PROYECTO_DIR / "cultura" / "mak_plataforma"

sys.path.insert(0, str(MAK_PLATAFORMA))
import entregar  # noqa: E402 -- stdlib-only, importable en Windows


def _job(job_id, path, estado="listo", error="", pedido="pedido", **extra):
    j = {"job_id": job_id, "path": path, "estado": estado, "error": error,
         "pedido": pedido}
    j.update(extra)
    return j


def _escribir_jobs(tmp_path, jobs):
    jf = tmp_path / "jobs.jsonl"
    jf.write_text("\n".join(json.dumps(j, ensure_ascii=False) for j in jobs) + "\n",
                 encoding="utf-8")
    return jf


def _escribir_pieza_md(piezas_dir, nombre_md, meta=None, meta_texto_plano=None):
    """Escribe una pieza .md minima bajo piezas_dir con el meta al final,
    igual que codex_lib.guardar_pieza (meta JSON) o agente_libre.py (meta
    de texto plano)."""
    piezas_dir.mkdir(parents=True, exist_ok=True)
    contenido = "# Codex: pedido\n\nSandbox: OK.\n\n```python\nprint('x')\n```\n\n---\n"
    if meta_texto_plano is not None:
        contenido += "meta: %s\n" % meta_texto_plano
    else:
        contenido += "meta: %s\n" % json.dumps(meta or {}, ensure_ascii=False)
    (piezas_dir / nombre_md).write_text(contenido, encoding="utf-8")


class TestLeerSmokeMeta:
    def test_lee_meta_json_valido(self, tmp_path, monkeypatch):
        monkeypatch.setattr(entregar, "PIEZAS_DIR", str(tmp_path))
        _escribir_pieza_md(tmp_path, "p1.md", meta={"smoke_ok": True})
        assert entregar.leer_smoke_meta("p1.md") == {"smoke_ok": True}

    def test_archivo_inexistente_devuelve_vacio(self, tmp_path, monkeypatch):
        monkeypatch.setattr(entregar, "PIEZAS_DIR", str(tmp_path))
        assert entregar.leer_smoke_meta("no-existe.md") == {}

    def test_meta_texto_plano_no_json_devuelve_vacio(self, tmp_path, monkeypatch):
        """agente_libre.py escribe meta como texto plano (no json) -- debe
        tratarse como ausente, no reventar."""
        monkeypatch.setattr(entregar, "PIEZAS_DIR", str(tmp_path))
        _escribir_pieza_md(tmp_path, "p2.md",
                          meta_texto_plano="plan_por=x codigo_por=y ms=10")
        assert entregar.leer_smoke_meta("p2.md") == {}

    def test_toma_la_ultima_marca_no_la_primera(self, tmp_path, monkeypatch):
        """Si el codigo generado contiene la substring 'meta: ' en un
        comentario, rfind() debe seguir encontrando el meta REAL (el
        ultimo bloque del archivo), no confundirse con el primero."""
        monkeypatch.setattr(entregar, "PIEZAS_DIR", str(tmp_path))
        tmp_path.mkdir(parents=True, exist_ok=True)
        contenido = (
            "# Codex: pedido\n\nSandbox: OK.\n\n"
            "```python\n# nota: meta: esto no es el meta real\nprint('x')\n```\n\n"
            "---\nmeta: %s\n" % json.dumps({"smoke_ok": False, "smoke_stderr_tail": "boom"})
        )
        (tmp_path / "p3.md").write_text(contenido, encoding="utf-8")
        meta = entregar.leer_smoke_meta("p3.md")
        assert meta == {"smoke_ok": False, "smoke_stderr_tail": "boom"}


class TestLeerJobsListosSmokeGate:
    def _setup(self, tmp_path, monkeypatch, jobs, piezas=()):
        jf = _escribir_jobs(tmp_path, jobs)
        monkeypatch.setattr(entregar, "CODEX_JOBS", str(jf))
        piezas_dir = tmp_path / "piezas"
        monkeypatch.setattr(entregar, "PIEZAS_DIR", str(piezas_dir))
        for nombre, meta in piezas:
            _escribir_pieza_md(piezas_dir, nombre, meta=meta)
        # LOG bajo tmp_path para no ensuciar ~/plataforma/logs en la maquina real
        monkeypatch.setattr(entregar, "LOG", str(tmp_path / "entregar.log"))
        return jf

    def test_smoke_ok_true_en_jsonl_directo_pasa(self, tmp_path, monkeypatch):
        jobs = [_job("j1", "j1.md", smoke_ok=True)]
        self._setup(tmp_path, monkeypatch, jobs)
        out = entregar.leer_jobs_listos()
        assert [j["job_id"] for j in out] == ["j1"]

    def test_smoke_ok_false_en_jsonl_directo_se_rechaza(self, tmp_path, monkeypatch):
        jobs = [_job("j1", "j1.md", smoke_ok=False, smoke_stderr_tail="AssertionError")]
        self._setup(tmp_path, monkeypatch, jobs)
        out = entregar.leer_jobs_listos()
        assert out == []

    def test_smoke_ok_true_desde_meta_de_pieza(self, tmp_path, monkeypatch):
        jobs = [_job("j1", "j1.md")]
        self._setup(tmp_path, monkeypatch, jobs,
                   piezas=[("j1.md", {"smoke_ok": True})])
        out = entregar.leer_jobs_listos()
        assert [j["job_id"] for j in out] == ["j1"]
        assert out[0]["smoke_ok"] is True

    def test_smoke_ok_false_desde_meta_de_pieza_se_rechaza(self, tmp_path, monkeypatch):
        jobs = [_job("j1", "j1.md")]
        self._setup(tmp_path, monkeypatch, jobs,
                   piezas=[("j1.md", {"smoke_ok": False,
                                       "smoke_stderr_tail": "rc=1"})])
        out = entregar.leer_jobs_listos()
        assert out == []

    def test_job_viejo_sin_smoke_ok_pasa_con_warning(self, tmp_path, monkeypatch):
        """Sin meta en absoluto (pieza vieja o modo sin sandbox) -> pasa."""
        jobs = [_job("j1", "j1.md")]
        self._setup(tmp_path, monkeypatch, jobs)  # sin pieza .md -> meta {}
        out = entregar.leer_jobs_listos()
        assert [j["job_id"] for j in out] == ["j1"]
        assert out[0].get("smoke_ok") is None

    def test_meta_texto_plano_mejora_libre_pasa_con_warning(self, tmp_path, monkeypatch):
        """Piezas de agente_libre.py (meta texto plano, nunca corren
        sandbox por diseno) no tienen smoke_ok -> pasan igual."""
        jf = _escribir_jobs(tmp_path, [_job("j1", "j1.md", modo="mejora-libre")])
        monkeypatch.setattr(entregar, "CODEX_JOBS", str(jf))
        piezas_dir = tmp_path / "piezas"
        monkeypatch.setattr(entregar, "PIEZAS_DIR", str(piezas_dir))
        monkeypatch.setattr(entregar, "LOG", str(tmp_path / "entregar.log"))
        _escribir_pieza_md(piezas_dir, "j1.md",
                          meta_texto_plano="plan_por=x codigo_por=y ms=10")
        out = entregar.leer_jobs_listos()
        assert [j["job_id"] for j in out] == ["j1"]

    def test_mezcla_true_false_ausente(self, tmp_path, monkeypatch):
        jobs = [
            _job("j-true", "j-true.md", smoke_ok=True),
            _job("j-false", "j-false.md", smoke_ok=False, smoke_stderr_tail="boom"),
            _job("j-ausente", "j-ausente.md"),
            _job("j-noestado", "j-noestado.md", estado="FALLO"),
            _job("j-conerror", "j-conerror.md", smoke_ok=True, error="algo paso"),
        ]
        self._setup(tmp_path, monkeypatch, jobs)
        out = entregar.leer_jobs_listos()
        ids = sorted(j["job_id"] for j in out)
        assert ids == ["j-ausente", "j-true"]

    def test_bypass_sin_smoke_incluye_los_rechazados(self, tmp_path, monkeypatch):
        jobs = [
            _job("j-true", "j-true.md", smoke_ok=True),
            _job("j-false", "j-false.md", smoke_ok=False, smoke_stderr_tail="boom"),
        ]
        self._setup(tmp_path, monkeypatch, jobs)
        out = entregar.leer_jobs_listos(bypass_smoke=True)
        ids = sorted(j["job_id"] for j in out)
        assert ids == ["j-false", "j-true"]

    def test_rechazado_marca_estado_en_memoria(self, tmp_path, monkeypatch):
        """El job rechazado por smoke queda marcado 'rechazado_smoke' en el
        dict en memoria (no se reescribe jobs.jsonl -- ledger append-only)."""
        jobs = [_job("j1", "j1.md", smoke_ok=False, smoke_stderr_tail="boom")]
        jf = self._setup(tmp_path, monkeypatch, jobs)
        entregar.leer_jobs_listos()
        # jobs.jsonl NO se modifico
        cruda = jf.read_text(encoding="utf-8")
        assert '"estado": "listo"' in cruda
        assert "rechazado_smoke" not in cruda

    def test_sin_job_id_o_path_se_ignora(self, tmp_path, monkeypatch):
        jobs = [
            {"estado": "listo", "path": "x.md", "error": ""},  # sin job_id
            {"estado": "listo", "job_id": "j2", "error": ""},  # sin path
        ]
        self._setup(tmp_path, monkeypatch, jobs)
        assert entregar.leer_jobs_listos() == []

    def test_linea_corrupta_se_ignora(self, tmp_path, monkeypatch):
        jf = tmp_path / "jobs.jsonl"
        jf.write_text('{"job_id":"j1","path":"j1.md","estado":"listo","error":"",'
                     '"smoke_ok":true}\nno es json\n', encoding="utf-8")
        monkeypatch.setattr(entregar, "CODEX_JOBS", str(jf))
        monkeypatch.setattr(entregar, "PIEZAS_DIR", str(tmp_path / "piezas"))
        monkeypatch.setattr(entregar, "LOG", str(tmp_path / "entregar.log"))
        out = entregar.leer_jobs_listos()
        assert [j["job_id"] for j in out] == ["j1"]


class TestRamaBase:
    """Topologia de ramas (CLAUDE.md): MAK entrega PRs contra 'mejoras',
    nunca contra main. entregar_una() debe usar RAMA_BASE, no un literal
    'main', tanto para el checkout como para gh pr create --base."""

    def test_constante_rama_base_es_mejoras(self):
        assert entregar.RAMA_BASE == "mejoras"

    def test_checkout_y_pr_create_usan_rama_base(self, tmp_path, monkeypatch):
        monkeypatch.setattr(entregar, "REPO", str(tmp_path))
        monkeypatch.setattr(entregar, "LOG", str(tmp_path / "entregar.log"))

        llamadas_git = []

        def fake_git(*args, check=True):
            llamadas_git.append(args)
            return None

        llamadas_gh = {}

        class FakeCompleted:
            returncode = 0
            stdout = "https://github.com/ligereza/vibecodeine/pull/999\n"
            stderr = ""

        def fake_run(cmd, cwd=None, capture_output=None, text=None):
            llamadas_gh["cmd"] = cmd
            return FakeCompleted()

        monkeypatch.setattr(entregar, "git", fake_git)
        monkeypatch.setattr(entregar.subprocess, "run", fake_run)

        job = {"job_id": "20260101-000000-abc123", "path": "20260101-000000-abc123.md",
              "pedido": "pedido de prueba"}
        monkeypatch.setattr(entregar, "extraer_codigo",
                            lambda md_path: ("print('x')\n", "fake.py"))

        res = entregar.entregar_una(job, dry_run=False)

        assert res == "ok"
        checkout = next(c for c in llamadas_git if c[0] == "checkout")
        assert checkout[3] == "origin/%s" % entregar.RAMA_BASE
        assert "origin/main" not in checkout

        gh_cmd = llamadas_gh["cmd"]
        i = gh_cmd.index("--base")
        assert gh_cmd[i + 1] == entregar.RAMA_BASE
        assert "main" not in gh_cmd


class TestMainSinSmokeFlag:
    def test_main_pasa_bypass_a_leer_jobs_listos(self, tmp_path, monkeypatch):
        """--sin-smoke debe propagarse a leer_jobs_listos(bypass_smoke=True)."""
        monkeypatch.setattr(entregar, "CODEX_JOBS", str(tmp_path / "jobs.jsonl"))
        monkeypatch.setattr(entregar, "STATE", str(tmp_path / "codex_delivered.json"))
        monkeypatch.setattr(entregar, "LOG", str(tmp_path / "entregar.log"))
        (tmp_path / "jobs.jsonl").write_text("", encoding="utf-8")

        recibido = {}

        def fake_leer_jobs_listos(bypass_smoke=False):
            recibido["bypass_smoke"] = bypass_smoke
            return []

        monkeypatch.setattr(entregar, "leer_jobs_listos", fake_leer_jobs_listos)
        monkeypatch.setattr(sys, "argv", ["entregar.py", "--sin-smoke"])
        entregar.main()
        assert recibido["bypass_smoke"] is True

    def test_main_default_no_bypass(self, tmp_path, monkeypatch):
        monkeypatch.setattr(entregar, "CODEX_JOBS", str(tmp_path / "jobs.jsonl"))
        monkeypatch.setattr(entregar, "STATE", str(tmp_path / "codex_delivered.json"))
        monkeypatch.setattr(entregar, "LOG", str(tmp_path / "entregar.log"))
        (tmp_path / "jobs.jsonl").write_text("", encoding="utf-8")

        recibido = {}

        def fake_leer_jobs_listos(bypass_smoke=False):
            recibido["bypass_smoke"] = bypass_smoke
            return []

        monkeypatch.setattr(entregar, "leer_jobs_listos", fake_leer_jobs_listos)
        monkeypatch.setattr(sys, "argv", ["entregar.py"])
        entregar.main()
        assert recibido["bypass_smoke"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
