"""One cross-process GPU lease for the MAK shadow phase.

The arbiter intentionally enforces the strongest safe invariant first: one
GPU-bound job at a time. VRAM estimates reject impossible jobs before they
reach Ollama. The lock is released by the operating system if the owner dies.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


class GpuBusy(RuntimeError):
    """Raised when the GPU lease cannot be acquired before its deadline."""


class GpuBudgetExceeded(ValueError):
    """Raised when a job declares more VRAM than the configured capacity."""


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    temp = path.with_name(".%s.%s.tmp" % (path.name, os.getpid()))
    temp.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    os.replace(temp, path)


class GpuArbiter:
    """Portable exclusive file lease with an explicit VRAM ceiling."""

    def __init__(self, lock_path: str | os.PathLike[str], *,
                 capacity_mb: int = 4096, poll_s: float = 0.05) -> None:
        self.lock_path = Path(lock_path).expanduser()
        self.metadata_path = self.lock_path.with_name(self.lock_path.name
                                                       + ".owner.json")
        self.capacity_mb = int(capacity_mb)
        self.poll_s = max(0.01, float(poll_s))
        self._fd: int | None = None
        self._platform = "windows" if os.name == "nt" else "posix"

    def would_exceed_budget(self, estimated_vram_mb: int) -> bool:
        return int(estimated_vram_mb) > self.capacity_mb

    def acquire(self, *, job_id: str, estimated_vram_mb: int = 0,
                timeout_s: float = 0.0, priority: int = 0) -> None:
        estimate = max(0, int(estimated_vram_mb))
        if self.would_exceed_budget(estimate):
            raise GpuBudgetExceeded(
                "job %s requests %d MB; capacity is %d MB"
                % (job_id, estimate, self.capacity_mb))
        if self._fd is not None:
            raise RuntimeError("GPU lease is already held by this arbiter")

        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(self.lock_path), os.O_RDWR | os.O_CREAT, 0o600)
        os.ftruncate(fd, 1)
        deadline = time.monotonic() + max(0.0, float(timeout_s))
        try:
            while True:
                if self._try_lock(fd):
                    try:
                        _write_json_atomic(self.metadata_path, {
                            "job_id": job_id,
                            "owner_pid": os.getpid(),
                            "estimated_vram_mb": estimate,
                            "priority": int(priority),
                            "acquired_at": time.time(),
                        })
                    except BaseException:
                        raise
                    self._fd = fd
                    return
                if time.monotonic() >= deadline:
                    raise GpuBusy("GPU lease busy for job %s" % job_id)
                time.sleep(self.poll_s)
        except BaseException:
            os.close(fd)
            raise

    def _try_lock(self, fd: int) -> bool:
        if self._platform == "posix":
            import fcntl
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return True
            except BlockingIOError:
                return False
        import msvcrt
        os.lseek(fd, 0, os.SEEK_SET)
        try:
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            return True
        except OSError:
            return False

    def release(self) -> None:
        fd, self._fd = self._fd, None
        if fd is None:
            return
        try:
            # Remove ownership metadata while this process still owns the
            # lock. Removing it after unlock could delete a new owner's data.
            try:
                self.metadata_path.unlink()
            except FileNotFoundError:
                pass
            if self._platform == "posix":
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_UN)
            else:
                import msvcrt
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        finally:
            os.close(fd)

    def __enter__(self) -> "GpuArbiter":
        if self._fd is None:
            raise RuntimeError("call acquire() before entering the context")
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.release()
