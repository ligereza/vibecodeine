# Phase 227 — Non-serve FLUJO CLI gate

## Scope

Foreground validation of the local, non-`serve` FLUJO command surface. The
checks use the existing base environment and only read current MAK state. No
job was created or activated, no datadrop was ingested, no render was run, and
no external provider was contacted.

## Results

| Surface | Command | Exit | Classification |
|---|---|---:|---|
| Version | `python -m flujo version` | 0 | read-only, passes |
| Health | `python -m flujo health` | 0 | read-only, passes |
| RD packs | `python -m flujo rd-db packs` | 0 | read-only, passes |
| RD events | `python -m flujo rd-db eventos` | 0 | read-only, passes |
| RD tests | `python -m flujo rd-db testeos` | 0 | read-only, passes |
| RD venues | `python -m flujo rd-db venues` | 0 | read-only, passes |
| Jobs | `python -m flujo job list` | 0 | read-only, 8 jobs visible |
| Next job | `python -m flujo job next` | 0 | read-only, next job resolved |
| Job status, valid path | `python -m flujo job status jobs/2026-07-02_cotizacion_general_agencia_eventos` | 0 | read-only, passes |
| Job status, missing argument | `python -m flujo job status` | 2 | expected CLI usage gate, not a runtime failure |
| Knowledge | `python -m flujo knowledge list` | 0 | read-only, passes |
| Datadrop | `python -m flujo datadrop list` | 0 | read-only, passes |
| Render formats | `python -m flujo render formats` | 0 | catalog read-only, passes |
| CLI syntax | `python -m py_compile src/flujo/cli.py` | 0 | syntax passes |

## Consumer map

- The canonical entry point is `/home/mak/flujo/src/flujo/cli.py`, exposed as
  `flujo = flujo.cli:app` in `pyproject.toml`.
- The hub advertises the same local commands through
  `/home/mak/flujo/src/flujo/web/hub.py`.
- Job lifecycle guidance points to `job prepare`, `job activate` and render;
  those are mutating or output-producing gates and were not invoked here.
- `rd-db build`, `rd-datos ingest`, datadrop ingest, job creation/activation,
  render execution and provider sync remain named mutators, not failures of
  the read-only CLI surface.

## Files changed

Only this report, its CSV companion and the operational handoff changed. No
runtime source, job, database, asset or historical WIN file changed.

## Next concrete action

Use the existing duplicate/document/tool ledgers to classify the remaining
MAK candidates by active consumer, language (Spanish/English), platform and
rollback. Quarantine only an exact, empty or confirmed-residue candidate; do
not merge or remove a working tool merely because it has a similar name.
