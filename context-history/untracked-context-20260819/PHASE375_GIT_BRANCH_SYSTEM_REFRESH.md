# Phase 375 — Git branch system refresh

Date: 2026-08-15 (America/Santiago)

This is a historical proposal superseded in strategy by
`context/PHASE409_GIT_STRATEGY_RESEARCH.md`. No Git command, branch, commit, merge, reset,
checkout or push was performed.

## Branches and write sets

| Branch | Purpose | Exclusive write set | Required gate |
|---|---|---|---|
| `main` | stable MAK baseline | approved integrated source/docs only | health, doctor, AST, focused runtime |
| `codex/rd/field-review` | resolve RD candidate decision | review packet, mapping manifest, `rd_datos` ingest code/tests only | human data/privacy/ingest authority |
| `codex/rd/runtime` | RD route/mutator integration | hub/RD route code and bounded rollback tests | fixture then one authorized foreground mutation |
| `codex/flujo/event-bridge` | EVENTO issue/URL automation | adapter/config/tests for paused bridge | provider/issue contract; no cron by default |
| `codex/rd/assets` | RD asset/index/render contracts | asset manifests, selected index/render consumers | read/fixture/export validation |
| `codex/portfolio/web` | public iskvw portfolio and web catalogue | `web/`, `tools/portfolio/`, `iskvw/`, portfolio tests/docs; no bulk media | typecheck/build and local catalogue fixture; no publish |
| `codex/mak/ownership` | final physical architecture | owner manifests, launchers and path references | parity/import/unit verification |
| `codex/tools/consolidation` | equivalent tools by consumer | one named tool family and inverse rollback | consumer proof and focused tests |
| `codex/cleanup/confirmed-junk` | approved reversible cleanup | exact path ledger/quarantine only | pre/post invariant and rollback proof |
| `codex/release/full-audit` | final 13-objective closeout | objective matrix, handoff, verification scripts | all required gates resolved or explicitly accepted |

## Merge order

`rd/field-review` → `rd/runtime` → `flujo/event-bridge` → `rd/assets` →
`portfolio/web` → `mak/ownership` → `tools/consolidation` → `cleanup/confirmed-junk` →
`release/full-audit` → `main`.

Blocked authority branches do not block unrelated local branches. A branch
cannot merge because its report exists; its consumer, write set and
foreground gate must pass.

## Current recommendation

Do not create branches retroactively for the current uncommitted work without
first reviewing the worktree and choosing a snapshot boundary. The next
safe Git action, if the user authorizes it, is to create only
`codex/mak/ownership` from the current baseline and carry the
Phase 361–374 owner/cleanup matrices as its documentation payload.

The portfolio branch is separate because `iskvw` is the public portfolio and
the only site by user decision. Its canonical catalogue is
`flujo/tools/portfolio/proyectos.json`; matching copies under `flujo-deploy`
and `vibecodeine` are projections, not independent owners. The existing
`/api/portafolio` read endpoint is already integrated; shared `hub.py` edits
must be isolated from the portfolio branch. `/home/mak/portfolio_media`
remains protected media storage and is referenced by manifests/paths rather
than copied into Git.

The strategy shape in this historical matrix is superseded: use one protected
`main`, short-lived `codex/<area>/<slice>` branches that merge directly to
`main`, and an optional temporary `release/vX.Y`. Do not maintain the listed
area branches as long-lived branches or merge them sequentially into each
other.
