#!/usr/bin/env python3
"""One cross-process GPU slot for MAK local model and render calls."""
import contextlib
import json
import os
import time

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows director has no fcntl
    fcntl = None

try:
    from actividad import record
except ImportError:  # pragma: no cover - direct imports outside MAK
    record = None


HOME = os.path.expanduser("~")
LOCK_FILE = os.environ.get("MAK_GPU_LOCK", os.path.join(HOME, "plataforma", ".gpu.lock"))
STATE_FILE = os.environ.get("MAK_GPU_STATE", os.path.join(HOME, "plataforma", "gpu_state.json"))
DEFAULT_TIMEOUT = float(os.environ.get("MAK_GPU_SLOT_TIMEOUT", "300"))
POLL_SECONDS = 0.25


class GPUSlotBusy(RuntimeError):
    """The shared GPU slot could not be acquired before its deadline."""


def _write_state(data):
    parent = os.path.dirname(os.path.abspath(STATE_FILE))
    os.makedirs(parent, exist_ok=True)
    temp = None
    try:
        with open(STATE_FILE + ".tmp", "w", encoding="utf-8") as stream:
            temp = STATE_FILE + ".tmp"
            json.dump(data, stream, ensure_ascii=False, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, STATE_FILE)
        temp = None
    finally:
        if temp:
            try:
                os.unlink(temp)
            except OSError:
                pass


def _clear_state(activity_id):
    try:
        with open(STATE_FILE, encoding="utf-8") as stream:
            current = json.load(stream)
        if current.get("activity_id") != activity_id:
            return
        os.unlink(STATE_FILE)
    except (OSError, ValueError, AttributeError):
        pass


@contextlib.contextmanager
def slot(*, caller, queue, model, department, trigger="manual", job_id="",
         resource="ollama", timeout=None):
    """Acquire the one GPU slot, record the owner, and release it safely."""
    if fcntl is None:  # The shared lock is a Linux MAK runtime boundary.
        yield
        return
    timeout = DEFAULT_TIMEOUT if timeout is None else float(timeout)
    started_wait = time.time()
    fd = os.open(LOCK_FILE, os.O_CREAT | os.O_RDWR, 0o600)
    acquired = False
    activity_id = ""
    started = None
    try:
        deadline = started_wait + max(0.0, timeout)
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
                break
            except BlockingIOError:
                if time.time() >= deadline:
                    if record:
                        record("gpu", "busy", trigger=trigger, caller=caller,
                               queue=queue, department=department, job_id=job_id,
                               model=model, resource=resource)
                    raise GPUSlotBusy("GPU slot busy after %.1fs" % timeout)
                time.sleep(POLL_SECONDS)
        started = time.time()
        activity_id = record(
            "gpu", "acquired", trigger=trigger, caller=caller, queue=queue,
            department=department, job_id=job_id, model=model,
            resource=resource, started=started) if record else ""
        _write_state({
            "schema": "mak-gpu-state-v1", "activity_id": activity_id,
            "pid": os.getpid(), "caller": caller, "queue": queue,
            "department": department, "job_id": job_id, "model": model,
            "resource": resource, "trigger": trigger, "started": started,
        })
        yield
        ended = time.time()
        if record:
            record("gpu", "released", trigger=trigger, caller=caller,
                   queue=queue, department=department, job_id=job_id,
                   model=model, resource=resource, activity_id=activity_id,
                   started=started, ended=ended)
    except Exception as exc:
        if acquired and record:
            record("gpu", "failed", trigger=trigger, caller=caller,
                   queue=queue, department=department, job_id=job_id,
                   model=model, resource=resource, activity_id=activity_id,
                   started=started, ended=time.time(), error=str(exc))
        raise
    finally:
        if acquired:
            _clear_state(activity_id)
            fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def current_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, ValueError):
        return {}
