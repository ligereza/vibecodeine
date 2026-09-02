# Phase 362 — physical MAK architecture refresh

Date: 2026-08-15 (America/Santiago)

## Root disposition

| Physical root | Current owner/disposition | Consumer evidence | Action |
|---|---|---|---|
| `/home/mak/flujo` | canonical authoring/integration | CLI, hub, RD, intake, render and index consumers | retain as baseline |
| `/home/mak/RD` | protected RD data/media surface | RD assets and Blender provenance | preserve; no broad scan/delete |
| `/home/mak/research` | active Research runtime and credential owner | provider, parser, service manifests and reports | retain; now owns `research.env` |
| `/home/mak/plataforma` | active platform/runtime owner | provider and projection consumers | retain; n8n fallback removed |
| `/home/mak/curatoria` | active cultural state/evidence owner | ledgers, reports and local fixtures | preserve data/evidence |
| `/home/mak/codex` | active local orchestration/evidence owner | local contracts and reports | retain |
| `/home/mak/xio_puente` | user-excluded external bridge | no migration action authorized | preserve; do not test ADB |
| `/home/mak/n8n-local` | discarded automation label; protected credential evidence | no n8n process/unit; old active fallbacks removed in Phase 361 | retain secrets in place; do not execute |
| `/home/mak/WIN` | historical Windows source/archive | migration provenance only | read-only; never clean as active MAK |
| `/home/mak/blender` | active creative runtime | Phase 331/332 Blender and RD asset refs | retain |
| `/home/mak/blender-4.5.3-viejo` | older distinct runtime | no active path ref; provenance unresolved | preserve pending provenance decision |
| `/home/mak/post` | absent physical root | no active root to integrate | no action; avoid inventing it |
| `/home/mak/workspace` | empty tree already quarantined | Phase 228 zero-file proof | retain reversible quarantine |
| `/home/mak/OneDrive` | disconnected mount | shell scan returned connection error | do not infer contents or mutate |

## Architecture decision

The active architecture is owner-based, not name-based: Research owns its
credential path, n8n is not an active department, XIO is excluded, and WIN is
historical. Missing `/home/mak/post` is a fact, not a migration failure. The
remaining roots are protected, external, evidence or reversible-quarantine
surfaces until a named consumer proves otherwise.

## Validation

This refresh is backed by the Phase 361 active-reference/static/unit gate and
the explicit top-level physical listing. No root was deleted or copied, and no
disconnected mount was traversed beyond the failed metadata lookup.
