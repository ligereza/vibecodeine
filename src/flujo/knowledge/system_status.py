"""Read-only operational map for the consumers that make up MAK.

The project ledger answers "what does the learning loop know?".  This module
answers the larger operational question: are the local Hub, Research, event
runner, render stack, portfolio surface, search service and configured model
routes present and reachable on this machine?

It intentionally performs bounded local checks only.  It does not call the
internet, execute a job, start a service, write a database or return secret
values.  A provider being configured is reported as configuration evidence,
not as a successful external API call.
"""

from __future__ import annotations

import os
import re
import shutil
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .project_api import operational_status
from .runtime_tools import resolve_blender


SYSTEM_SCHEMA = "mak-system-status-v1"
_PORTS = {
    "hub": 8900,
    "research": 8890,
    "codex": 8891,
    "search": 8888,
    "ollama": 11434,
}


def _path_status(path: Path, *, kind: str = "file") -> dict[str, Any]:
    try:
        exists = path.is_file() if kind == "file" else path.is_dir()
    except OSError:
        exists = False
    return {"path": str(path), "exists": exists}


def _listener(port: int) -> dict[str, Any]:
    """Check one loopback listener without making a request or changing state."""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.25):
            return {"host": "127.0.0.1", "port": port, "reachable": True}
    except OSError:
        return {"host": "127.0.0.1", "port": port, "reachable": False}


def _process_snapshot(tokens: Iterable[str]) -> dict[str, Any]:
    """Count matching local processes without returning command lines or PIDs."""
    wanted = tuple(token.lower() for token in tokens if token)
    count = 0
    try:
        proc_root = Path("/proc")
        for entry in proc_root.iterdir():
            if not entry.name.isdigit():
                continue
            try:
                command = (entry / "cmdline").read_bytes()[:2048].replace(b"\x00", b" ").decode(
                    "utf-8", "replace"
                ).lower()
            except OSError:
                continue
            if command and any(token in command for token in wanted):
                count += 1
    except OSError:
        pass
    return {"running": count > 0, "count": count}


def _executable_snapshot(names: Iterable[str]) -> dict[str, Any]:
    """Count processes by their actual executable, not by argument text."""
    wanted = {Path(name).name.lower() for name in names if name}
    count = 0
    try:
        for entry in Path("/proc").iterdir():
            if not entry.name.isdigit():
                continue
            try:
                executable = Path(os.readlink(entry / "exe")).name.lower()
            except OSError:
                continue
            if executable in wanted:
                count += 1
    except OSError:
        pass
    return {"running": count > 0, "count": count}


def _component(
    component_id: str,
    label: str,
    status: str,
    *,
    severity: str = "none",
    read_only: bool = True,
    evidence: dict[str, Any] | None = None,
    next_action: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": component_id,
        "label": label,
        "status": status,
        "severity": severity,
        "read_only": read_only,
        "evidence": evidence or {},
    }
    if next_action:
        result["next_action"] = next_action
    return result


def _repo_component(repo: Path) -> dict[str, Any]:
    required = {
        "agents": repo / "agents.md",
        "hub_source": repo / "cultura" / "mak_plataforma" / "hub.py",
        "knowledge_api": repo / "src" / "flujo" / "knowledge" / "project_api.py",
        "web_source": repo / "web" / "package.json",
    }
    evidence = {name: _path_status(path) for name, path in required.items()}
    ok = all(row["exists"] for row in evidence.values())
    return _component(
        "repo",
        "MAK source",
        "ready" if ok else "attention",
        severity="none" if ok else "attention",
        evidence=evidence,
        next_action=None if ok else "restore the missing source contract before changing consumers",
    )


def _service_component(
    component_id: str,
    label: str,
    source: Path,
    port: int,
    process_tokens: Iterable[str],
) -> dict[str, Any]:
    source_evidence = _path_status(source)
    listener = _listener(port)
    process = _process_snapshot(process_tokens)
    ok = source_evidence["exists"] and listener["reachable"] and process["running"]
    return _component(
        component_id,
        label,
        "ready" if ok else "attention",
        severity="none" if ok else "attention",
        evidence={"source": source_evidence, "listener": listener, "process": process},
        next_action=None if ok else "check the source, local listener and process before sending work to this consumer",
    )


def _runner_component(repo: Path, physical: Path) -> dict[str, Any]:
    workflow = repo / ".github" / "workflows" / "issue_descarga_ig.yml"
    runner_dir = physical / "actions-runner"
    process = _process_snapshot(("actions-runner", "Runner.Listener"))
    evidence = {
        "workflow": _path_status(workflow),
        "runner_root": _path_status(runner_dir, kind="dir"),
        "process": process,
        "mode": "local_runner_only",
        "external_delivery": "not_verified",
    }
    ok = evidence["workflow"]["exists"] and evidence["runner_root"]["exists"] and process["running"]
    return _component(
        "events",
        "Issue/event runner",
        "ready" if ok else "attention",
        severity="none" if ok else "attention",
        evidence=evidence,
        next_action=None if ok else "inspect the bounded runner contract before accepting a new event",
    )


def _render_component(repo: Path, physical: Path) -> dict[str, Any]:
    blender = resolve_blender(repo)
    scene = physical / "RD" / "AUTOMATIZACION" / "RD.blend"
    active = _executable_snapshot(("blender",))
    evidence = {
        "blender": {"path": str(blender), "exists": blender is not None} if blender else {"exists": False},
        "scene": _path_status(scene),
        "process": active,
        "execution": "not_started_by_status",
    }
    ok = blender is not None and evidence["scene"]["exists"]
    return _component(
        "render",
        "Blender / render",
        "active" if ok and active["running"] else "ready" if ok else "attention",
        severity="none" if ok else "attention",
        evidence=evidence,
        next_action=None if ok else "restore the Blender binary or the authorized RD scene before rendering",
    )


def _portfolio_component(physical: Path) -> dict[str, Any]:
    platform = physical / "plataforma"
    media = physical / "portfolio_media"
    evidence = {
        "platform": _path_status(platform, kind="dir"),
        "media": _path_status(media, kind="dir"),
        "local_surface": "available_if_platform_is_running",
        "external_verification": "not_run",
    }
    ok = evidence["platform"]["exists"] and evidence["media"]["exists"]
    return _component(
        "portfolio",
        "Portafolio / web local",
        "ready" if ok else "attention",
        severity="none" if ok else "attention",
        evidence=evidence,
        next_action=None if ok else "restore the local portfolio surface before treating deployment as available",
    )


def _dependency_component(repo: Path) -> dict[str, Any]:
    blender = resolve_blender(repo)
    node_candidates = []
    configured_node = os.environ.get("NODE_EXE", "").strip()
    if configured_node:
        node_candidates.append(Path(configured_node).expanduser())
    found_node = shutil.which("node")
    if found_node:
        node_candidates.append(Path(found_node))
    node_candidates.append(Path("/home/mak/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"))
    node = next((path for path in node_candidates if path.is_file()), None)
    evidence = {
        "python": {"available": True, "version": sys.version.split()[0]},
        "node": {"available": node is not None, **({"path": str(node)} if node else {})},
        "blender": {"available": blender is not None, **({"path": str(blender)} if blender else {})},
        "install_policy": "status_never_installs",
    }
    ok = bool(node and blender)
    return _component(
        "dependencies",
        "Runtime dependencies",
        "ready" if ok else "attention",
        severity="none" if ok else "attention",
        evidence=evidence,
        next_action=None if ok else "restore the missing local runtime before running a consumer",
    )


def _provider_component(repo: Path, physical: Path) -> dict[str, Any]:
    try:
        # The CLI is launched from ``tools/`` and therefore does not always
        # have the repository root on sys.path.  Add only this known source
        # root for the in-process registry import; no files are changed.
        import sys as _sys
        repo_text = str(repo)
        if repo_text not in _sys.path:
            _sys.path.insert(0, repo_text)
        from cultura.mak_plataforma import providers

        names: set[str] = set(os.environ)
        env_files = (
            physical / "research" / "research.env",
            physical / "research.env",
            Path.home() / "research" / "research.env",
        )
        key_pattern = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=")
        for env_file in env_files:
            try:
                for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
                    match = key_pattern.match(line)
                    if match:
                        names.add(match.group(1))
            except OSError:
                continue
        # Values are intentionally replaced by a sentinel.  The registry only
        # needs presence to classify configuration and never receives secrets.
        safe_environment = {name: "configured" for name in names}
        registry = providers.provider_registry(environment=safe_environment)
        configured = sum(1 for row in registry["providers"] if row["configured"])
        return _component(
            "providers",
            "API/model routes",
            "ready" if configured else "attention",
            severity="none" if configured else "attention",
            evidence={
                "configured": configured,
                "total": len(registry["providers"]),
                "providers": registry["providers"],
                "runtime": "configuration_only_unverified",
            },
            next_action=None if configured else "configure an authorized provider or use the local deterministic route",
        )
    except Exception as exc:  # noqa: BLE001 - status must remain available
        return _component(
            "providers",
            "API/model routes",
            "attention",
            severity="attention",
            evidence={"available": False, "error": type(exc).__name__},
            next_action="repair the provider registry import before routing external work",
        )


def system_status(
    database: str | Path,
    *,
    repo_root: str | Path,
    physical_root: str | Path | None = None,
) -> dict[str, Any]:
    """Return one read-only status envelope for local MAK consumers."""
    repo = Path(repo_root).expanduser().resolve()
    physical = Path(physical_root).expanduser().resolve() if physical_root else repo.parent
    ledger = operational_status(database, repo_root=repo)
    components = {
        "repo": _repo_component(repo),
        "hub": _service_component(
            "hub", "MAK Hub 8900", physical / "plataforma" / "hub.py", _PORTS["hub"],
            ("plataforma/hub.py", "mak_plataforma/hub.py"),
        ),
        "research": _service_component(
            "research", "Research 8890", physical / "research" / "interfaz.py", _PORTS["research"],
            ("research/interfaz.py",),
        ),
        "codex": _service_component(
            "codex", "Codex bridge 8891", physical / "codex" / "interfaz_codex.py", _PORTS["codex"],
            ("codex/interfaz_codex.py",),
        ),
        "search": _service_component(
            "search", "SearXNG 8888", physical / "searxng" / "settings.yml", _PORTS["search"],
            ("searxng", "searxng_server"),
        ),
        "events": _runner_component(repo, physical),
        "render": _render_component(repo, physical),
        "portfolio": _portfolio_component(physical),
        "dependencies": _dependency_component(repo),
        "providers": _provider_component(repo, physical),
    }

    attention: list[dict[str, Any]] = []
    for item in ledger.get("attention", []):
        attention.append({"scope": "ledger", **item})
    for component in components.values():
        if component["severity"] in {"attention", "blocked"}:
            attention.append({
                "scope": "component",
                "id": component["id"],
                "kind": "consumer",
                "status": component["status"],
                "severity": component["severity"],
                "reason": f"{component['label']} is {component['status']}",
                "next_action": component.get("next_action", "inspect the component evidence"),
            })
    severities = {str(item.get("severity")) for item in attention}
    if "blocked" in severities:
        overall = "blocked"
    elif "attention" in severities:
        overall = "attention"
    elif ledger.get("status") == "unknown":
        overall = "unknown"
    else:
        overall = "ready"
    next_actions: list[str] = []
    for item in attention:
        action = str(item.get("next_action") or "").strip()
        if action and action not in next_actions:
            next_actions.append(action)
    return {
        "schema": SYSTEM_SCHEMA,
        "status": overall,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "repo_root": str(repo),
        "physical_root": str(physical),
        "learning": ledger.get("learning", {}),
        "ledger": ledger,
        "components": components,
        "attention": attention,
        "counts": {
            "attention": sum(1 for item in attention if item.get("severity") == "attention"),
            "blocked": sum(1 for item in attention if item.get("severity") == "blocked"),
            "info": sum(1 for item in attention if item.get("severity") == "info"),
            "components": len(components),
        },
        "next_actions": next_actions,
    }
