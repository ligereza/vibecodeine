"""Mechanical acceptance gate for the C03 public-input and blind bridge cycle."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENDPOINTS = (ROOT / "public_input", ROOT / "blind_bridge")
CONTROL_TESTS = ROOT / "tests"
REAL_STATUS = ROOT / "real_input_status.json"


def _tests(root: Path) -> list[Path]:
    return sorted(root.rglob("test_*.py")) + sorted(root.rglob("*_test.py"))


def _run_tests(cwd: Path, tests: list[Path]) -> dict:
    if not tests:
        return {"status": "FAIL", "reason": "no_tests"}
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"],
        cwd=cwd, text=True, capture_output=True, check=False,
    )
    return {
        "status": "PASS" if result.returncode == 0 else "FAIL",
        "exit_code": result.returncode,
        "stdout_tail": result.stdout[-3000:],
        "stderr_tail": result.stderr[-3000:],
    }


def _report(endpoint: Path) -> dict:
    path = endpoint / "REPORT.md"
    if not path.is_file():
        return {"status": "FAIL", "reason": "missing_REPORT.md"}
    text = path.read_text(encoding="utf-8").lower()
    required = {
        "scope": ("scope", "alcance", "resultado", "contrato"),
        "limits": ("limit", "límite", "no se puede", "unknown"),
        "commands": ("command", "comando", "exit"),
        "evidence": ("evidence", "evidencia", "observ"),
    }
    missing = [name for name, alternatives in required.items()
               if not any(option in text for option in alternatives)]
    return {"status": "PASS" if not missing else "FAIL", "path": str(path), "missing": missing}


def _real_status() -> dict:
    if not REAL_STATUS.is_file():
        return {"status": "FAIL", "reason": "missing_real_input_status"}
    try:
        payload = json.loads(REAL_STATUS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "reason": f"invalid_real_input_status:{exc}"}
    passed = (
        payload.get("schema") == "mak-cycle-c03-public-input-audit-v1"
        and payload.get("catalog_status") == "unavailable"
        and payload.get("public_join") == "unknown"
        and payload.get("input", {}).get("extracted") is False
        and not payload.get("archive", {}).get("media_members_excluding_brand_logo")
        and not payload.get("archive", {}).get("public_named_members_outside_connections")
    )
    return {
        "status": "PASS" if passed else "FAIL",
        "member_count": payload.get("archive", {}).get("member_count"),
        "catalog_status": payload.get("catalog_status"),
        "public_join": payload.get("public_join"),
        "extracted": payload.get("input", {}).get("extracted"),
    }


def main() -> int:
    endpoints = {}
    for endpoint in ENDPOINTS:
        tests = _tests(endpoint) if endpoint.is_dir() else []
        endpoints[endpoint.name] = {
            "report": _report(endpoint) if endpoint.is_dir() else {"status": "FAIL", "reason": "missing_endpoint"},
            "tests": _run_tests(endpoint, tests) if endpoint.is_dir() else {"status": "FAIL", "reason": "missing_endpoint"},
            "test_files": [str(path) for path in tests],
        }
    control_tests = _tests(CONTROL_TESTS) if CONTROL_TESTS.is_dir() else []
    controls = {
        "real_input": _real_status(),
        "tests": _run_tests(ROOT, control_tests) if CONTROL_TESTS.is_dir() else {"status": "FAIL", "reason": "missing_control_tests"},
        "test_files": [str(path) for path in control_tests],
    }
    passed = (
        controls["real_input"]["status"] == "PASS"
        and controls["tests"]["status"] == "PASS"
        and all(data["report"]["status"] == "PASS" and data["tests"]["status"] == "PASS" for data in endpoints.values())
    )
    payload = {
        "schema": "mak-cycle-c03-gate-v1",
        "status": "PASS" if passed else "FAIL",
        "endpoints": endpoints,
        "controls": controls,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
