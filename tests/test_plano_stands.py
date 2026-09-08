"""Tests for the stand-plan engine wrapper, `projects/plano/plano_stands.py`.

These five tests had skipped on every run since 2026-09-02 and nobody saw it,
because the guard below turns a missing subject into a skip instead of an
error. Two things were stale at once:

* `plano_stands.py` was removed from MAK that day, in the separation that
  dropped the tools importing `flujo.plano`. It lives in the FLUJO checkout
  now, and it calls itself "wrapper local del motor de planos de flujo" -- an
  entry point over the engine, which is exactly what the MAK side consumes
  through the `flujo` symlink. `flujo.plano` imports cleanly from here today,
  so the premise that retired it ("this branch cannot execute it") no longer
  holds.
* `PYTHONPATH` pointed at `REPO/src`, and MAK has no `src/`. That was the
  retired layout. Even with the script present the subprocess would have run
  without the engine on its path.

Retiring the file was the other option and it was the wrong one: MAK still
carries `projects/plano/ejemplos/evento_ejemplo.json`, the input these tests
feed the script, so the input stayed and only the subject left. Pointing at
the motor costs nothing and turns five dead tests into five that run.

The subject spans both checkouts, so this belongs to the `integration` lane,
where CI checks out MAK and FLUJO together. With no motor present it still
skips -- and now says which checkout is missing rather than naming a path that
moved.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tools.motor_checkout import motor_root

REPO = Path(__file__).resolve().parent.parent
MOTOR = motor_root(REPO)
# The script moved to the motor; the example input stayed here.
SCRIPT = (MOTOR / "projects" / "plano" / "plano_stands.py") if MOTOR else None
EJEMPLO = REPO / "projects" / "plano" / "ejemplos" / "evento_ejemplo.json"


def _run_script(args: list) -> subprocess.CompletedProcess:
    """Ejecuta plano_stands.py como subproceso con PYTHONPATH correcto."""
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    # The engine lives in the motor checkout. `REPO / "src"` was the retired
    # layout and does not exist in MAK.
    src_path = str(MOTOR / "src")
    env["PYTHONPATH"] = src_path + (os.pathsep + existing if existing else "")
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )


@pytest.mark.skipif(
    SCRIPT is None or not SCRIPT.exists(),
    reason="el checkout FLUJO no está presente: no hay motor de planos",
)
class TestPlanoStands:
    def test_ejemplo_json_existe(self):
        assert EJEMPLO.exists(), f"Falta ejemplo: {EJEMPLO}"

    def test_genera_svg(self):
        res = _run_script([str(EJEMPLO)])
        assert res.returncode == 0, f"stderr: {res.stderr}"
        svg = res.stdout
        assert svg.startswith("<svg")
        assert "</svg>" in svg
        assert "PLANO" in svg
        assert "Stand Informativo" in svg
        assert "Stand Testeo" in svg
        assert "Contención" in svg

    def test_genera_rider(self):
        res = _run_script([str(EJEMPLO), "--rider"])
        assert res.returncode == 0, f"stderr: {res.stderr}"
        rider = res.stdout
        assert "RIDER TÉCNICO" in rider
        assert "ALIMENTACIÓN" in rider
        assert "2 mesa(s)" in rider
        assert "testeo" in rider.lower()
        assert "ZONA DE CONTENCIÓN" in rider

    def test_evento_pequeno_sin_extras(self, tmp_path):
        peq = tmp_path / "evento_pequeno.json"
        peq.write_text(
            json.dumps(
                {
                    "nombre": "Evento pequeño",
                    "duracion_horas": 3,
                    "voluntarios": 3,
                    "asistentes_estimados": 100,
                    "incluye_testeo": False,
                    "masivo": False,
                }
            ),
            encoding="utf-8",
        )
        res = _run_script([str(peq), "--rider"])
        assert res.returncode == 0, f"stderr: {res.stderr}"
        rider = res.stdout
        assert "1 mesa(s)" in rider
        assert "colación" not in rider.lower()
        assert "alimentación" not in rider.lower()
        assert "testeo" not in rider.lower()
        assert "contención" not in rider.lower()

    def test_evento_masivo_agrega_contencion(self, tmp_path):
        masivo = tmp_path / "evento_masivo.json"
        masivo.write_text(
            json.dumps(
                {
                    "nombre": "Evento masivo",
                    "duracion_horas": 2,
                    "voluntarios": 2,
                    "asistentes_estimados": 2500,
                    "incluye_testeo": False,
                    "masivo": False,
                }
            ),
            encoding="utf-8",
        )
        res = _run_script([str(masivo), "--rider"])
        assert res.returncode == 0, f"stderr: {res.stderr}"
        rider = res.stdout
        assert "ZONA DE CONTENCIÓN" in rider
