# Phase 261 — organs and GPU inventory fixture gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Scope

Validate the local organ inventory and GPU/activity seam:

- `tests/test_mak_organos_visibles.py`
- `tests/test_mak_gpu_activity.py`

The organ test substitutes the Linux worker module with a stub. The activity
tests redirect state and lock files to temporary paths. Tests that create
threads or import the visual worker were intentionally left gated.

## Validation

```text
pytest -q --disable-warnings \
  tests/test_mak_organos_visibles.py tests/test_mak_gpu_activity.py
exit 0; 5 tests passed
```

## Result

The organ inventory and portable activity/GPU seam are green without starting
workers, probing hardware or writing active state.

## Risk and rollback

All writes were temporary and the worker was stubbed. No persistent state,
service, GPU process or external integration changed. No rollback is needed.

## Next concrete action

Refresh the objective matrix and residual inventory with the fixture gates now
closed; preserve the thread/worker/provider tests as separately gated work.
