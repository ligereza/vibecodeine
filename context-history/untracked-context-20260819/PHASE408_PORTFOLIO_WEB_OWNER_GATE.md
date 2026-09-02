# Phase 408 — portfolio web owner and branch gate

Date: 2026-08-15 (America/Santiago)

## Current owner

The canonical portfolio web owner is `/home/mak/flujo`:

```text
/home/mak/flujo/tools/portfolio/proyectos.json       catalogue source
/home/mak/flujo/tools/portfolio/*.py                 generation/asset tools
/home/mak/flujo/web/src/components/PortafolioPanel.tsx  app panel
/home/mak/flujo/src/flujo/web/hub.py                 read-only /api/portafolio
/home/mak/flujo/iskvw/                                public portfolio surface
/home/mak/portfolio_media/media                       protected media store
```

`iskvw` is the public portfolio and the only site by the recorded user
decision. The panel reads the catalogue; editing
`tools/portfolio/proyectos.json` is the deliberate publishing input. The hub
endpoint is read-only.

## Duplicate tool check

The four files in each of these directories have identical SHA-256 values:

```text
/home/mak/flujo/tools/portfolio
/home/mak/flujo-deploy/tools/portfolio
/home/mak/vibecodeine/tools/portfolio
```

The canonical owner is `flujo/tools/portfolio`. The other two remain runtime
projections/evidence until their consumers are formally retired; no copies
were moved or deleted.

## Git branch

The branch for this slice is:

```text
codex/portfolio/web
```

Exclusive write set:

```text
flujo/web/
flujo/tools/portfolio/
flujo/iskvw/
portfolio-specific tests and docs
```

It must not bulk-add `/home/mak/portfolio_media`, edit RD databases, revive
XIO, or modify shared `hub.py` routes assigned to another branch. Any shared
API change needs an explicitly isolated integration patch.

Required gate: local typecheck/build or fixture validation, catalogue schema
check and asset-path check. Publishing remains a separate external action.

Disposition: `PORTFOLIO_OWNER_CONFIRMED; DUPLICATE_TOOLS_PARITY; BRANCH_ADDED_TO_PROPOSAL`.
