# Phase 221 — RD field ingest fixture and privacy gate

Date: 2026-08-15 (America/Santiago)

## Evidence boundary

The only structured CSV candidates found in the bounded search are:

- `/home/mak/flujo/data/rd_datos_demo/atenciones_demo.csv`
- `/home/mak/flujo/data/rd_datos_demo/encuestas_demo.csv`
- `/home/mak/flujo/data/rd_datos_demo/testeos_demo.csv`

They are demo fixtures, not real field data, and were not ingested into
`data/rd_datos.db`. The real field database remains 0 rows in all three
tables.

## Positive fixture gate

Ran the canonical CLI against `testeos_demo.csv` with a temporary SQLite path
outside MAK:

```text
python -m flujo rd-datos ingest \
  /home/mak/flujo/data/rd_datos_demo/testeos_demo.csv \
  --tipo testeo --policy strict --db <temporary-db>
```

Exit `0`; `Insertadas: 30`; temporary fixture table count `30`; temporary
directory was cleaned by the test harness. `real_db_untouched=true`.

## Privacy negative fixture gate

A temporary one-row CSV containing `test@example.com` in free text was ingested
with `--policy strict` into another temporary DB. Exit `0`; `Insertadas: 0`;
`Rechazadas por PII: 1`; persisted rows `0`. The sensitive row content was not
printed by the CLI.

## Decision

The field-ingest implementation and privacy boundary function in isolation.
Objective 1 remains open only because no real field source/acta and no user
authority to promote data have been supplied. Demo fixtures and the historical
`rd_fuentes/testeo_eventos_2025_evidence.json` remain evidence, not field data.

## Next concrete action

Keep `rd_datos.db` empty. If real CSV/acta authority arrives, ingest it through
the same CLI with an explicit type/policy and record its provenance; otherwise
continue the final read-only audit without promoting demo/evidence files.

