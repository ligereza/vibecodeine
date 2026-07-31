"""The venue viewer's JS actually runs, projects and reports, or CI goes red.

Same cause as tests/test_iskvw_piel_smoke.py (PR #403 shipped a skin whose
inline JS died on frame one under a green CI), plus the two failures specific
to a 3D viewer, both of which look perfect in a screenshot: a projection that
does not move when you drag, and an edge budget that crops the venue in
silence. tools/venue3d_smoke.mjs boots the real inline script twice -- with
the default cap and with ?aristas=120 -- and checks both.

Retirement: if the viewer ever gains a real browser test in CI.
"""
import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SMOKE = RAIZ / "tools" / "venue3d_smoke.mjs"


def test_venue_viewer_js_runs_projects_and_reports():
    node = shutil.which("node")
    if not node:
        pytest.skip("node not on PATH (CI runners ship it; install node locally)")
    proc = subprocess.run(
        [node, str(SMOKE)], capture_output=True, text=True, timeout=120, cwd=RAIZ,
    )
    assert proc.returncode == 0, (
        "the venue viewer failed its smoke:\n" + proc.stdout + proc.stderr
    )
