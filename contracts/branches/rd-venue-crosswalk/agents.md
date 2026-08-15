# Scoped branch contract

Branch: `rd/venue-crosswalk`
Owner: `LUNA-504`
Base: `main` at `2431b26`
Domain: `rd`
Consumer: `src/flujo/rd/entity_crosswalk.py`

## Objective

Make the read-only RD/portfolio crosswalk preserve and validate its declared
source database list. The adapter must expose provenance without opening,
merging, rebuilding or writing either SQLite database.

## Allowed write set

- `src/flujo/rd/entity_crosswalk.py`
- `tests/test_entity_crosswalk.py`
- `contracts/branches/rd-venue-crosswalk/agents.md`
- `context/handoffs/rd-venue-crosswalk.md`

## Read-only inputs

- `data/rd_fuentes/candidates/rd_portfolio_entity_crosswalk.json`
- `data/rd.db`
- `data/rd_datos.db`
- `data/venues/*.json`
- `schemas/venue.schema.json`

The SQLite files are evidence only. The branch may hash or inspect them but
must not connect in write mode or call `build_rd_db`.

## Forbidden

Do not physically merge databases, insert identity rows, infer venue joins
from names, publish technical records, call providers, start services, add
dependencies, edit WIN or touch the README.

## Validation gate

```text
python -m py_compile src/flujo/rd/entity_crosswalk.py tests/test_entity_crosswalk.py
python -m pytest -q tests/test_entity_crosswalk.py tests/test_rd_database.py tests/test_venue.py
python -c 'from flujo.rd.entity_crosswalk import load_crosswalk; print(load_crosswalk().source_databases)'
git diff --check
```

The gate must prove source database hashes are unchanged.

## Rollback

Revert the branch commit or delete the short-lived branch. Keep every source
database, crosswalk candidate and historical evidence file.
