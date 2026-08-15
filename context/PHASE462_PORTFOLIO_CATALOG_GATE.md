# Phase 462 — portfolio catalog boundary gate

## Scope

The portfolio surface was inspected in the isolated worktree on
`codex/portfolio/web`. The two JSON files are different contracts:

- `tools/portfolio/proyectos.json`: 10 curated public projects, with project
  identity, human-facing name/description, line, state and administration
  route.
- `iskvw/datos/obras.json`: 8 visual works consumed by ISKVW skins, with media,
  technique, dates and artwork assets.

They are not byte duplicates and were not merged.

## Changes

- Added `tools/portfolio/catalog_contract.py`.
- `generar_portfolio.py` now validates the curated catalogue before producing
  its projection.
- Generated `out/flujo-projects.json` now carries a portable contract marker:
  `portfolio_project_catalog`, version `1`, with an explicit visual-works
  source reference.
- Extended `tests/test_portfolio_gen.py` with contract and duplicate-id checks.

The contract keeps machine identifiers lowercase ASCII slugs while allowing
human-facing Spanish text with accents. It is read-only and does not modify
catalogue data.

## Foreground validation

| Command | Result |
| --- | --- |
| `python3 -m py_compile tools/portfolio/catalog_contract.py tools/portfolio/generar_portfolio.py tests/test_portfolio_gen.py` | exit 0 |
| `python3 tools/portfolio/generar_portfolio.py --out /tmp/... --max 25` | exit 0; 10 projects and 25 archive entries |
| JSON contract assertion on generated output | exit 0; portable source and visual-works source present |
| duplicate-id negative contract probe | exit 0; invalid catalogue rejected |
| `npm run typecheck` in `web/` | exit 127; `tsc` is absent from isolated worktree; no install performed |

No API route, RD file, `iskvw/datos/obras.json`, generated repository output,
deployment workflow or historical evidence was changed. Temporary outputs
were written under `/tmp` only.

## Disposition

`PORTFOLIO_PROJECT_CATALOG_CONTRACT_GREEN; VISUAL_WORKS_CONTRACT_PRESERVED;
GENERATOR_OUTPUT_GREEN; DUPLICATE_ID_GATE_GREEN; WEB_TYPECHECK_UNAVAILABLE`

## Next action

Inspect and refactor the `PortafolioPanel` contract consumer in isolation,
using the existing read-only `/api/portafolio` response. Keep `hub.py` changes
out of this write set unless a minimal endpoint compatibility change is proven
necessary. Re-run the catalog gate and use the existing web toolchain if its
dependencies become available without installation.
