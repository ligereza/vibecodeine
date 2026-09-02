# Phase 54 — RD database merge gate

## Scope

The active catalog database was `/home/mak/flujo/data/rd.db`. Historical
evidence databases were `/home/mak/WIN/flujo/data/rd.db` and
`/home/mak/state/windows-director-20260813/rd/rd.db`; those two historical
copies had the same enriched schema and counts. `/home/mak/flujo/data/rd_datos.db`
remains a separate zero-byte field-data database and was not seeded.

## Action

Created the recoverable file backup `/home/mak/flujo/data/rd.db.premerge-20260815`.
Inside one SQLite transaction, the active database retained its catalog rows,
received the two historical `productora_eventos` columns, and received the
eight `testeo_*` evidence tables and their rows/indexes. Historical files were
not changed.

## Foreground evidence

```text
merge transaction
exit=0; commit succeeded; PRAGMA user_version=20260815

post-merge read-only inspection
productora_eventos: 7 rows, 9 columns
testeo_fuentes: 1
testeo_hojas: 42
testeo_eventos_fuente: 42
testeo_filas_fuente: 1831
testeo_observaciones_fuente: 5394
testeo_mapa_sustancias: 30
testeo_mapa_reactivos: 50
testeo_enlaces_revision: 84
foreign_key_check: []
quick_check: ok

temporary flujo serve + GET /api/rd-db
HTTP 200; payload keys connected/excluido_a_proposito/productoras/resumen/venues
clean SIGTERM; process_alive=false
```

## Decision and risk

`rd.db` is now merged at the schema/data-projection level without deleting
historical evidence. The public `/api/rd-db` reader does not expose `testeo_*`
directly; this is correct because those rows are evidence, not public claims.
The next gate is the separate `rd_datos.db` field-data authority and privacy
contract. Do not copy historical evidence into it automatically.
