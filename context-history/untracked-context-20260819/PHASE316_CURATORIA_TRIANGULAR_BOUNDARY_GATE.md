# Phase 316 — curatoria triangular boundary gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Status: `EXACT_PAIR_NO_ACTIVE_CONSUMER_MUTATOR_GATED`

## Candidate

```text
canonical:  /home/mak/flujo/cultura/mak_curatoria/triangular.py
projection: /home/mak/curatoria/triangular.py
```

The pair is byte-identical and parses successfully. It is a legacy queue
builder: `main()` reads `~/curatoria/fichas/fichas.jsonl` and writes
`~/curatoria/triangulacion.jsonl`. That write contract is not a pure import and
was not executed.

## Consumer crosswalk

The active conductor's triangular branch imports
`tools.triangular_fichas`, not this `mak_curatoria.triangular` module. No exact
active import or launcher reference to this pair was found. The pair therefore
has no proven current consumer, although its input/output paths and historical
department role make it unsafe to call junk.

## Foreground validation

```text
SHA/cmp source and projection: exit 0; exact parity
AST parse both files: exit 0
pure posibles_headliners fixture on both imports: PASS
main() not executed because it writes triangulacion.jsonl
cron active entries: 0
matching processes: none
```

No file, ficha, JSONL, database, output, service, provider, WIN or Git state
changed.

## Decision

Classify as `PROTECTED_LEGACY_PROJECTION`: not a merge candidate and not
confirmed junk. Keep it until the owner of the replacement
`tools/triangular_fichas` explicitly covers the same queue contract and a
rollback/archive decision is recorded. This is a semantic consumer gap, not a
duplicate-file problem.

## Next action

Continue with the next bounded duplicate family in Research or platform state,
starting from its active consumer and write set. Prefer a pure reader or
projection; do not execute mutating queue builders, live providers or output
writers.
