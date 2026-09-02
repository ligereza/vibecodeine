# Phase 124 - cleanup quarantine for Finder metadata

## Candidate gate

The bounded cleanup scan found 92 files named `.DS_Store` under
`/home/mak/curatoria_inbox`, totaling about 1.2 MB. A code-reference scan
found no references to `.DS_Store` in the scoped MAK/curatoria surfaces. These
are Finder metadata files, not RD assets, source, database, ledger, recovery,
credential or historical evidence.

## Action

Moved exactly those 92 files, preserving their paths relative to
`/home/mak/curatoria_inbox`, to the reversible quarantine:

`/home/mak/flujo/context/quarantine/phase124_ds_store/`

No `.bak`, `~`, lock, rollback, corpus, output, database, WIN or source file
was moved.

## Foreground validation

The exact preflight count was 92. The move command exited 0 and reported:

```text
before=92 source_after=0 quarantined=92
```

The source tree now has zero `.DS_Store` files and the quarantine has 92. A
rollback, if needed, is the inverse path-preserving move from
`context/quarantine/phase124_ds_store` back to `/home/mak/curatoria_inbox`.

## Decision

`JUNK_CONFIRMED`: yes for these exact Finder metadata files. This is the first
path-level cleanup after the ownership closure. No broader pattern is inferred
from it; `.bak`, `~`, zero-byte locks, rollback trees and generated artifacts
remain unresolved/protected.

## Next action

Run a focused post-cleanup read-only health/entrypoint check and refresh the
objective/cleanup matrix. Do not widen the deletion scope without a separate
consumer and recovery gate.
