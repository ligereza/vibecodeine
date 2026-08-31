# Phase 413 — cross-domain service architecture

Date: 2026-08-15
Agent: LUNA principal
Scope: record the user's product vision and map it to verified MAK
consumers. This is an architecture/documentation phase; no runtime, data,
provider or Git mutation was performed.

## Verified SCD proof slice

The SCD slice is a concrete prototype for a venue service, not merely a
database row:

- `/home/mak/flujo/data/venues/scd-plaza-egana.json` — technical venue record.
- `/home/mak/flujo/tools/venue_geometria_scd.py` — deterministic geometry
  generator with `--stdout` and file-output modes.
- `/home/mak/flujo/iskvw/piel/venue/` — browser venue skin.
- `/home/mak/flujo/tools/venue3d_smoke.mjs` — bounded 3D behavior smoke test.
- `/home/mak/flujo/schemas/venue.schema.json` — confidence and public/private
  contract.
- `/home/mak/flujo/tools/portfolio/proyectos.json` — public catalogue already
  contains `plano-rider-rd` and other related offerings.

The current SCD record is suitable as a demonstrator, not yet as a certified
technical survey: its stage dimensions are `aportado`, its projection surface
is `desconocido`, and the venue record is public. That distinction must remain
visible in any commercial delivery.

## Product architecture

```text
MAK shared identity/provenance layer
├── Venue service
│   ├── capture/index technical venue data
│   ├── regenerate 3D geometry and web viewer
│   └── deliver venue-specific technical dossier
├── Curatoria service
│   ├── ingest chaotic folders
│   ├── classify, index and preserve provenance
│   └── co-produce dossiers and proposals with colleagues
├── RD/VJ production service
│   ├── event + venue + screen/scenography inputs
│   ├── resolve operational layout
│   ├── generate plan/rider/quote
│   └── adapt the venue layout to visual/screen production reality
└── Portfolio service
    ├── expose safe public projections
    ├── show selected venue/3D/curatorial work
    └── separate public case studies from private source data
```

## Shared contracts

The services should converge on shared identifiers and evidence fields, not
on one undifferentiated database:

```text
venue_id       stable venue identity
project_id     curatorial/RD/VJ project identity
asset_id       source file or generated deliverable
provenance     where the fact came from
confidence     measured/adjusted/contributed/cited/unverified
publico        whether it may be published
consumer       RD, VJ, Curatoria or portfolio consumer
```

`venue_id` links SCD-like technical venue records to RD events and layouts.
`project_id` links Curatoria research and folders to proposals or portfolio
case studies. Neither link authorizes copying private source material or
publishing unverified measurements.

## Vertical commercial slices

1. `venue-3d`: technical intake → venue JSON → 3D viewer → client dossier.
2. `curatoria-index`: chaotic folder intake → bilingual classification →
   provenance index → collaborative dossier/proposal.
3. `rd-vj-layout`: event + venue + screen/scenography constraints → layout,
   rider and quote.
4. `portfolio-cases`: approved public projection of the three services.

The recommended topic branches follow these vertical consumers rather than
department folders:

```text
codex/integration/venue-3d
codex/curatoria/indexing-service
codex/rd-vj/layout-rider
codex/portfolio/service-cases
```

These are names for future short-lived branches only; no branch was created.

## Risks and next action

- Do not sell `aportado` dimensions as measured or certified.
- Do not merge all RD/VJ/Curatoria records into one physical database.
- Do not index or publish chaotic folders without source/provenance and
  privacy classification.
- Do not confuse the RD stand layout with a complete venue technical survey;
  they are related layers with different consumers.

Next: map the three vertical slices to exact existing consumers and generate a
read-only owner/contract matrix before implementing or moving anything.
