# Phase 286 — safe local surface gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Scope

Selected pure or `tmp_path`-isolated tests from the remaining static inventory:

```text
tests/test_analyze.py
tests/test_autofit.py
tests/test_brand.py
tests/test_coherence.py
tests/test_coherence_boundaries.py
tests/test_cotizaciones_base.py
tests/test_dashboard.py
tests/test_datadrop_scan.py
tests/test_debate_modelos.py
```

## Validation

```text
61 passed, PYTEST_RC=0
```

The image, dashboard, datadrop and project tests wrote only temporary fixtures
or redirected their roots with monkeypatches. No real RD media, catalog,
field database, service, provider, network, worker, cron, XIO, n8n or Git
state changed.

## Decision

Count this group as locally verified for the bounded MAK audit. The remaining
residual tests must continue to be selected individually because their static
surface includes subprocesses, external providers, workers, renderers,
schedulers or live mutation paths.

## Next concrete action

Refresh the objective audit and residual coverage ledger with Phases 284–286,
then inspect whether any unexecuted residual file has a provably temporary
write set. Do not widen execution authority by test filename alone.
