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
    "cultura/mak_plataforma/mak-xio.service":
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
HOST = "%s@%s" % (os.environ.get("MAK_USER", "mak"),
                  os.environ.get("MAK_HOST", "192.168.50.2"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "MISSING"


def remote_hashes() -> tuple[dict[str, str], int, str]:
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
    try:
        r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", HOST, "sha256sum", *paths],
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
    a = ap.parse_args()
    remote, code, error = remote_hashes()
    rows = []
    for component, names in FILES.items():
        for name in names:
            win = sha(ROOT / "cultura" / component / name)
            repo = remote.get(f"/home/mak/flujo/cultura/{component}/{name}", "MISSING")
            live = remote.get(f"/home/mak/{LIVE_DIRS[component]}/{name}", "MISSING")
            state = "PASS" if win == repo == live and win != "MISSING" else "MISMATCH"
            rows.append((f"{component}/{name}", state, win[:12], repo[:12], live[:12]))
    for source, live_path in UNIT_FILES.items():
        win = sha(ROOT / source)
        live = remote.get(live_path, "MISSING")
        state = "PASS" if win == live and win != "MISSING" else "MISMATCH"
        rows.append((f"{source} -> {live_path}", state,
                     win[:12], "(not mirrored)", live[:12]))
    for name in CONDUCTOR_FILES:
        local_path = ROOT / "cultura" / "mak_conductor" / name
        remote_path = f"/home/mak/flujo/cultura/mak_conductor/{name}"
        win = sha(local_path)
        repo = remote.get(remote_path, "MISSING")
        state = "PASS" if win == repo and win != "MISSING" else "MISMATCH"
        rows.append((f"cultura/mak_conductor/{name}", state,
                     win[:12], repo[:12], "(repo package)"))
    for name in CONDUCTOR_TOOL_FILES:
        local_path = ROOT / "tools" / "mak_ops" / name
        remote_path = f"/home/mak/flujo/tools/mak_ops/{name}"
        win = sha(local_path)
        repo = remote.get(remote_path, "MISSING")
        state = "PASS" if win == repo and win != "MISSING" else "MISMATCH"
        rows.append((f"tools/mak_ops/{name}", state,
                     win[:12], repo[:12], "(repo tool)"))
    md = ["# MAK mirror check", "", f"Generated: `{dt.datetime.now().astimezone().isoformat(timespec='seconds')}`", "",
          f"SSH exit: `{code}`", f"SSH error: `{error or '(none)'}`", "",
          "| File | State | Windows main | MAK repo | MAK live |", "|---|---|---|---|---|"]
    md += [
        f"| {filename} | **{state}** | `{win_hash}` | `{repo_hash}` | `{live_hash}` |"
        for filename, state, win_hash, repo_hash, live_hash in rows
    ]
    Path(a.output).write_text("\n".join(md)+"\n", encoding="utf-8")
    print(f"Written: {Path(a.output).resolve()}")
    return 0 if code == 0 and all(row[1] == "PASS" for row in rows) else 1

if __name__ == "__main__":
    raise SystemExit(main())
