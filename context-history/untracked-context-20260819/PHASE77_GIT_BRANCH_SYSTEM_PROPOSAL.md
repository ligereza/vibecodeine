# Phase 77 — Git branch system proposal

## Principles

- `main` is the only stable integration line and must always pass the local
  FLUJO health/doctor/AST gates.
- Branches represent live domains or bounded integration slices, not copies of
  MAK folders, WIN generations or duplicate documents.
- `/home/mak/WIN` is historical evidence and never receives a branch.
- A branch must have one owner, one write set and one foreground validation
  contract. No branch may contain broad cleanup mixed with feature work.
- Use the `codex/` prefix for traceability and short-lived branches.

## Proposed branches

| Branch | Scope | Write set | Gate |
|---|---|---|---|
| `main` | stable MAK/FLUJO baseline | integrated code and approved docs | health, doctor, AST, focused runtime |
| `codex/integration/rd-data` | approved RD field-data contract | `rd_datos` reader/ingestion and evidence manifest | schema/read/write/rollback |
| `codex/integration/rd-runtime` | RD routes and mutators | hub/rd modules and bounded tests | fixture then authorized foreground run |
| `codex/integration/flujo-automation` | EVENTO issue/URL processing adapter | automation adapter/config/tests | provider fixture and issue contract |
| `codex/integration/rd-assets` | RD path contract and asset manifests | route resolver, asset manifests, selected consumers | no-copy path fixture and output check |
| `codex/architecture/mak-ownership` | canonical folder/projection ownership | manifests, launcher references, bounded adapters | import/launcher parity |
| `codex/consolidation/tools` | equivalent tools by consumer | one selected source/projection or adapter per slice | AST/import/contract/rollback |
| `codex/cleanup/confirmed-junk` | only approved cleanup | exact path manifest and quarantine ledger | pre/post health and reversible quarantine |
| `codex/release/verification` | final audit and release notes | objective matrix, checks and handoff | all required gates green |

## Merge order

`rd-data` → `rd-runtime` → `flujo-automation` → `rd-assets` →
`mak-ownership` → `tools` → `confirmed-junk` → `verification` → `main`.

If a slice is blocked by external authority, its branch remains explicit and
does not block unrelated local slices. Do not merge a branch merely because a
report exists; its consumer and foreground validation must pass.

## Naming and handoff

Commit messages should identify the slice and gate, for example
`rd: verify field-data read contract` or `mak: consolidate ledger projection`.
Every branch handoff records source/target paths, write set, commands, exit
codes, changed files, rollback and next action in `LAST_HANDOFF.md`.

This is a proposal only. No branch, commit, merge, reset, checkout or push was
performed.
