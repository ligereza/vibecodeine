# Phase 431: Paralelo 89 role correction and research triangulation

## Finding

`Paralelo 89` was not supported as a venue. The active YAML source was inferred
only from the filename `FRVR.PARALELO89.png`. The image itself shows:

- `FRVR` as the headliner/DJ mark (user-confirmed); it is not the producer;
- `PARALELO 86` in the artist lineup;
- `SALA METRONOMO` as the event venue;
- `10 JULIO 2026` as the event date;

The user also flags that the `Paralelo 89` label is likely an artist/DJ label
or a dataset error. It must not become a canonical venue without a primary
source. The producer/organizer remains unknown.

## External triangulation

- `https://paralelo86.com/` identifies Paralelo 86 as a Chilean DJ/producer
  duo and lists venues where it performs; it does not identify Paralelo 89.
- `https://salametronomo.com/pages/faq` identifies Sala Metronomo as the
  event-space consumer; Passline also lists the address and venue.
- No reliable public result was found for `Paralelo 89` as a Chilean venue.

This is evidence for classification, not a claim that the event or its
producer has been externally verified.

## Reversible action

The inferred source was moved, not deleted:

`knowledge/venues/paralelo_89.yaml` ->
`context/quarantine/phase431_paralelo89_role_correction/paralelo_89.yaml`

Original SHA-256:

`9ba9b1785954227325b31292e02d794068867a7466c59ec87963ec6a97d0f4c9`

`data/productoras/frvr.json` now records `FRVR` as `tipo: artist_dj` and
`headliner: true`, records Sala Metronomo as an unresolved event venue
(`venue_id: null`) and explicitly preserves the filename conflict. The file
remains in the compatibility `data/productoras` store because that is the
existing RD catalog owner; its role field prevents treating it as a producer.

## Research triangulation contract

The Research department should resolve incomplete event identities through
orthogonal searches, without promoting guesses to canonical data:

| missing field | search keys | acceptable evidence |
|---|---|---|
| date | artist/DJ + producer + venue | dated primary event, ticketing or venue page |
| producer | artist/DJ + date + venue | organizer page, ticketing or venue announcement |
| artist/DJ | date + producer + venue | lineup, artist or venue source |
| venue | date + artist/DJ + producer | venue/ticketing/official event source |

Every result keeps raw query terms, URL, retrieval date, matched fields,
confidence and unresolved conflicts. A filename, OCR token or repeated guess
alone cannot create a venue, producer or artist entity.

## Next gate

Rebuild and validate the RD catalog after removing `paralelo_89` from active
venue knowledge. Then refresh generated projections and assert that the only
active canonical venue from this family is not `paralelo_89`; keep Sala
Metronomo as an unresolved event venue until its catalog contract is defined.
Connect the FRVR headliner to the existing triangulator output rather than
creating a new research script.
