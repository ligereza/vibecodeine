#!/usr/bin/env python3
"""Build one auditable filesystem map for the local MAK surface.

The map is deliberately not a Git index, a semantic knowledge map, or a
remote-drive inventory. It records current local evidence and says why any
subtree was excluded or measured only at its root.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/home/mak")
OUTPUT = ROOT / "indexes" / "mak-canonical-20260829" / "mak-canonical-map.json"

PROTECTED_TOP_LEVEL = {
    "WIN": "operator-protected historical evidence",
    "curatoria_inbox": "operator-protected Windows-to-Linux migration staging",
    "GoogleDrive": "active rclone mount; remote content is not local evidence",
    "OneDrive": "active rclone mount; remote content is not local evidence",
}

RUNTIME_METADATA_ONLY = {
    ".cache": "application and tool cache",
    ".claude": "agent runtime/session state",
    ".codex": "agent runtime/session state",
    ".config": "desktop and application configuration",
    ".local": "desktop/application state and trash",
    ".mozilla": "browser profile",
    ".npm": "package manager cache",
    ".ollama": "model runtime state",
    ".lmstudio": "model application state",
    ".venvs": "Python runtime environments",
    ".wine": "compatibility runtime",
    ".gnupg": "private key material",
    ".ssh": "private key material",
    ".aws": "provider credentials/configuration",
    ".pki": "certificate material",
    ".vscode": "editor state",
    ".vscode-shared": "editor state",
    ".copilot": "editor/agent state",
    ".continue": "editor/agent state",
    ".crawl4ai": "tool runtime state",
    ".dotnet": "SDK/runtime state",
    ".gemini": "agent runtime state",
    ".icons": "desktop theme state",
    ".idlerc": "editor state",
    ".nv": "GPU runtime state",
    ".themes": "desktop theme state",
    ".pytest_cache": "test cache",
}

SKIP_DIR_NAMES = {
    ".git": "Git internals; Git is outside this task",
    ".venv": "Python runtime environment",
    "venv": "Python runtime environment",
    "__pycache__": "Python generated cache",
    "node_modules": "package installation tree",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def basic_entry(path: Path, relative: str, scope: str, traversal: str) -> dict:
    item = {
        "path": str(path),
        "relative_path": relative,
        "scope": scope,
        "traversal": traversal,
    }
    try:
        info = path.lstat()
    except OSError as exc:
        item["kind"] = "unreadable"
        item["error"] = f"{type(exc).__name__}: {exc}"
        return item

    item.update(
        {
            "kind": (
                "directory"
                if stat.S_ISDIR(info.st_mode)
                else "symlink"
                if stat.S_ISLNK(info.st_mode)
                else "file"
                if stat.S_ISREG(info.st_mode)
                else "special"
            ),
            "size_bytes": info.st_size,
            "mtime_ns": info.st_mtime_ns,
            "mode": stat.filemode(info.st_mode),
            "device": info.st_dev,
            "inode": info.st_ino,
        }
    )
    if stat.S_ISLNK(info.st_mode):
        try:
            item["link_target"] = os.readlink(path)
        except OSError as exc:
            item["error"] = f"{type(exc).__name__}: {exc}"
    return item


def walk_local(root: Path, top_name: str, entries: list[dict], hash_cache: dict) -> None:
    stack = [(root, top_name)]
    while stack:
        current, relative = stack.pop()
        try:
            children = sorted(os.scandir(current), key=lambda item: item.name, reverse=True)
        except OSError as exc:
            entries.append(
                {
                    "path": str(current),
                    "relative_path": relative,
                    "scope": "local",
                    "traversal": "scan-error",
                    "kind": "unreadable",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            continue

        for child in children:
            child_path = Path(child.path)
            child_relative = f"{relative}/{child.name}"
            if child.name == OUTPUT.name and child_path.parent == OUTPUT.parent:
                continue
            if child.is_dir(follow_symlinks=False) and child.name in SKIP_DIR_NAMES:
                entry = basic_entry(child_path, child_relative, "local", "metadata-only")
                entry["exclusion_reason"] = SKIP_DIR_NAMES[child.name]
                entries.append(entry)
                continue

            entry = basic_entry(child_path, child_relative, "local", "scanned")
            if entry["kind"] == "file":
                cache_key = (entry["device"], entry["inode"], entry["size_bytes"], entry["mtime_ns"])
                if cache_key not in hash_cache:
                    try:
                        hash_cache[cache_key] = file_hash(child_path)
                    except OSError as exc:
                        entry["hash_error"] = f"{type(exc).__name__}: {exc}"
                    else:
                        entry["sha256"] = hash_cache[cache_key]
                else:
                    entry["sha256"] = hash_cache[cache_key]
                    entry["hash_reused_from_same_inode"] = True
            entries.append(entry)
            if entry["kind"] == "directory":
                stack.append((child_path, child_relative))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the current MAK filesystem hash and authority map."
    )
    parser.parse_args()
    entries: list[dict] = []
    hash_cache: dict = {}
    top_level = []

    for child in sorted(ROOT.iterdir(), key=lambda item: item.name):
        relative = child.name
        top_level.append(relative)
        if relative == OUTPUT.relative_to(ROOT).parts[0]:
            # The indexes root is scanned; only the generated map itself is omitted.
            pass
        if relative in PROTECTED_TOP_LEVEL:
            entry = basic_entry(child, relative, "protected", "root-only")
            entry["exclusion_reason"] = PROTECTED_TOP_LEVEL[relative]
            entries.append(entry)
            continue
        if relative in RUNTIME_METADATA_ONLY:
            entry = basic_entry(child, relative, "runtime", "root-only")
            entry["exclusion_reason"] = RUNTIME_METADATA_ONLY[relative]
            entries.append(entry)
            continue
        if relative.startswith("."):
            entry = basic_entry(child, relative, "runtime", "root-only")
            entry["exclusion_reason"] = "hidden user/runtime root; no reorganization without a separate operator decision"
            entries.append(entry)
            continue
        if child.is_dir() and not child.is_symlink():
            entry = basic_entry(child, relative, "local", "scanned")
            entries.append(entry)
            walk_local(child, relative, entries, hash_cache)
        else:
            entry = basic_entry(child, relative, "local", "scanned")
            if entry["kind"] == "file":
                try:
                    entry["sha256"] = file_hash(child)
                except OSError as exc:
                    entry["hash_error"] = f"{type(exc).__name__}: {exc}"
            entries.append(entry)

    entries.sort(key=lambda item: item["relative_path"])
    counts = Counter((item["scope"], item["kind"]) for item in entries)
    hashed = [item for item in entries if "sha256" in item]
    payload = {
        "schema": "mak-canonical-map-v1",
        "generated_at": utc_now(),
        "root": str(ROOT),
        "purpose": "single current filesystem inventory and content hash map for the local MAK surface",
        "authority": "filesystem measurement at generation time; it does not prove service health or artistic meaning",
        "git_policy": "Git commands and .git internals excluded; repository working files are read-only evidence unless separately authorized",
        "protected_policy": "WIN, curatoria_inbox, GoogleDrive and OneDrive are recorded at root only and never traversed",
        "runtime_policy": "hidden user/runtime roots are recorded at root only to avoid treating caches, credentials or application state as project material",
        "top_level_entries": top_level,
        "measurement_commands": [
            "python3 /home/mak/tools/build_mak_canonical_map.py",
            "python3 -m json.tool /home/mak/indexes/mak-canonical-20260829/mak-canonical-map.json",
        ],
        "summary": {
            "entry_count": len(entries),
            "hashed_file_count": len(hashed),
            "hashed_bytes": sum(item.get("size_bytes", 0) for item in hashed),
            "counts_by_scope_kind": {f"{scope}:{kind}": count for (scope, kind), count in sorted(counts.items())},
            "hash_errors": sum(1 for item in entries if "hash_error" in item),
            "unreadable_entries": sum(1 for item in entries if item["kind"] == "unreadable"),
        },
        "entries": entries,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=True, sort_keys=True))
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
