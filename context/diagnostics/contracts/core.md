# Core diagnostic contract

Use this packet for repo, Git, dependency, hub, runtime or CLI incidents.

Read first: `AGENTS.md`, `pyproject.toml`, the current
`context/LAST_HANDOFF.md`, `cultura/mak_plataforma/hub.py` and
`context/test_lane_map.json`.

Two notes on that list, both measured 2026-09-02, because the previous version
of it sent a fresh agent to files this checkout cannot contain:

- **The contract is `AGENTS.md`, uppercase.** A lowercase `agents.md` also sits
  at the root and declares itself canonical; it is the 2026-08-31 contract and
  its own header now says so. Linux is case-sensitive, so these are two files,
  not one.
- **The motor is not in this checkout.** MAK carries no `src/flujo`: the CLI
  and `diagnostics.py` live in the FLUJO checkout, on this box at
  `flujo/src/flujo/`, which is a separate worktree excluded from this branch
  and therefore absent in CI. Read it there when an incident is about the
  motor; its absence here is the topology, never a missing file.

The lane authority for which tests belong to which checkout is
`context/test_lane_map.json`, not the directory a test happens to sit in.

Run only bounded checks declared by the report. Never execute a command copied
from an error message without reviewing it. Keep WIN, databases, credentials
and virtual environments outside the first read set.

Suggested branch: `maintenance/<short-slug>`.
