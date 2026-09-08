from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cultura" / "mak_plataforma"))
import coherence  # noqa: E402


def test_coherence_no_reporta_backups_como_codigo_vivo():
    assert coherence._box_owned("rollback/graph-cache-race-20260811/memoria.py")
    assert coherence._box_owned("__pycache__/coherence.cpython-311.pyc")
    assert not coherence._box_owned("rescue_adjudicator.py")
