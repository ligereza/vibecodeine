# Phase 475 — RD database physical authority

Read-only verification on 2026-08-15. No SQLite connection opened in write
mode and no database file was changed.

## Physical findings

| Path | Size | Role | Tables |
|---|---:|---|---:|
| `/home/mak/flujo/data/rd.db` | 2,740,224 | MAK physical enriched candidate | 20 |
| `/home/mak/flujo/data/rd_datos.db` | 20,480 | MAK operational projection | 4 |
| `/home/mak/WIN/flujo/data/rd.db` | 2,740,224 | Windows historical evidence | 20 |
| `/home/mak/state/windows-director-20260813/rd/rd.db` | 2,740,224 | recovered Windows snapshot | 20 |

The MAK `rd.db` SHA-256 begins `91b748f5661ed948`; the WIN and recovered
Windows copies both begin `c3ddea0c77c8d3ee`. Therefore MAK `rd.db` is not an
exact duplicate of the Windows authority even though the table surface is the
same. It must remain a candidate requiring reconciliation, not be overwritten
by either copy.

`rd_datos.db` has only `atenciones`, `encuestas`, `registros_testeo` and
`sqlite_sequence`; it is not a second enriched catalog. It remains a separate
operational projection. The entity adapter and web consumers must read through
bounded contracts and must not silently merge or write either database.

## Git consequence

The clean Git checkout intentionally does not contain these ignored/local
SQLite files. Git tracks the schema-facing code and fixtures; the physical
databases remain on MAK/WIN with provenance and hashes recorded here. Any
future promotion must include a read-only comparison report, explicit owner,
target path, rollback copy and human authorization before a data mutation.

Disposition:
`RD_DB_PRESENT_PHYSICALLY; MAK_HASH_DIFFERS_FROM_WIN; RD_DATOS_SEPARATE;
READ_ONLY; NO_DATABASE_MERGE_PERFORMED`.
