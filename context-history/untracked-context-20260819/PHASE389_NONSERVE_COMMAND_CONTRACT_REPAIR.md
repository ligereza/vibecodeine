# Phase 389 — non-serve CLI regression and command-contract repair

Date: 2026-08-15 (America/Santiago)

## Change

The active CLI contract is nested Typer syntax: `flujo job list` and
`flujo job next`. The source docstring and dashboard quick-command text still
printed the obsolete `flujo job-list`; both references were corrected.

Changed files:

- `/home/mak/flujo/src/flujo/cli.py`
- `/home/mak/flujo/src/flujo/dashboard/report.py`

## Foreground validation

| Command | Result |
|---|---|
| `venvs/flujo/bin/python -m flujo.cli version` | exit 0 |
| `... health` | exit 0; jobs/inbox/projects/scripts/tools OK |
| `... render formats` | exit 0; 14 formats listed |
| `... job list` | exit 0; 8 jobs listed |
| `... job next` | exit 0; next actions listed |
| `... datadrop list` | exit 0 |
| `... knowledge list` | exit 0 |
| `... rd-db --help` | exit 0 |
| `... rd-datos --help` | exit 0 |
| dashboard fixture render | exit 0; emits `flujo job list` and not `flujo job-list` |
| source AST (`cli.py`, `dashboard/report.py`) | 2/2 parsed |

`flujo job-list` was intentionally not added as a new alias; the documented
and implemented nested command remains the canonical interface. The separate
legacy `scripts/flujo.py job-next` wrapper was not changed because it has its
own dispatcher and consumer contract.

No service, hub, provider, network, database or generated product was used.

Disposition: `NONSERVE_COMMAND_CONTRACT_REPAIRED; LOCAL_GATE_GREEN`.
