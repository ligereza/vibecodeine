# Phase 83 — RD field report read-only gate

## Scope

Validated the installed non-serve command for the real field-data boundary:
`/home/mak/venvs/flujo/bin/flujo rd-datos informe`.

## Foreground validation

- `flujo rd-datos --help` -> exit `0`; `ingest` and `informe` are exposed.
- Calling `informe` without required `--salida` -> exit `2`; correct CLI
  validation, no file/database change.
- `flujo rd-datos informe --salida /tmp/phase83-rd-datos-informe.md` -> exit
  `0`; wrote a 934-byte temporary report.
- The report correctly states that there is no real field data and emits empty
  trend/attention tables; no synthetic data was promoted.
- `/home/mak/flujo/data/rd_datos.db`: before and after size `0` bytes, mtime
  unchanged at `1786608165`.

## Decision

The read/report contract is integrated and truthful. Objective 1 remains
`DEFERRED_EMPTY_DATA_SOURCE`: the missing acta/approved real field dataset is
an external authority boundary, not a reason to seed demo rows.

## Safety and rollback

Only `/tmp/phase83-rd-datos-informe.md` was written. There was no ingest,
schema creation, database mutation, provider call or service. Rollback is
removal of the temporary report only; no MAK data requires recovery.

## Next

Continue with another read-only consumer or static dependency gate. Keep
`rd-datos ingest` deferred until real approved field data exists.
