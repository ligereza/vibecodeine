# Phase 280 — external deploy surface gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Scope

Audited `/home/mak/flujo-deploy` and `/home/mak/bin/mak_sync_safe.py` from the
physical root. The deploy tree is a separate Git worktree/artifact surface,
not the human authoring checkout `/home/mak/flujo`.

## Evidence

```text
/home/mak/bin/mak_sync_safe.py AST parse: rc=0
installed crontab active non-comment entries: 0
```

The only operational references found are the paused `MAK-REPO-SYNC` manifest
and repair/history records. No active source/test consumer calls the deploy
script.

## Function and risk

`mak_sync_safe.py` is a deployment mutator. It:

- validates that `/home/mak/flujo-deploy` is a clean separate worktree;
- runs fetch/reset against `origin/main` inside that deploy worktree;
- hashes live department projections and copies drift to
  `/home/mak/rollback/mak-sync`;
- writes `/home/mak/plataforma/deploy_manifest.json` atomically;
- copies platform, research, codex and curatoria projections into runtime
  roots.

This is useful deployment infrastructure but it is not part of the active
FLUJO application migration. Running it would use Git/network and overwrite
runtime projections, so it remains explicitly gated.

## Disposition

Keep `/home/mak/flujo-deploy` as a separate external deploy owner and keep
`/home/mak/bin/mak_sync_safe.py` preserved but disabled. Do not merge it into
`flujo`, do not promote its workflows or installers, and do not treat it as
confirmed junk. The paused manifest is evidence of historical operation, not
authorization to re-enable it.

No deploy, fetch, reset, copy, backup, manifest write, service start, provider
call, WIN change or Git operation occurred.

## Rollback

No mutation occurred. The safe rollback is preservation of the current deploy
worktree and script at their original paths; no inverse filesystem operation
is needed.

## Next concrete action

Reconcile the final root-side review list (`model-config`, `searxng`, old
Blender/provider environments and loose narratives) against this owner map,
then produce the visual architecture closeout and Git-branch proposal update.
Keep all external/mutating surfaces gated until explicitly authorized.
