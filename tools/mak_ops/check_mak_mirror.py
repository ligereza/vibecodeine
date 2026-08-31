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
    # xio_puente is the only organ whose live files are plain copies rather
    # than bridges: `mak-xio.service` declares the organ copy as its runtime
    # source on purpose, so a phone incident can be patched without going
    # through commit, CI and merge. A copy CAN drift where a shim cannot, and
    # until 2026-08-29 this was the one organ with no drift check at all.
    # Measured that day: the three files were still byte-identical.
    "mak_xio_puente": ["monitor.py"],
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
    "mak_xio_puente": "xio_puente",
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
MAK_HOME = Path("/home/mak")
HOST = "%s@%s" % (os.environ.get("MAK_USER", "mak"),
                  os.environ.get("MAK_HOST", "192.168.50.2"))

# Measured 2026-08-29: 192.168.50.2 is the old Windows machine on the old LAN.
# It does not answer, and this box now lives on 10.75.122.x. With the SSH leg
# dead, `remote_hashes()` returned {} and EVERY row printed MISMATCH/MISSING --
# including files that plainly exist. A drift detector that always cries drift
# is worse than none: it trains the reader to ignore it.
#
# So the local comparison is now the default and the only one that runs unless
# `--remoto` is passed: does each organ copy under /home/mak still match its
# canonical file in flujo/cultura/? That is the question MAK has today, and it
# is the only one that can be answered without a machine that is gone.


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


def local_rows() -> tuple[list[tuple[str, str, str, str, str]], int]:
    """Organ copy versus canonical file, on this machine. No network."""
    rows: list[tuple[str, str, str, str, str]] = []
    drifted = 0
    for component, names in FILES.items():
        live_dir = LIVE_DIRS.get(component)
        if not live_dir:
            continue
        for name in names:
            canonical = ROOT / "cultura" / component / name
            live = MAK_HOME / live_dir / name
            c_hash, l_hash = sha(canonical), sha(live)
            if l_hash == "MISSING":
                state = "AUSENTE en el organo"
            elif c_hash == "MISSING":
                state = "AUSENTE en el repo"
            elif c_hash == l_hash:
                state = "IGUAL"
            elif _is_bridge(live, canonical):
                state = "PUENTE"          # a bridge is not expected to match
            else:
                state = "DERIVO"
                drifted += 1
            rows.append((f"{component}/{name}", state, c_hash[:12], l_hash[:12],
                         "symlink" if live.is_symlink() else ""))
    return rows, drifted


def _is_bridge(live: Path, canonical: Path) -> bool:
    """Does this organ file delegate to the canonical instead of copying it?

    Three shapes, and missing one of them is how a healthy bridge gets reported
    as drift: a symlink, a Python shim loading the canonical with
    `spec_from_file_location` or `runpy`, and -- the one this check missed at
    first -- a shell bridge that `exec`s the canonical path directly, which is
    what `backup.sh` and `watchdog_mak.sh` do.
    """
    if live.is_symlink():
        return True
    body = _head(live, 4000)
    if "spec_from_file_location" in body or "runpy" in body:
        return True
    return "exec" in body and (canonical.name in body or str(canonical) in body)


def _head(path: Path, limit: int = 2000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Deriva entre las copias de organo y el canonico del repo.")
    ap.add_argument("--output", default="mak_mirror_check.md")
    ap.add_argument("--remoto", action="store_true",
                    help="ademas compara por SSH contra MAK_HOST (la maquina "
                         "de la arquitectura anterior; hoy no responde)")
    a = ap.parse_args()

    rows_local, drifted = local_rows()
    print(f"deriva local: {drifted} archivo(s) divergen del canonico")
    for name, state, c, l, note in rows_local:
        if state not in ("IGUAL", "PUENTE"):
            print(f"  {state:22} {name} {note}")
    if not drifted:
        print("  ninguno: cada copia de organo coincide con su canonico")
    if not a.remoto:
        md = ["| archivo | estado | canonico | organo |", "|---|---|---|---|"]
        md += [f"| {n} | {s} | `{c}` | `{l}` |" for n, s, c, l, _ in rows_local]
        Path(a.output).write_text("\n".join(md) + "\n", encoding="utf-8")
        print(f"\nEscrito: {Path(a.output).resolve()}")
        return 1 if drifted else 0

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
