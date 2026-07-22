#!/usr/bin/env python3
"""Comprueba read-only que repo main -> espejo vivo MAK coincide."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, subprocess
from pathlib import Path

FILES = ["trabajo.py", "guardia.py", "hub.py", "backlog.py", "roles.py"]
ROOT = Path.cwd()
HOST = "mak@192.168.50.2"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "MISSING"


def remote_hashes() -> tuple[dict[str, str], int, str]:
    paths = []
    for name in FILES:
        paths += [f"/home/mak/flujo/cultura/mak_plataforma/{name}", f"/home/mak/plataforma/{name}"]
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
    for name in FILES:
        win = sha(ROOT / "cultura" / "mak_plataforma" / name)
        repo = remote.get(f"/home/mak/flujo/cultura/mak_plataforma/{name}", "MISSING")
        live = remote.get(f"/home/mak/plataforma/{name}", "MISSING")
        state = "PASS" if win == repo == live and win != "MISSING" else "MISMATCH"
        rows.append((name, state, win[:12], repo[:12], live[:12]))
    md = ["# MAK mirror check", "", f"Generated: `{dt.datetime.now().astimezone().isoformat(timespec='seconds')}`", "",
          f"SSH exit: `{code}`", f"SSH error: `{error or '(none)'}`", "",
          "| File | State | Windows main | MAK repo | MAK live |", "|---|---|---|---|---|"]
    md += [f"| {f} | **{s}** | `{w}` | `{r}` | `{l}` |" for f,s,w,r,l in rows]
    Path(a.output).write_text("\n".join(md)+"\n", encoding="utf-8")
    print(f"Written: {Path(a.output).resolve()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
