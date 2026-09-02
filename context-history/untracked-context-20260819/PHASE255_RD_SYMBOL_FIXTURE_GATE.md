# Phase 255 — RD symbol catalogue and tracer fixture gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Scope

Validate the RD symbol slice through its real Python functions while routing
all writes to pytest temporary roots:

- `tests/test_plano_simbolos_catalogo.py`
- `tests/test_plano_simbolos_alta.py`
- `tests/test_plano_trazador.py`

The group covers SVG catalogue loading, user-facing symbol registration,
sanitization, image tracing and plan rendering. It does not start the hub or
call a live POST route.

## Validation

```text
pytest -q --disable-warnings \
  tests/test_plano_simbolos_catalogo.py \
  tests/test_plano_simbolos_alta.py \
  tests/test_plano_trazador.py
exit 0; 28 tests passed
```

## Result

The symbol consumer slice is green in isolated fixtures: an operator can
declare or save a symbol, SVG sanitization holds, image tracing produces the
catalogue-compatible currentColor form, and the plan receives the new symbol.
The active catalogue and generated products were not changed.

## Risk and rollback

All writes were under temporary roots owned by pytest. No active data, source,
database, service or route changed; no rollback is needed. The live symbol
POST remains classified as a mutator and stays deferred.

## Next concrete action

Promote the render/export fixture group next, still using temporary outputs and
no browser, service, provider or external delivery path.
