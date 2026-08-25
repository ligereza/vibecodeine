"""Mechanical acceptance gate for the real-input C02 endpoints."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENDPOINTS = (ROOT / "blender_endpoint", ROOT / "aep_endpoint")
CONTROL_TESTS = ROOT / "tests"
GRAPH = ROOT / "native_graph.json"
INPUT_HASHES = {
    Path("/home/mak/curatoria_inbox/ARICA/RAYU.blend"): "acafc1db0088016139921b1ea2c9d7a5310247658117fa7021662e13e907ce86",
    Path("/home/mak/curatoria_inbox/ARICA/ARICA.aep"): "99247d6506c6d1d9ce3023f4a1e044da47c806e3cd606d47b61e70fb32f5c460",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _source_status() -> dict:
    result = {}
    for path, expected in INPUT_HASHES.items():
        actual = _sha256(path) if path.is_file() else None
        result[str(path)] = {
            "status": "PASS" if actual == expected else "FAIL",
            "expected_sha256": expected,
            "actual_sha256": actual,
        }
    return result


def _report_status(endpoint: Path) -> dict:
    report = endpoint / "REPORT.md"
    if not report.is_file():
        return {"status": "FAIL", "reason": "missing_REPORT.md"}
    text = report.read_text(encoding="utf-8").lower()
    required = {
        "read-only claim": ("read-only", "read only", "solo lectura", "se leyó", "no se abrió", "no se escribió"),
        "observed/unknown distinction": ("unknown", "desconoc", "observ"),
        "execution evidence": ("exit", "resultado", "command", "comando"),
        "limitations": ("limit", "límite", "no prueba", "cannot", "no se puede", "no hay"),
    }
    missing = [name for name, alternatives in required.items()
               if not any(option in text for option in alternatives)]
    return {"status": "PASS" if not missing else "FAIL",
            "report": str(report), "missing": missing}


def _tests(endpoint: Path) -> list[Path]:
    return sorted(endpoint.rglob("test_*.py")) + sorted(endpoint.rglob("*_test.py"))


def _run_tests(endpoint: Path, tests: list[Path]) -> dict:
    if not tests:
        return {"status": "FAIL", "reason": "no_tests"}
    # The endpoint tests intentionally use stdlib unittest so the gate does
    # not depend on a project-wide test runner being installed in the
    # execution environment.
    command = [sys.executable, "-m", "unittest", "discover", "-s", "tests",
               "-p", "test_*.py", "-v"]
    result = subprocess.run(command, cwd=endpoint, text=True,
                            capture_output=True, check=False)
    return {
        "status": "PASS" if result.returncode == 0 else "FAIL",
        "exit_code": result.returncode,
        "command": command,
        "stdout_tail": result.stdout[-2000:],
        "stderr_tail": result.stderr[-2000:],
    }


def _graph_status() -> dict:
    if not GRAPH.is_file():
        return {"status": "FAIL", "reason": "missing_native_graph.json"}
    try:
        payload = json.loads(GRAPH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "reason": f"invalid_native_graph:{exc}"}
    safety = payload.get("safety", {})
    forbidden = [
        edge for edge in payload.get("edges", [])
        if edge.get("relation") in {"generated", "RENDERS_TO", "renders_to"}
    ]
    passed = (
        payload.get("schema") == "mak-cycle-c02-native-graph-v1"
        and safety.get("forbidden_relations_absent") is True
        and safety.get("learning_or_inference_performed") is False
        and safety.get("public_catalog_available") is False
        and not forbidden
    )
    return {
        "status": "PASS" if passed else "FAIL",
        "schema": payload.get("schema"),
        "node_count": len(payload.get("nodes", [])),
        "edge_count": len(payload.get("edges", [])),
        "unknown_count": len(payload.get("unknowns", [])),
        "forbidden_relation_count": len(forbidden),
    }


def main() -> int:
    sources = _source_status()
    endpoints = {}
    for endpoint in ENDPOINTS:
        tests = _tests(endpoint) if endpoint.is_dir() else []
        endpoints[endpoint.name] = {
            "report": _report_status(endpoint) if endpoint.is_dir()
            else {"status": "FAIL", "reason": "missing_endpoint"},
            "tests": _run_tests(endpoint, tests) if endpoint.is_dir()
            else {"status": "FAIL", "reason": "missing_endpoint"},
            "test_files": [str(path) for path in tests],
        }
    control_tests = _tests(CONTROL_TESTS) if CONTROL_TESTS.is_dir() else []
    controls = {
        "tests": _run_tests(ROOT, control_tests) if CONTROL_TESTS.is_dir()
        else {"status": "FAIL", "reason": "missing_control_tests"},
        "test_files": [str(path) for path in control_tests],
        "graph": _graph_status(),
    }
    passed = all(item["status"] == "PASS" for item in sources.values()) and all(
        data["report"]["status"] == "PASS" and data["tests"]["status"] == "PASS"
        for data in endpoints.values()
    ) and controls["tests"]["status"] == "PASS" and controls["graph"]["status"] == "PASS"
    payload = {
        "schema": "mak-cycle-c02-gate-v1",
        "status": "PASS" if passed else "FAIL",
        "sources": sources,
        "endpoints": endpoints,
        "controls": controls,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
