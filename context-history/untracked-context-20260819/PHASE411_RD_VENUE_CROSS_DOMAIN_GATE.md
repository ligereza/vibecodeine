# Phase 411 — RD / VJ / portfolio venue cross-domain gate

Date: 2026-08-15
Agent: LUNA principal
Scope: read-only clarification of the venue relationship across RD,
technical VJ work and the portfolio/Curatoria surface.

## Verified physical model

- Canonical RD catalog: `/home/mak/flujo/data/rd.db`.
- Separate privacy/field store: `/home/mak/flujo/data/rd_datos.db`.
- Canonical RD venue relations: tables `venues`, `productora_venues`,
  `productora_eventos` in `rd.db`.
- Technical venue records: `/home/mak/flujo/data/venues/*.json`.
- Technical venue knowledge records:
  `/home/mak/flujo/knowledge/venues/*.yaml`.
- Technical contract: `/home/mak/flujo/schemas/venue.schema.json`.
- VJ/visual venue surface: `/home/mak/flujo/iskvw/piel/venue/` and the
  related `tools/venue*.mjs` consumers.

The active `rd.db` contains 3 canonical venues, 8 productora-to-venue rows,
7 productora-event rows and 20 productoras. `rd_datos.db` has 4 tables and
0 rows; it is not the owner of venue catalog data.

## Correct interpretation

`VENUE` is a cross-domain entity, not merely an RD field:

```text
canonical venue identity
├── RD: productora, event, quote, operational requirements
├── VJ: geometry, projection surface, access, technical measurements
├── Curatoria: event/context/artist relationship and provenance
└── Portfolio: only the public-safe projection when authorized
```

The databases should therefore be joined logically through a stable
`venue_id`, provenance and confidence level. RD-specific operational fields
and VJ-specific technical fields can remain separate extensions of the same
venue identity. A venue name alone is not a safe join key because several
current rows are inferred, examples or candidates without confirmation.

## Disposition

`rd.db` remains the canonical catalog owner. `rd_datos.db` remains a separate
privacy/field store and must not be physically merged merely because both
domains mention venues. The next valid integration slice is a read-only venue
crosswalk: canonical IDs, aliases, source/confidence, public/private status,
RD consumers, VJ consumers and safe portfolio projection. No database or venue
file was modified.

## Next action

Build and validate the venue crosswalk before any physical merge, duplicate
cleanup or public portfolio exposure. Preserve unconfirmed venue rows and
technical records as evidence until their provenance and publication status
are explicit.
