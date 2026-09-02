# Phase 322 — RD temporary write-set gate

Date: 2026-08-15 (America/Santiago)
Scope: static and temporary validation of the two remaining RD writer paths.

## Paths and boundaries

- CLI: `/home/mak/flujo/src/flujo/cli.py`
- Catalog builder: `/home/mak/flujo/src/flujo/rd/database.py`
- Privacy-first field ingest: `/home/mak/flujo/src/flujo/rd/datos.py`
- Protected catalog: `/home/mak/flujo/data/rd.db`
- Protected field store: `/home/mak/flujo/data/rd_datos.db`

No canonical database was used as a write target. The command used the
existing `/home/mak/venvs/flujo/bin/python`, `PYTHONDONTWRITEBYTECODE=1`, and
temporary paths created under a temporary directory that was removed after
the foreground assertions.

## Static gate

`cli.py`, `rd/database.py` and `rd/datos.py` all parsed successfully. Static
write sets are explicit:

- `build_rd_db()` unlinks/rebuilds its target database from canonical source
  files; safe only when its target is a deliberate snapshot or rollback path.
- `ingest_csv()` creates schema if needed and inserts validated rows into its
  selected field database; it scans all row values for PII first.
- Neither path is allowed to write the other database.

## Temporary foreground results

The temporary catalog command called `build_rd_db(temp/rd.db)` and returned:

```text
TEMP_BUILD=PASS tables=20 rows=7587 integrity=ok
```

The temporary privacy fixture contained one valid row, one malformed row and
one row with an email. `ingest_csv(..., policy="strict")` returned:

```text
TEMP_INGEST=PASS inserted=1 invalid=1 pii=1 persisted=1
```

The canonical database size/mtime/SHA tuple was captured before and after;
both `rd.db` and `rd_datos.db` returned unchanged:

```text
CANONICAL_DATABASES_UNCHANGED=PASS
```

## Disposition

`VERIFIED_TEMPORARY_WRITER_CONTRACT; LIVE_AUTHORITY_PENDING`.

The rebuild and field-ingest implementations work inside their declared
boundaries. This does not authorize real field-data ingestion, publication or
reconstruction of the catalog. `rd_datos.db` remains empty and separate; a
real CSV needs human date/required-field/privacy review and explicit ingest
authority. A future catalog rebuild needs a source snapshot and rollback
record even though the temporary rebuild passed.

## Changes and risks

- Source, canonical databases, data and outputs: unchanged.
- Providers, network, services, workers, cron, Git and WIN: untouched.
- Risk: `build_rd_db()` is destructive for its selected target and
  `ingest_csv()` is cumulative for its selected field store; never point the
  temporary gate at canonical paths.
- Rollback: no rollback needed; only temporary paths were written.

