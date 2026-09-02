# Phase 366 — Codex projection/consumer gate

Date: 2026-08-15 (America/Santiago)

## Scope

Audited the declared Codex mirror set without traversing caches or data:
`agente_libre.py`, `interfaz_codex.py` and the service unit. The root
`agente_libre.py` is an intentional compatibility wrapper around the
canonical implementation; `interfaz_codex.py` is an exact paired projection.

## Results

```text
CODEX_CANONICAL_IMPORTS=PASS
IMPORT_RC=0
PYCOMPILE_RC=0
UNIT_VERIFY_RC=0
```

The active consumer references the canonical Codex path through the declared
deployment manifest. No server, generated job, provider, subprocess worker or
external call was started.

## Disposition

`CODEX_OWNER_PROJECTION_VERIFIED; WRAPPER_INTENTIONAL`

No merge or deletion is justified: the wrapper and the exact projection have
different roles, and the service entrypoint remains explicit.

## Rollback and boundary

No source, job ledger, generated piece, database, service state, Git, Docker or
WIN evidence changed. No rollback is required. POST/job execution remains a
separate live-mutation gate.
