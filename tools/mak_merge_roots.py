#!/usr/bin/env python3
"""Merge duplicate MAK roots into the canonical flujo tree, fail-closed.

The operator's box contains historical, runner and cache copies of the same
project.  This tool maps them to one destination without treating a filename
or a clean-looking directory as authority:

* regular files are compared by SHA-256, with inode-aware hash reuse;
* identical content is kept once at the destination and logged as a duplicate;
* divergent content is preserved below ``_archive/<run>/variants/<source-id>/``;
* every applied action is appended to a JSONL log and verified after copying;
* source roots are never removed by ``--apply``.  ``--retire-sources`` moves a
  source into the destination only after the copy plan succeeds and leaves a
  symlink redirect at its old path.

The default destination is ``/home/mak/flujo``.  The scanner discovers only
directories named ``flujo`` or ``vibecodeine``; generated internals such as
``.git``, virtual environments, caches and node_modules are recorded as
excluded rather than merged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


HOME = Path("/home/mak")
DEFAULT_DEST = HOME / "flujo"
RUN_ID = "mak-merge-20260831"
ARCHIVE_ID = RUN_ID.removeprefix("mak-")
PLAN_PATH = DEFAULT_DEST / "context" / RUN_ID / "plan.json"
LOG_PATH = DEFAULT_DEST / "context" / RUN_ID / "actions.jsonl"
ARCHIVE_ROOT_NAME = "_archive"
ARCHIVE_BASE = HOME / ARCHIVE_ROOT_NAME

SOURCE_NAMES = {"flujo", "vibecodeine"}
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
}
SKIP_FILES = {".env", ".env.local", ".env.production"}
DISCOVERY_PRUNE_DIRS = SKIP_DIRS | {
    "_archive",
    "OneDrive",
    "GoogleDrive",
    "site-packages",
    "dist-packages",
}
HASH_SUFFIXES = {
    ".py",
    ".pyi",
    ".sh",
    ".js",
    ".mjs",
    ".cjs",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".md",
    ".txt",
    ".xml",
    ".html",
    ".css",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def source_id(path: Path) -> str:
    rel = path.relative_to(HOME).as_posix()
    safe = "-".join(part for part in rel.split("/") if part)
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", safe.lower()) or "root"


def source_mode(path: Path) -> str:
    """Return ``repo`` for live checkouts and ``snapshot`` for evidence/caches."""
    rel = path.relative_to(HOME).as_posix()
    if rel.startswith(("_archive/", "state/", ".cache/", ".local/", "actions-runner/_work/_PipelineMapping/")):
        return "snapshot"
    if "/src/flujo" in rel or "/projects/flujo" in rel or "/proyectos/flujo" in rel:
        return "snapshot"
    return "repo"


def is_under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def archive_run(destination: Path) -> Path:
    """Return the durable archive outside the active checkout when possible."""
    if destination.resolve() == DEFAULT_DEST.resolve():
        return ARCHIVE_BASE / ARCHIVE_ID
    return destination / ARCHIVE_ROOT_NAME / ARCHIVE_ID


def action_target(destination: Path, relative: str) -> Path:
    """Resolve an active-relative or snapshot-relative plan location."""
    marker = "__snapshot__/"
    if relative.startswith(marker):
        _, source, source_rel = relative.split("/", 2)
        return archive_run(destination) / "sources" / source / source_rel
    return destination / relative


def discover_roots(home: Path = HOME, destination: Path = DEFAULT_DEST) -> list[Path]:
    """Discover outermost named roots, preferring a nested checkout with .git."""
    candidates: list[Path] = []
    for current, dirnames, _filenames in os.walk(home, topdown=True, followlinks=False):
        dirnames[:] = sorted(name for name in dirnames if name not in DISCOVERY_PRUNE_DIRS)
        path = Path(current)
        if path.is_symlink() or is_under(path, destination) or path.name.lower() not in SOURCE_NAMES:
            continue
        candidates.append(path)

    selected: list[Path] = []
    for candidate in sorted(candidates, key=lambda item: (len(item.parts), str(item))):
        ancestors = [item for item in selected if is_under(candidate, item)]
        if not ancestors:
            selected.append(candidate)
            continue
        nearest = max(ancestors, key=lambda item: len(item.parts))
        # Runner work directories can be named vibecodeine while the actual
        # checkout is their child. Prefer the child checkout in that case.
        if (candidate / ".git").exists() and not (nearest / ".git").exists():
            selected.remove(nearest)
            selected.append(candidate)
    return sorted(selected, key=str)


@dataclass
class FileRecord:
    source: str
    source_id: str
    source_rel: str
    destination_rel: str
    source_mode: str
    kind: str
    size_bytes: int
    mode: str
    mtime_ns: int
    sha256: str | None = None
    link_target: str | None = None
    excluded_reason: str | None = None


def sha256(path: Path, cache: dict[tuple[int, int, int, int], str]) -> str:
    info = path.stat()
    key = (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)
    if key in cache:
        return cache[key]
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    value = digest.hexdigest()
    cache[key] = value
    return value


def iter_records(root: Path, destination: Path, cache: dict) -> Iterable[FileRecord]:
    sid = source_id(root)
    root_mode = source_mode(root)
    for current, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        kept_dirs: list[str] = []
        for name in sorted(dirnames):
            if name in SKIP_DIRS:
                yield FileRecord(
                    str(current_path / name), sid, "", "", root_mode, "excluded", 0, "", 0,
                    excluded_reason=f"generated directory: {name}",
                )
            else:
                kept_dirs.append(name)
        dirnames[:] = kept_dirs
        for name in sorted(filenames):
            path = current_path / name
            source_rel = path.relative_to(root).as_posix()
            destination_rel = source_rel
            try:
                info = path.lstat()
            except OSError as exc:
                yield FileRecord(
                    str(path), sid, source_rel, destination_rel, root_mode, "unreadable", 0, "", 0,
                    excluded_reason=f"{type(exc).__name__}: {exc}",
                )
                continue
            file_mode = stat.filemode(info.st_mode)
            if name in SKIP_FILES:
                yield FileRecord(
                    str(path), sid, source_rel, destination_rel, root_mode, "excluded", info.st_size,
                    file_mode, info.st_mtime_ns, excluded_reason="credential-bearing env file",
                )
                continue
            if stat.S_ISLNK(info.st_mode):
                yield FileRecord(
                    str(path), sid, source_rel, destination_rel, root_mode, "symlink", info.st_size,
                    file_mode, info.st_mtime_ns, link_target=os.readlink(path),
                )
            elif stat.S_ISREG(info.st_mode):
                digest = None
                if path.suffix.lower() in HASH_SUFFIXES:
                    try:
                        digest = sha256(path, cache)
                    except OSError as exc:
                        yield FileRecord(
                            str(path), sid, source_rel, destination_rel, root_mode, "unreadable",
                            info.st_size, file_mode, info.st_mtime_ns,
                            excluded_reason=f"hash failed: {type(exc).__name__}: {exc}",
                        )
                        continue
                yield FileRecord(
                    str(path), sid, source_rel, destination_rel, root_mode, "file", info.st_size,
                    file_mode, info.st_mtime_ns, sha256=digest,
                )
            else:
                yield FileRecord(
                    str(path), sid, source_rel, destination_rel, root_mode, "special", info.st_size,
                    file_mode, info.st_mtime_ns, excluded_reason="non-regular file",
                )


def ensure_hash(record: FileRecord, cache: dict[tuple[int, int, int, int], str]) -> str | None:
    if record.kind != "file":
        return None
    if record.sha256:
        return record.sha256
    try:
        record.sha256 = sha256(Path(record.source), cache)
    except OSError as exc:
        record.excluded_reason = f"hash failed: {type(exc).__name__}: {exc}"
        record.kind = "unreadable"
        return None
    return record.sha256


def load_plan(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_plan(roots: list[Path], destination: Path) -> dict:
    cache: dict[tuple[int, int, int, int], str] = {}
    records: list[FileRecord] = []
    for root in roots:
        records.extend(iter_records(root, destination, cache))

    for record in records:
        if record.source_mode == "snapshot" and record.destination_rel:
            record.destination_rel = (
                f"__snapshot__/{record.source_id}/{record.source_rel}"
            )

    by_destination: dict[str, list[FileRecord]] = defaultdict(list)
    for record in records:
        if record.kind in {"file", "symlink", "special", "unreadable"}:
            by_destination[record.destination_rel].append(record)

    actions: list[dict] = []
    hash_groups: dict[str, list[str]] = defaultdict(list)
    for relative, items in sorted(by_destination.items()):
        target = action_target(destination, relative)
        target_record = None
        if target.is_file() and not target.is_symlink():
            try:
                target_hash = sha256(target, cache)
            except OSError:
                target_hash = None
            target_record = {"path": str(target), "sha256": target_hash}

        file_items = [item for item in items if item.kind == "file"]
        # Hash source files when they can collide with each other or with a
        # destination file.  Unique binary payloads are copied and hashed
        # during apply; Python/config/text files were already hashed at scan
        # time and feed the duplicate report.
        if len(file_items) > 1 or target_record is not None:
            for item in file_items:
                ensure_hash(item, cache)
        for item in file_items:
            if item.sha256:
                hash_groups[item.sha256].append(f"{item.source}:{item.source_rel}")
        unique_hashes = {item.sha256 for item in file_items}
        archived_hashes: dict[tuple[str, str], str] = {}
        for item in file_items:
            archived = archive_run(destination) / "sources" / item.source_id / item.source_rel
            if not archived.is_file():
                continue
            try:
                archived_hashes[(item.source_id, item.source_rel)] = sha256(archived, cache)
            except OSError:
                continue
        if target_record and target_record["sha256"] in unique_hashes:
            actions.append({
                "operation": "duplicate_exact_existing",
                "destination": str(target),
                "destination_rel": relative,
                "sha256": target_record["sha256"],
                "sources": [item.source for item in file_items if item.sha256 == target_record["sha256"]],
            })
        elif len(unique_hashes) <= 1 and file_items:
            winner = sorted(file_items, key=lambda item: (item.source_id, item.source_rel))[0]
            already_archived = (
                winner.source_mode == "repo"
                and winner.sha256 is not None
                and archived_hashes.get((winner.source_id, winner.source_rel)) == winner.sha256
            )
            actions.append({
                "operation": (
                    "record_snapshot" if winner.source_mode == "snapshot" else
                    ("duplicate_exact_archived" if already_archived else
                     ("copy_unique" if not target.exists() else "conflict_existing_unhashed"))
                ),
                "source": winner.source,
                "source_id": winner.source_id,
                "source_rel": winner.source_rel,
                "destination": str(target),
                "destination_rel": relative,
                "sha256": winner.sha256,
                "size_bytes": winner.size_bytes,
                "source_mode": winner.source_mode,
            })
        elif len(unique_hashes) > 1:
            for item in sorted(file_items, key=lambda entry: (entry.source_id, entry.source_rel)):
                variant = (
                    archive_run(destination) / "variants"
                    / item.source_id / relative
                )
                actions.append({
                    "operation": "record_snapshot" if item.source_mode == "snapshot" else "preserve_variant",
                    "source": item.source,
                    "source_id": item.source_id,
                    "source_rel": item.source_rel,
                    "destination": str(variant),
                    "destination_rel": relative,
                    "sha256": item.sha256,
                    "size_bytes": item.size_bytes,
                    "source_mode": item.source_mode,
                })
        else:
            for item in items:
                actions.append({
                    "operation": "record_non_file",
                    "source": item.source,
                    "source_id": item.source_id,
                    "source_rel": item.source_rel,
                    "destination_rel": relative,
                    "kind": item.kind,
                    "link_target": item.link_target,
                    "excluded_reason": item.excluded_reason,
                    "source_mode": item.source_mode,
                })

    return {
        "schema": "mak-merge-plan-v1",
        "generated_at": utc_now(),
        "destination": str(destination),
        "sources": [str(root) for root in roots],
        "source_modes": {str(root): source_mode(root) for root in roots},
        "excluded_directory_count": sum(1 for item in records if item.kind == "excluded"),
        "record_count": len(records),
        "python_record_count": sum(
            1 for item in records if item.source_rel.endswith(".py") and item.kind == "file"
        ),
        "duplicate_hash_groups": {
            digest: sorted(paths) for digest, paths in hash_groups.items() if len(paths) > 1
        },
        "actions": actions,
        "summary": {
            operation: sum(1 for action in actions if action["operation"] == operation)
            for operation in sorted({action["operation"] for action in actions})
        },
    }


def append_log(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"at": utc_now(), **payload}, ensure_ascii=True) + "\n")


def apply_plan(plan: dict, *, retire_sources: bool = False) -> dict:
    destination = Path(plan["destination"])
    log_path = destination / "context" / RUN_ID / "actions.jsonl"
    result = {"applied": 0, "verified": 0, "failed": 0, "retired": 0}
    for action in plan["actions"]:
        operation = action["operation"]
        if operation not in {"copy_unique", "preserve_variant", "conflict_existing_unhashed"}:
            continue
        source = Path(action["source"])
        target = Path(action["destination"])
        try:
            if target.exists() or target.is_symlink():
                if target.is_file() and not target.is_symlink() and sha256(target, {}) == action["sha256"]:
                    append_log(log_path, {"operation": "already_verified", **action})
                    result["verified"] += 1
                    continue
                if operation == "conflict_existing_unhashed":
                    variant = (
                        archive_run(destination) / "variants"
                        / action["source_id"] / action["destination_rel"]
                    )
                    target = variant
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            observed = sha256(target, {})
            if action.get("sha256") and observed != action["sha256"]:
                raise RuntimeError(f"hash mismatch after copy: {observed}")
            append_log(log_path, {"operation": operation, "status": "applied", **action, "verified_sha256": observed})
            result["applied"] += 1
            result["verified"] += 1
        except (OSError, RuntimeError) as exc:
            append_log(log_path, {"operation": operation, "status": "failed", **action, "error": str(exc)})
            result["failed"] += 1

    if retire_sources and result["failed"] == 0:
        merge_sources = archive_run(destination) / "sources"
        for source in plan["sources"]:
            source_path = Path(source)
            if not source_path.exists() or is_under(source_path, destination):
                continue
            relocated = merge_sources / source_id(source_path)
            try:
                relocated.parent.mkdir(parents=True, exist_ok=True)
                if relocated.exists() or relocated.is_symlink():
                    raise RuntimeError(f"retirement destination exists: {relocated}")
                shutil.move(str(source_path), str(relocated))
                source_path.symlink_to(os.path.relpath(relocated, source_path.parent), target_is_directory=True)
                append_log(log_path, {
                    "operation": "retire_source_with_redirect",
                    "status": "applied",
                    "source": str(source_path),
                    "redirect": str(relocated),
                })
                result["retired"] += 1
            except (OSError, RuntimeError) as exc:
                append_log(log_path, {
                    "operation": "retire_source_with_redirect",
                    "status": "failed",
                    "source": str(source_path),
                    "redirect": str(relocated),
                    "error": str(exc),
                })
                result["failed"] += 1
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", default=str(DEFAULT_DEST))
    parser.add_argument("--source", action="append", help="explicit source root; repeatable")
    parser.add_argument("--plan", default=str(PLAN_PATH), help="plan JSON path")
    parser.add_argument("--apply", action="store_true", help="apply copy/variant actions")
    parser.add_argument("--retire-sources", action="store_true", help="move sources inside destination and leave redirects")
    args = parser.parse_args()

    destination = Path(args.destination).resolve()
    roots = [Path(item).resolve() for item in args.source] if args.source else discover_roots(destination=destination)
    roots = [root for root in roots if root != destination and root.exists()]
    plan = build_plan(roots, destination)
    plan_path = Path(args.plan)
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(json.dumps(plan, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "mode": "apply" if args.apply else "plan",
        "destination": str(destination),
        "sources": roots,
        "records": plan["record_count"],
        "python_records": plan["python_record_count"],
        "duplicate_hash_groups": len(plan["duplicate_hash_groups"]),
        "summary": plan["summary"],
        "plan": str(plan_path),
    }, default=str, ensure_ascii=True, sort_keys=True))
    if not args.apply:
        return 0
    result = apply_plan(plan, retire_sources=args.retire_sources)
    print(json.dumps({"result": result, "log": str(destination / "context" / RUN_ID / "actions.jsonl")}, sort_keys=True))
    return 0 if result["failed"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
