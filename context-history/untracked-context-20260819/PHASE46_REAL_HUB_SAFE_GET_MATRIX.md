# Phase 46 — real hub safe GET matrix

Identity: LUNA principal
Status: PASS_REAL_RUNTIME_MATRIX
Scope: validate the integrated read-only slices together inside one real
temporary `flujo serve` process.

## Process

Command:

```text
/home/mak/venvs/flujo/bin/flujo serve --no-abrir --host 127.0.0.1 --port 49349
```

The process used an ephemeral localhost port, no desktop mode and no
`--procesar-pendientes`. It was explicitly terminated after the matrix and no
process remained.

## Safe GET matrix

All 12 endpoints returned HTTP `200` in the same process:

- `/api/ping`
- `/api/status`
- `/api/rd-packs`
- `/api/rd-db`
- `/api/list-svg-works`
- `/api/svg-index`
- `/api/portafolio`
- `/api/show-kit`
- `/api/list-jobs`
- `/api/dashboard-summary`
- `/api/event-presets`
- `/api/agents-roles`

The response envelopes were valid and the expected keys were present for each
slice. This is stronger than isolated in-process calls: the installed CLI,
real HTTP server, hub routing and local readers operated together.

## Explicit exclusions

- `/api/automatizaciones` was skipped because the configured path can shell
  out to external GitHub/provider infrastructure.
- `/api/rd-datos-summary` was skipped unguarded because the active
  `rd_datos.db` is empty and its normal connector can create schema; Phase 40
  proved its guarded fallback instead.
- All POST routes, job lifecycle actions, uploads, renderers and workers were
  skipped.

## Result and rollback

- Process return code after explicit termination: `-15`.
- `process_alive=false`.
- Protected source/data/jobs/SVG/projects snapshot:
  `writes_detected=false`.
- No source, data, artwork or evidence changed.

The integrated safe GET surface is operational in MAK. Remaining work is
bounded to the explicitly deferred external/mutating/empty-data boundaries and
the open CLI content-difference anchor; no broad tree merge is justified.

