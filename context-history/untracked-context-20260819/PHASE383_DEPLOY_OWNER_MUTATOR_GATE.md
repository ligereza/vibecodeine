# Phase 383 — deploy owner and sync mutator gate

Date: 2026-08-15 (America/Santiago)

## Scope

Read-only audit began at `/home/mak/*` and then narrowed to
`/home/mak/flujo-deploy` and `/home/mak/bin/mak_sync_safe.py`. No Git command,
network fetch, deploy, copy, backup, manifest write or service action ran.

## Findings

| Surface | Evidence | Disposition |
|---|---|---|
| `/home/mak/flujo-deploy` | Separate deploy worktree/artifact with CI, visual assets, `cultura/*` projections and Windows launcher material | Preserve as external deploy owner; do not merge whole tree into `flujo` |
| `/home/mak/bin/mak_sync_safe.py` | Active local mutator targets `/home/mak/flujo-deploy`, runtime projections, rollback and manifest paths | Preserve but keep gated; never execute as an inventory shortcut |
| `/home/mak/WIN/flujo/tools/mak_ops/sync_mak_safe.py` | Historical richer implementation; SHA differs from active `/home/mak/bin/mak_sync_safe.py` | Preserve as provenance; do not replace active file by name similarity |
| `flujo-deploy` direct sync references | No direct `mak_sync_safe`/`sync_mak_safe` reference found in bounded deploy/bin/mak_ops scan | No active consumer proof for promotion |

## Foreground validation

```text
AST structure of both active and WIN sync files: parse succeeded
/home/mak/bin/mak_sync_safe.py: python3 -m py_compile exit=0
active scheduler entries: 0
no matching MAK sync process observed
```

The active file exposes Git, copy, backup and manifest operations through its
main path. Those operations were not called. The deploy worktree is not an
active FLUJO application consumer and remains outside the migration merge.

Disposition: `DEPLOY_OWNER_PRESERVED; MUTATOR_GATED; NO_MERGE`.
