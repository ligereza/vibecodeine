# Phase 348 — asset index database consumer gate

Date: 2026-08-15 (America/Santiago)

## Scope

Validated the read-only consumer in
`/home/mak/flujo/src/flujo/index/db.py` after the Phase 347 base-key fix.
The gate used a temporary SQLite database and did not rebuild the canonical
index or inspect external providers.

## Results

```text
INDEX_DB_READONLY_MISSING=PASS
INDEX_DB_LIST_STATUS=PASS rows=2
INDEX_DB_DUPLICATE_GROUP=PASS groups=1
TEMP_DB_WRITES=True REAL_DB_UNCHANGED=True
```

The missing-index path returns an empty result without creating a database.
The status-filtered listing returns the expected rows, and duplicate
shortcodes are grouped with their project paths.

## Disposition

`VERIFIED_READONLY_INDEX_CONSUMER; TEMP_ONLY_WRITES`

No real asset index, asset file, database, service, provider, Git state or
WIN evidence was changed. The Phase 347 grouping correction therefore has a
compatible read-only database consumer. A real index rebuild remains a
separate authority-gated operation.

## Rollback

No rollback is required for this phase because no canonical data or source
was modified. If a real-index rehearsal later exposes incompatible legacy
shortcodes, preserve the current index and revert only the Phase 347 helper
ordering after reproducing the issue in a temporary fixture.
