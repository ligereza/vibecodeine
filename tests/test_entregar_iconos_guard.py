#!/usr/bin/env python3
"""tests/test_entregar_iconos_guard.py -- entregar.leer_jobs_listos() must
never let a `modo == "iconos"` job (a .svg piece) reach the path that later
compile()s the harvested piece as Python before opening a PR. The guard sits
right after the `estado != "listo"` filter, and is an explicit EXCLUSION
(not an inclusion list) so jobs from before the `modo` field existed keep
passing -- an inclusion list would silently drop them."""
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


def _setup(tmp_path, monkeypatch, jobs):
    jf = tmp_path / "jobs.jsonl"
    jf.write_text("\n".join(json.dumps(j, ensure_ascii=False) for j in jobs) + "\n",
                  encoding="utf-8")
    monkeypatch.setattr(entregar, "CODEX_JOBS", str(jf))
    monkeypatch.setattr(entregar, "PIEZAS_DIR", str(tmp_path / "piezas"))
    monkeypatch.setattr(entregar, "LOG", str(tmp_path / "entregar.log"))
    return jf


class TestGuardaIconosExcluyeDelCaminoDeCodigo:
    def test_job_iconos_se_excluye_y_el_de_generar_pasa(self, tmp_path, monkeypatch):
        jobs = [
            _job("j-icono", "j-icono.md", modo="iconos", smoke_ok=True),
            _job("j-codigo", "j-codigo.md", modo="generar", smoke_ok=True),
        ]
        _setup(tmp_path, monkeypatch, jobs)
        out = entregar.leer_jobs_listos()
        assert [j["job_id"] for j in out] == ["j-codigo"]

    def test_job_sin_campo_modo_sigue_pasando(self, tmp_path, monkeypatch):
        """Compatibilidad hacia atras: jobs anteriores al campo `modo` no lo
        traen en absoluto. Una lista de INCLUSION (solo dejar pasar modos
        conocidos) los habria descartado en silencio -- por eso el guard es
        una exclusion explicita de 'iconos', no una inclusion."""
        jobs = [_job("j-viejo", "j-viejo.md", smoke_ok=True)]
        _setup(tmp_path, monkeypatch, jobs)
        out = entregar.leer_jobs_listos()
        assert [j["job_id"] for j in out] == ["j-viejo"]

    def test_iconos_se_saltea_por_modo_no_por_smoke(self, tmp_path, monkeypatch, capsys):
        """Un job iconos con smoke_ok=True de todas formas se descarta, y el
        log debe decir POR QUE (modo iconos), no confundirse con un rechazo
        de smoke."""
        jobs = [_job("j-icono", "j-icono.md", modo="iconos", smoke_ok=True)]
        _setup(tmp_path, monkeypatch, jobs)
        out = entregar.leer_jobs_listos()
        assert out == []
        salida = capsys.readouterr().out
        assert "iconos" in salida
        assert "rechazado_smoke" not in salida
        assert "SKIP" in salida

    def test_iconos_no_se_beneficia_del_bypass_sin_smoke(self, tmp_path, monkeypatch):
        """--sin-smoke bypasea el gate de SMOKE, no el gate de MODO: un
        iconos sigue afuera del camino de entrega de codigo aunque se pida
        el bypass humano."""
        jobs = [_job("j-icono", "j-icono.md", modo="iconos", smoke_ok=False)]
        _setup(tmp_path, monkeypatch, jobs)
        out = entregar.leer_jobs_listos(bypass_smoke=True)
        assert out == []


class TestMutacionGuardIconos:
    """Mutation check: se comenta temporalmente el guard `modo == iconos` en
    entregar.py, se corre el primer test de esta clase, se confirma que se
    pone rojo (el .svg pasaria como si fuera codigo), y se restaura el
    archivo exacto. Documentado aca porque no se puede tocar el archivo de
    codigo como parte de la suite (regla del repo: solo tests/); la mutacion
    real se hizo a mano y se reporta en el mensaje de cierre, no queda
    codificada como test que edite entregar.py en disco."""

    def test_guard_referencia_el_string_literal_iconos(self):
        """Asercion barata sobre el propio codigo fuente: el guard debe
        seguir comparando literalmente contra 'iconos', para que si alguien
        lo reescribe mal (p.ej. compara contra 'icono' sin 's') el test de
        exclusion de arriba deje de coincidir con la intencion documentada."""
        src = Path(entregar.__file__).read_text(encoding="utf-8")
        assert '"iconos"' in src
        assert "modo iconos" in src


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
