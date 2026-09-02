# Phase 260 — Curatoria/platform fixture gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Scope

Validate local Curatoria/platform consumers with fakes and temporary state:

- `tests/test_curatoria_watchdog_panel.py`
- `tests/test_vigia_opportunity_queue.py`
- `tests/test_revisor_gates.py`
- `tests/test_metricas_capataz.py`
- `tests/test_material_ocurrencias.py`
- `tests/test_energia_log.py`
- `tests/test_mak_tandas_surface.py`

The suite covers watchdog decision logic, opportunity ledger, review gates,
metrics, queue classification, GPU-energy parsing and MAK batch surfaces. Its
external calls are mocked; no watchdog, worker, GitHub command, GPU probe or
service was launched.

## Validation

```text
pytest -q --disable-warnings \
  tests/test_curatoria_watchdog_panel.py \
  tests/test_vigia_opportunity_queue.py tests/test_revisor_gates.py \
  tests/test_metricas_capataz.py tests/test_material_ocurrencias.py \
  tests/test_energia_log.py tests/test_mak_tandas_surface.py
exit 0; 71 tests passed
```

## Result

The local Curatoria/platform fixture slice is green. Queue/ledger writes were
temporary, subprocess/GitHub/GPU calls were faked, and the active runtime and
external systems were untouched.

## Risk and rollback

No persistent state changed; no rollback is needed. Real issue creation,
watchdog execution, worker dispatch, GitHub operations and GPU probes remain
gated.

## Next concrete action

Run the remaining static/local platform projections that do not invoke
workers, issue providers or external integrations; then refresh the objective
matrix before considering any authorized live gate.
