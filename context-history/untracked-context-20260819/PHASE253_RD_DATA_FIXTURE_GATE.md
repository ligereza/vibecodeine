# Phase 253 — RD database and privacy fixture gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Scope

Promote one bounded group from the excluded-test inventory:

- `tests/test_rd_database.py`
- `tests/test_rd_datos.py`
- `tests/test_rd_db_logos.py`
- `tests/test_privacy.py`

These tests construct catalog/privacy databases and files under pytest
`tmp_path`, or inspect static source. They do not require a server, provider,
network, live route or external integration.

## Validation

```text
BEFORE=sha256(/home/mak/flujo/data/rd_datos.db)
pytest -q --disable-warnings \
  tests/test_rd_database.py tests/test_rd_datos.py \
  tests/test_rd_db_logos.py tests/test_privacy.py
exit 0; 62 tests passed
AFTER=sha256(/home/mak/flujo/data/rd_datos.db)
BEFORE = AFTER = 70feaf43b5269b6c0341d1ba3debdac60e40fb902cc4bedb41254fdc84d1f703
SELECT COUNT(*) FROM registros_testeo = 0
```

The test-created SQLite files were temporary. The active privacy store stayed
empty and byte-identical. No runtime route or database merge was performed.

## Result

The RD catalog projections, privacy-first ingest validators, logo lookup and
privacy scanner are green in a bounded fixture-only execution. This does not
authorize ingesting the historical `Testeo 2025` candidate into the live
privacy store.

## Rollback and risk

No persistent file was changed by the test group. There is no rollback action
needed; temporary fixtures were owned by pytest. Keep the live field candidate
gated by date/required-field/privacy review and explicit authority.

## Next concrete action

Promote one additional bounded gate around the hub command allow-list only if
its subprocess calls remain limited to the version/invalid-command fixtures;
do not exercise command, automation, provider or live mutator routes.
