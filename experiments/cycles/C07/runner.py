"""C07 gate: tests, py_compile, and deterministic fixture graph output."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from fixtures.build_fixtures import create_case
from practice_graph import build_graph


def main() -> int:
    tests = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-p", "test_*.py"], cwd=ROOT, capture_output=True, text=True, check=False)
    compile_targets = [ROOT / "practice_graph.py", ROOT / "runner.py", ROOT / "fixtures" / "build_fixtures.py", ROOT / "tests" / "test_practice_graph.py"]
    compile_run = subprocess.run([sys.executable, "-m", "py_compile", *map(str, compile_targets)], cwd=ROOT, capture_output=True, text=True, check=False)
    cases = {}
    with tempfile.TemporaryDirectory() as temp:
        for case_id in ("frames_plus_export", "export_without_project", "project_without_export", "same_name_different_work", "same_work_different_proportions"):
            cases[case_id] = build_graph(create_case(case_id, Path(temp) / case_id), root=Path(temp) / case_id)
    output = ROOT / "graph.json"
    output.write_text(json.dumps({"schema": "mak-cycle-c07-run-v1", "cases": cases}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = {"tests_exit_code": tests.returncode, "py_compile_exit_code": compile_run.returncode, "output": str(output), "case_count": len(cases), "candidate_count": sum(item["summary"]["candidate_count"] for item in cases.values())}
    print(json.dumps(summary, sort_keys=True))
    if tests.returncode != 0 or compile_run.returncode != 0:
        print(tests.stdout + tests.stderr + compile_run.stdout + compile_run.stderr, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
