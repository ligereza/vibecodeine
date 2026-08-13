#!/usr/bin/env python3
"""Import a recoverable Claude session tree without importing an environment.

The source tree is evidence and candidate material. This importer preserves
relative paths and SHA-256 values, while excluding virtual environments,
private web-export records, and credential-shaped files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path


EXCLUDED_DIRS = {".venv", "__pycache__", "claude_web_export_2026-08-11"}
EXCLUDED_NAMES = {".env"}
EXCLUDED_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
WINDOWS_USER_ROOT = re.compile(r"[A-Za-z]:[\\/]Users[\\/]+[^\\/\s]+", re.IGNORECASE)


def sanitize_text(text: str) -> str:
    return WINDOWS_USER_ROOT.sub("<local-user-home>", text)


def public_bytes(path: Path) -> tuple[bytes, bool]:
    content = path.read_bytes()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return content, False
    sanitized = sanitize_text(text)
    return sanitized.encode("utf-8"), sanitized != text


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def excluded(relative: Path) -> str | None:
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        if "claude_web_export_2026-08-11" in relative.parts:
            return "private_web_export"
        return "runtime_environment"
    if relative.name in EXCLUDED_NAMES:
        return "credential_file"
    if relative.suffix.lower() in EXCLUDED_SUFFIXES:
        return "credential_file"
    return None


def import_tree(source: Path, destination: Path) -> dict[str, object]:
    source = source.resolve()
    destination = destination.resolve()
    rows: list[dict[str, object]] = []
    excluded_rows: list[dict[str, str]] = []
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        reason = excluded(relative)
        if reason:
            excluded_rows.append({"source": relative.as_posix(), "reason": reason})
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        rows.append({
            "source": relative.as_posix(),
            "target": target.relative_to(destination).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    manifest = {
        "schema": "recovered-session-import-v1",
        "source": str(source),
        "destination": str(destination),
        "status": "evidence_preserved_candidate_material",
        "files": rows,
        "excluded": excluded_rows,
    }
    manifest_path = destination / "MANIFEST.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    if not args.source.is_dir():
        parser.error("source directory does not exist")
    result = import_tree(args.source, args.destination)
    print(json.dumps({
        "files": len(result["files"]),
        "excluded": len(result["excluded"]),
        "destination": result["destination"],
    }, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
