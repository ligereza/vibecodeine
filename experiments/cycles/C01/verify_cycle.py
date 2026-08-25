"""Mechanical acceptance gate for cycle C01 endpoint experiments."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENDPOINTS = (ROOT / "public_endpoint", ROOT / "native_endpoint")
REQUIRED_REPORT_MARKER_ALTERNATIVES = (
    ("files changed", "changed files"),
    ("exit", "exit code"),
    ("can observe",),
    ("cannot observe", "limits", "limitations"),
)


def _report_status(endpoint: Path) -> dict:
    report = endpoint / "REPORT.md"
    if not report.is_file():
        return {"status": "FAIL", "reason": "missing_REPORT.md"}
    text = report.read_text(encoding="utf-8").lower()
    missing = [
        " / ".join(options)
        for options in REQUIRED_REPORT_MARKER_ALTERNATIVES
        if not any(option in text for option in options)
    ]
    if missing:
        return {"status": "FAIL", "reason": "report_missing_markers", "missing": missing}
    return {"status": "PASS", "report": str(report)}


def _tests(endpoint: Path) -> list[Path]:
    return sorted(endpoint.rglob("test_*.py")) + sorted(endpoint.rglob("*_test.py"))


def _run_tests(endpoint: Path, tests: list[Path]) -> dict:
    if not tests:
        return {"status": "FAIL", "reason": "no_tests"}
    command = [sys.executable, "-m", "pytest", "-q", *[str(path.relative_to(endpoint)) for path in tests]]
    result = subprocess.run(command, cwd=endpoint, text=True,
                            capture_output=True, check=False)
    return {
        "status": "PASS" if result.returncode == 0 else "FAIL",
        "exit_code": result.returncode,
        "command": command,
        "stdout_tail": result.stdout[-2000:],
        "stderr_tail": result.stderr[-2000:],
    }


def main() -> int:
    results = {}
    for endpoint in ENDPOINTS:
        key = endpoint.name
        if not endpoint.is_dir():
            results[key] = {"status": "FAIL", "reason": "missing_endpoint"}
            continue
        tests = _tests(endpoint)
        results[key] = {
            "report": _report_status(endpoint),
            "tests": _run_tests(endpoint, tests),
            "test_files": [str(path) for path in tests],
        }

    passed = all(
        value.get("report", {}).get("status") == "PASS"
        and value.get("tests", {}).get("status") == "PASS"
        for value in results.values()
    ) and len(results) == len(ENDPOINTS)
    payload = {"schema": "mak-cycle-c01-gate-v1", "status": "PASS" if passed else "FAIL", "endpoints": results}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
