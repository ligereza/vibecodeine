# Phase 463 — portfolio panel consumer boundary

## Scope

The React consumer of the read-only `/api/portafolio` endpoint was extracted
from the component into `web/src/data/portfolio.ts`.

The loader now owns:

- response parsing and HTTP error handling;
- required human-facing project fields;
- duplicate project-id rejection;
- optional contract metadata and prototype metadata.

`PortafolioPanel.tsx` remains a presentation/filtering component. It does not
write to the catalogue, invoke POST routes or import RD data.

## Files changed

- `web/src/data/portfolio.ts`
- `web/src/components/PortafolioPanel.tsx`

The backend endpoint in `src/flujo/web/hub.py` was not changed. The consumer
continues to use the existing route and the existing read-only semantics.

## Validation

- The Python catalogue gate from Phase 462 was rerun: compile, generator,
  portable output assertion and duplicate-id rejection all exited 0.
- The new TypeScript import path exists and the component no longer defines a
  second local catalogue type; static source assertions passed.
- `npm run typecheck` could not run: `web/node_modules/.bin/tsc` is absent and
  `tsc` is not available on PATH (exit 127). No package installation was
  attempted.
- The existing public skin smoke suite ran with Node 18 for `campo`,
  `terminal` and `venue`; all exited 0 and the three real inline skins booted
  and completed their bounded frame checks.

## Risk and disposition

`PORTFOLIO_PANEL_CONTRACT_EXTRACTED; API_READ_ONLY_PRESERVED;
PUBLIC_SKINS_SMOKE_GREEN; RD_WRITE_SET_UNTOUCHED; TS_TOOLCHAIN_UNAVAILABLE`

The remaining risk is toolchain-level TypeScript verification, not an observed
runtime failure. The next action is to validate the isolated web slice with
the available repository toolchain if it appears, then inspect the public
`iskvw` build contract separately.
