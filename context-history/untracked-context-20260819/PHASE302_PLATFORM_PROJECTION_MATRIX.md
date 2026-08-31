# Phase 302 — platform projection matrix

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none  
Status: `MATRIX_COMPLETE_NO_SOURCE_DIVERGENCE`

## Scope and method

Read-only comparison from `/home/mak/*` between:

- canonical surface: `/home/mak/flujo/cultura/mak_plataforma/*.py`
- runtime surface: `/home/mak/plataforma/*.py`

Classification used exact bytes, explicit shim markers
(`spec_from_file_location`/`runpy`) and physical presence. No Git inventory,
tree copy or deletion was used.

## Result

```text
canonical/runtime rows: 50
exact pairs:            25
compatibility shims:    21
source-divergent pairs:  0
canonical-only pairs:    0
runtime-only files:      4
```

Exact pairs:

`benchmark.py`, `calidad_loop.py`, `copilot.py`, `cuotas.py`, `descargar.py`,
`discernment.py`, `energia.py`, `energia_log.py`, `entregar.py`, `gpu_guard.py`,
`guardia.py`, `ideas.py`, `instagram_source.py`, `ledger.py`, `mantenimiento.py`,
`metricas_capataz.py`, `mineria_rd.py`, `mutaciones.py`, `providers.py`,
`red_watch.py`, `rescue_adjudicator.py`, `revision_episodios.py`, `revisor.py`,
`visual_index.py`, `xio_evidence.py`.

Shim pairs:

`actividad.py`, `backlog.py`, `backlog_codex.py`, `capataz.py`, `chat_agente.py`,
`coherence.py`, `contrato_archivo.py`, `entregar_micelio.py`,
`filtro_entrada.py`, `hub.py`, `junta.py`, `latido.py`, `material.py`,
`puente_issues.py`, `research_router.py`, `revision.py`, `roles.py`,
`salud.py`, `tandas.py`, `trabajo.py`, `vigilar_red.py`.

Runtime-only files requiring a separate consumer decision:

`/home/mak/plataforma/agente_real.py`,
`/home/mak/plataforma/memoria.py`,
`/home/mak/plataforma/panel_directivo.py`,
`/home/mak/plataforma/vigia.py`.

These are not declared junk. They may be projections from another department,
historical runtime tools or unowned residue; their consumers and provenance
must be checked before quarantine.

## Validation

The matrix command exited 0 and reported no source-divergent pair. Previous
phases supplied focused compile/import/test evidence for the exact and shim
families. No file changed in this phase.

## Decision and next

The platform owner architecture is coherent: canonical FLUJO source plus
runtime projections, with no hidden second implementation among paired files.
Next audit the four runtime-only files from `/home/mak/*`, searching active
consumers and historical provenance in bounded scope. Preserve any data,
ledger, generated output or service contract; quarantine only with exact
consumer proof and rollback.
