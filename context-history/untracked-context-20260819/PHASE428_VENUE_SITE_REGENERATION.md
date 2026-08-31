# Phase 428 - venue catalogue projection regeneration

Date: 2026-08-15
Agent: LUNA principal
Scope: update the local generated Venue HTML from its declared JSON source,
while preserving the RD producer/venue distinction.

## Action

`tools/venue.py` declares `web/venues/index.html` as its output. The previous
HTML contained two example records and did not contain the current SCD record.
The generator was run against the existing `data/venues/*.json` source.

## Verification

- Before SHA-256: `43138aeb5ca39c475e04529e6da7198533cf42616b0a93405b4456e1f5be754a`.
- Command: `PYTHONDONTWRITEBYTECODE=1 python3 tools/venue.py sitio`.
- Generator result: exit 0, `web/venues/index.html · 3 salas · 27 KB`.
- After SHA-256: `f8604f03828727b826975a9ea49899449a3ec42c43b98be556f84728e5af5145`.
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/venue.py validar`: exit 0,
  `3 venues · 0 errores · 0 avisos`.
- Marker check confirms `scd-plaza-egana`, `santiago-sala-ejemplo` and
  `valparaiso-otro-ejemplo` are present.

## Scope and role safety

- Modified only the generated projection
  `/home/mak/flujo/web/venues/index.html`.
- No `data/rd.db`, `knowledge/venues`, producer JSON, Portfolio HTML or
  historical copy changed.
- OpenKlub is not inserted as a venue; it remains a producer/brand, with its
  existing conflated RD row gated for later correction.

## Next concrete action

Prepare the read-only correction plan for consumers of `data/rd.db.venues` row
`openklub` and `knowledge/venues/openklub.yaml`. The safe disposition is to
keep OpenKlub in `productoras`, preserve the conflated evidence and wait for a
real venue identity before changing the RD projection.
