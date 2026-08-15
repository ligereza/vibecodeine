# Branch handoff: rd/venue-crosswalk

Branch: `rd/venue-crosswalk`
Contract: `contracts/branches/rd-venue-crosswalk/agents.md`
Owner: `LUNA-504`
Base commit: `2431b26`

## Current objective

Expose the crosswalk's declared source databases as validated provenance while
keeping RD and technical venue sources physically separate and read-only.

## Baseline evidence

- `data/rd.db`: populated catalog, 2,740,224 bytes, 20 tables with RD data.
- `data/rd_datos.db`: separate operational store, 20,480 bytes, 4 empty
  tables; not a second catalog.
- `data/venues/*.json`: technical venue projections, including SCD.
- Existing crosswalk adapter tests pass before this change.

## Open items

- Promote the durable gate result to the root handoff before branch deletion.

## Next concrete action

`EntityCrosswalk` now preserves the declared `source_databases` tuple and
rejects absolute, Windows-drive, empty-segment or parent-traversal references.
The adapter remains JSON-only and does not open SQLite.

Validation results:

- compile and combined crosswalk/RD/venue suite: exit 0;
- current contract exposes `('data/rd.db', 'data/rd_datos.db')`, four entities
  and `review_only` status;
- unsafe source reference negative test rejects without writing;
- SHA-256 hashes for `data/rd.db` and `data/rd_datos.db` unchanged;
- `git diff --check`: exit 0.

No database, venue JSON, portfolio artifact, README, WIN or service changed.

## Disposition

`RD_VENUE_PROVENANCE_GREEN; NO_DATABASE_MERGE; REVIEW_ONLY_PRESERVED;
SOURCE_HASHES_GREEN`

## Next concrete action

Promote this result to the root handoff, remove the temporary branch contract
and handoff, fast-forward `main`, and delete the short-lived branch.

Last verified: 2026-08-15 America/Santiago.
