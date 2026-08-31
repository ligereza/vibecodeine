# Phase 321 — non-serve read-only consumer gate

Date: 2026-08-15 (America/Santiago)
Scope: read-only FLUJO commands deferred by the earlier CLI matrix.

## Runtime and safety boundary

Used the existing interpreter `/home/mak/venvs/flujo/bin/python` with
`PYTHONPATH=/home/mak/flujo/src:/home/mak/flujo` and
`PYTHONDONTWRITEBYTECODE=1`. No `serve`, `app`, worker, provider, network,
ingest, build, render or mutator command was called.

## Commands and results

Help/namespace checks all returned rc=0:

- `python -m flujo --help`
- `python -m flujo knowledge --help`
- `python -m flujo job --help`
- `python -m flujo job list --help`
- `python -m flujo job status --help`
- `python -m flujo job next --help`
- `python -m flujo job report --help`
- `python -m flujo rd-db productora --help`
- `python -m flujo rd-db lookup --help`
- `python -m flujo datadrop --help`
- `python -m flujo datadrop list --help`
- `python -m flujo datadrop scan --help`

Read-only foreground commands returned rc=0:

- `knowledge list`: 3 entities (`creamfields`, `rave_under_template`,
  `thegrid`).
- `job list`: 8 jobs and their states/pendientes rendered.
- `job next`: next actions rendered for all 8 jobs.
- `rd-db lookup MDMA`: reactives, TESTEO/COMPLETO packs and the presumptive
  disclaimer rendered from the canonical catalog.
- `rd-db productora thegrid`: profile, aliases, logo and venue status rendered.
- `knowledge show productora thegrid`: YAML-backed JSON profile rendered.
- `rd-db reactivo --familia MDMA`: five reactive rows rendered with the same
  presumptive disclaimer.
- `datadrop list`: five existing datadrop entries rendered.

Two intentional command-shape probes returned rc=2 and caused no mutation:

- `rd-db productoras` was rejected; the command is singular `productora`.
- `knowledge show thegrid` was rejected; the contract requires
  `knowledge show productora thegrid`. A first probe `rd-db reactivo MDMA`
  was also rejected; the valid form is `rd-db reactivo --familia MDMA`.

## Disposition

`VERIFIED_READ_ONLY_CONSUMER_SURFACE`.

The read-only non-serve surface is usable for jobs, knowledge, RD catalog
lookup/profile/reactives and datadrops. The command help clearly separates
writers (`build`, `ingest`, `scan`, `new`, `prepare`, `activate`, `render run`)
from readers. The earlier objective remains partial because those writers and
live/provider boundaries still need separate fixtures, rollback and authority.

## Changes and risks

- Source/data/output changes: none observed.
- `rd.db` and `rd_datos.db`: not written.
- Risk: `datadrop scan`, `rd-db build`, job creation/preparation and field-data
  ingest remain mutating; help success is not execution success.
- Rollback: none needed; no file was changed.

