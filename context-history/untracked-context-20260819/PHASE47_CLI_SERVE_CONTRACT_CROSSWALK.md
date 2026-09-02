# Phase 47 — CLI serve contract crosswalk

Identity: LUNA principal
Status: RESOLVED_NO_SERVE_MISMATCH
Scope: resolve the open full-file `cli.py` difference by comparing only the
actual `serve` and `app` entrypoint contracts.

## Physical sources

- MAK: `/home/mak/flujo/src/flujo/cli.py`.
- WIN: `/home/mak/WIN/flujo/src/flujo/cli.py`.
- Full files differ, so whole-file replacement was not authorized.

## Bounded AST comparison

Foreground command (exit 0): parse both files with Python AST and compare
`FunctionDef` nodes named `serve` and `app_alias`, omitting source locations.

Observed:

- Both files contain `serve` and `app_alias`.
- `serve` AST: equal.
- `app_alias` AST: equal.
- Therefore options, defaults, mutating `--procesar-pendientes` flag,
  `--abrir/--no-abrir` behavior and dispatch to `web.hub.launch` are equal in
  the migrated entrypoint.
- Phase 44 help and Phase 45/46 real-process checks independently confirmed
  the MAK behavior.

## Decision

The open `cli.py` difference is not a `serve` migration mismatch. Keep MAK's
full-file variant and WIN as historical evidence; do not merge unrelated CLI
commands or packaging history. The `serve`/`app` entrypoint contract is
resolved with no source edit.

Residual CLI work, if later required, must name a specific non-serve command,
consumer and runtime mismatch. No Git inspection or mutation was performed.

