# Phase 224 — final open-gate ledger

Date: 2026-08-15 (America/Santiago)

This is the current boundary after all executable local checks. It does not
replace validation; each row points to the evidence that already ran and the
smallest next action when the missing input exists.

| Gate | Current evidence | Exact missing input | Recovery/next action |
|---|---|---|---|
| Real RD field data | `/home/mak/flujo/data/rd_datos.db` has 0 rows in `registros_testeo`, `atenciones`, `encuestas`; demo ingest and PII rejection fixtures pass | Real CSV/acta and provenance/authority; bounded search found only `data/rd_datos_demo/*` and historical evidence JSON | Run `python -m flujo rd-datos ingest <real.csv> --tipo <testeo|atencion|encuesta> --policy strict --db /home/mak/flujo/data/rd_datos.db`, then record source/hash; do not use demo files |
| RD mutators | Logo mutator fixture passes; symbol, datadrop, and database writer paths are mapped; live POSTs not called | Explicit decision/source for logo/symbol/data upload and output destinations | Run one bounded POST/CLI fixture only after authority; preserve rollback and hashes |
| Optional runtime | Base venv `pip check` exit 0; imports pass; optional provider/GPU paths not invoked | External provider credentials/hardware authority, if those slices are required | Validate the named optional slice in its own environment; no installation by inference |
| Historical incomplete panel | `/home/mak/plataforma/panel_directivo.py` AST failure at line 145; no active consumer | Human decision whether to preserve as evidence or retire after provenance | Preserve unchanged unless a bounded repair/retirement request exists |
| Legacy platform UI | `/home/mak/plataforma/interfaz.py` full hash and no bounded launcher reference; historical source role remains | Explicit quarantine approval if historical source may be moved | Keep at original path; inverse quarantine exists only as a proposal |
| Git branches | Phase 218 proposal complete; no Git operation performed | User authorization to create/switch branches | Create only the named branch with disjoint write set after architecture acceptance |

## Verified invariants

- `/home/mak/WIN` remains intact and historical.
- `rd.db` and `rd_datos.db` remain separate; read/report/render fixtures did
  not change their hashes.
- Confirmed shell residue is absent from active surfaces and recoverable in
  phase quarantines.
- `n8n-local` is excluded from active MAK; XIO is excluded by user.
- All four relevant user services are inactive; no persistent process remains.

## Next concrete action

No further local mutation is justified without one of the exact missing inputs
above. Continue read-only checks only, or resume the named gate when its source
or authority becomes available.

