#!/usr/bin/env python3
"""Observe, plan, or explicitly apply a non-destructive MAK transport.

The default is a read-only plan.  Git is a transport checkpoint, never the
authority for local material.  Runtime state, databases, memories, mounts,
logs, private files, and generated products are excluded from versioned
transport and are never replaced by this module.
"""
from __future__ import annotations

import argparse
import datetime as dt
try:
    import fcntl
except ImportError:  # pragma: no cover - MAK runs Linux; fixtures run on Windows.
    fcntl = None  # type: ignore[assignment]
try:
    import msvcrt
except ImportError:  # pragma: no cover - Windows only.
    msvcrt = None  # type: ignore[assignment]
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any, Iterable


TARGET_REF = "origin/main"
DIRECTION = "git-to-runtime"
SCHEMA = "mak-transport-v2"
JOURNAL_SCHEMA = "mak-transport-journal-v2"
GIT_TIMEOUT_SECONDS = 30
WINDOWS_REPARSE_POINT = 0x0400
# Legacy ``"schema": "mak-deploy-v1"`` manifests are intentionally not
# accepted; they lack the source/target inventory and resumable journal.
EXCLUDED_DIRS = frozenset({
    ".git", ".venv", "venv", "__pycache__", "logs", "memoria", "memory",
    "backups", "rollback", "mounts", "mounted", "generated", "outputs",
    "informes", "paneles", "cache", "caches",
})
EXCLUDED_SUFFIXES = (".db", ".sqlite", ".sqlite3", ".sqlite-wal", ".sqlite-shm")
EXCLUDED_NAMES = frozenset({".env", ".env.local", ".env.production"})


@dataclass(frozen=True)
class Settings:
    deploy_repo: Path
    user_repo: Path
    lock_path: Path
    manifest_path: Path
    backup_root: Path
    recovery_root: Path
    staging_root: Path


SOURCES = {
    "mak_plataforma": ("cultura/mak_plataforma", "/home/mak/plataforma"),
    "mak_research": ("cultura/mak_research", "/home/mak/research"),
    "mak_codex": ("cultura/mak_codex", "/home/mak/codex"),
    "mak_curatoria": ("cultura/mak_curatoria", "/home/mak/curatoria"),
}


def settings_from_env() -> Settings:
    return Settings(
        deploy_repo=Path(os.environ.get("MAK_DEPLOY_REPO", "/home/mak/flujo-deploy")),
        user_repo=Path(os.environ.get("MAK_USER_REPO", "/home/mak/flujo")),
        lock_path=Path(os.environ.get("MAK_SYNC_LOCK", "/home/mak/.cache/mak-sync.lock")),
        manifest_path=Path(os.environ.get(
            "MAK_SYNC_MANIFEST", "/home/mak/plataforma/deploy_manifest.json")),
        backup_root=Path(os.environ.get(
            "MAK_SYNC_BACKUP_ROOT", "/home/mak/rollback/mak-sync")),
        recovery_root=Path(os.environ.get(
            "MAK_SYNC_RECOVERY_ROOT", "/home/mak/rollback/mak-sync-recovery")),
        staging_root=Path(os.environ.get(
            "MAK_SYNC_STAGING_ROOT", "/home/mak/rollback/mak-sync-staging")),
    )


def settings_path_errors(settings: Settings) -> list[str]:
    errors: list[str] = []
    deploy = settings.deploy_repo.resolve(strict=False)
    user = settings.user_repo.resolve(strict=False)
    if not deploy.is_dir() or _is_link_or_reparse(deploy):
        errors.append("deploy worktree is missing or linked")
    if deploy == user:
        errors.append("deploy worktree equals human checkout")
    target_roots: list[Path] = []
    for component, (source_rel, target_root) in SOURCES.items():
        source_raw = deploy / PurePosixPath(source_rel)
        target_raw = Path(target_root)
        source = source_raw.resolve(strict=False)
        target = target_raw.resolve(strict=False)
        if not _within(source, deploy, allow_equal=False):
            errors.append(f"{component}: source root escapes deploy worktree")
        if not source.is_dir() or _path_has_link_component(source_raw):
            errors.append(f"{component}: source root is missing or linked")
        if not target.is_dir() or _path_has_link_component(target_raw):
            errors.append(f"{component}: target root is missing or linked")
        if _within(target, deploy) or _within(target, user):
            errors.append(f"{component}: target root overlaps a protected checkout")
        target_roots.append(target)
    for index, left in enumerate(target_roots):
        for right in target_roots[index + 1:]:
            if _within(left, right) or _within(right, left):
                errors.append("runtime target roots overlap")
    protected = [deploy, user, *target_roots]
    for label, configured in (
        ("backup", settings.backup_root),
        ("recovery", settings.recovery_root),
        ("staging", settings.staging_root),
    ):
        path = configured.resolve(strict=False)
        if any(_within(path, root) for root in protected):
            errors.append(f"{label} root overlaps a protected path")
        if _path_has_link_component(path.parent):
            errors.append(f"{label} root parent is linked")
    return sorted(set(errors))


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    command = ["git", "-C", str(repo), *args]
    try:
        return subprocess.run(
            command,
            text=True,
            encoding="utf-8",
            errors="surrogateescape",
            capture_output=True,
            check=False,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(
            command, 124, exc.stdout or "", exc.stderr or "git command timed out"
        )
    except OSError as exc:
        return subprocess.CompletedProcess(command, 127, "", str(exc))


def blocked(message: str, *, code: int = 20) -> int:
    print(f"BLOCKED: {message}", file=sys.stderr)
    return code


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_link_or_reparse(path: Path) -> bool:
    """Reject symlinks and Windows junction/reparse points."""
    try:
        if os.path.islink(path):
            return True
        stat = path.lstat()
    except OSError:
        return False
    return bool(getattr(stat, "st_file_attributes", 0) & WINDOWS_REPARSE_POINT)


def _path_has_link_component(path: Path) -> bool:
    absolute = path if path.is_absolute() else Path.cwd() / path
    current = Path(absolute.anchor) if absolute.anchor else Path()
    for part in absolute.parts[1:] if absolute.anchor else absolute.parts:
        current = current / part
        if current.exists() and _is_link_or_reparse(current):
            return True
    return False


def _within(path: Path, root: Path, *, allow_equal: bool = True) -> bool:
    path = path.resolve(strict=False)
    root = root.resolve(strict=False)
    return (path == root and allow_equal) or root in path.parents


def _valid_relative(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\x00" in value:
        return False
    if "\\" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(part not in {"", ".", ".."} for part in path.parts)


def _safe_child(root: Path, relative: str) -> Path:
    if not _valid_relative(relative):
        raise RuntimeError(f"unsafe relative path: {relative!r}")
    raw_root = root
    if _path_has_link_component(raw_root):
        raise RuntimeError(f"symlink or junction in transport root: {root}")
    root = root.resolve(strict=False)
    candidate = (root / PurePosixPath(relative)).resolve(strict=False)
    if not _within(candidate, root, allow_equal=False):
        raise RuntimeError(f"path escapes approved root: {relative!r}")
    if _path_has_link_component(candidate):
        raise RuntimeError(f"symlink or junction in transport path: {relative!r}")
    return candidate


def _regular_file(path: Path) -> bool:
    return path.is_file() and not _is_link_or_reparse(path)


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(canonical_json(value))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def is_excluded(relative: Path) -> bool:
    parts = tuple(part.casefold() for part in relative.parts)
    if any(part in {item.casefold() for item in EXCLUDED_DIRS} for part in parts):
        return True
    name = relative.name.casefold()
    return name in {item.casefold() for item in EXCLUDED_NAMES} or name.endswith(
        tuple(item.casefold() for item in EXCLUDED_SUFFIXES)
    )


def walk_files(root: Path) -> tuple[dict[str, Path], list[str]]:
    files: dict[str, Path] = {}
    excluded: list[str] = []
    if not root.exists():
        return files, excluded
    for current, dirs, names in os.walk(root, followlinks=False):
        current_path = Path(current)
        kept_dirs: list[str] = []
        for directory in dirs:
            path = current_path / directory
            relative = path.relative_to(root)
            if _is_link_or_reparse(path):
                excluded.append(relative.as_posix() + " [link]")
            elif is_excluded(relative):
                excluded.append(relative.as_posix() + "/")
            else:
                kept_dirs.append(directory)
        dirs[:] = kept_dirs
        for name in names:
            path = current_path / name
            relative = path.relative_to(root)
            if _is_link_or_reparse(path):
                excluded.append(relative.as_posix() + " [link]")
            elif is_excluded(relative):
                excluded.append(relative.as_posix())
            elif path.is_file():
                files[relative.as_posix()] = path
    return dict(sorted(files.items())), sorted(excluded)


def git_inventory(repo: Path) -> dict[str, Any]:
    status = git(
        repo, "status", "--porcelain=v1", "--untracked-files=all",
        "--ignore-submodules=none",
    )
    head = git(repo, "rev-parse", "HEAD")
    tree = git(repo, "rev-parse", "HEAD^{tree}")
    branch = git(repo, "branch", "--show-current")
    remote = git(repo, "rev-parse", TARGET_REF)
    submodules = git(repo, "submodule", "status", "--recursive")
    lines = [line for line in status.stdout.splitlines() if line.strip()]
    untracked = [line[3:] for line in lines if line.startswith("?? ")]
    submodule_lines = [line for line in submodules.stdout.splitlines() if line.strip()]
    submodule_dirty = submodules.returncode != 0 or any(
        line[:1] in {"+", "-", "U"} for line in submodule_lines
    )
    return {
        "root": str(repo),
        "status_exit": status.returncode,
        "status_stderr": status.stderr.strip(),
        "status_porcelain": lines,
        "untracked": sorted(untracked),
        "submodule_status_exit": submodules.returncode,
        "submodule_status": submodule_lines,
        "submodule_dirty": submodule_dirty,
        "dirty": bool(lines) or submodule_dirty,
        "head": head.stdout.strip() if head.returncode == 0 else None,
        "tree": tree.stdout.strip() if tree.returncode == 0 else None,
        "branch": branch.stdout.strip() if branch.returncode == 0 else None,
        "target_ref": TARGET_REF,
        "target_ref_hash": remote.stdout.strip() if remote.returncode == 0 else None,
    }


def path_record(path: Path, relative: str) -> dict[str, Any]:
    stat = path.stat()
    return {
        "path": relative,
        "hash": sha256(path),
        "mtime_ns": stat.st_mtime_ns,
        "size": stat.st_size,
    }


def load_previous(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def previous_hashes(previous: dict[str, Any]) -> dict[str, str]:
    completed = previous.get("status") == "completed"
    return {
        f"{item.get('component', '')}:{item['path']}": str(
            item.get("deployed_source_hash") or item.get("source_hash")
            if completed else item.get("previous_source_hash")
        )
        for item in previous.get("managed_files", [])
        if isinstance(item, dict) and item.get("path") and (
            item.get("source_hash") or item.get("previous_source_hash")
        ) and (
            (completed and (item.get("deployed_source_hash") or item.get("source_hash")))
            or (not completed and item.get("previous_source_hash"))
        )
    }


def compare_files(
    source: dict[str, Path],
    target: dict[str, Path],
    previous: dict[str, Any],
    component: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    old = previous_hashes(previous)
    records: list[dict[str, Any]] = []
    untracked: list[str] = []
    for relative, target_path in target.items():
        if relative not in source:
            untracked.append(relative)
    for relative, source_path in source.items():
        source_item = path_record(source_path, relative)
        target_path = target.get(relative)
        if target_path is None:
            state = "missing"
            target_item = None
        else:
            target_item = path_record(target_path, relative)
            if target_item["hash"] == source_item["hash"]:
                state = "same"
            elif target_item["mtime_ns"] > source_item["mtime_ns"]:
                state = "target_newer"
            elif f"{component}:{relative}" in old and target_item["hash"] == old[f"{component}:{relative}"]:
                state = "source_newer"
            else:
                state = "dirty_target"
        records.append({
            "path": relative,
            "component": component,
            "source_hash": source_item["hash"],
            "previous_source_hash": old.get(f"{component}:{relative}"),
            "source_mtime_ns": source_item["mtime_ns"],
            "source_size": source_item["size"],
            "target_hash": target_item["hash"] if target_item else None,
            "target_mtime_ns": target_item["mtime_ns"] if target_item else None,
            "target_size": target_item["size"] if target_item else None,
            "state": state,
        })
    return records, sorted(untracked)


def inventory(settings: Settings, previous: dict[str, Any] | None = None) -> dict[str, Any]:
    previous = previous or {}
    source_git = git_inventory(settings.deploy_repo)
    components: dict[str, Any] = {}
    all_reasons: list[str] = settings_path_errors(settings)
    for name, (source_rel, target_root) in SOURCES.items():
        source_root = settings.deploy_repo / source_rel
        source_files, source_excluded = walk_files(source_root)
        target_path = Path(target_root)
        target_files, target_excluded = walk_files(target_path)
        managed, untracked = compare_files(source_files, target_files, previous, name)
        for item in managed:
            item["component"] = name
        for item in managed:
            if item["state"] in {"target_newer", "dirty_target"}:
                all_reasons.append(f"{name}:{item['path']}:{item['state']}")
        if untracked:
            all_reasons.append(f"{name}:untracked:{','.join(untracked)}")
        components[name] = {
            "source_root": str(source_root),
            "target_root": str(target_path),
            "managed_files": managed,
            "source_excluded": source_excluded,
            "target_excluded": target_excluded,
            "target_untracked": untracked,
        }
    if source_git["status_exit"] != 0:
        all_reasons.append("source_git_status_unavailable")
    if source_git["submodule_status_exit"] != 0:
        all_reasons.append("source_git_submodule_status_unavailable")
    if source_git["dirty"]:
        all_reasons.append("source_git_dirty_or_untracked")
    return {
        "source_git": source_git,
        "components": components,
        "block_reasons": sorted(set(all_reasons)),
    }


def checkpoint_for(settings: Settings, requested: str | None) -> tuple[str | None, str | None, str | None]:
    source_git = git_inventory(settings.deploy_repo)
    commit = requested or source_git.get("head")
    if not commit:
        return None, None, "source checkpoint is unavailable"
    if source_git.get("head") != commit:
        return None, None, "source HEAD does not match explicit checkpoint"
    tree = git(settings.deploy_repo, "rev-parse", f"{commit}^{{tree}}")
    if tree.returncode != 0:
        return None, None, "checkpoint tree is unavailable"
    return commit, tree.stdout.strip(), None


def operation_id(commit: str, tree: str, target_roots: Iterable[str], records: list[dict[str, Any]]) -> str:
    payload = {
        "direction": DIRECTION,
        "commit": commit,
        "tree": tree,
        "targets": sorted(target_roots),
        "records": records,
    }
    return hashlib.sha256(canonical_json(payload)).hexdigest()[:24]


def build_plan(settings: Settings, direction: str = DIRECTION, checkpoint: str | None = None) -> dict[str, Any]:
    if direction != DIRECTION:
        raise ValueError(f"unsupported direction: {direction}")
    commit, tree, error = checkpoint_for(settings, checkpoint)
    if error:
        raise RuntimeError(error)
    assert commit and tree
    state = inventory(settings, load_previous(settings.manifest_path))
    records = [item for component in state["components"].values() for item in component["managed_files"]]
    operation = operation_id(commit, tree, [v[1] for v in SOURCES.values()], records)
    backup = settings.backup_root / operation
    recovery = settings.recovery_root / operation
    blocked_reasons = list(state["block_reasons"])
    promotion = "blocked" if blocked_reasons else "ready"
    status = "planned"
    return {
        "schema": SCHEMA,
        "operation_id": operation,
        "direction": direction,
        "source_checkpoint": {"commit": commit, "tree": tree, "ref_evidence": state["source_git"]},
        "source_repo": str(settings.deploy_repo),
        "target_roots": {name: target for name, (_, target) in SOURCES.items()},
        "managed_files": records,
        "components": state["components"],
        "excluded_policy": {
            "directories": sorted(EXCLUDED_DIRS),
            "names": sorted(EXCLUDED_NAMES),
            "suffixes": list(EXCLUDED_SUFFIXES),
            "behavior": "preserve-and-never-transport",
        },
        "backup_path": str(backup),
        "recovery_path": str(recovery),
        "promotion_result": {
            "status": promotion,
            "reasons": sorted(blocked_reasons),
            "promoted_files": [],
        },
        "backup_live_drift": [],
        "status": status,
    }


def manifest_paths_are_safe(manifest: dict[str, Any]) -> str | None:
    source_value = manifest.get("source_repo")
    if not isinstance(source_value, str) or not source_value:
        return "manifest source repo is missing"
    source = Path(source_value).resolve(strict=False)
    target_values = manifest.get("target_roots")
    if not isinstance(target_values, dict) or not target_values:
        return "manifest target roots are missing"
    if any(not isinstance(path, str) or not path for path in target_values.values()):
        return "manifest target root is invalid"
    targets = [Path(str(path)).resolve(strict=False) for path in target_values.values()]
    if any(_within(target, source) for target in targets):
        return "runtime target overlaps source repo"
    for index, left in enumerate(targets):
        for right in targets[index + 1:]:
            if _within(left, right) or _within(right, left):
                return "runtime target roots overlap"
    for key in ("backup_path", "recovery_path"):
        value = manifest.get(key)
        if not isinstance(value, str) or not value:
            return f"manifest missing {key}"
        path = Path(value).resolve(strict=False)
        if _within(path, source):
            return f"{key} is inside source repo"
        if any(_within(path, target) for target in targets):
            return f"{key} is inside a runtime target"
    if Path(str(manifest.get("backup_path"))).resolve(strict=False) == Path(
        str(manifest.get("recovery_path"))
    ).resolve(strict=False):
        return "backup and recovery paths must be distinct"
    return None


def _hash_value(value: Any, *, allow_none: bool = False) -> bool:
    if allow_none and value is None:
        return True
    return isinstance(value, str) and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


def validate_manifest_structure(manifest: dict[str, Any], settings: Settings) -> str | None:
    records = manifest.get("managed_files")
    checkpoint = manifest.get("source_checkpoint")
    if not isinstance(records, list) or not isinstance(checkpoint, dict):
        return "manifest inventory is malformed"
    if not isinstance(manifest.get("operation_id"), str):
        return "manifest operation id is missing"
    if not isinstance(checkpoint.get("commit"), str) or not isinstance(checkpoint.get("tree"), str):
        return "manifest checkpoint is malformed"
    seen: set[tuple[str, str]] = set()
    allowed_states = {"same", "missing", "source_newer", "target_newer", "dirty_target"}
    for item in records:
        if not isinstance(item, dict):
            return "manifest file record is malformed"
        component = item.get("component")
        relative = item.get("path")
        if component not in SOURCES or not _valid_relative(relative):
            return "manifest contains an unmanaged or unsafe path"
        key = (str(component), str(relative))
        if key in seen:
            return f"manifest contains duplicate path: {component}:{relative}"
        seen.add(key)
        if not _hash_value(item.get("source_hash")) or not _hash_value(
            item.get("target_hash"), allow_none=True
        ):
            return f"manifest hash is malformed: {component}:{relative}"
        if not isinstance(item.get("source_mtime_ns"), int) or item["source_mtime_ns"] < 0:
            return f"manifest source timestamp is malformed: {component}:{relative}"
        if item.get("target_mtime_ns") is not None and (
            not isinstance(item.get("target_mtime_ns"), int) or item["target_mtime_ns"] < 0
        ):
            return f"manifest target timestamp is malformed: {component}:{relative}"
        if not isinstance(item.get("source_size"), int) or item["source_size"] < 0:
            return f"manifest source size is malformed: {component}:{relative}"
        if item.get("target_size") is not None and (
            not isinstance(item.get("target_size"), int) or item["target_size"] < 0
        ):
            return f"manifest target size is malformed: {component}:{relative}"
        if item.get("state") not in allowed_states:
            return f"manifest state is malformed: {component}:{relative}"
    expected = operation_id(
        checkpoint["commit"], checkpoint["tree"],
        [value[1] for value in SOURCES.values()], records,
    )
    if manifest.get("operation_id") != expected:
        return "manifest operation id does not match its inventory"
    if Path(str(manifest.get("backup_path"))).resolve(strict=False) != (
        settings.backup_root / expected
    ).resolve(strict=False):
        return "manifest backup path is not the configured operation path"
    if Path(str(manifest.get("recovery_path"))).resolve(strict=False) != (
        settings.recovery_root / expected
    ).resolve(strict=False):
        return "manifest recovery path is not the configured operation path"
    return None


def require_separate_deploy_worktree(settings: Settings) -> str | None:
    if settings.deploy_repo.resolve() == settings.user_repo.resolve():
        # Keep the human checkout out of the transport path entirely.
        return "deploy worktree must not be the human checkout"
    if not settings.deploy_repo.is_dir():
        return f"missing deploy worktree: {settings.deploy_repo}"
    return None


def write_plan(settings: Settings, plan: dict[str, Any], path: Path | None = None) -> Path:
    destination = path or settings.manifest_path
    atomic_json(destination, plan)
    return destination


def update_manifest(path: Path, manifest: dict[str, Any], **changes: Any) -> None:
    manifest.update(changes)
    atomic_json(path, manifest)


def current_matches_plan(
    settings: Settings,
    manifest: dict[str, Any],
    completed: set[str] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    state = inventory(settings, manifest)
    reasons = list(state["block_reasons"])
    completed = completed or set()
    planned = {(item["component"], item["path"]): item for item in manifest.get("managed_files", [])}
    current = {
        (item["component"], item["path"]): item
        for component in state["components"].values()
        for item in component["managed_files"]
    }
    if set(planned) != set(current):
        reasons.append("planned inventory differs from current inventory")
    for key, item in planned.items():
        now = current.get(key)
        relative = f"{key[0]}:{key[1]}"
        if now is None:
            reasons.append(f"planned file disappeared: {relative}")
        elif relative in completed:
            if now["target_hash"] != item.get("source_hash"):
                reasons.append(f"completed target is not at source hash: {relative}")
        else:
            for field in (
                "source_hash", "source_mtime_ns", "source_size",
                "target_hash", "target_mtime_ns", "target_size", "state",
            ):
                if now.get(field) != item.get(field):
                    reasons.append(f"{field} changed after plan: {relative}")
    return state, sorted(set(reasons))


def component_for(item: dict[str, Any]) -> tuple[str, str, str] | None:
    name = item.get("component")
    if name not in SOURCES or not _valid_relative(item.get("path")):
        return None
    return name, str(item["path"]), SOURCES[name][1]


def relative_transport_path(item: dict[str, Any]) -> Path:
    if not _valid_relative(item.get("path")) or item.get("component") not in SOURCES:
        raise RuntimeError("unsafe transport path")
    return Path(str(item["component"])) / str(item["path"])


def copy_to_stage(
    settings: Settings,
    manifest: dict[str, Any],
    stage: Path,
    completed: set[str] | None = None,
) -> None:
    expected_stage = (settings.staging_root / str(manifest["operation_id"])).resolve(strict=False)
    if stage.resolve(strict=False) != expected_stage or _path_has_link_component(stage):
        raise RuntimeError("staging path is outside the configured operation root")
    completed = completed or set()
    for item in manifest["managed_files"]:
        if item["state"] == "same" or f"{item['component']}:{item['path']}" in completed:
            continue
        component = component_for(item)
        if component is None:
            raise RuntimeError(f"manifest path is outside managed components: {item['path']}")
        _, relative, _ = component
        source_root = settings.deploy_repo / PurePosixPath(SOURCES[item["component"]][0])
        source = _safe_child(source_root, relative)
        if not _regular_file(source):
            raise RuntimeError(f"source is not a regular file: {item['path']}")
        staged = _safe_child(stage, relative_transport_path(item).as_posix())
        staged.parent.mkdir(parents=True, exist_ok=True)
        staged = _safe_child(stage, relative_transport_path(item).as_posix())
        shutil.copy2(source, staged)
        if sha256(staged) != item["source_hash"]:
            raise RuntimeError(f"source changed while staging: {item['path']}")


def backup_targets(settings: Settings, manifest: dict[str, Any], completed: set[str]) -> None:
    backup_root = Path(manifest["backup_path"])
    for item in manifest["managed_files"]:
        key = f"{item['component']}:{item['path']}"
        if item["state"] == "same" or key in completed or not item.get("target_hash"):
            continue
        component = component_for(item)
        if component is None:
            raise RuntimeError(f"cannot resolve backup path: {item['path']}")
        target = _safe_child(Path(component[2]), component[1])
        if not _regular_file(target):
            raise RuntimeError(f"target is not a regular file: {item['path']}")
        backup = _safe_child(backup_root, relative_transport_path(item).as_posix())
        backup.parent.mkdir(parents=True, exist_ok=True)
        if backup.exists():
            if not _regular_file(backup) or sha256(backup) != item["target_hash"]:
                raise RuntimeError(f"existing backup hash mismatch: {item['path']}")
            continue
        shutil.copy2(target, backup)
        if sha256(backup) != item["target_hash"]:
            raise RuntimeError(f"backup hash mismatch: {item['path']}")


def atomic_journal(path: Path, value: dict[str, Any]) -> None:
    atomic_json(path, value)


def _item_key(item: dict[str, Any]) -> str:
    return f"{item['component']}:{item['path']}"


def _target_for(item: dict[str, Any]) -> Path:
    component = component_for(item)
    if component is None:
        raise RuntimeError(f"unknown managed path: {item.get('path')}")
    return _safe_child(Path(component[2]), component[1])


def _target_matches(item: dict[str, Any], target: Path, *, source_hash: bool = False) -> bool:
    expected_hash = item["source_hash"] if source_hash else item.get("target_hash")
    if _is_link_or_reparse(target):
        return False
    if expected_hash is None:
        return not target.exists()
    if not _regular_file(target):
        return False
    return sha256(target) == expected_hash and (
        source_hash
        or target.stat().st_mtime_ns == item.get("target_mtime_ns")
    )


def verify_source_snapshot(settings: Settings, manifest: dict[str, Any]) -> None:
    source_git = git_inventory(settings.deploy_repo)
    if (
        source_git["status_exit"] != 0
        or source_git["submodule_status_exit"] != 0
        or source_git["dirty"]
        or source_git.get("head") != manifest["source_checkpoint"]["commit"]
    ):
        raise RuntimeError("source Git state changed during transport")
    tree = git(settings.deploy_repo, "rev-parse", "HEAD^{tree}")
    if tree.returncode != 0 or tree.stdout.strip() != manifest["source_checkpoint"]["tree"]:
        raise RuntimeError("source Git tree changed during transport")
    for item in manifest["managed_files"]:
        source_root = settings.deploy_repo / PurePosixPath(SOURCES[item["component"]][0])
        source = _safe_child(source_root, item["path"])
        if not _regular_file(source):
            raise RuntimeError(f"source disappeared or became linked: {item['path']}")
        current = path_record(source, item["path"])
        for field in ("hash", "mtime_ns", "size"):
            expected = item[f"source_{field if field != 'hash' else 'hash'}"]
            if current[field] != expected:
                raise RuntimeError(f"source changed during transport: {item['path']}")


def _normalise_journal(
    journal: dict[str, Any],
    manifest: dict[str, Any],
    settings: Settings,
    manifest_path: Path,
) -> tuple[dict[str, Any] | None, str | None]:
    if journal.get("schema") not in {"mak-transport-journal-v1", JOURNAL_SCHEMA}:
        return None, "recovery journal schema is unsupported"
    if journal.get("operation_id") != manifest["operation_id"]:
        return None, "recovery journal belongs to another operation"
    phase = journal.get("phase")
    if phase not in {"planned", "staging", "promoting", "interrupted", "completed"}:
        return None, "recovery journal phase is invalid"
    if journal.get("status") not in {None, "applying", "interrupted", "completed"}:
        return None, "recovery journal status is invalid"
    completed = journal.get("completed_files", [])
    if not isinstance(completed, list) or any(not isinstance(value, str) for value in completed):
        return None, "recovery journal completed files are malformed"
    by_relative: dict[str, list[str]] = {}
    by_key = {_item_key(item): item for item in manifest["managed_files"]}
    for item in manifest["managed_files"]:
        by_relative.setdefault(item["path"], []).append(_item_key(item))
    converted: list[str] = []
    for value in completed:
        if value in by_key:
            converted.append(value)
            continue
        matches = by_relative.get(value, [])
        if journal.get("schema") == "mak-transport-journal-v1" and len(matches) == 1:
            converted.append(matches[0])
            continue
        return None, f"recovery journal has unknown or ambiguous file: {value}"
    if len(set(converted)) != len(converted):
        return None, "recovery journal contains duplicate completed files"
    expected_stage = (settings.staging_root / manifest["operation_id"]).resolve(strict=False)
    stage_value = journal.get("staging_path")
    stage = expected_stage if stage_value is None else Path(str(stage_value)).resolve(strict=False)
    if stage != expected_stage or _path_has_link_component(stage):
        return None, "recovery journal staging path is outside configured root"
    recorded_manifest = journal.get("manifest")
    if recorded_manifest is not None and Path(str(recorded_manifest)).resolve(strict=False) != manifest_path.resolve(strict=False):
        return None, "recovery journal manifest path does not match"
    journal = dict(journal)
    journal.update({
        "schema": JOURNAL_SCHEMA,
        "manifest": str(manifest_path),
        "completed_files": converted,
        "staging_path": str(expected_stage),
    })
    return journal, None


def apply_manifest(settings: Settings, manifest_path: Path) -> int:
    separate = require_separate_deploy_worktree(settings)
    if separate:
        return blocked(separate)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as exc:
        return blocked(f"cannot read manifest: {exc}")
    if not isinstance(manifest, dict):
        return blocked("manifest must be a JSON object")
    if manifest.get("schema") != SCHEMA:
        return blocked("manifest schema is not mak-transport-v2")
    if manifest.get("direction") != DIRECTION:
        return blocked("manifest direction is not explicit git-to-runtime")
    if manifest.get("status") not in {"planned", "interrupted", "applying"}:
        return blocked("manifest is not resumable")
    settings_errors = settings_path_errors(settings)
    if settings_errors:
        return blocked("unsafe configured transport paths: " + "; ".join(settings_errors[:8]))
    unsafe = manifest_paths_are_safe(manifest)
    if unsafe:
        return blocked(unsafe)
    if Path(str(manifest.get("source_repo", ""))).resolve() != settings.deploy_repo.resolve():
        return blocked("manifest source repo does not match configured deploy worktree")
    expected_targets = {name: target for name, (_, target) in SOURCES.items()}
    if manifest.get("target_roots") != expected_targets:
        return blocked("manifest target roots do not match configured runtime targets")
    structure_error = validate_manifest_structure(manifest, settings)
    if structure_error:
        return blocked(structure_error)
    if manifest.get("status") == "planned" and manifest.get("promotion_result", {}).get("status") != "ready":
        return blocked("plan is not promotable")
    checkpoint = manifest.get("source_checkpoint", {}).get("commit")
    if not checkpoint:
        return blocked("manifest has no checkpoint hash")
    source_git = git_inventory(settings.deploy_repo)
    if (
        source_git.get("status_exit") != 0
        or source_git.get("submodule_status_exit") != 0
        or source_git.get("dirty")
    ):
        return blocked("source Git checkout is dirty or has untracked files")
    if source_git.get("head") != checkpoint:
        return blocked("source HEAD is newer/different than the manifest checkpoint")
    tree = git(settings.deploy_repo, "rev-parse", "HEAD^{tree}")
    if tree.returncode != 0 or tree.stdout.strip() != manifest.get("source_checkpoint", {}).get("tree"):
        return blocked("source tree differs from manifest checkpoint")
    operation = str(manifest["operation_id"])
    recovery = Path(manifest["recovery_path"])
    journal_path = recovery / "journal.json"
    journal: dict[str, Any]
    if journal_path.exists():
        try:
            journal = json.loads(journal_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeError) as exc:
            return blocked(f"recovery journal is unreadable: {exc}")
        if not isinstance(journal, dict):
            return blocked("recovery journal must be a JSON object")
        journal, journal_error = _normalise_journal(journal, manifest, settings, manifest_path)
        if journal_error:
            return blocked(journal_error)
        assert journal is not None
    else:
        journal = {
            "schema": JOURNAL_SCHEMA,
            "operation_id": operation,
            "manifest": str(manifest_path),
            "phase": "planned",
            "completed_files": [],
            "staging_path": str((settings.staging_root / operation).resolve(strict=False)),
        }
    completed = set(journal.get("completed_files", []))
    state, reasons = current_matches_plan(settings, manifest, completed)
    if reasons:
        return blocked("preflight changed or unsafe material: " + "; ".join(reasons[:8]))
    stage = Path(journal["staging_path"])
    journal.update({"phase": "staging", "status": "applying", "staging_path": str(stage)})
    atomic_journal(journal_path, journal)
    try:
        stage.mkdir(parents=True, exist_ok=True)
        copy_to_stage(settings, manifest, stage, completed)
        verify_source_snapshot(settings, manifest)
        backup_targets(settings, manifest, completed)
        journal.update({"phase": "promoting", "backup_path": manifest["backup_path"]})
        atomic_journal(journal_path, journal)
        for item in manifest["managed_files"]:
            key = _item_key(item)
            if key in completed:
                if not _target_matches(item, _target_for(item), source_hash=True):
                    raise RuntimeError(f"completed target changed: {key}")
                continue
            target = _target_for(item)
            if item["state"] == "same":
                if not _target_matches(item, target, source_hash=True):
                    raise RuntimeError(f"same target no longer matches source: {key}")
                completed.add(key)
                journal["completed_files"] = sorted(completed)
                atomic_journal(journal_path, journal)
                continue
            if not _target_matches(item, target):
                raise RuntimeError(f"target changed during promotion: {key}")
            verify_source_snapshot(settings, manifest)
            staged = _safe_child(stage, relative_transport_path(item).as_posix())
            if not _regular_file(staged) or sha256(staged) != item["source_hash"]:
                raise RuntimeError(f"staged source is missing or tampered: {key}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target = _safe_child(Path(SOURCES[item["component"]][1]), item["path"])
            os.replace(staged, target)
            if not _target_matches(item, target, source_hash=True):
                raise RuntimeError(f"promotion hash mismatch: {key}")
            completed.add(key)
            journal["completed_files"] = sorted(completed)
            atomic_journal(journal_path, journal)
        for item in manifest["managed_files"]:
            if not _target_matches(item, _target_for(item), source_hash=True):
                raise RuntimeError(f"final target verification failed: {_item_key(item)}")
        journal.update({"phase": "completed", "status": "completed"})
        atomic_journal(journal_path, journal)
        update_manifest(
            manifest_path,
            manifest,
            status="completed",
            promotion_result={
                "status": "completed",
                "reasons": [],
                "promoted_files": sorted(completed),
            },
        )
        for item in manifest["managed_files"]:
            item["deployed_source_hash"] = item["source_hash"]
        atomic_json(manifest_path, manifest)
        print(f"PROMOTED: {operation}")
        return 0
    except Exception as exc:
        journal.update({"phase": "interrupted", "status": "interrupted", "error": str(exc)})
        atomic_journal(journal_path, journal)
        update_manifest(
            manifest_path,
            manifest,
            status="interrupted",
            promotion_result={
                "status": "interrupted",
                "reasons": [str(exc)],
                "promoted_files": journal.get("completed_files", []),
            },
        )
        return blocked(f"transport interrupted; resumable journal: {journal_path}")


def acquire_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+b")
    if fcntl is None:
        if msvcrt is None:
            handle.close()
            raise RuntimeError("no supported cross-platform lock backend")
        if handle.tell() == 0 and handle.seek(0, os.SEEK_END) == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            handle.close()
            raise RuntimeError("another MAK sync is already running")
        return handle
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (BlockingIOError, OSError):
        handle.close()
        raise RuntimeError("another MAK sync is already running")
    return handle


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plan a safe MAK transport")
    parser.add_argument("--mode", choices=("observe", "plan", "apply"), default="plan")
    parser.add_argument("--apply", action="store_true", help="explicit alias for --mode apply")
    parser.add_argument("--direction", default=DIRECTION)
    parser.add_argument("--checkpoint", help="explicit source commit hash; plan defaults to HEAD")
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args(argv)
    mode = "apply" if args.apply else args.mode
    settings = settings_from_env()
    manifest_path = args.manifest or settings.manifest_path
    try:
        lock = acquire_lock(settings.lock_path)
    except RuntimeError as exc:
        return blocked(str(exc), code=21)
    try:
        if mode == "apply":
            return apply_manifest(settings, manifest_path)
        state = inventory(settings)
        if mode == "observe":
            print(json.dumps(state, ensure_ascii=True, sort_keys=True, indent=2))
            return 0
        try:
            plan = build_plan(settings, args.direction, args.checkpoint)
        except (RuntimeError, ValueError) as exc:
            return blocked(str(exc))
        destination = write_plan(settings, plan, manifest_path)
        print(json.dumps(plan, ensure_ascii=True, sort_keys=True, indent=2))
        print(f"PLAN: {destination}", file=sys.stderr)
        return 0
    finally:
        lock.close()


if __name__ == "__main__":
    raise SystemExit(main())
