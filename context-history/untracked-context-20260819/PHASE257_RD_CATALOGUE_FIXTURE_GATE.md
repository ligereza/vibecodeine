# Phase 257 — RD catalogue and proposal fixture gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Scope

Validate pure RD catalogue/proposal consumers with temporary candidate and
output files:

- `tests/test_gen_propuestas_rd.py`
- `tests/test_generar_catalogo_rd.py`
- `tests/test_formats_catalogo.py`
- `tests/test_comercial_multiformato.py`
- `tests/test_marca_sin_precio.py`

The group exercises catalog reconciliation, proposal drafts, multiformat
brief/quote packages and price-safety checks without external delivery or
provider calls.

## Validation

```text
pytest -q --disable-warnings \
  tests/test_gen_propuestas_rd.py tests/test_generar_catalogo_rd.py \
  tests/test_formats_catalogo.py tests/test_comercial_multiformato.py \
  tests/test_marca_sin_precio.py
exit 0; 50 tests passed
```

## Result

The catalogue/proposal fixture slice is green. All generated drafts and
manifests were temporary; active catalogue, products, databases and delivery
systems were not changed.

## Risk and rollback

No persistent state changed, so no rollback is needed. Real proposal delivery,
external storage, provider-backed generation and live mutation remain gated.

## Next concrete action

Promote the next read-only research/Codex fixture group, excluding provider
calls and network-backed execution.
