# Phase 429 - OpenKlub conflation correction plan

Date: 2026-08-15
Agent: LUNA principal
Scope: determine the smallest safe correction for the OpenKlub producer/venue
conflation before changing the RD source or rebuilding the database.

## Consumer trace

The active loader path is:

```text
knowledge/venues/*.yaml
    -> src/flujo/rd/database.py
    -> data/rd.db.venues
    -> rd-db CLI / RD panel / generated RD presentation
```

OpenKlub also has the correct producer path:

```text
data/productoras/openklub.json
    -> data/rd.db.productoras
    -> productora types/logos/event notes
```

The current `productora_venues` row for OpenKlub points to the unresolved
candidate `Central Cultural` with `venue_id=NULL`; it does not need the
conflated `venue_id=openklub` row to work.

## Safe correction plan

1. Keep `data/productoras/openklub.json` as the producer owner.
2. Preserve `knowledge/venues/openklub.yaml` as evidence until its provenance
   is classified and a real venue identity is known.
3. Remove the conflated file from the active `knowledge/venues` projection only
   through a reversible, recorded quarantine operation; do not delete it.
4. Rebuild `data/rd.db` from sources only after that boundary is approved.
5. Validate `rd-db venues`, the RD standalone panel, productora OpenKlub and
   the `Central Cultural` unresolved candidate. Confirm `openklub` no longer
   appears as a venue and remains present as a producer.

## Verification

- Consumer grep and loader inspection: exit 0.
- `tools/venue.py validar`: exit 0; 3 public JSON venues remain valid.
- No source, YAML, database, HTML, service, provider or Git state changed in
  this phase.

## Boundary

The plan identifies a reversible source correction, but it was not executed:
the replacement physical venue is unknown and the current evidence must remain
recoverable. The next mutation, if authorized by the active task, is the
quarantine of exactly `knowledge/venues/openklub.yaml`, followed by a bounded
RD database rebuild and foreground validation.
