# Phase 323 — RD field report/read gate

Date: 2026-08-15 (America/Santiago)
Scope: temporary field-data report and GET-summary contracts.

## Paths

- `/home/mak/flujo/src/flujo/rd/informe.py`
- `/home/mak/flujo/src/flujo/rd/datos.py`
- Runtime field store remains `/home/mak/flujo/data/rd_datos.db` and was not
  used as a write target.

## Foreground validation

An isolated temporary `rd_datos.db` received two synthetic, anonymous testeo
rows through `ingest_csv(..., policy="strict")`. Then:

- `informe_trimestral(db_path=temp, trimestre="2026-Q3")` returned Markdown
  with the mandatory presumptive-result and `DEMO/FICTICIOS` disclaimer,
  August aggregation and two rows.
- `resumen_json(db_path=temp)` returned `disponible=True`,
  `total_testeos=2`, `tasa_no_coincidencia_global=0.5` and did not change the
  temporary database size/mtime.
- `resumen_json(missing_path)` returned `{"disponible": False}` and did not
  create the missing file.

The foreground result was:

```text
TEMP_REPORT=PASS disclaimer=True rows=2 tasa=0.5 read_mtime_unchanged=True
MISSING_SUMMARY_NO_CREATE=PASS
```

## Disposition

`VERIFIED_READ_REPORT_CONTRACT; REAL_DATA_AUTHORITY_PENDING`.

The report and GET-summary layers correctly separate read aggregation from
ingest and communicate that the current evidence is demo/fictitious. This
does not turn the empty real field store into data and does not authorize
publication or live ingestion.

## Changes and risks

- Canonical source, `rd.db`, `rd_datos.db`, outputs, services and processes:
  unchanged.
- Risk: `informe_trimestral()` uses schema-creating `conectar()` when pointed
  at a missing path; the GET summary is the safe read-only endpoint and uses
  SQLite URI read-only mode.
- Rollback: no rollback needed; only temporary files were written.

