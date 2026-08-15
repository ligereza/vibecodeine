# Phase 474 — physical versus Git architecture

Status: reviewed on 2026-08-15, `main` promoted through `b0db4e3`.

## Decision

MAK uses one permanent Git trunk: `main`. Domain names are ownership and
consumer boundaries, not permanent branches. Integrated slices are preserved
as `archive/integrated/*` tags. The only remaining branch is
`mak/ownership`, retained as a local evidence lane because its worktree still
contains unreviewed reports and context changes.

## Current physical owners

| Concern | Current owner | Consumer boundary |
|---|---|---|
| FLUJO runtime and CLI | `src/flujo/` | Python entrypoints and hub |
| Human web surfaces | `web/` | Main, RD and Portfolio panels |
| Research and curation | `cultura/` and `projects/` | MAK research/curatoria consumers |
| RD sources and projections | `data/`, `src/flujo/rd/`, `svg/eventos_rd/` | quote, plano, rider, venue and reports |
| Reusable deterministic tools | `tools/` | generators, probes, adapters and indexes |
| Documentation and evidence | `docs/` and `context/` | operating docs versus audit continuity |
| Portfolio/ISKVW material | `iskvw/`, `assets/`, `web/src/data/` | authorial catalog and public shell |
| Historical Windows source | `/home/mak/WIN` | read-only physical evidence, never runtime |

## Target vocabulary without a mass move

The proposed names `apps/`, `domains/`, `shared/`, `data/canonical`,
`data/review` and `data/evidence` remain architectural vocabulary, not empty
folders to create for appearance. Current consumers are already bounded by
their existing owners. A future move is allowed only when an import map,
consumer test, rollback path and owner are attached to the slice. Until then:

- `src/flujo/` is the application/runtime layer;
- `cultura/`, `src/flujo/rd/` and portfolio paths are domain layers;
- `data/` and typed adapters are the shared data boundary;
- `tools/` is the tool layer;
- `docs/` and `context/` are documentation/evidence layers.

This keeps the conceptual architecture clear without duplicating files or
breaking relative imports, frontend aliases, generated artifacts or database
paths. `WIN` remains outside this Git projection and is not copied into it.

## Git evidence

Permanent trunk: `main` at `b0db4e3`.

Integrated history is recoverable through tags including:

- `archive/integrated/house-restructure-9bbec3c`
- `archive/integrated/portfolio-web-792d9a7`
- `archive/integrated/mak-ownership-9b398f1`
- `archive/integrated/rd-runtime-032822b`
- `archive/integrated/mak-continuity-f3ecfed`
- `archive/integrated/mak-handoff-e483ac5`

No source database, historical evidence or WIN material was deleted by this
phase. The obsolete sync mutator was removed from the active runtime and its
absence is guarded by tests; the historical copy remains in quarantine/context
evidence.

## Gate for the next physical move

Do not create `apps/`, `domains/` or `shared/` as a cosmetic migration. The
next valid slice must name one real consumer, move or adapt one bounded family,
pass static and runtime checks, and record rollback before changing paths.
