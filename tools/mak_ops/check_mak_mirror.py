#!/usr/bin/env python3
"""Comprueba read-only que repo main -> espejo vivo MAK coincide."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import os
import subprocess
from pathlib import Path

FILES = {
    "mak_plataforma": [
        "trabajo.py", "guardia.py", "hub.py", "backlog.py", "roles.py",
        "backlog_codex.py", "capataz.py", "coherence.py", "descargar.py",
        "entregar.py", "ideas.py", "junta.py", "latido.py", "material.py",
        "mutaciones.py", "providers.py", "puente_issues.py", "red_watch.py",
        "revision.py", "revision_episodios.py", "energia_log.py", "mineria_rd.py",
        "backup.sh", "watchdog_mak.sh", "vigilar_red.py", "revisor.py",
    ],
    "mak_research": [
        "fructificacion.py", "fusion.py", "ideas_a_micelio.py", "interfaz.py",
        "memoria.py", "pausa.py", "research_lib.py", "worker.py",
        "corpus_a_micelio.py", "micelio_guardia.sh", "retencion.py", "watchdog.sh",
    ],
    "mak_lenguaje": ["hook_barrido.py", "cron_lexicon.sh"],
    "mak_codex": ["agente_libre.py", "interfaz_codex.py"],
    "mak_vigia": ["vigia.py", "vigia_guardia.sh"],
    "mak_curatoria": ["percepcion.py", "curatoria_guardia.sh", "extraccion_db.py"],
}
# Service units are installed outside the component mirrors. Keep their source
# and live destination explicit so a bind or restart contract cannot drift.
UNIT_FILES = {
    "cultura/mak_plataforma/mak-hub.service":
        "/home/mak/.config/systemd/user/mak-hub.service",
    "cultura/mak_codex/mak-codex.service":
        "/home/mak/.config/systemd/user/mak-codex.service",
    "cultura/mak_xio_puente/mak-xio.service":
        "/home/mak/.config/systemd/user/mak-xio.service",
    "cultura/mak_research/interfaz.service":
        "/home/mak/.config/systemd/user/mak-research.service",
    "cultura/mak_research/cola.service":
        "/home/mak/.config/systemd/user/mak-research-queue.service",
}
LIVE_DIRS = {
    "mak_plataforma": "plataforma",
    "mak_research": "research",
    "mak_lenguaje": "lenguaje",
    "mak_codex": "codex",
    "mak_vigia": "vigia",
    "mak_curatoria": "curatoria",
}
CONDUCTOR_FILES = [
    "__init__.py", "conductor.py", "gpu_arbiter.py", "idempotency.py",
    "handler_registry.py", "producer_catalog.py", "queue_store.py",
    "queue_worker.py", "runtime.py", "source_bridge.py",
    "README.md",
]
CONDUCTOR_TOOL_FILES = [
    "run_conductor_worker.py", "run_conductor_shadow_probe.py",
    "run_conductor_source_probe.py", "mak-conductor-shadow.service",
    "mak-conductor-shadow.timer",
]
ROOT = Path(__file__).resolve().parents[2]
LIVE_ROOT = Path(os.environ.get("MAK_LIVE_ROOT", str(Path.home())))
AUDIT_SSH_HOST = os.environ.get("MAK_AUDIT_SSH_HOST", "").strip()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "MISSING"


def _local_hashes() -> tuple[dict[str, str], int, str]:
    values: dict[str, str] = {}
    for component, names in FILES.items():
        for name in names:
            values[str(ROOT / "cultura" / component / name)] = sha(
                ROOT / "cultura" / component / name)
            values[str(LIVE_ROOT / LIVE_DIRS[component] / name)] = sha(
                LIVE_ROOT / LIVE_DIRS[component] / name)
    values.update({path: sha(Path(path)) for path in UNIT_FILES.values()})
    for name in CONDUCTOR_FILES:
        path = ROOT / "cultura" / "mak_conductor" / name
        values[str(path)] = sha(path)
    for name in CONDUCTOR_TOOL_FILES:
        path = ROOT / "tools" / "mak_ops" / name
        values[str(path)] = sha(path)
    return values, 0, ""


def remote_hashes(host: str | None = None) -> tuple[dict[str, str], int, str]:
    """Hash the local box by default; SSH is an explicit audit exception."""
    if not host:
        return _local_hashes()
    paths = []
    for component, names in FILES.items():
        for name in names:
            paths += [f"/home/mak/flujo/cultura/{component}/{name}",
                      f"/home/mak/{LIVE_DIRS[component]}/{name}"]
    paths.extend(UNIT_FILES.values())
    paths.extend(f"/home/mak/flujo/cultura/mak_conductor/{name}"
                 for name in CONDUCTOR_FILES)
    paths.extend(f"/home/mak/flujo/tools/mak_ops/{name}"
                 for name in CONDUCTOR_TOOL_FILES)
    target = "%s@%s" % (os.environ.get("MAK_USER", "mak"), host)
    try:
        r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", target, "sha256sum", *paths],
                           capture_output=True, text=True, timeout=30)
    except Exception as exc:
        return {}, 99, str(exc)
    values: dict[str, str] = {}
    for line in r.stdout.splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            values[parts[1]] = parts[0]
    return values, r.returncode, r.stderr.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="mak_mirror_check.md")
    ap.add_argument("--ssh-host", default=AUDIT_SSH_HOST,
                    help="optional explicit SSH audit target; local is default")
    a = ap.parse_args()
    if a.ssh_host:
        remote, code, error = remote_hashes(a.ssh_host)
    else:
        remote, code, error = remote_hashes()
    checkout_root = Path("/home/mak/flujo") if a.ssh_host else ROOT
    live_root = Path("/home/mak") if a.ssh_host else LIVE_ROOT
    rows = []
    for component, names in FILES.items():
        for name in names:
            repo_path = checkout_root / "cultura" / component / name
            live_path = live_root / LIVE_DIRS[component] / name
            repo = remote.get(str(repo_path), "MISSING")
            live = remote.get(str(live_path), "MISSING")
            state = "PASS" if repo == live and repo != "MISSING" else "MISMATCH"
            rows.append((f"{component}/{name}", state, repo[:12], repo[:12], live[:12]))
    for source, live_path in UNIT_FILES.items():
        source_path = checkout_root / source
        live = remote.get(live_path, "MISSING")
        state = "PASS" if remote.get(str(source_path), "MISSING") == live and live != "MISSING" else "MISMATCH"
        rows.append((f"{source} -> {live_path}", state,
                     remote.get(str(source_path), "MISSING")[:12], "(not mirrored)", live[:12]))
    for name in CONDUCTOR_FILES:
        local_path = checkout_root / "cultura" / "mak_conductor" / name
        remote_path = f"/home/mak/flujo/cultura/mak_conductor/{name}"
        checkout = remote.get(str(local_path), "MISSING")
        repo = remote.get(remote_path, "MISSING")
        state = "PASS" if checkout == repo and checkout != "MISSING" else "MISMATCH"
        rows.append((f"cultura/mak_conductor/{name}", state,
                     checkout[:12], repo[:12], "(repo package)"))
    for name in CONDUCTOR_TOOL_FILES:
        local_path = checkout_root / "tools" / "mak_ops" / name
        remote_path = f"/home/mak/flujo/tools/mak_ops/{name}"
        checkout = remote.get(str(local_path), "MISSING")
        repo = remote.get(remote_path, "MISSING")
        state = "PASS" if checkout == repo and checkout != "MISSING" else "MISMATCH"
        rows.append((f"tools/mak_ops/{name}", state,
                     checkout[:12], repo[:12], "(repo tool)"))
    md = ["# MAK mirror check", "", f"Generated: `{dt.datetime.now().astimezone().isoformat(timespec='seconds')}`", "",
          f"Audit mode: `{'ssh' if a.ssh_host else 'local'}`", f"Audit exit: `{code}`", f"Audit error: `{error or '(none)'}`", "",
          "| File | State | Checkout | MAK repo | MAK live |", "|---|---|---|---|---|"]
    md += [
        f"| {filename} | **{state}** | `{win_hash}` | `{repo_hash}` | `{live_hash}` |"
        for filename, state, win_hash, repo_hash, live_hash in rows
    ]
    Path(a.output).write_text("\n".join(md)+"\n", encoding="utf-8")
    print(f"Written: {Path(a.output).resolve()}")
    return 0 if code == 0 and all(row[1] == "PASS" for row in rows) else 1

if __name__ == "__main__":
    raise SystemExit(main())
