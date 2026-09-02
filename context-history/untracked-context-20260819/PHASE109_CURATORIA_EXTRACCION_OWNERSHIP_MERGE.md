# Phase 109 — curatoria extraccion_db ownership merge

## Scope and evidence

The active MAK root and canonical `extraccion_db.py` differed from each other
only in documentation text; root and WIN were identical. Function structure
and behavior were unchanged. The tool reads perception fichas, matches
catalogs and can write candidate JSONL/reports, so only pure fixtures were
authorized in this phase.

## Action

Replaced only `/home/mak/curatoria/extraccion_db.py` with a compatibility
projection to canonical MAK. WIN and all fichas, candidate files, reports and
databases were preserved.

## Foreground validation

- Root import and pure normalization/identity/matching fixtures: exit 0.
- Fixture used the real nested `datos_evento` schema and verified canonical
  producer/venue matching plus deterministic new-producer clustering.
- Root bridge and canonical source compile: exit 0.
- No candidate JSONL, report, database, perception, OCR, vision or external
  process was run.

The first fixture used flat producer/venue keys; the real contract correctly
ignored them. The corrected nested fixture passed without code changes.

## Rollback and risk

Rollback is local from the pre-edit root file or WIN copy. Candidate/report
writers remain gated and were not invoked.

## Result

Curatoria extraction now has one active MAK implementation owner; its data
writing boundary remains explicit and unexecuted.
