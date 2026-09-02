# FLUJO branch capabilities

This branch owns the portable workflow engine, CLI and workspace Hub.

Physical layout (2026-09-02): `/home/mak/flujo` is this checkout. The Linux
box is the parent checkout `/home/mak` (branch `MAK`), which consumes this
motor from `/home/mak/flujo/src`. This branch does NOT carry the MAK
departments, services or Hub: `cultura/mak_plataforma`, `mak_research`,
`mak_codex` and the systemd units live in MAK, and the box layer is an
optional peer here -- `flujo.autonomia` exposes `MAK_BOX_AVAILABLE` and
refuses with `MakBoxUnavailable` instead of failing at import time, so the
motor installs and runs on a machine that has no MAK tree.

Lane and real commands:

- `flujo`: `PYTHONPATH=/home/mak/flujo/src python -m pytest -o addopts='' -q
  -m flujo` with `requirements-flujo.txt`.
- Entrypoint: `python -m flujo --help` resolves from this branch content.
- Contract port `8765`: auto-detection is opt-in, so an explicit `--port`
  binds that port or fails; it is never moved silently.
- The `integration` lane is not here: it lives once in MAK, since it needs
  both checkouts.

## Owned surfaces

- `src/flujo/cli.py`: command-line entrypoint and orchestration.
- `src/flujo/web/hub.py`: workflow/workspace Hub, default port `8765`.
- `src/flujo/knowledge/`: evidence-governed project and system contracts.
- `tools/`: engine-facing operator tools required by the `flujo` lane.

## Validation

```text
python -m pytest -m flujo -q
python -m flujo --help
```

## Transferable consumers

`project_api.py`, `system_status.py`, `departments.py` and the
`data/mak_knowledge.db` schema are shared contracts. Transfer uses typed JSON
payloads and explicit source references; this branch does not import the MAK
Hub implementation.
