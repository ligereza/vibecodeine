# Phase 301 — local platform risk gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none  
Status: `STATIC_IMPORT_AND_MOCK_PASS_RISK_CLASSES_OPEN`

## Scope

The local platform families were checked:

- `backlog.py`: mutates backlog/state files through atomic rewrites;
- `capataz.py`: can invoke subprocess/HTTP operations and append ledgers;
- `revision.py`: reads visual review data and records review decisions;
- their root paths are existing compatibility projections.

They are not interchangeable by filename and were not merged further. Their
semantic owners remain in `flujo/cultura/mak_plataforma`; the root projections
remain because runtime callers use `/home/mak/plataforma`.

## Foreground validation

| Command | Exit | Result |
|---|---:|---|
| `python3 -m py_compile` six canonical/runtime files | 0 | all parse |
| local backlog/capataz/revision pytest family | 0 | 96 tests pass |
| root-path imports | 0 | `cargar`, `evaluar_riesgo`, `rows` available |

Tests used mocks or temporary paths. No real subprocess, HTTP provider, queue,
ledger, review file, scheduler, service, database, XIO or WIN state changed.

## Decision and next

Keep these projections and risk boundaries. Do not execute `backlog.cosechar`,
`backlog.pop_pendiente`, `capataz.ejecutar` or `revision.record` against live
paths during this inventory. Next produce a bounded platform projection
matrix for every `cultura/mak_plataforma/*.py` versus `/home/mak/plataforma/*.py`,
classifying exact, shim, source-divergent and missing pairs; use it to select
the next real consumer rather than repeating already-fused families.
