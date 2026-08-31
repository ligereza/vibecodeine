# Phase 406 — RD database fusion closure

Date: 2026-08-15 (America/Santiago)

## Sources compared

| Path | Role | Tables | Rows | Integrity | Schema metadata |
|---|---|---:|---:|---|---|
| `/home/mak/flujo/data/rd.db` | active canonical catalog | 20 | 7,587 | `ok` | `schema_version=37`, `user_version=20260815` |
| `/home/mak/state/windows-director-20260813/rd/rd.db` | historical state snapshot | 20 | 7,587 | `ok` | `schema_version=35`, `user_version=0` |
| `/home/mak/WIN/flujo/data/rd.db` | historical Windows snapshot | 20 | 7,587 | `ok` | same normalized data |
| `/home/mak/WIN/flujo/tmp_rd_integration_check.db` | temporary integration evidence | 20 | 7,587 | `ok` | same normalized data |
| `/home/mak/WIN/flujo/_logs/local_reconciliation_20260813/mak_rd.db` | older reconciliation artifact | 12 | 113 | `ok` | incomplete historical subset |
| `/home/mak/flujo/data/rd.db.premerge-20260815` | recoverable pre-merge source | older snapshot | n/a | preserved | not active |

## Merge result

The two live data sets have identical normalized table schemas and identical
rows in all 20 tables. The comparison covered primary-key ordered rows and
column metadata; result:

```text
table_set_equal:       True
normalized_schema_equal: True
normalized_rows_equal:   True
```

The Windows catalog snapshot and temporary integration check also match the
canonical 20-table/7,587-row normalized data. The 12-table/113-row
`mak_rd.db` is an older reconciliation artifact and is not a complete source
for additive merge; it remains historical evidence.

The earlier apparent DDL difference in `productora_eventos` is formatting and
comment placement only. `PRAGMA table_info` is equal, including
`fuentes_primarias` and `sin_fuente_primaria`. The only meaningful database
metadata difference is that the state snapshot predates the active schema
version marker.

Therefore the correct fusion is additive/no-op at row level: the canonical
`/home/mak/flujo/data/rd.db` already contains the complete union and must not
be overwritten by the older snapshot. The state copy remains immutable
historical evidence and has no active MAK consumer. No row, schema, database,
WIN, credential or generated product was changed in this phase.

## Validation commands

```text
PRAGMA integrity_check on both databases: ok
20 tables and 7,587 rows on both databases: equal
active consumer search for state/WIN snapshots: no runtime reference found
```

`rd_datos.db` was not part of this fusion. It remains the separate empty
privacy/field store by design.

Disposition: `RD_DB_FUSION_CLOSED; CANONICAL_OWNER_CONFIRMED; SNAPSHOT_PRESERVED`.
