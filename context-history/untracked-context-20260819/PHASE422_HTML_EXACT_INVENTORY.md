# Phase 422 - HTML exact inventory and owner gate

Date: 2026-08-15
Agent: LUNA principal
Scope: read-only inventory of reachable HTML/HTM files across `/home/mak/*`.
No HTML was edited, moved, deleted or merged.

## Physical inventory

The protected-prune scan skipped only the disconnected `/home/mak/OneDrive`
mount during traversal. It found:

- 814 reachable `.html`/`.htm` files;
- 88,356,717 total bytes;
- 123 exact SHA-256 duplicate groups;
- 414 files belonging to those duplicate groups.

Largest physical owners by HTML bytes:

| owner | files | bytes | first disposition |
|---|---:|---:|---|
| `/home/mak/apps` | 9 | 39,177,362 | application/generated surface; owner still needs consumer check |
| `/home/mak/WIN` | 161 | 13,138,324 | historical evidence |
| `/home/mak/flujo` | 59 | 7,594,710 | canonical active/projection candidates |
| `/home/mak/quarantine` | 75 | 7,147,189 | protected rollback evidence |
| `/home/mak/flujo-deploy` | 49 | 4,892,667 | deployment projection candidate |
| `/home/mak/actions-runner` | 205 | 4,655,016 | generated/worktree projection evidence |
| `/home/mak/vibecodeine` | 42 | 3,548,101 | projection/worktree evidence |
| `/home/mak/curatoria_inbox` | 54 | 1,832,433 | intake/recovered evidence |
| `/home/mak/RD` | 3 | 1,288,244 | external/department surface; consumer check required |

## High-value exact groups

- `mapping.html`: 17 exact copies, 67,585 bytes each; copies span WIN,
  canonical web/public and generated deployment surfaces.
- `context/{flujo_hub,plano_demo,svg_visualizer}.html`: six exact copies in
  the canonical/deploy family plus protected worktrees; these are guarded
  visual surfaces, not safe deletion candidates.
- `cotizacion_general_eventos*.html`: six exact copies per variant across
  canonical, deploy, WIN, runner and vibecodeine projections.
- `rd.html`: four exact copies across `dist_compartir`, `web/dist-rd` and WIN.
- `lasertoolkit.html`, recovered RD prototypes and other recovered pages have
  exact groups that cross active, historical and evidence owners.

## Canonical candidates requiring owner mapping

- `web/dist/index.html` and `web/index.html`: public web output versus source
  shell; do not assume the larger file is the owner.
- `context/flujo_hub.html`, `context/plano_demo.html` and
  `context/svg_visualizer.html`: existing visual tool surfaces guarded by
  `docs/HERRAMIENTAS_VISUALES.md`.
- `web/dist-rd/rd.html`, `web/dist-plano/plano.html` and
  `web/venues/index.html`: RD/plano/venue projections with distinct consumers.
- `iskvw/` pages: portfolio/public projection candidates; publishing remains
  separately gated by Phase 410.
- `docs/rd/`, `docs/recovered/`, `projects/`, `tools/` and `cultura/`: pages
  are documentation, prototypes or visual experiments until a consumer is
  demonstrated.

## Verification

- Full HTML hash inventory with protected mount pruning: exit 0.
- Exact hash grouping: exit 0; 123 groups / 414 files.
- No source, database, service, external provider or Git state changed.

## Risks and next action

Exact equality proves content duplication, not interchangeable ownership. The
next safe step is a canonical owner/consumer matrix for the active `flujo`
HTML candidates, beginning with the guarded hub/plano/svg tools and the
portfolio/RD/plano outputs. Preserve WIN, quarantine, runner and deployment
copies until their projection owners are explicitly retired.
