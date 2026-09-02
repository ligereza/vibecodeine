# Phase 371 — RD field candidate review packet

Date: 2026-08-15 (America/Santiago)

## Candidate

`/home/mak/flujo/data/rd_fuentes/testeo_eventos_2025_evidence.json`

- status: `candidate_evidence_pending_human_review`
- SHA-256: `8b80830ba74cf5ff26b7575fed5ac5f2ed8cb204796be6d39a7a33b8586db127`
- 42 events/source sheets
- 1,831 test rows
- 5,394 observations
- 84 link-queue records

## Decision-relevant counts

| Gate | Count | Meaning |
|---|---:|---|
| `parsed_candidate` dates | 10 | possible ISO date candidates |
| `not_found` dates | 12 | no date candidate |
| partial/ambiguous dates | 20 | requires human date decision |
| exact duplicate-sheet candidates | 6 | retain raw evidence; decide canonical sheet |
| event labels from sheet names | 42 | not independently confirmed labels |
| linked events | 0 | all 84 link records remain pending human link |
| observations with missing reagent | 357 | strict ingest blocker until resolved |
| observations with unresolved reagent candidate | 8 | strict ingest blocker until resolved |
| observations with canonical reagent registry | 2,946 | locally mapped only |

## Human decisions required

1. Confirm which source sheets belong to the 2025 period when filename and
   sheet labels conflict.
2. Resolve the six exact duplicate-sheet candidates without deleting raw
   evidence.
3. Approve or correct substance/reagent mappings, especially missing and
   unresolved candidates.
4. Link `event_id` to venue/producer only where explicit evidence exists.
5. Approve any public interpretation of color changes.
6. Authorize strict ingest only after the above decisions and a final privacy
   review.

## Safety result

The corrected aggregation command exited 0. The live
`/home/mak/flujo/data/rd_datos.db` remained at SHA-256
`70feaf43b5269b6c0341d1ba3debdac60e40fb902cc4bedb41254fdc84d1f703` and was
not opened for writes. No source workbook, WIN evidence or candidate row was
copied.

Disposition: `REVIEW_PACKET_READY; LIVE_INGEST_BLOCKED_BY_DATA_QUALITY_AND_AUTHORITY`.
