# Phase 223 — RD render route mutation correction

Date: 2026-08-15 (America/Santiago)

## Finding

The earlier route ledger conservatively called the plan/quote POST endpoints
"output mutators". Source inspection and a direct foreground fixture show a
more precise result:

- `flujo.serve.server.api_plano_render()` builds layout/rider/cost strings in
  memory and returns a JSON-compatible payload.
- `flujo.cotizaciones_base.generar_cotizacion_base()` builds items/Markdown in
  memory and returns a payload.
- Neither function writes a file or database in the tested path.

## Validation

The `INFO` plan fixture returned layout, rider, costs and `validacion.ok=True`.
The quote fixture returned items, Markdown and a nonzero total. SHA-256 for
both `data/rd.db` and `data/rd_datos.db` was identical before and after.
Observed result: `persistent_outputs_written=false`.

## Correct classification

`POST /api/plano/render` and `POST /api/cotizacion/render` are transient
compute/render payload routes, not persistent database/file mutators in the
current implementation. They still require input validation and foreground
fixture gates, but do not need a deletion rollback. Logo upload, symbol add,
job creation, datadrop operations and database ingest/rebuild remain true
mutators.

## Next concrete action

Update the route matrix to use this corrected classification, then keep live
POST calls deferred while validating only transient fixtures.

