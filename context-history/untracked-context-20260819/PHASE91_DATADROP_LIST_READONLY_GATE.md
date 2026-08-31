# Phase 91 — datadrop list read-only gate

## Finding

`flujo datadrop list` called `datadrops_dir()` with implicit directory
creation. A read-only list command could therefore create the workspace and
`datadrops/` tree on an otherwise empty deployment.

## Change

- `workspace_root(create=True)` now supports an explicit non-creating path
  lookup with `create=False`.
- `datadrops_dir(create=True)` preserves writer behavior and supports
  `create=False` for readers.
- `flujo datadrop list` uses `create=False` and handles an absent directory
  without writing it.

## Foreground validation

- `FLUJO_WORKSPACE_ROOT=/tmp/phase91-unique flujo datadrop list` -> exit `0`,
  truthful empty warning, and the temporary root did not exist afterward.
- Real `/home/mak/venvs/flujo/bin/flujo datadrop list` -> exit `0`, listed
  existing datadrops without changing their contents.
- `py_compile paths.py cli.py` -> exit `0`.
- Direct path fixture confirmed `workspace_root(create=False)` and
  `datadrops_dir(create=False)` do not create missing directories.

## Decision

Datadrop readers are now `READ_ONLY`; ingestion, scan and prepare retain
explicit writer paths. No real datadrop, job, database, asset, provider or
service changed.

## Next

Continue the same audit for remaining list/status/read commands and preserve
all mutators behind explicit commands and rollback fixtures.
