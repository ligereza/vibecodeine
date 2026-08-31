# Phase 427 - venue role correction and crosswalk (corrected)

> Current-truth correction: `paralelo_89` was an inference from the filename
> `FRVR.PARALELO89.png`, not a confirmed venue. The active record identifies
> FRVR as an artist/DJ headliner and `Sala Metronomo` as the raw venue.

Date: 2026-08-15
Agent: LUNA principal
Scope: incorporate the user's authoritative distinction between venues and
producers into the read-only cross-domain map.

## Role map

| identifier/name | correct role | current evidence | disposition |
|---|---|---|---|
| `espacio_riesco` / Espacio Riesco | venue | `data/rd.db.venues`, `knowledge/venues/espacio_riesco.yaml`, producer relations | valid venue owner; event use still needs per-event confirmation |
| `openklub` / OpenKlub | producer/brand | `data/rd.db.productoras.openklub`, `data/productoras/openklub.json`, user correction | producer owner; do not use as venue |
| historical `openklub` row in old `data/rd.db.venues` | conflated role | present in WIN/old projection only; active MAK catalog no longer has it | preserve as historical evidence; not an active venue |
| quarantined `knowledge/venues/openklub.yaml` | conflated role | old venue knowledge file used producer name as venue ID | preserve in quarantine; do not promote |
| `Central Cultural` | unresolved venue candidate | `productora_venues` and `productora_eventos` for OpenKlub | candidate only; no canonical venue ID |
| `frvr` / FRVR | artist/DJ headliner | `data/productoras/frvr.json`, user correction, raw venue `Sala Metronomo` | preserve artist role; organizer unresolved; do not create `paralelo_89` |
| `scd-plaza-egana` / Teatro SCD Plaza Egaña | technical VJ venue | public `data/venues/scd-plaza-egana.json`, Portfolio venue skin | active technical venue projection; no RD ID auto-assigned |

## Evidence checked

- `data/rd.db`: `venues`, `productoras`, `productora_venues` and
  `productora_eventos` rows for OpenKlub and Espacio Riesco.
- `data/productoras/openklub.json` and `knowledge/venues/openklub.yaml`.
- `data/venues/scd-plaza-egana.json` and `knowledge/venues/espacio_riesco.yaml`.
- Existing RD database state documentation and candidate records.

## Verification

- Read-only SQLite query and JSON/YAML path inspection: exit 0.
- No database row, YAML file, JSON file, HTML, source, service, provider or
  Git state changed.

## Decision

Do not merge venue and producer identities by equal/slightly similar names.
`Espacio Riesco` is a venue. `OpenKlub` is a producer/brand. The active MAK
`data/rd.db` now has one canonical venue, `espacio_riesco`; the old OpenKlub
and Paralelo 89 rows remain only in WIN/archived evidence. `Central Cultural`
is still an unresolved raw relation in OpenKlub's producer record and must
not be promoted without a real venue identity.

## Next concrete action

Continue with the read-only venue/entity consumer gate using the active
`espacio_riesco` catalog row, the three technical JSON venues and the review
crosswalk. Do not recreate `venues.openklub` or `paralelo_89`, merge databases,
or expose a technical venue in Portfolio until its ID, provenance and
publication status are explicit.
