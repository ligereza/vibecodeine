# Phase 231 — RD database merge probe

## Scope

The user-requested RD database fusion was tested in a temporary SQLite output,
without touching either live database. The probe copied table schemas and rows
from the two sources into a disposable file, then ran SQLite integrity check.

## Source state

| Source | Tables | Rows | Integrity |
|---|---:|---:|---|
| `/home/mak/flujo/data/rd.db` | 20 | 7,587 | ok |
| `/home/mak/flujo/data/rd_datos.db` | 3 | 0 | ok |

The table-name intersection is empty. A temporary unified candidate therefore
contains 23 tables and 7,587 copied rows, with integrity `ok`. Both live SHA-256
hashes were unchanged (`LIVE_HASHES_UNCHANGED=True`). The probe's first draft
had a temporary SQLite attach/detach harness error (`database src0 is locked`);
the corrected foreground probe completed with exit 0 and no live writes.

## Architectural decision still open

Physical consolidation is technically possible, but the sources have different
authority contracts: `rd.db` is a regenerable public/catalog projection,
whereas `rd_datos.db` is the privacy-first field-data store and its ingest code
explicitly keeps it separate. The evidence proves that a blind table merge is
not necessary to resolve a schema collision; it does not yet prove that
co-locating privacy data in `rd.db` is safe for every consumer.

Therefore no live database was merged in this phase. The exact next decision is
either:

1. approve a physical consolidation with a migration/rollback and updated
   privacy boundary, or
2. accept a logical unified access contract while retaining the two physical
   stores by role.

Until that choice is explicit, both originals remain intact and operational.

## Next concrete action

Continue the objective audit with the proven current boundary: preserve the two
physical stores, map every database consumer, and keep the merge decision
visible rather than silently treating a temporary copy as integration.
