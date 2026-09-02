# Phase 436: Plano/Rider HTML owner gate

## Owner chain

The active source chain is:

`web/plano.html` -> `web/src/mainPlano.tsx` ->
`web/src/components/PlanoStandalone.tsx` -> `vite.plano.config.ts`.

The entry explicitly mounts only the standalone Plano/Rider tool, applies the
local plano configuration before React render and loads browser-local symbols.
The config defines `__SIN_SERVIDOR__ = true`, so the distributed file is
intended to work without a hub service.

## Projection evidence

The current source and generated files are distinct:

- `web/plano.html` SHA-256:
  `4b9e3e01da7b906711f736ddec3833f8a951180a84779f452e43b482ffee69c4`;
- `web/dist-plano/plano.html` SHA-256:
  `9d7d7a2aa3186dba78521dc5a275e97101d5cffe81ded55951cbe612c1461cc1`;
- `dist_compartir/plano_rd.html` SHA-256:
  `3cad95f4b6389f47d8e5b0b818ce1d98e9b449bc643abdf2df05e4f20df6c37d`.

`cmp` between the two generated outputs returned exit 1. They are therefore
not a safe duplicate-fusion candidate. No source or projection was edited.

## Disposition

`PLANO_RIDER_SOURCE_OWNER_CONFIRMED; GENERATED_OUTPUTS_DIVERGENT; BUILD_PARITY_OPEN; NO_OVERWRITE`.

This preserves the functional source and both historical/generated outputs
until the Vite environment can regenerate them deterministically. The theater
seating primitive and the SCD headless derivative remain separate contracts.

## Next action

Continue the HTML owner audit on the next independent active consumer. Keep
Plano/Rider build repair separate from data/venue corrections and do not edit
minified bundles manually. The RD catalog still has a legacy compatibility
boundary: `data/productoras/frvr.json` is role-marked `artist_dj`, but the
SQLite table is named `productoras`; do not expose that legacy placement as
proof that FRVR is an organizer until a role-aware projection is connected.
