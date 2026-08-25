"""Mechanical acceptance gate for C04 real media evidence."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENDPOINTS = (ROOT / "media_observer", ROOT / "evidence_evaluator")
CONTROL_TESTS = ROOT / "tests"
REAL_EVIDENCE = ROOT / "real_evidence.json"
INPUTS = {
    Path("/home/mak/curatoria_inbox/ARICA/ARICA.aep"): "99247d6506c6d1d9ce3023f4a1e044da47c806e3cd606d47b61e70fb32f5c460",
    Path("/home/mak/curatoria_inbox/ARICA/tottem_ojo.mp4"): "b7253320e7a23917439dd6ad2fa084a68510469517b76b6428c54f9856ca0776",
}


def _sha256(path: Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                digest.update(block)
        return digest.hexdigest()
    except OSError:
        return None


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
        "stdout_tail": result.stdout[-2500:],
        "stderr_tail": result.stderr[-2500:],
    }


def _report(endpoint: Path) -> dict:
    path = endpoint / "REPORT.md"
    if not path.is_file():
        return {"status": "FAIL", "reason": "missing_REPORT.md"}
    text = path.read_text(encoding="utf-8").lower()
    required = {
        "evidence": ("evidence", "evidencia", "resultado"),
        "limits": ("limit", "límite", "no demuestra", "unknown"),
        "read_only": ("read-only", "read only", "read_only", "solo lectura", "no se escribe", "no abre", "no escanea", "no consulta"),
        "commands": ("command", "comando", "exit"),
    }
    missing = [name for name, alternatives in required.items()
               if not any(option in text for option in alternatives)]
    return {"status": "PASS" if not missing else "FAIL", "path": str(path), "missing": missing}


def _source_status() -> dict:
    rows = {}
    for path, expected in INPUTS.items():
        actual = _sha256(path)
        rows[str(path)] = {
            "status": "PASS" if actual == expected else "FAIL",
            "expected_sha256": expected,
            "actual_sha256": actual,
        }
    return rows


def _real_evidence_status() -> dict:
    if not REAL_EVIDENCE.is_file():
        return {"status": "FAIL", "reason": "missing_real_evidence.json"}
    try:
        payload = json.loads(REAL_EVIDENCE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "reason": f"invalid_real_evidence:{exc}"}
    evaluation = payload.get("evaluation", {})
    claims = evaluation.get("claims", {})
    policy = evaluation.get("decision_policy", {})
    dimensions = payload.get("artifact", {}).get("dimensions")
    forbidden = [
        relation for relation in evaluation.get("relations", [])
        if relation.get("relation") in {"generated", "RENDERS_TO"}
    ]
    passed = (
        payload.get("schema") == "mak-cycle-c04-real-evidence-v1"
        and payload.get("status") == "observed"
        and dimensions == {"width": 256, "height": 1536}
        and claims.get("uses", {}).get("status") == "supported"
        and claims.get("output_role", {}).get("status") == "unknown"
        and not evaluation.get("relations")
        and policy.get("causality_from_coexistence") is False
        and policy.get("uses_hidden_truth") is False
        and not forbidden
    )
    return {
        "status": "PASS" if passed else "FAIL",
        "dimensions": dimensions,
        "uses_status": claims.get("uses", {}).get("status"),
        "output_role_status": claims.get("output_role", {}).get("status"),
        "relation_count": len(evaluation.get("relations", [])),
        "forbidden_relation_count": len(forbidden),
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
        "sources": _source_status(),
        "real_evidence": _real_evidence_status(),
        "tests": _run_tests(ROOT, control_tests) if CONTROL_TESTS.is_dir() else {"status": "FAIL", "reason": "missing_control_tests"},
        "test_files": [str(path) for path in control_tests],
    }
    passed = (
        all(item["status"] == "PASS" for item in controls["sources"].values())
        and controls["real_evidence"]["status"] == "PASS"
        and controls["tests"]["status"] == "PASS"
        and all(data["report"]["status"] == "PASS" and data["tests"]["status"] == "PASS" for data in endpoints.values())
    )
    payload = {
        "schema": "mak-cycle-c04-gate-v1",
        "status": "PASS" if passed else "FAIL",
        "endpoints": endpoints,
        "controls": controls,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
