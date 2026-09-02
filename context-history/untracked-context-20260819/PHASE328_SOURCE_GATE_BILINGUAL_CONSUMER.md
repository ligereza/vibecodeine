# Phase 328 — bilingual source-gate consumer slice

Date: 2026-08-15 (America/Santiago)
Scope: Research source-quality helper consumed by the RD catalog builder.

## Paths and consumer

- Source gate: `/home/mak/flujo/cultura/mak_research/fuentes.py`
- Consumer: `_event_source_gate()` in
  `/home/mak/flujo/src/flujo/rd/database.py`
- The gate classifies primary URLs for `cl_eventos`, and persists only the
  verdict/primary URL list in the regenerable catalog projection.

## Foreground validation

With bytecode disabled and no provider/network call:

- Spanish `reducción de daños en fiestas` and English `harm reduction at
  festivals` both mapped to `biomedico` and correctly marked a secondary-only
  URL as `SIN FUENTE PRIMARIA`.
- A `passline.com` event URL was accepted as a primary `cl_eventos` source.
- `database._event_source_gate()` returned `([], 1)` for a secondary-only URL
  and the primary URL list plus flag `0` for the Passline URL.
- The source module parsed successfully.

Results:

```text
FUENTES_BILINGUAL_FIXTURE=PASS
RD_EVENT_SOURCE_CONSUMER=PASS primary_and_secondary_gates=True
NETWORK_CALLS=0 FILE_WRITES=0
```

## Disposition

`VERIFIED_CONSUMER_DEPENDENCY_BILINGUAL`.

This is a pure stdlib dependency with a real RD consumer. Spanish/English
matching is part of the contract; searching only one language would produce a
false absence. No duplicate or package merge is needed in this slice.

## Changes and risks

- Source, databases, assets, services, providers, Git and WIN: unchanged.
- Risk: primary-domain lists are policy/data contracts and need explicit review
  when domains change; this gate does not browse or verify live URLs.
- Rollback: none needed; pure fixtures only.

