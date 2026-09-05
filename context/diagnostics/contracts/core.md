# Core diagnostic contract

Use this packet for repo, Git, dependency, hub, runtime or CLI incidents.

Read first: `DECISIONES.md`, `pyproject.toml`,
`cultura/mak_plataforma/hub.py` and `context/test_lane_map.json`.

Four notes on that list, because earlier versions of it sent a fresh agent to
files this checkout cannot contain:

- **There is no contract file, and that is the decision** (2026-09-05). Every
  one this repository had was deleted by the operator's order: `CLAUDE.md`, the
  lowercase `agents.md` and the three `contracts/departments/*/agents.md` on
  2026-09-03, and `AGENTS.md` itself on 2026-09-05. Nothing replaced it.
  `DECISIONES.md` holds what the operator decided, and a decision does not age
  because it already happened. **Do not reconstruct a contract from anything
  you find, and do not write a new one.** The absence is not a gap to fill.
- **Facts come from the machine, not from a document**:
  `.venv/bin/python tools/mak_status.py`. `context/HANDOFF_HISTORICO.md` was
  `LAST_HANDOFF.md` and is a record only -- for finding information that is
  missing, or what happened to a file or document. It is deliberately NOT in
  the read-first list: routing history as a first read turns it back into
  state.
- **The motor is not in this checkout.** MAK carries no `src/flujo`: the CLI
  and `diagnostics.py` live in the FLUJO checkout, on this box at
  `flujo/src/flujo/`, which is a separate worktree excluded from this branch
  and therefore absent in CI. Read it there when an incident is about the
  motor; its absence here is the topology, never a missing file.
- **There is no Windows node** (2026-09-03, operator). It was an old computer
  and it is gone. This Linux box is the whole system, and the interpreter is
  `.venv/bin/python` -- the system `python3` carries neither `flujo` nor
  `pytest`.

The lane authority for which tests belong to which checkout is
`context/test_lane_map.json`, not the directory a test happens to sit in.

Run only bounded checks declared by the report. Never execute a command copied
from an error message without reviewing it. Keep the mounted SSD raw archive,
databases, credentials and virtual environments outside the first read set.

Suggested branch: `maintenance/<short-slug>`.
