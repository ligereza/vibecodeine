#!/usr/bin/env python3
"""Comprueba read-only que repo main -> espejo vivo MAK coincide."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, os, subprocess
from pathlib import Path

FILES = {
    "mak_plataforma": ["trabajo.py", "guardia.py", "hub.py", "backlog.py", "roles.py"],
    "mak_curatoria": ["percepcion.py", "curatoria_guardia.sh", "extraccion_db.py"],
}
LIVE_DIRS = {"mak_plataforma": "plataforma", "mak_curatoria": "curatoria"}
ROOT = Path.cwd()
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
    md = ["# MAK mirror check", "", f"Generated: `{dt.datetime.now().astimezone().isoformat(timespec='seconds')}`", "",
          f"SSH exit: `{code}`", f"SSH error: `{error or '(none)'}`", "",
          "| File | State | Windows main | MAK repo | MAK live |", "|---|---|---|---|---|"]
    md += [f"| {f} | **{s}** | `{w}` | `{r}` | `{l}` |" for f,s,w,r,l in rows]
    Path(a.output).write_text("\n".join(md)+"\n", encoding="utf-8")
    print(f"Written: {Path(a.output).resolve()}")
    return 0 if code == 0 and all(row[1] == "PASS" for row in rows) else 1

if __name__ == "__main__":
    raise SystemExit(main())
