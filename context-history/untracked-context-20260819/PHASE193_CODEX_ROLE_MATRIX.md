# Phase 193 — Codex role matrix

Status: `COMPLETE; SOURCE_RUNTIME_BOUNDARY_CONFIRMED`

## Evidence

The direct source/runtime comparison for the ten Codex Python modules found:

- Exact pairs: `debug.py`, `fallback_util.py`, `iconos.py`, and
  `interfaz_codex.py`.
- Semantic runtime projections: `agente_libre.py`, `codex_lib.py`,
  `generar.py`, `revisar.py`, `testear.py`, and `worker_codex.py`.
- No source-only or runtime-only Python module in this paired set.

The canonical semantic owner is `/home/mak/flujo/cultura/mak_codex`; runtime
entry points under `/home/mak/codex` are retained for service/manual paths.
The source `testear.py` path was repaired in Phase 171 and passed isolated
fixture validation. `interfaz_codex.py` is the service declaration target but
the user unit is currently inactive.

## Decision

Codex is already fused at the ownership level: one canonical implementation,
thin runtime projections for the historical paths, and exact shared helpers
where no projection is needed. No duplicate deletion or new copy is justified.

## Validation

Hash comparison exited `0`; prior Codex semantic/fixture gates passed through
Phases 168–174 and 171's test-runner fix. No provider, service, worker, package,
cron, WIN or Git action occurred in this phase.

Next: use the same matrix for the remaining platform projections, prioritizing
one actual consumer with a bounded pure fixture rather than broad cleanup.
