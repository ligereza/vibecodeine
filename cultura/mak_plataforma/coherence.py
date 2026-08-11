#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Drift between the REPO and what the box actually runs.

Why it exists, measured 2026-07-30: the MAK-REPO-SYNC cron copies with
`cp -ru`, and `-u` means "only if the source is NEWER". One edit made on the
box freezes that file forever -- the repo version never lands again. Found
this way:

    revisor.py    repo 165 lines (2026-07-20 15:48)
                  box  216 lines (2026-07-20 17:39)  <- the one that runs

Those 51 extra lines were `enforce_pr()`, which merges PRs by itself and runs
every 6 hours by cron. It lived on one disk, unreviewed and unbacked. And the
repo copy -- the one anybody reads to understand what the reviewer does -- did
not even carry the `--enforce` flag it is invoked with.

The drift is one-directional and that is why nobody sees it: repo -> box is
forced every 10 minutes, box -> repo never happens.

    python3 coherence.py            # report
    python3 coherence.py --strict   # also exit 1 on drift

Exits 0 when everything matches. Writes nothing: it only looks.

Language note: names and comments here are ENGLISH, per CLAUDE.md. The organs
around it are Spanish-named for historical reasons (`entregar.py`, `revisor.py`,
`capataz.py`), and `docs/GLOSSARY.md` maps both sides so that a search in either
language finds the code instead of concluding it does not exist.
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
CLONE = HOME / "flujo" / "cultura"

# organ -> (directory in the repo, directory where it RUNS)
ORGANS = {
    "plataforma": (CLONE / "mak_plataforma", HOME / "plataforma"),
    "research": (CLONE / "mak_research", HOME / "research"),
    "codex": (CLONE / "mak_codex", HOME / "codex"),
    "curatoria": (CLONE / "mak_curatoria", HOME / "curatoria"),
    "xio_puente": (CLONE / "mak_xio_puente", HOME / "xio_puente"),
}

# What the box PRODUCES, which has no business being in the repo. This is not
# drift, it is its state. The distinction matters: if everything counts as
# drift the report becomes noise, nobody reads it, and that is exactly how the
# real findings get lost.
BOX_OWNED = ("piezas/", "fichas/", "jobs/", "logs/", "revisiones/", "estado",
             "procesados", "backlog", "rollback/", "__pycache__/", ".git/",
             "memoria/")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _box_owned(rel: str) -> bool:
    return any(m in rel.replace("\\", "/") for m in BOX_OWNED)


def inspect(name: str, repo: Path, live: Path) -> dict:
    r = {"organ": name, "different": [], "box_only": [], "not_copied": [],
         "exists": repo.is_dir() and live.is_dir()}
    if not r["exists"]:
        return r
    for f in sorted(repo.rglob("*.py")):
        rel = f.relative_to(repo).as_posix()
        if _box_owned(rel):
            continue
        target = live / rel
        if not target.exists():
            r["not_copied"].append(rel)
        elif _md5(f) != _md5(target):
            # who wins today: the newer mtime, which is what `cp -u` looks at
            wins = "box" if target.stat().st_mtime > f.stat().st_mtime else "repo"
            r["different"].append((rel, wins))
    for f in sorted(live.rglob("*.py")):
        rel = f.relative_to(live).as_posix()
        if _box_owned(rel):
            continue
        if not (repo / rel).exists():
            r["box_only"].append((rel, len(
                f.read_text(encoding="utf-8", errors="replace").splitlines())))
    return r


def _is_invoked(rel: str, cron: str, units: str) -> bool:
    """Whether cron or a systemd unit invokes it. An orphan that ALSO runs is
    urgent; one that does not run is a line in the handoff and nothing more.

    Both are checked because looking at cron alone missed `xio_puente/monitor.py`
    on 2026-07-30: 172 lines, no copy in the repo, started by `mak-xio.service`.
    """
    base = Path(rel).name
    return base in cron or base in units


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 on drift (for cron or CI)")
    args = ap.parse_args()

    def _run(cmd):
        try:
            return subprocess.run(cmd, capture_output=True, text=True,
                                  timeout=20).stdout
        except Exception:
            return ""

    cron = _run(["crontab", "-l"])
    units = ""
    for unit in (HOME / ".config" / "systemd" / "user").glob("*.service"):
        units += unit.read_text(encoding="utf-8", errors="replace")

    drift = 0
    for name, (repo, live) in ORGANS.items():
        r = inspect(name, repo, live)
        if not r["exists"]:
            print("== %-11s n/a (missing %s)"
                  % (name, repo if not repo.is_dir() else live))
            continue
        bad = len(r["different"]) + len(r["not_copied"])
        live_orphans = [(f, n) for f, n in r["box_only"]
                        if _is_invoked(f, cron, units)]
        drift += bad + len(live_orphans)
        print("== %-11s %d different, %d not copied, %d box-only "
              "(%d of them INVOKED)"
              % (name, len(r["different"]), len(r["not_copied"]),
                 len(r["box_only"]), len(live_orphans)))
        for rel, wins in r["different"]:
            print("   DIFFERENT  %-38s wins today: %s" % (rel, wins))
        for rel in r["not_copied"]:
            print("   NOT COPIED %-38s the repo has it, the box does not" % rel)
        for rel, n in live_orphans:
            print("   BOX ONLY   %-38s %d lines, AND SOMETHING RUNS IT"
                  % (rel, n))

    print()
    if drift:
        print("%d drift point(s). Whatever says 'wins today: box' will never "
              "update on its own again: `cp -u` does not overwrite a newer "
              "file." % drift)
    else:
        print("No drift: the box runs what the repo says.")
    return 1 if (drift and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
