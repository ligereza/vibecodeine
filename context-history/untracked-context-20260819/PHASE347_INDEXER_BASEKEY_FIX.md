# Phase 347 — asset indexer basekey fix

Date: 2026-08-15 (America/Santiago)

## Finding

The temporary asset fixture exposed a real duplicate/version grouping bug in
`/home/mak/flujo/src/flujo/index/indexer.py`: `_basekey()` removed `final`
from `creatina final.svg` but not from `creatina_final.svg`, because underscore
normalization occurred after the token-boundary regex. Exact hashes were found
correctly, but version queries could split the same piece.

## Change

Reordered the helper's existing normalization so `-`/`_` separators become
spaces before removing version/status tokens. No other index behavior changed.

## Validation

```text
INDEXER_BASEKEY_FIX=PASS
TEMP_INDEX_WRITES=True REAL_INDEX_UNCHANGED=True
PYCOMPILE_RC=0
```

The fixture confirmed `creatina_final.svg`, `creatina_v03.ai` and
`creatina copia.ai` all map to `creatina`; exact duplicate detection, cleanup
classification and search grouping passed. Only a temporary index was written.

## Impact and rollback

- Changed source: `/home/mak/flujo/src/flujo/index/indexer.py` only.
- This improves objective 9 duplicate classification without moving/deleting
  any asset. The real index was not rebuilt.
- Rollback: restore the prior `_basekey()` ordering if a consumer demonstrates
  an incompatible legacy grouping, then rerun the same fixture.
- No database, service, provider, Git or WIN operation occurred.

