# Phase 468 — RD/portfolio entity crosswalk gate

## Result

The physical authority check across `/home/mak/*` confirms that the RD and
portfolio surfaces should be connected by an explicit review-only crosswalk,
not by merging their databases.

- `data/rd.db` is the populated RD catalogue and contains packs, productoras,
  venues, event links and evidence tables.
- `data/rd_datos.db` contains only empty operational tables and is not a second
  populated RD catalogue.
- `data/venues/*.json` contains technical/public venue projections for VJ and
  geometry consumers.
- `iskvw/datos/obras.json` contains visual works and is not an event/venue
  database.
- `tools/portfolio/proyectos.json` contains curated public projects and is not
  the visual work catalogue.

## Role corrections carried into the crosswalk

- Espacio Riesco remains a venue candidate/example, not an automatic event
  venue for every producer relation.
- OpenKlub is a producer/brand. Its `Central Cultural` reference remains an
  unconfirmed venue candidate.
- FRVR is represented as the headliner DJ/artist. Its producer and venue
  relations remain unresolved; `Sala Metronomo` is the raw venue evidence and
  `Paralelo 86` is preserved as a lineup token. No `paralelo_89` venue is
  created.
- SCD Plaza Egaña is a technical venue record without an automatic RD join.

The machine-readable crosswalk is
`context/PHASE468_RD_PORTFOLIO_ENTITY_CROSSWALK.json`. It is `review_only`,
contains provenance and confidence, and does not modify any source database.

## Foreground evidence

- Read-only SQLite schema/count inspection of MAK `data/rd.db`,
  `data/rd_datos.db`, `data/rd.db.premerge-20260815`, WIN `data/rd.db`, the
  Windows reconciliation DB and the state DB exited 0.
- The populated `data/rd.db` and WIN `data/rd.db` have the same 2,740,224-byte
  surface and matching table/row counts; the premerge DB is a smaller
  historical projection with 3 venue rows and no later evidence columns.
- JSON root/schema inspection of venue, producer and portfolio sources exited
  0.
- No database, JSON source, YAML knowledge record, portfolio work, runtime,
  service or WIN evidence was modified.

## Disposition

`RD_CATALOG_IDENTIFIED; RD_DATOS_EMPTY_OPERATIONAL;
ENTITY_ROLE_CROSSWALK_REVIEW_ONLY; VENUE_PRODUCER_CONFLATION_PROTECTED;
NO_DATABASE_MERGE; NO_AUTOMATIC_ID_JOIN`

## Next action

Validate the crosswalk against read-only RD consumers and the venue schema,
then decide whether a small shared identity adapter belongs in `rd/runtime` or
`mak/ownership`. Do not insert rows or expose technical venue data in the
public portfolio until each relation has explicit provenance, confidence and
publication status.
