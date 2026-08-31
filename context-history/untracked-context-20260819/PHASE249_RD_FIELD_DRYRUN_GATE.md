# Phase 249 - RD field candidate dry-run gate

Date: 2026-08-15 (America/Santiago)
Owner: LUNA principal

## Scope

The active derived candidate
`/home/mak/flujo/data/rd_fuentes/testeo_eventos_2025_evidence.json` was
joined in memory by `event_id` and converted to the real `rd-datos` testeo CSV
contract in a temporary directory. No candidate row was copied to the live
`/home/mak/flujo/data/rd_datos.db`.

## Dry-run result

Input: 5,394 observations across 42 events.

- Event date status: 10 `parsed_candidate`, 4 `ambiguous_compact_numeric_token`,
  12 `partial_day_month_compact`, 4 `partial_day_month_only`, 12 `not_found`.
- Only 10 of 42 events have a valid ISO date candidate.
- 4,425 observation rows lack a date after the join.
- 318 lack a substance candidate and 357 lack a reagent candidate.
- 762 rows passed form and strict privacy checks in the temporary DB.
- 19 rows were rejected by the privacy scanner.
- 4,613 rows were invalid by form (principally missing date/required fields).
- The temporary DB contained exactly 762 inserted rows and was removed with
  the temporary directory.
- The live `rd_datos.db` SHA-256 was unchanged before/after the dry-run.

## CLI route check

The same generated CSV was passed through the actual foreground command:

```text
/home/mak/venvs/flujo/bin/python -m flujo rd-datos ingest <temporary-csv> \
  --tipo testeo --policy strict --db <temporary-db>
```

Corrected command result: exit 0, 762 temporary rows, 12 stdout lines, 0
stderr lines. The first harness attempt returned exit 1 because it passed
`None` to `date.fromisoformat`; it failed before invoking the CLI and touched
no live path. The corrected rerun is the authoritative route result.

## Decision

The RD field ingest route works and the privacy gate behaves as designed, but
the candidate is not ready for live ingest. Dates, required fields, duplicate
groups, unresolved labels and the 19 privacy rejections require review and
authority. This is a concrete data-quality gate, not a missing-code problem.

## Next concrete action

Obtain review/authority for the candidate and resolve the date/field mapping
before any live ingest. Until then keep `rd_datos.db` empty and preserve WIN,
the source workbook and the derived evidence.

