# Phase 40 — RD field-data boundary

Identity: LUNA principal
Status: DEFERRED_EMPTY_DATA_SOURCE
Scope: classify `/api/rd-datos-summary` safely without seeding or mutating the
privacy-first field-data database.

## Physical search and provenance

The physical search started at `/home/mak/*`, then narrowed by exact database
names. Results:

- Active catalog database: `/home/mak/flujo/data/rd.db` (131072 bytes).
- Field-data database: `/home/mak/flujo/data/rd_datos.db` (0 bytes).
- Historical WIN projection: `/home/mak/WIN/flujo/data/rd.db` (2740224 bytes).
- MAK state snapshot: `/home/mak/state/windows-director-20260813/rd/rd.db`
  (2740224 bytes).
- No other `rd_datos.db`, `*rd*datos*.sqlite` or `*rd*datos*.db` was found
  under `/home/mak` in the bounded exact-name scan.
- A separate demo/evidence surface does exist and must not be mistaken for
  field data: `/home/mak/flujo/data/rd_datos_demo/` contains three synthetic
  CSVs plus `generar_demo.py`, while `/home/mak/flujo/data/rd_fuentes/`
  contains controlled research evidence. The corresponding WIN archive
  surface is `/home/mak/WIN/flujo/data/rd_datos_demo/`; normalized demo
  generator/content parity is evidence only, not an ingestion authorization.
- The two non-active `rd.db` files are evidence/snapshots, not substitutes for
  the active runtime field-data source and were not opened for migration.

## Boundary and risk

- Hub route: `GET /api/rd-datos-summary`.
- MAK sources: `/home/mak/flujo/src/flujo/web/hub.py`,
  `/home/mak/flujo/src/flujo/rd/informe.py` and
  `/home/mak/flujo/src/flujo/rd/datos.py`.
- `resumen_json()` currently calls `conectar(path)` when the empty file exists.
  `conectar()` executes `CREATE TABLE IF NOT EXISTS` and `commit()`. Therefore
  a normal route call is not an acceptable read-only validation of this empty
  source, despite the function docstring promising no side effect.
- Search vocabulary used: `rd datos`, `field data`, `datos de campo`,
  `testeo`, `atencion`, `encuesta`, `summary`, `resumen`, `sqlite`, `db`,
  `database`, `base`, `demo`, `ficticio`, `evidence`, `fuente`. Residual risk
  is limited to non-database field records stored under other names; the
  discovered demo/evidence files are explicitly synthetic or pending human
  review and are not a live field-data source.

## Guarded foreground validation

Foreground command (exit 0) performed:

```text
PYTHONPATH=/home/mak/flujo/src /home/mak/venvs/flujo/bin/python - <<'PY'
  ast.parse(hub.py); ast.parse(informe.py); ast.parse(datos.py)
  sqlite3.connect('file:data/rd_datos.db?mode=ro', uri=True)
  monkeypatch informe.conectar -> raise guarded RuntimeError
  call resumen_json() and GET /api/rd-datos-summary on a temporary server
PY
```

Observed:

- AST/import: `PASS`.
- SQLite read-only inspection: zero objects, no error.
- Guarded direct reader: `disponible=false` with the guard error.
- Guarded handler and temporary HTTP route: HTTP `200`, same fallback payload.
- Normal connector call: `false`.
- Protected source/database snapshot: `writes_detected=false`.

## Decision and recovery

This slice is not integrated because its source contains no field data and the
ordinary connector can create schema. Do not seed it from demo data, WIN
snapshots, `rd.db`, CSV guesses or historical evidence. The minimal recovery
path is a separately authorized privacy/rollback slice with an actual acta de
entrega, approved input files, backup/rollback procedure and a connector
opened in a controlled write gate. Until then the existing zero-byte file and
the truthful unavailable response are preserved.
