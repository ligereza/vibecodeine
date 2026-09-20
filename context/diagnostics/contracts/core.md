# Core diagnostic contract

Use this packet for repo, Git, dependency, hub, runtime or CLI incidents.

## Read order

1. `AGENTS.md`
2. `REAL_INFO.md`
3. `branch_profile.json`
4. the exact code/config involved in the incident

Do not bootstrap from `DECISIONES.md`, `LAST_HANDOFF`, PHASE reports, recovered sessions or old “current state” documents.

## Facts

- Runtime MAK facts come from `.venv/bin/python tools/mak_status.py --json` when the MAK machine is available.
- Git facts come from the current branch/tree.
- `main` is currently the integrated MAK + FLUJO baseline; do not reuse old two-checkout assumptions without measuring them.
- The lane mapping lives in `context/test_lane_map.json` and its current tooling.
- Historical explanation lives in `HISTORICO.md`, never as a first read.

Run only bounded checks relevant to the report. Review commands before executing them and keep raw archives, credentials, databases and virtual environments outside the first read set.
