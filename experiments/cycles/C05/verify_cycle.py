"""Gate the C05 real Blender export-witness observation."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from real_export_observer import build_observation, sha256_file


ROOT = Path(__file__).resolve().parent
ARICA = Path("/home/mak/curatoria_inbox/ARICA")
SOURCE = ARICA / "RAYU.blend"
EXPECTED_SOURCE_SHA256 = "acafc1db0088016139921b1ea2c9d7a5310247658117fa7021662e13e907ce86"
OUTPUT = ROOT / "real_export_witness.json"


def run_tests() -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        (str(ROOT), str(ROOT / "tests"), str(ROOT.parent.parent.parent / "src"))
    )
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-p", "test_real_export_observer.py"],
        cwd=ROOT.parent.parent.parent,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return {"exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def main() -> int:
    tests = run_tests()
    before = sha256_file(SOURCE)
    observation = build_observation(
        source_blend=SOURCE,
        source_snapshot=ROOT.parent / "C02" / "blender_endpoint" / "snapshot.json",
        export_script=ARICA / "rayu_export.py",
        marker=ARICA / "rayu_export_done.txt",
        output_glb=ARICA / "rayu_resources.glb",
    )
    OUTPUT.write_text(json.dumps(observation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    after = sha256_file(SOURCE)
    summary = {
        "tests_exit_code": tests["exit_code"],
        "source_hash_before": before,
        "source_hash_after": after,
        "source_unchanged": before == after == EXPECTED_SOURCE_SHA256,
        "witness_status": observation["witness"]["status"],
        "check_count": len(observation["witness"]["checks"]),
        "output": str(OUTPUT),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0 if tests["exit_code"] == 0 and summary["source_unchanged"] and summary["witness_status"] == "supported" else 1


if __name__ == "__main__":
    raise SystemExit(main())
