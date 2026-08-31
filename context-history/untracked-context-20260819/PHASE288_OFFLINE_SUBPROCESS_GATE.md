# Phase 288 — offline subprocess fixture gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Selection

This group was selected after source inspection proved its boundaries:

```text
tests/test_iskvw_piel_medir.py
tests/test_adobe_panel.py
tests/test_auto_pending_flyers.py
```

The ISKVW measurement generator writes under pytest temporary storage and is
forced to a dead local port so it cannot use a live Research service. The
Adobe tests inspect files without installation. Flyer activation redirects its
job root to `tmp_path`.

## Validation

```text
8 passed, PYTEST_RC=0
```

No effective network call, provider, persistent subprocess, service, worker,
cron, RD live data, XIO, n8n, Git or external state was touched.

## Decision

Count this group as bounded local evidence. Remaining unexecuted residual
surfaces need the same per-file boundary proof; no blanket runtime execution
is authorized.

## Next concrete action

Refresh the objective audit with Phases 284–288 and perform a final physical
invariant check. Leave authority-gated objectives open and do not claim full
completion.
