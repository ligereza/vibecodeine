# Scoped branch contract

Branch: `tools/venue-scd`
Owner: `LUNA-503`
Base: `main` at `da8ab50`
Domain: `tools`
Consumer: `tools/venue_geometria_scd.py`

## Objective

Add a non-mutating `--check` gate for the SCD Plaza Egana geometry generator.
It must compare the committed canonical venue JSON with the deterministic
generator output without writing the venue file.

## Allowed write set

- `tools/venue_geometria_scd.py`
- `tests/test_venue.py`
- `contracts/branches/tools-venue-scd/agents.md`
- `context/handoffs/tools-venue-scd.md`

Generated venue JSON, HTML, databases, README, WIN and historical context are
read-only for this branch.

## Validation gate

```text
python -m py_compile tools/venue_geometria_scd.py tests/test_venue.py
python -m pytest -q tests/test_venue.py tests/test_venue3d_smoke.py
python tools/venue_geometria_scd.py --check
python tools/venue_geometria_scd.py --stdout | python -m json.tool
git diff --check
```

The check must prove that `data/venues/scd-plaza-egana.json` is unchanged.

## Forbidden

Do not add network calls, browser services, dependencies, database writes or
venue claims. The SCD file remains a derived demo with explicit confidence
tiers; no measured data may be invented.

## Rollback

Revert the branch commit or delete the short-lived branch. Preserve the demo
JSON and every historical evidence file.
