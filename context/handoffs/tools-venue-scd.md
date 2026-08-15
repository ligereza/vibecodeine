# Branch handoff: tools/venue-scd

Branch: `tools/venue-scd`
Contract: `contracts/branches/tools-venue-scd/agents.md`
Owner: `LUNA-503`
Base commit: `da8ab50`

## Current objective

Add a non-mutating `--check` mode to the SCD geometry generator so the
canonical venue JSON can be verified in CI or by an operator without running
the default writer.

## Baseline evidence

- `tests/test_venue.py` and `tests/test_venue3d_smoke.py`: 45 tests passed.
- `tools/venue_geometria_scd.py --stdout`: valid JSON, 56 polylines, unit m,
  explicit DEMO note.
- `tools/venue.py geometria`: 1 geometry venue, 503 edges, zero degenerate
  segments; no database or venue source was changed.

## Open items

- Promote the durable gate result to the root handoff before branch deletion.

## Next concrete action

Implemented `--check` in `tools/venue_geometria_scd.py`. It parses the
deterministic document, compares it with the committed canonical JSON, reports
drift with exit 1 and never writes the file. Passing `--check` and `--stdout`
together is rejected with exit 2.

Validation results:

- compile and focused suite: exit 0, `46 passed`;
- `tools/venue_geometria_scd.py --check`: exit 0;
- `--stdout | python -m json.tool`: exit 0;
- canonical venue JSON and README SHA-256 hashes unchanged;
- `git diff --check`: exit 0.

The SCD demo remains explicitly derived/unmeasured where appropriate: 56
polylines, 503 edges and zero degenerate segments. No RD database, venue
source, generated site, README, WIN or service was changed.

## Disposition

`SCD_REGENERATION_CHECK_GREEN; OFFLINE_JSON_GREEN; SOURCE_HASHES_GREEN`

## Next concrete action

Promote this result to the root handoff, remove the temporary branch contract
and handoff, fast-forward `main`, and delete the short-lived branch.

Last verified: 2026-08-15 America/Santiago.
