# Phase 82 — installed CLI repo namespace gate

## Problem

The installed launcher `/home/mak/venvs/flujo/bin/flujo` could import the
`flujo` package but `flujo autonomia status` failed with
`ModuleNotFoundError: No module named 'cultura'`. The MAK repo-level namespace
`/home/mak/flujo/cultura` is intentionally outside `src/` and is used by the
autonomy consumer.

## Change

Added `_expose_repo_namespace()` to `src/flujo/cli.py`. At CLI import time it
derives the repo from the source path and adds it to `sys.path` only when the
repo-level `cultura` directory exists. This is an import-path adapter; it does
not copy, package, start or mutate the department.

## Foreground validation

- `/home/mak/venvs/flujo/bin/python -m py_compile src/flujo/cli.py` -> exit 0.
- `/home/mak/venvs/flujo/bin/flujo autonomia status` -> exit 0 and emitted
  `flujo-autonomy-status-v1` JSON. No provider or SSH executor was called.
- `/home/mak/venvs/flujo/bin/flujo knowledge list productoras` -> exit 0;
  three entities listed.

The autonomy payload reports pre-existing diagnostic blockers `repo_dirty` and
`extra_remote_branches`; this gate did not inspect or mutate Git. No jobs,
ledgers, databases, assets or services changed.

## Rollback

Remove the `_expose_repo_namespace` helper and its invocation from
`src/flujo/cli.py`. No other file is required for rollback.

## Next

Continue with another bounded local consumer. Keep autonomy `run`, SSH,
providers and Git operations outside foreground execution.
