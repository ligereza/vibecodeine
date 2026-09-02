# Phase 204 — FLUJO non-serve command gate (LUNA-1)

Date: 2026-08-15 (America/Santiago)

## Result

The canonical FLUJO CLI is `/home/mak/flujo/src/flujo/cli.py`, exposed by
`/home/mak/flujo/src/flujo/__main__.py`. The actual RD namespace is `rd-db`.
The CLI module header does not currently advertise an `rd` command; no source
edit was needed for this point.

## Read-only commands validated

All commands used `PYTHONPATH=/home/mak/flujo/src`
and `/home/mak/venvs/flujo/bin/python`:

| Command | Exit | Result |
|---|---:|---|
| `python -m flujo --help` | 1 | Help rendered; exit 1 came from `head` closing the pipe, not a CLI startup failure. |
| `python -m flujo version` | 0 | Version `0.56.1`; changelog rendered. |
| `python -m flujo rd-db --help` | 0 | RD commands exposed, including explicit mutator boundaries. |
| `python -m flujo rd-db packs` | 0 | Three operational packs rendered. |
| `python -m flujo rd-db eventos` | 0 | Two registered events rendered. |
| `python -m flujo rd-db testeos` | 0 | Evidence summary rendered: 42 sheets, 1,831 test rows, 5,394 observations; status remains human-review pending. |
| `python -m flujo rd-db venues` | 0 | Three canonical venues rendered. |
| `python -m flujo health` | 0 | Required workspace folders, eight jobs and `data/flujo.db` detected. |
| `python -m flujo render formats` | 1 | Fourteen formats rendered; exit 1 came from `head` closing the pipe. |

The command family `rd-db build` and `rd-datos ingest` remains deferred because
it writes databases. `render run`, `job new/prepare/activate`, `datadrop
ingest`, `airdrop apply`, `serve`, `app`, and provider/automation commands are
also outside this read-only gate. They require their own fixture, mutation,
rollback and/or explicit external-authority boundary.

## Interpretation

The non-`serve` CLI layer is present and usable for read-only operations. This
does not mean every command is functionally closed: commands that create jobs,
render products, ingest field data, or call providers are still pending. The
RD evidence summary is not the empty field database: it is a separate imported
evidence summary with publication still blocked by human review. `rd.db` and
`rd_datos.db` remain separate authorities.

## Change and safety record

- Added this report and its CSV companion.
- No source, database, output, service, package, provider, or Git mutation
  occurred in this phase.
- The user service states remained inactive during the gate.

## Next concrete action

Continue the open functional audit by mapping the remaining non-`serve`
commands to their consumers and mutation class, beginning with read-only
`knowledge`, `job list/status/next/report`, `rd-db productora/lookup`, and
`datadrop list/scan`. Keep writes deferred and feed any confirmed duplicate or
legacy family into the Phase 203 cleanup ledger.

