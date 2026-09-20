# Core diagnostic contract

Use this packet for repo, Git, dependency, hub, runtime or CLI incidents.

Read first: `SYSTEM.md`, `pyproject.toml`,
`cultura/mak_plataforma/hub.py`, `src/flujo/cli.py` and
`context/test_lane_map.json`.

Current invariants:

- There is no persistent `AGENTS.md` or handoff entry contract. Do not
  reconstruct one. Durable identities and operator decisions live in
  `SYSTEM.md`.
- Facts are measured, not copied from prose. Use
  `python tools/contexto_repo.py --json` for the checkout and
  `python tools/mak_status.py --json` when MAK runtime state matters.
- Integrated main carries FLUJO under `src/flujo/`. A sibling FLUJO checkout
  may exist on MAK, but its presence is not required to understand this tree.
- MAK is the Linux computer. Windows is the current control/development/render
  workstation connected to MAK. The retired historical Windows runtime/archive
  (for example `/home/mak/WIN`) is not the current Windows workstation.
- History explains provenance; it is not the default first-read surface.

The lane authority for which tests belong to which checkout is
`context/test_lane_map.json`.

Run only bounded checks declared by the report. Never execute a command copied
from an error message without reviewing it. Keep mounted raw archives,
databases, credentials and virtual environments outside the first read set.

Suggested branch: `maintenance/<short-slug>`.
