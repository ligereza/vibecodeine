# Phase 470 — RD/portfolio read-only entity adapter

## Scope

The RD/portfolio relation boundary is now represented by a candidate data
contract and a small read-only adapter:

- `data/rd_fuentes/candidates/rd_portfolio_entity_crosswalk.json`
- `src/flujo/rd/entity_crosswalk.py`
- `tests/test_entity_crosswalk.py`

The adapter returns typed immutable records containing canonical id, role,
confidence, publication state and evidence. It does not open SQLite, write
JSON, mutate venue/productora data or publish technical records.

## Foreground validation

- Python compilation of the adapter and test exited 0.
- Default crosswalk load returned four unique entities with
  `status=review_only`.
- Role assertions returned OpenKlub as `producer_or_brand`, FRVR as
  `artist_dj_headliner`, and SCD Plaza Egaña as `gated`.
- Duplicate-id negative fixture was rejected and remained on disk.
- Read-only source databases were not opened by the adapter process.

## Disposition

`RD_ENTITY_ADAPTER_GREEN; ROLES_PRESERVED; PROVENANCE_REQUIRED;
NO_SQLITE_MUTATION; NO_PUBLICATION`

## Next action

Run the adapter against the existing RD read consumers and venue schema. Only
after that gate passes should the crosswalk be considered for a future API
projection; keep `review_only` as the default.
