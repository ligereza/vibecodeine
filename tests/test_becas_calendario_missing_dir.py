"""`consolidar()` used to read a missing informes directory as "zero becas".

Fixed defect: `consolidar(informes_dir)` returned `[]` when the directory did
not exist -- a typo'd path, an unmounted drive, a wrong argument -- exactly
the same `[]` it returns for a directory that genuinely has no matching
informes this cycle. `main()` then printed "Fondos procesados: 0" and exited
0, indistinguishable from an honestly empty result. Same family as `flujo
doctor` reporting `airdrop pendiente: OK` for a directory that did not exist.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import becas_calendario  # noqa: E402


def test_consolidar_raises_instead_of_reporting_zero_becas(tmp_path):
    missing = tmp_path / "no_existe"
    with pytest.raises(FileNotFoundError):
        becas_calendario.consolidar(str(missing))


def test_main_exits_nonzero_and_says_why_on_missing_dir(tmp_path):
    missing = tmp_path / "no_existe"
    out = tmp_path / "calendario.md"
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "becas_calendario.py"),
         str(missing), "--out", str(out)],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode != 0, (
        "a missing informes directory must not exit 0 like an empty result")
    assert "no existe" in result.stderr.lower()
    assert not out.exists(), "no calendar file should be written for a failed run"
