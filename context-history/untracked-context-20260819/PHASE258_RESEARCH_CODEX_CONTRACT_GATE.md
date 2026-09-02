# Phase 258 — Research/Codex contract gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Scope

Run source/configuration-only Research/Codex contracts:

- `tests/test_formatos_mak.py`
- `tests/test_codex_no_es_sandbox.py`
- `tests/test_codex_cadena.py`
- `tests/test_refutar_orden.py`
- `tests/test_formato_ensayo.py`
- `tests/test_fuentes.py`
- `tests/test_mapa_completo.py`
- `tests/test_mak_sin_gptmini.py`

These verify model/roster boundaries, prompt contracts, source gates and MAPA
coverage. They do not call providers or network-backed research.

## Validation

```text
pytest -q --disable-warnings \
  tests/test_formatos_mak.py tests/test_codex_no_es_sandbox.py \
  tests/test_codex_cadena.py tests/test_refutar_orden.py \
  tests/test_formato_ensayo.py tests/test_fuentes.py \
  tests/test_mapa_completo.py tests/test_mak_sin_gptmini.py
exit 0; 81 tests passed
```

## Result

The read-only Research/Codex contract slice is green. Provider rosters remain
configuration evidence; no provider was contacted and no external state was
changed.

## Risk and rollback

No persistent file, database, service or provider state changed. No rollback is
needed. Provider-backed research and workers remain gated.

## Next concrete action

Promote one bounded local research-state/queue fixture group, keeping worker
threads and provider/network calls disabled.
