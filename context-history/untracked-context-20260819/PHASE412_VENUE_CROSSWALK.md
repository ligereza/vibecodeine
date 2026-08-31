# Phase 412 — Venue crosswalk (read-only, corrected)

> Current-truth correction: the earlier `paralelo_89` row was inferred from
> the filename `FRVR.PARALELO89.png` and must not be treated as a venue. The
> active FRVR authority is an artist/DJ headliner with raw venue
> `Sala Metronomo`; the organizer remains unconfirmed.

Date: 2026-08-15
Agent: LUNA principal
Scope: cross-domain mapping of RD catalog venues to VJ technical venue
records and possible Curatoria/portfolio consumers. No database or venue data
was modified.

## Physical inputs

| Domain | Owner | Input |
|---|---|---|
| RD catalog | `/home/mak/flujo/data/rd.db` | `venues`, `productora_venues`, `productora_eventos` |
| VJ technical | `/home/mak/flujo/data/venues/*.json` | venue technical/public records |
| Venue knowledge | `/home/mak/flujo/knowledge/venues/*.yaml` | canonical presets and confidence notes |
| Visual consumer | `/home/mak/flujo/iskvw/piel/venue/` | venue skin and technical visual surface |
| Contract | `/home/mak/flujo/schemas/venue.schema.json` | public/private and measurement confidence rules |

## Canonical crosswalk

| canonical_id | RD name | RD status | VJ record | technical status | public projection | action |
|---|---|---|---|---|---|---|
| `espacio_riesco` | Espacio Riesco | example/candidate by producer | no matching JSON | catalog requirements only | gated | confirm venue/date before operational use |
| `openklub` | OpenKlub producer/brand, not canonical venue | raw `Central Cultural` candidate only | no matching JSON | no active venue YAML | gated | do not promote producer name to venue identity |
| `frvr` | FRVR artist/DJ headliner | producer role unconfirmed; raw venue `Sala Metronomo` | no matching JSON | no technical venue record | review-only | do not create `paralelo_89`; confirm organizer before joining |

## Unresolved RD event names

The following event venue strings are not yet canonicalized and must not be
silently joined by fuzzy name alone:

| raw venue | current source/state |
|---|---|
| Club Hípico, Santiago | Creamfields 2025; candidate/unconfirmed |
| Basel Venue Santiago | Dame / Jeff Mills; confirmed IG row but no canonical ID |
| Club Freedom | user-confirmed spot; no canonical ID |
| Central Cultural | OpenKlub candidate; needs confirmation |
| Parque Padre Hurtado | Piknic 2026; no canonical ID |
| Santiago | incomplete Piknic historical row |
| needs_confirmation | Sundeck event without venue resolved |

## Technical VJ records not yet joined to RD

`data/venues/` currently contains `santiago-sala-ejemplo`, `scd-plaza-egana`
and `valparaiso-otro-ejemplo`. They are valid technical-contract candidates,
but none has an evidenced RD catalog relation in the current `rd.db` rows.
Their `venue.schema.json` contract requires an explicit public/private status
and confidence for measurements; a technical record must not become a public
portfolio record merely because it has a name.

## Consumer interpretation

```text
raw event / venue mention
  -> canonical venue_id only after provenance check
  -> RD event/productora/quote consumers
  -> VJ geometry/projection/rider consumers when technical data exists
  -> Curatoria context link when the event/artwork relation is evidenced
  -> portfolio-safe projection only when publico=true and publication allowed
```

## Result and rollback

Result: `CROSSWALK_CORRECTED; 1 ACTIVE RD CANONICAL VENUE; 7 UNRESOLVED EVENT
NAMES; NO_AUTOMATIC_MERGE`. The old WIN-only `openklub` and `paralelo_89`
venue rows are historical evidence, not active MAK venue identities.

Rollback is a no-op because this phase wrote only this report and the handoff;
all source databases, JSON, YAML, skins and historical evidence are intact.

## Foreground verification

- `find /home/mak -mindepth 1 -maxdepth 1 -type d ...`: exit 0; physical
  scope enumerated first. The historical `OneDrive` endpoint was not traversed.
- Python `sqlite3` read-only URI inspection of `data/rd.db`, plus JSON/YAML
  enumeration and schema inspection: exit 0; counts and rows above observed.
- Exact runtime guard for `uvicorn` and `gunicorn`: exit 0; both absent.
- Files modified: this report and `context/LAST_HANDOFF.md` only.

Risk: current `venue_id` coverage is intentionally incomplete. Promoting raw
names to canonical IDs could misattribute a venue, expose private technical
data or produce incorrect RD quotes.

## Next concrete action

Add only explicit aliases/provenance to a crosswalk artifact, then validate it
against RD read consumers and the venue schema. Do not insert new venue rows,
merge databases or expose technical venue data in the portfolio until each
candidate has an owner, confidence and publication status.
