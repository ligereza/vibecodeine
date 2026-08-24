#!/usr/bin/env python3
"""Ask Blender for scene output paths without rendering or saving.

This is a bounded fallback for files the static .blend reader cannot decode.
Blender is launched in background mode with factory startup and auto-execution
disabled. The expression only reads bpy.data.filepath and
scene.render.filepath; it never calls a render or save operator.

The result is evidence about the current file as Blender 4.x opens it. It is
not a history witness and it does not emit RENDERS_TO. A caller must still
apply the directory/candidate-cardinality contract before writing an edge.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

CONTRACT = "mak-blender-scene-probe-v1"
MARKER = "MAK_SCENE_PROBE="
DEFAULT_TIMEOUT = 120

PROBE_EXPRESSION = (
    "import bpy,json; "
    "print(\"MAK_SCENE_PROBE=\"+json.dumps({"
    "\"filepath\":bpy.data.filepath,"
    "\"scenes\":[{\"name\":s.name,\"render_filepath\":s.render.filepath}"
    " for s in bpy.data.scenes]},ensure_ascii=False))"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_blender(explicit: str | None) -> Path:
    candidates = [
        Path(explicit).expanduser() if explicit else None,
        Path(os.environ["BLENDER_EXE"]).expanduser()
        if os.environ.get("BLENDER_EXE") else None,
        Path("/home/mak/blender/blender"),
    ]
    for candidate in candidates:
        if candidate and candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate.resolve()
    found = shutil.which("blender")
    if found:
        return Path(found).resolve()
    raise FileNotFoundError("blender_executable_not_found")


def blender_version(blender: Path) -> str:
    result = subprocess.run(
        [str(blender), "--version"],
        capture_output=True, text=True, errors="replace", timeout=30,
        check=False)
    line = next((line.strip() for line in result.stdout.splitlines() if line.strip()), "")
    return line[:200] or f"exit:{result.returncode}"


def _tail(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        value = value.decode("utf-8", "replace")
    return value[-2000:]


def _probe_payload(stdout: str) -> dict[str, Any] | None:
    for line in reversed(stdout.splitlines()):
        if line.startswith(MARKER):
            try:
                value = json.loads(line[len(MARKER):])
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict) and isinstance(value.get("scenes"), list):
                return value
    return None


def probe_file(path: Path, *, blender: Path, timeout: int) -> dict[str, Any]:
    """Probe one file and return a report row without mutating it."""
    row: dict[str, Any] = {
        "path": str(path),
        "sha256": _sha256(path),
        "status": "",
        "returncode": None,
        "scenes": [],
    }
    command = [
        str(blender), "--background", "--factory-startup",
        "--disable-autoexec", str(path), "--python-expr", PROBE_EXPRESSION,
    ]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, errors="replace",
            timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        row.update({
            "status": "timeout",
            "error": f"timeout_seconds:{timeout}",
            "stdout_tail": _tail(exc.stdout),
            "stderr_tail": _tail(exc.stderr),
        })
        return row
    except OSError as exc:
        row.update({"status": "launch_error", "error": str(exc)[:200]})
        return row

    row["returncode"] = result.returncode
    payload = _probe_payload(result.stdout)
    if result.returncode != 0 or payload is None:
        row.update({
            "status": "decoder_limit",
            "error": "probe_payload_missing" if payload is None else "blender_nonzero",
            "stdout_tail": _tail(result.stdout),
            "stderr_tail": _tail(result.stderr),
        })
        return row

    row.update({
        "status": "ok",
        "file_declared_path": payload.get("filepath", ""),
        "scenes": payload["scenes"],
    })
    return row


def _paths_from_render_report(path: Path) -> list[Path]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    result = payload.get("result", payload)
    root = Path(result["root"])
    return [
        root / row["relative_path"]
        for row in result.get("files", [])
        if row.get("error")
    ]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", help="Blender executable; BLENDER_EXE is a fallback")
    parser.add_argument("--input", action="append", type=Path,
                        help="one .blend to probe; repeatable")
    parser.add_argument("--render-report", type=Path,
                        help="probe only decoder-limit files from render_output_edges JSON")
    parser.add_argument("--output", type=Path,
                        help="write the JSON report here; otherwise print it")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help=f"per-file timeout in seconds (default: {DEFAULT_TIMEOUT})")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    inputs = list(args.input or [])
    if args.render_report:
        inputs.extend(_paths_from_render_report(args.render_report))
    unique_inputs = sorted({path.expanduser().resolve() for path in inputs})
    if not unique_inputs:
        parser.error("provide --input or --render-report")
    missing = [str(path) for path in unique_inputs if not path.is_file()]
    if missing:
        parser.error(f"input_not_a_file: {missing[0]}")

    blender = resolve_blender(args.blender)
    rows = [probe_file(path, blender=blender, timeout=args.timeout)
            for path in unique_inputs]
    report: dict[str, Any] = {
        "schema": CONTRACT,
        "read_only": True,
        "renders": False,
        "saves": False,
        "blender": str(blender),
        "blender_version": blender_version(blender),
        "timeout_seconds": args.timeout,
        "file_count": len(rows),
        "ok_files": sum(row["status"] == "ok" for row in rows),
        "decoder_limit_files": sum(row["status"] != "ok" for row in rows),
        "files": rows,
    }
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if report["decoder_limit_files"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
