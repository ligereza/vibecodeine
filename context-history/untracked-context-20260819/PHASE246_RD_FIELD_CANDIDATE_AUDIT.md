# Phase 246 - RD field evidence candidate audit

Date: 2026-08-15 (America/Santiago)
Owner: LUNA principal

## Finding

A concrete historical RD field-testing candidate exists. It is not absent, but
it is not yet authorized production field data. The machine-readable record
explicitly carries `candidate_evidence_pending_human_review`.

## Evidence surface

| Path | Role | SHA-256 / counts | Disposition |
|---|---|---|---|
| `/home/mak/WIN/claude_sesiones/Testeo 2025.source.xlsx` | preserved source workbook | `5b9e54c6...54c8055`, 2,096,806 bytes | historical source; do not mutate |
| `/home/mak/state/windows-director-20260813/claude-recovered-artifacts/Testeo 2025.source.xlsx` | recovered duplicate | same SHA-256 and size | preserve recovery copy |
| `/home/mak/WIN/claude_sesiones/rd_testeos_eventos_2025_evidence_2026-08-12.json` | historical derived evidence | same SHA as state copy; 42 sheets/events, 1,831 test rows, 5,394 observations | preserve; pending review |
| `/home/mak/flujo/data/rd_fuentes/testeo_eventos_2025_evidence.json` | active derived catalog source | 42 sheets/events, 1,831 test rows, 5,394 observations, 84 link-queue rows | already projected into `rd.db` test evidence; not privacy ingest |

The workbook has 42 source sheets and the integrated evidence has explicit
quality/review structures. The accompanying report says that 1,646 rows are
classified as data and 115 have anomalies; it also says dates, duplicate
sheets, substance/reagent labels and event links require human review. The
semantic rule is presence-signal evidence only, not identity, purity, dose or
safety.

## Foreground verification

The read-only candidate audit used ZIP/XML workbook metadata and JSON parsing;
it did not open LibreOffice, write a workbook, ingest a CSV, alter a database
or expose row contents. Exit code was 0. SHA-256 confirms the source and
recovered source are identical. The active derived JSON has the expected
schema and review status.

## Boundary and next gate

Phase 54 already projected the historical test-evidence tables into the
canonical catalog `/home/mak/flujo/data/rd.db`. That does not authorize copying
rows into `/home/mak/flujo/data/rd_datos.db`, whose privacy-first schema is
currently empty. The missing gate is human confirmation of provenance, period,
duplicate handling, event links and permission to ingest into the field store.

No active file changed in this phase. No demo data, WIN source or candidate
rows were copied. Next action, if authority arrives: hash the approved source,
run the strict privacy scan through `flujo rd-datos ingest` into a rollback
backup, then validate counts and the report foreground.

