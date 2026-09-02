# Phase 63 — MAK folder architecture and cleanup policy

## Objective

Define where each class of artifact belongs before proposing Git branches,
merging equivalent tools or deleting anything. This is an ownership and
consumer map, not a move operation. The physical authority remains
`/home/mak/*`; `/home/mak/WIN` is historical evidence only.

## Canonical ownership model

| Canonical owner | Allowed contents | Examples | Rule |
|---|---|---|---|
| `/home/mak/flujo/src` | FLUJO source and importable runtime code | hub, RD, ISKVW, CULTURA, CLI | one active implementation per import path |
| `/home/mak/flujo/data` | canonical structured runtime data | `rd.db`, tariffs, catalogs, manifests | schema/reader owns each database; no demo data mixed in |
| `/home/mak/flujo/jobs` | operational job state and traceability | briefs, outputs, lifecycle metadata | each job has one owner and rollback path |
| `/home/mak/flujo/datadrops` | inbound files awaiting analysis/review | uploaded source files and manifests | never mix with published assets |
| `/home/mak/flujo/projects` | active FLUJO/CULTURA project sources | tapiz, SVG projects, active templates | project-local source plus explicit export destination |
| `/home/mak/RD` | RD creative source, editable files, deliveries and retained evidence | Blender/Adobe sources, event history, supplements | preserve existing surface; classify internally before any move |
| `/home/mak/flujo/assets` | only assets proven to be consumed by FLUJO runtime | logos, SVGs, palettes, small static resources | link or register provenance; do not bulk-copy from RD |
| `/home/mak/<department>` | live department-owned tools with a real consumer | `lenguaje`, `vigia`, `plataforma`, `research`, `curatoria`, `post` | keep at root while its owner/consumer is live and distinct |
| `/home/mak/archive` | intentionally retained historical or superseded artifacts | retired variants, migration notes, recovery snapshots | archive only after provenance and replacement are recorded |
| `/home/mak/WIN` | complete Windows historical archive | former FLUJO tree and MAK genealogy | read-only historical source; never runtime or cleanup target |

The architecture does not force every department into `flujo`. A live
department remains where its consumer, owner and runtime contract are clear.
The canonical owner is a logical responsibility first; physical moves happen
only when a consumer-tested migration slice exists.

## Classification states

Every file or bounded directory receives exactly one primary state:

1. `LIVE_SOURCE`: imported or executed by a current consumer.
2. `LIVE_DATA`: read or written by a current runtime contract.
3. `LIVE_OUTPUT`: current deliverable referenced by a job or human workflow.
4. `EDITABLE_TEMPLATE`: source for a live output, including Blender/Adobe
   files; external application ownership must be recorded.
5. `EVIDENCE`: historical input, provenance, review material or source record.
6. `RECOVERY`: autosave, rollback or safety copy retained until its owner and
   replacement are proven.
7. `DUPLICATE_EXACT`: byte-identical to another item; never delete solely for
   matching hash because location and provenance may differ.
8. `DUPLICATE_VARIANT`: visually/functionally related but not identical;
   requires human-facing comparison and consumer decision.
9. `UNRESOLVED`: no consumer, owner or provenance established yet.
10. `JUNK_CONFIRMED`: only after the deletion gate below passes.

## Duplicate-document policy

Exact hashes are the first pass, not the decision. For each collision record:

- all absolute paths, sizes, hashes, mtimes and provenance;
- whether each path is referenced by code, route maps, jobs, manifests or
  human-facing documents;
- whether the files are source, output, recovery or evidence;
- whether one copy is a platform projection (for example line endings or
  Windows path metadata);
- a canonical owner and an archive/recovery destination.

Merge an exact duplicate only when the surviving path is consumer-tested and
the other path is not a required provenance location. Keep a small manifest of
the retired path. For PDFs, images, SVGs, Blender, Adobe and office files,
hash equality is insufficient for semantic equivalence; use metadata and
bounded visual/content comparison before classification.

## Equivalent-tool policy

Tools merge by consumer contract, not by filename or apparent similarity. Two
tools are candidates only if they share a function, inputs, outputs and owner.
The merge gate is:

1. identify all entrypoints and import consumers in MAK and WIN;
2. cover Spanish/English names, aliases and platform-specific launchers;
3. compare schemas, CLI/API behavior, side effects and external dependencies;
4. choose one implementation with the stronger current consumer and evidence;
5. preserve unique capabilities as adapters or separate tools;
6. run parse/import/fixture/foreground contract checks;
7. retain the superseded implementation as evidence until rollback is proven.

Examples: `flyer_auto.py` and the Windows automation scripts are not merged
just because both mention flyers; the former is an active Python consumer,
while the latter includes external Blender/Adobe/EXE workflows. Likewise,
`packs.py` and web tariff data require source-of-truth reconciliation, not a
blind file merge.

## Cleanup gate

No deletion occurs from a hash report alone. A candidate may be removed only
when it is `JUNK_CONFIRMED` and all of these are true:

- no active code, route, job, manifest or documented human workflow consumes
  it;
- it is not evidence, source, editable template, recovery or credential data;
- a replacement or canonical copy is identified where relevant;
- a reversible quarantine or backup exists;
- a foreground validation proves the surviving consumer still works;
- the exact path, reason, command, result and rollback are recorded in the
  handoff.

`WIN` is never a cleanup target. Generated caches such as `__pycache__` may be
considered separately, but only with explicit path-level evidence and without
using a broad recursive deletion.

## Sequence before Git branches

1. Freeze this ownership model and enumerate physical roots from `/home/mak/*`.
2. Build exact-hash duplicate manifests for bounded roots, excluding caches,
   environments and the historical WIN archive from automatic decisions.
3. Build the consumer/tool crosswalk and select merge candidates.
4. Integrate one candidate at a time with fixture and foreground validation.
5. Produce a deletion/quarantine manifest containing only confirmed junk.
6. Validate MAK entrypoints and data contracts after each controlled cleanup.
7. Only then design branches around live domains and integration slices.

No files were moved, merged or deleted in this phase.
