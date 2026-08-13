#!/usr/bin/env python3
"""Deploy origin/main to MAK without touching the human working checkout."""
from __future__ import annotations

import datetime as dt
import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


DEPLOY_REPO = Path(os.environ.get("MAK_DEPLOY_REPO", "/home/mak/flujo-deploy"))
USER_REPO = Path(os.environ.get("MAK_USER_REPO", "/home/mak/flujo"))
LOCK_PATH = Path(os.environ.get("MAK_SYNC_LOCK", "/home/mak/.cache/mak-sync.lock"))
MANIFEST_PATH = Path(
    os.environ.get("MAK_SYNC_MANIFEST", "/home/mak/plataforma/deploy_manifest.json")
)
BACKUP_ROOT = Path(
    os.environ.get("MAK_SYNC_BACKUP_ROOT", "/home/mak/rollback/mak-sync")
)
TARGET_REF = "origin/main"
SOURCES = {
    "mak_plataforma": ("cultura/mak_plataforma", "/home/mak/plataforma"),
    "mak_research": ("cultura/mak_research", "/home/mak/research"),
    "mak_codex": ("cultura/mak_codex", "/home/mak/codex"),
    "mak_curatoria": ("cultura/mak_curatoria", "/home/mak/curatoria"),
}


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(DEPLOY_REPO), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def blocked(message: str, *, code: int = 20) -> int:
    print(f"BLOCKED: {message}", file=sys.stderr)
    return code


def require_deploy_worktree() -> int | None:
    if DEPLOY_REPO.resolve() == USER_REPO.resolve():
        return blocked("deploy worktree must not be the human checkout")
    if not DEPLOY_REPO.is_dir():
        return blocked(f"missing deploy worktree: {DEPLOY_REPO}")

    top = git("rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != DEPLOY_REPO.resolve():
        return blocked("deploy path is not the expected Git worktree")

    status = git("status", "--porcelain")
    if status.returncode != 0:
        return blocked("cannot inspect deploy worktree status")
    if status.stdout.strip():
        return blocked("deploy worktree is dirty; no reset or copy performed")
    return None


def copy_tree(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise RuntimeError(f"missing source component: {source}")
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, dirs_exist_ok=True, copy_function=shutil.copy2)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def backup_live_drift(commit: str) -> list[str]:
    """Preserve live files that differ before the source copy overwrites them."""
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = BACKUP_ROOT / f"{stamp}-{commit[:12]}"
    changed: list[str] = []
    for source, destination in SOURCES.values():
        source_root = DEPLOY_REPO / source
        live_root = Path(destination)
        for candidate in source_root.rglob("*"):
            if not candidate.is_file():
                continue
            live = live_root / candidate.relative_to(source_root)
            if not live.is_file() or file_hash(candidate) == file_hash(live):
                continue
            target = backup / destination.lstrip("/") / candidate.relative_to(source_root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(live, target)
            changed.append(str(live))
    if not changed and backup.exists():
        shutil.rmtree(backup)
    return changed


def write_manifest(commit: str, tree: str, status: str, drift: list[str]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "mak-deploy-v1",
        "source_repo": str(DEPLOY_REPO),
        "target_ref": TARGET_REF,
        "commit": commit,
        "tree": tree,
        "status": status,
        "deployed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "live_drift_backed_up": drift,
        "components": {
            name: {"source": source, "destination": destination}
            for name, (source, destination) in SOURCES.items()
        },
    }
    fd, temporary = tempfile.mkstemp(
        prefix=f".{MANIFEST_PATH.name}.", suffix=".tmp", dir=MANIFEST_PATH.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, MANIFEST_PATH)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOCK_PATH.open("w", encoding="ascii") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return blocked("another MAK sync is already running", code=21)

        error = require_deploy_worktree()
        if error is not None:
            return error

        fetched = git(
            "fetch",
            "--quiet",
            "origin",
            "+refs/heads/main:refs/remotes/origin/main",
        )
        if fetched.returncode != 0:
            return blocked(f"fetch failed: {fetched.stderr.strip() or 'unknown error'}")

        target = git("rev-parse", TARGET_REF)
        if target.returncode != 0:
            return blocked("origin/main is unavailable after fetch")
        commit = target.stdout.strip()

        # This reset is confined to the disposable deploy worktree, never the
        # human checkout at /home/mak/flujo.
        updated = git("reset", "--hard", TARGET_REF)
        if updated.returncode != 0:
            return blocked(f"deploy worktree update failed: {updated.stderr.strip()}")
        head = git("rev-parse", "HEAD")
        if head.returncode != 0 or head.stdout.strip() != commit:
            return blocked("deploy worktree HEAD does not match origin/main")
        tree = git("rev-parse", "HEAD^{tree}")
        if tree.returncode != 0:
            return blocked("cannot resolve deployed tree")

        try:
            drift = backup_live_drift(commit)
            write_manifest(commit, tree.stdout.strip(), "planned", drift)
            for source, destination in SOURCES.values():
                copy_tree(DEPLOY_REPO / source, Path(destination))
            write_manifest(commit, tree.stdout.strip(), "deployed", drift)
        except (OSError, RuntimeError) as exc:
            return blocked(f"component copy failed: {exc}")

        print(f"DEPLOYED: {commit} from {DEPLOY_REPO}")
        print(f"MANIFEST: {MANIFEST_PATH}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
