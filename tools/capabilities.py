#!/usr/bin/env python3
"""Probe MAK and FLUJO capability surfaces against their declarations.

The registry in this file is deliberately small and explicit: a path or a
process name is not treated as a capability by itself.  The command compares
the registry with the capability documents, then (optionally) probes the
current user services and local listeners.  It emits evidence; it never edits
CAPACIDADES.md automatically.

Examples::

    python3 tools/capabilities.py
    python3 tools/capabilities.py --format json --output state/capabilities-runtime.json
    python3 tools/capabilities.py --check --no-live
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.error import URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class Surface:
    """One declared runtime/capability surface."""

    surface_id: str
    label: str
    owner: str
    source: str
    doc_anchors: tuple[str, ...]
    unit: str | None = None
    ports: tuple[int, ...] = ()
    http_paths: tuple[str, ...] = ()
    expectation: str = "manual"
    unit_scope: str = "user"
    models: tuple[str, ...] = ()
    consumer_sources: tuple[str, ...] = ()


# Keep this list explicit.  It is the semantic bridge between the physical
# services and the human capability registry; discovery alone cannot tell a
# compatibility wrapper from an owned Hub.
SURFACES: tuple[Surface, ...] = (
    Surface(
        "mak_hub",
        "MAK Hub",
        "mak",
        "cultura/mak_plataforma/hub.py",
        ("MAK Hub", "cultura/mak_plataforma/hub.py"),
        unit=".config/systemd/user/mak-hub.service",
        ports=(8900,),
        http_paths=("/health", "/api/status"),
        expectation="service_active",
    ),
    Surface(
        "flujo_app",
        "FLUJO App",
        "flujo",
        "src/flujo/web/hub.py",
        ("FLUJO App", "src/flujo/web/hub.py"),
        ports=(8765, 8766),
        http_paths=("/",),
        expectation="manual",
    ),
    Surface(
        "flujo_serve",
        "FLUJO serve",
        "flujo",
        "src/flujo/serve/server.py",
        ("FLUJO `serve`", "src/flujo/serve/server.py"),
        ports=(8777,),
        http_paths=("/",),
        expectation="manual",
    ),
    Surface(
        "mak_research",
        "Research",
        "mak",
        "cultura/mak_research/interfaz.py",
        ("Research", "cultura/mak_research/interfaz.py"),
        unit=".config/systemd/user/mak-research.service",
        ports=(8890,),
        http_paths=("/",),
        expectation="service_active",
    ),
    Surface(
        "mak_codex",
        "Codex bridge",
        "mak",
        "cultura/mak_codex/interfaz_codex.py",
        ("Codex bridge", "cultura/mak_codex/interfaz_codex.py"),
        unit=".config/systemd/user/mak-codex.service",
        ports=(8891,),
        http_paths=("/",),
        expectation="service_active",
    ),
    Surface(
        "ollama",
        "Ollama local inference",
        "mak",
        "cultura/mak_research/research_lib.py",
        ("ollama LOCAL en MAK", "ollama.service"),
        unit="/etc/systemd/system/ollama.service",
        unit_scope="system",
        ports=(11434,),
        http_paths=("/api/version", "/api/tags"),
        expectation="service_active",
        models=("gemma3:4b", "deepseek-coder:6.7b", "nomic-embed-text:latest"),
        consumer_sources=(
            "cultura/mak_research/research_lib.py",
            "cultura/mak_codex/codex_lib.py",
            "cultura/mak_plataforma/discernment.py",
            "cultura/mak_plataforma/mineria_rd.py",
            "cultura/mak_plataforma/tandas.py",
            "cultura/mak_plataforma/chat_agente.py",
        ),
    ),
    Surface(
        "mak_copilot",
        "Copilot curatorial",
        "mak",
        "cultura/mak_plataforma/copilot.py",
        ("Copilot curatorial", "cultura/mak_plataforma/copilot.py"),
        expectation="embedded",
    ),
    Surface(
        "searxng",
        "SearXNG",
        "mak",
        "searxng/settings.yml",
        ("SearXNG", "searxng/settings.yml"),
        ports=(8888,),
        http_paths=("/",),
        expectation="observe",
    ),
    Surface(
        "mak_research_queue",
        "ntfy queue",
        "mak",
        ".config/systemd/user/mak-research-queue.service",
        ("Cola ntfy", ".config/systemd/user/mak-research-queue.service"),
        unit=".config/systemd/user/mak-research-queue.service",
        expectation="optional_inactive",
    ),
)


def _run_systemctl(unit: str, scope: str = "user") -> str:
    """Return a bounded unit state without treating missing systemd as a bug."""

    try:
        command = ["systemctl"]
        if scope == "user":
            command.append("--user")
        command.extend(("is-active", unit))
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=3,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "unavailable"
    state = result.stdout.strip()
    if state in {"active", "inactive", "failed", "activating", "deactivating"}:
        return state
    if result.returncode == 5 or "not found" in result.stderr.lower():
        return "missing"
    return state or "unavailable"


def _probe_http(port: int, paths: Iterable[str]) -> dict[str, object]:
    """Probe one local TCP port and the first responding HTTP path."""

    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.5):
            socket_open = True
    except OSError:
        return {"port": port, "socket_open": False, "http_status": None, "http_path": None}

    for path in paths:
        try:
            request = Request(f"http://127.0.0.1:{port}{path}", method="GET")
            with urlopen(request, timeout=2) as response:
                return {
                    "port": port,
                    "socket_open": socket_open,
                    "http_status": int(response.status),
                    "http_path": path,
                }
        except (OSError, URLError, ValueError):
            continue
    return {"port": port, "socket_open": socket_open, "http_status": None, "http_path": None}


def _declared(docs: list[Path], anchors: tuple[str, ...]) -> list[str]:
    """Find rows where the label and canonical source occur together."""

    hits: list[str] = []
    lowered = tuple(anchor.lower() for anchor in anchors)
    for doc in docs:
        try:
            lines = doc.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        if any(all(anchor in line.lower() for anchor in lowered) for line in lines):
            hits.append(str(doc))
    return hits


def _surface_result(root: Path, docs: list[Path], surface: Surface, live: bool) -> dict[str, object]:
    source_path = root / surface.source
    unit_path = None
    if surface.unit:
        unit_path = Path(surface.unit)
        if not unit_path.is_absolute():
            unit_path = root / unit_path
    consumer_present = [
        path for path in surface.consumer_sources if (root / path).is_file()
    ]
    consumer_missing = [
        path for path in surface.consumer_sources if not (root / path).is_file()
    ]
    result: dict[str, object] = {
        "id": surface.surface_id,
        "label": surface.label,
        "owner": surface.owner,
        "source": surface.source,
        "source_exists": source_path.is_file(),
        "unit": surface.unit,
        "unit_scope": surface.unit_scope,
        "unit_exists": unit_path.is_file() if unit_path else None,
        # systemctl receives the unit name, while the registry keeps the
        # repository-relative unit path for provenance and source checks.
        "unit_state": (
            _run_systemctl(Path(surface.unit).name, scope=surface.unit_scope)
            if live and surface.unit
            else "not_applicable"
        ),
        "declared_in": _declared(docs, surface.doc_anchors),
        "ports": [],
        "expectation": surface.expectation,
        "models_expected": list(surface.models),
        "models_present": [],
        "consumer_sources": list(surface.consumer_sources),
        "consumer_sources_present": consumer_present,
        "consumer_sources_missing": consumer_missing,
        "issues": [],
    }
    if live and surface.ports:
        result["ports"] = [_probe_http(port, surface.http_paths) for port in surface.ports]

    issues: list[str] = result["issues"]  # type: ignore[assignment]
    if not result["source_exists"]:
        issues.append("source_missing")
    if not result["declared_in"]:
        issues.append("capability_row_missing")
    if consumer_missing:
        issues.append("consumer_source_missing:" + ",".join(consumer_missing))

    if live and surface.models and surface.ports:
        try:
            request = Request(f"http://127.0.0.1:{surface.ports[0]}/api/tags", method="GET")
            with urlopen(request, timeout=2) as response:
                payload = json.load(response)
            model_rows = payload.get("models", []) if isinstance(payload, dict) else []
            names = {
                str(row.get("name"))
                for row in model_rows
                if isinstance(row, dict) and row.get("name")
            }
            present = [name for name in surface.models if name in names]
            result["models_present"] = present
            missing = [name for name in surface.models if name not in names]
            if missing:
                issues.append("models_missing:" + ",".join(missing))
        except (OSError, URLError, ValueError, json.JSONDecodeError):
            issues.append("models_probe_failed")

    state = str(result["unit_state"])
    if surface.expectation == "service_active" and live:
        if state != "active":
            issues.append(f"unit_not_active:{state}")
        ports = result["ports"]
        if ports and not any(bool(item["socket_open"]) for item in ports):
            issues.append("listener_missing")
    return result


def _git_value(root: Path, *args: str) -> str | None:
    """Read one bounded Git fact without treating Git as physical authority."""

    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=3,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _branch_result(root: Path) -> dict[str, object]:
    """Check the branch contract when a checkout exposes one."""

    branch = _git_value(root, "branch", "--show-current")
    profile_path = root / "branch_profile.json"
    result: dict[str, object] = {
        "branch": branch,
        "profile_path": str(profile_path),
        "profile_exists": profile_path.is_file(),
        "profile_branch": None,
        "profile_kind": None,
        "capabilities": None,
        "requirements": None,
        "hub_source": None,
        "selector": None,
        "pyproject_addopts": None,
        "issues": [],
    }
    issues: list[str] = result["issues"]  # type: ignore[assignment]
    if not branch:
        issues.append("branch_unknown")
    if not profile_path.is_file():
        issues.append("branch_profile_missing")
        return result
    try:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        issues.append("branch_profile_unreadable")
        return result

    profile_branch = profile.get("branch")
    profile_kind = profile.get("kind", "runtime")
    result["profile_branch"] = profile_branch
    result["profile_kind"] = profile_kind
    result["selector"] = profile.get("default_test_selector")
    capabilities = profile.get("capabilities")
    requirements = profile.get("requirements")
    hub = profile.get("hub") or {}
    hub_source = hub.get("module") if isinstance(hub, dict) else None
    result["capabilities"] = capabilities
    result["requirements"] = requirements
    result["hub_source"] = hub_source

    if branch and profile_branch != branch:
        issues.append(f"profile_branch_mismatch:{profile_branch!s}->{branch}")
    if not isinstance(capabilities, str) or not (root / capabilities).is_file():
        issues.append("profile_capabilities_missing")
    if not isinstance(requirements, str) or not (root / requirements).is_file():
        issues.append("profile_requirements_missing")
    if profile_kind == "historical":
        if hub_source is not None:
            issues.append("historical_hub_declared")
    elif not isinstance(hub_source, str) or not (root / hub_source).is_file():
        issues.append("profile_hub_source_missing")

    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        try:
            text = pyproject.read_text(encoding="utf-8")
        except OSError:
            text = ""
        marker = next(
            (line.split("=", 1)[1].strip().strip('"')
             for line in text.splitlines() if line.strip().startswith("addopts =")),
            None,
        )
        result["pyproject_addopts"] = marker
        selector = profile.get("default_test_selector")
        if profile_kind == "historical" and selector:
            issues.append("historical_selector_declared")
        elif isinstance(selector, str) and selector and selector not in (marker or ""):
            issues.append("profile_selector_not_in_pytest_addopts")
    return result


def _markdown(report: dict[str, object]) -> str:
    rows = [
        "# Capability runtime check",
        "",
        f"- schema: `{report['schema']}`",
        f"- generated_at: `{report['generated_at']}`",
        f"- root: `{report['root']}`",
        "",
        "| Surface | Owner | Source | Declared | Unit | Listener | Issues |",
        "|---|---|---|---:|---|---|---|",
    ]
    for item in report["surfaces"]:  # type: ignore[union-attr]
        declared = ", ".join(Path(p).name for p in item["declared_in"]) or "NO"
        unit = item["unit_state"]
        listeners = [p for p in item["ports"] if p["socket_open"]]
        listener = ", ".join(str(p["port"]) for p in listeners) or "none"
        issues = ", ".join(item["issues"]) or "—"
        rows.append(
            f"| {item['label']} | {item['owner']} | `{item['source']}` | "
            f"{declared} | {unit} | {listener} | {issues} |"
        )
    rows.extend(
        [
            "",
            f"- branch: `{report['branch']['branch']}`; profile: `{report['branch']['profile_branch']}`; "
            f"branch_issues: {', '.join(report['branch']['issues']) or '—'}",
            "",
            "This report is evidence only; it does not rewrite capability documents.",
        ]
    )
    return "\n".join(rows) + "\n"


def _write_atomic(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def build_report(root: Path, docs: list[Path], live: bool) -> dict[str, object]:
    results = [_surface_result(root, docs, surface, live) for surface in SURFACES]
    return {
        "schema": "mak-capabilities-runtime-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "documents": [str(doc) for doc in docs],
        "live_probe": live,
        "summary": {
            "surfaces": len(results),
            "declared": sum(bool(item["declared_in"]) for item in results),
            "sources_present": sum(bool(item["source_exists"]) for item in results),
            "with_issues": sum(bool(item["issues"]) for item in results),
        },
        "branch": _branch_result(root),
        "surfaces": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--docs",
        type=Path,
        action="append",
        help="capability document(s), relative to --root; defaults to existing CAPACIDADES files",
    )
    parser.add_argument("--format", choices=("text", "json", "markdown"), default="text")
    parser.add_argument("--output", type=Path, help="write the selected report atomically")
    parser.add_argument("--no-live", action="store_true", help="skip systemd, socket and HTTP probes")
    parser.add_argument(
        "--check-branch",
        action="store_true",
        help="also require branch_profile.json to match the checkout and pytest selector",
    )
    parser.add_argument("--check", action="store_true", help="exit 1 if a source/row/service is missing")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    doc_paths = args.docs or [
        Path("CAPACIDADES.md"),
        Path("CAPACIDADES_MAK.md"),
        Path("CAPACIDADES_FLUJO.md"),
    ]
    docs = [(path if path.is_absolute() else root / path) for path in doc_paths]
    docs = [path for path in docs if path.is_file()]
    report = build_report(root, docs, live=not args.no_live)

    if args.format == "json":
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    elif args.format == "markdown":
        rendered = _markdown(report)
    else:
        rendered = (
            f"{report['schema']} | {report['summary']['declared']}/"
            f"{report['summary']['surfaces']} declared | "
            f"{report['summary']['sources_present']}/{report['summary']['surfaces']} sources | "
            f"issues={report['summary']['with_issues']}\n"
        )
        rendered += (
            f"- branch: {report['branch']['branch'] or 'UNKNOWN'}; "
            f"profile={report['branch']['profile_branch'] or 'UNKNOWN'}; "
            f"branch_issues={','.join(report['branch']['issues']) or 'ok'}\n"
        )
        for item in report["surfaces"]:  # type: ignore[union-attr]
            listeners = [p["port"] for p in item["ports"] if p["socket_open"]]
            problems = ",".join(item["issues"]) or "ok"
            rendered += (
                f"- {item['label']}: source={'yes' if item['source_exists'] else 'NO'}; "
                f"declared={'yes' if item['declared_in'] else 'NO'}; "
                f"unit={item['unit_state']}; listeners={listeners or '-'}; {problems}\n"
            )
            if item["models_expected"]:
                rendered += (
                    f"  models={item['models_present']}/{item['models_expected']}; "
                    f"consumers={len(item['consumer_sources_present'])}/"
                    f"{len(item['consumer_sources'])}\n"
                )

    if args.output:
        output = args.output if args.output.is_absolute() else root / args.output
        _write_atomic(output, rendered)
    else:
        sys.stdout.write(rendered)

    if args.check:
        issues = int(report["summary"]["with_issues"])
        if args.check_branch:
            issues += len(report["branch"]["issues"])
        return 1 if issues else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
