# Phase 90 — flyer index reader/writer separation

## Finding

`flujo flyer-list` was presented as a reader but `list_flyers()` called
`init_db()`, which could create the SQLite database/schema/indexes as a side
effect. `find_duplicates()` had the same issue.

## Change

`src/flujo/index/db.py` now separates responsibilities:

- `list_flyers()` and `find_duplicates()` use an existing SQLite connection in
  `mode=ro`; if the index is absent they return an empty result.
- `rebuild_index()` and explicit `init_db()` retain the write path and create
  the parent/database schema when requested.
- `db_path()` itself no longer creates directories.

## Foreground validation

- Existing `/home/mak/flujo/data/flujo.db` before/after `flujo flyer-list`:
  20,480 bytes and mtime `1782809697` in both observations.
- `/home/mak/venvs/flujo/bin/flujo flyer-list --limit 3` -> exit `0`.
- `py_compile src/flujo/index/db.py` -> exit `0`.
- Temporary fixture with two manifests: explicit `rebuild_index()` indexed 2;
  read-only `list_flyers()` returned 2 and `find_duplicates()` returned 1;
  database mtime was unchanged across both readers.

## Decision

The index slice is `READERS_READONLY / WRITER_EXPLICIT`. No production data,
job, asset, provider, Git or service mutation occurred.

## Rollback

Restore the prior `db.py` implementation from the recorded source patch. The
database schema and existing rows were not changed by this gate.

## Next

Continue the remaining local mutator/read contract audit and tool ownership
consolidation. Keep any command that creates/rebuilds data explicitly labeled
as a writer.
