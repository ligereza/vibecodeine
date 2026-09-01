# Phase 405 — owner, cleanup and branch handoff

Date: 2026-08-15 (America/Santiago)

This is a physical `/home/mak/*` disposition map. It is an ordering plan,
not a move/delete operation. `/home/mak/WIN` remains historical read-only.

## Physical owner map

| Physical surface | Disposition | Rule before any change |
|---|---|---|
| `/home/mak/flujo` | Canonical authoring and FLUJO APP | Keep one active owner; integrate smallest consumer slice |
| `/home/mak/RD` | Protected RD data/media/products | Preserve data and generated products; edit only named targets |
| `/home/mak/data/rd.db` | Canonical catalog owner | Reconcile by schema/table/consumer, never filename alone |
| `/home/mak/flujo/data/rd_datos.db` | Separate privacy/field store | Keep physically separate and empty until human authority |
| `/home/mak/plataforma`, `research`, `codex`, `curatoria`, `vigia`, `lenguaje` | Runtime projections/department consumers | Retain only where a real consumer exists; wrappers may remain thin |
| `/home/mak/curatoria_inbox`, `curatoria_test`, `state`, `indexes`, `labs` | Intake/test/state/evidence surfaces | Classify provenance and lifecycle before consolidation |
| `/home/mak/flujo-deploy`, `/home/mak/bin` | Deploy/sync owner, gated mutators | Static audit only; no deploy, sync or Git execution |
| `/home/mak/WIN` | Historical Windows archive | Crosswalk only; never active destination or deletion target |
| `/home/mak/context/quarantine`, `/home/mak/quarantine`, `/home/mak/rollback` | Reversible containment/recovery | Preserve manifests and rollback paths |
| `/home/mak/n8n-local` | Discarded/excluded path with protected credentials | No active consumer; preserve evidence, do not revive |
| `/home/mak/xio_puente` | User-excluded | Out of migration and out of cleanup scope |
| `/home/mak/blender`, `blender-4.5.3-viejo`, `searxng`, `venv-providers`, `models`, `model-config` | Optional/external/tool environments | Owner and concrete consumer required before pruning |
| `/home/mak/apps`, `Apps`, `vibecodeine`, `portfolio_media`, `renders`, `trazos`, `actions-runner` | Separate creative/tool/product surfaces | Do not merge by name; audit consumer and provenance first |
| `/home/mak/Descargas`, `Documentos`, `Documents`, `Escritorio` and user home config | User data/home surface | Not application cleanup scope; preserve untouched |

## Merge and cleanup order

1. Assign one owner per active tool by consumer contract, not by folder name,
   language or timestamp.
2. Compare equivalent variants using AST, imports, output contract and parity;
   keep the canonical implementation and retain thin wrappers only when a
   real runtime consumer needs them.
3. For duplicate documents, compare content and active references first;
   preserve exact copies as evidence until editorial authority approves a
   reversible quarantine or a documented canonical link.
4. Keep `rd.db` catalog state separate from `rd_datos.db` privacy/field state;
   related schema does not authorize a physical merge.
5. Quarantine only confirmed residue with a manifest, checksum and rollback;
   never classify WIN, databases, credentials, generated products, logs or
   user documents as junk from age or duplicate names alone.
6. Re-run parse/import/focused tests after each bounded change, then update the
   owner ledger and handoff before selecting the next slice.

## Branch proposal handoff

The branch system is already proposed in
`context/PHASE375_GIT_BRANCH_SYSTEM_REFRESH.md`:

```text
main
codex/rd/field-review
codex/rd/runtime
codex/flujo/event-bridge
codex/rd/assets
codex/mak/ownership
codex/tools/consolidation
codex/cleanup/confirmed-junk
codex/release/full-audit
```

No branch was created or changed. Applying it is a separate explicit Git
operation after the physical owner decisions and live authority gates.

## Remaining external decisions

```text
RD field/date/privacy authority
one named live RD mutation with rollback
provider/IMAP/OSC/Blender/GPU/network execution, if required
optional dependency installation, if a consumer requires it
physical document fusion or residue quarantine approvals
Git branch creation and later integration
```

Disposition: `OWNER_MAP_READY; CLEANUP_ORDER_DEFINED; BRANCH_PROPOSAL_HANDOFF_READY`.
