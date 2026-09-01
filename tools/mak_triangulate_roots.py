#!/usr/bin/env python3
"""Triangulate competing MAK roots from metadata, not from prose.

This is deliberately a metadata pass.  It does not import project modules or
interpret their contents.  It compares inode dates, byte hashes and Git
history so an old implementation (for example the June airdrop engine) is
not silently mistaken for a disposable duplicate.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from mak_merge_roots import DISCOVERY_PRUNE_DIRS, HOME, RUN_ID, discover_roots, source_id, source_mode


OUT_DIR = HOME / "flujo" / "context" / RUN_ID
TEMP_BASES = (HOME / ".claude" / "jobs", HOME / "state")
TEMP_PARTS = {"tmp", "temp", "temporary", "scratch", "tmpfiles"}
CODE_SUFFIXES = {".py", ".pyi"}


def _is_checkout(root: Path) -> bool:
    """Return true only for a real checkout rooted here.

    A compatibility adapter may expose a symlink named ``.git`` to its parent
    repository, and an rclone snapshot may contain an empty placeholder
    directory.  Neither is an independent checkout whose history belongs in
    the root matrix.
    """
    marker = root / ".git"
    if marker.is_symlink():
        return False
    if marker.is_file():
        return True  # linked worktree: .git is a gitdir file
    return marker.is_dir() and (marker / "HEAD").is_file()


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


def _birth(path: Path) -> int | None:
    """Linux birth time; None means the filesystem did not expose one."""
    result = subprocess.run(["stat", "-c", "%W", str(path)], capture_output=True, text=True)
    value = result.stdout.strip()
    try:
        parsed = int(value)
    except ValueError:
        return None
    return parsed if parsed >= 0 else None


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_file_history(root: Path) -> dict[str, dict[str, str]]:
    """Build first/last path dates with one log walk per checkout."""
    if not _is_checkout(root):
        return {}
    text = _git(root, "log", "--all", "--format=commit%x09%cI", "--name-only")
    current_date = ""
    dates: dict[str, list[str]] = defaultdict(list)
    for line in text.splitlines():
        if line.startswith("commit\t"):
            current_date = line.split("\t", 1)[1]
        elif line and current_date and not line.startswith(" "):
            dates[line].append(current_date)
    return {path: {"first": min(values), "last": max(values)} for path, values in dates.items()}


def _root_meta(root: Path) -> dict[str, object]:
    stat_result = root.stat()
    # Do not let Git walk up into /home/mak when a discovered snapshot is not
    # itself a checkout.  A parent repository's HEAD/dirty state is not
    # evidence about that snapshot and previously made the matrix misleading.
    has_git = _is_checkout(root)
    if has_git:
        first = _git(root, "log", "--reverse", "--format=%cI", "--all", "-1")
        head = _git(root, "rev-parse", "HEAD")
        remote = _git(root, "remote", "get-url", "origin")
        dirty = bool(_git(root, "status", "--porcelain"))
    else:
        first = head = remote = ""
        dirty = None
    files = 0
    python_files = 0
    for current, dirs, names in os.walk(root, topdown=True, followlinks=False):
        dirs[:] = sorted(name for name in dirs if name not in DISCOVERY_PRUNE_DIRS)
        for name in names:
            files += 1
            if Path(name).suffix.lower() in CODE_SUFFIXES:
                python_files += 1
    return {
        "path": str(root),
        "source_id": source_id(root),
        "source_mode": source_mode(root),
        "has_git": has_git,
        "birth_epoch": _birth(root),
        "mtime_epoch": stat_result.st_mtime_ns,
        "git_first_commit": first,
        "git_head": head,
        "git_remote": remote,
        "git_dirty": dirty,
        "file_count": files,
        "python_file_count": python_files,
    }


def _file_meta(path: Path, root: Path, history: dict[str, dict[str, str]], *, role: str) -> dict[str, object]:
    stat_result = path.stat()
    rel = path.relative_to(root).as_posix()
    row: dict[str, object] = {
        "path": str(path),
        "root": str(root),
        "source_id": source_id(root),
        "relative": rel,
        "role": role,
        "size_bytes": stat_result.st_size,
        "birth_epoch": _birth(path),
        "mtime_epoch": stat_result.st_mtime_ns,
        "sha256": _hash(path),
    }
    row.update(history.get(rel, {}))
    return row


def _candidate_files(root: Path, history: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    rows = []
    for current, dirs, names in os.walk(root, topdown=True, followlinks=False):
        dirs[:] = sorted(name for name in dirs if name not in DISCOVERY_PRUNE_DIRS)
        for name in names:
            path = Path(current) / name
            if path.suffix.lower() not in CODE_SUFFIXES:
                continue
            lowered = name.lower()
            if any(token in lowered for token in ("airdrop", "reception", "checkpoint", "import_claude")):
                role = "historical-family-candidate"
            elif any(part.lower() in TEMP_PARTS for part in path.relative_to(root).parts):
                role = "temporary-python"
            else:
                continue
            try:
                rows.append(_file_meta(path, root, history, role=role))
            except OSError as exc:
                rows.append({"path": str(path), "root": str(root), "role": role, "error": str(exc)})
    return rows


def _temporary_files() -> list[dict[str, object]]:
    rows = []
    for base in TEMP_BASES:
        if not base.is_dir():
            continue
        for current, dirs, names in os.walk(base, topdown=True, followlinks=False):
            dirs[:] = sorted(name for name in dirs if name not in DISCOVERY_PRUNE_DIRS)
            current_path = Path(current)
            for name in names:
                path = current_path / name
                if path.suffix.lower() not in CODE_SUFFIXES:
                    continue
                try:
                    rel = path.relative_to(base)
                    if not any(part.lower() in TEMP_PARTS for part in rel.parts):
                        continue
                    rows.append(_file_meta(path, base, {}, role="temporary-python"))
                except OSError as exc:
                    rows.append({"path": str(path), "root": str(base), "role": "temporary-python", "error": str(exc)})
    return rows


def _redirect_targets() -> list[Path]:
    """Include resolved targets of named-root symlinks in the evidence matrix."""
    found: list[Path] = []
    for parent in (HOME / "WIN", HOME / "actions-runner" / "_work" / "vibecodeine"):
        if not parent.is_dir():
            continue
        for child in parent.iterdir():
            if child.name.lower() in {"flujo", "vibecodeine"} and child.is_symlink():
                target = child.resolve()
                if target.is_dir():
                    found.append(target)
    return found


def main() -> int:
    roots = discover_roots(destination=HOME / "flujo")
    for target in _redirect_targets():
        if target not in roots:
            roots.append(target)
    roots = sorted(roots, key=str)
    root_rows = [_root_meta(root) for root in roots]
    candidate_rows: list[dict[str, object]] = []
    for root in roots:
        history = _git_file_history(root)
        candidate_rows.extend(_candidate_files(root, history))
    candidate_rows.extend(_temporary_files())
    by_hash: dict[str, list[str]] = defaultdict(list)
    for row in candidate_rows:
        digest = row.get("sha256")
        if digest:
            by_hash[str(digest)].append(str(row["path"]))
    duplicate_groups = {
        digest: sorted(paths) for digest, paths in by_hash.items() if len(paths) > 1
    }
    result = {
        "schema": "mak-root-triangulation-v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "method": ["inode_birth", "mtime", "sha256", "git_first_last_path_commit", "root_git_metadata"],
        "roots": root_rows,
        "candidates": candidate_rows,
        "duplicate_candidate_hashes": duplicate_groups,
        "counts": {
            "roots": len(root_rows),
            "candidates": len(candidate_rows),
            "temporary_python": sum(row.get("role") == "temporary-python" for row in candidate_rows),
            "historical_family_candidates": sum(row.get("role") == "historical-family-candidate" for row in candidate_rows),
            "duplicate_hash_groups": len(duplicate_groups),
        },
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "triangulation.json").write_text(json.dumps(result, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Triangulación de raíces MAK",
        "",
        "Generada automáticamente con metadatos; no interpreta el contenido de los archivos.",
        "",
        f"- raíces: {len(root_rows)}",
        f"- candidatos de familias históricas: {result['counts']['historical_family_candidates']}",
        f"- `.py` temporales: {result['counts']['temporary_python']}",
        f"- grupos de hash duplicado entre candidatos: {len(duplicate_groups)}",
        "",
        "## Señales por raíz",
        "",
        "| raíz | modo | primer commit | nacimiento inode | Python | dirty |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in root_rows:
        lines.append(
            f"| `{row['path']}` | {row['source_mode']} | {row['git_first_commit'] or 'n/a'} | "
            f"{row['birth_epoch'] or 'n/a'} | {row['python_file_count']} | "
            f"{row['git_dirty'] if row['git_dirty'] is not None else 'n/a'} |"
        )
    (OUT_DIR / "triangulation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT_DIR), "counts": result["counts"]}, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
