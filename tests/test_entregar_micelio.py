#!/usr/bin/env python3
"""tests/test_entregar_micelio.py -- pure-logic tests for
cultura/mak_plataforma/entregar_micelio.py, the box-side script that
pushes the micelio's measured graph into the repo as a PR (2026-08-01),
mirroring entregar.py's proven git/gh pattern.

No network, no git, no gh: every path exercised here returns before
main() touches REPO (unreachable micelio and 0-vinculos both exit early;
--dry-run stops right after building the payload). That mirrors the
convention test_entregar_smoke_gate.py already uses for entregar.py's
own pure helpers.
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "cultura" / "mak_plataforma"))
import entregar_micelio as EM  # noqa: E402


@pytest.fixture(autouse=True)
def _isolated_log(tmp_path, monkeypatch):
    """Point LOG at tmp_path so the suite never writes MAK's production log.

    Same convention as tests/test_entregar_smoke_gate.py:89. Without it the
    three tests that call EM.main() append to
    /home/mak/plataforma/logs/entregar_micelio.log. Measured 2026-08-28: one
    run added 361 bytes there, and the lines it left read "simulated: box
    unreachable", which is indistinguishable from a real outage.

    This matters more than it looks. The MAK organism has been paused since
    2026-08-14 and those logs are the evidence of what ran and when. A test
    writing into them destroys the evidence. See docs/MAK_ORGANISMO.md.
    """
    monkeypatch.setattr(EM, "LOG", str(tmp_path / "entregar_micelio.log"))


GRAFO = {
    "nodes": [
        {"id": "obra-1.md", "dir": "corpus", "titulo": "percibido uno",
         "chunks": 2},
        {"id": "obra-2.md", "dir": "corpus", "titulo": "percibido dos",
         "chunks": 1},
    ],
    "edges": [{"a": "obra-1.md", "b": "obra-2.md", "w": 0.812}],
}

GRAFO_SIN_VINCULOS = {
    "nodes": [{"id": "obra-1.md", "dir": "corpus", "titulo": "sola",
               "chunks": 1}],
    "edges": [{"a": "obra-1.md", "b": "nodo-que-no-existe.md", "w": 0.9}],
}


class TestConstruirSalida:
    def test_convierte_y_cuenta(self):
        salida, n_piezas, n_vinculos = EM.construir_salida(GRAFO, 0.55)
        assert (n_piezas, n_vinculos) == (2, 1)
        assert salida["vinculos"][0]["clase"] == "semantico"
        assert salida["version"] == 1
        assert salida["fuente"] == "micelio_snapshot"
        assert salida["umbral"] == 0.55
        assert "generado" in salida

    def test_vinculos_a_nodos_fantasma_no_cuentan(self):
        # contrato_archivo.convertir already filters to known ids -- confirms
        # that filter is what produces the 0 that trips the gate below.
        _, n_piezas, n_vinculos = EM.construir_salida(GRAFO_SIN_VINCULOS, 0.55)
        assert (n_piezas, n_vinculos) == (1, 0)


class TestGateDeCero:
    """The real gate lives in main(): 0 vinculos = ERROR, nothing gets
    written and no PR opens. Exercised via main() because that is where
    the decision lives, but neither of these two branches ever reaches
    git/gh (see the module docstring)."""

    def test_micelio_inalcanzable_sale_1_sin_tocar_git(self, monkeypatch, capsys):
        def _explota(url, umbral, timeout=90):
            raise TimeoutError("simulated: box unreachable")
        monkeypatch.setattr(EM, "leer_grafo", _explota)
        monkeypatch.setattr(EM, "git", lambda *a, **k: pytest.fail(
            "no deberia llamar a git si el micelio no respondio"))
        monkeypatch.setattr(sys, "argv", ["entregar_micelio.py"])
        assert EM.main() == 1
        assert "ERROR" in capsys.readouterr().out

    def test_cero_vinculos_sale_1_sin_tocar_git(self, monkeypatch, capsys):
        monkeypatch.setattr(EM, "leer_grafo",
                            lambda url, umbral, timeout=90: GRAFO_SIN_VINCULOS)
        monkeypatch.setattr(EM, "git", lambda *a, **k: pytest.fail(
            "no deberia llamar a git con 0 vinculos"))
        monkeypatch.setattr(sys, "argv", ["entregar_micelio.py"])
        assert EM.main() == 1
        salida = capsys.readouterr().out
        assert "ERROR" in salida
        assert "0 vinculos" in salida

    def test_dry_run_con_datos_reales_sale_0_sin_tocar_git(self, monkeypatch, capsys):
        monkeypatch.setattr(EM, "leer_grafo",
                            lambda url, umbral, timeout=90: GRAFO)
        monkeypatch.setattr(EM, "git", lambda *a, **k: pytest.fail(
            "--dry-run no deberia llamar a git"))
        monkeypatch.setattr(sys, "argv", ["entregar_micelio.py", "--dry-run"])
        assert EM.main() == 0
        salida = capsys.readouterr().out
        assert "DRY-RUN" in salida
        assert "1 vinculos" in salida or "1, " in salida  # real count, not guessed


class TestSinGenerado:
    def test_solo_saca_la_marca_de_tiempo(self):
        a = {"a": 1, "generado": "hoy"}
        b = {"a": 1, "generado": "ayer"}
        assert EM._sin_generado(a) == EM._sin_generado(b)
        assert EM._sin_generado({"a": 1, "b": 2}) == {"a": 1, "b": 2}
