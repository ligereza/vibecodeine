# Phase 432: RD bundle stale projection gate

## Scope

The source-level RD correction is current, but the standalone Vite bundle was
checked separately before any overwrite.

## Evidence

`web/dist-rd/rd.html` and `dist_compartir/herramientas_rd.html` are byte-identical:

- SHA-256: `11eb4eab551129f779caba4734d66736312c270cb700b96e803ad9f5c72fa175`
- `cmp -s`: exit 0

Both stale bundles contain the old markers:

- `paralelo_89`: 1 occurrence;
- `openklub`: 2 occurrences;
- `espacio_riesco`: 1 occurrence;
- `Sala Metronomo`: 0 occurrences;
- `artist_dj`: 0 occurrences.

The current source/projections were checked separately:

- `web/src/data/rdDbEmbebida.json`: no `paralelo_89`, one canonical venue,
  one unresolved `Sala Metronomo` relation and one expected `openklub`
  producer record;
- `docs/rd/presentacion_db.html`: no `paralelo_89`, `artist_dj` present and
  `Sala Metronomo` present;
- `docs/rd/propuesta_directiva.html`: no `paralelo_89`, current producer
  relations retained.

## Owner and gate

The owner chain is:

`web/src/mainRd.tsx` + `web/src/components/RdDbPanel.tsx` +
`web/src/data/rdDbEmbebida.json` -> `vite.rd.config.ts` ->
`web/dist-rd/rd.html` -> `web/scripts/copy-rd-share.mjs` ->
`dist_compartir/herramientas_rd.html`.

The build gate remains closed from Phase 424: the local Vite wrapper is not
executable, direct Vite requires a newer Node runtime and the optional Rollup
Linux module is missing. No package, permission or bundle was changed here.
Manual replacement of minified HTML would bypass the owner and is prohibited.

## Disposition

`SOURCE_PROJECTIONS_CURRENT; RD_VITE_BUNDLE_STALE_AND_GATED; NO_MANUAL_BUNDLE_EDIT`.

Keep both exact copies as a documented stale projection until the authorized
Node/Vite build environment is repaired. This does not invalidate the source
database correction or the read-only triangulation result.

## Next action

Continue the HTML owner audit on the next independent active consumer. Keep the
RD bundle build as an explicit environment gate, not as a data rollback.
