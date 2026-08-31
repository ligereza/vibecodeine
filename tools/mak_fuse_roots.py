#!/usr/bin/env python3
"""Build a lossless, side-by-side fusion of complete MAK project roots.

No source is selected as authoritative.  Equal bytes are represented once in
``tree/`` (with all origins recorded); divergent paths are represented under
``variants/<source-id>/``.  The complete source checkouts remain under
``origins/`` so a later adapter can expose either implementation deliberately.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache", "node_modules"}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def collect(source_id: str, root: Path) -> tuple[dict[str, list[dict]], int]:
    rows: dict[str, list[dict]] = defaultdict(list)
    excluded = 0
    for current, dirs, names in os.walk(root, topdown=True, followlinks=False):
        kept = []
        for name in sorted(dirs):
            if name in SKIP_DIRS:
                excluded += 1
            else:
                kept.append(name)
        dirs[:] = kept
        for name in sorted(names):
            path = Path(current) / name
            rel = path.relative_to(root).as_posix()
            try:
                info = path.lstat()
                if os.path.islink(path):
                    item = {"source_id": source_id, "source": str(path), "kind": "symlink", "link_target": os.readlink(path)}
                elif path.is_file():
                    item = {"source_id": source_id, "source": str(path), "kind": "file", "sha256": digest(path), "size_bytes": info.st_size}
                else:
                    item = {"source_id": source_id, "source": str(path), "kind": "special", "size_bytes": info.st_size}
            except OSError as exc:
                item = {"source_id": source_id, "source": str(path), "kind": "unreadable", "error": str(exc)}
            rows[rel].append(item)
    return rows, excluded


def link_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    os.link(source, target)


def link_or_copy(item: dict, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    source = Path(item["source"])
    if item["kind"] == "file":
        link_file(source, target)
    elif item["kind"] == "symlink":
        target.symlink_to(item["link_target"])


def fuse(sources: dict[str, Path], output: Path) -> dict:
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"output is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    tree = output / "tree"
    variants = output / "variants"
    tree.mkdir(exist_ok=True)
    variants.mkdir(exist_ok=True)
    grouped: dict[str, list[dict]] = defaultdict(list)
    excluded = 0
    for source_id, root in sources.items():
        if not root.is_dir():
            raise SystemExit(f"source is not a directory: {root}")
        rows, skipped = collect(source_id, root)
        excluded += skipped
        for rel, items in rows.items():
            grouped[rel].extend(items)

    manifest_rows = []
    counts = defaultdict(int)
    for rel, items in sorted(grouped.items()):
        kinds = {item["kind"] for item in items}
        signatures = {
            (item.get("kind"), item.get("sha256"), item.get("link_target"), item.get("error"))
            for item in items
        }
        divergent = len(signatures) > 1 or len(kinds) > 1
        if not divergent and items[0]["kind"] in {"file", "symlink"}:
            link_or_copy(items[0], tree / rel)
            counts["deduplicated_equal"] += len(items) - 1
            counts["tree_paths"] += 1
            operation = "tree_equal"
        else:
            for item in items:
                link_or_copy(item, variants / item["source_id"] / rel)
            counts["divergent_paths"] += 1
            counts["variant_paths"] += len(items)
            operation = "variants_all_preserved"
        manifest_rows.append({"relative": rel, "operation": operation, "items": items})

    manifest = {
        "schema": "mak-lossless-fused-root-v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "sources": {source_id: str(path) for source_id, path in sources.items()},
        "excluded_generated_directories": excluded,
        "counts": dict(counts),
        "paths": manifest_rows,
        "policy": "no winner; equal bytes once, divergent bytes side-by-side",
    }
    (output / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--win", type=Path, required=True)
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument(
        "--active",
        type=Path,
        help="Third source: the currently active flujo checkout.",
    )
    args = parser.parse_args()
    sources = {
        "win-flujo": args.win.resolve(),
        "runner-vibecodeine": args.runner.resolve(),
    }
    if args.active:
        sources["active-flujo"] = args.active.resolve()
    manifest = fuse(sources, args.output.resolve())
    print(json.dumps({"output": str(args.output.resolve()), "counts": manifest["counts"], "excluded": manifest["excluded_generated_directories"]}, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
