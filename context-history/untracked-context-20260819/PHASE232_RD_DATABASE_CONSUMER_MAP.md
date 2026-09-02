# Phase 232 — RD database consumer map

## Physical sources

| Source | Owner | Read/write behavior | Consumer contract |
|---|---|---|---|
| `/home/mak/flujo/data/rd.db` | `src/flujo/rd/database.py` | `build_rd_db()` regenerates; `connect()` may build if missing; query helpers read through that connection | catalog, productoras, venues, packs, events and imported testing evidence |
| `/home/mak/flujo/data/rd_datos.db` | `src/flujo/rd/datos.py` | `conectar()` creates schema for ingest; `ingest_csv()` inserts only after privacy scan; report reader is separate | privacy-first field data: testeos, atenciones and encuestas |

## Active source consumers

The bounded source search found six relevant operational files:

- `/home/mak/flujo/src/flujo/rd/database.py`: catalog builder and readers;
- `/home/mak/flujo/src/flujo/rd/datos.py`: field ingest/schema owner;
- `/home/mak/flujo/src/flujo/rd/informe.py`: read-only field summary;
- `/home/mak/flujo/src/flujo/web/hub.py`: RD catalog and field-summary endpoints;
- `/home/mak/flujo/src/flujo/cli.py`: `rd-db` and `rd-datos` commands;
- `/home/mak/flujo/cultura/mak_curatoria/ingesta_archivo.py`: read-only
  catalog snapshot for producer/venue/event metadata.

Tests use temporary paths and do not define a production owner. Documentation
and historical reports were excluded from the active consumer count.

## Merge implication

The temporary Phase 231 candidate proved that the schemas can coexist (20 + 3
tables, no name collision), but the consumer map shows a lifecycle collision:
`rd.db` can be rebuilt and `rd_datos.db` is accumulative/privacy-first. A
physical merge would require changing both default paths, the builder's
regeneration boundary, ingest privacy assumptions, hub readers and tests. A
logical facade could expose both under one RD access contract without moving
private rows into the regenerable catalog. No live database was changed.

## Validation

- SQLite source inspection: both integrity checks `ok`.
- Bounded consumer/reference scan: exit 0.
- Live database SHA-256 values unchanged after the merge probe.
- No provider, service, job, ingest, rebuild or Git operation.

## Next concrete action

Keep this consumer map as the authority while finishing the remaining RD route
mutator fixtures. If physical fusion is required, perform it only as a named
migration with a backup, path transition, privacy review and rollback; do not
silently rewrite the two current owners.
