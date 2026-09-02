# Phase 304 — material import owner gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none  
Status: `RUNTIME_IMPORT_CONTRACT_REPAIRED`

## Finding

`/home/mak/plataforma/material.py` was a `runpy`-only CLI wrapper. When
`/home/mak/plataforma/trabajo.py` imported `material`, it received a wrapper
without `pop_pendiente()`, although canonical `material.py` defines and
`trabajo._tarea()` calls that function. This caused
`test_dispatch_rechazado_no_incrementa_count` to fail before the dispatcher
could reach its intended assertion.

## Action

Replaced only the wrapper with a canonical module projection that registers
the loaded module, aliases normal imports to it, and forwards direct execution
to `main`. The material queue data and all scheduler state were untouched.

## Foreground validation

| Command | Exit | Result |
|---|---:|---|
| `python3 -m py_compile` canonical/projection | 0 | both parse |
| selected `trabajo`, `micelio` and `tandas` pytest suite | 0 | all selected tests pass |
| root import of `material` | 0 | `pop_pendiente` available |
| root import of `trabajo` | 0 | consumer references the repaired module |
| active crontab count | 0 | 0 entries |

No queue pop, network, provider, service, worker or external mutation was
executed; test writes were temporary.

## Next

Classify the remaining runtime-only `agente_real.py` and
`panel_directivo.py` by active consumer/provenance. Preserve them unless a
path-specific optional/manual status is proven; do not delete by absence of a
canonical pair.
