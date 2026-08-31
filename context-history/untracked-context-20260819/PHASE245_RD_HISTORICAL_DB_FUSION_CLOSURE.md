# Phase 245 - RD historical database fusion closure

Date: 2026-08-15 (America/Santiago)
Owner: LUNA principal

## Finding

The user-requested fusion of the `rd.db` sources is already present in the
active MAK database. This is distinct from `rd_datos.db`, which is a separate
privacy-first field-data store and is not another catalog `rd.db` source.

## Sources checked

| Path | Tables | Rows | Integrity | Content vs active |
|---|---:|---:|---|---|
| `/home/mak/flujo/data/rd.db` | 20 | 7,587 | ok | canonical active |
| `/home/mak/WIN/flujo/data/rd.db` | 20 | 7,587 | ok | identical |
| `/home/mak/state/windows-director-20260813/rd/rd.db` | 20 | 7,587 | ok | identical |
| `/home/mak/flujo/data/rd.db.premerge-20260815` | 12 | 113 | ok | recoverable pre-merge source |

## Foreground verification

The read-only SQLite command opened every source with `mode=ro`, checked
`PRAGMA integrity_check`, enumerated tables and rows, and computed a SHA-256
digest over each table schema and ordered row stream. It returned exit 0.
All 20 table digests and the table names match between the active database,
the WIN copy and the state snapshot. The pre-merge backup is intentionally
different: it contains the older 12-table/113-row catalog and is retained as
rollback evidence.

Phase 54 records the actual prior additive merge into
`/home/mak/flujo/data/rd.db`: historical `testeo_*` evidence tables and the
missing `productora_eventos` columns were added in a transaction, followed by
foreign-key, quick-check and temporary hub GET validation. No historical
source was deleted.

## Boundary

`/home/mak/flujo/data/rd_datos.db` currently has four schema tables and zero
data rows. Its consumers and lifecycle are privacy-first field ingest/report,
not catalog reconstruction. It remains separate; no field data was invented
or copied into the catalog. If the phrase "merge the RD databases" was meant
to include this privacy store, that is a different physical-consolidation
decision requiring a migration contract and rollback, and is not silently
performed by this closure.

## Result and rollback

Objective 2 is VERIFIED for the historical/catalog `rd.db` family. This phase
made no active-file changes. Rollback evidence remains at
`/home/mak/flujo/data/rd.db.premerge-20260815`, while WIN and the state copy
remain preserved as historical evidence.

## Next concrete action

Advance to the next unresolved objective: real RD field data, which requires
an actual CSV/acta and provenance authority. Keep `rd_datos.db` separate until
that input and its privacy contract exist; do not re-run the catalog merge.

