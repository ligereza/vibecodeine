# Phase 135 - Git branch proposal refresh

This is a proposal only. No Git history, branch list, status, checkout, merge,
commit or push was inspected or changed.

## Rules

- `main` is the stable MAK/FLUJO line.
- Branches represent a bounded consumer slice, not a copy of a folder or WIN.
- Each branch has one owner, disjoint write set, foreground gate and rollback.
- WIN never receives a branch and never becomes a cleanup source.
- External gates remain visible in branch status; they do not become fake green
  through a report-only merge.

## Proposed branches

| Branch | Current scope | Write set | Gate |
|---|---|---|---|
| `main` | stable integrated MAK/FLUJO | approved merged surfaces | verify, health, typecheck, focused runtime |
| `codex/architecture/mak-ownership` | final folder/projection ownership | manifests, launcher references, path adapters | import/launcher/path parity |
| `codex/consolidation/tools` | equivalent pure tools by consumer | canonical modules and compatibility projections | AST/import/fixture/rollback |
| `codex/integration/rd-assets` | RD source/output/delivery manifests | asset manifests, route/index contracts, selected generators | isolated generation, index and output checks |
| `codex/integration/rd-data` | authorized field dataset | field reader/ingestion/evidence manifest | schema, provenance, read/write/rollback |
| `codex/integration/rd-runtime` | RD mutating routes | route adapters and bounded tests | disposable fixtures then authorized foreground run |
| `codex/integration/flujo-automation` | confirmed EVENTO -> issue -> URL chain | adapter/config/tests | local fixture then provider-backed contract |
| `codex/verification/dependency-gates` | pytest/qwen/web runtime closure | dependency manifests and verification docs | supported runtime and full tests |
| `codex/cleanup/confirmed-junk` | exact approved cleanup only | quarantine manifests and reversible moves | pre/post health and exact rollback |
| `codex/release/verification` | final 13-objective audit | objective matrix, handoff and release notes | every required gate proven |

## Merge order

`mak-ownership` -> `tools` -> `rd-assets` -> `rd-data` -> `rd-runtime` ->
`flujo-automation` -> `dependency-gates` -> `confirmed-junk` ->
`release/verification` -> `main`.

The current local work has evidence for the pure projection/tool and partial
RD asset slices. `rd-data`, provider-backed automation, production mutators,
full pytest, qwen-agent and the web production build remain gated by external
state or authority. The cleanup branch must contain only path-specific
quarantine records, never broad duplicate removal.

## Handoff contract

Every branch handoff must record exact source/target paths, write set, consumer,
commands, exit codes, changed files, rollback and next action in
`context/LAST_HANDOFF.md`. This proposal becomes actionable only after the
physical ownership matrix is closed and the user explicitly requests Git
operations.
