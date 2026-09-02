#!/usr/bin/env python3
"""Prove which code each MAK/FLUJO runtime surface is actually executing.

`tools/capabilities.py` answers "is the declared surface present and alive?".
It never answers "is the live process running the canonical source?", so an
HTTP 200 has repeatedly been read as proof of a healthy runtime.  This
preflight closes that gap with four independent pieces of evidence per
surface:

1. the declared canonical source under the physical root, plus its SHA-256;
2. the unit fragment and its expanded ``ExecStart`` (systemd surfaces) or an
   import probe against the live interpreter (manual surfaces);
3. the running command line read from ``/proc/<pid>/cmdline``, which is the
   only thing that reflects what was actually launched;
4. the listening socket, and only then an HTTP status.

Contract of this file:

* ``/home/mak`` is the canonical physical root.  ``__file__`` is resolved, so
  invoking the tool through the compatibility adapter still reports the
  physical root and records the indirection instead of hiding it.
* ``/home/mak/flujo`` is a ``compatibility_adapter``: a real directory of
  sibling symlinks.  It is never reported as a second repository, a worktree
  or an independent operational root.
* Git is version reference, not physical authority.  Branch facts are read
  from ``branch_profile.json`` and annotate a surface; they never override a
  measurement taken from the filesystem or from ``/proc``.
* The checks do not fail open.  A missing source, an executed source that
  differs from the declared one, a source edited after the process started, an
  ``ExecStart`` resolving outside the physical root, and an open listener
  whose source cannot be verified are all errors.  A missing unit is
  ``unknown`` (never silently ok) unless the surface is a declared manual
  process.

Examples::

    python3 tools/runtime_preflight.py --format text
    python3 tools/runtime_preflight.py --format json
    python3 tools/runtime_preflight.py --check
    python3 tools/runtime_preflight.py --check --check-adapter
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

SCHEMA = "mak-runtime-preflight-v1"
PHYSICAL_ROOT = Path("/home/mak")
# /home/mak/flujo is no longer a compatibility adapter: it is the physical
# FLUJO checkout, and MAK consumes the motor from /home/mak/flujo/src without
# copying src/flujo. What used to be "adapter indirection" is now the declared
# layout; resolving OUTSIDE this root is the defect.
FLUJO_CHECKOUT = "flujo"
FLUJO_SOURCE_ROOT = "flujo/src"
ADAPTER_NAME = FLUJO_CHECKOUT
# Evidence trees.  Code executed from here is historical material, not runtime.
FROZEN_PREFIXES = ("_archive", "WIN")

STATUS_OK = "ok"
STATUS_OK_VIA_ADAPTER = "ok_via_adapter"
STATUS_WARN = "warn"
STATUS_UNKNOWN = "unknown"
STATUS_ERROR = "error"

# Ordered worst-last; the surface status is the worst finding it carries.
STATUS_RANK = {
    STATUS_OK: 0,
    STATUS_OK_VIA_ADAPTER: 1,
    STATUS_WARN: 2,
    STATUS_UNKNOWN: 3,
    STATUS_ERROR: 4,
}

# Exit codes.  One code per condition, so a caller can tell them apart.
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_UNKNOWN = 2
EXIT_WARN = 3
EXIT_ADAPTER = 4

# A single status per surface hides a second condition underneath it: a
# surface that both falls back to another port and depends on the adapter
# reports only `warn`, and the adapter dependency disappears from the counts.
# Conditions are therefore counted independently of the worst status, and the
# exit code is derived from them.
CONDITION_ERROR = "error"
CONDITION_UNKNOWN = "unknown"
CONDITION_WARN = "warn"
CONDITION_ADAPTER = "adapter_dependency"


@dataclass(frozen=True)
class Surface:
    """One declared runtime surface and how to prove what it executes."""

    surface_id: str
    label: str
    owner_branch: str
    source_declared: str
    kind: str
    declared_port: int | None
    http_paths: tuple[str, ...]
    unit: str | None = None
    unit_scope: str = "user"
    fallback_ports: tuple[int, ...] = ()
    # Manual surfaces are not launched from a unit, so the script path is not
    # in the command line.  These fields say how to identify and interrogate
    # the live process instead of guessing.
    process_match: tuple[str, ...] = ()
    import_probe: str | None = None
    # A surface whose runtime is a compiled binary cannot be proven by a .py
    # path.  Declaring the kind keeps the tool from demanding a Python source
    # from a daemon that has none, and keeps it from accepting a repo-side
    # consumer library as if it were the executed code.
    source_kind: str = "python_script"
    # Repo files that call the surface.  Evidence of ownership, never evidence
    # of what the surface executes.
    consumer_sources: tuple[str, ...] = ()


# Keep this registry explicit and small.  Discovery cannot tell a compatibility
# wrapper from an owned hub, and it cannot tell a manual process from a
# deployment: both distinctions have to be declared.
SURFACES: tuple[Surface, ...] = (
    Surface(
        surface_id="mak_hub",
        label="MAK Hub",
        owner_branch="MAK",
        source_declared="cultura/mak_plataforma/hub.py",
        kind="systemd_user",
        declared_port=8900,
        http_paths=("/health", "/api/status"),
        unit="mak-hub.service",
    ),
    Surface(
        surface_id="mak_research",
        label="Research",
        owner_branch="MAK",
        source_declared="cultura/mak_research/interfaz.py",
        kind="systemd_user",
        declared_port=8890,
        http_paths=("/",),
        unit="mak-research.service",
    ),
    Surface(
        surface_id="mak_codex",
        label="Codex bridge",
        owner_branch="MAK",
        source_declared="cultura/mak_codex/interfaz_codex.py",
        kind="systemd_user",
        declared_port=8891,
        http_paths=("/",),
        unit="mak-codex.service",
    ),
    Surface(
        surface_id="flujo_app",
        label="FLUJO App",
        owner_branch="FLUJO",
        source_declared="flujo/src/flujo/web/hub.py",
        kind="manual_process",
        declared_port=8765,
        # src/flujo/web/hub.py::_find_free_port(start_port=8765, max_tries=8)
        # only auto-detects when the requested port is exactly the default.
        fallback_ports=(8766, 8767, 8768, 8769, 8770, 8771, 8772),
        http_paths=("/",),
        process_match=("-m", "flujo", "app"),
        import_probe="flujo.web.hub",
    ),
    Surface(
        surface_id="ollama",
        label="Ollama local inference",
        owner_branch="MAK",
        # The executed code is the system binary.  Naming a repo library here
        # would let a MAK-side edit look like runtime drift in the daemon, and
        # would leave the daemon's real executable unverified.
        source_declared="/usr/local/bin/ollama",
        source_kind="native_binary",
        kind="systemd_system",
        declared_port=11434,
        http_paths=("/api/version", "/api/tags"),
        unit="ollama.service",
        unit_scope="system",
        consumer_sources=(
            "cultura/mak_research/research_lib.py",
            "cultura/mak_codex/codex_lib.py",
        ),
    ),
)


@dataclass
class Finding:
    code: str
    status: str
    detail: str


@dataclass
class SurfaceReport:
    surface_id: str
    label: str
    kind: str
    findings: list[Finding] = field(default_factory=list)
    data: dict[str, object] = field(default_factory=dict)

    def add(self, code: str, status: str, detail: str) -> None:
        self.findings.append(Finding(code, status, detail))

    @property
    def status(self) -> str:
        if not self.findings:
            return STATUS_OK
        return max((f.status for f in self.findings), key=lambda s: STATUS_RANK[s])

    @property
    def conditions(self) -> dict[str, bool]:
        """Every condition the surface carries, not only its worst one."""

        present = {f.status for f in self.findings}
        return {
            CONDITION_ERROR: STATUS_ERROR in present,
            CONDITION_UNKNOWN: STATUS_UNKNOWN in present,
            CONDITION_WARN: STATUS_WARN in present,
            CONDITION_ADAPTER: STATUS_OK_VIA_ADAPTER in present,
        }


# --------------------------------------------------------------------------
# primitives


def _sha256(path: Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 20), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def _run(command: list[str], timeout: float = 5.0) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            command, check=False, capture_output=True, text=True, timeout=timeout
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
        return 127, "", str(exc)
    return result.returncode, result.stdout, result.stderr


def _systemctl(unit: str, scope: str, *properties: str) -> dict[str, str]:
    command = ["systemctl"]
    if scope == "user":
        command.append("--user")
    command.append("show")
    for name in properties:
        command.extend(("-p", name))
    command.append(unit)
    code, out, _ = _run(command)
    if code != 0:
        return {}
    values: dict[str, str] = {}
    for line in out.splitlines():
        if "=" in line:
            key, _, value = line.partition("=")
            values[key] = value
    return values


def _exec_start_argv(raw: str) -> str | None:
    """Extract the expanded argv from a systemd ``ExecStart`` property.

    systemd renders it as ``{ path=... ; argv[]=/usr/bin/python3 /a/b.py ; ...``
    and the ``argv[]`` field is already ``%h``-expanded, so it is the command
    systemd would launch now.
    """

    match = re.search(r"argv\[\]=([^;}]+)", raw)
    if match:
        return match.group(1).strip() or None
    match = re.search(r"path=([^;}]+)", raw)
    if match:
        return match.group(1).strip() or None
    return None


def _proc_cmdline(pid: int) -> list[str] | None:
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError:
        return None
    parts = [part for part in raw.split(b"\0") if part]
    return [part.decode("utf-8", "replace") for part in parts]


def _proc_start_time(pid: int) -> float | None:
    try:
        return Path(f"/proc/{pid}").stat().st_mtime
    except OSError:
        return None


def _listeners() -> dict[int, dict[str, object]]:
    """Map local listening port -> owning pid/process, best effort.

    ``ss`` omits the process for sockets owned by another user, so a port can
    be open with an unknown owner.  That case must stay visible: it is exactly
    the "listener without verifiable source" error.
    """

    code, out, _ = _run(["ss", "-ltnpH"])
    rows: dict[int, dict[str, object]] = {}
    if code != 0:
        return rows
    for line in out.splitlines():
        fields = line.split()
        if len(fields) < 4:
            continue
        local = fields[3]
        _, _, port_text = local.rpartition(":")
        if not port_text.isdigit():
            continue
        port = int(port_text)
        pid: int | None = None
        name: str | None = None
        match = re.search(r'users:\(\("([^"]+)",pid=(\d+)', line)
        if match:
            name = match.group(1)
            pid = int(match.group(2))
        rows[port] = {"address": local, "pid": pid, "process": name}
    return rows


def _socket_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.5):
            return True
    except OSError:
        return False


def _probe_http(port: int, paths: tuple[str, ...]) -> dict[str, object]:
    for path in paths:
        try:
            request = Request(f"http://127.0.0.1:{port}{path}", method="GET")
            with urlopen(request, timeout=3) as response:
                return {
                    "http_path": path,
                    "http_status": int(response.status),
                    "bytes": len(response.read(1 << 16)),
                }
        except (OSError, URLError, ValueError) as exc:
            last = str(exc)
    return {"http_path": paths[0] if paths else None, "http_status": None, "error": last if paths else None}


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _frozen_prefix(path: Path, root: Path) -> str | None:
    if not _inside(path, root):
        return None
    first = path.relative_to(root).parts
    if first and first[0] in FROZEN_PREFIXES:
        return first[0]
    return None


def _script_tokens(argv: list[str]) -> list[str]:
    return [token for token in argv if token.endswith(".py")]


# --------------------------------------------------------------------------
# adapter and branch context


def adapter_report(root: Path) -> dict[str, object]:
    """Describe /home/mak/flujo as the physical FLUJO checkout.

    It used to be a directory of sibling symlinks and this function used to
    prove it was not a second repository. The layout decision inverted that:
    it must now BE a checkout of FLUJO, and finding symlinks or no git dir
    there is the defect.
    """

    adapter = root / FLUJO_CHECKOUT
    entries: list[str] = []
    links = 0
    cycles: list[str] = []
    broken: list[str] = []
    if adapter.is_dir():
        for child in sorted(adapter.iterdir()):
            entries.append(child.name)
            if child.is_symlink():
                links += 1
                target = Path(os.path.realpath(child))
                if target == adapter or _inside(target, adapter):
                    cycles.append(child.name)
                if not child.exists():
                    broken.append(child.name)
    code, out, _ = _run(["git", "-C", str(root), "worktree", "list", "--porcelain"])
    worktrees = [line.split(" ", 1)[1] for line in out.splitlines() if line.startswith("worktree ")]
    code_b, out_b, _ = _run(["git", "-C", str(adapter), "branch", "--show-current"])
    branch = out_b.strip() if code_b == 0 else None
    return {
        "path": str(adapter),
        "role": "flujo_physical_checkout",
        "branch": branch,
        "is_flujo_checkout": branch == "FLUJO",
        "source_root": str(root / FLUJO_SOURCE_ROOT),
        "exists": adapter.is_dir(),
        "is_symlink": adapter.is_symlink(),
        "own_git_dir": (adapter / ".git").exists(),
        "is_git_worktree": str(adapter) in worktrees,
        "git_worktrees": worktrees if code == 0 else [],
        "entries": len(entries),
        "sibling_symlinks": links,
        "recursive_symlinks": cycles,
        "broken_symlinks": broken,
    }


def _branch_profile(root: Path, branch: str | None) -> dict[str, object]:
    """Read one branch_profile.json without checking anything out."""

    if branch is None:
        return {}
    code, out, _ = _run(["git", "-C", str(root), "show", f"{branch}:branch_profile.json"])
    if code != 0:
        return {}
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {}


def branch_context(root: Path) -> dict[str, object]:
    code, out, _ = _run(["git", "-C", str(root), "branch", "--show-current"])
    checkout = out.strip() if code == 0 else ""
    local = root / "branch_profile.json"
    profile: dict[str, object] = {}
    if local.is_file():
        try:
            profile = json.loads(local.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            profile = {}
    return {
        "checkout_branch": checkout or None,
        "checkout_branch_kind": profile.get("kind", "runtime") if profile else None,
        "checkout_selector": profile.get("default_test_selector") if profile else None,
        "profiles": {
            name: _branch_profile(root, name) for name in ("MAK", "FLUJO", "main", "historia")
        },
        "note": "git is version reference; it does not decide what the box executes",
    }


def _declared_port_from_branch(
    profiles: dict[str, object], branch: str, source_declared: str
) -> int | None:
    """Return the branch hub port only for the surface that IS that hub.

    A branch profile declares one hub.  Comparing every surface of a branch
    against it turned Research (8890) and Codex (8891) into false drift
    against the MAK hub port 8900, which is the kind of manufactured finding
    this tool exists to prevent.
    """

    profile = profiles.get(branch)
    if not isinstance(profile, dict):
        return None
    hub = profile.get("hub")
    if not isinstance(hub, dict):
        return None
    modules = {
        str(hub.get(key))
        for key in ("module", "compatibility_module")
        if isinstance(hub.get(key), str)
    }
    if source_declared not in modules:
        return None
    port = hub.get("default_port")
    return port if isinstance(port, int) else None


# --------------------------------------------------------------------------
# per-surface evidence


def _resolve_source(report: SurfaceReport, root: Path, surface: Surface) -> Path | None:
    # `root / "/abs/path"` yields the absolute path, so a native binary and a
    # repo-relative script share one code path.
    declared = root / surface.source_declared
    resolved = Path(os.path.realpath(declared))
    report.data["source_kind"] = surface.source_kind
    report.data["source_declared"] = str(declared)
    report.data["source_resolved"] = str(resolved)
    if not resolved.is_file():
        report.data["source_sha256"] = None
        report.add(
            "source_missing",
            STATUS_ERROR,
            f"declared source does not exist: {declared}",
        )
        return None
    report.data["source_sha256"] = _sha256(resolved)
    report.data["source_mtime"] = datetime.fromtimestamp(
        resolved.stat().st_mtime, timezone.utc
    ).isoformat()
    frozen = _frozen_prefix(resolved, root)
    if frozen:
        report.add(
            "source_in_frozen_evidence",
            STATUS_ERROR,
            f"declared source resolves into frozen evidence tree {frozen}/",
        )

    present = [name for name in surface.consumer_sources if (root / name).is_file()]
    missing = [name for name in surface.consumer_sources if not (root / name).is_file()]
    if surface.consumer_sources:
        report.data["consumer_sources_present"] = present
        report.data["consumer_sources_missing"] = missing
    if missing:
        report.add(
            "consumer_source_missing",
            STATUS_WARN,
            "declared consumers absent: " + ",".join(missing),
        )
    return resolved


def _check_exec_paths(
    report: SurfaceReport,
    root: Path,
    resolved_source: Path | None,
    argv: list[str],
    origin: str,
) -> None:
    """Verify every script path in a command line against the physical root."""

    scripts = _script_tokens(argv)
    report.data[f"{origin}_scripts"] = scripts
    for token in scripts:
        candidate = Path(token)
        if not candidate.is_absolute():
            candidate = root / candidate
        real = Path(os.path.realpath(candidate))
        if token.startswith(f"{root}/{FLUJO_SOURCE_ROOT}/"):
            report.add(
                "resolves_in_flujo_checkout",
                STATUS_OK,
                f"{origin} resolves inside the FLUJO checkout: {token}",
            )
        elif token.startswith(f"{root}/src/flujo/"):
            report.add(
                "flujo_resolved_outside_its_checkout",
                STATUS_ERROR,
                f"{origin} resolves the motor from {token}; the declared source root "
                f"is {root}/{FLUJO_SOURCE_ROOT}",
            )
        frozen = _frozen_prefix(real, root)
        if frozen:
            report.add(
                "exec_start_historical",
                STATUS_ERROR,
                f"{origin} resolves into frozen evidence {frozen}/: {real}",
            )
            continue
        if not _inside(real, root):
            report.add(
                "exec_start_outside_root",
                STATUS_ERROR,
                f"{origin} resolves outside the physical root: {real}",
            )
            continue
        if resolved_source is not None and real != resolved_source:
            report.add(
                "executed_source_mismatch",
                STATUS_ERROR,
                f"{origin} executes {real}, declared {resolved_source}",
            )


def _check_native_executable(
    report: SurfaceReport, root: Path, resolved_source: Path | None, argv: list[str]
) -> None:
    """Prove a compiled surface by its argv[0], the only path it exposes."""

    if not argv:
        report.add("executed_source_unverifiable", STATUS_ERROR, "empty command line")
        return
    real = Path(os.path.realpath(argv[0]))
    report.data["executed_binary"] = str(real)
    frozen = _frozen_prefix(real, root)
    if frozen:
        report.add(
            "exec_start_historical",
            STATUS_ERROR,
            f"the running binary resolves into frozen evidence {frozen}/: {real}",
        )
        return
    if resolved_source is None:
        report.add(
            "executed_source_unverifiable",
            STATUS_ERROR,
            f"the running binary is {real} but no declared executable was resolved",
        )
        return
    if real != resolved_source:
        report.add(
            "executed_source_mismatch",
            STATUS_ERROR,
            f"the running binary is {real}, declared {resolved_source}",
        )


def _unit_evidence(report: SurfaceReport, root: Path, surface: Surface, resolved: Path | None) -> int | None:
    properties = _systemctl(
        surface.unit or "",
        surface.unit_scope,
        "FragmentPath",
        "ExecStart",
        "ActiveState",
        "SubState",
        "MainPID",
    )
    report.data["unit"] = surface.unit
    report.data["unit_scope"] = surface.unit_scope
    if not properties:
        report.data["unit_state"] = "missing"
        report.data["exec_start"] = None
        report.add(
            "unit_missing",
            STATUS_UNKNOWN,
            f"systemd has no unit {surface.unit} in the {surface.unit_scope} scope",
        )
        return None

    fragment = properties.get("FragmentPath") or None
    report.data["unit_fragment_path"] = fragment
    if fragment:
        fragment_real = Path(os.path.realpath(fragment))
        report.data["unit_fragment_resolved"] = str(fragment_real)
        report.data["unit_fragment_sha256"] = _sha256(fragment_real)
        target = os.readlink(fragment) if Path(fragment).is_symlink() else None
        report.data["unit_fragment_symlink_target"] = target
        if target and target.startswith(f"{root}/{ADAPTER_NAME}/"):
            report.add(
                "unit_fragment_via_adapter",
                STATUS_OK_VIA_ADAPTER,
                f"unit fragment reaches its body through the adapter: {target} -> {fragment_real}",
            )

    exec_raw = properties.get("ExecStart", "")
    exec_start = _exec_start_argv(exec_raw)
    report.data["exec_start"] = exec_start
    report.data["unit_state"] = properties.get("ActiveState", "unknown")
    report.data["unit_sub_state"] = properties.get("SubState")
    if exec_start and surface.source_kind == "native_binary":
        _check_native_executable(report, root, resolved, exec_start.split())
    elif exec_start:
        _check_exec_paths(report, root, resolved, exec_start.split(), "exec_start")
    elif surface.unit_scope == "user":
        report.add(
            "exec_start_unreadable",
            STATUS_UNKNOWN,
            "systemd reported the unit but no ExecStart could be parsed",
        )

    main_pid_text = properties.get("MainPID", "0")
    main_pid = int(main_pid_text) if main_pid_text.isdigit() else 0
    if properties.get("ActiveState") != "active":
        report.add(
            "unit_not_active",
            STATUS_ERROR if surface.kind.startswith("systemd") else STATUS_WARN,
            f"unit state is {properties.get('ActiveState')}",
        )
        return None
    return main_pid or None


def _find_manual_pid(surface: Surface) -> int | None:
    for entry in sorted(Path("/proc").iterdir()):
        if not entry.name.isdigit():
            continue
        argv = _proc_cmdline(int(entry.name))
        if not argv:
            continue
        if all(token in argv for token in surface.process_match):
            return int(entry.name)
    return None


def _import_probe(report: SurfaceReport, root: Path, surface: Surface, interpreter: str, resolved: Path | None) -> None:
    """Ask the live interpreter which file it would import for the surface.

    This is the only available answer for a ``-m module`` launch: the script
    path is absent from the command line.  It reflects the interpreter's
    current ``sys.path``, not the bytes already loaded in the running process,
    and is labelled as such.
    """

    if not surface.import_probe:
        return
    code, out, err = _run(
        [interpreter, "-c", f"import {surface.import_probe} as m; print(m.__file__)"],
        timeout=20.0,
    )
    if code != 0:
        report.data["import_probe"] = None
        report.add(
            "import_probe_failed",
            STATUS_ERROR,
            f"{interpreter} could not import {surface.import_probe}: {err.strip()[:200]}",
        )
        return
    probed = out.strip()
    report.data["import_probe"] = probed
    report.data["import_probe_module"] = surface.import_probe
    report.data["import_probe_interpreter"] = interpreter
    _check_exec_paths(report, root, resolved, [probed], "import_probe")

    # Record every editable-install hook that routes the import through the
    # adapter, so the indirection has a file behind it and not a guess.
    pth_hits: list[str] = []
    site_packages = Path(interpreter).resolve().parent.parent / "lib"
    if site_packages.is_dir():
        for pth in sorted(site_packages.glob("python3*/site-packages/*.pth")):
            try:
                text = pth.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for line in text.splitlines():
                if f"{root}/{ADAPTER_NAME}/" in line:
                    pth_hits.append(f"{pth}:{line.strip()}")
    report.data["adapter_path_hooks"] = pth_hits


def _process_evidence(report: SurfaceReport, root: Path, surface: Surface, pid: int | None, resolved: Path | None) -> None:
    report.data["pid"] = pid
    if pid is None:
        report.data["cmdline"] = None
        status = STATUS_ERROR if surface.kind.startswith("systemd") else STATUS_WARN
        report.add("process_missing", status, "no live process could be identified")
        return
    argv = _proc_cmdline(pid)
    report.data["cmdline"] = " ".join(argv) if argv else None
    if not argv:
        report.add("cmdline_unreadable", STATUS_UNKNOWN, f"/proc/{pid}/cmdline is not readable")
        return
    cwd = os.readlink(f"/proc/{pid}/cwd") if os.access(f"/proc/{pid}/cwd", os.R_OK) else None
    report.data["process_cwd"] = cwd
    for label, value in (("cwd", cwd), ("cmdline", " ".join(argv))):
        if value and "/.claude/worktrees/" in value:
            report.add(
                "runtime_from_claude_worktree",
                STATUS_ERROR,
                f"the live {label} points into a Claude worktree, which is never runtime: {value}",
            )
    start = _proc_start_time(pid)
    if start is not None:
        report.data["process_started_at"] = datetime.fromtimestamp(start, timezone.utc).isoformat()

    scripts = _script_tokens(argv)
    if surface.source_kind == "native_binary":
        _check_native_executable(report, root, resolved, argv)
    elif scripts:
        _check_exec_paths(report, root, resolved, argv, "cmdline")
    elif surface.import_probe:
        _import_probe(report, root, surface, argv[0], resolved)
    else:
        report.add(
            "executed_source_unverifiable",
            STATUS_ERROR,
            "the command line carries no script path and no import probe is declared",
        )

    declared_exec = report.data.get("exec_start")
    if isinstance(declared_exec, str) and declared_exec.split() != argv:
        report.add(
            "unit_drift_since_start",
            STATUS_WARN,
            f"unit would now launch {declared_exec!r}; the live process runs {' '.join(argv)!r}",
        )

    if resolved is not None and start is not None:
        try:
            if resolved.stat().st_mtime > start:
                report.add(
                    "source_changed_after_start",
                    STATUS_ERROR,
                    f"{resolved} was modified after the process started; the "
                    "running bytes are not the bytes on disk",
                )
        except OSError:
            pass


def _port_evidence(report: SurfaceReport, surface: Surface, listeners: dict[int, dict[str, object]], profiles: dict[str, object]) -> None:
    branch_port = _declared_port_from_branch(
        profiles, surface.owner_branch, surface.source_declared
    )
    declared = surface.declared_port
    report.data["declared_port"] = declared
    report.data["declared_port_branch_profile"] = branch_port
    report.data["is_branch_hub"] = branch_port is not None
    if branch_port is not None and declared is not None and branch_port != declared:
        report.add(
            "declared_port_drift",
            STATUS_WARN,
            f"registry declares {declared}; branch {surface.owner_branch} profile declares {branch_port}",
        )

    pid = report.data.get("pid")
    candidates = ([declared] if declared is not None else []) + list(surface.fallback_ports)
    owned = [port for port, row in listeners.items() if pid is not None and row.get("pid") == pid]
    report.data["ports_owned_by_process"] = sorted(owned)

    effective: int | None = None
    fallback: int | None = None
    for port in candidates:
        row = listeners.get(port)
        if row is None and not _socket_open(port):
            continue
        if pid is not None and row is not None and row.get("pid") not in (None, pid):
            report.add(
                "port_owned_by_other_process",
                STATUS_ERROR,
                f"port {port} is held by pid {row.get('pid')} ({row.get('process')}), not {pid}",
            )
            continue
        effective = port
        if declared is not None and port != declared:
            fallback = port
        break

    if effective is None and owned:
        effective = sorted(owned)[0]
        if declared is not None and effective != declared:
            fallback = effective
            report.add(
                "undeclared_port",
                STATUS_ERROR,
                f"process listens on {effective}, which is neither the declared "
                f"port {declared} nor a known fallback",
            )

    report.data["effective_port"] = effective
    report.data["fallback_port"] = fallback
    report.data["declared_port_open"] = declared is not None and (
        declared in listeners or _socket_open(declared)
    )

    if effective is None:
        report.add(
            "listener_missing",
            STATUS_ERROR if surface.kind.startswith("systemd") else STATUS_WARN,
            f"no listener on {candidates}",
        )
        report.data["http_path"] = None
        report.data["http_status"] = None
        return

    if fallback is not None:
        report.add(
            "port_fallback",
            STATUS_WARN,
            f"declared {declared} is closed; the surface answers on fallback {fallback}",
        )

    probe = _probe_http(effective, surface.http_paths)
    report.data["http_path"] = probe.get("http_path")
    report.data["http_status"] = probe.get("http_status")
    report.data["http_bytes"] = probe.get("bytes")
    if probe.get("http_status") is None:
        report.add(
            "http_no_answer",
            STATUS_WARN,
            f"socket {effective} is open but no declared path answered",
        )
        return

    # An open listener is only credible once the source behind it is proven.
    source_proven = report.data.get("source_sha256") is not None and not any(
        finding.code
        in {
            "executed_source_mismatch",
            "executed_source_unverifiable",
            "exec_start_outside_root",
            "exec_start_historical",
            "import_probe_failed",
            "source_missing",
            "process_missing",
        }
        for finding in report.findings
    )
    if not source_proven:
        report.add(
            "listener_source_unverified",
            STATUS_ERROR,
            f"port {effective} answered HTTP {probe.get('http_status')} while the "
            "executed source could not be verified; a 200 is not proof of source",
        )


def evaluate(root: Path, surface: Surface, listeners: dict[int, dict[str, object]], profiles: dict[str, object]) -> SurfaceReport:
    report = SurfaceReport(surface.surface_id, surface.label, surface.kind)
    report.data["owner_branch"] = surface.owner_branch
    resolved = _resolve_source(report, root, surface)

    pid: int | None
    if surface.unit:
        pid = _unit_evidence(report, root, surface, resolved)
    else:
        report.data["unit"] = None
        report.data["unit_state"] = "manual_process"
        report.data["exec_start"] = None
        pid = None
    if pid is None and surface.process_match:
        pid = _find_manual_pid(surface)

    _process_evidence(report, root, surface, pid, resolved)
    _port_evidence(report, surface, listeners, profiles)
    return report


# --------------------------------------------------------------------------
# report assembly


def normalize_root(candidate: Path) -> tuple[Path, str | None]:
    """Collapse a root that points at the compatibility adapter.

    `/home/mak/flujo` is a real directory, so `realpath` does not collapse it
    and `root / "flujo"` would then invent `/home/mak/flujo/flujo`.  The
    adapter is never an independent operational root, so it is normalized to
    its parent and the substitution is recorded rather than hidden.
    """

    resolved = Path(os.path.realpath(candidate))
    if resolved.name == ADAPTER_NAME and (resolved.parent / ADAPTER_NAME).is_dir():
        siblings = [child for child in resolved.iterdir() if child.is_symlink()]
        if siblings:
            return resolved.parent, str(resolved)
    return resolved, None


def build_report(root: Path, invoked_from: Path) -> dict[str, object]:
    listeners = _listeners()
    branch = branch_context(root)
    profiles = branch.get("profiles", {})
    assert isinstance(profiles, dict)
    reports = [evaluate(root, surface, listeners, profiles) for surface in SURFACES]

    surfaces: list[dict[str, object]] = []
    for report in reports:
        row: dict[str, object] = {
            "surface_id": report.surface_id,
            "label": report.label,
            "kind": report.kind,
            "status": report.status,
            "branch": branch.get("checkout_branch"),
            "branch_kind": branch.get("checkout_branch_kind"),
            "conditions": report.conditions,
            "findings": [
                {"code": f.code, "status": f.status, "detail": f.detail} for f in report.findings
            ],
        }
        row.update(report.data)
        surfaces.append(row)

    counts = {
        status: sum(1 for report in reports if report.status == status)
        for status in (STATUS_OK, STATUS_OK_VIA_ADAPTER, STATUS_WARN, STATUS_UNKNOWN, STATUS_ERROR)
    }
    conditions = {
        condition: sum(1 for report in reports if report.conditions[condition])
        for condition in (CONDITION_ERROR, CONDITION_UNKNOWN, CONDITION_WARN, CONDITION_ADAPTER)
    }
    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "physical_root": str(root),
        "invoked_from": str(invoked_from),
        # sys.argv[0] is kept unresolved on purpose: realpath() collapses the
        # adapter, so the resolved path alone would report "not via adapter"
        # for an invocation that did go through it.
        "invoked_argv0": sys.argv[0],
        "invoked_via_adapter": (
            sys.argv[0].startswith(f"{root}/{ADAPTER_NAME}/")
            or str(invoked_from).startswith(f"{root}/{ADAPTER_NAME}/")
        ),
        "adapter": adapter_report(root),
        "branch": branch,
        "listeners": {str(port): row for port, row in sorted(listeners.items())},
        "summary": counts,
        "conditions": conditions,
        "surfaces": surfaces,
    }


def render_text(report: dict[str, object]) -> str:
    adapter = report["adapter"]
    assert isinstance(adapter, dict)
    lines = [
        f"{report['schema']} | root={report['physical_root']} | {report['generated_at']}",
        f"- invoked_from: {report['invoked_argv0']} -> {report['invoked_from']} "
        f"(via_adapter={report['invoked_via_adapter']})",
        (
            f"- adapter: {adapter['path']} role={adapter['role']} "
            f"symlink={adapter['is_symlink']} own_git_dir={adapter['own_git_dir']} "
            f"worktree={adapter['is_git_worktree']} sibling_symlinks={adapter['sibling_symlinks']} "
            f"recursive={len(adapter['recursive_symlinks'])} broken={len(adapter['broken_symlinks'])}"
        ),
    ]
    if report.get("root_normalized_from"):
        lines.append(
            f"- root_normalized_from: {report['root_normalized_from']} "
            "(the adapter is not an independent root)"
        )
    branch = report["branch"]
    assert isinstance(branch, dict)
    lines.append(
        f"- branch: {branch['checkout_branch']} kind={branch['checkout_branch_kind']} "
        f"selector={branch['checkout_selector']}"
    )
    summary = report["summary"]
    assert isinstance(summary, dict)
    lines.append(
        "- summary (worst status per surface): "
        + " ".join(f"{key}={value}" for key, value in summary.items())
    )
    conditions = report.get("conditions")
    if isinstance(conditions, dict):
        lines.append(
            "- conditions (surfaces carrying each, independent): "
            + " ".join(f"{key}={value}" for key, value in conditions.items())
        )
        lines.append(
            f"- exit codes: ok={EXIT_OK} error={EXIT_ERROR} unknown={EXIT_UNKNOWN} "
            f"warn={EXIT_WARN} (--strict) adapter={EXIT_ADAPTER} (--strict or --check-adapter)"
        )
    lines.append("")
    for row in report["surfaces"]:  # type: ignore[union-attr]
        assert isinstance(row, dict)
        sha = row.get("source_sha256")
        conds = row.get("conditions")
        carried = (
            ",".join(name for name, present in conds.items() if present)
            if isinstance(conds, dict)
            else ""
        )
        lines.append(
            f"[{row['status'].upper()}] {row['label']} ({row['surface_id']}, {row['kind']})"
            + (f" carries={carried}" if carried else "")
        )
        lines.append(f"    source_declared : {row.get('source_declared')}")
        lines.append(f"    source_resolved : {row.get('source_resolved')}")
        lines.append(f"    source_sha256   : {sha[:16] + '...' if isinstance(sha, str) else None}")
        lines.append(f"    unit / pid      : {row.get('unit')} [{row.get('unit_state')}] / {row.get('pid')}")
        lines.append(f"    exec_start      : {row.get('exec_start')}")
        lines.append(f"    cmdline         : {row.get('cmdline')}")
        if row.get("import_probe"):
            lines.append(f"    import_probe    : {row.get('import_probe')}")
        lines.append(
            f"    ports           : declared={row.get('declared_port')} "
            f"effective={row.get('effective_port')} fallback={row.get('fallback_port')}"
        )
        lines.append(
            f"    http            : {row.get('http_path')} -> {row.get('http_status')}"
        )
        for finding in row["findings"]:  # type: ignore[union-attr]
            assert isinstance(finding, dict)
            lines.append(f"    - {finding['status']}/{finding['code']}: {finding['detail']}")
        lines.append("")
    return "\n".join(lines)


def exit_code(report: dict[str, object], strict: bool = False, check_adapter: bool = False) -> int:
    """Map conditions to one code, worst condition first.

    Normal mode keeps its original contract: only a real error or an unknown
    unit is non-zero, so an operational warning does not block a caller that
    just wants to know whether the runtime is sound.

    ``--strict`` adds the two softer conditions, and ``--check-adapter``
    escalates the adapter dependency on its own.  Both codes are fixed per
    condition, so 3 always means "warning" and 4 always means "adapter
    dependency" no matter which flags produced them.  A run carrying several
    conditions returns the worst one; the full breakdown stays in
    ``conditions`` and in the per-surface rows.
    """

    conditions = report.get("conditions")
    if not isinstance(conditions, dict):
        conditions = {}
    if conditions.get(CONDITION_ERROR):
        return EXIT_ERROR
    if conditions.get(CONDITION_UNKNOWN):
        return EXIT_UNKNOWN
    if strict and conditions.get(CONDITION_WARN):
        return EXIT_WARN
    if (strict or check_adapter) and conditions.get(CONDITION_ADAPTER):
        return EXIT_ADAPTER
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=PHYSICAL_ROOT,
        help="physical root; defaults to /home/mak and is always resolved",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 on a source/exec/listener mismatch, 2 when a unit is unknown",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="also exit 3 on an operational warning and 4 on an adapter dependency",
    )
    parser.add_argument(
        "--check-adapter",
        action="store_true",
        help="exit 4 on an adapter dependency; independent of --strict",
    )
    args = parser.parse_args(argv)
    # --strict and --check-adapter are escalations of the check, so they imply
    # it.  Passing --check explicitly keeps working unchanged.
    checking = args.check or args.strict or args.check_adapter

    root, normalized_from = normalize_root(args.root)
    invoked_from = Path(__file__).resolve()
    report = build_report(root, invoked_from)
    report["root_normalized_from"] = normalized_from

    if args.format == "json":
        sys.stdout.write(json.dumps(report, ensure_ascii=True, indent=2) + "\n")
    else:
        sys.stdout.write(render_text(report))

    if checking:
        return exit_code(report, strict=args.strict, check_adapter=args.check_adapter)
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
