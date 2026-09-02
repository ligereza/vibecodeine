# Phase 265 — local ISKVW/Research fixture gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Scope

Validate local ISKVW, Research and Curatoria projections without external
effects:

- `tests/test_campo_filtro.py`
- `tests/test_cartografia_filtros.py`
- `tests/test_debate_modelos.py`
- `tests/test_entregar_micelio.py`
- `tests/test_extraccion_db.py`
- `tests/test_informe_plantilla.py`
- `tests/test_intake.py`
- `tests/test_iskvw_editor_contract.py`
- `tests/test_latido.py`
- `tests/test_mak_benchmark.py`
- `tests/test_mak_research_watchdog.py`

Fixtures use temporary roots; latido's URL opener is faked; micelio delivery
returns before Git; the watchdog is source-only. The destructive cron-nocturno
test was intentionally excluded even though it targets temporary files.

## Validation

```text
pytest -q --disable-warnings \
  tests/test_campo_filtro.py tests/test_cartografia_filtros.py \
  tests/test_debate_modelos.py tests/test_entregar_micelio.py \
  tests/test_extraccion_db.py tests/test_informe_plantilla.py \
  tests/test_intake.py tests/test_iskvw_editor_contract.py \
  tests/test_latido.py tests/test_mak_benchmark.py \
  tests/test_mak_research_watchdog.py
exit 0; 105 tests passed
```

## Result

The local ISKVW/Research fixture slice is green. No live URL, Git operation,
watchdog, worker, database or provider was used.

## Risk and rollback

No persistent state changed; no rollback is needed. The excluded destructive
cron test, live provider/worker paths and external integrations remain gated.

## Next concrete action

Continue with remaining pure fixture candidates, then re-run the residual
static count and update the objective matrix.
