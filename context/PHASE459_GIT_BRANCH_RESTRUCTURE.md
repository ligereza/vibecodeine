# Phase 459 — Git branch system restructuring (historical snapshot)

> This file records an earlier branch experiment. It is not the current
> topology. Current state is maintained in LAST_HANDOFF.md: one main branch,
> one archive tag, and explicitly named source copies created only after their
> exact tip commits are verified.

## Decision

The repository now uses one clean baseline ref, `main`, and short-lived topic
branches named by area and bounded slice. Existing historical branches were
not deleted, rebased, merged or renamed.

```text
main @ 032822b
  ├── codex/rd/field-review
  ├── codex/rd/runtime
  ├── codex/rd/assets
  ├── codex/flujo/event-bridge
  ├── codex/portfolio/web
  ├── codex/mak/ownership       <- active worktree
  ├── codex/tools/consolidation
  └── codex/cleanup/confirmed-junk
```

All eight new local topic refs point to the exact same baseline commit:
`032822b61f3d7cb84c7b52ae1ac6330b2a1f7fcb`.

No permanent `develop`, `staging` or environment branch was created. A
`release/vX.Y` branch remains optional and will only be created for a real
release hardening window.

## Comparison of existing refs

The comparison used commit ancestry and tip-to-tip path differences against
`main`, not the dirty worktree:

| Existing ref family | Result against main | Disposition |
|---|---:|---|
| `mak`, `rd`, `iskvw` | divergent historical lines; 1/6/7 local commits ahead and 18/29/29 behind | preserve as historical refs; do not use as new integration bases |
| `ddbase` | 0 commits ahead, 18 behind; content diverges through old merge context | preserve as mirror/history |
| `codex/mak-linux-only` | 10 ahead, 5 behind; 170 tip-difference paths | preserve; superseded as active base by new `codex/mak/ownership` |
| `codex/mak-local-authority-reconciliation-20260813` | 4 ahead, 18 behind; 230 paths | preserve as historical work |
| `codex/mak-web-restructure-20260813` | 6 ahead, 23 behind; 294 paths | preserve as historical work |
| `codex/mak-web-restructure-20260814` | 8 ahead, 5 behind; 148 paths | preserve as historical work |
| `codex/nudo-rd-evidence` | 2 ahead, 18 behind; 207 paths | preserve as historical work |
| `origin/*` refs | remote tracking evidence only | no fetch, push, delete or rewrite performed |

The old names mix machine identity, department identity, deployment snapshots
and historical agent work. They are therefore not safe as permanent current
development lanes. The physical MAK/WIN state remains the authority for
integration decisions.

## Worktree boundary

Before restructuring, `/home/mak/flujo` was on `main` with a dirty worktree.
The branch switch to `codex/mak/ownership` occurred at the same commit and
carried the worktree unchanged:

```text
active branch: codex/mak/ownership
modified/untracked status entries: 793
baseline ref: main = 032822b61f3d7cb84c7b52ae1ac6330b2a1f7fcb
```

Those changes were not staged, committed, stashed, reset or reassigned by
content. They now have an explicit active topic branch while `main` remains a
clean reference. The broad status is intentionally still open; it must be
split into consumer-backed commits before any merge or push.

## Operating rule from this point

- Work only on one bounded topic branch at a time.
- Each branch gets one consumer-backed write set and one foreground gate.
- Merge directly to `main` after validation; never merge topic branches into
  one another.
- Delete a topic ref only after its changes are merged and its commit is
  retained in history; do not delete the old historical refs during this
  cleanup.
- Keep `WIN`, databases, credentials and bulk media outside ordinary branch
  write sets; version code, schemas, manifests and evidence references.
- The active `codex/mak/ownership` worktree must first be partitioned into
  reviewable slices before its first commit.

## Validation

```text
git branch <new-name> main                 -> exit 0 for all 8 refs
git switch codex/mak/ownership              -> exit 0
git rev-parse each new ref                  -> all equal main
git status --short --branch                 -> active branch and 793 entries retained
```

No remote state changed. No branch was merged, deleted, rebased, reset or
pushed.

## Next action

Partition the 793 uncommitted entries on `codex/mak/ownership` into the first
consumer-backed slice, beginning with the current handoff/context evidence and
the MAK ownership manifests. Stage nothing until the write set is explicit;
then create the first focused commit and validate it before considering a
merge to `main`.
