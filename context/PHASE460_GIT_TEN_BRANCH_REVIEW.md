# Phase 460 — Review of the ten historical Git branches (historical snapshot)

> This file is provenance, not an active branch instruction. Its codex-prefixed
> names and old branch counts are historical. The current copy/update state is
> in LAST_HANDOFF.md and the current branch-copy manifest.

## Baseline

The only current integration baseline is:

```text
main = 032822b61f3d7cb84c7b52ae1ac6330b2a1f7fcb
```

The ten local branches that existed before the new topic refs were reviewed
against that baseline using commit ancestry, tip-to-tip path differences and
recent commit subjects. Git history was used only for branch orientation; the
physical MAK/WIN surfaces remain the authority for runtime integration.

## Disposition of all ten branches

| Historical branch | Observed role | Review result | New operational home |
|---|---|---|---|
| `main` | current transport baseline | keep as the only permanent baseline | `main` |
| `mak` | broad MAK/research reconciliation line; 1 ahead / 18 behind | historical source line, not current MAK truth | `codex/mak/ownership` plus bounded topic branches |
| `ddbase` | MAK mirror/conductor predecessor; 0 ahead / 18 behind | preserve as transport history | `codex/mak/ownership` |
| `codex/nudo-rd-evidence` | RD evidence checkpoint built over `ddbase`; 2 ahead / 18 behind | preserve as evidence history | `codex/rd/field-review` |
| `codex/mak-local-authority-reconciliation-20260813` | MAK archive/runtime handoff; 4 ahead / 18 behind | preserve as historical reconciliation | `codex/mak/ownership` |
| `codex/mak-linux-only` | Linux runtime/CI boundary; 10 ahead / 5 behind | preserve; do not use as permanent platform branch | `codex/mak/ownership` or the smallest active slice |
| `codex/mak-web-restructure-20260813` | broad web publication/restructure history; 6 ahead / 23 behind | preserve; split by consumer | `codex/portfolio/web`, `codex/rd/assets` |
| `codex/mak-web-restructure-20260814` | dependency/CI follow-up; 8 ahead / 5 behind | preserve as validation history | relevant short-lived topic branch |
| `iskvw` | wide merged portfolio/product branch; 7 ahead / 29 behind | not a clean portfolio-only base; preserve | `codex/portfolio/web` |
| `rd` | wide merged RD/product branch; 6 ahead / 29 behind | not a clean RD-only base; preserve | `codex/rd/field-review`, `codex/rd/runtime`, `codex/rd/assets` |

`iskvw` and `rd` each differ from `main` across 378 paths, including shared
MAK, culture, docs, tests and tools. They cannot safely become permanent
department branches without reintroducing cross-domain drift.

## Resulting operating topology

```text
main
  ├── codex/mak/ownership
  ├── codex/rd/field-review
  ├── codex/rd/runtime
  ├── codex/rd/assets
  ├── codex/portfolio/web
  ├── codex/flujo/event-bridge
  ├── codex/tools/consolidation
  └── codex/cleanup/confirmed-junk
```

Each new branch was created from the same `main` commit. The historical ten
branches remain available as provenance and rollback references, but they are
not merge targets for new work. No branch was deleted, renamed, rebased,
merged or pushed.

## Visible checkpoint

The active worktree is `codex/mak/ownership`. The pre-existing dirty scope is
carried there unchanged. This review and the branch-system report are the
first deliberately bounded documentation write set; the 794 other status
entries remain unstaged and are not included in this checkpoint.

## Next action

Create the first focused commit containing only the branch-system checkpoint,
then partition the remaining dirty worktree by consumer. Do not stage the 794
entries as one merge and do not revive any historical branch as a permanent
development line.
