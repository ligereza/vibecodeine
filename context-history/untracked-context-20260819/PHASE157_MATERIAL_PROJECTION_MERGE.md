# Phase 157 — material queue projection merge

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Source, target and consumer

- Canonical source: `/home/mak/flujo/cultura/mak_plataforma/material.py`
- Runtime target: `/home/mak/plataforma/material.py`
- Queue output: `/home/mak/plataforma/material.jsonl`
- Consumer: `/home/mak/plataforma/trabajo.py`
- Scheduled template: `/home/mak/plataforma/crontab.mak` (`MAK-MATERIAL`);
  installed cron line remains paused.

## Action

The 20,211-byte exact target copy was moved reversibly to
`context/quarantine/phase156_platform_projection/material.py.pre-wrapper`.
The runtime target now contains a 479-byte wrapper that resolves the canonical
source and executes it with the same command-line contract. No queue, lock,
consumer, cron installation, rollback archive or WIN file was changed.

## Foreground validation

```text
/usr/bin/python3 -m py_compile target canonical -> exit 0
canonical --contar ->  tareas en cola: 3269 | pendientes: 0
wrapper --contar   ->  tareas en cola: 3269 | pendientes: 0
cmp output -> exit 0
queue before/after -> 1786731301:1019885 / 1786731301:1019885
queue hash before/after -> 4d30c139...cd7723 / 4d30c139...cd7723
matching material.py process after check -> none
```

## Decision

`material.py` is consolidated as a canonical-source projection. Normal mode
still writes the queue and therefore remains outside this read-only gate; the
paused cron must not be enabled by this phase. Rollback is the quarantined
pre-wrapper file.

## Next action

Inspect the next real platform consumer, excluding state/evidence and already
consolidated bridge/tariff projections. Prefer a bounded non-mutating contract;
if no safe read path exists, perform static/compile validation and leave the
runtime projection untouched until its mutation boundary is explicit.
