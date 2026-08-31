# Phase 318 — platform copilot contract gate

Date: 2026-08-15 (America/Santiago)
Scope: one pure platform duplicate family with real hub consumers.

## Paths and consumers

- Canonical implementation: `/home/mak/flujo/cultura/mak_plataforma/copilot.py`
- Root projection: `/home/mak/plataforma/copilot.py`
- Consumer hubs: `/home/mak/flujo/cultura/mak_plataforma/hub.py` and
  `/home/mak/plataforma/hub.py` import and call the module's copilot contracts.
- The module owns curatorial transformations and feedback contracts; it does
  not own provider calls or a persistent output writer.

## Foreground validation

Command:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/mak/flujo/cultura/mak_plataforma:/home/mak/plataforma python3 - <<'PY'
... AST, SHA-256, byte equality and feedback fixture ...
PY
```

Result: exit code 0. Both files parse, are 80,079 bytes and share SHA-256
`b194403d66cf3f0c4f46378fb8a9befbc5cff635c110964a66b596be7b9369f4`.
`dedupe_feedback()` and `feedback_index()` passed the pure fixture,
including the undo barrier and latest-link behavior. The gate printed
`provider_calls=False writer_calls=False`; no hub or service was started.

## Disposition

`PROTECT_EXACT_CONSUMER_BACKED_PROJECTION`.

The pair is intentionally synchronized and has active hub consumers. It is
not a deletion candidate. Consolidation can be considered later only after a
single import root is chosen and both launcher paths receive a focused import
test. Copying or rewriting the pair now would add risk without improving
functionality.

## Changes and risks

- Source/data changes: none.
- External providers, network, cron and services: not called.
- Risk: the full pytest suite remains unavailable in system Python (`pytest`
  module absent, recorded in Phase 317); direct AST/import/fixture coverage
  passed.
- Rollback: no rollback needed because no file changed.

