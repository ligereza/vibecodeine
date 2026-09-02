#!/usr/bin/env python3
"""Materialize one MAK tree at /home/mak without deleting existing data.

The lossless projection has one record per relative path.  Equal paths are
linked once.  For divergent paths the already-active checkout is used as the
operational baseline (or the first available source when it did not contain
the path); every alternate byte stream remains in the dated origins and is
listed in the report.  Existing home-level files are never overwritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter
from pathlib import Path


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def same_bytes(left: Path, right: Path) -> bool:
    if left.is_symlink() or right.is_symlink():
        return left.is_symlink() and right.is_symlink() and os.readlink(left) == os.readlink(right)
    return left.is_file() and right.is_file() and left.stat().st_size == right.stat().st_size and digest(left) == digest(right)


def install(source: Path, target: Path) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.is_symlink():
        target.symlink_to(os.readlink(source))
        return "linked_symlink"
    os.link(source, target)
    return "linked_file"


def materialize(projection: Path, output: Path, report_path: Path) -> dict:
    manifest = json.loads((projection / "MANIFEST.json").read_text(encoding="utf-8"))
    rows = []
    counts = Counter()
    tree = projection / "tree"

    for item in manifest["paths"]:
        rel = item["relative"]
        target = output / rel
        operation = item["operation"]
        if operation == "tree_equal":
            source = tree / rel
            source_id = "equal-projection"
        else:
            active = next((x for x in item["items"] if x["source_id"] == "active-flujo"), None)
            selected = active or item["items"][0]
            source = Path(selected["source"])
            source_id = selected["source_id"]

        record = {
            "relative": rel,
            "operation": operation,
            "source_id": source_id,
            "source": str(source),
        }
        if target.exists() or target.is_symlink():
            if source.exists() or source.is_symlink():
                if same_bytes(source, target):
                    record["action"] = "existing_equal"
                    counts["existing_equal"] += 1
                else:
                    record["action"] = "root_collision_preserved"
                    counts["root_collision_preserved"] += 1
            else:
                record["action"] = "source_unreadable"
                counts["source_unreadable"] += 1
        elif not source.exists() and not source.is_symlink():
            record["action"] = "source_missing"
            counts["source_missing"] += 1
        else:
            try:
                record["action"] = install(source, target)
                counts[record["action"]] += 1
            except OSError as exc:
                record["action"] = "install_error"
                record["error"] = str(exc)
                counts["install_error"] += 1
        rows.append(record)

    report = {
        "schema": "mak-root-materialization-v1",
        "projection": str(projection),
        "output": str(output),
        "policy": "one path at output; no overwrite; active baseline for divergent paths; origins preserve alternates",
        "projection_counts": manifest["counts"],
        "counts": dict(counts),
        "paths": rows,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projection", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = materialize(args.projection.resolve(), args.output.resolve(), args.report.resolve())
    print(json.dumps({"output": report["output"], "counts": report["counts"]}, sort_keys=True))
    return 0 if not report["counts"].get("install_error") else 1


if __name__ == "__main__":
    raise SystemExit(main())
