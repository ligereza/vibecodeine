"""Regression tests for physical repo/runtime coherence boundaries."""
from pathlib import Path

from cultura.mak_plataforma import coherence


def test_coherence_excludes_virtualenv_code_from_runtime_drift():
    assert coherence._box_owned(".venv/lib/python3.11/site-packages/x.py")
    assert coherence._box_owned("venv/lib/python3.11/site-packages/x.py")
    assert coherence._box_owned(".venv/bin/tool")


def test_coherence_matches_the_invoked_absolute_path_not_a_basename():
    units = "ExecStart=%h/research/interfaz.py"
    assert not coherence._is_invoked(
        "interfaz.py", Path("/home/mak/plataforma"), "", units)
    assert coherence._is_invoked(
        "interfaz.py", Path("/home/mak/research"), "", units)


def test_coherence_keeps_unapproved_curatoria_candidates_out_of_live_scope():
    assert coherence.REPO_ONLY["curatoria"] == {
        "diagnostico_proyectos.py", "ingesta_archivo.py",
    }
