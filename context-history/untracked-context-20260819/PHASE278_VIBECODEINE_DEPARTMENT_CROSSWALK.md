# Phase 278 — vibecodeine department crosswalk

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## `mak_plataforma`

```text
snapshot files: 49
active files:   61
common paths:   44
identical:      16
divergent:      28 (23 Python, all parse on both sides)
snapshot-only:  5
active-only:    17
```

Snapshot-only material is doctrine/history (`RELEVO_MAK.md` and four doctrine
documents). Active-only material includes current activity, benchmark,
provider, GPU, ledger, routing, review, batching, rescue and XIO-evidence
surfaces. The active department is therefore not missing a snapshot tool by
filename; it has evolved beyond it. The paused `crontab.mak` and service files
remain contracts/evidence, not permission to start workers.

## `mak_research`

```text
snapshot files: 41
active files:   41
common paths:   40
identical:      20
divergent:      20 (16 Python, all parse on both sides)
snapshot-only:  1 (`PLAN_VSCODE.md`)
active-only:    1 (`cola.service`)
```

This family is a maintained projection with controlled evolution, not a
candidate for snapshot replacement. Its current consumers and tests point to
the active `flujo/cultura/mak_research` owner; historical worker/watchdog and
service variants are gated.

## Decision

No file from `vibecodeine/cultura/mak_plataforma` or
`vibecodeine/cultura/mak_research` was promoted, copied, moved or deleted.
The active tree has more current consumers and contracts, while the snapshot
still has historical doctrine and divergent behavior that must remain
available for provenance. The correct state is canonical active departments
plus preserved historical snapshot, not an automatic merge.

No service, worker, cron, provider, XIO path, database, external system, WIN
content or Git state changed.

## Next concrete action

Finish the snapshot gate with a bounded `vibecodeine/data` and generated-output
crosswalk, distinguishing configuration/catalog from protected products. Do
not compare or remove full media trees; use manifests and consumer paths.
