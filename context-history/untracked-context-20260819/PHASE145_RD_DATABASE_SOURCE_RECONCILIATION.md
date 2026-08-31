# Phase 145 — RD database source reconciliation

Date: 2026-08-15
Scope: `/home/mak/*`, with `WIN` treated as historical evidence.

## Result

MAK has two different RD databases by design; they must not be merged into one
file.

- `/home/mak/flujo/data/rd.db` is the active canonical projection. Its default
  path is declared by `src/flujo/rd/database.py` and its readers use it for
  packs, reactivos, productoras, venues, events and historical test-evidence
  projections. Read-only integrity check: `ok`; 20 SQLite tables; populated
  source/projection counts match the current MAK baseline.
- `/home/mak/flujo/data/rd_datos.db` is the separate privacy-first field-data
  accumulator declared by `src/flujo/rd/datos.py`. It has four schema tables
  and zero rows in `registros_testeo`, `atenciones`, `encuestas` and
  `sqlite_sequence`. It is correctly empty because no real field-data handoff
  has been authorized. It is not a duplicate of `rd.db`.

## Other database files found

| path | role | disposition |
|---|---|---|
| `/home/mak/WIN/flujo/data/rd.db` | historical WIN copy; same table contents as canonical | preserve; do not make active |
| `/home/mak/state/windows-director-20260813/rd/rd.db` | exact-content state snapshot of the WIN copy | preserve as evidence; no consumer found |
| `/home/mak/WIN/flujo/tmp_rd_integration_check.db` | temporary integration-check database | preserve inside WIN historical record; do not consume |
| `/home/mak/WIN/flujo/_logs/local_reconciliation_20260813/mak_rd.db` | older partial reconciliation snapshot; lacks `testeo_*` tables | preserve as log evidence; do not merge |

The canonical database and the WIN/state copies have identical table-level row
content in the read-only comparison. Their SQLite schema-object hashes differ
because the files were produced at different times/contexts, so the files are
not interchangeable runtime targets. The temporary integration-check copy has
the same table counts but different rows in five `testeo_*` tables. The older
log snapshot has the 12 base tables but no historical test-evidence projection.

## Consumer gate

Static inspection found the following ownership:

- `src/flujo/rd/database.py`: `DEFAULT_DB_PATH = repo/data/rd.db` and
  regenerable projection builder/readers.
- `src/flujo/rd/datos.py`: `DEFAULT_DB_PATH = repo/data/rd_datos.db`, separate
  privacy-first ingest schema.
- `src/flujo/rd/informe.py`: field-data summaries open `rd_datos.db` read-only
  for GET/report reads and return unavailable/empty-safe values.
- `src/flujo/web/hub.py`: `/api/rd-datos-summary` calls the field-data summary;
  it does not redirect the endpoint to `rd.db`.

Foreground read-only call `PYTHONPATH=/home/mak/flujo/src python3 ...
resumen_json()` exited 0 and returned `disponible=True` with all three field
totals at zero, `ultimo_ingest=None`, and the mandatory presuntive-data
disclaimer. No database file, WAL, source, output or WIN path changed.

## Decision

No database merge or cleanup is authorized by this phase. The next work is the
remaining RD source/output/delivery manifest and semantic document ownership
review. Any future field-data load requires a real handoff and the existing
privacy/ingest gate; any future database replacement requires a source-backed
rebuild and foreground validation.

## Commands and codes

- bounded database inventory under `/home/mak`: exit 0; one unavailable
  OneDrive mount warning was emitted by `find`, outside the RD paths.
- read-only SQLite integrity/schema/table-count audit: exit 0.
- table-content comparison against canonical: exit 0.
- consumer search with `grep` fallback because `rg` is unavailable: exit 0.
- read-only `resumen_json()` foreground call: exit 0.

