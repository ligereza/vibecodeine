"""Provenance for a measurement tool: what code ran, over what, and when.

A result without one of these is not a measurement, it is an anecdote. This
module exists because the same discipline was needed a second time, by a second
tool, and the first copy lives inline in ``tools/substrate_scan.py``.

That copy is deliberately NOT refactored to import this one. Its
``extractor_version`` is a digest of the sources it actually imports, so
changing its imports changes the version, and the two byte-identical scans it
already produced would stop being reproducible from their own record. A frozen
instrument stays frozen; the next tool gets the shared module.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

CONTRACT = "mak-run-record-v1"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def source_version(modules: Iterable[Any]) -> dict[str, str]:
    """A digest of the source of every module the caller actually imported.

    Not a hand-maintained version string. A version somebody has to remember to
    bump is a version that stops being true, and the failure is silent.
    """
    digest = hashlib.sha256()
    files: list[str] = []
    for module in modules:
        path = getattr(module, "__file__", None)
        if not path:
            continue
        blob = Path(path).read_bytes()
        digest.update(blob)
        files.append(Path(path).name)
    return {"version": digest.hexdigest()[:32], "sources": sorted(files)}


def git_state(repo: Path) -> dict[str, Any]:
    def run(*args: str) -> str:
        try:
            out = subprocess.run(("git", "-C", str(repo)) + args,
                                 capture_output=True, text=True, timeout=20)
            return out.stdout.strip()
        except Exception:                                    # noqa: BLE001
            return ""
    status = run("status", "--porcelain")
    return {
        "commit": run("rev-parse", "HEAD"),
        "branch": run("rev-parse", "--abbrev-ref", "HEAD"),
        # A dirty tree means the commit does not describe what ran. Saying so is
        # the whole point; a clean-looking record over a dirty tree is a lie.
        "tree_dirty": bool(status),
        "dirty_paths": sorted(line[3:] for line in status.splitlines())[:40],
    }


def input_identity(path: Path) -> dict[str, Any]:
    """Identify an input file by content, not by name.

    A read-only index consulted by two runs must be provably the same index.
    """
    out: dict[str, Any] = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return out
    stat = path.stat()
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    out.update(size=stat.st_size, mtime_ns=stat.st_mtime_ns,
               sha256=digest.hexdigest())
    return out


def volume_identity(root: Path) -> dict[str, Any]:
    """Which physical volume, and mounted how.

    Two directories with the same name are not the same corpus, and a case
    insensitive or metadata-lossy filesystem changes what a scan can even see.
    """
    out: dict[str, Any] = {"root": str(root), "exists": root.exists()}
    if root.exists():
        out["device"] = os.stat(root).st_dev
    fstype = ""
    try:
        for line in Path("/proc/mounts").read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) > 2 and parts[1] == str(root):
                fstype = parts[2]
    except OSError:
        pass
    out["fstype"] = fstype
    return out


def result_digest(result: Any, *, ignore: tuple[str, ...] = ()) -> str:
    """Digest of a result with non-deterministic fields removed.

    Wall time and timestamps differ between two identical runs. Leaving them in
    guarantees the digests differ and destroys the only cheap check available:
    did running it twice produce the same answer?
    """
    def strip(value: Any) -> Any:
        if isinstance(value, dict):
            return {k: strip(v) for k, v in sorted(value.items())
                    if k not in ignore}
        if isinstance(value, list):
            return [strip(v) for v in value]
        return value
    blob = json.dumps(strip(result), sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(blob.encode("ascii")).hexdigest()


def record(*, contract: str, argv: list[str], modules: Iterable[Any],
           repo: Path, inputs: Iterable[Path] = (),
           volumes: Iterable[Path] = ()) -> dict[str, Any]:
    return {
        "contract": contract,
        "run_record": CONTRACT,
        "started_at": now(),
        "argv": list(argv),
        "code": source_version(modules),
        "git": git_state(repo),
        "python": sys.version.split()[0],
        "inputs": [input_identity(p) for p in inputs],
        "volumes": [volume_identity(p) for p in volumes],
    }
