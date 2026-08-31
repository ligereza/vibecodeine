# Phase 213 — RD route and field-data authority audit

Date: 2026-08-15 (America/Santiago)

## Authority map

| Surface | Method/command | Reads/writes | Decision |
|---|---|---|---|
| Catalog panel | `GET /api/rd-db` | Reads `data/productoras/*.json`, `knowledge/venues/*.yaml` and logo metadata through the privacy allowlist; does not use the regenerable SQLite catalog as its source | read-only, validated |
| Tariff panel | `GET /api/rd-packs` | Reads/reloads `data/rd_packs.json` through `src/flujo/plano/packs.py` | read-only, validated |
| Field summary | `GET /api/rd-datos-summary` | Opens existing `data/rd_datos.db` read-only; empty totals are valid; does not create the DB on a GET | read-only, validated |
| Logo preview | `GET /api/rd-db/logo?slug=...` | Reads a bounded logo candidate path; current `thegrid` probe returned HTTP 404 because no serving file was found | read-only, validated as non-mutating; missing asset remains a data gap |
| Catalog rebuild | `flujo rd-db build` | Rebuilds `data/rd.db` from canonical sources, deleting/re-writing the projection | writer, deferred |
| Field ingest | `flujo rd-datos ingest CSV --tipo ...` | Privacy-scans each row, then appends to `data/rd_datos.db`; schema remains separate from `rd.db` | writer, deferred pending real field authority |
| Field report | `flujo rd-datos informe --salida ...` | Reads field DB and writes a Markdown report | output writer, fixture not yet run |
| Logo upload | `POST /api/rd-db/logo` | Writes `knowledge/logos/descargas` | mutator, deferred |
| Symbol add | `POST /api/plano-simbolos` | Persists a symbol in `data/plano_simbolos.json` | mutator, deferred |
| Plan render | `POST /api/plano/render` | Builds layout/rider/cost payload in memory; no persistent write in current `api_plano_render` path | transient compute, fixture validated in Phase 223 |
| Quote render | `POST /api/cotizacion/render` | Builds quote items/Markdown payload in memory; no persistent write in current `generar_cotizacion_base` path | transient compute, fixture validated in Phase 223 |
| Datadrop upload/analyze/prepare/scan | POST endpoints | Writes photos/manifests/analysis/review package or processes incoming evidence | evidence mutators, deferred |
| Symbol trace preview | `POST /api/plano-simbolos/trazar` | Computes an SVG preview from request bytes; no persistent write in handler | transient compute, not called in this phase |

## Foreground GET validation

A temporary `ThreadingHTTPServer` bound to a free loopback port and shut down
in the same process. It called only:

- `/api/rd-db` → HTTP 200
- `/api/rd-packs` → HTTP 200
- `/api/rd-datos-summary` → HTTP 200
- `/api/rd-db/logo?slug=thegrid` → HTTP 404 (missing serving asset, no write)

In a second temporary-server run, all three read endpoints returned `[200, 200,
200]`; SHA-256 before/after was unchanged for both `data/rd.db` and
`data/rd_datos.db`; server shutdown returned `shutdown=True`.

## Conclusion

There is no evidence-based reason to merge `rd.db` and `rd_datos.db`. They
have opposite lifecycles: one is a regenerable catalog/evidence projection,
the other is an accumulative privacy-first field store that is currently empty.
The route boundary is explicit and safe for GET reads. All writes remain
deferred until the corresponding source, field authority, output destination
or logo/symbol decision is supplied.

## Next concrete action

Validate the field-data read/report path against the existing empty database
without ingesting rows, then reconcile dependency declarations and remaining
runtime slices. Do not call a POST route, rebuild `rd.db`, or promote demo/
evidence data to real field data.
