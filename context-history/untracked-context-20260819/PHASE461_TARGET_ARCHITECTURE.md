# Phase 461 — Target architecture and migration boundary

## Decision

MAK remains one repository with one permanent integration branch, `main`.
The target architecture is logical and consumer-oriented, but the physical
migration is staged. Existing active paths remain stable until their imports,
entrypoints, tests and deploy consumers have been migrated together.

The previous proposal to move everything immediately under `apps/` and
`domains/` is therefore a target model, not a permission to copy or rename
the whole tree.

## Current canonical surfaces

| Current path | Role | Target boundary | Migration rule |
| --- | --- | --- | --- |
| `src/flujo/` | Python hub, API and runtime | `apps/hub` plus shared runtime packages | Keep path until import and entrypoint migration is verified |
| `web/` | React hub and RD/Plano panels | `apps/hub` and `apps/rd-studio` | Split by entrypoint/consumer, not by file count |
| `iskvw/` | Public portfolio artifact and static deploy surface | `apps/portfolio` | Preserve public output and deployment contract |
| `cultura/` | Curatoria, research and POST pipelines | `domains/curatoria`, `domains/research`, `domains/cultura` | Separate only when a real owner and consumer exist |
| `tools/` | CLI tools and adapters | `tools/importers`, `tools/generators`, `tools/triangulation`, `tools/maintenance` | One canonical owner per function; keep historical variants classified |
| `data/` | Operational, candidate and source data | `data/canonical`, `data/review`, `data/fixtures`, `data/evidence` | Never merge databases by byte copy |
| `docs/`, `context/` | Operating docs, evidence and handoff | `docs/operating`, `docs/decisions`, `docs/ideas`, `docs/archive` | Consolidate content before moving files |
| `WIN/` | Windows genealogy and source evidence | `WIN/` | Read-only historical archive |

## Data and identity boundary

RD, portfolio and curatoria must not create competing copies of the same
venue, artist, producer or event. The shared layer is a relation contract and
crosswalk, not an automatic replacement of source databases:

```text
RD source data ---------\
Portfolio source data ----> shared identity/crosswalk -> consumers
Curatoria evidence -----/
```

The first shared records are expected to distinguish `venue`, `producer`,
`artist`, `event`, `project` and `work`. Ambiguous records remain in review
state and preserve provenance. A human-facing Spanish label may contain
diacritics; machine identifiers and schemas remain English ASCII.

## Git boundary

Only `main` is permanent. The current dirty worktree must not be committed as
one block. The restructuring itself may use one temporary branch, but each
integrated change needs a bounded write set and a real consumer:

```text
main
integration/house-restructure
work/portfolio-rebuild
work/rd-entity-bridge
work/flujo-event-bridge
work/research-fondart
work/tools-consolidation
archive/<historical-line>
```

The existing ten branches are historical inputs, not clean domain bases. They
remain preserved while their changes are classified. No `develop`, permanent
`rd`, permanent `mak`, or permanent `iskvw` branch is required.

## Migration order

1. Establish the target contracts and ownership manifest.
2. Rebuild the portfolio catalog boundary while retaining `iskvw/` output.
3. Split the hub web entrypoints only where a consumer and validation exist.
4. Add the RD/portfolio/entity crosswalk without destroying source databases.
5. Consolidate equivalent tools after their consumers are mapped.
6. Move documentation and evidence by status, not by filename similarity.
7. Integrate each verified slice to `main` and tag stable states.

## Explicit non-goals

- No whole-tree copy from `WIN`.
- No blind mass rename to `apps/` or `domains/`.
- No deletion of old databases, memories or generated evidence.
- No reactivation of XIO, n8n or unrelated external services.
- No dependency installation or permanent service startup.

## First concrete slice

The first implementation slice is the portfolio boundary: identify the
canonical catalog source, its generator(s), the `/api/portafolio` consumer and
the public `iskvw/` deploy artifact. The slice must produce a deterministic
catalog contract and preserve the existing output before any physical move.
