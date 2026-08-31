# Phase 259 — local Research state/queue fixture gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Scope

Validate local Research state and routing contracts without workers or
providers:

- `tests/test_mak_process_guard.py`
- `tests/test_mak_research_router.py`
- `tests/test_mak_pausa.py`
- `tests/test_mak_hub_salud.py`
- `tests/test_mak_interfaz_config.py`

The group uses temporary checkpoints/configuration and monkeypatched LLM,
search and provider-health functions. It does not launch a worker, start a
service, contact a provider or use the live queue.

## Validation

```text
pytest -q --disable-warnings \
  tests/test_mak_process_guard.py tests/test_mak_research_router.py \
  tests/test_mak_pausa.py tests/test_mak_hub_salud.py \
  tests/test_mak_interfaz_config.py
exit 0; 58 tests passed
```

## Result

Checkpoint persistence/resume, pause behavior, research routing, simulated
provider-health state, process-guard discovery and interface configuration
contracts are green in isolation.

## Risk and rollback

All writes were temporary or monkeypatched. No live queue, provider, service,
database, cron or external system changed. No rollback is needed.

## Next concrete action

Promote the next local Curatoria/platform fixture group, keeping watchdogs,
workers, issue creation and external integrations disabled.
