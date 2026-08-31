# Phase 201 — RD field-data and mutation authority gate

Status: `READ_ONLY_PASS; MUTATORS_DEFERRED`

## Read-only surfaces

| Route | Input | Output | Mutation |
|---|---|---|---|
| `GET /api/rd-db` | none | catalog productoras/venues/events | none; reader catches errors |
| `GET /api/rd-packs` | none | canonical `PACKS`, order, default | reloads in memory from `data/rd_packs.json`; no file write |
| `GET /api/rd-datos-summary` | none | zero-count/privacy-safe field summary + disclaimer | opens existing `rd_datos.db` read-only |
| `GET /api/rd-db/logo` | validated slug | image bytes | none; no upload |

These routes were previously exercised in bounded foreground gates. The field
database remains three valid empty tables; demo/evidence data is not promoted
to real field data.

## Mutating surfaces intentionally not called

- `POST /api/rd-db/logo`: writes downloaded/uploaded logo material under
  `knowledge/logos/descargas`; requires explicit logo-source authority and
  rollback.
- `POST /api/plano-simbolos`: writes SVG/catalog entries under
  `data/plano_simbolos*`; requires a bounded symbol payload and rollback.
- `POST /api/plano/render` and `POST /api/cotizacion/render`: generate output
  artifacts; routes are known to work from prior fixture gates, but live
  delivery output was not regenerated in this audit.
- Datadrop upload/analyze/package routes: write and/or analyze incoming media;
  outside the current RD field-data authority.

No mutator was invoked. There is no justification to merge `rd.db` with
`rd_datos.db`: catalog projection and privacy-first field records have
different authorities, lifecycles and disclosure rules.

## Validation

- Static route/handler inspection: exit `0`.
- Existing read-only RD and quote/plano foreground gates: passed in prior
  phases and referenced in the handoff.
- No upload, logo download, symbol write, field ingest, demo promotion,
  provider, service, cron, package, WIN or Git action.

Next: keep mutators deferred until an explicit bounded request supplies input,
expected output and rollback. Continue final progress/visual reporting and
folder cleanup ledger instead of inventing field data.
