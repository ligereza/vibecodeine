# Phase 142 - RD tariff single-source merge

## Problem

`data/rd_packs.json` declared itself the single editable tariff, but
`web/src/rdBrand.ts` still contained a second hardcoded copy of pack names,
prices, inclusions and proportions. This could desynchronize the web UI from
the Python rider/quote consumers.

## Change

Edited `/home/mak/flujo/web/src/rdBrand.ts` to import the canonical JSON tariff
from `../../data/rd_packs.json`. The public `PACKS`, `ALL_PACKS`, runtime price
override and reset APIs remain intact; only the duplicate literal source was
removed. No generated web build, PDF, database or live job output was changed.

## Foreground validation

- First typecheck attempt exposed an incorrect relative path (`../data`),
  exit 2; no output was written.
- Corrected to `../../data/rd_packs.json`.
- `npm run typecheck`: exit 0 (`tsc --noEmit`).
- JSON fixture: exit 0; order `INFO, TESTEO, COMPLETO`, prices
  `250000, 300000, 500000`, and COMPLETO proportions remained valid.

## Decision

`MERGE_NOW`: yes. The web and Python consumers now share one tariff source;
runtime web overrides remain an intentional consumer behavior, not a second
source of truth.

## Next action

Run the post-merge FLUJO verification and refresh the objective matrix. Keep
the production web build separately gated by Node/Rollup compatibility.
